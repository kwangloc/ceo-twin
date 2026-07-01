from retrieval.base import RetrieverSource


class RetrieverRegistry:
    """Holds registered retrieval sources and dispatches queries to them."""

    def __init__(self) -> None:
        self._sources: dict[str, RetrieverSource] = {}

    def register(self, source: RetrieverSource) -> None:
        self._sources[source.name] = source

    def available(self) -> list[str]:
        return list(self._sources.keys())

    def retrieve_from(self, sources: list[str], query: str) -> list[str]:
        """Query the specified sources and return their combined results."""
        results: list[str] = []
        for name in sources:
            src = self._sources.get(name)
            if src is not None:
                results.extend(src.retrieve(query))
        return results
