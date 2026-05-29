"""
ventana_principal.py
--------------------
Ventana principal de la aplicación "¿Dónde pongo mi concierto?".

Organiza la interfaz en dos áreas:
    - Panel izquierdo : ingreso de datos (dos modos: Formulario o Texto directo).
    - Panel derecho   : dos pestañas — Mapa de ciudades y Código MiniZinc.

Modos de ingreso de datos:
    - Formulario    : el usuario ingresa N, M y cada ciudad campo por campo.
                      El mapa se actualiza en tiempo real.
    - Texto directo : el usuario pega o escribe el texto completo en el formato
                      del enunciado (N / M / Ciudad X Y). Este es el modo que
                      describe el PDF del proyecto.

Flujo de uso (cualquier modo):
    1. El usuario ingresa los datos.
    2. Presiona "Generar MiniZinc".
    3. El sistema valida, genera el código y lo muestra en la pestaña Código.
    4. El usuario copia el código y lo pega en MiniZinc IDE.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.parser_entrada import parse_input
from src.core.validador_entrada import validar_datos, verificar_factibilidad, hay_errores
from src.core.generador_minizinc import generar_codigo_minizinc
from src.gui.componentes import AreaTextoCopiable
from src.gui.mapa_canvas import MapaCiudades


class VentanaPrincipal(tk.Tk):
    """Ventana principal de la aplicación."""

    def __init__(self):
        super().__init__()
        self.title("¿Dónde pongo mi concierto? — Generador MiniZinc")
        self.geometry("1050x620")
        self.resizable(True, True)
        self._construir_layout()

    # ─────────────────────────────────────────
    # Construcción del layout
    # ─────────────────────────────────────────

    def _construir_layout(self) -> None:
        """Construye título + los dos paneles principales."""

        tk.Label(
            self,
            text="¿Dónde pongo mi concierto?",
            font=("Arial", 14, "bold"),
            pady=7
        ).pack(fill='x')

        marco = tk.Frame(self)
        marco.pack(fill='both', expand=True, padx=10, pady=(0, 8))

        # ── Panel izquierdo ───────────────────────────────────────────
        panel_izq = tk.LabelFrame(
            marco,
            text=" Datos del problema ",
            font=("Arial", 10, "bold"),
            padx=8, pady=8,
            width=380
        )
        panel_izq.pack(side=tk.LEFT, fill='y', padx=(0, 6))
        panel_izq.pack_propagate(False)
        self._construir_panel_entrada(panel_izq)

        # ── Panel derecho ─────────────────────────────────────────────
        panel_der = tk.LabelFrame(
            marco,
            text=" Visualización ",
            font=("Arial", 10, "bold"),
            padx=6, pady=6
        )
        panel_der.pack(side=tk.LEFT, fill='both', expand=True)
        self._construir_panel_derecho(panel_der)

    def _construir_panel_entrada(self, padre) -> None:
        """
        Construye el panel izquierdo con dos pestañas de ingreso:
            - Formulario    : entrada campo por campo.
            - Texto directo : entrada pegando el texto completo del enunciado.

        Los botones de acción (Generar / Limpiar) quedan fuera de las pestañas
        para estar siempre visibles sin importar qué pestaña esté activa.
        """
        # Notebook de modos de entrada
        self.notebook_entrada = ttk.Notebook(padre)
        self.notebook_entrada.pack(fill='both', expand=True, pady=(0, 8))

        # ── Pestaña 1: Formulario ─────────────────────────────────────
        tab_form = tk.Frame(self.notebook_entrada, padx=4, pady=4)
        self.notebook_entrada.add(tab_form, text="  📝 Formulario  ")
        self._construir_tab_formulario(tab_form)

        # ── Pestaña 2: Texto directo ──────────────────────────────────
        tab_texto = tk.Frame(self.notebook_entrada, padx=4, pady=4)
        self.notebook_entrada.add(tab_texto, text="  📋 Texto directo  ")
        self._construir_tab_texto(tab_texto)

        # ── Botones de acción (fuera del notebook) ────────────────────
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

    def _construir_tab_formulario(self, padre) -> None:
        """Construye la pestaña de ingreso campo por campo."""

        tk.Label(padre, text="Tamaño de la cuadrícula (N):",
                 font=("Arial", 9, "bold")).pack(anchor='w', pady=(4, 2))
        self.entry_n = tk.Entry(padre, width=10)
        self.entry_n.pack(anchor='w', pady=(0, 8))

        tk.Label(padre, text="Número de ciudades (M):",
                 font=("Arial", 9, "bold")).pack(anchor='w', pady=(0, 2))
        self.entry_m = tk.Entry(padre, width=10)
        self.entry_m.pack(anchor='w', pady=(0, 8))

        tk.Label(padre, text="Agregar ciudad (Nombre  X  Y):",
                 font=("Arial", 9, "bold")).pack(anchor='w', pady=(0, 2))

        fila = tk.Frame(padre)
        fila.pack(anchor='w', pady=(0, 4))

        self.entry_nombre = tk.Entry(fila, width=11)
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

        tk.Label(padre, text="Ciudades registradas:",
                 font=("Arial", 9, "bold")).pack(anchor='w', pady=(4, 2))
        self.listbox = tk.Listbox(padre, height=7, font=("Courier", 9))
        self.listbox.pack(fill='x', pady=(0, 4))

        tk.Button(
            padre, text="Eliminar ciudad seleccionada",
            command=self.eliminar_ciudad,
            bg="#f44336", fg="white", font=("Arial", 8)
        ).pack(anchor='w')

    def _construir_tab_texto(self, padre) -> None:
        """
        Construye la pestaña de texto directo.

        El usuario pega aquí la entrada completa en el formato del enunciado:
            N
            M
            Ciudad1 X1 Y1
            Ciudad2 X2 Y2
            ...

        Las líneas en blanco se ignoran automáticamente.
        Los nombres de ciudad pueden tener espacios (ej: "Santa Marta 5 3").
        """
        # Instrucciones con el formato esperado
        tk.Label(
            padre,
            text="Pega o escribe la entrada en el formato del enunciado:",
            font=("Arial", 9, "bold"),
            anchor='w'
        ).pack(fill='x', pady=(4, 2))

        tk.Label(
            padre,
            text="N\nM\nCiudad1 X1 Y1\nCiudad2 X2 Y2\n...",
            font=("Courier", 8),
            fg="#555555",
            justify='left',
            bg="#F5F5F5",
            relief='groove',
            padx=6, pady=4
        ).pack(fill='x', pady=(0, 6))

        # Área de texto con scrollbar
        marco_texto = tk.Frame(padre)
        marco_texto.pack(fill='both', expand=True)

        scrollbar = tk.Scrollbar(marco_texto)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_entrada_directa = tk.Text(
            marco_texto,
            yscrollcommand=scrollbar.set,
            font=("Courier", 10),
            wrap='none',
            relief='sunken',
            bg="#FAFFFE"
        )
        self.text_entrada_directa.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=self.text_entrada_directa.yview)

        # Texto de ejemplo como placeholder
        self._establecer_ejemplo_textarea()

        # Limpiar el placeholder al hacer clic por primera vez
        self.text_entrada_directa.bind("<FocusIn>", self._limpiar_placeholder_textarea)
        self._textarea_tiene_placeholder = True

    def _construir_panel_derecho(self, padre) -> None:
        """Construye el panel derecho: pestaña Mapa y pestaña Código."""
        self.notebook = ttk.Notebook(padre)
        self.notebook.pack(fill='both', expand=True)

        # Pestaña: Mapa
        tab_mapa = tk.Frame(self.notebook)
        self.notebook.add(tab_mapa, text="  🗺  Mapa de ciudades  ")
        self.mapa = MapaCiudades(tab_mapa)
        self.mapa.pack(fill='both', expand=True)

        # Pestaña: Código MiniZinc
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
    # Acciones del formulario
    # ─────────────────────────────────────────

    def agregar_ciudad(self) -> None:
        """Lee los campos y agrega la ciudad a la lista. Actualiza el mapa."""
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
            messagebox.showerror("Fuera de rango",
                                 f"X={x_int} debe estar entre 0 y {n_int}.")
            return
        if not (0 <= y_int <= n_int):
            messagebox.showerror("Fuera de rango",
                                 f"Y={y_int} debe estar entre 0 y {n_int}.")
            return

        for ciudad in ciudades_actuales:
            partes = ciudad.split()
            # En el formulario los nombres no tienen espacios,
            # por lo que partes[0] es siempre el nombre completo.
            if partes[0] == nombre:
                messagebox.showerror("Nombre duplicado",
                                     f"Ya existe una ciudad llamada '{nombre}'.")
                return
            if int(partes[1]) == x_int and int(partes[2]) == y_int:
                messagebox.showerror("Posición ocupada",
                                     f"Ya hay una ciudad en ({x_int}, {y_int}).")
                return

        self.listbox.insert(tk.END, f"{nombre}  {x_int}  {y_int}")

        self.entry_nombre.delete(0, tk.END)
        self.entry_x.delete(0, tk.END)
        self.entry_y.delete(0, tk.END)
        self.entry_nombre.focus()

        # Bloquear N y M para que no cambien mientras hay ciudades
        self.entry_n.config(state='disabled')
        self.entry_m.config(state='disabled')

        self._actualizar_mapa_desde_formulario()

    def eliminar_ciudad(self) -> None:
        """Elimina la ciudad seleccionada. Actualiza el mapa."""
        seleccion = self.listbox.curselection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione una ciudad de la lista.")
            return
        self.listbox.delete(seleccion[0])
        self._actualizar_mapa_desde_formulario()

    # ─────────────────────────────────────────
    # Acción principal: generar código MiniZinc
    # ─────────────────────────────────────────

    def generar_minizinc(self) -> None:
        """
        Detecta el modo activo (Formulario o Texto directo), obtiene los datos
        del modo correspondiente y ejecuta el flujo completo de validación
        y generación de código MiniZinc.
        """
        # Detectar qué pestaña de entrada está activa (0 = Formulario, 1 = Texto)
        modo = self.notebook_entrada.index(self.notebook_entrada.select())

        if modo == 0:
            texto_entrada = self._construir_texto_desde_formulario()
        else:
            texto_entrada = self._leer_texto_directo()

        if texto_entrada is None:
            return  # El modo ya mostró el error correspondiente

        # ── Parsear ───────────────────────────────────────────────────
        n, ciudades, error_parseo = parse_input(texto_entrada)
        if error_parseo:
            messagebox.showerror("Error al leer los datos", error_parseo)
            return

        # ── Validar ───────────────────────────────────────────────────
        errores = validar_datos(n, ciudades)
        if hay_errores(errores):
            messagebox.showerror(
                "Errores de validación",
                "Corrija estos problemas:\n\n" + "\n".join(errores)
            )
            return

        # ── Verificar factibilidad ────────────────────────────────────
        factibilidad = verificar_factibilidad(n, ciudades)

        if factibilidad["infactible"]:
            messagebox.showerror(
                "Problema sin solución (UNSATISFIABLE)",
                f"{factibilidad['mensaje_error']}\n\n"
                f"Posiciones totales: {factibilidad['total_posiciones']}\n"
                f"Ciudades ingresadas: {len(ciudades)}\n"
                f"Posiciones libres: {factibilidad['posiciones_libres']}"
            )
            return

        if factibilidad["advertencia"]:
            continuar = messagebox.askyesno(
                "Advertencia — espacio muy reducido",
                f"{factibilidad['mensaje_advertencia']}\n\n"
                f"Posiciones totales: {factibilidad['total_posiciones']}\n"
                f"Ciudades ingresadas: {len(ciudades)}\n"
                f"Posiciones libres: {factibilidad['posiciones_libres']}\n\n"
                "¿Desea generar el código MiniZinc de todas formas?"
            )
            if not continuar:
                return

        # ── Si el modo es Texto directo, actualizar el mapa ──────────
        # En el formulario el mapa ya se actualiza en tiempo real.
        # En Texto directo lo actualizamos aquí, tras el parseo exitoso.
        if modo == 1:
            self.mapa.dibujar_mapa(n, ciudades)

        # ── Generar y mostrar código ──────────────────────────────────
        codigo = generar_codigo_minizinc({"n": n, "ciudades": ciudades})
        self.area_codigo.establecer_texto(codigo)
        self.notebook.select(self.tab_codigo)

    def limpiar_todo(self) -> None:
        """Resetea todos los campos y el estado visual de la aplicación."""
        # Formulario
        self.entry_n.config(state='normal')
        self.entry_m.config(state='normal')
        self.entry_n.delete(0, tk.END)
        self.entry_m.delete(0, tk.END)
        self.entry_nombre.delete(0, tk.END)
        self.entry_x.delete(0, tk.END)
        self.entry_y.delete(0, tk.END)
        self.listbox.delete(0, tk.END)

        # Texto directo
        self._establecer_ejemplo_textarea()
        self._textarea_tiene_placeholder = True

        # Mapa y código
        self.mapa.limpiar()
        self.area_codigo.establecer_texto(
            "% El código MiniZinc aparecerá aquí\n"
            "% después de presionar 'Generar MiniZinc'.\n"
        )

    # ─────────────────────────────────────────
    # Lectura de datos según el modo activo
    # ─────────────────────────────────────────

    def _construir_texto_desde_formulario(self) -> str | None:
        """
        Reconstruye el texto de entrada a partir del formulario.

        Retorna None si faltan datos (N o M no definidos), mostrando
        el error correspondiente.
        """
        n_str = self.entry_n.get().strip()
        m_str = self.entry_m.get().strip()
        ciudades_raw = self.listbox.get(0, tk.END)

        if not n_str:
            messagebox.showerror("Falta N", "Ingrese el tamaño N de la cuadrícula.")
            return None
        if not m_str:
            messagebox.showerror("Falta M", "Ingrese el número de ciudades M.")
            return None
        if not ciudades_raw:
            messagebox.showerror("Sin ciudades", "Agregue al menos una ciudad.")
            return None

        texto = f"{n_str}\n{m_str}\n"
        for ciudad in ciudades_raw:
            # La listbox guarda "nombre  x  y" (nombre sin espacios en modo formulario)
            partes = ciudad.split()
            texto += f"{partes[0]} {partes[1]} {partes[2]}\n"

        return texto

    def _leer_texto_directo(self) -> str | None:
        """
        Lee el contenido del TextArea.

        Retorna None si el área está vacía o solo tiene el placeholder.
        """
        if self._textarea_tiene_placeholder:
            messagebox.showwarning(
                "Sin datos",
                "Escribe o pega los datos del problema en el área de texto."
            )
            return None

        contenido = self.text_entrada_directa.get("1.0", tk.END).strip()
        if not contenido:
            messagebox.showwarning(
                "Sin datos",
                "El área de texto está vacía. "
                "Escribe o pega los datos del problema."
            )
            return None

        return contenido

    # ─────────────────────────────────────────
    # Sincronización del mapa (modo formulario)
    # ─────────────────────────────────────────

    def _actualizar_mapa_desde_formulario(self) -> None:
        """
        Redibuja el mapa con el estado actual del formulario.
        Solo se llama desde agregar_ciudad() y eliminar_ciudad().
        """
        n_str = self.entry_n.get().strip()
        try:
            n = int(n_str)
        except ValueError:
            return  # N todavía no está definido

        ciudades = []
        for ciudad_str in self.listbox.get(0, tk.END):
            partes = ciudad_str.split()
            ciudades.append((partes[0], int(partes[1]), int(partes[2])))

        self.mapa.dibujar_mapa(n, ciudades)

    # ─────────────────────────────────────────
    # Placeholder del TextArea
    # ─────────────────────────────────────────

    def _establecer_ejemplo_textarea(self) -> None:
        """Muestra el texto de ejemplo en el TextArea (placeholder visual)."""
        self.text_entrada_directa.config(state='normal')
        self.text_entrada_directa.delete("1.0", tk.END)
        self.text_entrada_directa.insert(tk.END,
            "12\n"
            "5\n"
            "Cali 2 3\n"
            "Palmira 10 2\n"
            "Buga 11 0\n"
            "Pradera 0 3\n"
            "Candelaria 1 2\n"
        )
        self.text_entrada_directa.config(fg="#AAAAAA")

    def _limpiar_placeholder_textarea(self, event) -> None:
        """Limpia el placeholder la primera vez que el usuario hace clic."""
        if self._textarea_tiene_placeholder:
            self.text_entrada_directa.delete("1.0", tk.END)
            self.text_entrada_directa.config(fg="black")
            self._textarea_tiene_placeholder = False

    # ─────────────────────────────────────────
    # Limpieza de placeholders del formulario
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
