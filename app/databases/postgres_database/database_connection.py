from datetime import datetime
from typing import Optional

import psycopg2
from contextlib import contextmanager

from app.models.database import Database

metadata_db_connection_info = Database(
    dbname='database_search_db',
    user='postgres',
    password='postgres',
    host='localhost',
    port=5433,
    table_schema=None,
    date_created=None,
)


@contextmanager
def get_db_connection(database: Database):
    conn = psycopg2.connect(
        dbname=database.dbname,
        user=database.user,
        password=database.password,
        host=database.host,
        port=database.port
    )
    try:
        yield conn
    finally:
        conn.close()


def get_database_info_by_name(dbname: str) -> Optional[Database]:
    query = """
    SELECT * FROM database WHERE dbname = %s;
    """

    with get_db_connection(metadata_db_connection_info) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (dbname,))
            result = cur.fetchone()

            if result:
                return Database(
                    dbname=result[0],
                    user=result[1],
                    password=result[2],
                    host=result[3],
                    port=result[4],
                    table_schema=result[5],
                    date_created=result[6]
                )
            else:
                return None


def register_database(database: Database):
    try:
        with get_db_connection(metadata_db_connection_info) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                       INSERT INTO "database" (host, port, "user", password, dbname, "schema", date_created)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)
                   """, (
                    database.host,
                    database.port,
                    database.user,
                    database.password,
                    database.dbname,
                    database.table_schema,
                    datetime.now()
                ))
                conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        raise e


def get_all_registered_databases():
    try:
        with get_db_connection(metadata_db_connection_info) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT dbname FROM "database"
                """)
                dbnames = [row[0] for row in cur.fetchall()]
                return dbnames
    except psycopg2.Error as e:
        print(f"Error: {e}")
        conn.rollback()
        return []
