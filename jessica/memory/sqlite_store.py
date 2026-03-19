import sqlite3, json, time
from typing import List, Dict, Any

class EpisodicStore:
    def __init__(self, db_path="jessica_data.db"):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_schema()

    def _init_schema(self):
        cur = self._conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS episodic (
            id INTEGER PRIMARY KEY,
            ts INTEGER,
            user TEXT,
            input_text TEXT,
            output_json TEXT,
            meta_json TEXT
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS milestones (
            id INTEGER PRIMARY KEY,
            ts INTEGER,
            episode_id INTEGER,
            title TEXT,
            meta_json TEXT
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS meta_observations (
            id INTEGER PRIMARY KEY,
            ts INTEGER,
            episode_id INTEGER,
            user TEXT,
            intent TEXT,
            model_used TEXT,
            confidence REAL,
            memory_used INTEGER,
            user_sentiment TEXT,
            followup_needed INTEGER,
            values_alignment TEXT,
            improvement_note TEXT,
            meta_json TEXT
        )""")
        self._conn.commit()

    def save_episode(self, user: str, input_text: str, output: dict, meta: dict = None):
        ts = int(time.time())
        cur = self._conn.cursor()
        cur.execute("INSERT INTO episodic (ts, user, input_text, output_json, meta_json) VALUES (?, ?, ?, ?, ?)",
                    (ts, user, input_text, json.dumps(output), json.dumps(meta or {})))
        self._conn.commit()
        return cur.lastrowid

    def add_milestone(self, title: str, meta: dict | None = None, episode_id: int | None = None):
        ts = int(time.time())
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO milestones (ts, episode_id, title, meta_json) VALUES (?, ?, ?, ?)",
            (ts, episode_id, title, json.dumps(meta or {})),
        )
        self._conn.commit()
        return cur.lastrowid

    def save_meta_observation(self, meta: Dict[str, Any], episode_id: int | None = None, user: str | None = None):
        ts = int(time.time())
        cur = self._conn.cursor()
        cur.execute(
            """INSERT INTO meta_observations
            (ts, episode_id, user, intent, model_used, confidence, memory_used,
             user_sentiment, followup_needed, values_alignment, improvement_note, meta_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                ts,
                episode_id,
                user,
                str(meta.get("intent", "")),
                str(meta.get("model_used", "")),
                float(meta.get("confidence", 0.0) or 0.0),
                1 if meta.get("memory_used") else 0,
                str(meta.get("user_sentiment", "")),
                1 if meta.get("followup_needed") else 0,
                str(meta.get("values_alignment", "")),
                str(meta.get("improvement_note", "")),
                json.dumps(meta),
            ),
        )
        self._conn.commit()
        return cur.lastrowid

    def list_milestones(self, limit: int = 10) -> List[dict]:
        cur = self._conn.cursor()
        cur.execute(
            "SELECT id, ts, episode_id, title, meta_json FROM milestones ORDER BY ts DESC LIMIT ?",
            (limit,),
        )
        rows = cur.fetchall()
        return [
            {
                "id": r[0],
                "ts": r[1],
                "episode_id": r[2],
                "title": r[3],
                "meta": json.loads(r[4] or "{}"),
            }
            for r in rows
        ]

    def recent(self, limit: int = 10) -> List[dict]:
        cur = self._conn.cursor()
        cur.execute("SELECT id, ts, user, input_text, output_json, meta_json FROM episodic ORDER BY ts DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        return [{"id": r[0], "ts": r[1], "user": r[2], "input_text": r[3], "output": json.loads(r[4]), "meta": json.loads(r[5])} for r in rows]

    def get_meta_observations_since(self, ts_since: int) -> List[Dict[str, Any]]:
        cur = self._conn.cursor()
        cur.execute(
            """
            SELECT id, ts, episode_id, user, intent, model_used, confidence, memory_used,
                   user_sentiment, followup_needed, values_alignment, improvement_note, meta_json
            FROM meta_observations
            WHERE ts >= ?
            ORDER BY ts DESC
            """,
            (ts_since,),
        )
        rows = cur.fetchall()
        results = []
        for r in rows:
            results.append({
                "id": r[0],
                "ts": r[1],
                "episode_id": r[2],
                "user": r[3],
                "intent": r[4],
                "model_used": r[5],
                "confidence": r[6],
                "memory_used": bool(r[7]),
                "user_sentiment": r[8],
                "followup_needed": bool(r[9]),
                "values_alignment": r[10],
                "improvement_note": r[11],
                "meta": json.loads(r[12] or "{}"),
            })
        return results

    def get_meta_summary(self, days: int = 7) -> Dict[str, Any]:
        ts_since = int(time.time()) - (days * 86400)
        items = self.get_meta_observations_since(ts_since)
        if not items:
            return {
                "count": 0,
                "avg_confidence": 0.0,
                "memory_use_rate": 0.0,
                "followup_rate": 0.0,
                "top_model": None,
                "sentiment_mix": {},
                "top_improvement": None,
            }

        total = len(items)
        avg_conf = sum(i.get("confidence", 0.0) or 0.0 for i in items) / max(total, 1)
        memory_rate = sum(1 for i in items if i.get("memory_used")) / max(total, 1)
        follow_rate = sum(1 for i in items if i.get("followup_needed")) / max(total, 1)

        model_counts: Dict[str, int] = {}
        sentiment_counts: Dict[str, int] = {}
        improvement_counts: Dict[str, int] = {}

        for item in items:
            model = item.get("model_used") or "unknown"
            model_counts[model] = model_counts.get(model, 0) + 1

            sentiment = item.get("user_sentiment") or "unknown"
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1

            note = (item.get("improvement_note") or "").strip()
            if note:
                improvement_counts[note] = improvement_counts.get(note, 0) + 1

        top_model = max(model_counts, key=model_counts.get) if model_counts else None
        top_improvement = max(improvement_counts, key=improvement_counts.get) if improvement_counts else None

        return {
            "count": total,
            "avg_confidence": round(avg_conf, 3),
            "memory_use_rate": round(memory_rate, 3),
            "followup_rate": round(follow_rate, 3),
            "top_model": top_model,
            "sentiment_mix": sentiment_counts,
            "top_improvement": top_improvement,
        }
