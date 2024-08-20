import json
from typing import List, Set

from app.databases.neo4j_database.neo4j_database import get_tables_in_path
from app.databases.postgres_database.service import run_query
from app.databases.qdrant_database.qdrant import search_embeddings
from app.models.database import Table
from app.models.outputs import SearchOutput, SqlGenerationOutput, ValidationOutput


def gather_tables_from_paths(tables_objs: List[SearchOutput], columns_objs: List[SearchOutput], collection_name: str) -> \
        Set[Table | None]:
    table_names = {table.table_name for table in tables_objs} | {col.table_name for col in columns_objs}
    return _get_tables_in_paths(table_names, collection_name)


def execute_and_return_query_results(collection_name: str, sql_output: SqlGenerationOutput) -> str:
    results = run_query(collection_name, sql_output)
    if isinstance(results, str):
        return json.dumps({"message": results})

    return json.dumps({"query": sql_output.query, "output": results})


def find_missing_tables(validation_output: ValidationOutput, collection_name: str) -> Set[Table | None]:
    missing_tables_objs = set()

    for table in validation_output.missing_tables:
        missing_tables_objs.update(search_embeddings(query=table, search_type="table_name", score_threshold=0.2,
                                                     collection_name=collection_name))

    return _get_tables_in_paths({table.table_name for table in missing_tables_objs}, collection_name)


def _get_tables_in_paths(table_names: Set[str], collection_name: str) -> Set[Table | None]:
    tables = set()

    for table_from in table_names:
        for table_to in table_names:
            if table_from != table_to:
                tables.update(get_tables_in_path(table_from, table_to, collection_name))

    return tables
