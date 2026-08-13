from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


CONTENTS = [
    {
        "id": "frap-cafe", "name": "Café Frappuccino", "category": "Bebidas",
        "subcategory": "Frappuccino", "description": "Café, leche y hielo mezclados.",
        "productImage": "assets/products/frappuccino/frappuccino-04.webp",
        "referenceImage": "assets/references/frappuccino/frappuccino-04.webp",
        "selectors": [
            {"id": "size", "label": "Tamaño", "options": ["ALTO", "GRANDE", "VENTI"]},
        ],
        "routes": {"size=ALTO": "frap-cafe", "size=GRANDE": "frap-cafe", "size=VENTI": "frap-cafe"},
        "equipment": ["Vaso", "Licuadora", "Medida de hielo"],
        "rules": ["Usa la medida volumétrica correspondiente al tamaño."],
    },
    {
        "id": "frap-cajeta", "name": "Cajeta Frappuccino", "category": "Bebidas",
        "subcategory": "Frappuccino", "description": "Cajeta, leche y hielo; versión Café o Cream.",
        "productImage": "assets/products/frappuccino/frappuccino-05.webp",
        "referenceImage": "assets/references/frappuccino/frappuccino-05.webp",
        "selectors": [
            {"id": "size", "label": "Tamaño", "options": ["ALTO", "GRANDE", "VENTI"]},
            {"id": "version", "label": "Versión", "options": ["CAFE", "CREAM"]},
        ],
        "routes": {
            "size=ALTO|version=CAFE": "frap-cajeta-cafe", "size=GRANDE|version=CAFE": "frap-cajeta-cafe",
            "size=VENTI|version=CAFE": "frap-cajeta-cafe", "size=ALTO|version=CREAM": "frap-cajeta-cream",
            "size=GRANDE|version=CREAM": "frap-cajeta-cream", "size=VENTI|version=CREAM": "frap-cajeta-cream",
        },
        "equipment": ["Vaso", "Licuadora", "Dosificador metal espresso"],
        "rules": ["La versión Cream omite Frappuccino Roast y comienza con leche."],
    },
    {
        "id": "cold-brew-toddy", "name": "Cold Brew Toddy", "category": "Procesos",
        "subcategory": "Preparación base", "description": "Preparación y almacenamiento del concentrado Cold Brew.",
        "productImage": "assets/products/procesos/cold-brew-toddy.webp",
        "referenceImage": "assets/references/procesos/cold-brew-toddy.webp",
        "selectors": [{"id": "batch", "label": "Tanda", "options": ["COMPLETA", "MEDIA"]}],
        "routes": {"batch=COMPLETA": "toddy-completa", "batch=MEDIA": "toddy-media"},
        "equipment": ["Cafetera Toddy", "Filtros", "Hilo", "Jarras de 2 L o cubos plásticos"],
        "rules": [
            "Usa exclusivamente mezcla Cold Brew de Starbucks.",
            "Para una solicitud descafeinada, ofrece Americano helado descafeinado.",
        ],
    },
    {
        "id": "pan-queso", "name": "Pan de queso", "category": "Alimentos",
        "subcategory": "Horneo", "description": "Horneo, reposo, recalentamiento y entrega.",
        "productImage": "assets/products/procesos/pan-queso.webp",
        "referenceImage": "assets/references/procesos/pan-queso.webp",
        "selectors": [], "routes": {"default": "pan-queso"},
        "equipment": ["Charola", "Tapete siliconado", "Horno", "Merrychef/Turbochef"],
        "rules": ["Mantén el producto congelado a -18 °C hasta su preparación."],
    },
    {
        "id": "croissant", "name": "Croissant mantequilla", "category": "Alimentos",
        "subcategory": "Horneo", "description": "Descongelado, horneo, reposo y uso.",
        "productImage": "assets/products/procesos/croissant-mantequilla.webp",
        "referenceImage": "assets/references/procesos/croissant-mantequilla.webp",
        "selectors": [], "routes": {"default": "croissant"},
        "equipment": ["Charola", "Tapete siliconado", "Horno", "Merrychef/Turbochef"],
        "rules": ["Mantén el producto congelado a -18 °C hasta su preparación."],
    },
]


SIZE = {
    "ALTO": "Alto", "GRANDE": "Grande", "VENTI": "Venti",
    "CAFE": "Café", "CREAM": "Cream", "COMPLETA": "Tanda completa", "MEDIA": "Media tanda",
}


def step(route, order, title, detail, icon, values="", timer=0, stage=""):
    return {"route": route, "order": order, "title": title, "detail": detail, "icon": icon,
            "values": values, "timer": timer, "stage": stage or title}


