from pydantic import BaseModel

class Settings(BaseModel):

    qdrant_url: str = "https://7c3c42da-f043-4f34-b7b9-97e847dad8fb.us-west-1-0.aws.cloud.qdrant.io"
    qdrant_api_key: str = ""
    collection_name: str = "vceo_semantic"
    parent_store_path: str = ("data/index/parents.pkl")
    embedding_model: str = "text-embedding-3-small"
    sparse_model: str = "Qdrant/bm25"
    reranker_model: str = ("BAAI/bge-reranker-v2-m3")

    child_chunk_size: int = 150
    child_chunk_overlap: int = 30
    candidate_k: int = 50
    rerank_k: int = 10
    max_contexts: int = 5