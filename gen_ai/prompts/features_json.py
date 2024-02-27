import os

from langchain.prompts import PromptTemplate

from gen_ai.util import load_json_file, is_not_empty_str

prompt_indexes_template = """
请根据已知信息和问题，从下面指标列表中找出能够回答问题的一组或多组指标。不需要回答问题，不要提供任何解释，只回答找到的指标名称。如果提取不到就回答“无”。

指标包括：
{indexes}

问题：{question}

提取的指标是：
"""

PARAMS_INDEXES_PROMPT = PromptTemplate.from_template(prompt_indexes_template)

prompt_tags_template = """
请根据已知信息和问题，从下面指标列表中找出最接近问题的一组或多组指标。不需要回答问题，不要提供任何解释，只回答找到的指标名称。如果提取不到就回答“无”。

指标包括：
{indexes}

已知信息：{context}

问题：{question}

提取的指标是：
"""

PARAMS_TAGS_PROMPT = PromptTemplate.from_template(prompt_tags_template)

prompt_sheet_template = """
请从下面指标列表中找出最接近问题的一个指标并回答指标的名称。不需要回答问题，不要提供任何解释，只回答找到的指标名称。如果提取不到就回答“无”。

指标名称：指标描述
{indexes}

问题：{question}

提取的指标名称是：
"""

PARAMS_SHEET_PROMPT = PromptTemplate.from_template(prompt_sheet_template)


def get_sheet_description(sheet):
    if sheet and "sheet_name" in sheet:
        return sheet["sheet_description"] if "sheet_description" in sheet and is_not_empty_str(
            sheet["sheet_description"]) else sheet["sheet_name"]
    return ""


def params_excel_sheet_json(batch, question: str):
    sheets = []
    for q in batch:
        sheet_description = get_sheet_description(q)
        if sheet_description:
            sheets.append([q["sheet_name"], sheet_description])
    sheets_str = list(map(lambda v: "：".join(v), sheets))
    return (
        PARAMS_SHEET_PROMPT.format(indexes="\n".join(sheets_str), question=question),
        list(map(lambda v: v[0], sheets)),
    )


def params_excel_columns_json(batch, question: str, sheet_name: str):
    current_sheet = list(filter(lambda q: q["sheet_name"] == sheet_name, batch))[0]
    available_columns = list(
        filter(
            lambda c: isinstance(c, str) or (isinstance(c, dict) and "column" in c and is_not_empty_str(c["column"])),
            current_sheet["columns"]))
    columns = list(
        map(lambda c: {"column": c["column"],
                       "description": c["description"] if "description" in c and is_not_empty_str(c["description"]) else
                       c["column"],
                       "unit": ""} if isinstance(c, dict) else {"column": c,
                                                                "description": c,
                                                                "unit": ""},
            available_columns))
    columns_arr = list(map(lambda c: c["description"], columns))
    return (
        PARAMS_TAGS_PROMPT.format(indexes="\n".join(columns_arr), question=question,
                                  context=get_sheet_description(current_sheet)),
        current_sheet,
        columns
    )


def params_questions_json(questions, question: str):
    return PARAMS_INDEXES_PROMPT.format(indexes="\n".join(questions), question=question)
