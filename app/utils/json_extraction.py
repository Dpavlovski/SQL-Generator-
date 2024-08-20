import json
from typing import Any


def trim_and_load_json(input_string: str) -> Any:
    start = input_string.find("{")
    end = input_string.rfind("}") + 1

    if end == 0 and start != -1:
        input_string = input_string + "}"
        end = len(input_string)

    json_str = input_string[start:end] if start != -1 and end != 0 else ""

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        raise ValueError("The output is not a valid JSON.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")
