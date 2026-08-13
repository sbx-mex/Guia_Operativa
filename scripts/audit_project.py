from __future__ import annotations

import json
import re

from PIL import Image

from cms_engine import ROOT, load_cms

FORBIDDEN = {"data/recipes.js", "data/catalog.json", "data/catalog_audit.json", "scripts/build_recipes.py", "scripts/catalog_import.py",
             "scripts/process_media.py", "outputs/CMS_Recetarios_Manuales_Frappuccino.xlsx", "assets/references/frias/frias-06.tmp.webp"}


def main() -> None:
    data = load_cms()
    failures: list[str] = []
    if any(not item["name"].strip() for item in data["catalog"]):
        failures.append("El catálogo contiene nombres vacíos")
    if len({item["id"] for item in data["catalog"]}) != len(data["catalog"]):
        failures.append("El catálogo contiene IDs duplicados")
    if not {"Bebidas", "Procesos", "Alimentos"}.issubset({item["category"] for item in data["catalog"]}):
        failures.append("Falta una categoría operativa obligatoria")
    media = {(item[key], item["id"]) for item in data["catalog"] for key in ("productImage", "referenceImage")}
    media.update((item[key], item["id"]) for item in data["contents"] for key in ("productImage", "referenceImage"))
    for relative, owner in sorted(media):
        path = ROOT / relative
        if not path.is_file():
            failures.append(f"Medio ausente ({owner}): {relative}")
            continue
        try:
            with Image.open(path) as image:
                image.verify()
        except Exception as exc:
            failures.append(f"Imagen inválida {relative}: {exc}")
    for relative in FORBIDDEN:
        if (ROOT / relative).exists():
            failures.append(f"Archivo obsoleto presente: {relative}")
    for path in ROOT.rglob("*"):
        if not path.is_file() or {".git", ".venv", "_site"}.intersection(path.parts):
            continue
        if path.stat().st_size >= 25 * 1024 * 1024:
            failures.append(f"Archivo >=25 MB: {path.relative_to(ROOT)}")
        if path.stat().st_size == 0 and path.name != ".nojekyll":
            failures.append(f"Archivo vacío: {path.relative_to(ROOT)}")
    for directory in (ROOT / "assets").rglob("*"):
        if directory.is_dir() and len([entry for entry in directory.iterdir() if entry.is_file()]) >= 100:
            failures.append(f"Carpeta con 100+ archivos: {directory.relative_to(ROOT)}")
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    for relative in re.findall(r'(?:src|href)="([^"#]+)"', html):
        if not relative.startswith(("http://", "https://")) and not (ROOT / relative).exists():
            failures.append(f"Recurso HTML ausente: {relative}")
    controls = {"cms_source": data["meta"]["source"], "modules": len(data["contents"]), "steps": len(data["steps"]),
                "catalog_items": len(data["catalog"]), "media_checked": len(media), "failures": len(failures),
                "routes": len({route for item in data["contents"] for route in item["routes"].values()}),
                "status": "OK" if not failures else "ERROR"}
    print(json.dumps(controls, ensure_ascii=False))
    if failures:
        raise SystemExit("\n".join(failures))


if __name__ == "__main__":
    main()
