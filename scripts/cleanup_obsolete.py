from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OBSOLETE = (
    "ARCHIVOS_A_REEMPLAZAR.txt",
    "ELIMINAR_OBSOLETOS.txt",
    "INSTRUCCIONES.txt",
    "INSTRUCCIONES_DE_CARGA.txt",
    "VALIDACION_PYTHON.txt",
    "CMS_Guia_Operativa_v2.xlsx",
    "audit_project.py",
    "content.js",
    "bagel-jamon-queso (4).webp",
    "bagel-jamon-queso.webp",
    "baguette-clasica (2).webp",
    "baguette-espanola (1).webp",
    "chai-latte-helado-pumpkin-cold-foam (8).webp",
    "cold-brew-pumpkin-cold-foam (7).webp",
    "cold-brew-pumpkin-cold-foam.webp",
    "cold-foam-pumpkin (9).webp",
    "cold-foam-pumpkin.webp",
    "croissant-jamon-queso (3).webp",
    "pumpkin-spice-frappuccino (10).webp",
    "pumpkin-spice-frappuccino.webp",
    "pumpkin-spice-latte-helado.webp",
    "pumpkin-spice-latte.webp",
    "data/recipes.js",
    "data/catalog.json",
    "data/catalog_audit.json",
    "scripts/build_recipes.py",
    "scripts/catalog_import.py",
    "scripts/process_media.py",
    "outputs/CMS_Recetarios_Manuales_Frappuccino.xlsx",
    "assets/references/frias/frias-06.tmp.webp",
    "assets/campaigns/unicorn-impacto.mp4",
    "assets/campaigns/unicorn-impacto-v2.mp4",
    "assets/campaigns/unicorn-impacto-fallback.webp",
)


def authorized_path(relative: str) -> Path:
    """Resuelve una ruta cerrada y bloquea escapes o enlaces simbólicos."""
    candidate = ROOT / relative
    resolved_parent = candidate.parent.resolve()
    if ROOT != resolved_parent and ROOT not in resolved_parent.parents:
        raise SystemExit(f"Ruta fuera del repositorio: {relative}")
    if candidate.is_symlink():
        raise SystemExit(f"Se rechazó un enlace simbólico: {relative}")
    return candidate


def verify_git_diff() -> None:
    completed = subprocess.run(
        ["git", "diff", "--name-status", "--no-renames"], cwd=ROOT,
        check=True, capture_output=True, text=True,
    )
    allowed = set(OBSOLETE)
    unexpected = []
    for line in completed.stdout.splitlines():
        status, relative = line.split("\t", 1)
        if status != "D" or relative not in allowed:
            unexpected.append(line)
    if unexpected:
        raise SystemExit("Cambio no autorizado detectado:\n" + "\n".join(unexpected))
    print("Diff seguro: sólo eliminaciones autorizadas")


def main() -> None:
    parser = argparse.ArgumentParser(description="Detecta o elimina únicamente archivos heredados autorizados.")
    parser.add_argument("--apply", action="store_true", help="Elimina la lista cerrada de archivos obsoletos.")
    parser.add_argument("--verify-diff", action="store_true", help="Comprueba que Git sólo tenga eliminaciones autorizadas.")
    args = parser.parse_args()
    if args.verify_diff:
        verify_git_diff()
        return
    found = [relative for relative in OBSOLETE if authorized_path(relative).is_file()]
    if args.apply:
        for relative in found:
            authorized_path(relative).unlink()
            print(f"Eliminado: {relative}")
        print(f"Limpieza terminada: {len(found)} archivo(s)")
        return
    print("Archivos obsoletos detectados:" if found else "Repositorio limpio: 0 archivos obsoletos")
    for relative in found:
        print(relative)


if __name__ == "__main__":
    main()
