from retrieval.base import RetrieverSource


class MemoryRetriever(RetrieverSource):
    """Director's prior context, preferences, and conversation history."""

    name = "memory"

    def retrieve(self, query: str) -> list[str]:
        # TODO: replace with real memory/session store call
        if "atlas" in query.lower():
            return [
                "Memory: Director previously marked Atlas as high priority",
                "Memory: Earlier conversation suggested Vendor X was the main risk",
            ]
        return [f"Memory: relevant prior context for '{query}'"]
