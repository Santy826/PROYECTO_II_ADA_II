"""
validador_entrada.py
--------------------
Validación de los datos del problema del concierto.

Este módulo tiene dos responsabilidades:
    1. Validación general: delega en parse_input las reglas básicas de formato
       (N positivo, coordenadas en rango, sin duplicados).
    2. Factibilidad: determina si existe al menos una posición libre en el
       cuadrado N×N donde colocar el concierto, sin estar en ninguna ciudad.

La factibilidad es la propiedad que, de no cumplirse, hace que MiniZinc
devuelva UNSATISFIABLE. Por eso se verifica aquí, antes de generar el código.

Flujo esperado:
    errores = validar_datos(n, ciudades)
    if errores:
        mostrar_errores(errores)
    else:
        continuar_con_generacion()
"""

from src.core.parser_entrada import validate_input


# ─────────────────────────────────────────────────────────────
# Función principal
# ─────────────────────────────────────────────────────────────

def validar_datos(n: int, ciudades: list) -> list:
    """
    Valida que los datos del problema sean correctos y consistentes.

    Combina las validaciones básicas del parser con las validaciones
    de dominio específicas del problema del concierto.

    Parámetros:
        n        (int)  : tamaño del cuadrado (N x N).
        ciudades (list) : lista de tuplas (nombre, x, y).

    Retorna:
        list: Lista de strings con mensajes de error.
              Si la lista está vacía, los datos son válidos y el problema
              es factible (MiniZinc no debería devolver UNSATISFIABLE).
    """
    # Validaciones básicas: N positivo, coordenadas en rango, sin duplicados
    errores = validate_input(n, ciudades)

    # Si ya hay errores básicos, no tiene sentido continuar con las
    # validaciones de dominio (podrían dar mensajes confusos).
    if errores:
        return errores

    # Advertencia: con una sola ciudad el problema es trivial
    if len(ciudades) == 1:
        errores.append(
            "Con una sola ciudad el problema es trivial. "
            "Se recomienda ingresar al menos 2 ciudades."
        )

    # Verificación de factibilidad: ¿hay al menos una posición libre?
    resultado = verificar_factibilidad(n, ciudades)
    if resultado["infactible"]:
        errores.append(resultado["mensaje_error"])
    elif resultado["advertencia"]:
        # No es un error que impida generar el código, pero sí una advertencia
        # útil para que el equipo sepa que el espacio está muy restringido.
        errores.append(resultado["mensaje_advertencia"])

    return errores


# ─────────────────────────────────────────────────────────────
# Verificación de factibilidad
# ─────────────────────────────────────────────────────────────

def verificar_factibilidad(n: int, ciudades: list) -> dict:
    """
    Determina si el problema tiene al menos una solución posible.

    Un problema es INFACTIBLE cuando todas las posiciones enteras del
    cuadrado están ocupadas por ciudades. En ese caso MiniZinc devuelve
    UNSATISFIABLE porque no existe ningún (px, py) que no sea ciudad.

    También detecta una zona de advertencia: cuando quedan muy pocas
    posiciones libres (menos de 5), el problema sigue siendo factible
    pero el espacio de soluciones es muy reducido.

    El cuadrado N×N tiene exactamente (N+1)² posiciones enteras válidas:
    todas las combinaciones de x ∈ [0..N] e y ∈ [0..N].

    Parámetros:
        n        (int)  : tamaño del cuadrado.
        ciudades (list) : lista de tuplas (nombre, x, y). Se asume que
                          las posiciones son únicas (el parser lo valida).

    Retorna:
        dict con las claves:
            - "total_posiciones" (int) : total de celdas enteras del cuadrado.
            - "posiciones_libres" (int): celdas no ocupadas por ninguna ciudad.
            - "infactible"        (bool): True si no hay ninguna posición libre.
            - "advertencia"       (bool): True si quedan menos de 5 posiciones libres.
            - "mensaje_error"     (str) : mensaje para el caso infactible.
            - "mensaje_advertencia"(str): mensaje para el caso de advertencia.
    """
    total_posiciones = (n + 1) * (n + 1)
    ciudades_en_grid = len(ciudades)
    posiciones_libres = total_posiciones - ciudades_en_grid

    # Umbral: menos de 5 posiciones libres se considera zona de advertencia
    UMBRAL_ADVERTENCIA = 5

    infactible = posiciones_libres <= 0
    advertencia = (not infactible) and (posiciones_libres < UMBRAL_ADVERTENCIA)

    mensaje_error = ""
    if infactible:
        mensaje_error = (
            f"El problema no tiene solución (UNSATISFIABLE): "
            f"el cuadrado {n}×{n} tiene {total_posiciones} posición(es) "
            f"y todas están ocupadas por ciudades. "
            f"Aumente N o reduzca el número de ciudades."
        )

    mensaje_advertencia = ""
    if advertencia:
        mensaje_advertencia = (
            f"Advertencia: solo quedan {posiciones_libres} posición(es) "
            f"libre(s) en el cuadrado {n}×{n}. "
            f"El concierto tendrá muy pocas ubicaciones posibles."
        )

    return {
        "total_posiciones":    total_posiciones,
        "posiciones_libres":   posiciones_libres,
        "infactible":          infactible,
        "advertencia":         advertencia,
        "mensaje_error":       mensaje_error,
        "mensaje_advertencia": mensaje_advertencia,
    }


# ─────────────────────────────────────────────────────────────
# Utilidades
# ─────────────────────────────────────────────────────────────

def hay_errores(errores: list) -> bool:
    """
    Retorna True si la lista de errores no está vacía.

    Parámetros:
        errores (list): resultado de validar_datos().

    Retorna:
        bool: True si hay al menos un error.
    """
    return len(errores) > 0
