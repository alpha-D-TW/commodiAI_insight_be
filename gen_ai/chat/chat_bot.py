from abc import ABC, abstractmethod


class ChatBot(ABC):
    @abstractmethod
    def infer(self, question: str, history: list = None):
        pass
