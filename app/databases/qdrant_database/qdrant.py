import json
import logging
from typing import List, Dict, Any, Optional
import uuid

from qdrant_client import QdrantClient, models
import requests

from app.models.outputs import SearchOutput
from app.openai.embedding import embedd_content

client = QdrantClient(url="http://localhost:6333", timeout=60)


def create_collection(collection_name: str):
    try:
        logging.info(f"Creating collection: {collection_name}")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
        )
        logging.info(f"Collection {collection_name} created.")
    except Exception as e:
        logging.error(f"Failed to create collection {collection_name}: {e}")
        raise


def get_collection(collection_name: str):
    return client.get_collection(collection_name)


def upsert_record(
        vector: List[float],
        metadata: Dict[str, Any],
        collection_name: str
) -> None:
    unique_id = str(uuid.uuid4())

    client.upsert(
        collection_name=collection_name,
        points=[
            models.PointStruct(
                id=unique_id,
                payload=metadata,
                vector=vector,
            ),
        ],
    )


def search_embeddings(
        query: str,
        collection_name: str,
        search_type: Optional[str] = None,
        score_threshold: float = 0.6,
        top_k: int = 5
) -> list[SearchOutput]:
    headers = {
        "Content-Type": "application/json"
    }

    filter_condition = None
    if search_type == "table_name":
        filter_condition = {
            "must": [
                {"is_empty": {"key": "column_name"}}
            ]
        }
    elif search_type == "column_name":
        filter_condition = {
            "must": [
                {"is_empty": {"key": "value"}},
            ],
            "must_not": [
                {"is_empty": {"key": "column_name"}}
            ]
        }
    elif search_type == "value":
        filter_condition = {
            "must_not": [
                {"is_empty": {"key": "value"}}
            ]
        }

    query_vector = embedd_content(query)

    payload = {
        "vector": query_vector,
        "limit": top_k,
        "with_payload": True,
        "filter": filter_condition,
        "score_threshold": score_threshold
    }

    response = requests.post(
        f"http://localhost:6333/collections/{collection_name}/points/search",
        headers=headers,
        data=json.dumps(payload)
    )

    response.raise_for_status()
    search_result = response.json()

    results = []
    for point in search_result["result"]:
        result = SearchOutput(
            table_name=point['payload'].get("table_name"),
            column_name=point['payload'].get("column_name"),
            value=point['payload'].get("value"),
            score=point['score']
        )
        results.append(result)

    return results


def extract_search_objects(entities: List[str], collection_name: str):
    tables_objs, columns_objs, values_objs = [], [], []

    for entity in entities:
        tables_objs.extend(search_embeddings(query=entity, search_type="table_name", score_threshold=0.2, top_k=3,
                                             collection_name=collection_name))
        columns_objs.extend(search_embeddings(query=entity, search_type="column_name", score_threshold=0.2, top_k=3,
                                              collection_name=collection_name))
        values_objs.extend(search_embeddings(query=entity, search_type="value", score_threshold=0.8, top_k=3,
                                             collection_name=collection_name))

    return tables_objs, columns_objs, values_objs
