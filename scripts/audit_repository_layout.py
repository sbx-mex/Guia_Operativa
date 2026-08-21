#!/usr/bin/env python3
"""Valida el núcleo publicable y el CMS canónico."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_FILES = {".gitignore",".nojekyll","README.md","app.js","index.html","manifest.webmanifest","offline.html","requirements.txt","styles.css","sw.js"}
ALLOWED_DIRECTORIES = {".git",".github","assets","data","outputs","scripts","tests"}
IGNORED_DIRECTORIES = {"_site",".venv",".venv-ci",".pytest_cache","node_modules","__pycache__"}

def main() -> int:
    unexpected=[]
    for entry in ROOT.iterdir():
        if entry.name in IGNORED_DIRECTORIES: continue
        if entry.name not in (ALLOWED_DIRECTORIES if entry.is_dir() else ALLOWED_FILES): unexpected.append(entry.name)
    missing=sorted(name for name in ALLOWED_FILES if not (ROOT/name).is_file())
    cms=ROOT/"outputs/CMS_Guia_Operativa_CORE.xlsx"
    status="ok" if not unexpected and not missing and cms.is_file() else "error"
    print(json.dumps({"status":status,"unexpected":sorted(unexpected),"missing":missing,"canonicalCms":cms.relative_to(ROOT).as_posix() if cms.is_file() else None},ensure_ascii=False))
    return 0 if status=="ok" else 1

if __name__ == "__main__":
    raise SystemExit(main())
