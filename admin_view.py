import tkinter as tk
from tkinter import ttk, messagebox
import os
import utileria as utl
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))


class MasterPanel:
    def __init__(self, id_usuario=None):
        self.ventana = tk.Tk()
        self.ventana.title("🏢 Panel de Administrador - Lavandería Exprés")
        self.ventana.state('zoomed')
        try:
            self.ventana.attributes('-zoomed', True)
        except:
            pass

        self.ventana.config(bg="#f0f4f8")
        self.ventana.resizable(True, True)
        self.ventana.minsize(900, 650)

        self.id_usuario = id_usuario if id_usuario is not None else 1
        utl.centrar_ventana(self.ventana, 1000, 700)

        try:
            if os.path.exists("Img/lavadora.ico"):
                self.ventana.iconbitmap("Img/lavadora.ico")
        except Exception:
            pass

        self.construir_interfaz()
        self.ventana.mainloop()

    def construir_interfaz(self):
        self.canvas = tk.Canvas(self.ventana, bg="#f0f4f8", highlightthickness=0, bd=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.frame_principal = tk.Frame(self.canvas, bg="#f0f4f8")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.frame_principal, anchor="nw")

        def configurar_scroll(event=None):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            canvas_width = self.canvas.winfo_width()
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)

        self.frame_principal.bind("<Configure>", configurar_scroll)
        self.canvas.bind("<Configure>", configurar_scroll)

        def scroll_mouse(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def scroll_linux_up(event):
            self.canvas.yview_scroll(-1, "units")

        def scroll_linux_down(event):
            self.canvas.yview_scroll(1, "units")

        self.canvas.bind("<MouseWheel>", scroll_mouse)
        self.canvas.bind("<Button-4>", scroll_linux_up)
        self.canvas.bind("<Button-5>", scroll_linux_down)
        self.canvas.focus_set()

        def bind_scroll_to_all(widget):
            widget.bind("<MouseWheel>", scroll_mouse)
            widget.bind("<Button-4>", scroll_linux_up)
            widget.bind("<Button-5>", scroll_linux_down)
            for child in widget.winfo_children():
                bind_scroll_to_all(child)

        self.ventana.after(100, lambda: bind_scroll_to_all(self.frame_principal))

        self.crear_header()
        self.crear_contenido_principal()
        self.crear_footer()

    def crear_header(self):
        header_frame = tk.Frame(self.frame_principal, bg="#2563eb", height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        header_content = tk.Frame(header_frame, bg="#2563eb")
        header_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=15)

        titulo_frame = tk.Frame(header_content, bg="#2563eb")
        titulo_frame.pack(side=tk.LEFT, fill=tk.Y)

        titulo = tk.Label(titulo_frame, text="🏢 PANEL DE ADMINISTRACIÓN", font=("Segoe UI", 24, "bold"), bg="#2563eb",
                          fg="white")
        titulo.pack(anchor=tk.W)

        subtitulo = tk.Label(titulo_frame, text="Sistema de Gestión de Lavandería Exprés", font=("Segoe UI", 12),
                             bg="#2563eb", fg="#bfdbfe")
        subtitulo.pack(anchor=tk.W, pady=(5, 0))

        info_frame = tk.Frame(header_content, bg="#2563eb")
        info_frame.pack(side=tk.RIGHT)

        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        hora_actual = datetime.now().strftime("%H:%M")

        tk.Label(info_frame, text="👤 Administrador", font=("Segoe UI", 12, "bold"), bg="#2563eb", fg="white").pack(
            anchor=tk.E)
        tk.Label(info_frame, text=f"📅 {fecha_actual} • 🕐 {hora_actual}", font=("Segoe UI", 10), bg="#2563eb",
                 fg="#bfdbfe").pack(anchor=tk.E)

    def crear_contenido_principal(self):
        container = tk.Frame(self.frame_principal, bg="#f0f4f8")
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        titulo_seccion = tk.Label(container, text="🚀 Funciones del Sistema", font=("Segoe UI", 18, "bold"),
                                  bg="#f0f4f8", fg="#1f2937")
        titulo_seccion.pack(pady=(0, 20))

        grid_frame = tk.Frame(container, bg="#f0f4f8")
        grid_frame.pack(fill=tk.BOTH, expand=True)

        for i in range(3):
            grid_frame.columnconfigure(i, weight=1)

        # ⭐ BOTONES ACTUALIZADOS - SIN CONFIGURACIONES
        botones = [
            # Primera fila
            {"texto": "Gestionar Usuarios", "comando": self.gestionar_usuarios, "icono": "👤",
             "descripcion": "Administrar cuentas de usuario del sistema", "color": "#2563eb", "color_hover": "#1d4ed8",
             "fila": 0, "columna": 0},
            {"texto": "Productos y Servicios", "comando": self.gestionar_productos, "icono": "📦",
             "descripcion": "Gestionar inventario y catálogo de servicios", "color": "#059669",
             "color_hover": "#047857", "fila": 0, "columna": 1},
            {"texto": "Gestionar Clientes", "comando": self.gestionar_clientes, "icono": "👥",
             "descripcion": "Base de datos y perfiles de clientes", "color": "#d97706", "color_hover": "#b45309",
             "fila": 0, "columna": 2},

            # Segunda fila
            {"texto": "Gestionar Pedidos", "comando": self.gestionar_pedidos, "icono": "📋",
             "descripcion": "Control y seguimiento de pedidos", "color": "#7c3aed", "color_hover": "#6d28d9", "fila": 1,
             "columna": 0},
            {"texto": "Ventas con Cuentas", "comando": self.ventas_con_cuentas_abiertas, "icono": "💰",
             "descripcion": "Sistema de ventas con cuentas abiertas", "color": "#dc2626", "color_hover": "#b91c1c",
             "fila": 1,
             "columna": 1},
            {"texto": "Registrar Ventas", "comando": self.registrar_ventas, "icono": "💵",
             "descripcion": "Punto de venta tradicional", "color": "#16a34a", "color_hover": "#15803d", "fila": 1,
             "columna": 2},

            # Tercera fila
            {"texto": "Cuentas Abiertas", "comando": self.gestionar_cuentas_abiertas, "icono": "🧾",
             "descripcion": "Gestión de cuentas abiertas y facturación", "color": "#0891b2", "color_hover": "#0e7490",
             "fila": 2, "columna": 0},
            {"texto": "Gestionar Caja", "comando": self.gestionar_caja, "icono": "🏦",
             "descripcion": "Control de ingresos, egresos y arqueos", "color": "#be185d", "color_hover": "#9d174d",
             "fila": 2, "columna": 1},
            {"texto": "Seguimiento Pedidos", "comando": self.seguimiento_pedidos, "icono": "📊",
             "descripcion": "Monitoreo en tiempo real de pedidos", "color": "#7c2d12", "color_hover": "#92400e",
             "fila": 2, "columna": 2},

            # Cuarta fila
            {"texto": "Generar Reportes", "comando": self.generar_reportes, "icono": "📈",
             "descripcion": "Análisis, estadísticas y reportes", "color": "#374151", "color_hover": "#1f2937",
             "fila": 3,
             "columna": 0},
            {"texto": "Gestionar Respaldos", "comando": self.gestionar_respaldos, "icono": "💾",
             "descripcion": "Copias de seguridad del sistema", "color": "#0ea5e9", "color_hover": "#0369a1", "fila": 3,
             "columna": 1},
            {"texto": "Promos y Descuentos", "comando": self.abrir_promos_descuentos, "icono": "🏷️",
             "descripcion": "Gestiona promociones y descuentos", "color": "#f59e42", "color_hover": "#d97706",
             "fila": 3,
             "columna": 2},

            # Quinta fila
            {"texto": "Gestionar Permisos", "comando": self.gestionar_permisos_usuarios, "icono": "🔒",
             "descripcion": "Administrar permisos de acceso de cajeros", "color": "#991b1b", "color_hover": "#7f1d1d",
             "fila": 4, "columna": 0},
            {"texto": "Puntos de Lealtad", "comando": self.gestionar_puntos_lealtad, "icono": "⭐",
             "descripcion": "Gestiona y consulta los puntos de lealtad", "color": "#7c3aed", "color_hover": "#6d28d9",
             "fila": 4, "columna": 1}
        ]

        for config in botones:
            self.crear_boton_funcion(grid_frame, config)

        self.crear_boton_cerrar_sesion(grid_frame)

    def crear_boton_funcion(self, parent, config):
        frame_boton = tk.Frame(parent, bg="#ffffff", relief=tk.RAISED, bd=1)
        frame_boton.grid(row=config['fila'], column=config['columna'], padx=10, pady=10, sticky="nsew", ipadx=10,
                         ipady=10)

        icono_label = tk.Label(frame_boton, text=config['icono'], font=("Segoe UI Emoji", 24), bg="#ffffff",
                               fg=config['color'])
        icono_label.pack(pady=(15, 5))

        titulo_label = tk.Label(frame_boton, text=config['texto'], font=("Segoe UI", 11, "bold"), bg="#ffffff",
                                fg="#1f2937")
        titulo_label.pack(pady=(0, 5))

        desc_label = tk.Label(frame_boton, text=config['descripcion'], font=("Segoe UI", 8), bg="#ffffff",
                              fg="#6b7280", wraplength=150)
        desc_label.pack(pady=(0, 15))

        def on_enter(e):
            frame_boton.config(bg=config['color'])
            icono_label.config(bg=config['color'], fg="#ffffff")
            titulo_label.config(bg=config['color'], fg="#ffffff")
            desc_label.config(bg=config['color'], fg="#ffffff")

        def on_leave(e):
            frame_boton.config(bg="#ffffff")
            icono_label.config(bg="#ffffff", fg=config['color'])
            titulo_label.config(bg="#ffffff", fg="#1f2937")
            desc_label.config(bg="#ffffff", fg="#6b7280")

        def on_click(e):
            config['comando']()

        widgets = [frame_boton, icono_label, titulo_label, desc_label]
        for widget in widgets:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

    def crear_boton_cerrar_sesion(self, parent):
        frame_salir = tk.Frame(parent, bg="#dc2626", relief=tk.RAISED, bd=1)
        frame_salir.grid(row=5, column=1, padx=10, pady=20, sticky="nsew")

        icono_salir = tk.Label(frame_salir, text="🚪", font=("Segoe UI Emoji", 20), bg="#dc2626", fg="#ffffff")
        icono_salir.pack(pady=(10, 5))

        texto_salir = tk.Label(frame_salir, text="Cerrar Sesión", font=("Segoe UI", 12, "bold"), bg="#dc2626",
                               fg="#ffffff")
        texto_salir.pack(pady=(0, 10))

        def on_enter_salir(e):
            frame_salir.config(bg="#b91c1c")
            icono_salir.config(bg="#b91c1c")
            texto_salir.config(bg="#b91c1c")

        def on_leave_salir(e):
            frame_salir.config(bg="#dc2626")
            icono_salir.config(bg="#dc2626")
            texto_salir.config(bg="#dc2626")

        widgets_salir = [frame_salir, icono_salir, texto_salir]
        for widget in widgets_salir:
            widget.bind("<Enter>", on_enter_salir)
            widget.bind("<Leave>", on_leave_salir)
            widget.bind("<Button-1>", lambda e: self.salir())

    def crear_footer(self):
        footer_frame = tk.Frame(self.frame_principal, bg="#ffffff", height=50)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)

        tk.Frame(footer_frame, bg="#e5e7eb", height=1).pack(fill=tk.X)

        footer_content = tk.Frame(footer_frame, bg="#ffffff")
        footer_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        tk.Label(footer_content, text="🏢 Panel de Administración | Sistema de Lavandería v2.0", font=("Segoe UI", 9),
                 bg="#ffffff", fg="#6b7280").pack(side=tk.LEFT)
        tk.Label(footer_content, text="🟢 Conectado • Sistema operativo", font=("Segoe UI", 9), bg="#ffffff",
                 fg="#059669").pack(side=tk.RIGHT)

    # ==================== MÉTODOS EXISTENTES ====================

    def gestionar_usuarios(self):
        try:
            from gestionar_usuarios import GestionUsuarios
            GestionUsuarios(self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo de usuarios: {str(e)}")

    def gestionar_productos(self):
        try:
            from gestionar_productos_servicios import GestionProductosServicios
            GestionProductosServicios(self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo de productos: {str(e)}")

    def gestionar_clientes(self):
        try:
            from clientes import GestionClientes
            GestionClientes(self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo de clientes: {str(e)}")

    def gestionar_pedidos(self):
        try:
            from pedidos import Pedidos
            Pedidos(self.ventana, id_usuario=self.id_usuario)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo de pedidos: {str(e)}")

    def gestionar_caja(self):
        try:
            from caja import GestionCaja
            GestionCaja(ventana_padre=self.ventana, id_usuario=self.id_usuario)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo de caja: {str(e)}")

    def gestionar_respaldos(self):
        try:
            from respaldos2 import ModuloRespaldo
            ModuloRespaldo(self.ventana, self.id_usuario)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo de respaldos: {str(e)}")

    def registrar_ventas(self):
        try:
            from ventas import Ventas
            Ventas(self.ventana, id_usuario=self.id_usuario)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo de ventas: {str(e)}")

    def generar_reportes(self):
        try:
            from reportes import abrir_reportes
            abrir_reportes(self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo de reportes: {str(e)}")

    def seguimiento_pedidos(self):
        try:
            from seguimiento_pedidos import SeguimientoPedidos
            SeguimientoPedidos(self.ventana, self.id_usuario)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo de seguimiento: {str(e)}")

    def abrir_promos_descuentos(self):
        try:
            from promos_descuentos import PromosDescuentosVentana
            PromosDescuentosVentana(self.ventana, id_usuario=self.id_usuario)
        except ImportError:
            messagebox.showinfo("Información", "El módulo de promociones estará disponible próximamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo de promociones: {str(e)}")

    def gestionar_permisos_usuarios(self):
        try:
            from permisos_usuarios import GestionPermisosUsuarios
            GestionPermisosUsuarios(self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo de permisos: {str(e)}")

    def gestionar_puntos_lealtad(self):
        try:
            from puntos_lealtad import PuntosLealtadVentana
            PuntosLealtadVentana(self.ventana)
        except ImportError:
            messagebox.showinfo("Información", "El módulo de puntos de lealtad estará disponible próximamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo de puntos de lealtad: {str(e)}")

    # ==================== NUEVOS MÉTODOS PARA CUENTAS ABIERTAS ====================

    def gestionar_cuentas_abiertas(self):
        """Gestión de cuentas abiertas"""
        try:
            from cuentas_abiertas_gui import abrir_gestion_cuentas_abiertas
            abrir_gestion_cuentas_abiertas(self.ventana, {'id_usuario': self.id_usuario})
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir gestión de cuentas abiertas:\n{str(e)}")

    def ventas_con_cuentas_abiertas(self):
        """Sistema de ventas con cuentas abiertas"""
        try:
            from ventas_con_cuentas import abrir_ventas_con_cuentas_abiertas
            abrir_ventas_con_cuentas_abiertas(self.ventana, {'id_usuario': self.id_usuario})
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir sistema de ventas:\n{str(e)}")

    def salir(self):
        if messagebox.askyesno("Confirmar salida", "¿Estás seguro de que deseas cerrar sesión?"):
            self.ventana.destroy()
            try:
                from loginP import App
                App()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la pantalla de login: {str(e)}")


if __name__ == "__main__":
    MasterPanel()