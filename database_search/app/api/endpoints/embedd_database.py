from app.databases.neo4j_database.insert_data import insert_tables_with_foreign_keys, insert_columns
from app.databases.postgres_database.database_connection import Database, register_database
from app.databases.qdrant_database.insert_data import embedd_database
from fastapi import APIRouter

router = APIRouter()


@router.post("/add")
def add_database(database: Database, include_values: bool = False):
    try:
        register_database(database)
        embedd_database(database, include_values)
        insert_tables_with_foreign_keys(database)
        insert_columns(database)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
