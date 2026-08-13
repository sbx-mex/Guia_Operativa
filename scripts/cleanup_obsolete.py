from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OBSOLETE = (
    "data/recipes.js",
    "data/catalog.json",
    "data/catalog_audit.json",
    "scripts/build_recipes.py",
    "scripts/catalog_import.py",
    "scripts/process_media.py",
    "outputs/CMS_Recetarios_Manuales_Frappuccino.xlsx",
    "assets/references/frias/frias-06.tmp.webp",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Detecta o elimina únicamente archivos heredados autorizados.")
    parser.add_argument("--apply", action="store_true", help="Elimina la lista cerrada de archivos obsoletos.")
    args = parser.parse_args()
    found = [relative for relative in OBSOLETE if (ROOT / relative).is_file()]
    if args.apply:
        for relative in found:
            (ROOT / relative).unlink()
            print(f"Eliminado: {relative}")
        print(f"Limpieza terminada: {len(found)} archivo(s)")
        return
    if found:
        raise SystemExit("Archivos obsoletos detectados:\n" + "\n".join(found))
    print("Repositorio limpio: 0 archivos obsoletos")


if __name__ == "__main__":
    main()
