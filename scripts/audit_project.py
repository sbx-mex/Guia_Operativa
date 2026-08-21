#!/usr/bin/env python3
"""Auditoría integral del catálogo CORE, los lotes y sus medios."""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
LOT_LIMIT_FILES = 100
LOT_LIMIT_BYTES = 25 * 1024 * 1024
EXPECTED = {"Lote_01_Bebidas":49,"Lote_02_Bebidas":48,"Lote_01_Recetas":49,"Lote_02_Recetas":48,"Lote_01_Alimentos":6,"GIF_CORE":16}

def main() -> int:
    failures=[]
    data=json.loads((ROOT/"data/content.json").read_text(encoding="utf-8"))
    if data.get("meta",{}).get("version") != "5.0.0-core": failures.append("Versión CMS distinta de 5.0.0-core")
    if len(data.get("contents",[])) != 103 or len(data.get("catalog",[])) != 103: failures.append("Se esperan 103 módulos y 103 medios")
    categories=Counter(item["category"] for item in data["contents"])
    if categories["Alimentos"] != 6 or categories["Bebidas"] + categories["Procesos"] != 97: failures.append(f"Cobertura inválida: {dict(categories)}")
    text=json.dumps(data,ensure_ascii=False).lower()
    if "uni" + "corn" in text: failures.append("El CMS contiene referencias promocionales obsoletas")
    ids=[item["id"] for item in data["contents"]]
    if len(ids) != len(set(ids)): failures.append("ID de contenido duplicado")
    used_routes={route for item in data["contents"] for route in item["routes"].values()}
    step_routes={step["route"] for step in data["steps"]}
    if used_routes != step_routes: failures.append("Rutas y pasos no coinciden")
    for item in data["contents"]:
        if not item["equipment"] or not item["rules"]: failures.append(f"Módulo incompleto: {item['id']}")
        for key in ("productImage","referenceImage"):
            path=ROOT/item[key]
            if not path.is_file(): failures.append(f"Medio ausente: {item[key]}")
    report={}
    for folder,expected in EXPECTED.items():
        path=ROOT/"assets"/folder
        files=[item for item in path.iterdir() if item.is_file()] if path.is_dir() else []
        size=sum(item.stat().st_size for item in files)
        report[folder]={"files":len(files),"bytes":size}
        if len(files) != expected: failures.append(f"{folder}: {len(files)} archivos; se esperaban {expected}")
        if len(files) > LOT_LIMIT_FILES: failures.append(f"{folder}: supera 100 archivos")
        if size >= LOT_LIMIT_BYTES: failures.append(f"{folder}: supera 25 MB")
        for file in files:
            try:
                with Image.open(file) as image: image.verify()
            except Exception as exc: failures.append(f"Imagen inválida {file.relative_to(ROOT)}: {exc}")
    print(json.dumps({"status":"ok" if not failures else "error","modules":len(data["contents"]),"steps":len(data["steps"]),"categories":categories,"folders":report,"failures":failures},ensure_ascii=False,default=dict))
    return 0 if not failures else 1

if __name__ == "__main__":
    raise SystemExit(main())
