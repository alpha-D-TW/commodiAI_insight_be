import os

from dotenv import load_dotenv, set_key, find_dotenv

load_dotenv()

envs = {
    "aws_region": os.getenv("AWS_DEFAULT_REGION", "cn-north-1"),
    "opensearch_url": os.getenv("OPENSEARCH_URL", "https://localhost:9200"),
    "opensearch_pdf_index": os.getenv("OPENSEARCH_PDF_INDEX", "pdf-index"),
    "opensearch_json_index": os.getenv("OPENSEARCH_JSON_INDEX", "json-index"),
    "text_splitter_chunk_size": int(os.getenv("SPLITTER_CHUNK_SIZE", 1000)),
    "text_splitter_chunk_overlap": int(os.getenv("SPLITTER_CHUNK_OVERLAP", 100)),
    "embedding_model_name": os.getenv(
        "EMBEDDING_MODEL_NAME", "./embeddings_model/BAAI_bge-base-zh-v1.5"
    ),
    "s3_endpoint": os.getenv("S3_ENDPOINT", "http://localhost:4566"),
    "s3_bucket": os.getenv("S3_BUCKET", "chat-bucket"),
}

dbs = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "database": os.getenv("DB_NAME", "chat_db"),
}

secrets = {
    "wenxinApiKey": os.getenv("WENXIN_API_KEY"),
    "wenxinApiSecret": os.getenv("WENXIN_API_SECRET"),
    "wenxinAccessToken": os.getenv("WENXIN_ACCESS_TOKEN"),
    "qwenApiKey": os.getenv("QWEN_API_KEY"),
    "openaiApiKey": os.getenv("OPEN_AI_API_KEY"),
}


def is_local_env():
    return os.getenv("DEPLOY_ENV") == "local"


def update_wenxin_token(token):
    os.putenv("wenxinAccessToken", token)
    dotenv_file = find_dotenv()
    set_key(dotenv_path=dotenv_file, key_to_set="WENXIN_ACCESS_TOKEN", value_to_set=token)
