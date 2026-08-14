from __future__ import annotations

import json
import re

from PIL import Image

from cms_engine import ROOT, load_cms

FORBIDDEN = {"data/recipes.js", "data/catalog.json", "data/catalog_audit.json", "scripts/build_recipes.py", "scripts/catalog_import.py",
             "scripts/process_media.py", "outputs/CMS_Recetarios_Manuales_Frappuccino.xlsx", "assets/references/frias/frias-06.tmp.webp",
             "assets/campaigns/unicorn-impacto.mp4"}


def main() -> None:
    data = load_cms()
    failures: list[str] = []
    warnings: list[str] = []
    if any(not item["name"].strip() for item in data["catalog"]):
        failures.append("El catálogo contiene nombres vacíos")
    if len({item["id"] for item in data["catalog"]}) != len(data["catalog"]):
        failures.append("El catálogo contiene IDs duplicados")
    if not {"Bebidas", "Procesos", "Alimentos"}.issubset({item["category"] for item in data["catalog"]}):
        failures.append("Falta una categoría operativa obligatoria")
    media = {(item[key], item["id"]) for item in data["catalog"] for key in ("productImage", "referenceImage")}
    media.update((item[key], item["id"]) for item in data["contents"] for key in ("productImage", "referenceImage"))
    media.update((path, campaign["id"]) for campaign in data["meta"].get("campaigns", []) for path in campaign["resources"])
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
            warnings.append(f"Archivo obsoleto pendiente de limpieza manual: {relative}")
    for path in ROOT.rglob("*"):
        if not path.is_file() or {".git", ".venv", ".venv-ci", "_site"}.intersection(path.parts):
            continue
        if path.stat().st_size >= 25 * 1024 * 1024:
            failures.append(f"Archivo >=25 MB: {path.relative_to(ROOT)}")
        if path.stat().st_size == 0 and path.name != ".nojekyll" and str(path.relative_to(ROOT)).replace("\\", "/") not in FORBIDDEN:
            failures.append(f"Archivo vacío: {path.relative_to(ROOT)}")
    for directory in (ROOT / "assets").rglob("*"):
        if directory.is_dir() and len([entry for entry in directory.iterdir() if entry.is_file()]) >= 100:
            failures.append(f"Carpeta con 100+ archivos: {directory.relative_to(ROOT)}")
    campaign_video = ROOT / "assets" / "campaigns" / "unicorn-impacto-v2.mp4"
    campaign_fallback = ROOT / "assets" / "campaigns" / "unicorn-impacto-fallback.webp"
    campaign_poster = ROOT / "assets" / "campaigns" / "unicorn-impacto-poster.webp"
    if not campaign_video.is_file() or campaign_video.stat().st_size >= 150_000:
        failures.append("Video Unicorn ausente o sin optimizar")
    try:
        with Image.open(campaign_fallback) as image:
            image.verify()
    except Exception as exc:
        failures.append(f"Animación alternativa Unicorn inválida: {exc}")
    try:
        with Image.open(campaign_poster) as image:
            image.verify()
    except Exception as exc:
        failures.append(f"Póster del video Unicorn inválido: {exc}")
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    for relative in re.findall(r'(?:src|href)="([^"#]+)"', html):
        if not relative.startswith(("http://", "https://")) and not (ROOT / relative).exists():
            failures.append(f"Recurso HTML ausente: {relative}")
    objectives_path = ROOT / "data" / "objectives.json"
    if not objectives_path.is_file():
        failures.append("Motor de objetivos ausente: data/objectives.json")
    else:
        try:
            objectives = json.loads(objectives_path.read_text(encoding="utf-8"))
            if objectives.get("schemaVersion") != 4:
                failures.append("Versión inválida del motor de objetivos")
            if not objectives.get("products") or not objectives.get("days"):
                failures.append("Motor de objetivos sin productos o días")
            if [cut.get("id") for cut in objectives.get("cuts", [])] != ["am", "inter", "pm"]:
                failures.append("Motor de objetivos sin los tres turnos operativos")
            if not objectives.get("stores"):
                failures.append("Motor de objetivos sin tiendas")
            cecos = [item.get("ceco", "") for item in objectives.get("stores", [])]
            if cecos != sorted(cecos, key=lambda value: int(value)):
                failures.append("Las tiendas no están ordenadas por CeCo")
            shard_dir = ROOT / "data" / "objectives-data"
            shard_stores = []
            for path in sorted(shard_dir.glob("*.json")):
                shard = json.loads(path.read_text(encoding="utf-8"))
                if shard.get("schemaVersion") != 3:
                    failures.append(f"Paquete de objetivos inválido: {path.name}")
                shard_stores.extend(shard.get("stores", []))
            if len(shard_stores) != len(objectives.get("stores", [])):
                failures.append("Los paquetes por CeCo no coinciden con el índice")
            for product in objectives.get("products", []):
                if product.get("image") and not (ROOT / product["image"]).is_file():
                    failures.append(f"Imagen de objetivo ausente: {product.get('image')}")
            terms = ROOT / "assets" / "documents" / "terminos-y-condiciones-unicorn.pdf"
            if not terms.is_file() or not terms.stat().st_size:
                failures.append("PDF de términos y condiciones ausente")
        except (json.JSONDecodeError, TypeError) as exc:
            failures.append(f"JSON de objetivos inválido: {exc}")
    controls = {"cms_source": data["meta"]["source"], "modules": len(data["contents"]), "steps": len(data["steps"]),
                "catalog_items": len(data["catalog"]), "media_checked": len(media), "failures": len(failures),
                "routes": len({route for item in data["contents"] for route in item["routes"].values()}),
                "warnings": len(warnings), "status": "OK" if not failures else "ERROR"}
    print(json.dumps(controls, ensure_ascii=False))
    for warning in warnings:
        print(f"::warning::{warning}")
    if failures:
        raise SystemExit("\n".join(failures))


if __name__ == "__main__":
    main()
