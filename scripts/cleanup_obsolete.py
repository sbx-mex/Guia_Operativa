#!/usr/bin/env python3
"""Impide que artefactos de campañas obsoletas vuelvan al proyecto CORE."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PARTS = ("uni" + "corn", "object" + "ives", "salsa-azul", "cake-pop", "lavanda")
OBSOLETE = {
    "object" + "ives.js", "data/object" + "ives.csv", "data/object" + "ives.js", "data/object" + "ives.json",
    "scripts/build_object" + "ives.py", "scripts/export_object" + "ives.py",
    "outputs/CMS_Guia_Operativa_v2.xlsx",
}

def main() -> int:
    found = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in {".git", "_site"} for part in path.parts):
            continue
        relative = path.relative_to(ROOT).as_posix().lower()
        if relative in {item.lower() for item in OBSOLETE} or any(token in relative for token in FORBIDDEN_PARTS):
            found.append(relative)
    print(json.dumps({"status":"ok" if not found else "error","obsolete":sorted(found)}, ensure_ascii=False))
    return 0 if not found else 1

if __name__ == "__main__":
    raise SystemExit(main())
