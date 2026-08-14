from __future__ import annotations

import argparse
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
GREEN = colors.HexColor("#006241")
DEEP = colors.HexColor("#12372d")
PINK = colors.HexColor("#e64f9b")
PURPLE = colors.HexColor("#8e5aac")
MINT = colors.HexColor("#eef7f3")
GRAY = colors.HexColor("#eef1ef")
AMBER = colors.HexColor("#fff0c2")
SUCCESS = colors.HexColor("#dff3ea")
AMBER_TEXT = colors.HexColor("#855d00")


def non_negative(value: object) -> int:
    try:
        return max(0, round(float(value or 0)))
    except (TypeError, ValueError):
        return 0


def validate(data: dict) -> dict:
    if data.get("schemaVersion") not in {1, 2, 3}:
        raise ValueError("schemaVersion debe ser 1, 2 o 3")
    if not data.get("products") or not data.get("days"):
        raise ValueError("El JSON debe contener products y days")
    product_ids = [item.get("id") for item in data["products"]]
    if None in product_ids or len(product_ids) != len(set(product_ids)):
        raise ValueError("Los productos requieren IDs únicos")
    values = data.setdefault("values", {})
    for day in data["days"]:
        day_values = values.setdefault(day["id"], {})
        for product_id in product_ids:
            entry = day_values.setdefault(product_id, {})
            entry["goal"] = non_negative(entry.get("goal"))
            entry["actual"] = non_negative(entry.get("actual"))
    return data


def pct(actual: int, goal: int) -> int:
    return round(actual / goal * 100) if goal else 0


def progress_style(actual: int, goal: int) -> tuple[colors.Color, colors.Color, str]:
    reach = pct(actual, goal)
    if reach >= 100:
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


