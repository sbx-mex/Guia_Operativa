from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
FILES = ("index.html", "app.js", "styles.css", "manifest.webmanifest", "sw.js", ".nojekyll")


def main() -> None:
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    for name in FILES:
        shutil.copy2(ROOT / name, SITE / name)
    for name in ("assets", "data"):
        shutil.copytree(ROOT / name, SITE / name)
    unexpected = {"source", "outputs", "scripts", "tests"}.intersection(path.name for path in SITE.iterdir())
    if unexpected:
        raise SystemExit(f"Contenido privado en publicación: {sorted(unexpected)}")
    print(f"Sitio limpio: {sum(1 for path in SITE.rglob('*') if path.is_file())} archivos")


if __name__ == "__main__":
    main()
