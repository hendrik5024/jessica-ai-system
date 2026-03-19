import json
from pathlib import Path


class ConceptStore:
    """
    Stores relationships like:
    (subject, relation, value)
    """

    def __init__(self, path="data/concepts.json"):
        self.path = Path(path)
        self.data = self._load()

    def _load(self):
        if self.path.exists():
            try:
                return json.loads(self.path.read_text())
            except Exception:
                return []
        return []

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2))

    def add(self, subject: str, relation: str, value):
        record = {
            "subject": subject.lower(),
            "relation": relation,
            "value": value,
        }
        self.data.append(record)
        self._save()

    def find(self, subject: str, relation: str):
        for r in reversed(self.data):
            if r["subject"] == subject.lower() and r["relation"] == relation:
                return r["value"]
        return None
