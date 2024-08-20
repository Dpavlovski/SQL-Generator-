from typing import List

from app.templates.ner_prompt import ner_prompt
from app.openai.chat import chat_with_openai
from app.utils.json_extraction import trim_and_load_json


def ner_chain(
        query: str
) -> List[str]:
    prompt = ner_prompt(text=query)
    chat_output = chat_with_openai(prompt) or ""
    extracted_info = trim_and_load_json(input_string=chat_output)

    if not isinstance(extracted_info, dict) or "information" not in extracted_info:
        raise ValueError("Invalid extracted information format.")

    return extracted_info["information"]
