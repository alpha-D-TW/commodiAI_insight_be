import json

import requests
from typing_extensions import override

from gen_ai.chat.chat_bot import ChatBot
from gen_ai.util import is_not_empty_array
from gen_ai.wenxin.auth_wenxin import get_token_from_auth, get_token_from_env


def handle_wenxin_response(question, response):
    if "result" in response and response["result"]:
        return [question, response["result"]]
    else:
        raise Exception(f'{response["error_code"]}: {response["error_msg"]}')


def call_wenxin_api(access_token, messages):
    try:
        response = requests.post(
            f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={access_token}",
            data=json.dumps({"messages": messages}),
        )
        result = response.json()
        if "result" in result or "error_code" in result:
            return result
        else:
            raise Exception(f"Error occurred: {result}")
    except Exception as err:
        raise Exception(f"Error occurred: {err}")


def chat_refresh_token(question, messages):
    new_token = get_token_from_auth()
    response = call_wenxin_api(new_token, messages)
    return handle_wenxin_response(question, response)


class ChatWenxin(ChatBot):
    @override
    def infer(self, question: str, history: list = None):
        last_message = {"role": "user", "content": question}
        messages = [last_message]
        if is_not_empty_array(history):
            history.append(last_message)
            messages = history
        access_token = get_token_from_env()
        if access_token:
            response = call_wenxin_api(access_token, messages)
            if "error_code" in response and 100 <= response["error_code"] <= 111:
                return chat_refresh_token(question, messages)
            else:
                return handle_wenxin_response(question, response)
        else:
            return chat_refresh_token(question, messages)
