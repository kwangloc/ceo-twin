from langchain_openai import OpenAIEmbeddings

from langchain_qdrant import (
    FastEmbedSparse,
    QdrantVectorStore,
    RetrievalMode,
)

from retrieval.qdrant.config import Settings
from retrieval.qdrant.qdrant_store import get_client

class HybridRetriever:

    def __init__(
        self,
        settings: Settings,
    ):
        client = get_client(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key
        )

        self.store = QdrantVectorStore(
            client=client,
            collection_name=settings.collection_name,

            embedding=OpenAIEmbeddings(
                model=settings.embedding_model,
            ),

            sparse_embedding=FastEmbedSparse(
                model_name=settings.sparse_model,
            ),

            retrieval_mode=RetrievalMode.HYBRID,

            vector_name="dense",
            sparse_vector_name="sparse",
        )

    def retrieve(
        self,
        query: str,
        k: int,
    ):
        return self.store.similarity_search(
            query=query,
            k=k,
        )