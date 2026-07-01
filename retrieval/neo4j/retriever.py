from __future__ import annotations

import json
import os

from neo4j import GraphDatabase
from langchain.chat_models import init_chat_model
from config import RETRIEVAL_MODEL
from .prompts import (
    ENTITY_EXTRACTION_PROMPT,
    GRAPH_SUMMARIZE_PROMPT,
)
from dotenv import load_dotenv

load_dotenv()

class Neo4jGraphRetriever:
    def __init__(self) -> None:
        self.driver = GraphDatabase.driver(
            os.environ["NEO4J_URI"],
            auth=(
                os.environ["NEO4J_USERNAME"],
                os.environ["NEO4J_PASSWORD"],
            ),
        )

        self.database = os.getenv(
            "NEO4J_DATABASE",
            "neo4j",
        )

        self.llm = init_chat_model(RETRIEVAL_MODEL)

    def close(self) -> None:
        self.driver.close()

    def get_catalog(self) -> list[dict]:
        cypher = """
        MATCH (n)
        RETURN DISTINCT
            head(labels(n)) AS type,
            n.label AS label
        ORDER BY type, label
        """

        rows = []

        with self.driver.session(
            database=self.database,
        ) as session:
            result = session.run(cypher)

            for row in result:
                rows.append(
                    {
                        "type": row["type"],
                        "label": row["label"],
                    }
                )

        return rows

    def extract_entities(
        self,
        query: str,
    ) -> list[str]:
        prompt = ENTITY_EXTRACTION_PROMPT.format(
            catalog=json.dumps(
                self.get_catalog(),
                ensure_ascii=False,
                indent=2,
            ),
            query=query,
        )

        response = self.llm.invoke(prompt)

        print("\n=== ENTITY EXTRACTION ===")
        print("LLM response:", response.content)

        try:
            data = json.loads(response.content)

            print("Parsed JSON:", data)

            return data.get(
                "entities",
                [],
            )

        except Exception as e:
            print("Exception while parsing JSON:", e)
            return []

    def retrieve_triples(
        self,
        entity: str,
        limit: int = 100,
    ) -> list[dict]:
        cypher = """
        MATCH (n)
        WHERE toLower(n.label) = toLower($entity)

        MATCH (n)-[r]-(m)

        RETURN
            n.label AS source,
            type(r) AS relation,
            m.label AS target

        LIMIT $limit
        """

        triples = []

        with self.driver.session(
            database=self.database,
        ) as session:
            result = session.run(
                cypher,
                entity=entity,
                limit=limit,
            )

            for row in result:
                triples.append(
                    {
                        "source": row["source"],
                        "relation": row["relation"],
                        "target": row["target"],
                    }
                )

        return triples

    def deduplicate_triples(
        self,
        triples: list[dict],
    ) -> list[dict]:
        seen = set()
        deduped = []

        for triple in triples:
            key = (
                triple["source"],
                triple["relation"],
                triple["target"],
            )

            if key not in seen:
                seen.add(key)
                deduped.append(triple)

        return deduped

    def format_triples(
        self,
        triples: list[dict],
    ) -> str:
        return "\n".join(
            f"{t['source']} -[{t['relation']}]-> {t['target']}"
            for t in triples
        )

    def search(
        self,
        query: str,
    ) -> dict:
        entities = self.extract_entities(query)

        all_triples = []

        for entity in entities:
            all_triples.extend(
                self.retrieve_triples(entity)
            )

        all_triples = self.deduplicate_triples(
            all_triples
        )

        formatted_triples = self.format_triples(
            all_triples
        )

        answer = self.generate_answer(
            query,
            formatted_triples,
        )

        return {
            "entities": entities,
            "triples": all_triples,
            "answer": answer,
        }
    
    def generate_answer(
        self,
        query: str,
        graph_context: str,
    ) -> str:
        prompt = GRAPH_SUMMARIZE_PROMPT.format(
            query=query,
            facts=graph_context,
        )

        response = self.llm.invoke(prompt)

        return response.content


if __name__ == "__main__":
    retriever = Neo4jGraphRetriever()

    try:
        # =====================================================
        # STEP 1 - TEST ENTITY EXTRACTION
        # =====================================================

        # print(
        #     retriever.extract_entities(
        #         "Who are owners of Project V-CEO?"
        #     )
        # )

        # =====================================================
        # STEP 2 - TEST SINGLE ENTITY TRIPLE RETRIEVAL
        # =====================================================

        # triples = retriever.retrieve_triples(
        #     "Project V-CEO"
        # )
        #
        # for t in triples:
        #     print(t)

        # =====================================================
        # STEP 3 - TEST FULL SEARCH PIPELINE
        # =====================================================

        result = retriever.search(
            "Who are owners of Project V-CEO?"
        )

        # print("\n=== SEARCH RESULT ===")
        # print(
        #     json.dumps(
        #         result,
        #         indent=2,
        #         ensure_ascii=False,
        #     )
        # )

        print("\n=== FORMATTED TRIPLES ===")
        print(result["formatted_triples"])
        
        print("\n=== GENERATED ANSWER ===")
        print(result["answer"])

    finally:
        retriever.close()