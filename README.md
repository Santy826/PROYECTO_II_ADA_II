# PROYECTO_II_ADA_II

Estructura base del Proyecto II (ADA II) para el problema **"¿Dónde pongo mi concierto?"**.

## Objetivo de esta primera entrega interna

En este estado del repositorio se incluye **solo la estructura** del proyecto, organizada para cumplir los requisitos académicos:

- Informe en PDF con formato IEEE.
- Modelo del problema (MiniZinc).
- Explicación de implementación (sin código en el informe final).
- Pruebas con datos específicos y su análisis.
- Interfaz gráfica para cargar entrada y generar código MiniZinc.

## Estructura propuesta

```text
.
├── docs/
│   ├── informe_ieee/
│   │   ├── README.md
│   │   └── secciones/
│   │       ├── 01_modelo_del_problema.md
│   │       ├── 02_explicacion_implementacion.md
│   │       ├── 03_pruebas_con_datos.md
│   │       ├── 04_analisis_de_resultados.md
│   │       └── 05_conclusiones.md
│   └── requisitos_proyecto.md
├── minizinc/
│   ├── model/
│   │   └── concierto_base.mzn
│   ├── data/
│   │   ├── ejemplo_1.dzn
│   │   └── README.md
│   └── output/
│       └── README.md
├── src/
│   ├── app/
│   │   └── main.py
│   ├── core/
│   │   ├── parser_entrada.py
│   │   ├── validador_entrada.py
│   │   └── generador_minizinc.py
│   ├── gui/
│   │   ├── ventana_principal.py
│   │   └── componentes.py
│   └── utils/
│       └── constantes.py
├── tests/
│   ├── inputs/
│   │   ├── caso_basico.txt
│   │   ├── caso_colineal.txt
│   │   └── caso_extremo.txt
│   └── README.md
├── data/
│   └── samples/
│       └── entrada_ejemplo.txt
├── scripts/
│   └── run_app.sh
├── requirements.txt
└── .gitignore
```

## Siguiente paso sugerido

Implementar la lógica por módulos siguiendo este orden:

1. Parser y validación de entrada.
2. Generador de modelo/datos MiniZinc.
3. Interfaz gráfica para pegar entrada y obtener salida.
4. Casos de prueba y análisis.