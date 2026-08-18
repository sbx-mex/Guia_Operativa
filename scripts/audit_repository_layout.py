#!/usr/bin/env python3
"""Valida que la raíz conserve únicamente el núcleo público del proyecto."""

from __future__ import annotations

import json
from pathlib import Path

from cleanup_obsolete import OBSOLETE

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_FILES = {
    ".gitignore",
    ".nojekyll",
    "README.md",
    "app.js",
    "index.html",
    "manifest.webmanifest",
    "objectives.js",
    "offline.html",
    "requirements.txt",
    "styles.css",
    "sw.js",
}
ALLOWED_DIRECTORIES = {".git", ".github", "assets", "data", "outputs", "scripts", "tests"}
IGNORED_DIRECTORIES = {"_site", ".venv", ".venv-ci", "node_modules"}


def main() -> int:
    unexpected = []
    for entry in sorted(ROOT.iterdir(), key=lambda value: value.name.casefold()):
        if entry.name in IGNORED_DIRECTORIES:
            continue
        allowed = entry.name in (ALLOWED_DIRECTORIES if entry.is_dir() else ALLOWED_FILES)
        if not allowed:
            unexpected.append(entry.name)
    obsolete = sorted(relative for relative in OBSOLETE if (ROOT / relative).exists())
    missing = sorted(name for name in ALLOWED_FILES if not (ROOT / name).is_file())
    canonical = ROOT / "outputs" / "CMS_Guia_Operativa_v2.xlsx"
    report = {
        "status": "ok" if not unexpected and not obsolete and not missing and canonical.is_file() else "error",
        "rootFiles": len([entry for entry in ROOT.iterdir() if entry.is_file()]),
        "unexpected": unexpected,
        "obsolete": obsolete,
        "missing": missing,
        "canonicalCms": canonical.relative_to(ROOT).as_posix() if canonical.is_file() else None,
    }
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
