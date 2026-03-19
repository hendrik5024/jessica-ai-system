"""
Teaching interface: Simple CLI to add facts, documents, and web content to Jessica.
"""
import sys
import os
from pathlib import Path

# Make repo importable
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from jessica.memory.knowledge_store import KnowledgeStore


def teach_fact(topic: str, fact: str):
    """Teach a single fact."""
    ks = KnowledgeStore()
    ks.add_fact(topic, fact)
    print(f"[teach] Added fact to '{topic}': {fact[:50]}...")
    print(f"[teach] Knowledge stats: {ks.describe()}")


def teach_document(title: str, content: str, tags: str = "general"):
    """Teach a document."""
    ks = KnowledgeStore()
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    doc_id = ks.add_document(title, content, source="user", tags=tag_list)
    print(f"[teach] Added document '{title}' (id={doc_id})")
    print(f"[teach] Knowledge stats: {ks.describe()}")


def teach_from_file(filepath: str, tags: str = "document"):
    """Teach from a text file."""
    fpath = Path(filepath)
    if not fpath.exists():
        print(f"[teach] File not found: {filepath}")
        return
    
    try:
        content = fpath.read_text(encoding="utf-8")
        title = fpath.stem
        teach_document(title, content, tags)
    except Exception as e:
        print(f"[teach] Error reading file: {e}")


def teach_from_web(url: str, tags: str = "web"):
    """Fetch and teach from a URL."""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        print(f"[teach] Fetching {url}...")
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Extract main text content
        for script in soup(["script", "style"]):
            script.decompose()
        
        title = (soup.title.string if soup.title else url).strip()
        content = " ".join(soup.stripped_strings)
        
        ks = KnowledgeStore()
        doc_id = ks.add_document(title, content[:5000], source=url, tags=[tags])
        ks.add_source(url, {"title": title})
        
        print(f"[teach] Added web content from {url}")
        print(f"[teach] Knowledge stats: {ks.describe()}")
    except ImportError:
        print("[teach] Install requests and beautifulsoup4: pip install requests beautifulsoup4")
    except Exception as e:
        print(f"[teach] Error fetching web content: {e}")


def teach_recipe(name: str, ingredients: str, instructions: str, category: str = "general"):
    """Add a recipe to the recipe database."""
    from jessica.memory.recipe_store import RecipeStore
    
    recipe_id = name.lower().replace(" ", "_")
    recipe = {
        "name": name,
        "category": category,
        "difficulty": "medium",
        "ingredients": [i.strip() for i in ingredients.split(",")],
        "instructions": [s.strip() for s in instructions.split("|")],
        "tags": [category, "custom"]
    }
    
    rs = RecipeStore()
    rs.add_recipe(recipe_id, recipe)
    print(f"[teach] Added recipe: {name}")
    print(f"[teach] Total recipes: {len(rs.recipes)}")


def list_knowledge():
    """Show current knowledge base."""
    ks = KnowledgeStore()
    stats = ks.describe()
    print(f"\n[Knowledge Base Stats]")
    print(f"  Documents: {stats['documents']}")
    print(f"  Facts: {stats['facts']}")
    print(f"  Categories: {', '.join(stats['categories'])}")
    print(f"  Topics: {', '.join(stats['topics'][:10])}")


def interactive_teach():
    """Interactive teaching session."""
    ks = KnowledgeStore()
    print("\n[Jessica Teaching Mode]")
    print("Commands: fact <topic> <fact> | doc <title> <content> | file <path> | web <url> | recipe <name> | list | quit")
    
    while True:
        cmd = input("\n> ").strip()
        if not cmd:
            continue
        
        parts = cmd.split(maxsplit=2)
        if not parts:
            continue
        
        action = parts[0].lower()
        
        if action == "quit" or action == "exit":
            print("[teach] Goodbye!")
            break
        elif action == "list":
            list_knowledge()
        elif action == "fact" and len(parts) >= 3:
            topic = parts[1]
            fact = parts[2]
            teach_fact(topic, fact)
        elif action == "doc" and len(parts) >= 3:
            title = parts[1]
            content = parts[2]
            teach_document(title, content)
        elif action == "file" and len(parts) >= 2:
            teach_from_file(parts[1])
        elif action == "web" and len(parts) >= 2:
            teach_from_web(parts[1])
        elif action == "recipe":
            print("Recipe name:")
            name = input("  > ")
            print("Ingredients (comma separated):")
            ingredients = input("  > ")
            print("Instructions (pipe | separated steps):")
            instructions = input("  > ")
            print("Category (breakfast/lunch/dinner/dessert):")
            category = input("  > ") or "general"
            teach_recipe(name, ingredients, instructions, category)
        else:
            print("[teach] Unknown command. Try: fact | doc | file | web | recipe | list | quit")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        interactive_teach()
    else:
        cmd = sys.argv[1].lower()
        
        if cmd == "fact":
            if len(sys.argv) >= 4:
                teach_fact(sys.argv[2], sys.argv[3])
            else:
                print("Usage: teach_jessica.py fact <topic> <fact>")
        elif cmd == "doc":
            if len(sys.argv) >= 4:
                teach_document(sys.argv[2], sys.argv[3])
            else:
                print("Usage: teach_jessica.py doc <title> <content>")
        elif cmd == "file":
            if len(sys.argv) >= 3:
                teach_from_file(sys.argv[2])
            else:
                print("Usage: teach_jessica.py file <filepath>")
        elif cmd == "web":
            if len(sys.argv) >= 3:
                teach_from_web(sys.argv[2])
            else:
                print("Usage: teach_jessica.py web <url>")
        elif cmd == "list":
            list_knowledge()
        else:
            print(f"Unknown command: {cmd}")
