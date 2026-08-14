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
    expected = {"Instrucciones", "Contenidos", "Selectores", "Opciones", "Rutas", "Pasos", "Equipo", "Normas", "Medios", "Auditoria", "Campanas"}
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
    legacy = {"assets/references/frias/frias-06.tmp.webp"}
    files = [path for path in ROOT.rglob("*") if path.is_file() and not {".git", ".venv", ".venv-ci", "_site"}.intersection(path.parts)
             and str(path.relative_to(ROOT)).replace("\\", "/") not in legacy]
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
    assert 'apple-mobile-web-app-capable' in html
    assert 'id="installApp"' in html and 'id="evaluationDialog"' in html


def test_unicorn_campaign_and_grande_only_routes_are_safe():
    data = load()
    contents = {item["id"]: item for item in data["contents"]}
    for content_id in ("unicorn-frappuccino", "salsa-azul-drizzle"):
        assert contents[content_id]["selectors"] == [{"id": "size", "label": "Tamaño", "options": ["GRANDE"]}]
        assert set(contents[content_id]["routes"]) == {"size=GRANDE"}
    unicorn_steps = [step for step in data["steps"] if step["route"] == "unicorn-frappuccino"]
    assert len(unicorn_steps) == 9
    assert any("1 espiral" in step["values"] for step in unicorn_steps)
    campaign = data["meta"]["campaigns"][0]
    assert campaign["start"] == "2026-08-13" and campaign["end"] == "2026-08-17"
    assert campaign["timezone"] == "America/Mexico_City"
    for media in campaign["resources"]:
        assert (ROOT / media).is_file()
    salsa = [step for step in data["steps"] if step["route"] == "salsa-azul-drizzle"]
    assert salsa[0]["values"] == "GRANDE=6 pumps CBS"
    assert salsa[3]["values"] == "GRANDE=8 pumps CBS"


def test_pwa_is_ios_ready_offline_and_contextual():
    manifest = json.loads((ROOT / "manifest.webmanifest").read_text(encoding="utf-8"))
    assert manifest["id"] == "./" and manifest["scope"] == "./"
    assert manifest["orientation"] == "portrait-primary"
    assert {item["url"] for item in manifest["shortcuts"]} == {"./#capacitar", "./#recetario", "./#objetivos"}
    worker = (ROOT / "sw.js").read_text(encoding="utf-8")
    assert "self.skipWaiting()" in worker and "self.clients.claim()" in worker
    assert "offline.html" in worker
    app = (ROOT / "app.js").read_text(encoding="utf-8")
    assert "campaignResourceCopy" in app and "unicornQuiz" in app
    assert "beforeinstallprompt" in app and "Agregar a inicio" in app


def test_clean_site_builder_excludes_legacy_data():
    subprocess.run([sys.executable, "scripts/prepare_site.py"], cwd=ROOT, check=True)
    assert {path.name for path in (ROOT / "_site" / "data").iterdir()} == {"content.js", "content.json", "objectives.js", "objectives.json"}
    assert (ROOT / "_site" / "offline.html").is_file()


def test_objectives_engine_and_practice_evidence_are_integrated():
    template = json.loads((ROOT / "data" / "objectives.json").read_text(encoding="utf-8"))
    assert template["schemaVersion"] == 1
    assert {item["id"] for item in template["products"]} == {"unicorn", "cake-pop"}
    assert len(template["days"]) == 3
    assert all((ROOT / item["image"]).is_file() for item in template["products"])
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert 'id="objectivesView"' in html and 'id="evaluationPhoto"' in html
    assert 'capture="environment"' in html
    engine = (ROOT / "objectives.js").read_text(encoding="utf-8")
    assert "window.OBJECTIVES_TEMPLATE" in (ROOT / "data" / "objectives.js").read_text(encoding="utf-8")
    assert "navigator.share" in engine and "window.print()" in engine


def test_python_objectives_exporter_is_safe_and_available():
    script = (ROOT / "scripts" / "export_objectives.py").read_text(encoding="utf-8")
    assert "def validate" in script and "def create_pdf" in script
    assert "schemaVersion" in script and "ZoneInfo" in script


def test_python_objectives_exporter_generates_one_page_pdf(tmp_path):
    from scripts.export_objectives import create_pdf
    from pypdf import PdfReader

    data = json.loads((ROOT / "data" / "objectives.json").read_text(encoding="utf-8"))
    data["store"] = {"ceco": "38101", "name": "Luna Park"}
    data["values"] = {
        "2026-08-15": {"unicorn": {"goal": 30, "actual": 24}, "cake-pop": {"goal": 20, "actual": 18}},
        "2026-08-16": {"unicorn": {"goal": 35, "actual": 0}, "cake-pop": {"goal": 22, "actual": 0}},
        "2026-08-17": {"unicorn": {"goal": 28, "actual": 0}, "cake-pop": {"goal": 18, "actual": 0}},
    }
    output = tmp_path / "objetivos.pdf"
    create_pdf(data, output)
    reader = PdfReader(output)
    assert len(reader.pages) == 1
    extracted = reader.pages[0].extract_text()
    assert all(value in extracted for value in ("Luna Park", "38101", "Unicorn Frappuccino", "Cake Pop Unicornio", "80%"))
