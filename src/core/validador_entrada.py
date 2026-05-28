"""
validador_entrada.py
--------------------
Punto de entrada único para validar los datos del problema.

NOTA PARA EL EQUIPO:
    El módulo parser_entrada.py ya incluye una función validate_input()
    que cubre las validaciones básicas. Este módulo la reutiliza y agrega
    validaciones específicas del dominio del problema del concierto.

Flujo esperado:
    errores = validar_datos(n, ciudades)
    if errores:
        mostrar_errores(errores)
    else:
        continuar_con_generacion()
"""

from src.core.parser_entrada import validate_input


def validar_datos(n: int, ciudades: list) -> list:
    """
    Valida que los datos del problema sean correctos y consistentes.

    Combina las validaciones básicas del parser con validaciones
    adicionales propias del problema del concierto.

    Parámetros:
        n       (int)  : tamaño del cuadrado N x N.
        ciudades (list): lista de tuplas (nombre, x, y).

    Retorna:
        list: Lista de strings con mensajes de error.
              Si la lista está vacía, los datos son válidos.
    """
    # Reutilizar las validaciones básicas ya implementadas en parser_entrada
    errores = validate_input(n, ciudades)

    # Validación adicional: debe haber al menos 2 ciudades para que el
    # problema de equidad tenga sentido (1 ciudad siempre tiene solución trivial)
    if len(ciudades) == 1:
        errores.append(
            "Con una sola ciudad el problema es trivial. "
            "Se recomienda ingresar al menos 2 ciudades."
        )

    # Validación adicional: verificar que el espacio tenga al menos una
    # posición libre (en teoría siempre hay una, pero es buena práctica)
    total_posiciones = (n + 1) * (n + 1)
    if len(ciudades) >= total_posiciones:
        errores.append(
            f"No hay posiciones libres en el cuadrado {n}x{n} "
            f"para ubicar el concierto con {len(ciudades)} ciudades."
        )

    return errores


def hay_errores(errores: list) -> bool:
    """
    Función de conveniencia: retorna True si la lista de errores no está vacía.

    Parámetros:
        errores (list): resultado de validar_datos().

    Retorna:
        bool: True si hay al menos un error.
    """
    return len(errores) > 0
