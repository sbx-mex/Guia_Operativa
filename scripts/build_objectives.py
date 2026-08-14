from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from export_objectives import create_pdf

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "objectives.csv"
JSON_OUTPUT = ROOT / "data" / "objectives.json"
JS_OUTPUT = ROOT / "data" / "objectives.js"

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
    return sorted(stores, key=lambda store: (store["name"].casefold(), store["ceco"]))


def build_template(source: Path = SOURCE) -> dict:
    return {
        "schemaVersion": 2,
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


def serialize(template: dict) -> tuple[str, str]:
    compact = json.dumps(template, ensure_ascii=False, separators=(",", ":"))
    return compact + "\n", f"window.OBJECTIVES_TEMPLATE = {compact};\n"


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
    json_text, js_text = serialize(template)
    if args.check:
        if JSON_OUTPUT.read_text(encoding="utf-8") != json_text or JS_OUTPUT.read_text(encoding="utf-8") != js_text:
            raise SystemExit("data/objectives.json o data/objectives.js no están actualizados")
    else:
        JSON_OUTPUT.write_text(json_text, encoding="utf-8")
        JS_OUTPUT.write_text(js_text, encoding="utf-8")
        print(f"Objetivos generados: {len(template['stores'])} tiendas")
    if args.pdf_root:
        count = generate_pdfs(template, args.pdf_root, args.limit)
        print(f"PDFs de objetivos generados: {count}")


if __name__ == "__main__":
    main()
