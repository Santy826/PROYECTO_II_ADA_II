"""Genera texto MiniZinc (modelo y/o datos) desde la entrada parseada.

Este generador produce un modelo con secciones comentadas que siguen
el formato esperado por la corrección: encabezados como
"%Variables" y "%Restricciones", comentarios al lado de cada
declaración y un bloque `solve` y `output` legible.

La función acepta como `entrada` un diccionario con la forma opcional:

{
  "variables": [ ("int", "x_1", "Mesa"), ("int", "x_2", "Notebook") ],
  "constraints": ["x_1 >= 0; %No negatividad", "x_1 + x_2 <= 10000; %Procesadores"],
  "objective": "maximize 1000*x_1 + 750*x_2;",
  "output_vars": ["x_1", "x_2"]
}

Si `entrada` no tiene la forma esperada, la función intentará producir
un modelo mínimo o devolver una cadena vacía.
"""

from typing import Any, Dict, Iterable, List, Tuple


def _format_variable(v: Tuple[str, str, str]) -> str:
    tipo, nombre, comentario = v
    line = f"var {tipo}: {nombre};"
    if comentario:
        line += f" %" + comentario
    return line


def generar_codigo_minizinc(entrada: Any) -> str:
    if entrada is None:
        return ""

    # Si entrada es un string, asumimos ya es código MiniZinc: devolver tal cual.
    if isinstance(entrada, str):
        return entrada

    # Esperamos un diccionario con claves opcionales.
    if not isinstance(entrada, Dict):
        try:
            entrada = dict(entrada)
        except Exception:
            return ""

    vars_list: List[Tuple[str, str, str]] = entrada.get("variables", [])
    constraints: List[str] = entrada.get("constraints", [])
    objective: str = entrada.get("objective", "")
    output_vars: List[str] = entrada.get("output_vars", [])

    parts: List[str] = []

    # Variables
    parts.append("%Variables")
    if vars_list:
        for v in vars_list:
            # permitir tuplas de 2 o 3 elementos
            if len(v) == 3:
                parts.append(_format_variable(v))
            elif len(v) == 2:
                tipo, nombre = v
                parts.append(f"var {tipo}: {nombre};")
            else:
                # ignorar formato inesperado
                continue
    else:
        parts.append("% (No se declararon variables en la entrada)")

    parts.append("")

    # Restricciones
    parts.append("%Restricciones")
    if constraints:
        for c in constraints:
            # Aceptar constraint sin el prefijo
            c_str = c.strip()
            if not c_str.startswith("constraint") and not c_str.startswith("solve"):
                # aseguramos terminar en ';' si no lo tiene
                if not c_str.endswith(";"):
                    c_str += ";"
                parts.append(f"constraint {c_str}")
            else:
                parts.append(c_str)
    else:
        parts.append("% (No hay restricciones definidas)")

    parts.append("")

    # Objetivo / solve
    if objective:
        obj = objective.strip()
        # permitir que venga con o sin 'solve'
        if not obj.startswith("solve"):
            parts.append(f"solve {obj}")
        else:
            parts.append(obj)
    else:
        parts.append("% (No se definió objetivo - añadir 'solve ...;')")

    parts.append("")

    # Output
    if output_vars:
        out_items = []
        for i, name in enumerate(output_vars):
            if i == 0:
                label = f"{name}: "
            else:
                label = f"\\n{name}: "
            out_items.append(f'"{label}"')
            out_items.append(f"show({name})")
        out_line = "output([" + ", ".join(out_items) + "]);"
        parts.append(out_line)
    else:
        parts.append('% (No hay variables para output)')

    # Unir con saltos de línea
    return "\n".join(parts)

