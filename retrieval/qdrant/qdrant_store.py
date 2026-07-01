from qdrant_client import QdrantClient

from qdrant_client.models import (
    Distance,
    VectorParams,
    SparseVectorParams,
)

def get_client(url, api_key: str = None):
    return QdrantClient(url=url, api_key=api_key)

def ensure_collection(
    client,
    collection_name,
):
    existing = {
        c.name
        for c in client.get_collections().collections
    }

    if collection_name in existing:
        return

    client.create_collection(
        collection_name=collection_name,

        vectors_config={
            "dense": VectorParams(
                size=1536,
                distance=Distance.COSINE,
            )
        },

        sparse_vectors_config={
            "sparse": SparseVectorParams()
        },
    )