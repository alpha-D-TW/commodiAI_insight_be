from gen_ai.chat.chat_excel import chat_excel, chat_json
from gen_ai.chat.chat_pdf import chat_pdf
from gen_ai.util import is_not_empty_array


def chat(model, question, history):
    # domain_result = chat_json(model, question)
    # if domain_result and is_not_empty_array(domain_result["answer"]):
    #     return domain_result
    excel_result = chat_excel(model, question)
    if excel_result and is_not_empty_array(excel_result["answer"]):
        return excel_result
    return chat_pdf(model, question, history)
