"""
generador_minizinc.py
---------------------
Convierte los datos parseados del problema del concierto en código MiniZinc
listo para copiar y pegar.

El modelo generado busca la ubicación más EQUITATIVA para el concierto:
minimiza la distancia Manhattan máxima a cualquier ciudad (minimax),
es decir, se acerca lo más posible a la ciudad más alejada.

Restricción clave: el concierto NO puede estar en la misma posición
exacta que ninguna ciudad.

Flujo esperado:
    datos = {"n": 10, "ciudades": [("Cali", 2, 3), ("Palmira", 5, 7)]}
    codigo = generar_codigo_minizinc(datos)
    # codigo es un string listo para pegar en MiniZinc IDE
"""


def generar_codigo_minizinc(datos: dict) -> str:
    """
    Genera un archivo MiniZinc completo (.mzn) con los datos del problema.

    El archivo generado incluye:
    - Datos del problema embebidos (N, M, coordenadas)
    - Variables de decisión (px, py)
    - Restricciones (no estar en ciudad, distancia máxima)
    - Objetivo (minimizar distancia máxima)
    - Bloque output legible

    Parámetros:
        datos (dict): Diccionario con las claves:
            - "n"       : int, tamaño del cuadrado N x N
            - "ciudades": lista de tuplas (nombre, x, y)

    Retorna:
        str: Código MiniZinc completo listo para copiar.
             Si los datos son inválidos, retorna un mensaje de error.
    """
    # Verificar que los datos tengan la forma esperada
    if not isinstance(datos, dict):
        return "% ERROR: los datos deben ser un diccionario."

    n = datos.get("n")
    ciudades = datos.get("ciudades", [])

    if n is None:
        return "% ERROR: falta el valor de N en los datos."

    if not ciudades:
        return "% ERROR: no hay ciudades en los datos."

    m = len(ciudades)

    # Construir la línea de comentario con los nombres de ciudades
    nombres_str = _formatear_nombres(ciudades)

    # Construir los arreglos de coordenadas
    coords_x = _formatear_arreglo([x for (_, x, _) in ciudades])
    coords_y = _formatear_arreglo([y for (_, _, y) in ciudades])

    # Construir el código MiniZinc por secciones
    lineas = []

    lineas += _seccion_encabezado()
    lineas += _seccion_datos(n, m, nombres_str, coords_x, coords_y)
    lineas += _seccion_variables(n)
    lineas += _seccion_restricciones()
    lineas += _seccion_objetivo()
    lineas += _seccion_output()

    return "\n".join(lineas)


# ─────────────────────────────────────────────
# Funciones auxiliares de construcción
# ─────────────────────────────────────────────

def _seccion_encabezado() -> list:
    """Retorna el bloque de comentarios de encabezado del modelo."""
    return [
        "% ============================================================",
        "% Modelo MiniZinc: ¿Dónde pongo mi concierto?",
        "% Asignatura: Análisis y Diseño de Algoritmos",
        "% Generado automáticamente — copiar y pegar en MiniZinc IDE",
        "% ============================================================",
        "",
    ]


def _seccion_datos(n: int, m: int, nombres_str: str,
                   coords_x: str, coords_y: str) -> list:
    """
    Retorna el bloque de datos del problema:
    N, M y los arreglos de coordenadas.
    """
    return [
        "% --- Datos del problema ---",
        f"int: N = {n};   % tamaño del cuadrado (N x N)",
        f"int: M = {m};   % número de ciudades",
        "",
        f"% Ciudades: {nombres_str}",
        f"array[1..M] of int: ciudad_x = {coords_x};",
        f"array[1..M] of int: ciudad_y = {coords_y};",
        "",
    ]


def _seccion_variables(n: int) -> list:
    """
    Retorna el bloque de variables de decisión.
    px y py son las coordenadas del concierto.
    dist_max es la mayor distancia Manhattan a cualquier ciudad.
    """
    return [
        "% --- Variables de decisión ---",
        f"var 0..N: px;          % coordenada X del concierto (0 a {n})",
        f"var 0..N: py;          % coordenada Y del concierto (0 a {n})",
        "",
        "% dist_max: distancia Manhattan al vecino más lejano",
        "% (usamos 2*N como cota superior máxima posible)",
        "var 0..2*N: dist_max;",
        "",
    ]


def _seccion_restricciones() -> list:
    """
    Retorna el bloque de restricciones:
    1. El concierto no puede estar en ninguna ciudad.
    2. dist_max >= distancia a cada ciudad.
    """
    return [
        "% --- Restricciones ---",
        "",
        "% 1. El concierto NO puede estar exactamente en ninguna ciudad",
        "constraint forall(i in 1..M)(",
        "    not (px = ciudad_x[i] /\\ py = ciudad_y[i])",
        ");",
        "",
        "% 2. dist_max debe ser mayor o igual que la distancia a cada ciudad",
        "%    (esto fuerza a dist_max a tomar el valor de la distancia máxima real)",
        "constraint forall(i in 1..M)(",
        "    dist_max >= abs(px - ciudad_x[i]) + abs(py - ciudad_y[i])",
        ");",
        "",
    ]


def _seccion_objetivo() -> list:
    """
    Retorna el bloque del objetivo de optimización.
    Minimizar dist_max = solución más equitativa (minimax).
    """
    return [
        "% --- Objetivo ---",
        "% Minimizar la distancia máxima: el concierto queda lo más",
        "% cerca posible de la ciudad más alejada (criterio de equidad).",
        "solve minimize dist_max;",
        "",
    ]


def _seccion_output() -> list:
    """Retorna el bloque de salida del modelo."""
    return [
        "% --- Salida ---",
        "output [",
        '    "=== Resultado del modelo ===\\n",',
        '    "Posición del concierto: (", show(px), ", ", show(py), ")\\n",',
        '    "Distancia máxima (equidad): ", show(dist_max), "\\n"',
        "];",
    ]


# ─────────────────────────────────────────────
# Utilidades de formato de texto
# ─────────────────────────────────────────────

def _formatear_arreglo(valores: list) -> str:
    """
    Convierte una lista de enteros al formato de arreglo MiniZinc.
    Ejemplo: [2, 5, 1] → "[2, 5, 1]"
    """
    elementos = ", ".join(str(v) for v in valores)
    return f"[{elementos}]"


def _formatear_nombres(ciudades: list) -> str:
    """
    Convierte la lista de ciudades en un string legible para el comentario.
    Ejemplo: [("Cali", 2, 3)] → "Cali(2,3)"
    """
    partes = [f"{nombre}({x},{y})" for (nombre, x, y) in ciudades]
    return ", ".join(partes)
