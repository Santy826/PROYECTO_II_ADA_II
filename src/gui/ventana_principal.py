"""Ventana principal de la interfaz gráfica."""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Añadir el path al sistema para permitir la importación de src si corremos el archivo directamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.parser_entrada import parse_input, validate_input

class VentanaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Validador de Entrada - Optimizador de Conciertos")
        self.geometry("500x480")
        
        # --- TAMAÑO DE CUADRÍCULA ---
        tk.Label(self, text="1. Tamaño de la cuadrícula (N):", font=("Arial", 10, "bold")).pack(pady=(10, 0), anchor='w', padx=10)
        self.entry_n = tk.Entry(self)
        self.entry_n.pack(fill='x', padx=10)
        
        # --- NÚMERO DE CIUDADES ---
        tk.Label(self, text="2. Número de ciudades (M):", font=("Arial", 10, "bold")).pack(pady=(10, 0), anchor='w', padx=10)
        self.entry_m = tk.Entry(self)
        self.entry_m.pack(fill='x', padx=10)
        
        # --- AÑADIR CIUDAD ---
        tk.Label(self, text="3. Añadir Ciudad (Nombre, X, Y):", font=("Arial", 10, "bold")).pack(pady=(10, 0), anchor='w', padx=10)
        frame_city = tk.Frame(self)
        frame_city.pack(fill='x', padx=10)
        
        self.entry_name = tk.Entry(frame_city, width=15)
        self.entry_name.pack(side=tk.LEFT, padx=2)
        
        self.entry_x = tk.Entry(frame_city, width=5)
        self.entry_x.pack(side=tk.LEFT, padx=2)
        
        self.entry_y = tk.Entry(frame_city, width=5)
        self.entry_y.pack(side=tk.LEFT, padx=2)
        
        # Placeholders
        self.entry_name.insert(0, "Nombre")
        self.entry_x.insert(0, "X")
        self.entry_y.insert(0, "Y")
        
        # Limpiar al hacer click
        self.entry_name.bind("<FocusIn>", lambda e: self.entry_name.delete(0, 'end') if self.entry_name.get() == "Nombre" else None)
        self.entry_x.bind("<FocusIn>", lambda e: self.entry_x.delete(0, 'end') if self.entry_x.get() == "X" else None)
        self.entry_y.bind("<FocusIn>", lambda e: self.entry_y.delete(0, 'end') if self.entry_y.get() == "Y" else None)
        
        tk.Button(frame_city, text="Agregar", command=self.agregar_ciudad).pack(side=tk.LEFT, padx=5)
        
        # --- LISTADO DE CIUDADES ---
        tk.Label(self, text="Ciudades Registradas:", font=("Arial", 10, "bold")).pack(pady=(10, 0), anchor='w', padx=10)
        self.listbox = tk.Listbox(self, height=8)
        self.listbox.pack(fill='both', padx=10, pady=5, expand=True)
        
        # --- BOTONES DE ACCIÓN ---
        frame_actions = tk.Frame(self)
        frame_actions.pack(pady=10)
        btn_validar = tk.Button(frame_actions, text="Validar y Procesar Datos", command=self.validar_todo, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        btn_validar.pack(side=tk.LEFT, padx=5, ipady=3, ipadx=5)
        
        tk.Button(frame_actions, text="Limpiar", command=self.limpiar).pack(side=tk.LEFT, padx=5)

    def agregar_ciudad(self):
        name = self.entry_name.get().strip()
        x = self.entry_x.get().strip()
        y = self.entry_y.get().strip()
        
        if name in ["Nombre", ""] or x in ["X", ""] or y in ["Y", ""]:
            messagebox.showwarning("Campos Incompletos", "Por favor ingrese un Nombre, una coordenada X y una Y válidas.")
            return
            
        # Validar que exista el número de ciudades (M) y no se haya superado
        m_text = self.entry_m.get().strip()
        try:
            m_int = int(m_text)
        except ValueError:
            messagebox.showerror("Falta Número", "Por favor ingrese un número de ciudades (M) válido antes de agregar.")
            return
            
        ciudades_actuales = self.listbox.get(0, tk.END)
        if len(ciudades_actuales) >= m_int:
            messagebox.showerror("Límite de Ciudades Alcanzado", f"Ya se han agregado las {m_int} ciudades establecidas.")
            return

        # Validar que X e Y sean enteros
        try:
            x_int = int(x)
            y_int = int(y)
        except ValueError:
            messagebox.showerror("Error de formato", "Las coordenadas X e Y deben ser números enteros válidos.")
            return
            
        # Validar que exista el tamaño de la cuadrícula (N)
        n_text = self.entry_n.get().strip()
        try:
            n_int = int(n_text)
        except ValueError:
            messagebox.showerror("Falta Cuadrícula", "Por favor ingrese un tamaño de cuadrícula (N) válido antes de agregar ciudades.")
            return
            
        # Validar límites de la cuadrícula
        if x_int < 0 or x_int > n_int:
            messagebox.showerror("Límites Excedidos", f"La coordenada X={x_int} supera el límite de la cuadrícula [0, {n_int}].")
            return
            
        if y_int < 0 or y_int > n_int:
            messagebox.showerror("Límites Excedidos", f"La coordenada Y={y_int} supera el límite de la cuadrícula [0, {n_int}].")
            return
            
        # Validar nombres duplicados y posiciones ocupadas en la interfaz
        for ciudad in ciudades_actuales:
            partes = ciudad.split()
            if partes[0] == name:
                messagebox.showerror("Ciudad Duplicada", f"Ya existe una ciudad con el nombre '{name}'.")
                return
            if int(partes[1]) == x_int and int(partes[2]) == y_int:
                messagebox.showerror("Posición Ocupada", f"Ya existe una ciudad en la misma ubicación ({x_int}, {y_int}).")
                return
        
        self.listbox.insert(tk.END, f"{name} {x} {y}")
        self.entry_name.delete(0, tk.END)
        self.entry_x.delete(0, tk.END)
        self.entry_y.delete(0, tk.END)
        self.entry_name.focus()
        
        # Bloquear N y M después de agregar la primera ciudad
        self.entry_n.config(state='disabled')
        self.entry_m.config(state='disabled')

    def validar_todo(self):
        val_n = self.entry_n.get().strip()
        val_m = self.entry_m.get().strip()
        ciudades = self.listbox.get(0, tk.END)
        
        # Construimos el texto con el formato exigido por parser_entrada.py
        texto = f"{val_n}\n{val_m}\n"
        for c in ciudades:
            texto += f"{c}\n"
            
        # Utilizamos las funciones del parser para conectar en conjunto
        n, ciudades_parseadas, error_parseo = parse_input(texto)
        
        if error_parseo:
            messagebox.showerror("Error en Formato de Datos", error_parseo)
            return
            
        errores_validacion = validate_input(n, ciudades_parseadas)
        
        if errores_validacion:
            mensaje = "\n".join(errores_validacion)
            messagebox.showerror("Errores de Validación", f"Se encontraron problemas con la entrada:\n\n{mensaje}")
        else:
            messagebox.showinfo("Validación Exitosa", "Todos los datos son válidos.\n- Tipos de datos correctos\n- Respetan los límites de la cuadrícula\n- No hay ciudades duplicadas.\n\n¡Listos para pasar al modelo!")

    def limpiar(self):
        # Desbloquear N y M
        self.entry_n.config(state='normal')
        self.entry_m.config(state='normal')
        
        self.entry_n.delete(0, tk.END)
        self.entry_m.delete(0, tk.END)
        self.entry_name.delete(0, tk.END)
        self.entry_x.delete(0, tk.END)
        self.entry_y.delete(0, tk.END)
        self.listbox.delete(0, tk.END)
        

def construir_ventana():
    app = VentanaPrincipal()
    app.mainloop()

if __name__ == "__main__":
    construir_ventana()
