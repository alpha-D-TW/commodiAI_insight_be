from datetime import datetime
from http import HTTPStatus
import dashscope
from typing_extensions import override

from gen_ai.chat.chat_bot import ChatBot
from gen_ai.config import secrets
from gen_ai.util import is_not_empty_array


class ChatQwenAPI(ChatBot):
    @override
    def infer(self, question: str, history: list = None):
        print(f"start inference at: {datetime.now()}")

        api_key = secrets["qwenApiKey"] if "qwenApiKey" in secrets else None

        if api_key:
            dashscope.api_key = api_key

            last_message = {"role": "user", "content": question}
            messages = [last_message]

            if is_not_empty_array(history):
                history.append(last_message)
                messages = history

            gen = dashscope.Generation()
            response = gen.call(
                dashscope.Generation.Models.qwen_turbo,
                messages=messages,
                result_format='message',  # set the result is message format.
            )

            if response.status_code == HTTPStatus.OK:
                choice = response.output.choices[0]
                answer = choice.message.content
                return [question, answer]
            else:
                raise Exception(f'{response.code}: {response.message}')
        else:
            raise Exception('QWEN API key not found')
