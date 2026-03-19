import json
import os
import sys
from typing import List, Dict, Any

# Make repo root importable
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from jessica.memory.sqlite_store import EpisodicStore
from jessica.memory.embeddings_index import EmbeddingsIndex


def build_example(entry: Dict[str, Any], recent: List[Dict[str, Any]], relevant: List[Dict[str, Any]]) -> Dict[str, str]:
    input_text = entry.get("input_text", "")
    output_obj = entry.get("output", {})
    reply = ""
    # Try common paths in result
    if isinstance(output_obj, dict):
        reply = output_obj.get("reply") or output_obj.get("text") or json.dumps(output_obj)[:2048]
    else:
        reply = str(output_obj)

    # Construct a lightweight context block
    ctx_lines = []
    for r in recent[:3]:
        it = (r.get("input_text") or "").strip()
        if it:
            ctx_lines.append(f"- {it}")
    for h in relevant[:2]:
        meta = h.get("meta", {})
        it = (meta.get("meta", {}) if isinstance(meta, dict) else {})
        if isinstance(it, dict):
            itext = it.get("input_text") or ""
            if itext:
                ctx_lines.append(f"- {itext}")

    context_block = "\n".join(ctx_lines)
    instruction = "Answer the user's message naturally and helpfully."
    input_field = input_text if not context_block else f"Context:\n{context_block}\n\nUser:\n{input_text}"

    return {"instruction": instruction, "input": input_field, "output": reply}


def export(jsonl_path: str = "datasets/user_finetune/train.jsonl", min_len: int = 8, max_export: int = 5000, include_knowledge: bool = True):
    os.makedirs(os.path.dirname(jsonl_path), exist_ok=True)
    db = EpisodicStore("jessica_data.db")
    emb = EmbeddingsIndex("jessica_data_embeddings")

    examples = []
    
    # Add examples from episodic memory
    cur = db._conn.cursor()
    cur.execute("SELECT id, ts, user, input_text, output_json, meta_json FROM episodic ORDER BY ts DESC")
    rows = cur.fetchall()

    for r in rows:
        eid, ts, user, input_text, output_json, meta_json = r
        if not input_text or len(input_text.strip()) < min_len:
            continue

        try:
            output_obj = json.loads(output_json) if output_json else {}
        except Exception:
            output_obj = {"reply": str(output_json)}

        recent = db.recent(5)
        relevant_hits = []
        try:
            for id_, score in emb.search(input_text, top_k=5):
                meta = emb.get_meta(id_)
                relevant_hits.append({"id": id_, "score": score, "meta": meta})
        except Exception:
            pass

        ex = build_example({"input_text": input_text, "output": output_obj}, recent, relevant_hits)
        if not ex["output"] or len(ex["output"].strip()) < min_len:
            continue
        examples.append(ex)
        if len(examples) >= max_export:
            break

    # Optionally add knowledge base facts as synthetic training examples
    if include_knowledge:
        try:
            from jessica.memory.knowledge_store import KnowledgeStore
            ks = KnowledgeStore()
            
            # Add facts as Q/A pairs
            for topic, facts_list in ks.data.get("facts", {}).items():
                for fact in facts_list[:5]:
                    ex = {
                        "instruction": f"Provide information about {topic}.",
                        "input": topic,
                        "output": fact.get("text", "")
                    }
                    examples.append(ex)
            
            # Add document chunks
            for doc_id, doc in list(ks.data.get("documents", {}).items())[:10]:
                ex = {
                    "instruction": f"Summarize knowledge from {doc.get('title', 'document')}.",
                    "input": doc.get("title", ""),
                    "output": doc.get("content", "")[:500]
                }
                examples.append(ex)
        except Exception as e:
            print(f"[export_dataset] skipping knowledge: {e}")

    with open(jsonl_path, "w", encoding="utf-8") as f:
        for ex in reversed(examples):
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"[export_dataset] Wrote {len(examples)} examples to {jsonl_path}")


if __name__ == "__main__":
    export()
