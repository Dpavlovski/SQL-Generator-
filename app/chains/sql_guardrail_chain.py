from app.openai.chat import chat_with_openai
from app.templates.guardrails import sql_query_guardrail
from app.utils.json_extraction import trim_and_load_json


def guardrail_chain(
        query: str
) -> dict:
    prompt = sql_query_guardrail(question=query)
    output = chat_with_openai(message=prompt) or ""
    extracted_info = trim_and_load_json(output)

    if not isinstance(extracted_info, dict) or "verdict" not in extracted_info:
        raise ValueError("Invalid extracted verdict format.")

    return extracted_info
