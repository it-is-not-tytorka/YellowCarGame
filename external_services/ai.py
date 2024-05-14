from openai import AsyncOpenAI
from config_data.config import load_config, Config
import base64
import aiohttp

config: Config = load_config()

API_KEY = config.open_ai.openai_key

client = AsyncOpenAI(api_key=API_KEY)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


async def recognize_car(image_path: str) -> str:
    base64_image = encode_image(image_path)

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

    payload = {
        "model": "gpt-4-turbo",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Is there a real yellow car on a photo? Answer only 1 if True or 0 if False.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            },
        ],
        "max_tokens": 100,
        "temperature": 0,
    }
    # send async request gpt-4-turbo to get 1 if there's a yellow car or 0 in another way
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        ) as response:
            response_data = await response.json()
    return response_data["choices"][0]["message"]["content"]
