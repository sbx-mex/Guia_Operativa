from __future__ import annotations

import argparse
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def optimize(input_path: Path, output_path: Path) -> None:
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
        writer.pages[-1].compress_content_streams()
    writer.add_metadata({"/Title": "Términos y condiciones · Concurso Unicornio Frappuccino"})
    writer.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as stream:
        writer.write(stream)


def main() -> None:
    parser = argparse.ArgumentParser(description="Optimiza un PDF para descarga web rápida.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    optimize(args.input, args.output)
    print(f"PDF optimizado: {args.output} ({args.output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
