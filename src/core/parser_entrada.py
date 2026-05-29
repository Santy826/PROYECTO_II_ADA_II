"""
parser_entrada.py
-----------------
Parsea el texto de entrada del problema del concierto.

Formato esperado:
    N
    M
    NombreCiudad1 X1 Y1
    NombreCiudad2 X2 Y2
    ...

Reglas importantes:
    - Las líneas vacías o en blanco se ignoran automáticamente.
    - El nombre de una ciudad puede tener espacios (ej: "Santa Marta").
      Los dos últimos tokens de cada línea son siempre X e Y; todo lo
      anterior forma el nombre.
    - N y M deben ser enteros. Las coordenadas también.
"""


def parse_input(texto: str):
    """
    Convierte el texto de entrada en los datos estructurados del problema.

    Parámetros:
        texto (str): texto completo en el formato N / M / ciudades.

    Retorna:
        tuple (n, ciudades, error):
            - Si OK  : (n:int, ciudades:list[tuple], None)
            - Si falla: (None, None, mensaje_error:str)

    Ejemplo de uso:
        n, ciudades, error = parse_input("10\\n2\\nCali 2 3\\nPalmira 7 5")
        if error:
            print("Error:", error)
        else:
            print(n, ciudades)
    """
    try:
        # ── 1. Separar líneas y descartar las vacías ──────────────────
        # Las líneas en blanco se ignoran para ser tolerantes con copiar-pegar
        # desde editores que insertan líneas extras.
        todas_las_lineas = texto.strip().split('\n')
        lineas = [l for l in todas_las_lineas if l.strip() != '']

        if len(lineas) < 2:
            return None, None, (
                "Entrada incompleta: se necesitan al menos 2 líneas "
                "(N en la primera, M en la segunda)."
            )

        # ── 2. Primera línea: N ───────────────────────────────────────
        try:
            n = int(lineas[0].strip())
        except ValueError:
            return None, None, (
                f"Primera línea inválida: '{lineas[0].strip()}' no es un entero. "
                f"Se esperaba el tamaño N del cuadrado."
            )

        # ── 3. Segunda línea: M ───────────────────────────────────────
        try:
            m = int(lineas[1].strip())
        except ValueError:
            return None, None, (
                f"Segunda línea inválida: '{lineas[1].strip()}' no es un entero. "
                f"Se esperaba el número M de ciudades."
            )

        # ── 4. Verificar que haya suficientes líneas de ciudades ──────
        lineas_ciudades = lineas[2:]
        if len(lineas_ciudades) < m:
            return None, None, (
                f"Se esperaban {m} ciudad(es) pero solo se encontraron "
                f"{len(lineas_ciudades)} línea(s) de datos."
            )

        # ── 5. Parsear cada ciudad ────────────────────────────────────
        ciudades = []
        for i in range(m):
            linea = lineas_ciudades[i].strip()
            partes = linea.split()

            # Mínimo: una palabra de nombre + X + Y = 3 tokens
            if len(partes) < 3:
                return None, None, (
                    f"Ciudad {i + 1}: línea '{linea}' está incompleta. "
                    f"Formato esperado: NombreCiudad X Y"
                )

            # Los dos últimos tokens son X e Y.
            # Todo lo anterior forma el nombre (permite nombres con espacios).
            y_str = partes[-1]
            x_str = partes[-2]
            nombre = " ".join(partes[:-2])

            # Validar X
            try:
                x = int(x_str)
            except ValueError:
                return None, None, (
                    f"Ciudad {i + 1} ('{nombre}'): "
                    f"'{x_str}' no es un número entero válido para X."
                )

            # Validar Y
            try:
                y = int(y_str)
            except ValueError:
                return None, None, (
                    f"Ciudad {i + 1} ('{nombre}'): "
                    f"'{y_str}' no es un número entero válido para Y."
                )

            ciudades.append((nombre, x, y))

        return n, ciudades, None

    except Exception as e:
        return None, None, f"Error inesperado al procesar la entrada: {str(e)}"


def validate_input(n, cities):
    """
    Valida que los datos ya parseados sean correctos.

    Esta función recibe datos ya convertidos a Python (n como int,
    cities como lista de tuplas) y aplica las reglas del dominio.

    Parámetros:
        n      (int)  : tamaño del cuadrado.
        cities (list) : lista de tuplas (nombre, x, y).

    Retorna:
        list: lista de strings con mensajes de error.
              Lista vacía significa que los datos son válidos.
    """
    errores = []

    # ── Validar N ─────────────────────────────────────────────────────
    if n <= 0:
        errores.append(f"N debe ser un entero positivo (recibido: {n}).")

    if n > 1000:
        errores.append(f"N={n} es muy grande. El máximo recomendado es 1000.")

    # ── Validar que haya ciudades ──────────────────────────────────────
    if len(cities) == 0:
        errores.append("Debe haber al menos una ciudad.")
        return errores  # sin ciudades no tiene sentido continuar

    if len(cities) > 100:
        errores.append(
            f"Hay {len(cities)} ciudades. El máximo recomendado es 100."
        )

    # ── Validar coordenadas de cada ciudad ────────────────────────────
    for nombre, x, y in cities:
        if x < 0 or x > n:
            errores.append(
                f"Ciudad '{nombre}': X={x} está fuera del rango [0, {n}]."
            )
        if y < 0 or y > n:
            errores.append(
                f"Ciudad '{nombre}': Y={y} está fuera del rango [0, {n}]."
            )

    # ── Validar nombres duplicados ────────────────────────────────────
    nombres = [nombre for nombre, _, _ in cities]
    nombres_vistos = set()
    for nombre in nombres:
        if nombre in nombres_vistos:
            errores.append(f"Nombre duplicado: '{nombre}'.")
        nombres_vistos.add(nombre)

    # ── Validar posiciones duplicadas ─────────────────────────────────
    posiciones = [(x, y) for _, x, y in cities]
    posiciones_vistas = set()
    for nombre, x, y in cities:
        pos = (x, y)
        if pos in posiciones_vistas:
            errores.append(
                f"Posición duplicada ({x}, {y}): "
                f"ya hay una ciudad en esa coordenada."
            )
        posiciones_vistas.add(pos)

    return errores
