import os
from typing import Optional

from dotenv import load_dotenv
import requests
import json


def chat_with_openai(
        message: str,
        system_message: str = "You are a helpful assistant."
) -> Optional[str]:
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    url = 'https://api.openai.com/v1/chat/completions'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_api_key}'
    }

    data = {
        'model': 'gpt-4o',
        'messages': [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": message
            }
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_data = response.json()
        return response_data['choices'][0]['message']['content']
    else:
        response.raise_for_status()
        return None
