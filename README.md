# Guía Operativa · Capacitación

Aplicación estática para capacitación paso a paso y consulta rápida de recetas. El único motor editable es `outputs/CMS_Guia_Operativa_v2.xlsx`.

## Prioridad Unicorn · 13–17 de agosto

- **Unicorn Frappuccino:** práctica guiada únicamente en tamaño Grande.
- **Salsa Azul Drizzle:** preparación separada, mezcla sin grumos y vida útil de 24 horas.
- Los dosificadores de mocha blanco muestran **6 pumps CBS** y **8 pumps CBS** sin ambigüedad.
- La ventana emergente se activa del **13 al 17 de agosto** en horario `America/Mexico_City`.
- La campaña integra contexto para Checklist, Buenas prácticas y Concurso, más una evaluación de cinco reactivos.
- Las recetas Lavanda W33 quedan disponibles como temporada adicional, sin desplazar la prioridad Unicorn.

## Flujo seguro

1. Edita el CMS sin cambiar nombres de pestañas ni encabezados.
2. Ejecuta `python scripts/build_content.py`.
3. Valida con `python scripts/audit_project.py` y `python -m pytest -q`.
4. Sube el proyecto. GitHub Actions regenera, audita, prueba y publica únicamente el sitio limpio.

El workflow instala siempre `requirements.txt`; esto incluye `openpyxl`, requerido para leer el CMS Excel.

## Objetivos y avance

- Abre **Objetivos** desde el menú principal.
- Selecciona la tienda por CC o nombre. Los objetivos diarios de ADT y los objetivos diarios de Unicorn/Cake Pop se cargan desde `data/objectives.csv`.
- Actualiza únicamente **Real del día**; el alcance diario y acumulado se recalcula en el dispositivo y queda guardado por tienda.
- **Descargar objetivos PDF** entrega de inmediato el documento precalculado de la tienda.
- **Exportar avance a PDF** abre la hoja horizontal con objetivos, reales y alcance para los tres indicadores.
- **Ver términos y condiciones** descarga una versión optimizada para web del documento oficial.
- El exportador técnico acepta un JSON compatible mediante `python scripts/export_objectives.py captura.json`. El PDF se guarda automáticamente como `Tienda_Unicorn_Frapp_Cake_Pop.pdf`; también puedes indicar una ruta de salida como segundo argumento.
- **Compartir en Workvivo** usa el menú nativo del dispositivo; si no está disponible, copia un resumen listo para pegar.

Para regenerar el catálogo después de editar el CSV usa `python scripts/build_objectives.py`. Los PDFs ligeros se generan durante `python scripts/prepare_site.py`, por lo que no se almacenan 873 duplicados en el repositorio.

La evaluación Unicorn permite registrar a quién se evaluó, fecha/hora automática y una foto opcional de práctica. La foto permanece en la sesión del dispositivo y no se envía a servidores.

Si actualizas un repositorio que todavía conserva archivos heredados, ejecuta **Actions → Limpiar archivos obsoletos → Run workflow** y confirma `ELIMINAR`. Sólo se pueden borrar las rutas explícitas de `scripts/cleanup_obsolete.py`.

## Diez correcciones integradas

1. Restauración de las tres fichas de proceso faltantes, incluida Cold Brew Toddy.
2. CMS Excel convertido en fuente única del catálogo, módulos, rutas y pasos.
3. Escritura atómica de `content.json` y `content.js`.
4. Validación estricta de pestañas, encabezados, IDs, opciones y rutas.
5. Auditoría de imágenes reales, archivos vacíos, límite de 25 MB y carpetas menores a 100 archivos.
6. Eliminación de motores Python/JSON duplicados, CMS heredado y medio temporal de cero bytes.
7. Workflow con dependencias fijadas, caché pip y etapas separadas de generación, auditoría y pruebas.
8. Publicación mínima mediante `prepare_site.py`, sin CMS, scripts, pruebas ni fuentes privadas.
9. Navegación con URL, botón Atrás, reanudación y salto automático del selector Grande cuando es la única opción.
10. PWA para iOS/Android con guía de instalación, atajos, áreas seguras, caché offline y evaluación Unicorn.

## Contenido validado

- 90 referencias visuales.
- 13 módulos interactivos y 92 pasos.
- Bebidas, procesos y alimentos.
- Cajeta Cream omite Roast; Cold Brew conserva parámetros de tanda completa y media.

Ningún archivo del proyecto supera 25 MB.
