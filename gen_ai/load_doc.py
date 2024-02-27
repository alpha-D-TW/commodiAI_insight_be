import io
import json
from datetime import datetime
from typing import List

import pandas as pd
from dateutil.relativedelta import relativedelta
from langchain.document_loaders import PyPDFLoader, S3FileLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from gen_ai.aws import get_file_from_s3
from gen_ai.chat.chat_pdf import chat_for_params_with_retry
from gen_ai.config import envs, is_local_env
from gen_ai.open_search.open_search_vector_search import OpenSearchVectorSearch, get_os_index
from gen_ai.prompts import DATE_RANGE_PARAMS, prompt_date_json
from gen_ai.util import load_json


def load_pdf_from_s3(s3_key):
    bucket_name = envs.get('s3_bucket')
    if bucket_name:
        if is_local_env():
            loader = S3FileLoader(bucket_name, s3_key,
                                  aws_access_key_id="test",
                                  aws_secret_access_key="test",
                                  endpoint_url=envs.get("s3_endpoint"),
                                  region_name=envs.get('aws_region'))
        else:
            loader = S3FileLoader(bucket_name, s3_key)
        return loader
    return None


def load_pdf_by_path(s3_key):
    s3_loader = load_pdf_from_s3(s3_key)
    loader = s3_loader if s3_loader is not None else PyPDFLoader(s3_key)
    return loader.load()


def load_json_by_path(s3_key):
    contents = get_file_from_s3(s3_key)
    return load_json(contents.decode('utf-8'))


def load_pdf_doc(s3_key, filename, model):
    print(f"start load_pdf_doc at: {datetime.now()}")
    documents = load_pdf_by_path(s3_key)
    contents = "\n".join([doc.page_content for doc in documents])
    merged_document = Document(page_content=contents, metadata=documents[0].metadata)
    print(f"pdf documents loaded at: {datetime.now()}")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=envs.get("text_splitter_chunk_size"),
        chunk_overlap=envs.get("text_splitter_chunk_overlap"),
        length_function=len,
        is_separator_regex=False,
    )
    docs = text_splitter.split_documents([merged_document])

    print(f"start add_documents at: {datetime.now()}")
    client = OpenSearchVectorSearch(get_os_index())
    file_params = get_file_params(filename, docs[0], model)
    result = client.add_texts(docs=docs, file_params=file_params)
    print(f"end add_documents at: {datetime.now()}")
    print(f"end load_pdf_doc at: {datetime.now()}")
    return result


def load_json_doc(s3_key, filename):
    client = OpenSearchVectorSearch(get_os_index("json"))
    print(f"delete json index at: {datetime.now()}")
    client.delete_index()
    print(f"start load_json_doc at: {datetime.now()}")
    documents = load_json_by_path(s3_key)
    print(f"json documents loaded at: {datetime.now()}")
    merged_document: List[Document] = list()
    for doc in documents:
        merged_document.append(
            Document(page_content=json.dumps(doc, ensure_ascii=False).encode('utf8'),
                     metadata={"source": s3_key, "title": doc["title"]}))
    result = client.add_texts(docs=merged_document, file_params={
        "file_type": "json",
        "filename": filename,
        "knowledge_type": "domain_knowledge",
    })
    print(f"end add_documents at: {datetime.now()}")
    print(f"end load_json_doc at: {datetime.now()}")
    return result


def get_file_params(filename, first_doc, model):
    question = prompt_date_json(context=first_doc.page_content)
    dates = chat_for_params_with_retry(model, question, DATE_RANGE_PARAMS)
    final_dates = {
        key: dates[key] if key in dates else None for key in DATE_RANGE_PARAMS
    }
    return {
        **final_dates,
        **first_doc.metadata,
        "file_type": "pdf",
        "filename": filename,
        "knowledge_type": "weekly_report",
    }


def load_csv_data(s3_key, columns, date_range_years):
    date_column = columns[0]
    start_date = ((datetime.now() - relativedelta(years=date_range_years if date_range_years > 0 else 4))
                  .replace(month=12, day=31).strftime("%Y-%m-%d"))
    file_content = get_file_from_s3(s3_key)
    if not file_content:
        return {}
    df = pd.read_csv(io.BytesIO(file_content), usecols=columns)
    final_df = df.sort_values(by=date_column)
    # final_df = df[df[date_column] >= start_date].sort_values(by=date_column)
    return load_json(final_df.to_json(orient="records", force_ascii=False))


def load_csv_files(json_answer):
    result = []
    for ans in json_answer:
        if ans and "s3key" in ans and "period" in ans:
            date_column = ans["dateColumn"]
            data_columns = [col for col in ans["columns"] if "column" in col]
            all_columns = [date_column] + [col["column"] for col in data_columns]
            result.append({
                "data": load_csv_data(ans["s3key"], all_columns,
                                      ans["dataRangeYears"] if "dataRangeYears" in ans else 4),
                "dateColumn": date_column,
                "columns": data_columns,
            })
        else:
            result.append({
                "data": [],
                "dateColumn": "",
                "columns": [],
            })
    return result
