from app.models.outputs import ValidationOutput
from app.openai.chat import chat_with_openai
from app.templates.validate_info_prompt import validate_info_prompt
from app.utils.json_extraction import trim_and_load_json


def validate_info_chain(
        table_info: str,
        question: str
) -> ValidationOutput:
    prompt = validate_info_prompt(table_info=table_info, question=question)
    chat_output = chat_with_openai(prompt) or ""
    json_data = trim_and_load_json(input_string=chat_output)
    validation_output = ValidationOutput(**json_data)

    return validation_output
