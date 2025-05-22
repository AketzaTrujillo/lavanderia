import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import utileria as utl
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)


class CajeroPanel:
    def __init__(self, id_usuario=None):
        self.ventana = tk.Tk()
        self.ventana.title("💼 Panel de Cajero - Lavandería Exprés")
        self.ventana.geometry("900x650")
        self.ventana.config(bg="#f0f9ff")
        self.ventana.resizable(True, True)
        self.ventana.minsize(800, 600)

        self.id_usuario = id_usuario if id_usuario is not None else 2
        utl.centrar_ventana(self.ventana, 900, 650)

        try:
            if os.path.exists("Img/lavadora.ico"):
                self.ventana.iconbitmap("Img/lavadora.ico")
        except Exception:
            pass

        self.construir_interfaz()
        self.ventana.mainloop()

    def construir_interfaz(self):
        # Canvas para scroll SIN scrollbar visible
        self.canvas = tk.Canvas(self.ventana, bg="#f0f9ff", highlightthickness=0, bd=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame scrollable
        self.frame_principal = tk.Frame(self.canvas, bg="#f0f9ff")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.frame_principal, anchor="nw")

        # Configurar scroll
        def configurar_scroll(event=None):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            # Hacer que el frame ocupe todo el ancho del canvas
            canvas_width = self.canvas.winfo_width()
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)

        self.frame_principal.bind("<Configure>", configurar_scroll)
        self.canvas.bind("<Configure>", configurar_scroll)

        # SCROLL CON MOUSE - FUNCIONAL
        def scroll_mouse(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def scroll_linux_up(event):
            self.canvas.yview_scroll(-1, "units")

        def scroll_linux_down(event):
            self.canvas.yview_scroll(1, "units")

        # Vincular eventos de scroll
        self.canvas.bind("<MouseWheel>", scroll_mouse)  # Windows
        self.canvas.bind("<Button-4>", scroll_linux_up)  # Linux up
        self.canvas.bind("<Button-5>", scroll_linux_down)  # Linux down

        # Hacer que el canvas reciba el foco para scroll
        self.canvas.focus_set()

        # También vincular a todos los widgets hijos
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
        header_frame = tk.Frame(self.frame_principal, bg="#0891b2", height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        header_content = tk.Frame(header_frame, bg="#0891b2")
        header_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=15)

        titulo_frame = tk.Frame(header_content, bg="#0891b2")
        titulo_frame.pack(side=tk.LEFT, fill=tk.Y)

        titulo = tk.Label(titulo_frame, text="💼 PANEL DE CAJERO", font=("Segoe UI", 24, "bold"), bg="#0891b2",
                          fg="white")
        titulo.pack(anchor=tk.W)

        subtitulo = tk.Label(titulo_frame, text="Sistema de Gestión de Lavandería Exprés", font=("Segoe UI", 12),
                             bg="#0891b2", fg="#a7f3d0")
        subtitulo.pack(anchor=tk.W, pady=(5, 0))

        info_frame = tk.Frame(header_content, bg="#0891b2")
        info_frame.pack(side=tk.RIGHT)

        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        hora_actual = datetime.now().strftime("%H:%M")

        tk.Label(info_frame, text="👨‍💼 Cajero", font=("Segoe UI", 12, "bold"), bg="#0891b2", fg="white").pack(
            anchor=tk.E)
        tk.Label(info_frame, text=f"📅 {fecha_actual} • 🕐 {hora_actual}", font=("Segoe UI", 10), bg="#0891b2",
                 fg="#a7f3d0").pack(anchor=tk.E)

    def crear_contenido_principal(self):
        container = tk.Frame(self.frame_principal, bg="#f0f9ff")
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        titulo_seccion = tk.Label(container, text="🎯 Funciones de Cajero", font=("Segoe UI", 18, "bold"), bg="#f0f9ff",
                                  fg="#1f2937")
        titulo_seccion.pack(pady=(0, 20))

        grid_frame = tk.Frame(container, bg="#f0f9ff")
        grid_frame.pack(fill=tk.BOTH, expand=True)

        for i in range(2):
            grid_frame.columnconfigure(i, weight=1)

        botones = [
            {"texto": "Registrar Pedido", "comando": self.registrar_pedido, "icono": "📋",
             "descripcion": "Crear y gestionar nuevos pedidos de clientes", "color": "#7c3aed",
             "color_hover": "#6d28d9", "fila": 0, "columna": 0},
            {"texto": "Gestionar Clientes", "comando": self.gestionar_clientes, "icono": "👥",
             "descripcion": "Administrar información de clientes", "color": "#d97706", "color_hover": "#b45309",
             "fila": 0, "columna": 1},
            {"texto": "Registrar Venta", "comando": self.registrar_venta, "icono": "💰",
             "descripcion": "Procesar ventas y generar tickets", "color": "#dc2626", "color_hover": "#b91c1c",
             "fila": 1, "columna": 0},
            {"texto": "Gestionar Caja", "comando": self.gestionar_caja, "icono": "💵",
             "descripcion": "Control de caja y movimientos diarios", "color": "#059669", "color_hover": "#047857",
             "fila": 1, "columna": 1},
            {"texto": "Seguimiento Pedidos", "comando": self.seguimiento_pedidos, "icono": "📊",
             "descripcion": "Monitorear estado de pedidos en tiempo real", "color": "#0891b2", "color_hover": "#0e7490",
             "fila": 2, "columna": 0}
        ]

        for config in botones:
            self.crear_boton_funcion(grid_frame, config)

        self.crear_boton_cerrar_sesion(grid_frame)

    def crear_boton_funcion(self, parent, config):
        frame_boton = tk.Frame(parent, bg="#ffffff", relief=tk.RAISED, bd=1)
        frame_boton.grid(row=config['fila'], column=config['columna'], padx=15, pady=15, sticky="nsew", ipadx=15,
                         ipady=15)

        icono_label = tk.Label(frame_boton, text=config['icono'], font=("Segoe UI Emoji", 32), bg="#ffffff",
                               fg=config['color'])
        icono_label.pack(pady=(15, 8))

        titulo_label = tk.Label(frame_boton, text=config['texto'], font=("Segoe UI", 14, "bold"), bg="#ffffff",
                                fg="#1f2937", wraplength=250)
        titulo_label.pack(pady=(0, 8))

        desc_label = tk.Label(frame_boton, text=config['descripcion'], font=("Segoe UI", 10), bg="#ffffff",
                              fg="#6b7280", wraplength=230, justify=tk.CENTER)
        desc_label.pack(pady=(0, 15))

        btn_accion = tk.Button(frame_boton, text="ABRIR", font=("Segoe UI", 11, "bold"), bg=config['color'], fg="white",
                               activebackground=config['color_hover'], activeforeground="white", relief=tk.FLAT,
                               cursor="hand2", command=config['comando'], width=18, pady=8)
        btn_accion.pack(pady=(0, 15))

        def on_enter(event):
            frame_boton.config(bg="#f8fafc", relief=tk.RAISED, bd=2)
            icono_label.config(bg="#f8fafc")
            titulo_label.config(bg="#f8fafc")
            desc_label.config(bg="#f8fafc")
            btn_accion.config(bg=config['color_hover'])

        def on_leave(event):
            frame_boton.config(bg="#ffffff", relief=tk.RAISED, bd=1)
            icono_label.config(bg="#ffffff")
            titulo_label.config(bg="#ffffff")
            desc_label.config(bg="#ffffff")
            btn_accion.config(bg=config['color'])

        for widget in [frame_boton, icono_label, titulo_label, desc_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

    def crear_boton_cerrar_sesion(self, parent):
        frame_boton = tk.Frame(parent, bg="#fef2f2", relief=tk.RAISED, bd=1)
        frame_boton.grid(row=2, column=1, padx=15, pady=20, sticky="nsew", ipadx=15, ipady=15)

        tk.Label(frame_boton, text="🚪", font=("Segoe UI Emoji", 32), bg="#fef2f2", fg="#dc2626").pack(pady=(15, 8))
        tk.Label(frame_boton, text="Cerrar Sesión", font=("Segoe UI", 14, "bold"), bg="#fef2f2", fg="#1f2937").pack(
            pady=(0, 8))
        tk.Label(frame_boton, text="Salir del sistema de forma segura", font=("Segoe UI", 10), bg="#fef2f2",
                 fg="#6b7280", wraplength=230, justify=tk.CENTER).pack(pady=(0, 15))

        btn_salir = tk.Button(frame_boton, text="SALIR", font=("Segoe UI", 11, "bold"), bg="#dc2626", fg="white",
                              activebackground="#b91c1c", activeforeground="white", relief=tk.FLAT, cursor="hand2",
                              command=self.salir, width=18, pady=8)
        btn_salir.pack(pady=(0, 15))

    def crear_footer(self):
        footer_frame = tk.Frame(self.frame_principal, bg="#ffffff", height=50)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)

        tk.Frame(footer_frame, bg="#e5e7eb", height=1).pack(fill=tk.X)

        footer_content = tk.Frame(footer_frame, bg="#ffffff")
        footer_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        tk.Label(footer_content, text="💼 Panel de Cajero | Sistema de Lavandería v2.0", font=("Segoe UI", 9),
                 bg="#ffffff", fg="#6b7280").pack(side=tk.LEFT)
        tk.Label(footer_content, text="🟢 Conectado • Caja operativa", font=("Segoe UI", 9), bg="#ffffff",
                 fg="#059669").pack(side=tk.RIGHT)

    def registrar_pedido(self):
        try:
            from pedidos import Pedidos
            Pedidos(self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo: {str(e)}")

    def gestionar_clientes(self):
        try:
            from clientes import GestionClientes
            GestionClientes(self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo: {str(e)}")

    def registrar_venta(self):
        try:
            from ventas import Ventas
            Ventas(self.ventana, id_usuario=self.id_usuario)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo: {str(e)}")

    def gestionar_caja(self):
        try:
            from caja import GestionCaja
            GestionCaja(ventana_padre=self.ventana, id_usuario=self.id_usuario)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo de caja: {str(e)}")

    def seguimiento_pedidos(self):
        try:
            from seguimiento_pedidos import SeguimientoPedidos
            SeguimientoPedidos(self.ventana, self.id_usuario, 'cajero')
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo de seguimiento: {str(e)}")

    def salir(self):
        if messagebox.askyesno("Confirmar salida", "¿Estás seguro de que deseas cerrar sesión?"):
            self.ventana.destroy()
            try:
                from loginP import App
                App()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la pantalla de login: {str(e)}")


if __name__ == "__main__":
    CajeroPanel(2)