from typing import List, Tuple, Union, Dict, Any
from psycopg2.extras import RealDictCursor

from app.databases.postgres_database.database_connection import get_database_info_by_name, get_db_connection, Database
from app.models.database import Column
from app.models.enums.postgres_data_types import PostgresDataType
from app.models.outputs import SqlGenerationOutput
from app.utils.formatting import format_results


def fetch_all(cursor, query: str, params: Tuple = ()) -> List[Dict[Any, Any]]:
    cursor.execute(query, params)
    return cursor.fetchall()


def get_tables_with_foreign_keys(
        database: Database
) -> Dict[str, Any]:
    with get_db_connection(database) as conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s;
            """, (database.table_schema,))

            tables = cur.fetchall()
            tables_names = [table[0] for table in tables]

            all_foreign_keys = {}

            for table in tables_names:
                cur.execute("""
                SELECT 
                tc.constraint_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name
                FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu 
                ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_name = %s
                AND tc.table_schema = %s;
                """, (table, database.table_schema))

                foreign_keys = cur.fetchall()

                if foreign_keys:
                    all_foreign_keys[table] = foreign_keys
                else:
                    all_foreign_keys[table] = []

        cur.close()
        conn.close()

    return all_foreign_keys


def get_tables(database: Database) -> List[str]:
    with get_db_connection(database) as conn:
        with conn.cursor() as cur:
            tables = fetch_all(cur, """
                SELECT table_name FROM information_schema.tables WHERE table_schema = %s;
            """, (database.table_schema,))
            return [table[0] for table in tables]


def get_columns_by_table(database: Database, table_name: str) -> List[Column]:
    with get_db_connection(database) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            columns = fetch_all(cur, """
                SELECT column_name, data_type, is_nullable FROM information_schema.columns
                WHERE table_name = %s AND table_schema = %s;
            """, (table_name, database.table_schema))

            primary_key_columns = fetch_all(cur, """
                SELECT a.attname AS column_name FROM pg_index i
                JOIN pg_attribute a ON a.attnum = ANY(i.indkey)
                WHERE i.indisprimary AND i.indrelid = %s::regclass;
            """, (table_name,))
            primary_key_columns = [{'column_name': col['column_name']} for col in primary_key_columns]

            foreign_keys = fetch_all(cur, """
                SELECT kcu.column_name, ccu.table_name AS foreign_table_name
                FROM information_schema.table_constraints tco
                JOIN information_schema.key_column_usage kcu ON kcu.constraint_name = tco.constraint_name
                JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tco.constraint_name
                WHERE tco.table_name = %s AND tco.constraint_type = 'FOREIGN KEY';
            """, (table_name,))
            foreign_keys_dict = {fk['column_name']: fk['foreign_table_name'] for fk in foreign_keys}

            return [
                Column(
                    name=col['column_name'],
                    data_type=PostgresDataType(col['data_type']),
                    collection_name=database.dbname,
                    is_nullable=(col['is_nullable'] == 'YES'),
                    is_primary_key=(col['column_name'] in primary_key_columns),
                    foreign_key_table=foreign_keys_dict.get(col['column_name'])
                ) for col in columns
            ]


def get_char_varchar_text_columns(database: Database, table_name: str) -> List[str]:
    with get_db_connection(database) as conn:
        with conn.cursor() as cur:
            columns = fetch_all(cur, """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = %s AND table_schema = %s AND data_type IN ('character varying', 'character', 'text');
            """, (table_name, database.table_schema))
            return [column['column_name'] for column in columns]


def get_column_values(database: Database, table_name: str, column_name: str) -> List[str]:
    with get_db_connection(database) as conn:
        with conn.cursor() as cur:
            values = fetch_all(cur, f'SELECT "{column_name}" FROM "{table_name}";')
            return [value[column_name] for value in values if value[column_name] is not None]


def run_query(dbname: str, sql_output: SqlGenerationOutput) -> Union[List[Tuple], str]:
    database = get_database_info_by_name(dbname)
    if not database:
        return f"Database connection for '{dbname}' not found."

    try:
        with get_db_connection(database) as conn:
            with conn.cursor() as cur:
                cur.execute(sql_output.query)
                results = cur.fetchall()
                return format_results(results)

    except Exception as e:
        return f"SQL Execution Failed: {e}"
