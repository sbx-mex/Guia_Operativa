from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from openpyxl import load_workbook
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def load():
    return json.loads((ROOT / "data" / "content.json").read_text(encoding="utf-8"))


def test_generated_engine_is_synced_with_cms():
    subprocess.run([sys.executable, "scripts/build_content.py", "--check"], cwd=ROOT, check=True)
    assert load()["meta"]["source"] == "outputs/CMS_Guia_Operativa_v2.xlsx"


def test_cms_has_required_tabs_and_headers():
    book = load_workbook(ROOT / "outputs" / "CMS_Guia_Operativa_v2.xlsx", read_only=True, data_only=True)
    expected = {"Instrucciones", "Contenidos", "Selectores", "Opciones", "Rutas", "Pasos", "Equipo", "Normas", "Medios", "Auditoria"}
    assert expected.issubset(book.sheetnames)
    assert [cell.value for cell in book["Medios"][4]][:6] == ["ID_MEDIO", "NOMBRE", "CATEGORIA", "SUBCATEGORIA", "IMAGEN_PRODUCTO", "FICHA_REFERENCIA"]
    book.close()


def test_every_catalog_media_exists_and_is_valid():
    for item in load()["catalog"]:
        for key in ("productImage", "referenceImage"):
            path = ROOT / item[key]
            assert path.exists(), path
            with Image.open(path) as image:
                image.verify()


def test_process_reference_media_is_packaged():
    for name in ("cold-brew-toddy.webp", "croissant-mantequilla.webp", "pan-queso.webp"):
        assert (ROOT / "assets" / "references" / "procesos" / name).is_file()


def test_routes_have_sequential_steps():
    data = load()
    routes = {route for content in data["contents"] for route in content["routes"].values()}
    assert routes == {step["route"] for step in data["steps"]}
    for route in routes:
        orders = sorted(step["order"] for step in data["steps"] if step["route"] == route)
        assert orders == list(range(1, len(orders) + 1)), route


def test_cream_omits_roast_and_toddy_parameters_are_real():
    data = load()
    cream = [step["title"].lower() for step in data["steps"] if step["route"] == "frap-cajeta-cream"]
    assert cream[0] == "vierte la leche" and not any("roast" in title for title in cream)
    complete = " ".join(step["values"] for step in data["steps"] if step["route"] == "toddy-completa")
    half = " ".join(step["values"] for step in data["steps"] if step["route"] == "toddy-media")
    assert all(value in complete for value in ("5 lb", "7 L", "20 horas", "5 días"))
    assert all(value in half for value in ("3 lb", "4.5 L", "20 horas", "5 días"))


def test_no_obsolete_empty_or_oversized_files():
    forbidden = ("data/recipes.js", "data/catalog.json", "data/catalog_audit.json", "scripts/build_recipes.py", "scripts/catalog_import.py",
                 "scripts/process_media.py", "outputs/CMS_Recetarios_Manuales_Frappuccino.xlsx", "assets/references/frias/frias-06.tmp.webp")
    assert not any((ROOT / name).exists() for name in forbidden)
    files = [path for path in ROOT.rglob("*") if path.is_file() and not {".git", ".venv", "_site"}.intersection(path.parts)]
    assert all((path.name == ".nojekyll" or path.stat().st_size > 0) and path.stat().st_size < 25 * 1024 * 1024 for path in files)
    for directory in [path for path in (ROOT / "assets").rglob("*") if path.is_dir()]:
        assert len([path for path in directory.iterdir() if path.is_file()]) < 100


def test_catalog_has_names_unique_ids_and_operational_categories():
    catalog = load()["catalog"]
    assert all(item["name"].strip() for item in catalog)
    assert len({item["id"] for item in catalog}) == len(catalog)
    assert {"Bebidas", "Procesos", "Alimentos"}.issubset({item["category"] for item in catalog})


def test_html_references_and_accessibility_landmarks_exist():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    for match in re.findall(r'(?:src|href)="([^"#]+)"', html):
        if not match.startswith(("http://", "https://")):
            assert (ROOT / match).exists(), match
    assert 'class="skip-link"' in html and 'aria-live="polite"' in html
