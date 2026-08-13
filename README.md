# Guía Operativa · Capacitación

Aplicación estática para capacitación paso a paso y consulta rápida de recetas.

## Experiencia

- **Capacitarme:** el usuario elige área, receta/proceso, configuración y avanza una acción a la vez.
- **Buscar una receta:** muestra sólo el producto; la ficha completa aparece bajo demanda.
- **CMS:** `outputs/CMS_Guia_Operativa_v2.xlsx` separa contenidos, selectores, opciones, rutas, pasos, equipo, normas y medios.

## Contenido incluido

- 82 referencias visuales reales clasificadas en bebidas, procesos y alimentos.
- Rutas interactivas de Café Frappuccino, Cajeta Café/Cream, Cold Brew Toddy, Pan de queso y Croissant.
- Cold Brew Toddy con tanda completa/media, 20 horas de preparación y 5 días refrigerado.
- Pie de página y canal de comentarios solicitados.

## Actualización segura

1. Actualiza el CMS sin cambiar sus encabezados.
2. Mantén IDs únicos y rutas relativas.
3. Regenera `data/content.js` con `python scripts/build_content.py`.
4. Ejecuta `python -m pytest -q`.
5. Sube únicamente el contenido del ZIP. El workflow valida y publica GitHub Pages.

Las carpetas de medios están separadas por categoría, contienen menos de 100 archivos y ningún archivo excede 25 MB.
