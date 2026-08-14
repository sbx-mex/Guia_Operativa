from __future__ import annotations

import argparse
import json
import re
import unicodedata
from datetime import datetime
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image as RLImage
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
GREEN = colors.HexColor("#006241")
DEEP = colors.HexColor("#12372d")
GRAY = colors.HexColor("#eef1ef")
AMBER = colors.HexColor("#fff0c2")
SUCCESS = colors.HexColor("#dff3ea")
AMBER_TEXT = colors.HexColor("#855d00")
DEFAULT_CUTS = (
    {"id": "am", "label": "Apertura", "time": "Apertura - 12:00"},
    {"id": "inter", "label": "Intermedio", "time": "12:00 - 17:00"},
    {"id": "pm", "label": "Cierre", "time": "17:00 - cierre"},
)


def non_negative(value: object) -> int:
    try:
        return max(0, round(float(value or 0)))
    except (TypeError, ValueError):
        return 0


def validate(data: dict) -> dict:
    if data.get("schemaVersion") not in {1, 2, 3, 4}:
        raise ValueError("schemaVersion debe estar entre 1 y 4")
    if not data.get("products") or not data.get("days"):
        raise ValueError("El JSON debe contener products y days")
    product_ids = [item.get("id") for item in data["products"]]
    if None in product_ids or len(product_ids) != len(set(product_ids)):
        raise ValueError("Los productos requieren IDs únicos")
    cuts = data.setdefault("cuts", [dict(cut) for cut in DEFAULT_CUTS])
    cut_ids = [cut.get("id") for cut in cuts]
    if not cut_ids or None in cut_ids or len(cut_ids) != len(set(cut_ids)):
        raise ValueError("Los turnos requieren IDs únicos")
    values = data.setdefault("values", {})
    for day in data["days"]:
        day_values = values.setdefault(day["id"], {})
        for product_id in product_ids:
            entry = day_values.setdefault(product_id, {})
            entry["goal"] = non_negative(entry.get("goal"))
            raw_actuals = entry.get("actuals")
            if not isinstance(raw_actuals, dict):
                raw_actuals = {cut_ids[-1]: non_negative(entry.get("actual"))}
            entry["actuals"] = {cut_id: non_negative(raw_actuals.get(cut_id)) for cut_id in cut_ids}
            entry["actual"] = sum(entry["actuals"].values())
    return data


def pct(actual: int, goal: int) -> int:
    return round(actual / goal * 100) if goal else 0


def progress_style(actual: int, goal: int) -> tuple[colors.Color, colors.Color, str]:
    if goal and actual >= goal:
        return SUCCESS, GREEN, "LOGRADO"
    if actual > 0:
        return AMBER, AMBER_TEXT, "EN AVANCE"
    return GRAY, colors.HexColor("#63736e"), "PENDIENTE"


def safe_filename(value: str) -> str:
    plain = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", plain).strip("_") or "Tienda"


def dynamic_output(data: dict, directory: Path) -> Path:
    store = safe_filename(str(data.get("store", {}).get("name") or "Tienda"))
    return directory / f"{store}_Unicorn_Frapp_Cake_Pop.pdf"


@lru_cache(maxsize=8)
def optimized_thumbnail(path_text: str) -> bytes:
    with Image.open(path_text) as source:
        source.thumbnail((180, 180), Image.Resampling.LANCZOS)
        background = Image.new("RGB", source.size, "white")
        if source.mode in {"RGBA", "LA"}:
            background.paste(source, mask=source.getchannel("A"))
        else:
            background.paste(source.convert("RGB"))
        buffer = BytesIO()
        background.save(buffer, format="JPEG", quality=82, optimize=True)
        return buffer.getvalue()


def visual(product: dict, width: float = 18 * mm, height: float = 20 * mm):
    path = ROOT / str(product.get("image", ""))
    if path.is_file():
        return RLImage(BytesIO(optimized_thumbnail(str(path))), width=width, height=height, kind="proportional")
    return Paragraph(f"<b>{product['name']}</b>", getSampleStyleSheet()["BodyText"])


