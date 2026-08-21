# Guía Operativa CORE

Biblioteca didáctica para practicar bebidas, procesos base y alimentos. El CMS maestro es `outputs/CMS_Guia_Operativa_CORE.xlsx`; de él se regeneran `data/content.json` y `data/content.js`.

## Cobertura

- 97 bebidas y procesos, cada uno con imagen de producto, ficha original y ruta independiente.
- 6 guías de alimentos para ensamble y preensamble.
- 592 pasos didácticos con cantidades resaltadas y GIF únicamente para técnicas CORE.
- Sin campañas ni recursos promocionales heredados.

## Estructura de medios

- `assets/Lote_01_Bebidas` y `assets/Lote_02_Bebidas`: 49 + 48 imágenes.
- `assets/Lote_01_Recetas` y `assets/Lote_02_Recetas`: 49 + 48 fichas.
- `assets/Lote_01_Alimentos`: 6 guías.
- `assets/GIF_CORE`: 16 técnicas optimizadas.

Cada carpeta se mantiene por debajo de 100 archivos y 25 MB.

## Flujo de publicación

1. Edita el CMS sin cambiar los nombres originales de los medios.
2. Ejecuta `python scripts/build_content.py`.
3. Ejecuta `python scripts/build_content.py --check` y `python scripts/audit_project.py`.
4. Ejecuta `python -m pytest -q`.
5. Publica; GitHub Actions vuelve a validar y despliega Pages.

La imagen de receta es la autoridad operativa. El texto del paso ayuda a aprender la secuencia, pero no sustituye cantidades, líneas, botones ni puntos de calidad visibles en la ficha.
