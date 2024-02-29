from langchain_community.embeddings import HuggingFaceBgeEmbeddings

from .config import envs


def __build_embedding(
    model_kwargs={"device": "cpu"}, encode_kwargs={"normalize_embeddings": True}
):
    """
    set normalize_embeddings as True to compute cosine similarity
    """
    embeddings = HuggingFaceBgeEmbeddings(
        model_name=envs.get("embedding_model_name"),
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
    )
    return embeddings


embeddings = __build_embedding()
