from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageChops, ImageEnhance, ImageFilter
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
ASSETS = ROOT / "assets"


PACKS = {
    "frappuccino": {
        "folder": "RECETARIO BEBIDAS FRAPPUCCINO",
        "prefix": "RECETARIO BEBIDAS FRAPPUCCINO",
        "category": "Bebidas",
        "subcategory": "Frappuccino",
        "pages": {
            4: "Café Frappuccino", 5: "Cajeta Frappuccino", 6: "Caramel Frappuccino",
            7: "Cinnamon Dolce Frappuccino", 8: "Espresso Frappuccino",
            9: "Frappuccino Chip", 10: "Mocha Blanco Frappuccino",
            11: "Mocha Frappuccino", 13: "Berry Yogurt Frappuccino",
            14: "Chai Cream Frappuccino", 15: "Chocolate Blanco Cream Frappuccino",
            16: "Chocolate Cream Frappuccino", 17: "Chocolate Mexicano Frappuccino",
            18: "Cookies & Cream Frappuccino", 19: "Fresa Cream Frappuccino",
            20: "Matcha Green Tea Cream Frappuccino", 21: "Piñacoco Yogurt Frappuccino",
            22: "Vainilla Cream Frappuccino", 24: "Dragon Fruit Frozen Lemonade",
            25: "Mango Dragon Fruit Frozen Refresher",
            26: "Strawberry Acaí Frozen Refresher", 27: "Strawberry Frozen Lemonade",
        },
        "crop": (185, 205, 500, 650),
    },
    "frias": {
        "folder": "RECETARIO BEBIDAS FRIAS",
        "prefix": "RECETARIO BEBIDAS FRIAS",
        "category": "Bebidas",
        "subcategory": "Frías",
        "pages": {
            4: "Avellana Shaken Espresso Helado", 5: "Brown Sugar Shaken Espresso Helado",
            6: "Caramel Macchiato Helado", 7: "Chocolate Cream Cold Brew",
            8: "Vainilla Sweet Cream", 9: "Cold Brew", 10: "Cold Foam Cappuccino Helado",
            11: "Espresso Americano Helado", 12: "Latte Helado", 13: "Latte Macchiato Helado",
            14: "Mocha Blanco Helado", 15: "Mocha Blanco Shaken Espresso Helado",
            16: "Mocha Helado", 17: "Mocha Shaken Espresso Helado",
            18: "Vainilla Sweet Cream Cold Brew", 21: "Chai Latte Helado",
            22: "Chocolate Helado", 23: "Chocolate Mexicano Helado",
            24: "Dragon Drink Refresher", 25: "Mango Dragon Lemonade Refresher",
            26: "Mango Dragon Refresher", 27: "Matcha Green Tea Helado",
            28: "Matcha Lemonade Helado", 29: "Pink Drink Refresher",
            30: "Shaken Lemon Black Tea", 31: "Shaken Lemon Green Tea",
            32: "Shaken Lemon Hibiscus Tea", 33: "Strawberry Acaí Lemonade Refresher",
            34: "Strawberry Acaí Refresher", 35: "Té Helado Teavana",
        },
        "crop": (185, 205, 500, 650),
    },
    "calientes": {
        "folder": "RECETAS BEBIDAS HOT CORE 26",
        "prefix": "RECETAS BEBIDAS HOT CORE 26",
        "category": "Bebidas",
        "subcategory": "Calientes",
        "pages": {
            4: "Café Misto", 5: "Cajeta Latte", 6: "Cappuccino", 7: "Caramel Macchiato",
            8: "Cinnamon Dolce Latte", 9: "Espresso Americano", 10: "Espresso con Panna",
            11: "Espresso Macchiato", 12: "Espresso", 13: "Flat White",
            14: "Latte Macchiato", 15: "Latte", 16: "Mocha", 17: "Mocha Blanco",
            18: "Té Caliente Teavana", 19: "Cortado", 20: "Vainilla Protein Latte",
            21: "Vainilla Sugar Free Protein Latte", 24: "Chai Latte", 25: "Chocolate",
            26: "Chocolate Blanco", 27: "Chocolate Mexicano", 28: "Leche al Vapor",
            29: "Matcha Green Tea Latte", 30: "Matcha Protein Latte",
        },
        "crop": (185, 205, 500, 650),
    },
    "temporada": {
        "folder": "Recetas_Bebidas_CFS_Summer_2026",
        "prefix": "Recetas_Bebidas_CFS_Summer_2026",
        "category": "Bebidas",
        "subcategory": "Temporada",
        "pages": {1: "Ube Coco Latte", 2: "Ube Coco Frappuccino"},
        "crop": (185, 205, 500, 650),
    },
}


def slug(text: str) -> str:
    table = str.maketrans("áéíóúüñÁÉÍÓÚÜÑ", "aeiouunAEIOUUN")
    return re.sub(r"[^a-z0-9]+", "-", text.translate(table).lower()).strip("-")


