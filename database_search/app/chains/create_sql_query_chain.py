import json
from app.chains.ner_chain import ner_chain
from app.chains.validate_info_chain import validate_info_chain
from app.databases.neo4j_database.service import gather_tables_from_paths, find_missing_tables, \
    execute_and_return_query_results
from app.models.outputs import SqlGenerationOutput
from app.openai.chat import chat_with_openai
from app.templates.create_sql_prompt import postgresql_template
from app.databases.qdrant_database.qdrant import extract_search_objects
from app.utils.formatting import format_table_info, format_proper_nouns
from app.utils.json_extraction import trim_and_load_json


def create_sql_query(collection_name: str, query: str) -> str:
    try:
        entities = ner_chain(query)
        tables_objs, columns_objs, values_objs = extract_search_objects(entities, collection_name)

        tables = gather_tables_from_paths(tables_objs, columns_objs, collection_name)
        table_info = format_table_info(tables)

        validation_output = validate_info_chain(table_info=table_info, question=query)
        if validation_output.verdict == "no":
            tables.update(find_missing_tables(validation_output, collection_name))

        table_info = format_table_info(tables)
        proper_nouns = format_proper_nouns(values_objs)
        sql_query = generate_sql_query(table_info, proper_nouns, query)

        return execute_and_return_query_results(collection_name, sql_query)

    except Exception as e:
        return json.dumps({"error": str(e)})


def generate_sql_query(table_info: str, proper_nouns: str, query: str) -> SqlGenerationOutput:
    sql_prompt = postgresql_template(table_info, proper_nouns, query)
    chat_output = chat_with_openai(sql_prompt) or ""
    json_data = trim_and_load_json(input_string=chat_output)
    sql_output = SqlGenerationOutput(**json_data)
    return sql_output
