import io
import logging
import os
from io import StringIO

import pandas as pd
from fastapi import UploadFile

from gen_ai.aws import get_s3_client, upload_file_to_s3, get_file_from_s3, upload_csv_buffer_to_s3
from gen_ai.config import envs
from gen_ai.db import insert_knowledge, update_knowledge
from gen_ai.load_doc import load_pdf_doc, load_json_doc
from gen_ai.models.knowledge import KnowledgeStatus, KnowledgeType
from gen_ai.open_search.open_search_vector_search import OpenSearchVectorSearch, get_os_index
from gen_ai.util import build_s3_obj_key, load_json_file


def __load_os_file(db, knowledge_id, filename, file_type, s3_key, model):
    try:
        if file_type == 'pdf':
            ids = load_pdf_doc(s3_key, filename, model)
        else:
            ids = load_json_doc(s3_key, filename)
        update_knowledge(db, knowledge_id, status=KnowledgeStatus.OS_LOAD_SUCCEED, embedding_ids=",".join(ids))
        return ids
    except Exception as ex:
        print("Exception:", str(ex))
        update_knowledge(db, knowledge_id, status=KnowledgeStatus.OS_LOAD_FAILED)


def __load_excel(db, knowledge_id, file_name, s3_key):
    try:
        content = get_file_from_s3(s3_key)
        config_name, _ = os.path.splitext(file_name)
        sheet_configs = load_json_file(
            os.path.join(os.path.dirname(__file__), f"./data_config/{config_name}.json")
        )
        csv_keys = []
        for config in sheet_configs:
            df = pd.read_excel(
                io.BytesIO(content),
                sheet_name=config["sheet_name"],
                skiprows=config.get("skiprows"),
                index_col=0,
            )
            df = df.transpose()
            df.insert(0, "指标日期", df.index)
            df = df.reset_index(drop=True)
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_key = build_s3_obj_key(
                file_name=config_name,
                sheet_name=config["sheet_name"],
            )
            csv_keys.append(csv_key)
            upload_csv_buffer_to_s3(s3_key=csv_key, buffer=csv_buffer.getvalue())
        update_knowledge(db, knowledge_id, KnowledgeStatus.CSV_LOAD_SUCCEED)
        return csv_keys
    except Exception as ex:
        logging.error(f"Error when load excel: {str(ex)}")
        update_knowledge(db, knowledge_id, KnowledgeStatus.CSV_LOAD_FAILED)


def load_file(db, knowledge_id, filename, file_type, s3_key, model):
    if file_type in ["pdf", "json"]:
        return __load_os_file(db, knowledge_id, filename, file_type, s3_key, model)

    if file_type in ["xls", "xlsx"]:
        return __load_excel(db, knowledge_id, filename, s3_key)

    return f"no handler for {file_type}"


def load_files(db, files: list[UploadFile], knowledge_type: KnowledgeType):
    for f in files:
        try:
            file_extension = f.filename.split(".")[-1]
            if file_extension in ['xls', 'xlsx', 'pdf', 'json']:
                s3_key = f'knowledge/raw/{knowledge_type}/{f.filename}'
                upload_file_to_s3(s3_key=s3_key, file_obj=f.file)
                knowledge_id = insert_knowledge(db=db, file_name=f.filename, s3_key=s3_key,
                                                knowledge_type=knowledge_type)
                load_file(db, knowledge_id, f.filename, file_extension, s3_key, 'wenxin')
        except Exception as ex:
            logging.error(f'Error occurred when load file {f.filename}: {str(ex)}')


def delete_docs(file_type, ids):
    if ids:
        client = OpenSearchVectorSearch(get_os_index(file_type))
        return client.delete_doc(ids)
    return "no id need delete"


def delete_index():
    client = OpenSearchVectorSearch(get_os_index("json"))
    return client.delete_index()


def read_csv_from_s3(file_key):
    s3_resource = get_s3_client()
    s3_object = s3_resource.Object(envs.get("s3_bucket"), file_key).get()
    s3_data = s3_object["Body"].read().decode("utf-8")
    df = pd.read_csv(StringIO(s3_data))
    return df
