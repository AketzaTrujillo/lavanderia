"""
Panel de Administrador para el Sistema de Gestión de Lavandería
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import utileria as utl


# Asegurar que podamos importar los módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

class MasterPanel:
    """Clase que implementa el panel principal de administrador"""

    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Panel de Administrador - Lavandería")
        self.ventana.geometry("800x600")
        self.ventana.config(bg="#f5f5f5")
        self.ventana.resizable(False, False)

        # Centrar ventana
        utl.centrar_ventana(self.ventana, 800, 600)

        # Establecer ícono si existe
        try:
            if os.path.exists("Img/lavadora.ico"):
                self.ventana.iconbitmap("Img/lavadora.ico")
        except Exception:
            pass  # Si no se puede cargar el ícono, continuar sin él

        self.construir_interfaz()

        self.ventana.mainloop()

    def construir_interfaz(self):
        """Construye la interfaz gráfica del panel"""
        # Frame principal con padding
        frame_principal = tk.Frame(self.ventana, bg="#f5f5f5", padx=30, pady=30)
        frame_principal.pack(fill=tk.BOTH, expand=True)

        # Título con estilo
        titulo_frame = tk.Frame(frame_principal, bg="#f5f5f5")
        titulo_frame.pack(fill=tk.X, pady=(0, 30))

        titulo = tk.Label(
            titulo_frame,
            text="PANEL DE ADMINISTRACIÓN",
            font=("Helvetica", 24, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        )
        titulo.pack()

        subtitulo = tk.Label(
            titulo_frame,
            text="Sistema de Gestión de Lavandería",
            font=("Helvetica", 14),
            bg="#f5f5f5",
            fg="#666a88"
        )
        subtitulo.pack(pady=(5, 0))

        # Separador
        separador = ttk.Separator(frame_principal, orient="horizontal")
        separador.pack(fill=tk.X, pady=(0, 20))

        # Frame para botones con 2 columnas
        botones_frame = tk.Frame(frame_principal, bg="#f5f5f5")
        botones_frame.pack(fill=tk.BOTH, expand=True)

        # Configurar grid de 2 columnas
        botones_frame.columnconfigure(0, weight=1)
        botones_frame.columnconfigure(1, weight=1)

        # Definir botones con iconos y mejores estilos
        botones = [
            {
                "texto": "Gestionar Usuarios",
                "comando": self.gestionar_usuarios,
                "icono": "👤",
                "fila": 0,
                "columna": 0
            },
            {
                "texto": "Gestionar Productos",
                "comando": self.gestionar_productos,
                "icono": "📦",
                "fila": 0,
                "columna": 1
            },
            {
                "texto": "Gestionar Clientes",
                "comando": self.gestionar_clientes,
                "icono": "👥",
                "fila": 1,
                "columna": 0
            },
            {
                "texto": "Gestionar Pedidos",
                "comando": self.gestionar_pedidos,
                "icono": "📋",
                "fila": 1,
                "columna": 1
            },
            {
                "texto": "Registrar Ventas",
                "comando": self.registrar_ventas,
                "icono": "💰",
                "fila": 2,
                "columna": 0
            },
            {
                "texto": "Cerrar Sesión",
                "comando": self.salir,
                "icono": "🚪",
                "fila": 2,
                "columna": 1,
                "es_salir": True
            }
        ]

        # Crear los botones con mejor estilo
        for boton in botones:
            frame_boton = tk.Frame(
                botones_frame,
                bg="#f5f5f5",
                padx=10,
                pady=10
            )
            frame_boton.grid(
                row=boton["fila"],
                column=boton["columna"],
                padx=20,
                pady=20,
                sticky="nsew"
            )

            # Color basado en si es botón de salida
            color_bg = "#e53935" if boton.get("es_salir", False) else "#3a7ff6"

            # Crear el botón con icono y texto
            b = tk.Button(
                frame_boton,
                text=f"{boton['icono']} {boton['texto']}",
                font=("Helvetica", 14),
                bg=color_bg,
                fg="white",
                width=20,
                height=2,
                cursor="hand2",
                command=boton["comando"],
                relief=tk.RAISED,
                bd=1
            )
            b.pack(fill=tk.BOTH, expand=True)

            # Efecto hover
            b.bind("<Enter>", lambda e, btn=b, c=color_bg: self.on_hover(btn, c))
            b.bind("<Leave>", lambda e, btn=b, c=color_bg: self.on_leave(btn, c))

        # Pie de página
        pie_frame = tk.Frame(frame_principal, bg="#f5f5f5")
        pie_frame.pack(fill=tk.X, pady=(20, 0))

        pie_texto = tk.Label(
            pie_frame,
            text="Sistema de Lavandería v1.0 | Desarrollado con ❤",
            font=("Helvetica", 8),
            bg="#f5f5f5",
            fg="#666a88"
        )
        pie_texto.pack(side=tk.RIGHT)

    def on_hover(self, button, color):
        """Efecto al pasar el mouse sobre el botón"""
        button.config(
            bg=self.adjust_color_brightness(color, 1.1),  # Aclarar el color
            relief=tk.RIDGE
        )

    def on_leave(self, button, color):
        """Efecto al quitar el mouse del botón"""
        button.config(
            bg=color,
            relief=tk.RAISED
        )

    def adjust_color_brightness(self, hex_color, factor):
        """Ajusta el brillo de un color hexadecimal"""
        # Convertir HEX a RGB
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        # Ajustar brillo
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))

        # Convertir de nuevo a HEX
        return f"#{r:02x}{g:02x}{b:02x}"

    # Funciones para abrir módulos
    def gestionar_usuarios(self):
        """Abre la ventana de gestión de usuarios"""
        try:
            # Importar justo cuando se necesita para evitar errores de importación circular
            from gestionar_usuarios import GestionUsuarios
            GestionUsuarios(self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo: {str(e)}")

    def gestionar_productos(self):
        """Abre la ventana de gestión de productos"""
        try:
            # Importar justo cuando se necesita
            from gestionar_productos import GestionProductos
            GestionProductos(self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo: {str(e)}")

    def gestionar_clientes(self):
        """Abre la ventana de gestión de clientes"""
        try:
            # Importar justo cuando se necesita
            from clientes import GestionClientes
            GestionClientes(self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo: {str(e)}")

    def gestionar_pedidos(self):
        """Abre la ventana de gestión de pedidos"""
        try:
            # Importar justo cuando se necesita
            from pedidos import Pedidos
            Pedidos(self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo: {str(e)}")

    def registrar_ventas(self):
        """Abre la ventana de registro de ventas"""
        try:
            # Importar justo cuando se necesita
            from ventas import Ventas
            Ventas(self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo: {str(e)}")

    def salir(self):
        """Cierra la sesión y la ventana"""
        if messagebox.askyesno("Confirmar salida", "¿Estás seguro de que deseas cerrar sesión?"):
            self.ventana.destroy()
            # Reabrir la pantalla de login
            from loginP import App
            App()


# Para probar de forma independiente
if __name__ == "__main__":
    MasterPanel()