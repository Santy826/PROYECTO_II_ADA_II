"""
ventana_principal.py
--------------------
Ventana principal de la aplicación "¿Dónde pongo mi concierto?".

Organiza la interfaz en dos áreas:
    - Panel izquierdo : ingreso y validación de datos del problema.
    - Panel derecho   : dos pestañas — Mapa de ciudades y Código MiniZinc.

Flujo de uso:
    1. El usuario ingresa N, M y las ciudades.
       → el mapa se actualiza en tiempo real con cada ciudad que se agrega.
    2. Presiona "Generar MiniZinc".
       → el sistema valida, genera el código, lo muestra en la pestaña Código
         y cambia automáticamente a esa pestaña.
    3. El usuario copia el código y lo pega en MiniZinc IDE.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Garantizar que Python encuentre el paquete src sin importar
# desde dónde se ejecute este archivo.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.parser_entrada import parse_input
from src.core.validador_entrada import validar_datos, hay_errores
from src.core.generador_minizinc import generar_codigo_minizinc
from src.gui.componentes import AreaTextoCopiable
from src.gui.mapa_canvas import MapaCiudades


class VentanaPrincipal(tk.Tk):
    """
    Ventana principal de la aplicación.
    Hereda de tk.Tk para ser la ventana raíz del programa.
    """

    def __init__(self):
        super().__init__()
        self.title("¿Dónde pongo mi concierto? — Generador MiniZinc")
        self.geometry("1000x600")
        self.resizable(True, True)

        self._construir_layout()

    # ─────────────────────────────────────────
    # Construcción del layout
    # ─────────────────────────────────────────

    def _construir_layout(self) -> None:
        """Construye el layout de la ventana: título + dos paneles."""

        # Título
        tk.Label(
            self,
            text="¿Dónde pongo mi concierto?",
            font=("Arial", 14, "bold"),
            pady=7
        ).pack(fill='x')

        # Marco principal que contiene los dos paneles
        marco = tk.Frame(self)
        marco.pack(fill='both', expand=True, padx=10, pady=(0, 8))

        # ── Panel izquierdo: ingreso de datos ────────────────────
        panel_izq = tk.LabelFrame(
            marco,
            text=" Datos del problema ",
            font=("Arial", 10, "bold"),
            padx=8, pady=8,
            width=370
        )
        panel_izq.pack(side=tk.LEFT, fill='y', padx=(0, 6))
        panel_izq.pack_propagate(False)
        self._construir_panel_entrada(panel_izq)

        # ── Panel derecho: mapa + código MiniZinc (pestañas) ─────
        panel_der = tk.LabelFrame(
            marco,
            text=" Visualización ",
            font=("Arial", 10, "bold"),
            padx=6, pady=6
        )
        panel_der.pack(side=tk.LEFT, fill='both', expand=True)
        self._construir_panel_derecho(panel_der)

    def _construir_panel_entrada(self, padre) -> None:
        """Construye el panel izquierdo: campos N, M, ciudades y botones."""

        # ── N: tamaño de la cuadrícula ───────────────────────────
        tk.Label(padre, text="1. Tamaño de la cuadrícula (N):",
                 font=("Arial", 9, "bold")).pack(anchor='w', pady=(0, 2))
        self.entry_n = tk.Entry(padre, width=10)
        self.entry_n.pack(anchor='w', pady=(0, 8))

        # ── M: número de ciudades ────────────────────────────────
        tk.Label(padre, text="2. Número de ciudades (M):",
                 font=("Arial", 9, "bold")).pack(anchor='w', pady=(0, 2))
        self.entry_m = tk.Entry(padre, width=10)
        self.entry_m.pack(anchor='w', pady=(0, 8))

        # ── Agregar ciudad ───────────────────────────────────────
        tk.Label(padre, text="3. Agregar ciudad (Nombre  X  Y):",
                 font=("Arial", 9, "bold")).pack(anchor='w', pady=(0, 2))

        fila = tk.Frame(padre)
        fila.pack(anchor='w', pady=(0, 4))

        self.entry_nombre = tk.Entry(fila, width=12)
        self.entry_nombre.pack(side=tk.LEFT, padx=(0, 3))
        self.entry_nombre.insert(0, "Nombre")
        self.entry_nombre.bind("<FocusIn>", self._limpiar_placeholder_nombre)

        self.entry_x = tk.Entry(fila, width=5)
        self.entry_x.pack(side=tk.LEFT, padx=(0, 3))
        self.entry_x.insert(0, "X")
        self.entry_x.bind("<FocusIn>", self._limpiar_placeholder_x)

        self.entry_y = tk.Entry(fila, width=5)
        self.entry_y.pack(side=tk.LEFT, padx=(0, 3))
        self.entry_y.insert(0, "Y")
        self.entry_y.bind("<FocusIn>", self._limpiar_placeholder_y)

        tk.Button(
            fila, text="Agregar",
            command=self.agregar_ciudad,
            bg="#607D8B", fg="white"
        ).pack(side=tk.LEFT)

        # ── Lista de ciudades ────────────────────────────────────
        tk.Label(padre, text="Ciudades registradas:",
                 font=("Arial", 9, "bold")).pack(anchor='w', pady=(4, 2))
        self.listbox = tk.Listbox(padre, height=8, font=("Courier", 9))
        self.listbox.pack(fill='x', pady=(0, 4))

        tk.Button(
            padre, text="Eliminar ciudad seleccionada",
            command=self.eliminar_ciudad,
            bg="#f44336", fg="white", font=("Arial", 8)
        ).pack(anchor='w', pady=(0, 10))

        # ── Botones de acción ────────────────────────────────────
        marco_botones = tk.Frame(padre)
        marco_botones.pack(fill='x')

        tk.Button(
            marco_botones,
            text="⚙  Generar MiniZinc",
            command=self.generar_minizinc,
            bg="#4CAF50", fg="white",
            font=("Arial", 10, "bold"),
            pady=4
        ).pack(side=tk.LEFT, padx=(0, 5), fill='x', expand=True)

        tk.Button(
            marco_botones,
            text="Limpiar todo",
            command=self.limpiar_todo,
            bg="#9E9E9E", fg="white",
            font=("Arial", 9)
        ).pack(side=tk.LEFT)

    def _construir_panel_derecho(self, padre) -> None:
        """
        Construye el panel derecho con dos pestañas:
            - Pestaña 'Mapa'  : el widget MapaCiudades.
            - Pestaña 'Código': el widget AreaTextoCopiable.
        """
        # Notebook (sistema de pestañas de tkinter)
        self.notebook = ttk.Notebook(padre)
        self.notebook.pack(fill='both', expand=True)

        # ── Pestaña 1: Mapa ──────────────────────────────────────
        tab_mapa = tk.Frame(self.notebook)
        self.notebook.add(tab_mapa, text="  🗺  Mapa de ciudades  ")

        self.mapa = MapaCiudades(tab_mapa)
        self.mapa.pack(fill='both', expand=True)

        # ── Pestaña 2: Código MiniZinc ───────────────────────────
        self.tab_codigo = tk.Frame(self.notebook)
        self.notebook.add(self.tab_codigo, text="  📄  Código MiniZinc  ")

        tk.Label(
            self.tab_codigo,
            text="Presiona 'Generar MiniZinc', copia el código y pégalo en MiniZinc IDE.",
            font=("Arial", 8), fg="#555555", wraplength=480, justify='left'
        ).pack(anchor='w', padx=8, pady=(6, 2))

        self.area_codigo = AreaTextoCopiable(self.tab_codigo, titulo="")
        self.area_codigo.pack(fill='both', expand=True)

        self.area_codigo.establecer_texto(
            "% El código MiniZinc aparecerá aquí\n"
            "% después de presionar 'Generar MiniZinc'.\n"
        )

    # ─────────────────────────────────────────
    # Acciones de la interfaz
    # ─────────────────────────────────────────

    def agregar_ciudad(self) -> None:
        """
        Lee los campos de nombre, X e Y y agrega la ciudad a la lista.
        Después de agregar, actualiza el mapa automáticamente.
        """
        nombre = self.entry_nombre.get().strip()
        x_str  = self.entry_x.get().strip()
        y_str  = self.entry_y.get().strip()

        if nombre in ("Nombre", "") or x_str in ("X", "") or y_str in ("Y", ""):
            messagebox.showwarning("Campos incompletos",
                                   "Ingrese un nombre y coordenadas X e Y válidas.")
            return

        m_str = self.entry_m.get().strip()
        try:
            m_int = int(m_str)
        except ValueError:
            messagebox.showerror("Falta M", "Ingrese el número de ciudades (M) primero.")
            return

        ciudades_actuales = self.listbox.get(0, tk.END)
        if len(ciudades_actuales) >= m_int:
            messagebox.showerror("Límite alcanzado",
                                 f"Ya agregó {m_int} ciudades (el máximo definido).")
            return

        try:
            x_int = int(x_str)
            y_int = int(y_str)
        except ValueError:
            messagebox.showerror("Error de formato", "X e Y deben ser números enteros.")
            return

        n_str = self.entry_n.get().strip()
        try:
            n_int = int(n_str)
        except ValueError:
            messagebox.showerror("Falta N", "Ingrese el tamaño N de la cuadrícula primero.")
            return

        if not (0 <= x_int <= n_int):
            messagebox.showerror("Fuera de rango", f"X={x_int} debe estar entre 0 y {n_int}.")
            return
        if not (0 <= y_int <= n_int):
            messagebox.showerror("Fuera de rango", f"Y={y_int} debe estar entre 0 y {n_int}.")
            return

        for ciudad in ciudades_actuales:
            partes = ciudad.split()
            if partes[0] == nombre:
                messagebox.showerror("Nombre duplicado",
                                     f"Ya existe una ciudad llamada '{nombre}'.")
                return
            if int(partes[1]) == x_int and int(partes[2]) == y_int:
                messagebox.showerror("Posición ocupada",
                                     f"Ya hay una ciudad en ({x_int}, {y_int}).")
                return

        # Agregar a la lista
        self.listbox.insert(tk.END, f"{nombre}  {x_int}  {y_int}")

        # Limpiar campos de entrada
        self.entry_nombre.delete(0, tk.END)
        self.entry_x.delete(0, tk.END)
        self.entry_y.delete(0, tk.END)
        self.entry_nombre.focus()

        # Bloquear N y M para que no cambien mientras hay ciudades cargadas
        self.entry_n.config(state='disabled')
        self.entry_m.config(state='disabled')

        # ── NUEVO: actualizar el mapa con la ciudad recién agregada ──
        self._actualizar_mapa()

    def eliminar_ciudad(self) -> None:
        """
        Elimina la ciudad seleccionada en la listbox.
        Después de eliminar, actualiza el mapa automáticamente.
        """
        seleccion = self.listbox.curselection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione una ciudad de la lista.")
            return

        self.listbox.delete(seleccion[0])

        # ── NUEVO: redibujar el mapa sin la ciudad eliminada ──────
        self._actualizar_mapa()

    def generar_minizinc(self) -> None:
        """
        Orquesta el flujo completo:
        1. Lee los datos de la interfaz.
        2. Parsea y valida.
        3. Genera el código MiniZinc.
        4. Muestra el código y cambia a la pestaña Código automáticamente.
        """
        # Construir texto de entrada desde la interfaz
        n_str = self.entry_n.get().strip()
        m_str = self.entry_m.get().strip()
        ciudades_raw = self.listbox.get(0, tk.END)

        texto_entrada = f"{n_str}\n{m_str}\n"
        for ciudad in ciudades_raw:
            partes = ciudad.split()
            texto_entrada += f"{partes[0]} {partes[1]} {partes[2]}\n"

        # Parsear
        n, ciudades, error_parseo = parse_input(texto_entrada)
        if error_parseo:
            messagebox.showerror("Error en los datos", error_parseo)
            return

        # Validar
        errores = validar_datos(n, ciudades)
        if hay_errores(errores):
            messagebox.showerror("Errores de validación",
                                 "Corrija estos problemas:\n\n" + "\n".join(errores))
            return

        # Generar código MiniZinc
        codigo = generar_codigo_minizinc({"n": n, "ciudades": ciudades})

        # Mostrar código en el área de texto
        self.area_codigo.establecer_texto(codigo)

        # ── NUEVO: cambiar automáticamente a la pestaña Código ────
        self.notebook.select(self.tab_codigo)

    def limpiar_todo(self) -> None:
        """Borra todos los campos y resetea la interfaz al estado inicial."""
        self.entry_n.config(state='normal')
        self.entry_m.config(state='normal')

        self.entry_n.delete(0, tk.END)
        self.entry_m.delete(0, tk.END)
        self.entry_nombre.delete(0, tk.END)
        self.entry_x.delete(0, tk.END)
        self.entry_y.delete(0, tk.END)
        self.listbox.delete(0, tk.END)

        # ── NUEVO: limpiar el mapa ────────────────────────────────
        self.mapa.limpiar()

        # Restaurar texto placeholder en el área de código
        self.area_codigo.establecer_texto(
            "% El código MiniZinc aparecerá aquí\n"
            "% después de presionar 'Generar MiniZinc'.\n"
        )

    # ─────────────────────────────────────────
    # Método de sincronización con el mapa
    # ─────────────────────────────────────────

    def _actualizar_mapa(self) -> None:
        """
        Lee el estado actual de la interfaz (N y la lista de ciudades)
        y le pide al widget MapaCiudades que redibuje el mapa.

        Se llama automáticamente después de agregar o eliminar una ciudad.
        """
        # Leer N del campo de entrada
        n_str = self.entry_n.get().strip()
        try:
            n = int(n_str)
        except ValueError:
            return  # N no está definido todavía, no hay nada que dibujar

        # Construir la lista de ciudades desde la listbox
        ciudades = []
        for ciudad_str in self.listbox.get(0, tk.END):
            partes = ciudad_str.split()
            nombre = partes[0]
            x = int(partes[1])
            y = int(partes[2])
            ciudades.append((nombre, x, y))

        # Ordenarle al widget del mapa que redibuje
        self.mapa.dibujar_mapa(n, ciudades)

    # ─────────────────────────────────────────
    # Limpieza de placeholders
    # ─────────────────────────────────────────

    def _limpiar_placeholder_nombre(self, event) -> None:
        if self.entry_nombre.get() == "Nombre":
            self.entry_nombre.delete(0, tk.END)

    def _limpiar_placeholder_x(self, event) -> None:
        if self.entry_x.get() == "X":
            self.entry_x.delete(0, tk.END)

    def _limpiar_placeholder_y(self, event) -> None:
        if self.entry_y.get() == "Y":
            self.entry_y.delete(0, tk.END)


# ─────────────────────────────────────────────
# Función de arranque
# ─────────────────────────────────────────────

def construir_ventana() -> None:
    """Crea e inicia el loop principal de la interfaz gráfica."""
    app = VentanaPrincipal()
    app.mainloop()


if __name__ == "__main__":
    construir_ventana()
