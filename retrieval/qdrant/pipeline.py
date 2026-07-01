from retrieval.qdrant.config import Settings
from retrieval.qdrant.parent_store import ParentStore
from retrieval.qdrant.models import RetrievedContext
from retrieval.qdrant.retriever import HybridRetriever
from retrieval.qdrant.reranker import Reranker
from retrieval.qdrant.parent_expander import ParentExpander

class SemanticRAG:

    def __init__(
        self,
        settings: Settings,
        parent_store: ParentStore,
    ):
        self.settings = settings
        self.retriever = HybridRetriever(settings=settings)
        self.reranker = Reranker(model_name=settings.reranker_model)
        self.expander = ParentExpander(parent_store=parent_store)

    def build_context(self, contexts: list[RetrievedContext]) -> str:
        blocks = []
        for i, ctx in enumerate(contexts, start=1):
            blocks.append(f"[Document {i}]\n{ctx.content}".strip())

        return "\n\n".join(blocks)

    def retrieve(
        self,
        query: str,
    ) -> str:
        """
        Retrieval pipeline:

        Query
          ↓
        Hybrid Search
          ↓
        Top candidate_k child chunks
          ↓
        Cross-encoder rerank
          ↓
        Top rerank_k child chunks
          ↓
        Parent expansion
          ↓
        Retrieved contexts
        """

        candidates = (
            self.retriever.retrieve(
                query=query,
                k=self.settings.candidate_k,
            )
        )

        if not candidates:
            return ""

        reranked = (
            self.reranker.rerank(
                query=query,
                docs=candidates,
                top_k=self.settings.rerank_k,
            )
        )

        if not reranked:
            return ""

        contexts = self.expander.expand(
            reranked,
            max_contexts=self.settings.max_contexts,
        )

        context_text = self.build_context(contexts)
        return context_text