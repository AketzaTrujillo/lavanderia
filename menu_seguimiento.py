"""
Módulo para integrar el seguimiento de pedidos con el menú principal.
Este módulo se debe importar desde admin_view.py o cajero_view.py para agregar
la opción de seguimiento de pedidos.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import utileria as utl

# Asegurar que podamos importar los módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)


def agregar_opcion_seguimiento(admin_view):
    """
    Agrega la opción de seguimiento de pedidos al panel de administrador.

    Args:
        admin_view: Instancia de MasterPanel o CajeroPanel
    """
    try:
        from seguimiento_pedidos import SeguimientoPedidos

        def abrir_seguimiento():
            SeguimientoPedidos(admin_view.ventana)

        # Modificar la función para abrir el seguimiento
        return abrir_seguimiento
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el módulo de seguimiento: {str(e)}")
        return None


def modificar_admin_view():
    """
    Modifica el MasterPanel para agregar la opción de seguimiento de pedidos.
    Esta función debe ser llamada desde admin_view.py.
    """
    try:
        # Importar el módulo
        from admin_view import MasterPanel

        # Guardar la función original
        original_construir_interfaz = MasterPanel.construir_interfaz

        # Definir la nueva función
        def nueva_construir_interfaz(self):
            # Llamar a la función original
            original_construir_interfaz(self)

            # Agregar el botón de seguimiento
            frame_principal = self.ventana.winfo_children()[0]  # Obtener el frame principal

            # Buscar el frame de botones
            for child in frame_principal.winfo_children():
                if isinstance(child, tk.Frame) and len(child.winfo_children()) > 0:
                    # Este podría ser el frame de botones
                    botones_frame = child
                    break

            # Agregar un nuevo botón
            frame_boton = tk.Frame(
                botones_frame,
                bg="#f5f5f5",
                padx=10,
                pady=10
            )
            frame_boton.grid(
                row=3,  # Nueva fila
                column=0,  # Primera columna
                padx=20,
                pady=20,
                sticky="nsew"
            )

            # Crear el botón con el mismo estilo que los demás
            b = tk.Button(
                frame_boton,
                text="📊 Seguimiento Pedidos",
                font=("Helvetica", 14),
                bg="#3a7ff6",
                fg="white",
                width=20,
                height=2,
                cursor="hand2",
                command=agregar_opcion_seguimiento(self),
                relief=tk.RAISED,
                bd=1
            )
            b.pack(fill=tk.BOTH, expand=True)

            # Efecto hover
            b.bind("<Enter>", lambda e, btn=b: self.on_hover(btn, "#3a7ff6"))
            b.bind("<Leave>", lambda e, btn=b: self.on_leave(btn, "#3a7ff6"))

        # Reemplazar la función original
        MasterPanel.construir_interfaz = nueva_construir_interfaz

        return True
    except Exception as e:
        print(f"Error al modificar admin_view: {e}")
        return False


def modificar_cajero_view():
    """
    Modifica el CajeroPanel para agregar la opción de seguimiento de pedidos.
    Esta función debe ser llamada desde cajero_view.py.
    """
    try:
        # Importar el módulo
        from cajero_view import CajeroPanel

        # Guardar la función original
        original_construir_interfaz = CajeroPanel.construir_interfaz

        # Definir la nueva función
        def nueva_construir_interfaz(self):
            # Llamar a la función original
            original_construir_interfaz(self)

            # Agregar el botón de seguimiento
            frame_principal = self.ventana.winfo_children()[0]  # Obtener el frame principal

            # Buscar el frame de botones
            for child in frame_principal.winfo_children():
                if isinstance(child, tk.Frame) and len(child.winfo_children()) > 0:
                    # Este podría ser el frame de botones
                    botones_frame = child
                    break

            # Agregar un nuevo botón
            frame_boton = tk.Frame(
                botones_frame,
                bg="#e0f7fa",
                padx=10,
                pady=10
            )
            frame_boton.grid(
                row=2,  # Nueva fila
                column=0,  # Primera columna
                padx=20,
                pady=20,
                sticky="nsew"
            )

            # Crear el botón con el mismo estilo que los demás
            b = tk.Button(
                frame_boton,
                text="📊 Seguimiento Pedidos",
                font=("Helvetica", 14),
                bg="#00796b",
                fg="white",
                width=20,
                height=3,
                cursor="hand2",
                command=agregar_opcion_seguimiento(self),
                relief=tk.RAISED,
                bd=1
            )
            b.pack(fill=tk.BOTH, expand=True)

            # Efecto hover
            b.bind("<Enter>", lambda e, btn=b: self.on_hover(btn, "#00796b"))
            b.bind("<Leave>", lambda e, btn=b: self.on_leave(btn, "#00796b"))

        # Reemplazar la función original
        CajeroPanel.construir_interfaz = nueva_construir_interfaz

        return True
    except Exception as e:
        print(f"Error al modificar cajero_view: {e}")
        return False


# Para pruebas
if __name__ == "__main__":
    print("Este módulo debe ser importado desde admin_view.py o cajero_view.py")