STEPS = [
    step("frap-cafe", 1, "Agrega Frappuccino Roast", "Usa el dosificador metal.", "coffee", "ALTO=2|GRANDE=3|VENTI=4", stage="Base de café"),
    step("frap-cafe", 2, "Vierte la leche", "Hasta la línea inferior del vaso.", "milk", "TODOS=Línea inferior", stage="Leche"),
    step("frap-cafe", 3, "Pasa a la licuadora", "Vierte todo el contenido del vaso.", "pour", "TODOS=Contenido completo", stage="Integrar"),
    step("frap-cafe", 4, "Agrega hielo", "Usa la medida volumétrica apropiada.", "ice", "ALTO=Alto|GRANDE=Grande|VENTI=Venti", stage="Hielo"),
    step("frap-cafe", 5, "Agrega base Coffee", "Añade base Coffee para Frappuccino.", "bottle", "ALTO=2|GRANDE=3|VENTI=4", stage="Base"),
    step("frap-cafe", 6, "Mezcla", "Presiona el botón número 1.", "blend", "TODOS=Botón 1", stage="Mezclar"),
    step("frap-cafe", 7, "Termina", "Vierte 6 mm debajo del borde. Coloca tapa plana y popote.", "check", "TODOS=6 mm", stage="Listo"),

    step("frap-cajeta-cafe", 1, "Agrega Frappuccino Roast", "Usa el dosificador metal.", "coffee", "ALTO=2|GRANDE=3|VENTI=4", stage="Base de café"),
    step("frap-cajeta-cafe", 2, "Vierte la leche", "Hasta la línea inferior del vaso.", "milk", "TODOS=Línea inferior", stage="Leche"),
    step("frap-cajeta-cafe", 3, "Pasa a la licuadora", "Vierte el contenido del vaso.", "pour", "TODOS=Contenido completo", stage="Integrar"),
    step("frap-cajeta-cafe", 4, "Agrega salsa de cajeta", "Dosificador metal espresso.", "sauce", "ALTO=1|GRANDE=2|VENTI=2", stage="Cajeta"),
    step("frap-cajeta-cafe", 5, "Agrega hielo", "Usa la medida correspondiente.", "ice", "ALTO=Alto|GRANDE=Grande|VENTI=Venti", stage="Hielo"),
    step("frap-cajeta-cafe", 6, "Agrega base Coffee", "Base Coffee para Frappuccino.", "bottle", "ALTO=2|GRANDE=3|VENTI=4", stage="Base"),
    step("frap-cajeta-cafe", 7, "Mezcla", "Presiona el botón número 1.", "blend", "TODOS=Botón 1", stage="Mezclar"),
    step("frap-cajeta-cafe", 8, "Termina", "Crema batida, 5 vueltas de caramelo, tapa domo y popote.", "check", "TODOS=1 cm bajo el borde", stage="Listo"),

    step("frap-cajeta-cream", 1, "Vierte la leche", "La versión Cream comienza aquí; omite el Roast.", "milk", "TODOS=Línea inferior", stage="Leche"),
    step("frap-cajeta-cream", 2, "Pasa a la licuadora", "Vierte el contenido del vaso.", "pour", "TODOS=Contenido completo", stage="Integrar"),
    step("frap-cajeta-cream", 3, "Agrega salsa de cajeta", "Dosificador metal espresso.", "sauce", "ALTO=1|GRANDE=2|VENTI=2", stage="Cajeta"),
    step("frap-cajeta-cream", 4, "Agrega hielo", "Usa la medida correspondiente.", "ice", "ALTO=Alto|GRANDE=Grande|VENTI=Venti", stage="Hielo"),
    step("frap-cajeta-cream", 5, "Agrega base Cream", "Base Cream para Frappuccino.", "bottle", "ALTO=2|GRANDE=3|VENTI=4", stage="Base"),
    step("frap-cajeta-cream", 6, "Mezcla", "Presiona el botón número 1.", "blend", "TODOS=Botón 1", stage="Mezclar"),
    step("frap-cajeta-cream", 7, "Termina", "Crema batida, 5 vueltas de caramelo, tapa domo y popote.", "check", "TODOS=1 cm bajo el borde", stage="Listo"),

    step("toddy-completa", 1, "Muele la mezcla", "Ditting #9, Grindmaster 890 #15 o Grindmaster 875 grueso.", "grind", "TODOS=5 lb", stage="Café molido"),
    step("toddy-completa", 2, "Coloca el filtro", "Dobla 2 pulgadas y colócalo en la cafetera Toddy en seco.", "filter", "TODOS=Filtro seco", stage="Filtro"),
    step("toddy-completa", 3, "Agrega café y agua", "Vierte agua fría filtrada y moja todo el café molido.", "water", "TODOS=5 lb + 7 L", stage="Primera agua"),
    step("toddy-completa", 4, "Cierra y satura", "Ata el filtro dejando 3 a 4 pulgadas arriba y agrega agua adicional.", "tie", "TODOS=7 L adicionales", stage="Saturar"),
    step("toddy-completa", 5, "Deja preparar", "Cubre, etiqueta la hora de finalización y deja sin refrigerar.", "timer", "TODOS=20 horas", timer=72000, stage="Extracción"),
    step("toddy-completa", 6, "Transfiere y refrigera", "Pasa el concentrado a jarras de 2 L o cubo plástico. Etiqueta.", "store", "TODOS=5 días", stage="Listo"),

    step("toddy-media", 1, "Muele la mezcla", "Ditting #9, Grindmaster 890 #15 o Grindmaster 875 grueso.", "grind", "TODOS=3 lb", stage="Café molido"),
    step("toddy-media", 2, "Coloca el filtro", "Dobla 2 pulgadas y colócalo en la cafetera Toddy en seco.", "filter", "TODOS=Filtro seco", stage="Filtro"),
    step("toddy-media", 3, "Agrega café y agua", "Vierte agua fría filtrada y moja todo el café molido.", "water", "TODOS=3 lb + 4.5 L", stage="Primera agua"),
    step("toddy-media", 4, "Cierra y satura", "Ata el filtro dejando 3 a 4 pulgadas arriba y agrega agua adicional.", "tie", "TODOS=4.5 L adicionales", stage="Saturar"),
    step("toddy-media", 5, "Deja preparar", "Cubre, etiqueta la hora de finalización y deja sin refrigerar.", "timer", "TODOS=20 horas", timer=72000, stage="Extracción"),
    step("toddy-media", 6, "Transfiere y refrigera", "Pasa el concentrado a jarras de 2 L o cubo plástico. Etiqueta.", "store", "TODOS=5 días", stage="Listo"),

    step("pan-queso", 1, "Almacena", "Mantén congelado a -18 °C.", "freeze", "TODOS=-18 °C", stage="Congelado"),
    step("pan-queso", 2, "Prepara", "Descongela sólo las piezas necesarias y usa tapete siliconado.", "tray", "TODOS=Según venta", stage="Preparar"),
    step("pan-queso", 3, "Acomoda", "Coloca máximo 6 piezas con 2 cm de separación. Sin descongelar.", "layout", "TODOS=Máx. 6", stage="Charola"),
    step("pan-queso", 4, "Hornea y reposa", "Hornea a 325 °F y deja reposar.", "oven", "TODOS=18 min + 20–25 min", timer=1080, stage="Horneo"),
    step("pan-queso", 5, "Recalienta", "Programa Pan de queso (2 o 4 piezas).", "heat", "TODOS=20 min de vida", stage="Uso"),
    step("pan-queso", 6, "Entrega", "Sirve en plato o bolsa pastry panini según canal.", "serve", "TODOS=Listo", stage="Entrega"),

    step("croissant", 1, "Almacena", "Mantén congelado a -18 °C.", "freeze", "TODOS=-18 °C", stage="Congelado"),
    step("croissant", 2, "Prepara", "Descongela únicamente las piezas necesarias sobre tapete siliconado.", "tray", "TODOS=Según venta", stage="Preparar"),
    step("croissant", 3, "Acomoda", "Coloca máximo 5 piezas, separadas. Descongela de 1 h a 1 h 20 min.", "layout", "TODOS=Máx. 5", stage="Charola"),
    step("croissant", 4, "Hornea y reposa", "Hornea a 325 °F y deja reposar.", "oven", "TODOS=18 min + 20–25 min", timer=1080, stage="Horneo"),
    step("croissant", 5, "Calienta o ensambla", "Usa Merrychef/Turbochef o ensambla Croissant Pechuga Queso.", "heat", "TODOS=Según uso", stage="Uso"),
]


def main():
    catalog = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
    output = {"meta": {"version": "2.0.0", "catalogItems": len(catalog), "trainingModules": len(CONTENTS)},
              "labels": SIZE, "catalog": catalog, "contents": CONTENTS, "steps": STEPS}
    (ROOT / "data" / "content.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "data" / "content.js").write_text("window.TRAINING_CMS = " + json.dumps(output, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(f"Motor generado: {len(CONTENTS)} módulos, {len(STEPS)} pasos, {len(catalog)} referencias")


if __name__ == "__main__":
    main()