def create_pdf(data: dict, output: Path, title: str = "Objetivos y proyección") -> None:
    data = validate(data)
    campaign = data.get("campaign", {})
    store = data.get("store", {})
    generated = datetime.now(ZoneInfo(campaign.get("timezone", "America/Mexico_City"))).strftime("%d/%m/%Y a las %H:%M h")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleGreen", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=24, leading=25, textColor=GREEN, alignment=TA_CENTER, spaceAfter=1 * mm))
    styles.add(ParagraphStyle(name="Meta", parent=styles["BodyText"], fontSize=8, leading=10, textColor=DEEP, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="Head", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8, leading=9, textColor=colors.white, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="Cell", parent=styles["BodyText"], fontSize=7.5, leading=9, textColor=DEEP, alignment=TA_CENTER))
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output), pagesize=landscape(letter), leftMargin=6 * mm, rightMargin=6 * mm, topMargin=5 * mm, bottomMargin=5 * mm, title=f"{title} · Unicorn")
    store_name = str(store.get("name") or "Tienda sin nombre")
    ceco = f" · CeCo {store['ceco']}" if store.get("ceco") else ""
    update = campaign.get("operationsUpdate", "14 de agosto de 2026")
    story = [Paragraph("IMPULSO UNICORN", styles["TitleGreen"]), Paragraph(f"<b>{title}</b> | 15, 16 y 17 de agosto", styles["Meta"]), Paragraph(f"<b>{store_name}</b>{ceco} &nbsp; | &nbsp; Actualización {update} &nbsp; | &nbsp; <b>Creado {generated}</b>", styles["Meta"]), Spacer(1, 1.4 * mm)]
    guide = Table([[
        Paragraph("<b>1. CONOCE</b><br/><font size='7'>La meta permanece por día</font>", styles["Meta"]),
        Paragraph("<b>2. PROYECTA</b><br/><font size='7'>Un renglón opcional por turno</font>", styles["Meta"]),
        Paragraph("<b>3. MIDE</b><br/><font size='7'>El alcance se calcula automáticamente</font>", styles["Meta"]),
    ]], colWidths=[88 * mm] * 3, style=TableStyle([("BOX", (0, 0), (-1, -1), .8, colors.HexColor("#a8cdbf")), ("INNERGRID", (0, 0), (-1, -1), .5, colors.HexColor("#cbd9d3")), ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7fbf9")), ("TOPPADDING", (0, 0), (-1, -1), 1.3 * mm), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.3 * mm)]))
    story += [guide, Spacer(1, 1.4 * mm)]

    cards = []
    for product in data["products"]:
        goal = sum(data["values"][day["id"]][product["id"]]["goal"] for day in data["days"])
        actual = sum(data["values"][day["id"]][product["id"]]["actual"] for day in data["days"])
        accent = colors.HexColor(product.get("accent", "#006241"))
        background, state_color, state_label = progress_style(actual, goal)
        copy = Table([[Paragraph(f"<b><font color='{accent.hexval()}'>{product['name']}</font></b><br/><font size='7'>{product.get('note','')}</font>", styles["BodyText"])], [Paragraph(f"META <b>{goal}</b> &nbsp; REAL <b>{actual}</b> &nbsp; ALCANCE <b>{pct(actual, goal)}%</b><br/><font color='{state_color.hexval()}' size='7'><b>{state_label}</b></font>", styles["Meta"])]], colWidths=[60 * mm], style=TableStyle([("BACKGROUND", (0, 1), (-1, -1), background), ("PADDING", (0, 0), (-1, -1), 1.2 * mm)]))
        cards.append(Table([[visual(product), copy]], colWidths=[20 * mm, 62 * mm], style=TableStyle([("BOX", (0, 0), (-1, -1), 1, accent), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("PADDING", (0, 0), (0, -1), 1.2 * mm), ("PADDING", (1, 0), (1, -1), 1 * mm)])))
    story += [Table([cards], colWidths=[88 * mm] * 3, style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 1 * mm), ("RIGHTPADDING", (0, 0), (-1, -1), 1 * mm)])), Spacer(1, 1.4 * mm)]

    daily_rows = [[Paragraph("RESULTADO DIARIO · META / REAL / ALCANCE", styles["Head"]), "", "", ""], [Paragraph("Día", styles["Head"]), *[Paragraph(product["name"], styles["Head"]) for product in data["products"]]]]
    daily_styles = [("SPAN", (0, 0), (-1, 0))]
    for row_index, day in enumerate(data["days"], start=2):
        row = [Paragraph(day["label"], styles["Cell"])]
        for column, product in enumerate(data["products"], start=1):
            entry = data["values"][day["id"]][product["id"]]
            background, state_color, _ = progress_style(entry["actual"], entry["goal"])
            row.append(Paragraph(f"Meta <b>{entry['goal']}</b> &nbsp; Real <b>{entry['actual']}</b> &nbsp; <font color='{state_color.hexval()}'><b>{pct(entry['actual'], entry['goal'])}%</b></font>", styles["Cell"]))
            daily_styles.append(("BACKGROUND", (column, row_index), (column, row_index), background))
        daily_rows.append(row)
    daily = Table(daily_rows, colWidths=[42 * mm, 74 * mm, 74 * mm, 74 * mm])
    daily.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 1), GREEN), ("TEXTCOLOR", (0, 0), (-1, 1), colors.white), ("GRID", (0, 0), (-1, -1), .45, colors.HexColor("#aebdb7")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ROWBACKGROUNDS", (0, 2), (-1, -1), [colors.white, colors.HexColor("#f8f5ef")]), ("TOPPADDING", (0, 0), (-1, -1), 2 * mm), ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm), *daily_styles]))
    story += [KeepTogether(daily), Spacer(1, 1.4 * mm)]

    projection_rows = [[Paragraph("PROYECCIÓN POR TURNO · LLENADO OPCIONAL", styles["Head"]), "", "", "", ""], [Paragraph("Día", styles["Head"]), Paragraph("Turno", styles["Head"]), *[Paragraph(f"Real {product['name']}", styles["Head"]) for product in data["products"]]]]
    projection_styles = [("SPAN", (0, 0), (-1, 0))]
    row_index = 2
    for day in data["days"]:
        day_start = row_index
        for cut in data["cuts"]:
            projection_rows.append([Paragraph(day["label"], styles["Cell"]), Paragraph(f"<b>{cut['label']}</b><br/><font size='6'>{cut.get('time','')}</font>", styles["Cell"]), *[(data["values"][day["id"]][product["id"]]["actuals"][cut["id"]] or "") for product in data["products"]]])
            row_index += 1
        projection_styles.append(("SPAN", (0, day_start), (0, row_index - 1)))
    projection = Table(projection_rows, colWidths=[42 * mm, 58 * mm, 54.7 * mm, 54.7 * mm, 54.6 * mm])
    projection.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 1), GREEN), ("TEXTCOLOR", (0, 0), (-1, 1), colors.white), ("GRID", (0, 0), (-1, -1), .45, colors.HexColor("#aebdb7")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (2, 2), (-1, -1), "CENTER"), ("FONTSIZE", (0, 0), (-1, -1), 7.5), ("ROWBACKGROUNDS", (0, 2), (-1, -1), [colors.white, colors.HexColor("#f8f5ef")]), ("TOPPADDING", (0, 0), (-1, -1), 1.7 * mm), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.7 * mm), *projection_styles]))
    story += [KeepTogether(projection)]

    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#d5e1dc"))
        canvas.line(document.leftMargin, 4.5 * mm, landscape(letter)[0] - document.rightMargin, 4.5 * mm)
        canvas.setFillColor(DEEP)
        canvas.setFont("Helvetica", 7.5)
        canvas.drawString(document.leftMargin, 1.8 * mm, "Proyecta por turno, mide el alcance y comparte el cierre")
        canvas.drawRightString(landscape(letter)[0] - document.rightMargin, 1.8 * mm, "JUNTÉMONOS MÁS | PREPARÉMONOS MÁS")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def main() -> None:
    parser = argparse.ArgumentParser(description="Exporta objetivos y proyección por turno desde JSON a PDF.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path, nargs="?", help="Ruta de salida opcional")
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    output = args.output or dynamic_output(data, args.input.parent)
    create_pdf(data, output)
    print(f"PDF generado: {output}")


if __name__ == "__main__":
    main()
