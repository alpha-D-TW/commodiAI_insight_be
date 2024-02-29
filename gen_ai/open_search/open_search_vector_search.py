import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from opensearchpy import RequestsHttpConnection, OpenSearch, exceptions
from opensearchpy.helpers import bulk
from langchain.schema import Document

from gen_ai.config import envs
from gen_ai.embedding_model import embeddings
from gen_ai.open_search.credentials import get_credentials, should_verify_certs
from gen_ai.open_search.template import query_script, text_mapping

pdf_index = envs.get("opensearch_pdf_index")
json_index = envs.get("opensearch_json_index")


def get_os_index(file_type="pdf"):
    return json_index if file_type == "json" else pdf_index


def _bulk_ingest_embeddings(
        client: Any,
        index_name: str,
        embedding_result: List[List[float]],
        docs: List[Document],
        file_params,
        mapping: dict,
        max_chunk_bytes: Optional[int] = 1 * 1024 * 1024,
) -> List[str]:
    requests = []
    return_ids = []
    texts = [doc.page_content for doc in docs]
    metadatas = [doc.metadata for doc in docs]
    params = [param for param in file_params]

    try:
        client.indices.get(index=index_name)
    except exceptions.NotFoundError:
        client.indices.create(index=index_name, body=mapping)

    for i, text in enumerate(texts):
        metadata = metadatas[i] if metadatas and metadatas[i] else {}
        param = params[i] if params and params[i] else {}
        _id = str(uuid.uuid4())
        request = {
            "_id": _id,
            "_op_type": "index",
            "_index": index_name,
            "vector_field": embedding_result[i],
            "text": text,
            "metadata": metadata,
            "page_number": metadata['page_number'],
        }
        requests.append({**request, **param})
        return_ids.append(_id)
    bulk(client, requests, max_chunk_bytes=max_chunk_bytes)
    client.indices.refresh(index=index_name)
    return return_ids

class OpenSearchVectorSearch:
    def __init__(self, index_name):
        opensearch_url = envs.get("opensearch_url")
        use_ssl = should_verify_certs(opensearch_url)
        self.client = OpenSearch(
            hosts=[opensearch_url],
            http_auth=get_credentials(),
            timeout=300,
            use_ssl=use_ssl,
            verify_certs=use_ssl,
            ssl_assert_hostname=use_ssl,
            ssl_show_warn=use_ssl,
            connection_class=RequestsHttpConnection,
        )
        self.embedding_function = embeddings
        self.index_name = index_name

    def add_texts(
            self,
            docs: List[Document],
            file_params
    ) -> List[str]:
        texts = [doc.page_content for doc in docs]
        embedding_result = self.embedding_function.embed_documents(list(texts))
        dim = len(embedding_result[0])
        max_chunk_bytes = 1 * 1024 * 1024

        mapping = text_mapping(dim)

        return _bulk_ingest_embeddings(
            self.client,
            self.index_name,
            embedding_result,
            docs=docs,
            mapping=mapping,
            max_chunk_bytes=max_chunk_bytes,
            file_params=file_params
        )

    def similarity_search_with_score(
            self, query: str, k: int = 4, pre_filter: Optional[Dict] = None,
    ) -> List[Tuple[Document, float]]:
        embedding = self.embedding_function.embed_query(query)
        search_query = query_script(
            embedding, k, pre_filter
        )

        response = self.client.search(index=self.index_name, body=search_query)
        hits = [hit for hit in response["hits"]["hits"]]

        return hits

    def delete_doc(self, ids):
        print(f"start delete_documents at: {datetime.now()}")
        for _id in ids:
            try:
                self.client.delete(index=self.index_name, id=_id)
            except exceptions.NotFoundError:
                print(f"Doc already deleted for {_id} in index {self.index_name}")

        print(f"end delete at: {datetime.now()}")
        return f"delete succeed for {ids}"

    def delete_index(self):
        print(f"start delete_index at: {datetime.now()}")
        try:
            self.client.indices.delete(index=self.index_name)
        except exceptions.NotFoundError:
            print(f"Index already deleted for {self.index_name}")
        print(f"end delete at: {datetime.now()}")
        return f"delete succeed for {self.index_name}"
