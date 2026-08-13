from __future__ import annotations

from pathlib import Path
from PIL import Image
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def load():
    return json.loads((ROOT / "data" / "content.json").read_text(encoding="utf-8"))


def test_every_catalog_media_exists_and_is_valid():
    data = load()
    for item in data["catalog"]:
        for key in ("productImage", "referenceImage"):
            path = ROOT / item[key]
            assert path.exists(), path
            with Image.open(path) as image:
                image.verify()


def test_routes_have_steps():
    data = load()
    routes = {route for content in data["contents"] for route in content["routes"].values()}
    step_routes = {step["route"] for step in data["steps"]}
    assert routes == step_routes


def test_route_orders_are_unique_and_sequential():
    data = load()
    for route in {step["route"] for step in data["steps"]}:
        orders = sorted(step["order"] for step in data["steps"] if step["route"] == route)
        assert orders == list(range(1, len(orders) + 1)), route


def test_cream_omits_roast():
    data = load()
    cream = [step["title"].lower() for step in data["steps"] if step["route"] == "frap-cajeta-cream"]
    assert not any("roast" in title for title in cream)
    assert cream[0] == "vierte la leche"


def test_toddy_real_parameters():
    data = load()
    complete = " ".join(step["values"] for step in data["steps"] if step["route"] == "toddy-completa")
    half = " ".join(step["values"] for step in data["steps"] if step["route"] == "toddy-media")
    assert "5 lb" in complete and "7 L" in complete and "20 horas" in complete and "5 días" in complete
    assert "3 lb" in half and "4.5 L" in half and "20 horas" in half and "5 días" in half


def test_distribution_limits():
    files = [path for path in ROOT.rglob("*") if path.is_file() and "source" not in path.parts]
    assert max(path.stat().st_size for path in files) < 25 * 1024 * 1024
    for directory in [path for path in (ROOT / "assets").rglob("*") if path.is_dir()]:
        assert len([path for path in directory.iterdir() if path.is_file()]) < 100


def test_html_references_exist():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    for match in re.findall(r'(?:src|href)="([^"#]+)"', html):
        if match.startswith(("http", "https")):
            continue
        assert (ROOT / match).exists(), match
