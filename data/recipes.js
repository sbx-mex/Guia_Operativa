window.RECIPE_CMS = {
  "meta": {
    "version": "cms-v1",
    "source": "CMS_Recetarios_Manuales_Frappuccino.xlsx",
    "recipes": 2
  },
  "sizes": [
    {
      "id": "ALTO",
      "label": "Alto",
      "short": "A"
    },
    {
      "id": "GRANDE",
      "label": "Grande",
      "short": "G"
    },
    {
      "id": "VENTI",
      "label": "Venti",
      "short": "V"
    }
  ],
  "recipes": [
    {
      "id": "FRAP_CAFE",
      "name": "Café Frappuccino",
      "description": "Café, leche y hielo mezclados para crear una bebida original.",
      "image": "assets/cafe-frappuccino.png",
      "askVariant": false,
      "variants": [
        {
          "id": "CAFE",
          "label": "Café",
          "note": "Incluye Frappuccino Roast",
          "steps": [
            {
              "order": 1,
              "icon": "☕",
              "title": "Agrega Frappuccino Roast",
              "detail": "Dosificador metal Frappuccino Roast.",
              "values": {
                "ALTO": "2",
                "GRANDE": "3",
                "VENTI": "4"
              }
            },
            {
              "order": 2,
              "icon": "🥛",
              "title": "Vierte la leche",
              "detail": "Hasta la línea inferior del vaso.",
              "values": {
                "ALTO": "Línea inferior",
                "GRANDE": "Línea inferior",
                "VENTI": "Línea inferior"
              }
            },
            {
              "order": 3,
              "icon": "↘",
              "title": "Vierte el contenido del vaso",
              "detail": "En el vaso de la licuadora.",
              "values": {
                "ALTO": "Completo",
                "GRANDE": "Completo",
                "VENTI": "Completo"
              }
            },
            {
              "order": 4,
              "icon": "🧊",
              "title": "Agrega hielo",
              "detail": "Usa la medida volumétrica apropiada.",
              "values": {
                "ALTO": "Alto",
                "GRANDE": "Grande",
                "VENTI": "Venti"
              }
            },
            {
              "order": 5,
              "icon": "🧴",
              "title": "Agrega base Coffee",
              "detail": "Base Coffee para Frappuccino.",
              "values": {
                "ALTO": "2",
                "GRANDE": "3",
                "VENTI": "4"
              }
            },
            {
              "order": 6,
              "icon": "◉",
              "title": "Mezcla",
              "detail": "Presiona el botón n.º 1.",
              "values": {
                "ALTO": "Botón 1",
                "GRANDE": "Botón 1",
                "VENTI": "Botón 1"
              }
            },
            {
              "order": 7,
              "icon": "✓",
              "title": "Termina",
              "detail": "Vierte 6 mm debajo del borde; tapa plana y popote.",
              "values": {
                "ALTO": "6 mm",
                "GRANDE": "6 mm",
                "VENTI": "6 mm"
              }
            }
          ]
        }
      ]
    },
    {
      "id": "FRAP_CAJETA",
      "name": "Cajeta Frappuccino",
      "description": "Salsa de cajeta, leche y hielo; termina con crema batida y caramelo.",
      "image": "assets/cajeta-frappuccino.png",
      "askVariant": true,
      "variants": [
        {
          "id": "CAFE",
          "label": "Café",
          "note": "Incluye Frappuccino Roast",
          "steps": [
            {
              "order": 1,
              "icon": "☕",
              "title": "Agrega Frappuccino Roast",
              "detail": "Dosificador metal Frappuccino Roast.",
              "values": {
                "ALTO": "2",
                "GRANDE": "3",
                "VENTI": "4"
              }
            },
            {
              "order": 2,
              "icon": "🥛",
              "title": "Vierte la leche",
              "detail": "Hasta la línea inferior del vaso.",
              "values": {
                "ALTO": "Línea inferior",
                "GRANDE": "Línea inferior",
                "VENTI": "Línea inferior"
              }
            },
            {
              "order": 3,
              "icon": "↘",
              "title": "Vierte el contenido del vaso",
              "detail": "En el vaso de la licuadora.",
              "values": {
                "ALTO": "Completo",
                "GRANDE": "Completo",
                "VENTI": "Completo"
              }
            },
            {
              "order": 4,
              "icon": "🍯",
              "title": "Agrega salsa de cajeta",
              "detail": "Dosificador metal espresso.",
              "values": {
                "ALTO": "1",
                "GRANDE": "2",
                "VENTI": "2"
              }
            },
            {
              "order": 5,
              "icon": "🧊",
              "title": "Agrega hielo",
              "detail": "Usa la medida volumétrica apropiada.",
              "values": {
                "ALTO": "Alto",
                "GRANDE": "Grande",
                "VENTI": "Venti"
              }
            },
            {
              "order": 6,
              "icon": "🧴",
              "title": "Agrega base Coffee",
              "detail": "Base Coffee para Frappuccino.",
              "values": {
                "ALTO": "2",
                "GRANDE": "3",
                "VENTI": "4"
              }
            },
            {
              "order": 7,
              "icon": "◉",
              "title": "Mezcla",
              "detail": "Presiona el botón n.º 1.",
              "values": {
                "ALTO": "Botón 1",
                "GRANDE": "Botón 1",
                "VENTI": "Botón 1"
              }
            },
            {
              "order": 8,
              "icon": "✓",
              "title": "Termina",
              "detail": "Vierte 1 cm debajo del borde; crema batida, 5 vueltas de caramelo, tapa domo y popote.",
              "values": {
                "ALTO": "1 cm",
                "GRANDE": "1 cm",
                "VENTI": "1 cm"
              }
            }
          ]
        },
        {
          "id": "CREAM",
          "label": "Cream",
          "note": "Sin Roast · empieza con leche",
          "steps": [
            {
              "order": 2,
              "icon": "🥛",
              "title": "Vierte la leche",
              "detail": "Hasta la línea inferior del vaso.",
              "values": {
                "ALTO": "Línea inferior",
                "GRANDE": "Línea inferior",
                "VENTI": "Línea inferior"
              }
            },
            {
              "order": 3,
              "icon": "↘",
              "title": "Vierte el contenido del vaso",
              "detail": "En el vaso de la licuadora.",
              "values": {
                "ALTO": "Completo",
                "GRANDE": "Completo",
                "VENTI": "Completo"
              }
            },
            {
              "order": 4,
              "icon": "🍯",
              "title": "Agrega salsa de cajeta",
              "detail": "Dosificador metal espresso.",
              "values": {
                "ALTO": "1",
                "GRANDE": "2",
                "VENTI": "2"
              }
            },
            {
              "order": 5,
              "icon": "🧊",
              "title": "Agrega hielo",
              "detail": "Usa la medida volumétrica apropiada.",
              "values": {
                "ALTO": "Alto",
                "GRANDE": "Grande",
                "VENTI": "Venti"
              }
            },
            {
              "order": 6,
              "icon": "🧴",
              "title": "Agrega base Cream",
              "detail": "Base Cream para Frappuccino.",
              "values": {
                "ALTO": "2",
                "GRANDE": "3",
                "VENTI": "4"
              }
            },
            {
              "order": 7,
              "icon": "◉",
              "title": "Mezcla",
              "detail": "Presiona el botón n.º 1.",
              "values": {
                "ALTO": "Botón 1",
                "GRANDE": "Botón 1",
                "VENTI": "Botón 1"
              }
            },
            {
              "order": 8,
              "icon": "✓",
              "title": "Termina",
              "detail": "Vierte 1 cm debajo del borde; crema batida, 5 vueltas de caramelo, tapa domo y popote.",
              "values": {
                "ALTO": "1 cm",
                "GRANDE": "1 cm",
                "VENTI": "1 cm"
              }
            }
          ]
        }
      ]
    }
  ]
};
