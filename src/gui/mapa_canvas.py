"""
mapa_canvas.py
--------------
Widget que dibuja el mapa del Valle del Cauca (cuadrado N x N)
con las ciudades ingresadas y, opcionalmente, la posición del concierto.

Responsabilidades:
    - Dibujar la cuadrícula N x N con ejes y etiquetas de coordenadas.
    - Marcar cada ciudad con un círculo rojo y su nombre.
    - Marcar la posición del concierto con un símbolo verde (si se conoce).
    - Limpiar el canvas y volver al estado vacío inicial.

Uso típico desde ventana_principal.py:
    mapa = MapaCiudades(padre)
    mapa.pack(fill='both', expand=True)

    mapa.dibujar_mapa(n=10, ciudades=[("Cali", 2, 3), ("Palmira", 7, 5)])
    mapa.marcar_concierto(px=5, py=4)
    mapa.limpiar()
"""

import tkinter as tk

# ─────────────────────────────────────────────
# Constantes de dibujo
# ─────────────────────────────────────────────

CANVAS_SIZE = 370       # tamaño del canvas en píxeles (ancho = alto)
MARGEN = 38             # píxeles de margen alrededor de la cuadrícula
                        # (espacio para los números de los ejes)

RADIO_CIUDAD = 7        # radio del círculo que representa una ciudad
COLOR_CIUDAD = "#E53935"           # rojo fuerte
COLOR_CIUDAD_BORDE = "#B71C1C"     # rojo oscuro (borde)
COLOR_CIUDAD_NOMBRE = "#1A237E"    # azul oscuro (texto del nombre)

COLOR_CONCIERTO = "#43A047"        # verde (posición del concierto)
COLOR_CONCIERTO_BORDE = "#1B5E20"  # verde oscuro (borde)

COLOR_CUADRICULA = "#CCCCCC"       # gris claro (líneas internas)
COLOR_BORDE_MAPA = "#455A64"       # gris azulado (borde exterior)
COLOR_FONDO_MAPA = "#FAFAFA"       # casi blanco (fondo de la cuadrícula)


