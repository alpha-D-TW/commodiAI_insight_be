from gen_ai.chat.chat_agent import ChatAgent


def chat_func(model, question, history=None):
    agent = ChatAgent.build_instance(model)
    return agent.infer(question, history)
