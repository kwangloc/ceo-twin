from dataclasses import dataclass

@dataclass(slots=True)
class ParentChunk:
    chunk_id: str
    source: str
    title: str | None
    path: list[str]
    text: str

@dataclass(slots=True)
class ChildChunk:
    chunk_id: str
    parent_id: str
    source: str
    title: str | None
    path: list[str]
    text: str
    
@dataclass(slots=True)
class RetrievedContext:
    source: str
    title: str | None
    path: str
    content: str