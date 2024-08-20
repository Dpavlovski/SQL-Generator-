import json

from app.chains.create_sql_query_chain import create_sql_query
from app.chains.sql_guardrail_chain import guardrail_chain
from fastapi import APIRouter

router = APIRouter()


@router.post("/{collection_name}")
def get_sql_query(collection_name: str, prompt: str):
    result = guardrail_chain(prompt)
    if result['verdict'] == "no":
        return {"message": result['reason']}
    response = create_sql_query(collection_name, prompt)

    try:
        response_json = json.loads(response)
    except (json.JSONDecodeError, TypeError):
        return response

    return response_json
