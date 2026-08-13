# Guía Operativa · Capacitación

Aplicación estática para capacitación paso a paso y consulta rápida de recetas. El único motor editable es `outputs/CMS_Guia_Operativa_v2.xlsx`.

## Flujo seguro

1. Edita el CMS sin cambiar nombres de pestañas ni encabezados.
2. Ejecuta `python scripts/build_content.py`.
3. Valida con `python scripts/audit_project.py` y `python -m pytest -q`.
4. Sube el proyecto. GitHub Actions regenera, audita, prueba y publica únicamente el sitio limpio.

Si actualizas un repositorio que todavía conserva archivos heredados, ejecuta **Actions → Limpiar archivos obsoletos → Run workflow** y confirma `ELIMINAR`. Sólo se pueden borrar las rutas explícitas de `scripts/cleanup_obsolete.py`.

## Diez correcciones integradas

1. Restauración de las tres fichas de proceso faltantes, incluida Cold Brew Toddy.
2. CMS Excel convertido en fuente única del catálogo, módulos, rutas y pasos.
3. Escritura atómica de `content.json`, `content.js` y `catalog.json`.
4. Validación estricta de pestañas, encabezados, IDs, opciones y rutas.
5. Auditoría de imágenes reales, archivos vacíos, límite de 25 MB y carpetas menores a 100 archivos.
6. Eliminación de motores Python/JSON duplicados, CMS heredado y medio temporal de cero bytes.
7. Workflow con dependencias fijadas, caché pip y etapas separadas de generación, auditoría y pruebas.
8. Publicación mínima mediante `prepare_site.py`, sin CMS, scripts, pruebas ni fuentes privadas.
9. Navegación con URL, botón Atrás, reanudación de capacitación y filtros por subcategoría.
10. Accesibilidad, mensajes en vivo, atajo `/`, imagen de respaldo y caché offline renovada.

## Contenido validado

- 82 referencias visuales.
- 5 módulos interactivos y 45 pasos.
- Bebidas, procesos y alimentos.
- Cajeta Cream omite Roast; Cold Brew conserva parámetros de tanda completa y media.

Ningún archivo del proyecto supera 25 MB.