class MapaCiudades(tk.Frame):
    """
    Widget compuesto que muestra el mapa del problema del concierto.

    Internamente usa un tk.Canvas para dibujar la cuadrícula,
    los puntos de las ciudades y la posición del concierto.
    """

    def __init__(self, padre, **kwargs):
        """
        Inicializa el widget y muestra el canvas vacío.

        Parámetros:
            padre: widget padre de tkinter.
        """
        super().__init__(padre, **kwargs)

        # Estado interno: guardamos N y ciudades para poder redibujar
        # cuando se agrega o elimina una ciudad sin pasarlos de nuevo.
        self._n = None
        self._ciudades = []

        # Título del panel
        tk.Label(
            self,
            text="Mapa del Valle del Cauca",
            font=("Arial", 10, "bold")
        ).pack(pady=(6, 2))

        # Canvas principal de dibujo
        self.canvas = tk.Canvas(
            self,
            width=CANVAS_SIZE,
            height=CANVAS_SIZE,
            bg="white",
            relief="sunken",
            bd=1
        )
        self.canvas.pack(padx=8, pady=(0, 6))

        # Mostrar un texto guía cuando el canvas está vacío
        self._mostrar_mensaje_inicial()

    # ─────────────────────────────────────────
    # Métodos públicos
    # ─────────────────────────────────────────

    def dibujar_mapa(self, n: int, ciudades: list) -> None:
        """
        Redibuja el mapa completo con la cuadrícula y las ciudades.

        Llama a este método cada vez que se agrega o elimina una ciudad,
        para mantener el mapa sincronizado con la lista de la interfaz.

        Parámetros:
            n        (int)  : tamaño del cuadrado (N x N).
            ciudades (list) : lista de tuplas (nombre, x, y).
        """
        # Guardar estado para poder redibujar después
        self._n = n
        self._ciudades = ciudades

        # Borrar todo lo que había dibujado antes
        self.canvas.delete("all")

        # Dibujar en orden: primero la cuadrícula, luego los puntos
        self._dibujar_cuadricula(n)

        for nombre, x, y in ciudades:
            self._dibujar_ciudad(nombre, x, y)

    def marcar_concierto(self, px: int, py: int) -> None:
        """
        Dibuja la posición óptima del concierto sobre el mapa actual.

        Solo funciona si ya se dibujó el mapa (dibujar_mapa fue llamado).
        El marcador del concierto tiene el tag "concierto" para poder
        eliminarlo y reemplazarlo sin redibujar todo el mapa.

        Parámetros:
            px (int): coordenada X del concierto.
            py (int): coordenada Y del concierto.
        """
        if self._n is None:
            return  # No hay mapa dibujado todavía

        # Eliminar marcador anterior si existía
        self.canvas.delete("concierto")

        cx, cy = self._grid_a_canvas(px, py)
        r = RADIO_CIUDAD + 4   # el concierto es un poco más grande que las ciudades

        # Círculo verde que representa el concierto
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill=COLOR_CONCIERTO,
            outline=COLOR_CONCIERTO_BORDE,
            width=2,
            tags="concierto"
        )

        # Nota musical + coordenadas encima del círculo
        self.canvas.create_text(
            cx, cy - r - 10,
            text=f"♪ ({px},{py})",
            font=("Arial", 8, "bold"),
            fill=COLOR_CONCIERTO_BORDE,
            tags="concierto"
        )

    def limpiar(self) -> None:
        """
        Borra todo el canvas y resetea el estado interno.

        Llamar cuando el usuario presiona "Limpiar todo" en la ventana.
        """
        self._n = None
        self._ciudades = []
        self.canvas.delete("all")
        self._mostrar_mensaje_inicial()

    # ─────────────────────────────────────────
    # Métodos privados de dibujo
    # ─────────────────────────────────────────

    def _mostrar_mensaje_inicial(self) -> None:
        """Muestra un texto guía cuando el canvas está vacío."""
        centro = CANVAS_SIZE // 2
        self.canvas.create_text(
            centro, centro,
            text="Ingresa N y agrega ciudades\npara ver el mapa aquí.",
            font=("Arial", 11),
            fill="#BDBDBD",
            justify="center"
        )

    def _dibujar_cuadricula(self, n: int) -> None:
        """
        Dibuja la cuadrícula N×N con fondo, líneas internas,
        borde exterior y etiquetas numéricas en los ejes X e Y.

        Parámetros:
            n (int): tamaño del cuadrado.
        """
        celda = self._tamaño_celda(n)

        # Esquinas de la cuadrícula en píxeles del canvas
        x0 = MARGEN
        y0 = MARGEN
        x1 = MARGEN + n * celda
        y1 = MARGEN + n * celda

        # Fondo de la cuadrícula
        self.canvas.create_rectangle(x0, y0, x1, y1,
                                      fill=COLOR_FONDO_MAPA, outline="")

        # Líneas internas (grilla)
        for i in range(n + 1):
            # Líneas verticales
            px = MARGEN + i * celda
            self.canvas.create_line(px, y0, px, y1, fill=COLOR_CUADRICULA, width=1)

            # Líneas horizontales
            py = MARGEN + i * celda
            self.canvas.create_line(x0, py, x1, py, fill=COLOR_CUADRICULA, width=1)

        # Borde exterior más grueso
        self.canvas.create_rectangle(x0, y0, x1, y1,
                                      outline=COLOR_BORDE_MAPA, width=2)

        # ── Etiquetas de los ejes ──────────────────────
        # Para N grande, mostramos solo algunas etiquetas para no saturar.
        # paso_etiqueta = cada cuántos puntos ponemos un número.
        paso_etiqueta = max(1, n // 6)

        # Eje X: números abajo de la cuadrícula
        for i in range(n + 1):
            if i % paso_etiqueta == 0 or i == n:
                px = MARGEN + i * celda
                self.canvas.create_text(
                    px, y1 + 14,
                    text=str(i),
                    font=("Arial", 7),
                    fill="#555555"
                )

        # Eje Y: números a la izquierda de la cuadrícula
        # (Y=0 abajo, Y=N arriba — igual que el sistema de coordenadas del problema)
        for i in range(n + 1):
            if i % paso_etiqueta == 0 or i == n:
                py = MARGEN + (n - i) * celda   # invertir: Y crece hacia arriba
                self.canvas.create_text(
                    MARGEN - 16, py,
                    text=str(i),
                    font=("Arial", 7),
                    fill="#555555"
                )

        # Letras de eje en los extremos
        self.canvas.create_text(
            MARGEN + n * celda // 2, CANVAS_SIZE - 4,
            text="X", font=("Arial", 9, "bold"), fill="#333333"
        )
        self.canvas.create_text(
            7, MARGEN + n * celda // 2,
            text="Y", font=("Arial", 9, "bold"), fill="#333333"
        )

    def _dibujar_ciudad(self, nombre: str, x: int, y: int) -> None:
        """
        Dibuja el marcador de una ciudad: un círculo rojo con nombre y coordenadas.

        Parámetros:
            nombre (str): nombre de la ciudad.
            x, y   (int): coordenadas en la cuadrícula.
        """
        cx, cy = self._grid_a_canvas(x, y)
        r = RADIO_CIUDAD

        # Círculo rojo
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill=COLOR_CIUDAD,
            outline=COLOR_CIUDAD_BORDE,
            width=1.5
        )

        # Nombre encima del círculo
        self.canvas.create_text(
            cx, cy - r - 9,
            text=nombre,
            font=("Arial", 7, "bold"),
            fill=COLOR_CIUDAD_NOMBRE
        )

        # Coordenadas debajo del círculo
        self.canvas.create_text(
            cx, cy + r + 9,
            text=f"({x},{y})",
            font=("Arial", 6),
            fill="#757575"
        )

    # ─────────────────────────────────────────
    # Conversión de coordenadas
    # ─────────────────────────────────────────

    def _grid_a_canvas(self, x: int, y: int) -> tuple:
        """
        Convierte coordenadas de la cuadrícula del problema (x, y)
        a coordenadas en píxeles del canvas de tkinter.

        La cuadrícula del problema tiene Y creciendo hacia arriba.
        El canvas de tkinter tiene Y creciendo hacia abajo.
        Por eso se invierte el eje Y: canvas_y = MARGEN + (N - y) * celda.

        Parámetros:
            x, y (int): coordenadas en la cuadrícula.

        Retorna:
            tuple (canvas_x, canvas_y): píxeles en el canvas.
        """
        celda = self._tamaño_celda(self._n)
        canvas_x = MARGEN + x * celda
        canvas_y = MARGEN + (self._n - y) * celda   # invertir Y
        return canvas_x, canvas_y

    def _tamaño_celda(self, n: int) -> float:
        """
        Calcula el tamaño en píxeles de cada celda de la cuadrícula.

        La cuadrícula debe caber dentro del canvas menos los márgenes
        en los cuatro lados.

        Parámetros:
            n (int): tamaño del cuadrado.

        Retorna:
            float: píxeles por celda.
        """
        espacio = CANVAS_SIZE - 2 * MARGEN
        return espacio / n
