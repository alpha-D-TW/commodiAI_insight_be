from gen_ai.chat.chat_bot import ChatBot
from gen_ai.chat.chat_qwen import ChatQwenAPI
from gen_ai.chat.chat_wenxin import ChatWenxin
from gen_ai.chat.chat_openai import ChatOpenAIAPI


class ChatAgent:
    @staticmethod
    def build_instance(agent_name) -> ChatBot:
        if agent_name == "wenxin":
            return ChatWenxin()
        elif agent_name == "qwen":
            return ChatQwenAPI()
        elif agent_name == "gpt-3.5-turbo":
            return ChatOpenAIAPI()
        raise Exception(f"Unknown chat agent {agent_name}")
