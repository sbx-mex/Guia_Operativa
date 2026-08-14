from __future__ import annotations

import argparse
import csv
import json
import shutil
from collections import defaultdict
from pathlib import Path

from export_objectives import create_pdf

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "objectives.csv"
JSON_OUTPUT = ROOT / "data" / "objectives.json"
JS_OUTPUT = ROOT / "data" / "objectives.js"
SHARD_DIR = ROOT / "data" / "objectives-data"

DAYS = (
    ("2026-08-15", "Sábado 15 de agosto"),
    ("2026-08-16", "Domingo 16 de agosto"),
    ("2026-08-17", "Lunes 17 de agosto"),
)
PRODUCTS = (
    {"id": "adt", "name": "ADT", "note": "Órdenes del día", "unit": "ADT", "icon": "ADT", "accent": "#006241"},
    {"id": "unicorn", "name": "Unicorn Frappuccino", "note": "Objetivo diario · Tamaño Grande", "unit": "USD", "image": "assets/products/temporada/unicorn-frappuccino.webp", "accent": "#e64f9b"},
    {"id": "cake-pop", "name": "Cake Pop Unicornio", "note": "Objetivo diario", "unit": "USD", "image": "assets/products/temporada/cake-pop-unicornio.png", "accent": "#8e5aac"},
)


def clean_text(value: str) -> str:
    return " ".join(value.strip().split())


def integer(value: str, row_number: int, column: str) -> int:
    try:
        parsed = round(float(value.strip().replace(",", "")))
    except ValueError as exc:
        raise ValueError(f"Fila {row_number}: {column} no es numérico") from exc
    if parsed < 0:
        raise ValueError(f"Fila {row_number}: {column} no puede ser negativo")
    return parsed


def pdf_relative_path(ceco: str) -> str:
    return f"assets/documents/objectives/{ceco[:3]}/{ceco}_Objetivos_Unicorn.pdf"


def load_stores(source: Path = SOURCE) -> list[dict]:
    stores: list[dict] = []
    seen: set[str] = set()
    with source.open(encoding="utf-8-sig", newline="") as stream:
        rows = csv.reader(stream)
        header = next(rows, None)
        if not header or len(header) != 7:
            raise ValueError("El CSV de objetivos debe contener exactamente 7 columnas")
        for row_number, row in enumerate(rows, start=2):
            if not any(cell.strip() for cell in row):
                continue
            if len(row) != 7:
                raise ValueError(f"Fila {row_number}: se esperaban 7 columnas")
            ceco = clean_text(row[0])
            name = clean_text(row[1])
            if not ceco.isdigit() or not name:
                raise ValueError(f"Fila {row_number}: CC o tienda inválidos")
            if ceco in seen:
                raise ValueError(f"Fila {row_number}: CC duplicado {ceco}")
            seen.add(ceco)
            adt = [integer(row[index], row_number, f"ADT día {index - 1}") for index in range(2, 5)]
            unicorn = integer(row[5], row_number, "Unicorn Frappuccino")
            cake_pop = integer(row[6], row_number, "Cake Pop Unicornio")
            goals = {
                day_id: {"adt": adt[index], "unicorn": unicorn, "cake-pop": cake_pop}
                for index, (day_id, _) in enumerate(DAYS)
            }
            stores.append({"ceco": ceco, "name": name, "goals": goals, "objectivePdf": pdf_relative_path(ceco)})
    return sorted(stores, key=lambda store: int(store["ceco"]))


def build_template(source: Path = SOURCE) -> dict:
    return {
        "schemaVersion": 3,
        "campaign": {
            "id": "unicorn-2026",
            "name": "Dash de ventas · Unicorn",
            "source": "Voz de Operaciones",
            "operationsUpdate": "14 de agosto de 2026",
            "timezone": "America/Mexico_City",
            "start": DAYS[0][0],
            "end": DAYS[-1][0],
        },
        "products": list(PRODUCTS),
        "days": [{"id": day_id, "label": label} for day_id, label in DAYS],
        "stores": load_stores(source),
        "store": {"ceco": "", "name": ""},
        "values": {},
    }


