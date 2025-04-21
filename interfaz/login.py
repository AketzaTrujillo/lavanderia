"""
Sistema de inicio de sesión para la aplicación de Lavandería
Con diseño mejorado y consistente con el resto de módulos
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import sys
import utileria as utl

# Asegurar que podamos importar los módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Importar módulos del sistema
try:
    from conexion import conectar_bd
    from email_sender import enviar_codigo
except ImportError as e:
    print(f"Error al importar módulos: {e}")


class App:
    """Clase principal para la pantalla de inicio de sesión"""

    def __init__(self):
        # Configuración de la ventana principal
        self.ventana = tk.Tk()
        self.ventana.title('Sistema de Lavandería - Inicio de sesión')
        self.ventana.geometry('800x500')
        self.ventana.config(bg='#f5f5f5')
        self.ventana.resizable(width=0, height=0)