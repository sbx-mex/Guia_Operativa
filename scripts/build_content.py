from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from cms_engine import CMS_PATH, ROOT, load_cms


def atomic_write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(value)
        Path(temporary).replace(path)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera el motor web desde el CMS Excel.")
    parser.add_argument("--check", action="store_true", help="Comprueba que los archivos generados estén sincronizados.")
    args = parser.parse_args()
    data = load_cms(CMS_PATH)
    json_text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    js_text = "window.GUIDE_CMS = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
    targets = {ROOT / "data" / "content.json": json_text, ROOT / "data" / "content.js": js_text}
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, expected in targets.items() if not path.exists() or path.read_text(encoding="utf-8") != expected]
        if stale:
            raise SystemExit("Motor desactualizado; ejecuta python scripts/build_content.py: " + ", ".join(stale))
    else:
        for path, value in targets.items():
            atomic_write(path, value)
    print(f"Motor CMS válido: {len(data['contents'])} módulos, {len(data['steps'])} pasos, {len(data['catalog'])} referencias")


if __name__ == "__main__":
    main()
