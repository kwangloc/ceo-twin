from langchain_core.documents import Document

from retrieval.qdrant.parent_store import ParentStore
from retrieval.qdrant.models import RetrievedContext

class ParentExpander:

    def __init__(
        self,
        parent_store: ParentStore,
    ):
        self.parent_store = parent_store

    def expand(
        self,
        docs: list[Document],
        max_contexts: int = 5,
    ) -> list[RetrievedContext]:
        """
        Expand retrieved child chunks back to
        their parent sections.

        Deduplicates parents while preserving
        retrieval order.
        """
        
        contexts: list[
            RetrievedContext
        ] = []

        seen_parent_ids: set[
            str
        ] = set()

        for doc in docs:

            if len(contexts) >= max_contexts:
                break

            parent_id = (
                doc.metadata.get(
                    "parent_id"
                )
            )

            if not parent_id:
                continue

            if (
                parent_id
                in seen_parent_ids
            ):
                continue

            seen_parent_ids.add(
                parent_id
            )

            parent = (
                self.parent_store.get(
                    parent_id
                )
            )

            if parent is None:
                continue

            contexts.append(
                RetrievedContext(
                    source=parent.source,

                    title=parent.title,

                    path=" > ".join(
                        parent.path
                    ),

                    content=parent.text,
                )
            )

        return contexts