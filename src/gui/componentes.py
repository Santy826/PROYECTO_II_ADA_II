"""
componentes.py
--------------
Widgets reutilizables para la interfaz gráfica del proyecto.

Actualmente contiene:
    - AreaTextoCopiable: un cuadro de texto con scroll y botón "Copiar".

El objetivo es mantener aquí los componentes que se usan en más
de una ventana, para no repetir código en cada lugar.
"""

import tkinter as tk
from tkinter import messagebox


class AreaTextoCopiable(tk.Frame):
    """
    Widget compuesto: un área de texto con scroll vertical
    y un botón para copiar el contenido al portapapeles.

    Uso típico:
        area = AreaTextoCopiable(ventana, titulo="Código MiniZinc")
        area.pack(fill='both', expand=True)
        area.establecer_texto("var int: x;\\nsolve satisfy;")
    """

    def __init__(self, padre, titulo: str = "Resultado", **kwargs):
        """
        Inicializa el widget.

        Parámetros:
            padre  : widget padre de tkinter.
            titulo : texto que aparece como etiqueta sobre el área.
            **kwargs: argumentos adicionales para tk.Frame.
        """
        super().__init__(padre, **kwargs)

        # Etiqueta superior
        tk.Label(
            self,
            text=titulo,
            font=("Arial", 10, "bold")
        ).pack(anchor='w', padx=5, pady=(5, 0))

        # Marco para texto + scrollbar
        marco_texto = tk.Frame(self)
        marco_texto.pack(fill='both', expand=True, padx=5)

        # Scrollbar vertical
        scrollbar = tk.Scrollbar(marco_texto)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Área de texto (solo lectura para que el usuario no modifique el código)
        self.texto = tk.Text(
            marco_texto,
            wrap='none',               # sin ajuste de línea (el código MiniZinc no debe partirse)
            yscrollcommand=scrollbar.set,
            font=("Courier", 9),       # fuente monoespaciada, apropiada para código
            state='disabled',          # solo lectura por defecto
            bg="#f8f8f8",
            relief='sunken'
        )
        self.texto.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=self.texto.yview)

        # Botón para copiar
        tk.Button(
            self,
            text="📋 Copiar al portapapeles",
            command=self._copiar_al_portapapeles,
            bg="#2196F3",
            fg="white",
            font=("Arial", 9, "bold")
        ).pack(pady=5)

    def establecer_texto(self, contenido: str) -> None:
        """
        Reemplaza el contenido del área de texto.

        Habilita temporalmente la edición, actualiza el contenido
        y vuelve a poner el texto en modo solo lectura.

        Parámetros:
            contenido (str): el texto a mostrar (por ejemplo, código MiniZinc).
        """
        self.texto.config(state='normal')       # habilitar para escribir
        self.texto.delete("1.0", tk.END)         # borrar contenido anterior
        self.texto.insert(tk.END, contenido)     # insertar nuevo contenido
        self.texto.config(state='disabled')      # volver a solo lectura

    def obtener_texto(self) -> str:
        """
        Retorna el contenido actual del área de texto.

        Retorna:
            str: el texto completo del área.
        """
        return self.texto.get("1.0", tk.END)

    def _copiar_al_portapapeles(self) -> None:
        """
        Copia el contenido del área al portapapeles del sistema.
        Muestra un mensaje de confirmación al usuario.
        """
        contenido = self.obtener_texto().strip()
        if not contenido:
            messagebox.showwarning("Vacío", "No hay código para copiar todavía.")
            return

        # Limpiar portapapeles y escribir el nuevo contenido
        self.clipboard_clear()
        self.clipboard_append(contenido)
        messagebox.showinfo("¡Copiado!", "El código MiniZinc fue copiado al portapapeles.")
