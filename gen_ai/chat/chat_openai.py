from datetime import datetime
from typing_extensions import override

from gen_ai.chat.chat_bot import ChatBot
from gen_ai.config import secrets
from openai import OpenAI


class ChatOpenAIAPI(ChatBot):
    @override
    def infer(self, question: str, history: list = None):
        print(f"start inference use openai at: {datetime.now()}")

        api_key = secrets["openaiApiKey"] if "openaiApiKey" in secrets else None

        if api_key:
            client = OpenAI(
                api_key=api_key
            )

            print(f'Question is {question}')
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": question},
                ]
            )

            return [question, response.choices[0].message.content]
        else:
            raise Exception('OpenAI API key not found')
