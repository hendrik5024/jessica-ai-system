from jessica.memory.embeddings_index import EmbeddingsIndex
from jessica.memory.sqlite_store import EpisodicStore

emb = EmbeddingsIndex("jessica_data_embeddings")
db = EpisodicStore("jessica_data.db")

q = "reminder about call mom"
results = emb.search(q, top_k=5)
print("Results:", results)

for id_, score in results:
    cur = db._conn.cursor()
    cur.execute("SELECT id, ts, user, input_text, output_json, meta_json FROM episodic WHERE id=?", (int(id_),))
    row = cur.fetchone()
    if not row:
        continue
    print("----")
    print("id", row[0], "ts", row[1], "input:", row[3])
    print("output:", row[4])
    print("meta:", row[5])
    print("score:", score)
