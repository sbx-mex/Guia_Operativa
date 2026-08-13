# Muestra · Recetarios y Manuales

Prototipo operativo para convertir un recetario en una experiencia guiada.

## Flujo

1. El usuario elige **Tamaño**.
2. Elige la bebida: **Café Frappuccino** o **Cajeta Frappuccino**.
3. Cajeta pregunta **Café o Cream**.
4. La preparación avanza paso a paso mostrando sólo la cantidad del tamaño elegido.
5. Cajeta Cream omite Frappuccino Roast y comienza con leche.

## Actualizar el motor

Edita `CMS_Recetarios_Manuales_Frappuccino.xlsx` y ejecuta:

```bash
python scripts/build_recipes.py
```

El script valida pestañas, recetas activas, variantes, tamaños y la regla Cream antes de generar `data/recipes.js`.

## Abrir la muestra

Abre `index.html`. No requiere servidor, instalación ni conexión a internet.

Fuente de la muestra: `RECETARIO BEBIDAS FRAPPUCCINO.pdf`, páginas 4 y 5.