def public_template(template: dict) -> dict:
    public = {key: value for key, value in template.items() if key != "stores"}
    public["stores"] = [{"ceco": store["ceco"], "name": store["name"]} for store in template["stores"]]
    public["storeDataPath"] = "data/objectives-data/{prefix}.json"
    return public


def serialize(template: dict) -> tuple[str, str, dict[str, str]]:
    compact = json.dumps(public_template(template), ensure_ascii=False, separators=(",", ":"))
    groups: dict[str, list[dict]] = defaultdict(list)
    for store in template["stores"]:
        groups[store["ceco"][:3]].append(store)
    shards = {
        f"{prefix}.json": json.dumps({"schemaVersion": 3, "stores": stores}, ensure_ascii=False, separators=(",", ":")) + "\n"
        for prefix, stores in sorted(groups.items())
    }
    return compact + "\n", f"window.OBJECTIVES_TEMPLATE = {compact};\n", shards


def write_outputs(json_text: str, js_text: str, shards: dict[str, str]) -> None:
    JSON_OUTPUT.write_text(json_text, encoding="utf-8")
    JS_OUTPUT.write_text(js_text, encoding="utf-8")
    if SHARD_DIR.exists():
        shutil.rmtree(SHARD_DIR)
    SHARD_DIR.mkdir(parents=True)
    for name, content in shards.items():
        (SHARD_DIR / name).write_text(content, encoding="utf-8")


def outputs_match(json_text: str, js_text: str, shards: dict[str, str]) -> bool:
    if not JSON_OUTPUT.is_file() or not JS_OUTPUT.is_file() or not SHARD_DIR.is_dir():
        return False
    if JSON_OUTPUT.read_text(encoding="utf-8") != json_text or JS_OUTPUT.read_text(encoding="utf-8") != js_text:
        return False
    existing = {path.name for path in SHARD_DIR.glob("*.json")}
    return existing == set(shards) and all((SHARD_DIR / name).read_text(encoding="utf-8") == content for name, content in shards.items())


def store_document(template: dict, store: dict) -> dict:
    document = {key: value for key, value in template.items() if key != "stores"}
    document["store"] = {"ceco": store["ceco"], "name": store["name"]}
    document["values"] = {
        day["id"]: {
            product["id"]: {"goal": store["goals"][day["id"]][product["id"]], "actual": 0}
            for product in template["products"]
        }
        for day in template["days"]
    }
    return document


def generate_pdfs(template: dict, destination: Path, limit: int | None = None) -> int:
    stores = template["stores"][:limit] if limit else template["stores"]
    for store in stores:
        relative = Path(store["objectivePdf"]).relative_to("assets/documents/objectives")
        output = destination / relative
        create_pdf(store_document(template, store), output, title="Objetivos diarios")
    return len(stores)


def main() -> None:
    parser = argparse.ArgumentParser(description="Construye el catálogo de objetivos por tienda y sus PDFs ligeros.")
    parser.add_argument("--check", action="store_true", help="Valida que los archivos generados estén actualizados")
    parser.add_argument("--pdf-root", type=Path, help="Genera PDFs de objetivos bajo esta carpeta")
    parser.add_argument("--limit", type=int, help="Limita PDFs; útil para validación local")
    args = parser.parse_args()
    template = build_template()
    json_text, js_text, shards = serialize(template)
    if args.check:
        if not outputs_match(json_text, js_text, shards):
            raise SystemExit("El índice o los paquetes de objetivos no están actualizados")
    else:
        write_outputs(json_text, js_text, shards)
        print(f"Objetivos generados: {len(template['stores'])} tiendas en {len(shards)} paquetes por CeCo")
    if args.pdf_root:
        count = generate_pdfs(template, args.pdf_root, args.limit)
        print(f"PDFs de objetivos generados: {count}")


if __name__ == "__main__":
    main()
