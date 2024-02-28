from langchain.prompts import PromptTemplate

prompt_template = """
请你尝试扮演一名大宗商品期货分析师，那么根据下面已知信息，简洁和专业的来回答用户的问题，如果已知信息回答不了，就说不知道。

{context}

问题: {question}
"""
CONTEXT_PROMPT = PromptTemplate.from_template(prompt_template)


def prompt_context_chat(question, context):
    return CONTEXT_PROMPT.format(context=context, question=question)
