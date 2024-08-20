import logging

from app.databases.postgres_database.service import get_tables, get_columns_by_table, get_char_varchar_text_columns, \
    get_column_values
from app.models.database import Database
from app.openai.embedding import embedd_content
from app.databases.qdrant_database.qdrant import upsert_record, create_collection
from tqdm import tqdm


def embedd_table_names(database: Database, batch_size: int = 10):
    tables = get_tables(database)
    collection_name = database.dbname

    for i in range(0, len(tables), batch_size):
        batch = tables[i:i + batch_size]

        for table_name in tqdm(batch, desc=f"Embedding Tables {i + 1}-{i + len(batch)}"):
            metadata = {"table_name": table_name}
            try:
                vector = embedd_content(table_name)

                if vector is not None:
                    upsert_record(vector, metadata, collection_name)
                else:
                    raise ValueError(f"Embedding content failed for table: {table_name}")

            except Exception as e:
                print(f"Error embedding table {table_name}: {e}")
                continue


def embedd_columns(database: Database, batch_size: int = 10):
    tables = get_tables(database)
    collection_name = database.dbname

    for i in range(0, len(tables), batch_size):
        batch = tables[i:i + batch_size]

        for table_name in tqdm(batch, desc=f"Embedding Columns in Tables {i + 1}-{i + len(batch)}"):
            columns = get_columns_by_table(database, table_name)
            for column in columns:
                metadata = {
                    "table_name": table_name,
                    "column_name": column.name
                }
                try:
                    vector = embedd_content(table_name)

                    if vector is not None:
                        upsert_record(vector, metadata, collection_name)
                    else:
                        raise ValueError(f"Embedding content failed for table: {table_name}")

                except Exception as e:
                    print(f"Error embedding column {column.name} in table {table_name}: {e}")
                    continue


def embedd_string_values(database: Database, batch_size: int = 10):
    tables = get_tables(database)
    collection_name = database.dbname

    for i in range(0, len(tables), batch_size):
        batch = tables[i:i + batch_size]

        for table_name in tqdm(batch, desc=f"Embedding String Values in Tables {i + 1}-{i + len(batch)}"):
            char_varchar_text_columns = get_char_varchar_text_columns(database, table_name)
            for column_name in tqdm(char_varchar_text_columns, desc=f"Processing {table_name}", leave=False):
                column_values = get_column_values(database, table_name, column_name)
                for j in range(0, len(column_values), batch_size):
                    value_batch = column_values[j:j + batch_size]

                    for value in tqdm(value_batch, desc=f"Embedding {column_name} Values", leave=False):
                        metadata = {
                            "table_name": table_name,
                            "column_name": column_name,
                            "value": value
                        }
                        try:
                            vector = embedd_content(table_name)

                            if vector is not None:
                                upsert_record(vector, metadata, collection_name)
                            else:
                                raise ValueError(f"Embedding content failed for table: {table_name}")

                        except Exception as e:
                            print(f"Error embedding value {value} in column {column_name} of table {table_name}: {e}")
                            continue


def embedd_database(database: Database, include_values: bool):
    logging.info("Starting the embedding process...")
    try:
        create_collection(database.dbname)
        logging.info("Collection created successfully.")
    except Exception as e:
        logging.error(f"Error during collection creation: {e}")
        raise e
    try:
        embedd_table_names(database)
        logging.info("Tables embedded successfully.")
    except Exception as e:
        logging.error(f"Error during tables embedding: {e}")
        raise e
    try:
        embedd_columns(database)
        logging.info("Columns embedded successfully.")
    except Exception as e:
        logging.error(f"Error during columns embedding: {e}")
        raise e
    if include_values:
        try:
            embedd_string_values(database)
            logging.info("Values embedded successfully.")
        except Exception as e:
            logging.error(f"Error during values embedding: {e}")
            raise e
