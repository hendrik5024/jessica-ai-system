# jessica/memory/indexer.py
import sqlite3
import json
from jessica.memory.embeddings_index import EmbeddingsIndex

def build_index_from_db(sqlite_path: str = "jessica_data.db", index_path: str = "jessica_data_embeddings"):
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    cur.execute("SELECT id, ts, user, input_text, output_json, meta_json FROM episodic ORDER BY ts ASC")
    rows = cur.fetchall()
    items = []
    for r in rows:
        eid = r[0]
        ts = r[1]
        user = r[2]
        input_text = r[3] or ""
        output = r[4] or ""
        meta = r[5] or "{}"
        text_for_embed = f"INPUT: {input_text}\nOUTPUT: {output}\nMETA: {meta}"
        items.append((str(eid), text_for_embed, {"ts": ts, "user": user, "meta": json.loads(meta)}))
    emb = EmbeddingsIndex(path=index_path)
    emb.build_from_texts(items)
    print(f"[Indexer] built index with {len(items)} items")
    conn.close()
    return emb
