import os
from dotenv import load_dotenv

from retrieval.base import RetrieverSource
from retrieval.qdrant.config import Settings
from retrieval.qdrant.parent_store import ParentStore
from retrieval.qdrant.pipeline import SemanticRAG

load_dotenv()
settings = Settings()
settings.qdrant_api_key = os.getenv("QDRANT_API_KEY")

class VectorRetriever(RetrieverSource):
    """Semantic / vector retrieval (Qdrant, Pinecone, pgvector, etc.)."""
    name = "vector"
    
    parent_store = ParentStore.load(settings.parent_store_path)
    rag = SemanticRAG(settings=settings, parent_store=parent_store)

    def retrieve(self, query: str) -> list[str]:
        
        context_text = self.rag.retrieve(query)
        return [context_text]
    
    def close(self) -> None:
        self.parent_store.close()

# class VectorRetriever(RetrieverSource):
#     """Semantic / vector retrieval (Qdrant, Pinecone, pgvector, etc.)."""

#     name = "vector"

#     def retrieve(self, query: str) -> list[str]:
#         # TODO: replace with real vector store call
#         if "atlas" in query.lower():
#             return [
#                 "Vector: Slack discussion mentions staffing shortage on Atlas",
#                 "Vector: Meeting notes mention dependency slip in Atlas",
#                 "Vector: Postmortem draft references vendor delay",
#             ]
#         return [f"Vector: semantically related note for '{query}'"]

# python -m retrieval.sources.vector
if __name__ == "__main__":
    retriever = VectorRetriever()

    try:
        query = "Due Date triển khai môi trường Neo4j staging?"
        contexts = retriever.retrieve(query)

        print("\n=== RETRIEVAL CONTEXTS ===")
        for context in contexts:
            print(context)
            print("-" * 40)
    except Exception as exc:
        print(f"Vector retrieval failed: {exc}")