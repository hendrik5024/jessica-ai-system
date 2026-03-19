#!/usr/bin/env python3
"""Replace absolute occurrences of D:/Coding/Jessica -> D:/Coding/Jessica across repo.
Skips common binary/build folders and makes backups of changed files.
Also renames AGI.code-workspace -> Jessica.code-workspace if present.
"""
import os
from pathlib import Path
import shutil

BASE_DIR = Path(__file__).resolve().parent.parent

REPO = Path.cwd()
SKIP_DIRS = {'.git', '.venv', 'build', 'node_modules'}
CHANGES = []

REPLACEMENTS = [
    ("D:\\Coding\\AGI", str(BASE_DIR)),
    ("D:\\Coding\\Jessica", str(BASE_DIR)),
    ("d:\\Coding\\AGI", str(BASE_DIR)),
    ("d:\\Coding\\Jessica", str(BASE_DIR)),
]

def should_skip(path: Path):
    parts = {p for p in path.parts}
    if parts & SKIP_DIRS:
        return True
    # skip large generated build folders under llama.cpp/build
    if 'llama.cpp' in path.parts and 'build' in path.parts:
        return True
    return False

def try_read_text(path: Path):
    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return None
    except Exception:
        return None

def process_file(path: Path):
    txt = try_read_text(path)
    if txt is None:
        return False
    new = txt
    for a,b in REPLACEMENTS:
        if a in new:
            new = new.replace(a,b)
    if new != txt:
        bak = path.with_suffix(path.suffix + '.bak')
        shutil.copy2(path, bak)
        path.write_text(new, encoding='utf-8')
        CHANGES.append(str(path.relative_to(REPO)))
        return True
    return False

def main():
    for root, dirs, files in os.walk(REPO):
        rootp = Path(root)
        # mutate dirs in-place to skip
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not (rootp.name == 'llama.cpp' and d == 'build')]
        for f in files:
            p = rootp / f
            if should_skip(p):
                continue
            # skip binaries by extension
            if p.suffix.lower() in {'.exe', '.dll', '.pdb', '.vcxproj', '.png', '.jpg', '.zip'}:
                continue
            process_file(p)

    # rename workspace file if present
    old_ws = REPO / 'AGI.code-workspace'
    new_ws = REPO / 'Jessica.code-workspace'
    if old_ws.exists() and not new_ws.exists():
        old_ws.rename(new_ws)
        CHANGES.append(str(old_ws.name) + ' -> ' + str(new_ws.name))

    print(f"Completed. Files changed: {len(CHANGES)}")
    for c in CHANGES[:200]:
        print(c)

if __name__ == '__main__':
    main()
