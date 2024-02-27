import json
import logging
from typing import List
import requests
from langchain.embeddings.base import Embeddings
from langchain.pydantic_v1 import BaseModel

from gen_ai.wenxin.auth_wenxin import get_token_from_auth

logger = logging.getLogger(__name__)


def embedding_wenxin(access_token, texts: List[str]):
    response = call_wenxin_api(access_token, texts)
    if "data" in response and len(response["data"]) > 0:
        return response["data"][0]["embedding"]
    else:
        raise Exception(f'{response["error_code"]}: {response["error_msg"]}')


def call_wenxin_api(access_token: str, texts: List[str]):
    try:
        response = requests.post(
            f'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/embeddings/embedding-v1?access_token={access_token}',
            data=json.dumps({"input": texts}),
        )
        result = response.json()
        if "data" in result or "error_code" in result:
            return result
        else:
            raise Exception(f'Error occurred: {result}')
    except Exception as err:
        raise Exception(f'Error occurred: {err}')


def _get_len_safe_embeddings(access_token, texts: List[str]) -> List[List[float]]:
    _iter = range(len(texts))
    embeddings: List[List[float]] = []

    for i in _iter:
        response = embedding_wenxin(access_token, [texts[i]])
        embeddings.extend([response])

    return embeddings


class WenxinEmbeddings(BaseModel, Embeddings):

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        access_token = get_token_from_auth()
        texts = [t.replace("\n", " ") for t in texts]
        return _get_len_safe_embeddings(access_token, texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]
