import json

from langchain.prompts import PromptTemplate

prompt_date_template = """
请从下面信息中提取出开始日期和结束日期并按照以下JSON format回答。
JSON format是{schema}, 其中date格式为yyyy-MM-dd。

信息是：
{context}
"""
DATE_JSON_PROMPT = PromptTemplate.from_template(prompt_date_template)

DATE_RANGE_PARAMS = ["start_date", "end_date"]


def prompt_date_json(context):
    schema = {key: "" for key in DATE_RANGE_PARAMS}
    return DATE_JSON_PROMPT.format(context=context, schema=json.dumps(schema))
