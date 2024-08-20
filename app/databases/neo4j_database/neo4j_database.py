from typing import Any, Dict, List, Optional

from neo4j import GraphDatabase
from pydantic import BaseModel
from neo4j.graph import Node as Neo4jNode

from app.models.database import Column, Table

uri = "bolt://localhost:7687"
username = "neo4j"
password = "Test09875"

driver = GraphDatabase.driver(uri, auth=(username, password))


class Node(BaseModel):
    type: str
    properties: Dict[str, Any]


def create_node_from_neo4j(neo4j_node: Neo4jNode) -> Node:
    data = {
        'type': next(iter(neo4j_node.labels)),
        'properties': neo4j_node._properties
    }
    return Node.parse_obj(data)


class Relationship(BaseModel):
    type: str
    properties: Optional[Dict[str, Any]] = None


def _transform_properties(properties: Dict[str, Any]) -> str:
    return ", ".join(f"{key}: '{value}'" for key, value in properties.items())


def create_node(node: Node):
    with driver.session() as session:
        if not node_exists(node):
            properties = _transform_properties(node.properties)
            cypher_query = f"CREATE (n:{node.type} {{{properties}}}) RETURN n"
            session.run(cypher_query)


def node_exists(node: Node) -> bool:
    with driver.session() as session:
        label = node.type
        label_existence_query = f"CALL db.labels() YIELD label RETURN label"
        labels_result = session.run(label_existence_query)
        labels = [record["label"] for record in labels_result]

        if label not in labels:
            return False

        properties = _transform_properties(node.properties)
        cypher_query = f"MATCH (n:{label} {{{properties}}}) RETURN n"
        result = session.run(cypher_query, parameters={"properties": properties})
        return result.single() is not None


def create_relationship(
        node1: Node,
        node2: Node,
        relationship: Relationship,
):
    if not node_exists(node1):
        create_node(node1)
    if not node_exists(node2):
        create_node(node2)

    with driver.session() as session:
        properties1 = _transform_properties(node1.properties)
        properties2 = _transform_properties(node2.properties)
        relationship_prop = _transform_properties(relationship.properties) if relationship.properties else ""

        relationship_properties_clause = f" {{{relationship_prop}}}" if relationship_prop else ""
        cypher_query = f"""
        MATCH (node1:{node1.type} {{{properties1}}}), (node2:{node2.type} {{{properties2}}})
        CREATE (node1)-[:{relationship.type}{relationship_properties_clause}]->(node2)
        """

        session.run(cypher_query)


def find_shortest_path(
        table1: str,
        table2: str,
        collection_name: str
) -> List[Node]:
    start_node = Node(
        type="Table",
        properties={"name": table1, "collection_name": collection_name},
    )

    end_node = Node(
        type="Table",
        properties={"name": table2, "collection_name": collection_name}
    )

    if node_exists(start_node) and node_exists(end_node):
        start_prop = _transform_properties(start_node.properties)
        end_prop = _transform_properties(end_node.properties)
        query = f"""
        MATCH (start:{start_node.type} {{{start_prop}}}), (end:{end_node.type} {{{end_prop}}}),
        p = shortestPath((start)-[:FOREIGN_KEY|REFERENCED_BY*]-(end))
        RETURN p
        """

        with driver.session() as session:
            result = session.run(query)
            path = result.single()

            if path:
                nodes = path["p"].nodes
                return [create_node_from_neo4j(node) for node in nodes]
            else:
                return []
    else:
        return []


def get_table_from_node(table_name: str, collection_name: str) -> Optional[Table]:
    node = Node(
        type="Table",
        properties={"name": table_name, "collection_name": collection_name}
    )

    if node_exists(node):
        properties_str = _transform_properties(node.properties)
        query = f"""
            MATCH (n:{node.type} {{{properties_str}}})-[:HAS_COLUMN]-(column)
            RETURN column
        """

        with driver.session() as session:
            result = session.run(query)
            columns_nodes: List[Neo4jNode] = [record['column'] for record in result]

            columns = tuple(Column(**col._properties) for col in columns_nodes)
            return Table(name=table_name, columns=columns)
    else:
        print("The node does not exist.")
        return None


def get_tables_in_path(
        table1: str,
        table2: str,
        collection_name: str
) -> List[Table | None]:
    nodes = find_shortest_path(table1, table2, collection_name)
    return [get_table_from_node(node.properties["name"], collection_name) for node in nodes]
