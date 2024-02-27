from gen_ai.chat.chat_bot import ChatBot
from gen_ai.chat.chat_qwen import ChatQwenAPI
from gen_ai.chat.chat_wenxin import ChatWenxin


class ChatAgent:
    @staticmethod
    def build_instance(agent_name) -> ChatBot:
        if agent_name == "wenxin":
            return ChatWenxin()
        elif agent_name == "qwen":
            return ChatQwenAPI()
        raise Exception(f"Unknown chat agent {agent_name}")
