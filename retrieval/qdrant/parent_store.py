from pathlib import Path
import pickle

from retrieval.qdrant.models import ParentChunk

import sys
from retrieval.qdrant import models
sys.modules['models'] = models


class ParentStore:

    def __init__(self):
        self.parents: dict[str, ParentChunk] = {}   

    def add(self, parent: ParentChunk):
        self.parents[parent.chunk_id] = parent

    def get(self, parent_id: str) -> ParentChunk | None:
        return self.parents.get(parent_id)

    def save(self, path: str):
        path_obj = Path(path)

        path_obj.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(path_obj, "wb",) as f:
            pickle.dump(self.parents, f)

    @classmethod
    def load(cls, path: str):
        store = cls()

        path_obj = Path(path)

        if not path_obj.exists():
            raise FileNotFoundError(f"Parent store not found: {path}")

        with open(path_obj, "rb",) as f:
            store.parents = pickle.load(f)

        return store

    def __len__(self):
        return len(self.parents)