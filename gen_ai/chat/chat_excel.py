from gen_ai.chat import chat_func
from gen_ai.models.answer import ChatAnswerType
from gen_ai.prompts import params_excel_columns_json
from gen_ai.prompts.features_json import params_excel_sheet_json, params_questions_json
from gen_ai.retriever import search_json_doc
from gen_ai.util import build_s3_obj_key, load_single_batch_config, is_not_empty_array
from gen_ai.util import load_merged_batch_config

batch = load_merged_batch_config()


def chat_json(model, question):
    top10_questions = search_json_doc(question)
    top10_titles = list(map(lambda x: x["title"], top10_questions))
    domain_question = params_questions_json(top10_titles, question)
    _, domain_answer = chat_func(model, domain_question)
    final_questions = list(filter(lambda x: x["title"] in domain_answer, top10_questions))
    print('try to find domain', domain_question, domain_answer,
          list(filter(lambda x: x in domain_answer, top10_titles)))
    return {
        "type": ChatAnswerType.JSON,
        "question": question,
        "answer": prompt_excels(final_questions) if is_not_empty_array(final_questions) else None,
    }


def chat_excel(model, question):
    (sheet, columns) = chat_excel_params(model, question)
    result = None
    if sheet and is_not_empty_array(columns):
        result = [prompt_excel(sheet, columns)]
    return {
        "type": ChatAnswerType.JSON,
        "question": question,
        "answer": result,
    }


def chat_excel_params(model, question):
    (sheet_question, sheet_names) = params_excel_sheet_json(batch, question)
    _, sheet_answer = chat_func(model, sheet_question)
    final_sheet = next(filter(lambda x: x in sheet_answer, sheet_names), None)
    print('try to find sheet', sheet_question, sheet_answer, final_sheet)
    if final_sheet:
        (col_question, sheet, columns) = params_excel_columns_json(
            batch, question=question, sheet_name=final_sheet
        )
        _, col_answer = chat_func(model, col_question)
        columns = list(filter(lambda x: x["description"] in col_answer, columns))
        print('try to find columns', col_question, col_answer, columns)
        return sheet, columns
    return None, None


def prompt_excel(sheet, columns):
    return {
        "s3key": build_s3_obj_key(
            file_name=sheet["file_name"], sheet_name=sheet["sheet_name"]
        ),
        "dateColumn": "指标日期",
        "period": sheet["period"],
        "unit": sheet["unit"] if "unit" in sheet else None,
        "columns": columns,
    }


def prompt_excels(sheets):
    result = []
    for s in sheets:
        batch_config = load_single_batch_config(s["file_name"])
        sheet_config = next(filter(lambda x: x["sheet_name"] == s["sheet_name"], batch_config), None)
        result.append({
            **s,
            **prompt_excel(sheet_config, s["columns"]),
        })
    return result
