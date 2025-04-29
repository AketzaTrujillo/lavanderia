"""
Módulo de Historial de Cliente para el Sistema de Lavandería
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import utileria as utl
from datetime import datetime

# Asegurar que podamos importar módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Importar módulo de conexión
from conexion import conectar_bd

class HistorialCliente:
    """Clase para visualizar el historial de un cliente"""

    def __init__(self, id_cliente=None, ventana_padre=None):
        # Si hay una ventana padre, crear Toplevel en lugar de Tk
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Historial de Cliente - Lavandería")
        self.ventana.geometry("900x600")
        self.ventana.config(bg="#f5f5f5")
        self.ventana.resizable(False, False)

        # Cliente seleccionado
        self.id_cliente = id_cliente
        self.datos_cliente = None

        if ventana_padre:
            # Centrar la ventana si existe una ventana padre
            utl.centrar_ventana(self.ventana, 900, 600)
            # Hacer esta ventana modal
            self.ventana.transient(ventana_padre)
            self.ventana.grab_set()

        # Establecer ícono si existe
        try:
            if os.path.exists("Img/lavadora.ico"):
                self.ventana.iconbitmap("Img/lavadora.ico")
        except Exception:
            pass

        self.construir_interfaz()

        if not ventana_padre:
            self.ventana.mainloop()

    # El resto del código de la clase HistorialCliente sigue aquí...
    # Incluye métodos como construir_interfaz, cargar_cliente, etc.

    def construir_interfaz(self):
        """Construye la interfaz gráfica del módulo"""
        # Frame principal con padding
        self.frame_principal = tk.Frame(self.ventana, bg="#f5f5f5", padx=20, pady=20)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)

        # Si no hay cliente seleccionado, mostrar pantalla de selección
        if not self.id_cliente:
            self.mostrar_seleccion_cliente()
        else:
            # Cargar datos del cliente seleccionado
            self.cargar_cliente()
            if self.datos_cliente:
                self.mostrar_historial()
            else:
                self.mostrar_seleccion_cliente()

    def cargar_cliente(self):
        """Carga los datos del cliente seleccionado"""
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Obtener datos del cliente
            cursor.execute(
                "SELECT id_cliente, nombre, telefono, correo, puntos, fecha_registro FROM clientes WHERE id_cliente = %s",
                (self.id_cliente,)
            )

            cliente = cursor.fetchone()

            if cliente:
                self.datos_cliente = {
                    'id': cliente[0],
                    'nombre': cliente[1],
                    'telefono': cliente[2] or "No registrado",
                    'correo': cliente[3] or "No registrado",
                    'puntos': cliente[4],
                    'fecha_registro': cliente[5]
                }
            else:
                messagebox.showerror("Error", "No se encontró el cliente")
                self.datos_cliente = None

            conexion.close()

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos del cliente: {str(e)}")
            self.datos_cliente = None

    def mostrar_seleccion_cliente(self):
        """Muestra interfaz para seleccionar un cliente"""
        # Limpiar frame principal
        for widget in self.frame_principal.winfo_children():
            widget.destroy()

        # Título
        titulo_frame = tk.Frame(self.frame_principal, bg="#f5f5f5")
        titulo_frame.pack(fill=tk.X, pady=(0, 20))

        titulo = tk.Label(
            titulo_frame,
            text="SELECCIONAR CLIENTE",
            font=("Helvetica", 18, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        )
        titulo.pack()

        # Separador
        separador = ttk.Separator(self.frame_principal, orient="horizontal")
        separador.pack(fill=tk.X, pady=(0, 20))

        # Frame para búsqueda
        frame_busqueda = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_busqueda.pack(fill=tk.X, pady=10)

        tk.Label(
            frame_busqueda,
            text="Buscar cliente:",
            font=("Helvetica", 12),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        self.entry_buscar = tk.Entry(frame_busqueda, width=30, font=("Helvetica", 12))
        self.entry_buscar.pack(side=tk.LEFT, padx=5)

        # Vincular tecla Enter al buscador
        self.entry_buscar.bind("<Return>", lambda event: self.buscar_clientes(self.entry_buscar.get().strip()))

        btn_buscar = tk.Button(
            frame_busqueda,
            text="🔍 Buscar",
            font=("Helvetica", 10),
            bg="#3a7ff6",
            fg="white",
            padx=10,
            cursor="hand2",
            command=lambda: self.buscar_clientes(self.entry_buscar.get().strip())
        )
        btn_buscar.pack(side=tk.LEFT, padx=5)

        # Efecto hover
        btn_buscar.bind("<Enter>", lambda e: btn_buscar.config(bg="#1a5fce"))
        btn_buscar.bind("<Leave>", lambda e: btn_buscar.config(bg="#3a7ff6"))

        # Frame para la tabla
        frame_tabla = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10)

        # Tabla de clientes
        columnas = ('id', 'nombre', 'telefono', 'correo', 'puntos', 'fecha_registro')

        self.tabla_clientes = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=15)

        # Aplicar estilo a la tabla
        utl.aplicar_estilo_tabla(self.tabla_clientes)

        # Configurar encabezados
        self.tabla_clientes.heading('id', text='ID')
        self.tabla_clientes.heading('nombre', text='Nombre')
        self.tabla_clientes.heading('telefono', text='Teléfono')
        self.tabla_clientes.heading('correo', text='Correo')
        self.tabla_clientes.heading('puntos', text='Puntos')
        self.tabla_clientes.heading('fecha_registro', text='Fecha Registro')

        # Configurar anchos
        self.tabla_clientes.column('id', width=50, anchor=tk.CENTER)
        self.tabla_clientes.column('nombre', width=200)
        self.tabla_clientes.column('telefono', width=100, anchor=tk.CENTER)
        self.tabla_clientes.column('correo', width=150)
        self.tabla_clientes.column('puntos', width=80, anchor=tk.CENTER)
        self.tabla_clientes.column('fecha_registro', width=150, anchor=tk.CENTER)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_clientes.yview)
        self.tabla_clientes.configure(yscrollcommand=scrollbar.set)

        # Empaquetar tabla y scrollbar
        self.tabla_clientes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Botones de acción
        frame_botones = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_botones.pack(pady=10)

        btn_seleccionar = tk.Button(
            frame_botones,
            text="👁️ Ver Historial",
            font=("Helvetica", 11),
            bg="#3a7ff6",
            fg="white",
            width=12,
            cursor="hand2",
            command=self.seleccionar_cliente
        )
        btn_seleccionar.pack(side=tk.LEFT, padx=5)

        # Efecto hover
        btn_seleccionar.bind("<Enter>", lambda e: btn_seleccionar.config(bg="#1a5fce"))
        btn_seleccionar.bind("<Leave>", lambda e: btn_seleccionar.config(bg="#3a7ff6"))

        btn_volver = tk.Button(
            frame_botones,
            text="↩ Volver",
            font=("Helvetica", 11),
            bg="#e53935",
            fg="white",
            width=10,
            cursor="hand2",
            command=self.ventana.destroy
        )
        btn_volver.pack(side=tk.LEFT, padx=5)

        # Efecto hover
        btn_volver.bind("<Enter>", lambda e: btn_volver.config(bg="#c62828"))
        btn_volver.bind("<Leave>", lambda e: btn_volver.config(bg="#e53935"))

        # Cargar todos los clientes al iniciar
        self.cargar_clientes()

    def cargar_clientes(self):
        """Carga todos los clientes en la tabla"""
        # Limpiar tabla
        for item in self.tabla_clientes.get_children():
            self.tabla_clientes.delete(item)

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT id_cliente, nombre, telefono, correo, puntos, fecha_registro FROM clientes ORDER BY nombre")

            for cliente in cursor.fetchall():
                # Formatear fecha
                fecha = utl.formatear_fecha(cliente[5]) if cliente[5] else ""
                valores = (cliente[0], cliente[1], cliente[2] or "", cliente[3] or "", cliente[4], fecha)
                self.tabla_clientes.insert('', tk.END, values=valores)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los clientes: {str(e)}")

    def buscar_clientes(self, texto_busqueda):
        """Busca clientes según texto y actualiza la tabla"""
        # Limpiar tabla
        for item in self.tabla_clientes.get_children():
            self.tabla_clientes.delete(item)

        if not texto_busqueda:
            self.cargar_clientes()
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Búsqueda por nombre, teléfono o correo
            consulta = """
            SELECT id_cliente, nombre, telefono, correo, puntos, fecha_registro 
            FROM clientes 
            WHERE nombre LIKE %s OR telefono LIKE %s OR correo LIKE %s
            ORDER BY nombre
            """

            cursor.execute(consulta, (f"%{texto_busqueda}%", f"%{texto_busqueda}%", f"%{texto_busqueda}%"))

            for cliente in cursor.fetchall():
                # Formatear fecha
                fecha = utl.formatear_fecha(cliente[5]) if cliente[5] else ""
                valores = (cliente[0], cliente[1], cliente[2] or "", cliente[3] or "", cliente[4], fecha)
                self.tabla_clientes.insert('', tk.END, values=valores)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar clientes: {str(e)}")

    def seleccionar_cliente(self):
        """Selecciona un cliente de la tabla y muestra su historial"""
        seleccion = self.tabla_clientes.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un cliente para ver su historial")
            return

        # Obtener ID del cliente seleccionado
        self.id_cliente = self.tabla_clientes.item(seleccion[0], "values")[0]

        # Cargar datos del cliente y mostrar historial
        self.cargar_cliente()
        if self.datos_cliente:
            self.mostrar_historial()

    def cargar_cliente(self):
        """Carga los datos del cliente seleccionado"""
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Obtener datos del cliente
            cursor.execute(
                "SELECT id_cliente, nombre, telefono, correo, puntos, fecha_registro FROM clientes WHERE id_cliente = %s",
                (self.id_cliente,)
            )

            cliente = cursor.fetchone()

            if cliente:
                self.datos_cliente = {
                    'id': cliente[0],
                    'nombre': cliente[1],
                    'telefono': cliente[2] or "No registrado",
                    'correo': cliente[3] or "No registrado",
                    'puntos': cliente[4],
                    'fecha_registro': cliente[5]
                }
            else:
                messagebox.showerror("Error", "No se encontró el cliente")
                self.datos_cliente = None

            conexion.close()

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos del cliente: {str(e)}")
            self.datos_cliente = None

    def mostrar_historial(self):
        """Muestra el historial de pedidos y servicios del cliente"""
        # Limpiar frame principal
        for widget in self.frame_principal.winfo_children():
            widget.destroy()

        # Cabecera con información del cliente
        frame_cabecera = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_cabecera.pack(fill=tk.X, pady=(0, 20))

        titulo = tk.Label(
            frame_cabecera,
            text=f"HISTORIAL DE CLIENTE",
            font=("Helvetica", 18, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        )
        titulo.pack()

        subtitulo = tk.Label(
            frame_cabecera,
            text=f"{self.datos_cliente['nombre']}",
            font=("Helvetica", 14),
            bg="#f5f5f5",
            fg="#3a7ff6"
        )
        subtitulo.pack()

        # Separador
        separador = ttk.Separator(self.frame_principal, orient="horizontal")
        separador.pack(fill=tk.X, pady=(0, 10))

        # Información del cliente
        frame_info = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_info.pack(fill=tk.X, pady=10)

        # Datos básicos en dos columnas
        frame_col1 = tk.Frame(frame_info, bg="#f5f5f5")
        frame_col1.pack(side=tk.LEFT, padx=20, fill=tk.Y)

        frame_col2 = tk.Frame(frame_info, bg="#f5f5f5")
        frame_col2.pack(side=tk.LEFT, padx=20, fill=tk.Y)

        # Columna 1: Información de contacto
        tk.Label(
            frame_col1,
            text="Información de contacto",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5",
            fg="#333333"
        ).pack(anchor=tk.W, pady=(0, 5))

        tk.Label(
            frame_col1,
            text=f"Teléfono: {self.datos_cliente['telefono']}",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(anchor=tk.W, pady=2)

        tk.Label(
            frame_col1,
            text=f"Correo: {self.datos_cliente['correo']}",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(anchor=tk.W, pady=2)

        tk.Label(
            frame_col1,
            text=f"Fecha de registro: {utl.formatear_fecha(self.datos_cliente['fecha_registro'])}",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(anchor=tk.W, pady=2)

        # Columna 2: Información de puntos
        tk.Label(
            frame_col2,
            text="Información de fidelidad",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5",
            fg="#333333"
        ).pack(anchor=tk.W, pady=(0, 5))

        # Mostrar puntos con un estilo destacado
        frame_puntos = tk.Frame(frame_col2, bg="#e8f5e9", padx=10, pady=10, bd=1, relief=tk.GROOVE)
        frame_puntos.pack(anchor=tk.W, pady=5, fill=tk.X)

        tk.Label(
            frame_puntos,
            text="Puntos acumulados:",
            font=("Helvetica", 11),
            bg="#e8f5e9"
        ).pack(anchor=tk.W)

        tk.Label(
            frame_puntos,
            text=f"{self.datos_cliente['puntos']}",
            font=("Helvetica", 16, "bold"),
            bg="#e8f5e9",
            fg="#388e3c"
        ).pack(anchor=tk.W)

        # Separador antes de las pestañas
        ttk.Separator(self.frame_principal, orient="horizontal").pack(fill=tk.X, pady=10)

        # Crear notebook para pestañas
        style = ttk.Style()
        style.configure("TNotebook", background="#f5f5f5", borderwidth=0)
        style.configure("TNotebook.Tab", background="#ddd", padding=[10, 5], font=("Helvetica", 10))
        style.map("TNotebook.Tab", background=[("selected", "#3a7ff6")],
                  foreground=[("selected", "white"), ("!selected", "black")])

        notebook = ttk.Notebook(self.frame_principal)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Pestaña para pedidos
        tab_pedidos = tk.Frame(notebook, bg="#f5f5f5")
        notebook.add(tab_pedidos, text="Pedidos")

        # Pestaña para servicios detallados
        tab_servicios = tk.Frame(notebook, bg="#f5f5f5")
        notebook.add(tab_servicios, text="Servicios")

        # Pestaña para estadísticas
        tab_estadisticas = tk.Frame(notebook, bg="#f5f5f5")
        notebook.add(tab_estadisticas, text="Estadísticas")

        # Configurar pestaña de pedidos
        self.configurar_tab_pedidos(tab_pedidos)

        # Configurar pestaña de servicios
        self.configurar_tab_servicios(tab_servicios)

        # Configurar pestaña de estadísticas
        self.configurar_tab_estadisticas(tab_estadisticas)

        # Botón para volver
        frame_boton = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_boton.pack(fill=tk.X, pady=10)

        btn_volver = tk.Button(
            frame_boton,
            text="↩ Volver",
            font=("Helvetica", 11),
            bg="#e53935",
            fg="white",
            width=10,
            cursor="hand2",
            command=self.ventana.destroy
        )
        btn_volver.pack(side=tk.RIGHT, padx=10)

        # Efecto hover
        btn_volver.bind("<Enter>", lambda e: btn_volver.config(bg="#c62828"))
        btn_volver.bind("<Leave>", lambda e: btn_volver.config(bg="#e53935"))

    def configurar_tab_pedidos(self, tab):
        """Configura la pestaña de pedidos"""
        # Frame para la tabla
        frame_tabla = tk.Frame(tab, bg="#f5f5f5")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10)

        # Tabla de pedidos
        columnas = ('id', 'fecha', 'estado', 'total', 'observaciones')

        tabla_pedidos = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=10)

        # Aplicar estilo a la tabla
        utl.aplicar_estilo_tabla(tabla_pedidos)

        # Configurar encabezados
        tabla_pedidos.heading('id', text='ID')
        tabla_pedidos.heading('fecha', text='Fecha')
        tabla_pedidos.heading('estado', text='Estado')
        tabla_pedidos.heading('total', text='Total')
        tabla_pedidos.heading('observaciones', text='Observaciones')

        # Configurar anchos
        tabla_pedidos.column('id', width=50, anchor=tk.CENTER)
        tabla_pedidos.column('fecha', width=150, anchor=tk.CENTER)
        tabla_pedidos.column('estado', width=120, anchor=tk.CENTER)
        tabla_pedidos.column('total', width=100, anchor=tk.CENTER)
        tabla_pedidos.column('observaciones', width=300)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=tabla_pedidos.yview)
        tabla_pedidos.configure(yscrollcommand=scrollbar.set)

        # Empaquetar tabla y scrollbar
        tabla_pedidos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Cargar pedidos del cliente
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Consulta para obtener pedidos con su total
            consulta = """
            SELECT p.id_pedido, p.fecha_pedido, p.estado, 
                   (SELECT SUM(dp.cantidad * dp.precio_unitario) 
                    FROM detalle_pedido dp 
                    WHERE dp.id_pedido = p.id_pedido) as total,
                   p.observaciones
            FROM pedidos p
            WHERE p.id_cliente = %s
            ORDER BY p.fecha_pedido DESC
            """

            cursor.execute(consulta, (self.datos_cliente['id'],))

            # Colores para los estados
            colores_estado = {
                "Recibido": "#64b5f6",  # Azul claro
                "En proceso": "#ffb74d",  # Naranja
                "Listo para entrega": "#81c784",  # Verde claro
                "Entregado": "#4caf50"  # Verde
            }

            # Insertar datos en la tabla
            for pedido in cursor.fetchall():
                # Formatear fecha
                fecha = utl.formatear_fecha(pedido[1], '%d/%m/%Y %H:%M')

                # Formatear total
                total = utl.formatear_moneda(pedido[3]) if pedido[3] else "$0.00"

                # Configurar valores
                valores = (
                    pedido[0],  # ID
                    fecha,  # Fecha
                    pedido[2],  # Estado
                    total,  # Total
                    pedido[4] or ""  # Observaciones
                )

                # Insertar en tabla con tag para color
                tabla_pedidos.insert('', tk.END, values=valores, tags=(pedido[2],))

                # Configurar color según estado
                if pedido[2] in colores_estado:
                    tabla_pedidos.tag_configure(pedido[2], background=colores_estado[pedido[2]])

            conexion.close()

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar pedidos: {str(e)}")

        # Botón para ver detalles del pedido seleccionado
        frame_botones = tk.Frame(tab, bg="#f5f5f5")
        frame_botones.pack(fill=tk.X, pady=10)

        def ver_detalles_pedido():
            seleccion = tabla_pedidos.selection()

            if not seleccion:
                messagebox.showwarning("Selección requerida", "Por favor, selecciona un pedido para ver sus detalles")
                return

            # Obtener ID del pedido
            id_pedido = tabla_pedidos.item(seleccion[0], "values")[0]

            # Crear ventana para ver detalles
            ventana_detalles = tk.Toplevel(self.ventana)
            ventana_detalles.title(f"Detalles del Pedido #{id_pedido}")
            ventana_detalles.geometry("700x400")
            ventana_detalles.config(bg="#f5f5f5")
            ventana_detalles.grab_set()  # Hacer modal

            # Centrar ventana
            utl.centrar_ventana(ventana_detalles, 700, 400)

            # Establecer ícono si existe
            try:
                if os.path.exists("Img/lavadora.ico"):
                    ventana_detalles.iconbitmap("Img/lavadora.ico")
            except Exception:
                pass

            # Título
            tk.Label(
                ventana_detalles,
                text=f"DETALLES DEL PEDIDO #{id_pedido}",
                font=("Helvetica", 14, "bold"),
                bg="#f5f5f5",
                fg="#3a7ff6"
            ).pack(pady=(20, 10))

            # Separador
            ttk.Separator(ventana_detalles, orient="horizontal").pack(fill=tk.X, padx=20, pady=(0, 10))

            # Tabla de items
            frame_tabla_items = tk.Frame(ventana_detalles, bg="#f5f5f5")
            frame_tabla_items.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            columnas_items = ('servicio', 'cantidad', 'precio_unitario', 'subtotal')

            tabla_items = ttk.Treeview(frame_tabla_items, columns=columnas_items, show='headings')

            # Aplicar estilo a la tabla
            utl.aplicar_estilo_tabla(tabla_items)

            # Configurar encabezados
            tabla_items.heading('servicio', text='Servicio')
            tabla_items.heading('cantidad', text='Cantidad')
            tabla_items.heading('precio_unitario', text='Precio Unit.')
            tabla_items.heading('subtotal', text='Subtotal')

            # Configurar anchos
            tabla_items.column('servicio', width=300)
            tabla_items.column('cantidad', width=100, anchor=tk.CENTER)
            tabla_items.column('precio_unitario', width=100, anchor=tk.CENTER)
            tabla_items.column('subtotal', width=100, anchor=tk.CENTER)

            # Scrollbar para la tabla
            scrollbar_items = ttk.Scrollbar(frame_tabla_items, orient=tk.VERTICAL, command=tabla_items.yview)
            tabla_items.configure(yscrollcommand=scrollbar_items.set)

            # Empaquetar tabla y scrollbar
            tabla_items.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar_items.pack(side=tk.RIGHT, fill=tk.Y)

            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()

                # Obtener detalles del pedido
                consulta_items = """
                SELECT s.nombre, dp.cantidad, dp.precio_unitario, (dp.cantidad * dp.precio_unitario) as subtotal
                FROM detalle_pedido dp
                JOIN servicios s ON dp.id_item = s.id_servicio
                WHERE dp.id_pedido = %s AND dp.tipo_item = 'servicio'
                """

                cursor.execute(consulta_items, (id_pedido,))

                total = 0.0

                # Insertar datos en la tabla
                for item in cursor.fetchall():
                    valores_item = (
                        item[0],  # Servicio
                        item[1],  # Cantidad
                        utl.formatear_moneda(item[2]),  # Precio unitario
                        utl.formatear_moneda(item[3])  # Subtotal
                    )

                    tabla_items.insert('', tk.END, values=valores_item)
                    total += item[3]

                # Mostrar total
                frame_total = tk.Frame(ventana_detalles, bg="#f5f5f5")
                frame_total.pack(fill=tk.X, padx=20, pady=10)

                tk.Label(
                    frame_total,
                    text="TOTAL:",
                    font=("Helvetica", 12, "bold"),
                    bg="#f5f5f5"
                ).pack(side=tk.LEFT)

                tk.Label(
                    frame_total,
                    text=utl.formatear_moneda(total),
                    font=("Helvetica", 12, "bold"),
                    bg="#f5f5f5",
                    fg="#3a7ff6"
                ).pack(side=tk.LEFT, padx=10)

                conexion.close()

            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar detalles: {str(e)}")

            # Botón para cerrar
            btn_cerrar = tk.Button(
                ventana_detalles,
                text="✓ Cerrar",
                font=("Helvetica", 11),
                bg="#3a7ff6",
                fg="white",
                width=10,
                cursor="hand2",
                command=ventana_detalles.destroy
            )
            btn_cerrar.pack(pady=20)

            # Efecto hover
            btn_cerrar.bind("<Enter>", lambda e: btn_cerrar.config(bg="#1a5fce"))
            btn_cerrar.bind("<Leave>", lambda e: btn_cerrar.config(bg="#3a7ff6"))

        btn_detalles = tk.Button(
            frame_botones,
            text="👁️ Ver Detalles",
            font=("Helvetica", 10),
            bg="#3a7ff6",
            fg="white",
            padx=10,
            cursor="hand2",
            command=ver_detalles_pedido
        )
        btn_detalles.pack(side=tk.LEFT, padx=5)

        # Efecto hover
        btn_detalles.bind("<Enter>", lambda e: btn_detalles.config(bg="#1a5fce"))
        btn_detalles.bind("<Leave>", lambda e: btn_detalles.config(bg="#3a7ff6"))