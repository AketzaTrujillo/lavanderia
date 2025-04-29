"""
Panel de Cajero para el Sistema de Gestión de Lavandería
Versión actualizada con acceso a módulo de caja
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import utileria as utl

# Asegurar que podamos importar los módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

class CajeroPanel:
    """Clase que implementa el panel principal de cajero"""

    def __init__(self, id_usuario=None):
        self.ventana = tk.Tk()
        self.ventana.title("Panel de Cajero - Lavandería")
        self.ventana.geometry("800x600")
        self.ventana.config(bg="#e0f7fa")
        self.ventana.resizable(False, False)

        # ID del usuario actual (para registrar operaciones)
        self.id_usuario = id_usuario

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
        frame_principal = tk.Frame(self.ventana, bg="#e0f7fa", padx=30, pady=30)
        frame_principal.pack(fill=tk.BOTH, expand=True)

        # Título con estilo
        titulo_frame = tk.Frame(frame_principal, bg="#e0f7fa")
        titulo_frame.pack(fill=tk.X, pady=(0, 30))

        titulo = tk.Label(
            titulo_frame,
            text="PANEL DE CAJERO",
            font=("Helvetica", 24, "bold"),
            bg="#e0f7fa",
            fg="#00796b"
        )
        titulo.pack()

        subtitulo = tk.Label(
            titulo_frame,
            text="Sistema de Gestión de Lavandería",
            font=("Helvetica", 14),
            bg="#e0f7fa",
            fg="#00796b"
        )
        subtitulo.pack(pady=(5, 0))

        # Separador
        separador = ttk.Separator(frame_principal, orient="horizontal")
        separador.pack(fill=tk.X, pady=(0, 20))

        # Frame para botones con distribución en cuadrícula
        botones_frame = tk.Frame(frame_principal, bg="#e0f7fa")
        botones_frame.pack(fill=tk.BOTH, expand=True)

        # Configurar grid de 2 columnas
        botones_frame.columnconfigure(0, weight=1)
        botones_frame.columnconfigure(1, weight=1)

        # Definir botones con iconos y mejores estilos
        botones = [
            {
                "texto": "Registrar Pedido",
                "comando": self.registrar_pedido,
                "icono": "📋",
                "fila": 0,
                "columna": 0
            },
            {
                "texto": "Gestionar Clientes",
                "comando": self.gestionar_clientes,
                "icono": "👥",
                "fila": 0,
                "columna": 1
            },
            {
                "texto": "Registrar Venta",
                "comando": self.registrar_venta,
                "icono": "💰",
                "fila": 1,
                "columna": 0
            },
            {
                "texto": "Gestionar Caja",
                "comando": self.gestionar_caja,
                "icono": "💵",
                "fila": 1,
                "columna": 1
            },
            {
                "texto": "Cerrar Sesión",
                "comando": self.salir,
                "icono": "🚪",
                "fila": 2,
                "columna": 0,
                "es_salir": True
            }
        ]

        # Crear los botones con mejor estilo
        for boton in botones:
            frame_boton = tk.Frame(
                botones_frame,
                bg="#e0f7fa",
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
            color_bg = "#e53935" if boton.get("es_salir", False) else "#00796b"

            # Crear el botón con icono y texto
            b = tk.Button(
                frame_boton,
                text=f"{boton['icono']} {boton['texto']}",
                font=("Helvetica", 14),
                bg=color_bg,
                fg="white",
                width=20,
                height=3,
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
        pie_frame = tk.Frame(frame_principal, bg="#e0f7fa")
        pie_frame.pack(fill=tk.X, pady=(20, 0))

        # Fecha y hora actual
        from datetime import datetime
        fecha_actual = datetime.now().strftime("%d/%m/%Y")

        fecha_lbl = tk.Label(
            pie_frame,
            text=f"Fecha: {fecha_actual}",
            font=("Helvetica", 10),
            bg="#e0f7fa",
            fg="#00796b"
        )
        fecha_lbl.pack(side=tk.LEFT)

        pie_texto = tk.Label(
            pie_frame,
            text="Sistema de Lavandería v1.0",
            font=("Helvetica", 10),
            bg="#e0f7fa",
            fg="#00796b"
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

    # Funciones para abrir módulos - Actualizadas con mejor manejo de errores
    def registrar_pedido(self):
        """Abre la ventana para registrar pedidos"""
        try:
            # Importación correcta del módulo de pedidos
            from pedidos import Pedidos
            Pedidos(self.ventana)  # Crear instancia de la clase Pedidos
        except ImportError:
            messagebox.showerror("Error de importación",
                                "No se pudo importar el módulo de pedidos.\n"
                                "Verifique que el archivo 'pedidos.py' existe.")
        except AttributeError as e:
            messagebox.showerror("Error de atributo",
                                f"Error en el módulo de pedidos: {str(e)}\n"
                                "Verifique que los métodos estén correctamente definidos.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo: {str(e)}")

    def gestionar_clientes(self):
        """Abre la ventana de gestión de clientes"""
        try:
            # Importar justo cuando se necesita
            from clientes import GestionClientes
            GestionClientes(self.ventana)
        except ImportError:
            messagebox.showerror("Error de importación",
                                "No se pudo importar el módulo de clientes.\n"
                                "Verifique que el archivo 'clientes.py' existe.")
        except AttributeError as e:
            messagebox.showerror("Error de atributo",
                                f"Error en el módulo de clientes: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo: {str(e)}")

    def registrar_venta(self):
        """Abre la ventana de registro de ventas"""
        try:
            # Importar justo cuando se necesita
            from ventas import Ventas
            Ventas(self.ventana)
        except ImportError:
            messagebox.showerror("Error de importación",
                                "No se pudo importar el módulo de ventas.\n"
                                "Verifique que el archivo 'ventas.py' existe.")
        except AttributeError as e:
            messagebox.showerror("Error de atributo",
                                f"Error en el módulo de ventas: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo: {str(e)}")

    def gestionar_caja(self):
        """Abre la ventana de gestión de caja"""
        try:
            # Importación del módulo de caja
            from caja import abrir_caja
            abrir_caja(self.ventana, self.id_usuario)
        except ImportError:
            messagebox.showerror("Error de importación",
                                "No se pudo importar el módulo de caja.\n"
                                "Verifique que el archivo 'caja.py' existe.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo de caja: {str(e)}")

    def salir(self):
        """Cierra la sesión y la ventana"""
        if messagebox.askyesno("Confirmar salida", "¿Estás seguro de que deseas cerrar sesión?"):
            self.ventana.destroy()
            # Reabrir la pantalla de login
            try:
                from loginP import App
                App()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la pantalla de login: {str(e)}")
                self.ventana.destroy()


# Para probar de forma independiente
if __name__ == "__main__":
    # Para pruebas, asignar un ID de usuario fijo
    id_usuario_prueba = 2  # Suponiendo que 2 es un cajero
    CajeroPanel(id_usuario_prueba)