from gen_ai.open_search.open_search_vector_search import OpenSearchVectorSearch, get_os_index
from gen_ai.util import is_not_empty_array, load_json


def search_pdf_doc(question, pre_filter):
    client = OpenSearchVectorSearch(get_os_index())
    result = client.similarity_search_with_score(question, pre_filter=pre_filter)

    content = ""
    reference = ""
    if is_not_empty_array(result):
        sorted_doc = sorted(
            result,
            key=lambda x: (
                x["_source"]["start_date"] if x["_source"]["start_date"] else "",
                x["_score"],
            ),
            reverse=True,
        )
        ## 只取了第一个
        source_ = sorted_doc[0]["_source"]
        content = source_["text"].replace("\n", "")
        reference = f'《{source_["filename"]}》第{source_["page_number"]}页'
    return [content, reference]


def search_json_doc(question):
    client = OpenSearchVectorSearch(get_os_index("json"))
    result = client.similarity_search_with_score(question, k=10, pre_filter=None)
    return list(map(lambda x: load_json(x["_source"]["text"]), result))
