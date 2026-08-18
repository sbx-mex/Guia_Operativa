#!/usr/bin/env python3
"""Normaliza las fotos de producto del catálogo sin tocar las fichas de receta."""

from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "content.json"
CANVAS = 720
TARGET = 610
MANUAL_CROPS = {
    # Fichas oficiales donde texto, iconos y bebida comparten el mismo lienzo.
    "assets/products/temporada/pumpkin-spice-latte.webp": (205, 125, 525, 550),
    "assets/products/temporada/pumpkin-spice-latte-helado.webp": (205, 125, 515, 595),
    "assets/products/temporada/pumpkin-spice-frappuccino.webp": (205, 125, 495, 565),
    "assets/products/temporada/cold-brew-pumpkin-cold-foam.webp": (180, 120, 510, 645),
    "assets/products/temporada/chai-latte-helado-pumpkin-cold-foam.webp": (130, 155, 485, 655),
    "assets/products/temporada/cold-foam-pumpkin.webp": (180, 70, 540, 680),
    "assets/products/calientes/calientes-12.webp": (285, 265, 450, 440),
}


def foreground_mask(image: Image.Image, size: int = 240) -> Image.Image:
    sample = image.convert("RGB").resize((size, size), Image.Resampling.LANCZOS)
    white = Image.new("RGB", sample.size, "white")
    difference = ImageChops.difference(sample, white).convert("L")
    mask = difference.point(lambda value: 255 if value > 24 else 0)
    return mask.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(3))


def focus_mask(mask: Image.Image) -> Image.Image:
    """Aísla el centro cuando una ficha visual une bebida, textos y ornamentos."""
    focused = mask.copy()
    pixels = focused.load()
    width, height = focused.size
    for y in range(height):
        for x in range(width):
            if x < width * 0.20 or x > width * 0.80 or y < height * 0.13 or y > height * 0.94:
                pixels[x, y] = 0
    return focused


def components(mask: Image.Image) -> list[tuple[int, tuple[int, int, int, int]]]:
    width, height = mask.size
    pixels = mask.load()
    seen = bytearray(width * height)
    found = []
    for y in range(height):
        for x in range(width):
            index = y * width + x
            if seen[index] or not pixels[x, y]:
                continue
            queue = deque([(x, y)])
            seen[index] = 1
            count = 0
            left = right = x
            top = bottom = y
            while queue:
                px, py = queue.popleft()
                count += 1
                left, right = min(left, px), max(right, px)
                top, bottom = min(top, py), max(bottom, py)
                for nx, ny in ((px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)):
                    if 0 <= nx < width and 0 <= ny < height:
                        neighbor = ny * width + nx
                        if not seen[neighbor] and pixels[nx, ny]:
                            seen[neighbor] = 1
                            queue.append((nx, ny))
            found.append((count, (left, top, right + 1, bottom + 1)))
    return found


def best_component(mask: Image.Image) -> tuple[int, int, int, int] | None:
    width, height = mask.size
    candidates = []
    for area, box in components(mask):
        left, top, right, bottom = box
        box_width, box_height = right - left, bottom - top
        if area < 60 or box_height < height * 0.14 or box_width < width * 0.06:
            continue
        center_x = (left + right) / (2 * width)
        centrality = max(0.08, 1 - abs(center_x - 0.5) * 1.7)
        proportion = min(1.25, box_width / max(1, box_height))
        edge_strip = (left < 3 or right > width - 3) and box_width < width * 0.24 and box_height > height * 0.45
        score = area * (0.65 + centrality) * (0.6 + proportion) * (0.08 if edge_strip else 1)
        candidates.append((score, box))
    return max(candidates)[1] if candidates else None


def product_box(image: Image.Image) -> tuple[int, int, int, int]:
    mask = foreground_mask(image)
    box = best_component(mask)
    if box and (box[2] - box[0]) > mask.width * 0.58:
        box = best_component(focus_mask(mask)) or box
    if not box:
        return (0, 0, image.width, image.height)
    left, top, right, bottom = box
    width, height = mask.size
    scale_x, scale_y = image.width / width, image.height / height
    pad_x = max(14, int((right - left) * scale_x * 0.09))
    pad_y = max(14, int((bottom - top) * scale_y * 0.07))
    return (
        max(0, int(left * scale_x) - pad_x),
        max(0, int(top * scale_y) - pad_y),
        min(image.width, int(right * scale_x) + pad_x),
        min(image.height, int(bottom * scale_y) + pad_y),
    )


def normalize(source: Path) -> Image.Image:
    with Image.open(source) as opened:
        image = opened.convert("RGB")
    relative = source.relative_to(ROOT).as_posix()
    crop = image.crop(MANUAL_CROPS.get(relative, product_box(image)))
    scale = min(TARGET / crop.width, TARGET / crop.height)
    crop = crop.resize((max(1, round(crop.width * scale)), max(1, round(crop.height * scale))), Image.Resampling.LANCZOS)
    crop = ImageEnhance.Contrast(crop).enhance(1.025)
    crop = ImageEnhance.Color(crop).enhance(1.018)
    crop = crop.filter(ImageFilter.UnsharpMask(radius=1.0, percent=85, threshold=3))
    canvas = Image.new("RGB", (CANVAS, CANVAS), "white")
    canvas.paste(crop, ((CANVAS - crop.width) // 2, (CANVAS - crop.height) // 2))
    return canvas


def image_metrics(path: Path) -> dict[str, object]:
    with Image.open(path) as opened:
        image = opened.convert("RGB")
    difference = ImageChops.difference(image, Image.new("RGB", image.size, "white")).convert("L")
    box = difference.point(lambda value: 255 if value > 24 else 0).getbbox()
    if not box:
        return {"size": image.size, "foreground": 0, "margin": 0, "ok": False}
    area = (box[2] - box[0]) * (box[3] - box[1]) / (image.width * image.height)
    margin = min(box[0], box[1], image.width - box[2], image.height - box[3])
    return {"size": image.size, "foreground": round(area, 4), "margin": margin, "ok": image.size == (CANVAS, CANVAS) and margin >= 20 and 0.045 <= area <= 0.78}


def beverage_paths() -> list[Path]:
    payload = json.loads(CATALOG.read_text(encoding="utf-8"))
    return sorted({ROOT / item["productImage"] for item in payload["catalog"] if item.get("category") == "Bebidas"})


def main() -> int:
    parser = argparse.ArgumentParser(description="Recorta y audita las fotos de bebidas del catálogo.")
    parser.add_argument("--write", action="store_true", help="Aplica el recorte normalizado.")
    parser.add_argument("--report", default="reports/product-image-audit.json")
    args = parser.parse_args()
    rows = []
    for path in beverage_paths():
        if not path.is_file():
            rows.append({"path": path.relative_to(ROOT).as_posix(), "ok": False, "error": "archivo ausente"})
            continue
        if args.write:
            normalized = normalize(path)
            normalized.save(path, "WEBP", quality=90, method=6)
        rows.append({"path": path.relative_to(ROOT).as_posix(), **image_metrics(path)})
    report = {
        "status": "ok" if all(row.get("ok") for row in rows) else "error",
        "images": len(rows),
        "approved": sum(bool(row.get("ok")) for row in rows),
        "failed": [row for row in rows if not row.get("ok")],
    }
    target = ROOT / args.report
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
