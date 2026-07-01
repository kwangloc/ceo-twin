from abc import ABC, abstractmethod


class RetrieverSource(ABC):
    """
    Base class for all retrieval sources.

    To add a new source:
    1. Subclass RetrieverSource and set a unique ``name``.
    2. Implement ``retrieve``.
    3. Register an instance in ``retrieval/pipeline.py``.
    """

    name: str

    @abstractmethod
    def retrieve(self, query: str) -> list[str]:
        """Return context strings relevant to *query*."""
        ...
