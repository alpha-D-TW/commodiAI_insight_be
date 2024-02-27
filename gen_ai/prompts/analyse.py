from langchain.prompts import PromptTemplate

prompt_analyse_template = """
你是一个钢铁行业专家，请对下面数据进行简短而专业的走势分析。{language_requirement}

数据表示：
{question}

数据包括：
{data}
"""

PARAMS_ANALYSE_PROMPT = PromptTemplate.from_template(prompt_analyse_template)


def prompt_analysis(data, question: str, is_english):
    return PARAMS_ANALYSE_PROMPT.format(data=data, question=question,
                                        language_requirement="请用英文回答。" if is_english else "")
