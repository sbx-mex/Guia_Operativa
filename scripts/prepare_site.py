#!/usr/bin/env python3
"""Construye el directorio estático publicable de la Guía CORE."""
from __future__ import annotations
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
FILES = ("index.html", "offline.html", "app.js", "styles.css", "manifest.webmanifest", "sw.js", ".nojekyll")

def main() -> int:
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    for name in FILES:
        shutil.copy2(ROOT / name, SITE / name)
    (SITE / "data").mkdir()
    for name in ("content.js", "content.json"):
        shutil.copy2(ROOT / "data" / name, SITE / "data" / name)
    shutil.copytree(ROOT / "assets", SITE / "assets")
    print(f"Sitio CORE preparado en {SITE}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
