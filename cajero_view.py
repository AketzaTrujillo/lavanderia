import tkinter as tk
from tkinter import messagebox
import os
import sys

# Asegurar que podemos importar módulos del sistema
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

try:
    from conexion import conectar_bd
    from permisos_usuarios import GestionPermisosUsuarios
except ImportError as e:
    print(f"Error al importar dependencias: {e}")


class CajeroPanel:
    """Panel principal para cajeros con sistema de permisos"""

    def __init__(self, id_usuario):
        self.id_usuario = id_usuario
        self.permisos_usuario = []

        # Ventana principal
        self.ventana = tk.Tk()
        self.ventana.title("Panel de Cajero - Sistema Lavandería")
        self.ventana.geometry("1000x700")
        self.ventana.config(bg="#f0f9ff")
        self.ventana.resizable(False, False)

        # Cargar permisos del usuario
        self.cargar_permisos()

        # Crear interfaz
        self.crear_interfaz()

        # Iniciar bucle principal
        self.ventana.mainloop()

    def cargar_permisos(self):
        """Cargar permisos del usuario desde la base de datos"""
        try:
            self.permisos_usuario = GestionPermisosUsuarios.obtener_permisos_usuario(self.id_usuario)
            print(f"Debug - Permisos cargados para usuario {self.id_usuario}: {self.permisos_usuario}")

            # Si el usuario no tiene permisos definidos, mostrar advertencia
            if not self.permisos_usuario:
                messagebox.showwarning(
                    "Sin Permisos",
                    "Este usuario no tiene permisos asignados.\n"
                    "Contacte al administrador para configurar sus permisos de acceso."
                )

        except Exception as e:
            print(f"Error al cargar permisos: {e}")
            messagebox.showerror("Error", f"Error al cargar permisos del usuario: {e}")

    def tiene_permiso(self, modulo):
        """Verificar si el usuario tiene permiso para un módulo específico"""
        return modulo in self.permisos_usuario

    def crear_interfaz(self):
        """Crear la interfaz principal"""
        # Frame principal
        self.frame_principal = tk.Frame(self.ventana, bg="#f0f9ff")
        self.frame_principal.pack(fill=tk.BOTH, expand=True)

        # Crear header
        self.crear_header()

        # Crear área de funciones
        self.crear_area_funciones()

        # Crear footer
        self.crear_footer()

    def crear_header(self):
        """Crear la cabecera del panel"""
        header_frame = tk.Frame(self.frame_principal, bg="#1e40af", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Obtener información del usuario
        nombre_usuario = self.obtener_nombre_usuario()

        header_content = tk.Frame(header_frame, bg="#1e40af")
        header_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=15)

        # Título y bienvenida
        tk.Label(header_content, text="🧼 Sistema de Lavandería",
                 font=("Segoe UI", 20, "bold"), bg="#1e40af", fg="white").pack(side=tk.LEFT)

        user_info_frame = tk.Frame(header_content, bg="#1e40af")
        user_info_frame.pack(side=tk.RIGHT)

        tk.Label(user_info_frame, text=f"👋 Bienvenido, {nombre_usuario}",
                 font=("Segoe UI", 12), bg="#1e40af", fg="#dbeafe").pack(anchor="e")
        tk.Label(user_info_frame, text="🎯 Panel de Cajero",
                 font=("Segoe UI", 10), bg="#1e40af", fg="#93c5fd").pack(anchor="e")

    def obtener_nombre_usuario(self):
        """Obtener el nombre del usuario desde la base de datos"""
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("SELECT nombre FROM usuarios WHERE id_usuario = %s", (self.id_usuario,))
            resultado = cursor.fetchone()
            conexion.close()

            return resultado[0] if resultado else "Usuario"

        except Exception as e:
            print(f"Error al obtener nombre de usuario: {e}")
            return "Usuario"

    def crear_area_funciones(self):
        """Crear el área de funciones principales"""
        container = tk.Frame(self.frame_principal, bg="#f0f9ff")
        container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)

        # Título de la sección
        titulo_seccion = tk.Label(container, text="🎯 Funciones Disponibles",
                                  font=("Segoe UI", 18, "bold"), bg="#f0f9ff", fg="#1f2937")
        titulo_seccion.pack(pady=(0, 20))

        # Verificar si el usuario tiene permisos
        if not self.permisos_usuario:
            # Mostrar mensaje si no hay permisos
            frame_sin_permisos = tk.Frame(container, bg="#fef2f2", relief=tk.RAISED, bd=2)
            frame_sin_permisos.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            tk.Label(frame_sin_permisos, text="⚠️", font=("Segoe UI Emoji", 48),
                     bg="#fef2f2", fg="#dc2626").pack(pady=(30, 10))
            tk.Label(frame_sin_permisos, text="Sin Permisos Asignados",
                     font=("Segoe UI", 16, "bold"), bg="#fef2f2", fg="#dc2626").pack()
            tk.Label(frame_sin_permisos,
                     text="Este usuario no tiene permisos para acceder a ninguna función.\n"
                          "Contacte al administrador para configurar los permisos necesarios.",
                     font=("Segoe UI", 11), bg="#fef2f2", fg="#7f1d1d",
                     justify=tk.CENTER).pack(pady=(5, 30))
            return

        # Grid para botones de funciones
        grid_frame = tk.Frame(container, bg="#f0f9ff")
        grid_frame.pack(fill=tk.BOTH, expand=True)

        # Configurar grid
        for i in range(3):  # 3 columnas
            grid_frame.columnconfigure(i, weight=1)

        # CORREGIDO: Definir funciones usando módulos que realmente existen
        todas_las_funciones = [
            {
                "modulo": "registrar_pedido",
                "texto": "Registrar Pedido",
                "comando": self.registrar_pedido,
                "icono": "📋",
                "descripcion": "Crear y gestionar nuevos pedidos de clientes",
                "color": "#7c3aed",
                "color_hover": "#6d28d9"
            },
            {
                "modulo": "gestionar_clientes",
                "texto": "Gestionar Clientes",
                "comando": self.gestionar_clientes,
                "icono": "👥",
                "descripcion": "Administrar información de clientes",
                "color": "#d97706",
                "color_hover": "#b45309"
            },
            {
                "modulo": "registrar_venta",
                "texto": "Registrar Venta",
                "comando": self.registrar_venta,
                "icono": "💰",
                "descripcion": "Procesar ventas y generar tickets",
                "color": "#dc2626",
                "color_hover": "#b91c1c"
            },
            {
                "modulo": "gestionar_caja",
                "texto": "Gestionar Caja",
                "comando": self.gestionar_caja,
                "icono": "💵",
                "descripcion": "Control de caja y movimientos diarios",
                "color": "#059669",
                "color_hover": "#047857"
            },
            {
                "modulo": "seguimiento_pedidos",
                "texto": "Seguimiento Pedidos",
                "comando": self.seguimiento_pedidos,
                "icono": "📊",
                "descripcion": "Monitorear estado de pedidos en tiempo real",
                "color": "#0891b2",
                "color_hover": "#0e7490"
            },
            {
                "modulo": "ver_reportes",
                "texto": "Ver Reportes",
                "comando": self.ver_reportes,
                "icono": "📈",
                "descripcion": "Consultar reportes básicos del sistema",
                "color": "#9333ea",
                "color_hover": "#7c2d12"
            },
            {
                "modulo": "gestionar_inventario",
                "texto": "Gestionar Productos",
                "comando": self.gestionar_inventario,
                "icono": "📦",
                "descripcion": "Control de productos e inventario",
                "color": "#ea580c",
                "color_hover": "#c2410c"
            },
            {
                "modulo": "aplicar_descuentos",
                "texto": "Aplicar Descuentos",
                "comando": self.aplicar_descuentos,
                "icono": "🏷️",
                "descripcion": "Gestionar descuentos y promociones",
                "color": "#0d9488",
                "color_hover": "#0f766e"
            }
        ]

        # Filtrar funciones según permisos y crear botones
        funciones_permitidas = [f for f in todas_las_funciones if self.tiene_permiso(f["modulo"])]

        if not funciones_permitidas:
            # Este caso no debería darse, pero por seguridad
            tk.Label(grid_frame, text="No hay funciones disponibles",
                     font=("Segoe UI", 12), bg="#f0f9ff", fg="#6b7280").pack(pady=50)
            return

        # Crear botones para funciones permitidas
        fila, columna = 0, 0
        for i, config in enumerate(funciones_permitidas):
            config["fila"] = fila
            config["columna"] = columna
            self.crear_boton_funcion(grid_frame, config)

            # Calcular siguiente posición
            columna += 1
            if columna >= 3:  # 3 columnas máximo
                columna = 0
                fila += 1

        # Crear botón de cerrar sesión
        self.crear_boton_cerrar_sesion(grid_frame, fila + 1)

    def crear_boton_funcion(self, parent, config):
        """Crear un botón de función"""
        frame_boton = tk.Frame(parent, bg="#ffffff", relief=tk.RAISED, bd=1)
        frame_boton.grid(row=config['fila'], column=config['columna'],
                         padx=15, pady=15, sticky="nsew", ipadx=15, ipady=15)

        # Icono
        icono_label = tk.Label(frame_boton, text=config['icono'],
                               font=("Segoe UI Emoji", 32), bg="#ffffff", fg=config['color'])
        icono_label.pack(pady=(15, 8))

        # Título
        titulo_label = tk.Label(frame_boton, text=config['texto'],
                                font=("Segoe UI", 14, "bold"), bg="#ffffff", fg="#1f2937")
        titulo_label.pack(pady=(0, 5))

        # Descripción
        desc_label = tk.Label(frame_boton, text=config['descripcion'],
                              font=("Segoe UI", 9), bg="#ffffff", fg="#6b7280",
                              wraplength=150, justify=tk.CENTER)
        desc_label.pack(pady=(0, 15))

        # Botón de acción
        btn_accion = tk.Button(frame_boton, text="Acceder", command=config['comando'],
                               bg=config['color'], fg="white", font=("Segoe UI", 10, "bold"),
                               padx=20, pady=6, cursor="hand2")
        btn_accion.pack(pady=(0, 10))

        # Efectos hover
        def on_enter(e):
            btn_accion.config(bg=config['color_hover'])
            frame_boton.config(relief=tk.RAISED, bd=2)

        def on_leave(e):
            btn_accion.config(bg=config['color'])
            frame_boton.config(relief=tk.RAISED, bd=1)

        btn_accion.bind("<Enter>", on_enter)
        btn_accion.bind("<Leave>", on_leave)
        frame_boton.bind("<Enter>", on_enter)
        frame_boton.bind("<Leave>", on_leave)

    def crear_boton_cerrar_sesion(self, parent, fila):
        """Crear botón para cerrar sesión"""
        frame_cerrar = tk.Frame(parent, bg="#ffffff", relief=tk.RAISED, bd=1)
        frame_cerrar.grid(row=fila, column=1, padx=15, pady=20, sticky="nsew", ipadx=15, ipady=15)

        # Icono
        tk.Label(frame_cerrar, text="🚪", font=("Segoe UI Emoji", 32),
                 bg="#ffffff", fg="#dc2626").pack(pady=(15, 8))

        # Título
        tk.Label(frame_cerrar, text="Cerrar Sesión", font=("Segoe UI", 14, "bold"),
                 bg="#ffffff", fg="#1f2937").pack(pady=(0, 5))

        # Descripción
        tk.Label(frame_cerrar, text="Salir del sistema de forma segura",
                 font=("Segoe UI", 9), bg="#ffffff", fg="#6b7280",
                 wraplength=150, justify=tk.CENTER).pack(pady=(0, 15))

        # Botón
        btn_salir = tk.Button(frame_cerrar, text="Cerrar Sesión", command=self.salir,
                              bg="#dc2626", fg="white", font=("Segoe UI", 10, "bold"),
                              padx=20, pady=6, cursor="hand2")
        btn_salir.pack(pady=(0, 10))

    def crear_footer(self):
        """Crear pie de página"""
        footer_frame = tk.Frame(self.frame_principal, bg="#ffffff", height=50)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)

        # Línea separadora
        tk.Frame(footer_frame, bg="#e5e7eb", height=1).pack(fill=tk.X)

        footer_content = tk.Frame(footer_frame, bg="#ffffff")
        footer_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        # Información del sistema
        tk.Label(footer_content, text="💼 Panel de Cajero | Sistema de Lavandería v2.0",
                 font=("Segoe UI", 9), bg="#ffffff", fg="#6b7280").pack(side=tk.LEFT)

        # Estado de la conexión
        tk.Label(footer_content, text="🟢 Conectado • Permisos activos",
                 font=("Segoe UI", 9), bg="#ffffff", fg="#059669").pack(side=tk.RIGHT)

    # ==================== MÉTODOS DE FUNCIONALIDAD (NOMBRES EXACTOS) ====================

    def registrar_pedido(self):
        """CORRECTO: Abrir módulo de registro de pedidos"""
        if not self.tiene_permiso('registrar_pedido'):
            messagebox.showerror("Sin Permisos", "No tiene permisos para acceder a esta función.")
            return
        try:
            from pedidos import Pedidos
            Pedidos(self.ventana, id_usuario=self.id_usuario)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo: {e}")

    def gestionar_clientes(self):
        """CORRECTO: Abrir módulo de gestión de clientes"""
        if not self.tiene_permiso('gestionar_clientes'):
            messagebox.showerror("Sin Permisos", "No tiene permisos para acceder a esta función.")
            return
        try:
            from clientes import GestionClientes
            GestionClientes(self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo: {str(e)}")

    def registrar_venta(self):
        """CORRECTO: Abrir módulo de registro de ventas"""
        if not self.tiene_permiso('registrar_venta'):
            messagebox.showerror("Sin Permisos", "No tiene permisos para acceder a esta función.")
            return
        try:
            from ventas import Ventas
            Ventas(self.ventana, id_usuario=self.id_usuario)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo: {str(e)}")

    def gestionar_caja(self):
        """CORRECTO: Abrir módulo de gestión de caja"""
        if not self.tiene_permiso('gestionar_caja'):
            messagebox.showerror("Sin Permisos", "No tiene permisos para acceder a esta función.")
            return
        try:
            from caja import GestionCaja
            GestionCaja(ventana_padre=self.ventana, id_usuario=self.id_usuario)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo de caja: {str(e)}")

    def seguimiento_pedidos(self):
        """CORRECTO: Abrir módulo de seguimiento de pedidos"""
        if not self.tiene_permiso('seguimiento_pedidos'):
            messagebox.showerror("Sin Permisos", "No tiene permisos para acceder a esta función.")
            return
        try:
            from seguimiento_pedidos import SeguimientoPedidos
            SeguimientoPedidos(self.ventana, self.id_usuario, 'cajero')
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo de seguimiento: {str(e)}")

    def ver_reportes(self):
        """CORRECTO: Abrir módulo de reportes básicos"""
        if not self.tiene_permiso('ver_reportes'):
            messagebox.showerror("Sin Permisos", "No tiene permisos para acceder a esta función.")
            return
        try:
            from reportes import abrir_reportes
            abrir_reportes(self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo de reportes: {str(e)}")

    def gestionar_inventario(self):
        """CORREGIDO: Abrir módulo de productos (gestionar_productos_servicios)"""
        if not self.tiene_permiso('gestionar_inventario'):
            messagebox.showerror("Sin Permisos", "No tiene permisos para acceder a esta función.")
            return
        try:
            from gestionar_productos_servicios import GestionProductosServicios
            GestionProductosServicios(self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo de productos: {str(e)}")

    def aplicar_descuentos(self):
        """Función de descuentos (placeholder por ahora)"""
        if not self.tiene_permiso('aplicar_descuentos'):
            messagebox.showerror("Sin Permisos", "No tiene permisos para acceder a esta función.")
            return
        try:
            # Por ahora usar el módulo de promociones si existe
            from promos_descuentos import PromosDescuentosVentana
            PromosDescuentosVentana(self.ventana, id_usuario=self.id_usuario)
        except ImportError:
            messagebox.showinfo("Información", "El módulo de descuentos estará disponible próximamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo de descuentos: {str(e)}")

    def salir(self):
        """Cerrar sesión y volver al login"""
        if messagebox.askyesno("Confirmar salida", "¿Estás seguro de que deseas cerrar sesión?"):
            self.ventana.destroy()
            try:
                from loginP import App
                App()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la pantalla de login: {str(e)}")


if __name__ == "__main__":
    # Para pruebas (usar ID de usuario cajero válido)
    CajeroPanel(2)