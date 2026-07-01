def rewrite_query(query: str) -> list[str]:
    lower = query.lower()

    terms = [query]

    if "why" in lower:
        terms.append(query.replace("why", "").strip())
        terms.append("root cause")
        terms.append("blockers")

    if "delay" in lower or "blocked" in lower or "behind" in lower:
        terms.extend(["delayed dependencies", "project risks", "owner updates"])

    return [term for term in dict.fromkeys(t for t in terms if t)]


def graph_search(query: str) -> list[str]:
    if "atlas" in query.lower():
        return [
            "Graph: Project Atlas depends on Vendor X",
            "Graph: Vendor X is linked to delivery milestone M3",
            "Graph: Atlas owner is Maya",
        ]
    return [
        f"Graph: related entity found for '{query}'",
    ]


def semantic_search(query: str) -> list[str]:
    if "atlas" in query.lower():
        return [
            "Vector: Slack discussion mentions staffing shortage on Atlas",
            "Vector: Meeting notes mention dependency slip in Atlas",
            "Vector: Postmortem draft references vendor delay",
        ]
    return [
        f"Vector: semantically related note for '{query}'",
    ]


def memory_search(query: str) -> list[str]:
    if "atlas" in query.lower():
        return [
            "Memory: Director previously marked Atlas as high priority",
            "Memory: Earlier conversation suggested Vendor X was the main risk",
        ]
    return [
        f"Memory: relevant prior context for '{query}'",
    ]


def slack_search(query: str) -> list[str]:
    if "atlas" in query.lower():
        return [
            "Slack: team asked for an updated ETA from Vendor X",
            "Slack: engineering reported a blocked integration test",
        ]
    return [
        f"Slack: relevant chat result for '{query}'",
    ]


def jira_search(query: str) -> list[str]:
    if "atlas" in query.lower():
        return [
            "Jira: ticket ATLAS-12 is blocked by external dependency",
            "Jira: ticket ATLAS-18 moved to delayed state",
        ]
    return [
        f"Jira: relevant issue for '{query}'",
    ]


def retrieve_context(query: str) -> list[str]:
    subqueries = rewrite_query(query)

    results: list[str] = []
    for q in subqueries[:3]:
        results.extend(graph_search(q))
        results.extend(semantic_search(q))
        results.extend(memory_search(q))

    results.extend(slack_search(query))
    results.extend(jira_search(query))

    # Deduplicate while preserving order
    deduped: list[str] = []
    seen: set[str] = set()
    for item in results:
        if item not in seen:
            seen.add(item)
            deduped.append(item)

    return deduped