def create_pdf(data: dict, output: Path, title: str = "Objetivos y avance") -> None:
    data = validate(data)
    campaign = data.get("campaign", {})
    store = data.get("store", {})
    timezone = campaign.get("timezone", "America/Mexico_City")
    generated = datetime.now(ZoneInfo(timezone)).strftime("%d/%m/%Y a las %H:%M h")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleGreen", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=28, leading=30, textColor=GREEN, alignment=TA_CENTER, spaceAfter=3 * mm))
    styles.add(ParagraphStyle(name="Meta", parent=styles["BodyText"], fontSize=9, leading=12, textColor=DEEP, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="TableHead", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8, leading=9, textColor=colors.white, alignment=TA_CENTER))
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output), pagesize=landscape(letter), leftMargin=8 * mm, rightMargin=8 * mm, topMargin=7 * mm, bottomMargin=7 * mm, title=f"{title} · Unicorn")
    story = [Paragraph("IMPULSO UNICORN", styles["TitleGreen"]), Paragraph(f"{title} | 15, 16 y 17 de agosto", styles["Heading2"])]
    store_name = str(store.get("name") or "Tienda sin nombre")
    ceco = f" · CeCo {store['ceco']}" if store.get("ceco") else ""
    update = campaign.get("operationsUpdate", "14 de agosto de 2026")
    story += [Paragraph(f"<b>{store_name}</b>{ceco}<br/><font color='#63736e'>Voz de Operaciones | Actualización {update} | <b>Creado {generated}</b></font>", styles["Meta"]), Spacer(1, 2.5 * mm)]
    flow = Table([[
        Paragraph("<b>1. ANTICIPA</b><br/><font size='7'>Revisa objetivos antes del turno</font>", styles["Meta"]),
        Paragraph("<b>2. MIDE</b><br/><font size='7'>Captura el real al finalizar</font>", styles["Meta"]),
        Paragraph("<b>3. COMPARTE</b><br/><font size='7'>Envía el cierre a tu equipo</font>", styles["Meta"]),
    ]], colWidths=[82 * mm] * 3, style=TableStyle([
        ("BOX", (0, 0), (-1, -1), .8, colors.HexColor("#a8cdbf")),
        ("INNERGRID", (0, 0), (-1, -1), .5, colors.HexColor("#cbd9d3")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7fbf9")),
        ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
    ]))
    story += [flow, Spacer(1, 2.5 * mm)]

    summary = []
    card_width = 78 * mm
    for product in data["products"]:
        goal = sum(data["values"][day["id"]][product["id"]]["goal"] for day in data["days"])
        actual = sum(data["values"][day["id"]][product["id"]]["actual"] for day in data["days"])
        accent = colors.HexColor(product.get("accent", "#006241"))
        background, state_color, state_label = progress_style(actual, goal)
        summary.append(Table([[Paragraph(f"<b><font color='{accent.hexval()}'>{product['name']}</font></b><br/><font size='8'>{product.get('note','')}</font>", styles["BodyText"])], [Paragraph(f"OBJETIVO <b>{goal}</b> &nbsp;&nbsp; REAL <b>{actual}</b> &nbsp;&nbsp; ALCANCE <b>{pct(actual, goal)}%</b><br/><font color='{state_color.hexval()}' size='7'><b>{state_label}</b></font>", styles["Meta"])]], colWidths=[card_width], style=TableStyle([("BOX",(0,0),(-1,-1),1,accent),("BACKGROUND",(0,1),(-1,-1),background),("PADDING",(0,0),(-1,-1),2.1 * mm)])))
    story += [Table([summary], colWidths=[82 * mm] * len(summary), style=TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),2 * mm),("RIGHTPADDING",(0,0),(-1,-1),2 * mm)])), Spacer(1, 2.5 * mm)]

    header_top = [Paragraph("Indicador", styles["TableHead"])] + [Paragraph(day["label"], styles["TableHead"]) for day in data["days"] for _ in range(3)] + [Paragraph("Acumulado", styles["TableHead"]) for _ in range(3)]
    header_bottom = [""] + [label for _ in data["days"] for label in ("Objetivo", "Real", "Avance")] + ["Objetivo", "Real", "Avance"]
    rows = [header_top, header_bottom]
    progress_cells = []
    for row_index, product in enumerate(data["products"], start=2):
        row = [Paragraph(f"<b>{product['name']}</b><br/><font size='7'>{product.get('note','')}</font>", styles["BodyText"])]
        goals, actuals = [], []
        for day in data["days"]:
            entry = data["values"][day["id"]][product["id"]]
            goals.append(entry["goal"]); actuals.append(entry["actual"])
            row += [entry["goal"], entry["actual"], f"{pct(entry['actual'], entry['goal'])}%"]
            column = 3 + (len(goals) - 1) * 3
            background, state_color, _ = progress_style(entry["actual"], entry["goal"])
            progress_cells += [("BACKGROUND", (column, row_index), (column, row_index), background), ("TEXTCOLOR", (column, row_index), (column, row_index), state_color)]
        row += [sum(goals), sum(actuals), f"{pct(sum(actuals), sum(goals))}%"]
        background, state_color, _ = progress_style(sum(actuals), sum(goals))
        progress_cells += [("BACKGROUND", (12, row_index), (12, row_index), background), ("TEXTCOLOR", (12, row_index), (12, row_index), state_color)]
        rows.append(row)
    widths = [38 * mm] + [16.7 * mm] * (3 * (len(data["days"]) + 1))
    table = Table(rows, colWidths=widths, repeatRows=2)
    spans = []
    for index in range(len(data["days"]) + 1):
        start = 1 + index * 3
        spans.append(("SPAN", (start, 0), (start + 2, 0)))
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,1),GREEN),("TEXTCOLOR",(0,0),(-1,1),colors.white),("GRID",(0,0),(-1,-1),.45,colors.HexColor("#aebdb7")),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ALIGN",(1,0),(-1,-1),"CENTER"),("FONTSIZE",(0,0),(-1,-1),7),("TOPPADDING",(0,0),(-1,-1),2.5 * mm),("BOTTOMPADDING",(0,0),(-1,-1),2.5 * mm),("ROWBACKGROUNDS",(0,2),(-1,-1),[colors.white,colors.HexColor("#f7f3ea")]),*spans,*progress_cells]))
    story += [KeepTogether(table), Spacer(1, 2 * mm), Paragraph("Alcance = real / objetivo | Verde: logrado | Amarillo: en avance | Gris: pendiente", styles["Meta"])]
    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#d5e1dc"))
        canvas.line(document.leftMargin, 6 * mm, landscape(letter)[0] - document.rightMargin, 6 * mm)
        canvas.setFillColor(DEEP)
        canvas.setFont("Helvetica", 7.5)
        canvas.drawString(document.leftMargin, 3 * mm, "Diseñado: Jorge Alcantar Aguiar & Enrique César Flores")
        canvas.drawRightString(landscape(letter)[0] - document.rightMargin, 3 * mm, "JUNTÉMONOS MÁS | PREPARÉMONOS MÁS")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def main() -> None:
    parser = argparse.ArgumentParser(description="Exporta un tablero de objetivos JSON a PDF.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path, nargs="?", help="Ruta de salida opcional; si se omite, el nombre se genera a partir de la tienda.")
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    output = args.output or dynamic_output(data, args.input.parent)
    output.parent.mkdir(parents=True, exist_ok=True)
    create_pdf(data, output)
    print(f"PDF generado: {output}")


if __name__ == "__main__":
    main()
