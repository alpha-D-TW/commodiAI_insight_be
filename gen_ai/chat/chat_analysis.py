import json

import pandas as pd

from gen_ai.chat import chat_func
from gen_ai.prompts.analyse import prompt_analysis


def chat_analysis(model, question, data, is_english):
    prompted_question = prompt_analysis(data, question, is_english)
    _, answer = chat_func(model, prompted_question)
    return answer


def chat_all_analysis(model, question, data, is_english):
    result = []
    for v in data:
        df = pd.read_json(json.dumps(v["data"]), orient="records")
        if df.empty:
            result.append("")
        else:
            latest_10_rows = df.sort_values(by=v["dateColumn"], ascending=False).head(10)
            result.append(chat_analysis(model, question, latest_10_rows.to_string(index=False), is_english))
    return result
