"""
Sistema de Gestión de Lavandería
Módulo principal que inicia la aplicación
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Asegurar que podamos importar módulos en cualquier directorio
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Intentar importar el login
try:
    from loginP import App
except ImportError:
    messagebox.showerror(
        "Error de importación", 
        "No se pudo cargar el módulo de inicio de sesión.\n"
        "Por favor, asegúrate de que todos los archivos del sistema estén completos."
    )
    sys.exit(1)

# Función principal que inicia la aplicación
def main():
    try:
        # Iniciar la aplicación con la pantalla de login
        App()
    except Exception as e:
        messagebox.showerror(
            "Error", 
            f"Ha ocurrido un error al iniciar la aplicación:\n{str(e)}\n\n"
            "Por favor, contacta al soporte técnico."
        )
        sys.exit(1)

# Punto de entrada para la aplicación
if __name__ == "__main__":
    main()