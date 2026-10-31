import re
from dataclasses import dataclass


class FakeCursor:
    def __init__(self, docs: list[dict]):
        self._docs = docs

    def skip(self, n: int) -> "FakeCursor":
        self._docs = self._docs[n:]
        return self

    def limit(self, n: int) -> "FakeCursor":
        self._docs = self._docs[:n]
        return self

    def __aiter__(self):
        return self._aiter()

    async def _aiter(self):
        for doc in self._docs:
            yield doc


def _matches(doc: dict, query: dict) -> bool:
    for key, condition in query.items():
        value = doc.get(key)
        if isinstance(condition, dict) and "$regex" in condition:
            flags = re.IGNORECASE if condition.get("$options") == "i" else 0
            if not re.search(condition["$regex"], value or "", flags):
                return False
        elif value != condition:
            return False
    return True


@dataclass
class FakeInsertResult:
    inserted_id: object


@dataclass
class FakeUpdateResult:
    matched_count: int


@dataclass
class FakeDeleteResult:
    deleted_count: int


class FakeCollection:
    def __init__(self, docs: list[dict]):
        self._docs = docs

    def find(self, query: dict | None = None) -> FakeCursor:
        matched = [doc for doc in self._docs if _matches(doc, query or {})]
        return FakeCursor(matched)

    async def count_documents(self, query: dict | None = None) -> int:
        return len([doc for doc in self._docs if _matches(doc, query or {})])

    async def find_one(self, query: dict | None = None) -> dict | None:
        for doc in self._docs:
            if _matches(doc, query or {}):
                return doc
        return None

    async def insert_one(self, doc: dict) -> FakeInsertResult:
        self._docs.append(doc)
        return FakeInsertResult(inserted_id=doc.get("id"))

    async def replace_one(self, query: dict, doc: dict) -> FakeUpdateResult:
        for i, existing in enumerate(self._docs):
            if _matches(existing, query):
                self._docs[i] = doc
                return FakeUpdateResult(matched_count=1)
        return FakeUpdateResult(matched_count=0)

    async def delete_one(self, query: dict) -> FakeDeleteResult:
        for i, doc in enumerate(self._docs):
            if _matches(doc, query):
                del self._docs[i]
                return FakeDeleteResult(deleted_count=1)
        return FakeDeleteResult(deleted_count=0)


class FakeDatabase:
    def __init__(self, collections: dict[str, list[dict]]):
        self._collections = {name: FakeCollection(docs) for name, docs in collections.items()}

    def __getitem__(self, name: str) -> FakeCollection:
        return self._collections.setdefault(name, FakeCollection([]))
