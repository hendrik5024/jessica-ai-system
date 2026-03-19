import sqlite3
from pathlib import Path


class KnowledgeGraph:

    def __init__(self):

        db_path = Path("jessica/memory/knowledge_graph.db")

        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(db_path)

        self._create_tables()

    def _create_tables(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            relation TEXT,
            target TEXT
        )
        """)

        self.conn.commit()

    def add_node(self, name):

        cursor = self.conn.cursor()

        try:
            cursor.execute(
                "INSERT OR IGNORE INTO nodes(name) VALUES(?)",
                (name,)
            )
            self.conn.commit()
        except Exception:
            pass

    def add_relation(self, source, relation, target):

        cursor = self.conn.cursor()

        cursor.execute(
            "INSERT INTO edges(source, relation, target) VALUES(?,?,?)",
            (source, relation, target)
        )

        self.conn.commit()

    def get_relations(self, node):

        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT relation, target FROM edges WHERE source=?",
            (node,)
        )

        return cursor.fetchall()

    def query(self, node):

        relations = self.get_relations(node)

        return relations

    def get_dependents(self, node):

        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT source, relation FROM edges WHERE target=?",
            (node,)
        )

        return cursor.fetchall()