def trim_white(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    background = Image.new("RGB", rgb.size, (250, 250, 250))
    diff = ImageChops.difference(rgb, background).convert("L")
    diff = diff.point(lambda p: 255 if p > 22 else 0)
    bbox = diff.getbbox()
    if not bbox:
        return rgb
    left, top, right, bottom = bbox
    pad = 18
    return rgb.crop((max(0, left-pad), max(0, top-pad), min(rgb.width, right+pad), min(rgb.height, bottom+pad)))


def polish(image: Image.Image) -> Image.Image:
    image = ImageEnhance.Contrast(image).enhance(1.035)
    image = ImageEnhance.Color(image).enhance(1.025)
    return image.filter(ImageFilter.UnsharpMask(radius=1.1, percent=105, threshold=3))


def save_product(source: Path, crop: tuple[int, int, int, int], destination: Path) -> None:
    image = Image.open(source).convert("RGB").crop(crop)
    image = trim_white(image)
    image.thumbnail((720, 720), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (720, 720), "white")
    x = (720 - image.width) // 2
    y = (720 - image.height) // 2
    canvas.paste(image, (x, y))
    polish(canvas).save(destination, "WEBP", quality=92, method=6)


def save_reference(source: Path, destination: Path) -> None:
    image = Image.open(source).convert("RGB")
    temporary = destination.with_name(destination.stem + ".tmp.webp")
    image.save(temporary, "WEBP", quality=83, method=6)
    temporary.replace(destination)


def main() -> None:
    catalog = []
    for pack_id, pack in PACKS.items():
        product_dir = ASSETS / "products" / pack_id
        reference_dir = ASSETS / "references" / pack_id
        product_dir.mkdir(parents=True, exist_ok=True)
        reference_dir.mkdir(parents=True, exist_ok=True)
        for page, name in pack["pages"].items():
            source = SOURCE / pack["folder"] / f'{pack["prefix"]}_{page}.jpg'
            item_id = f"{pack_id}-{page:02d}"
            product = product_dir / f"{item_id}.webp"
            reference = reference_dir / f"{item_id}.webp"
            save_product(source, pack["crop"], product)
            save_reference(source, reference)
            catalog.append({
                "id": item_id,
                "name": name,
                "category": pack["category"],
                "subcategory": pack["subcategory"],
                "productImage": product.relative_to(ROOT).as_posix(),
                "referenceImage": reference.relative_to(ROOT).as_posix(),
                "sourcePage": page,
                "sourcePack": pack["folder"],
                "search": slug(name).replace("-", " "),
            })

    process_dir = ASSETS / "products" / "procesos"
    ref_dir = ASSETS / "references" / "procesos"
    process_dir.mkdir(parents=True, exist_ok=True)
    ref_dir.mkdir(parents=True, exist_ok=True)

    cold_source = ROOT.parent / "upload" / "WhatsApp Image 2026-08-13 at 5.20.41 AM.jpeg"
    cold = Image.open(cold_source).convert("RGB")
    save_product(cold_source, (180, 190, 590, 675), process_dir / "cold-brew-toddy.webp")
    save_reference(cold_source, ref_dir / "cold-brew-toddy.webp")
    catalog.append({
        "id": "cold-brew-toddy", "name": "Cold Brew Toddy", "category": "Procesos",
        "subcategory": "Preparación base", "productImage": "assets/products/procesos/cold-brew-toddy.webp",
        "referenceImage": "assets/references/procesos/cold-brew-toddy.webp", "sourcePage": 1,
        "sourcePack": "Cold Brew Toddy", "search": "cold brew toddy",
    })

    food_folder = SOURCE / "Alimentos Croissant y Pan de queso"
    food_specs = [
        (1, "Pan de queso", (560, 250, 945, 535)),
        (3, "Croissant mantequilla", (555, 235, 955, 535)),
    ]
    for page, name, crop in food_specs:
        source = food_folder / f"Alimentos Croissant y Pan de queso_{page}.jpg"
        item_id = "pan-queso" if page == 1 else "croissant-mantequilla"
        save_product(source, crop, process_dir / f"{item_id}.webp")
        save_reference(source, ref_dir / f"{item_id}.webp")
        catalog.append({
            "id": item_id, "name": name, "category": "Alimentos", "subcategory": "Horneo",
            "productImage": f"assets/products/procesos/{item_id}.webp",
            "referenceImage": f"assets/references/procesos/{item_id}.webp",
            "sourcePage": page, "sourcePack": "Alimentos Croissant y Pan de queso",
            "search": slug(name).replace("-", " "),
        })

    shutil.copy2(SOURCE / "icon-192.png", ASSETS / "icon-192.png")
    shutil.copy2(SOURCE / "icon-512.png", ASSETS / "icon-512.png")
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Catálogo visual: {len(catalog)} artículos")


if __name__ == "__main__":
    main()
