"""
Retrieval pipeline: source-selective retrieval.

To add a new retrieval source:
  1. Create a subclass of RetrieverSource in retrieval/sources/.
  2. Register it below with ``_registry.register(...)``.
  No other files need to change.
"""

from config import MAX_RETRIEVAL_SUBQUERIES
from retrieval.registry import RetrieverRegistry
from retrieval.sources.graph import GraphRetriever
from retrieval.sources.memory import MemoryRetriever
from retrieval.sources.vector import VectorRetriever

_registry = RetrieverRegistry()
_registry.register(GraphRetriever())
_registry.register(VectorRetriever())
_registry.register(MemoryRetriever())


def get_retriever_registry() -> RetrieverRegistry:
    return _registry


def retrieve(
    sources: list[str],
    query: str,
) -> list[str]:
    """
    Run retrieval across *sources* with deduplication.

    Args:
        sources:       Names of retrieval sources to query (e.g. ["graph", "vector"]).
                       Only registered sources are queried; unknown names are silently skipped.
        query:         The user's original query.

    Returns:
        Deduplicated list of context strings.
    """
    raw = _registry.retrieve_from(
        sources,
        query,
    )

    seen = set()
    deduped = []

    for item in raw:
        if item not in seen:
            seen.add(item)
            deduped.append(item)

    return deduped
