import json
from datetime import date

from langchain.prompts import PromptTemplate

prompt_params_template = """
假设今天是{today}，请从下面问题中提取出所需要的参数并按照要求的JSON format回答。不需要回答问题，只提取问题中的参数，如果提取不到就回答"不知道"。
JSON format是{schema}, 其中date格式为yyyy-MM-dd。
问题：{question}
"""
PARAMS_JSON_PROMPT = PromptTemplate.from_template(prompt_params_template)


def prompt_params_json(question: str, params: list[str]):
    today = date.today().strftime("%Y-%m-%d")
    schema = {key: "" for key in params}
    return PARAMS_JSON_PROMPT.format(
        today=today, question=question, schema=json.dumps(schema)
    )
