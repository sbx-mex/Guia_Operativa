from __future__ import annotations

from pathlib import Path
from PIL import Image
import json
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "catalog.json"


def ocr_title(path: Path) -> str:
    image = Image.open(path).convert("RGB")
    roi = image.crop((0, 0, int(image.width * .49), int(image.height * .34)))
    roi = roi.resize((roi.width * 2, roi.height * 2), Image.Resampling.LANCZOS)
    with tempfile.NamedTemporaryFile(suffix=".png") as temporary:
        roi.save(temporary.name)
        completed = subprocess.run(
            ["tesseract", temporary.name, "stdout", "--psm", "6"],
            capture_output=True, text=True, check=False,
        )
    lines = [re.sub(r"\s+", " ", line).strip() for line in completed.stdout.splitlines()]
    lines = [line for line in lines if len(line) > 4 and not line.upper().startswith(("GUÍA", "PASOS", "RECETA"))]
    return lines[0] if lines else path.stem


def main() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    names = {item["id"]: item["name"] for item in catalog}
    sample = {
        "catalog_items": len(catalog),
        "missing_names": sum(1 for value in names.values() if not value.strip()),
        "duplicate_ids": len(catalog) - len(names),
        "categories": sorted({item["category"] for item in catalog}),
    }
    (ROOT / "data" / "catalog_audit.json").write_text(json.dumps(sample, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(sample, ensure_ascii=False))


if __name__ == "__main__":
    main()
