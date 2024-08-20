from app.databases.neo4j_database.neo4j_database import create_relationship, Node, Relationship, create_node

from app.databases.postgres_database.service import get_tables_with_foreign_keys, get_tables, get_columns_by_table
from app.models.database import Database, ForeignKey


def insert_tables_with_foreign_keys(database: Database):
    tables = get_tables_with_foreign_keys(database)
    for table_name, foreign_keys in tables.items():
        fks = [ForeignKey(foreign_key) for foreign_key in foreign_keys]

        for fk in fks:
            fk_dump = fk.model_dump()
            fk_dump["collection_name"] = database.dbname

            create_relationship(
                node1=Node(
                    type="Table",
                    properties={"name": fk.to_table, "collection_name": database.dbname}
                ),
                node2=Node(
                    type="Table",
                    properties={"name": table_name, "collection_name": database.dbname}
                ),
                relationship=Relationship(
                    type="FOREIGN_KEY",
                    properties=fk_dump
                )
            )

            create_relationship(
                node1=Node(
                    type="Table",
                    properties={"name": table_name, "collection_name": database.dbname}
                ),
                node2=Node(
                    type="Table",
                    properties={"name": fk.to_table, "collection_name": database.dbname}
                ),
                relationship=Relationship(
                    type="REFERENCED_BY",
                    properties=fk_dump
                )
            )

        if len(fks) == 0:
            create_node(
                node=Node(
                    type="Table",
                    properties={"name": table_name, "collection_name": database.dbname}
                )
            )


def insert_columns(database: Database):
    tables = get_tables(database)
    for table_name in tables:
        columns = get_columns_by_table(database, table_name)

        for column in columns:
            column_dump = column.model_dump()
            column_dump["collection_name"] = database.dbname

            create_relationship(
                node1=Node(
                    type="Table",
                    properties={"name": table_name, "collection_name": database.dbname}
                ),
                node2=Node(
                    type="Column",
                    properties=column_dump
                ),
                relationship=Relationship(
                    type="HAS_COLUMN",
                    properties=None
                )
            )
