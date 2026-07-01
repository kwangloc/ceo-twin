from __future__ import annotations
from retrieval.neo4j.retriever import Neo4jGraphRetriever
from retrieval.base import RetrieverSource
from dotenv import load_dotenv

load_dotenv()

class GraphRetriever(RetrieverSource):
    """
    Neo4j-based graph retrieval.

    Flow:
        Query
            -> Entity Extraction
            -> Graph Expansion
            -> Triple Retrieval
            -> Graph Answer Generation

    Returns:
        List[str] context blocks for downstream workers.
    """

    name = "graph"

    def __init__(self) -> None:
        self.retriever = Neo4jGraphRetriever()

    def retrieve(
        self,
        query: str,
    ) -> list[str]:
        try:
            result = self.retriever.search(query)

            contexts: list[str] = []

            if result["answer"]:
                contexts.append(
                    f"Graph Analysis:\n{result['answer']}"
                )

            if result["triples"]:
                facts = "\n".join(
                    f"{t['source']} -[{t['relation']}]-> {t['target']}"
                    for t in result["triples"]
                )

                contexts.append(
                    f"Graph Facts:\n{facts}"
                )

            return contexts

        except Exception as exc:
            return [
                f"Graph retrieval failed: {exc}"
            ]

# class GraphRetriever(RetrieverSource):
#     """Knowledge graph retrieval (Neo4j / entity relationships)."""

#     name = "graph"

#     def retrieve(self, query: str) -> list[str]:
#         # TODO: replace with real Neo4j or graph DB call
#         if "atlas" in query.lower():
#             return [
#                 "Graph: Project Atlas depends on Vendor X",
#                 "Graph: Vendor X is linked to delivery milestone M3",
#                 "Graph: Atlas owner is Maya",
#             ]
#         return [f"Graph: related entity found for '{query}'"]

if __name__ == "__main__":
    retriever = GraphRetriever()

    try:
        query = "What are the dependencies of Project Atlas?"
        contexts = retriever.retrieve(query)

        print("\n=== RETRIEVAL CONTEXTS ===")
        for context in contexts:
            print(context)
            print("-" * 40)

    finally:
        retriever.close()