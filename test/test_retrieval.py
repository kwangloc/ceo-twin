# python -m test.test_retrieval

from retrieval.pipeline import retrieve

result = retrieve(
    sources=["graph"],
    query="Who are owners of Project V-CEO?",
)

for item in result:
    print(item)