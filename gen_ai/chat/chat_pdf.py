import re

from gen_ai.chat import chat_func
from gen_ai.models.answer import ChatAnswerType
from gen_ai.open_search.template import query_by_params
from gen_ai.prompts import (
    DATE_RANGE_PARAMS,
    prompt_context_chat,
    prompt_params_json,
)
from gen_ai.retriever import search_pdf_doc
from gen_ai.util import check_params_available, load_json


def chat_pdf(model, question, history):
    dates = chat_date_params(model, question)
    context = search_pdf_doc(question, query_by_params(dates, None))
    final_question = prompt_context_chat(question, context)
    _, answer = chat_func(model, final_question, history)
    return {
        "type": ChatAnswerType.STRING,
        "question": final_question,
        "answer": answer,
    }


def chat_for_params_with_retry(model, question, params_arr):
    max_retry_times = 3
    params = {}

    for _ in range(max_retry_times):
        params = chat_for_dict_params(model, question)
        if check_params_available(params_arr, params):
            break

    return params


def chat_date_params(model, question):
    params_question = prompt_params_json(question=question, params=DATE_RANGE_PARAMS)
    dates = chat_for_dict_params(model, params_question)
    return dates


def chat_for_dict_params(model, question):
    answer = chat_func(model, question)[1]
    match = re.search(r"```(?:json)?([\s\S]*?)```", answer)
    result = match.group(1) if match else answer
    return load_json(result)
