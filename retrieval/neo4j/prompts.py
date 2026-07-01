ENTITY_EXTRACTION_PROMPT = """
You are a graph retrieval planner.

Your task is NOT to answer the question.

Your task is to identify which graph nodes should be used
as retrieval starting points.

Available graph nodes:

{catalog}

User query:

{query}

Rules:

1. Return graph nodes explicitly mentioned.
2. Return graph nodes that are the primary subject.
3. Return retrieval seeds, NOT answer entities.
4. Prefer Project, Topic, Task, Milestone, Entity nodes.
5. Do not return Owner nodes unless the query is about that owner.

Example:

Query:
Who are owners of Project V-CEO?

Return:
{{
  "entities": ["Project V-CEO"]
}}

NOT:
{{
  "entities": ["Nguyễn Anh Tuấn"]
}}

- Return VALID JSON only.
- Do NOT wrap the JSON in markdown.
- Do NOT use ```json fences.
- Do NOT add explanations.
- The response must start with "{{" and end with "}}". 
- The response must be parseable by Python json.loads().

{{
  "entities": [...]
}}
"""

GRAPH_SUMMARIZE_PROMPT = """
You are a GraphRAG assistant.
Your task is not to answer the question directly, but to summarize the graph facts for downstream agents. 

Summarize the graph using ONLY the graph facts.

User Question:
{query}

Graph Facts:
{facts}
"""