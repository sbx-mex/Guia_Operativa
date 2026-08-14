from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
GREEN = colors.HexColor("#006241")
DEEP = colors.HexColor("#12372d")
PINK = colors.HexColor("#e64f9b")
PURPLE = colors.HexColor("#8e5aac")
MINT = colors.HexColor("#eef7f3")


def non_negative(value: object) -> int:
    try:
        return max(0, round(float(value or 0)))
    except (TypeError, ValueError):
        return 0


def validate(data: dict) -> dict:
    if data.get("schemaVersion") != 1:
        raise ValueError("schemaVersion debe ser 1")
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


def create_pdf(data: dict, output: Path) -> None:
    data = validate(data)
    campaign = data.get("campaign", {})
    store = data.get("store", {})
    timezone = campaign.get("timezone", "America/Mexico_City")
    generated = datetime.now(ZoneInfo(timezone)).strftime("%d/%m/%Y · %H:%M")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleGreen", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=28, leading=30, textColor=GREEN, alignment=TA_CENTER, spaceAfter=3 * mm))
    styles.add(ParagraphStyle(name="Meta", parent=styles["BodyText"], fontSize=9, leading=12, textColor=DEEP, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="TableHead", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8, leading=9, textColor=colors.white, alignment=TA_CENTER))
    doc = SimpleDocTemplate(str(output), pagesize=landscape(letter), leftMargin=8 * mm, rightMargin=8 * mm, topMargin=7 * mm, bottomMargin=7 * mm, title="Dash de ventas · Logro de objetivos")
    story = [Paragraph("META UNICORN", styles["TitleGreen"]), Paragraph("Objetivos y avance · 15, 16 y 17 de agosto", styles["Heading2"])]
    store_name = str(store.get("name") or "Tienda sin nombre")
    ceco = f" · CeCo {store['ceco']}" if store.get("ceco") else ""
    update = campaign.get("operationsUpdate", "14 de agosto de 2026")
    story += [Paragraph(f"<b>{store_name}</b>{ceco}<br/><font color='#63736e'>Voz de Operaciones · {update} &nbsp; | &nbsp; Exportado {generated}</font>", styles["Meta"]), Spacer(1, 4 * mm)]

    summary = []
    for index, product in enumerate(data["products"]):
        goal = sum(data["values"][day["id"]][product["id"]]["goal"] for day in data["days"])
        actual = sum(data["values"][day["id"]][product["id"]]["actual"] for day in data["days"])
        accent = PINK if index == 0 else PURPLE
        summary.append(Table([[Paragraph(f"<b><font color='{accent.hexval()}'>{product['name']}</font></b><br/><font size='8'>{product.get('note','')}</font>", styles["BodyText"])], [Paragraph(f"META <b>{goal}</b> &nbsp;&nbsp; REAL <b>{actual}</b> &nbsp;&nbsp; AVANCE <b>{pct(actual, goal)}%</b>", styles["Meta"])]], colWidths=[114 * mm], style=TableStyle([("BOX",(0,0),(-1,-1),1,accent),("BACKGROUND",(0,1),(-1,-1),MINT),("PADDING",(0,0),(-1,-1),3 * mm)])))
    story += [Table([summary], colWidths=[119 * mm] * len(summary), style=TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),2 * mm),("RIGHTPADDING",(0,0),(-1,-1),2 * mm)])), Spacer(1, 4 * mm)]

    header_top = [Paragraph("Producto", styles["TableHead"])] + [Paragraph(day["label"], styles["TableHead"]) for day in data["days"] for _ in range(3)] + [Paragraph("Total campaña", styles["TableHead"]) for _ in range(3)]
    header_bottom = [""] + [label for _ in data["days"] for label in ("Objetivo", "Real", "Avance")] + ["Objetivo", "Real", "Avance"]
    rows = [header_top, header_bottom]
    for product in data["products"]:
        row = [Paragraph(f"<b>{product['name']}</b><br/><font size='7'>{product.get('note','')}</font>", styles["BodyText"])]
        goals, actuals = [], []
        for day in data["days"]:
            entry = data["values"][day["id"]][product["id"]]
            goals.append(entry["goal"]); actuals.append(entry["actual"])
            row += [entry["goal"], entry["actual"], f"{pct(entry['actual'], entry['goal'])}%"]
        row += [sum(goals), sum(actuals), f"{pct(sum(actuals), sum(goals))}%"]
        rows.append(row)
    widths = [38 * mm] + [16.7 * mm] * (3 * (len(data["days"]) + 1))
    table = Table(rows, colWidths=widths, repeatRows=2)
    spans = []
    for index in range(len(data["days"]) + 1):
        start = 1 + index * 3
        spans.append(("SPAN", (start, 0), (start + 2, 0)))
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,1),GREEN),("TEXTCOLOR",(0,0),(-1,1),colors.white),("GRID",(0,0),(-1,-1),.45,colors.HexColor("#aebdb7")),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ALIGN",(1,0),(-1,-1),"CENTER"),("FONTSIZE",(0,0),(-1,-1),7),("TOPPADDING",(0,0),(-1,-1),3 * mm),("BOTTOMPADDING",(0,0),(-1,-1),3 * mm),("ROWBACKGROUNDS",(0,2),(-1,-1),[colors.white,colors.HexColor("#f7f3ea")]),*spans]))
    story += [KeepTogether(table), Spacer(1, 4 * mm), Paragraph("Anticipar · practicar · medir · lograr", styles["Meta"])]
    doc.build(story)


def main() -> None:
    parser = argparse.ArgumentParser(description="Exporta un tablero de objetivos JSON a PDF.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_pdf(json.loads(args.input.read_text(encoding="utf-8")), args.output)
    print(f"PDF generado: {args.output}")


if __name__ == "__main__":
    main()
