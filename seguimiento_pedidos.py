"""
Módulo de Seguimiento de Pedidos para el Sistema de Gestión de Lavandería
Permite visualizar, actualizar y dar seguimiento detallado a los pedidos
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import utileria as utl
from datetime import datetime, timedelta

# Asegurar que podamos importar módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Importar módulo de conexión
from conexion import conectar_bd


class SeguimientoPedidos:
    """Clase para el seguimiento de pedidos"""

    def __init__(self, ventana_padre=None):
        # Si hay una ventana padre, crear Toplevel en lugar de Tk
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Seguimiento de Pedidos - Lavandería")
        self.ventana.geometry("1000x700")
        self.ventana.config(bg="#f5f5f5")
        self.ventana.resizable(False, False)

        if ventana_padre:
            # Centrar la ventana si existe una ventana padre
            utl.centrar_ventana(self.ventana, 1000, 700)
            # Hacer esta ventana modal
            self.ventana.transient(ventana_padre)
            self.ventana.grab_set()

        # Pedido seleccionado actualmente
        self.pedido_actual = None

        # Colores para los estados de pedido
        self.colores_estado = {
            "Recibido": "#64b5f6",  # Azul claro
            "En proceso": "#ffb74d",  # Naranja
            "Listo para entrega": "#81c784",  # Verde claro
            "Entregado": "#4caf50"  # Verde
        }

        self.construir_interfaz()

        if not ventana_padre:
            self.ventana.mainloop()

    def construir_interfaz(self):
        """Construye la interfaz gráfica del módulo"""
        # Frame principal
        self.frame_principal = tk.Frame(self.ventana, bg="#f5f5f5")
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        titulo = tk.Label(
            self.frame_principal,
            text="SEGUIMIENTO DE PEDIDOS",
            font=("Helvetica", 20, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        )
        titulo.pack(pady=10)

        # Crear panel dividido en dos secciones
        panel = tk.PanedWindow(self.frame_principal, bg="#f5f5f5", orient=tk.HORIZONTAL)
        panel.pack(fill=tk.BOTH, expand=True, pady=10)

        # Panel izquierdo: Lista de pedidos
        self.panel_izquierdo = tk.Frame(panel, bg="#f5f5f5", width=400)
        panel.add(self.panel_izquierdo)

        # Panel derecho: Detalles del pedido
        self.panel_derecho = tk.Frame(panel, bg="#f5f5f5")
        panel.add(self.panel_derecho)

        # Configurar panel izquierdo
        self.configurar_panel_izquierdo()

        # Configurar panel derecho
        self.configurar_panel_derecho()

        # Botón para volver
        btn_volver = tk.Button(
            self.frame_principal,
            text="Volver",
            font=("Helvetica", 11),
            bg="#e53935",
            fg="white",
            width=10,
            cursor="hand2",
            command=self.ventana.destroy
        )
        btn_volver.pack(pady=10)

    def configurar_panel_izquierdo(self):
        """Configura el panel izquierdo con la lista de pedidos"""
        # Etiqueta
        tk.Label(
            self.panel_izquierdo,
            text="Listado de Pedidos",
            font=("Helvetica", 14, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        ).pack(pady=(0, 10))

        # Frame para filtros
        frame_filtros = tk.Frame(self.panel_izquierdo, bg="#f5f5f5")
        frame_filtros.pack(fill=tk.X, pady=5)

        # Filtro por estado
        tk.Label(
            frame_filtros,
            text="Estado:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.combo_estado = ttk.Combobox(
            frame_filtros,
            values=["Todos", "Recibido", "En proceso", "Listo para entrega", "Entregado"],
            width=15,
            state="readonly"
        )
        self.combo_estado.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.combo_estado.current(0)  # "Todos" por defecto
        self.combo_estado.bind("<<ComboboxSelected>>", lambda _: self.cargar_pedidos())

        # Filtro por periodo
        tk.Label(
            frame_filtros,
            text="Periodo:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self.combo_periodo = ttk.Combobox(
            frame_filtros,
            values=["Todos", "Hoy", "Ayer", "Esta semana", "Este mes"],
            width=15,
            state="readonly"
        )
        self.combo_periodo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.combo_periodo.current(0)  # "Todos" por defecto
        self.combo_periodo.bind("<<ComboboxSelected>>", lambda _: self.cargar_pedidos())

        # Botón de buscar por cliente
        btn_buscar = tk.Button(
            frame_filtros,
            text="🔍 Buscar Cliente",
            font=("Helvetica", 10),
            bg="#3a7ff6",
            fg="white",
            command=self.buscar_por_cliente
        )
        btn_buscar.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W + tk.E)

        # Botón de refrescar
        btn_refrescar = tk.Button(
            frame_filtros,
            text="🔄 Refrescar",
            font=("Helvetica", 10),
            bg="#3a7ff6",
            fg="white",
            command=self.cargar_pedidos
        )
        btn_refrescar.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W + tk.E)

        # Tabla de pedidos
        frame_tabla = tk.Frame(self.panel_izquierdo, bg="#f5f5f5")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10)

        columnas = ('id', 'cliente', 'fecha', 'estado')

        self.tabla_pedidos = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=15)

        # Aplicar estilo a la tabla
        utl.aplicar_estilo_tabla(self.tabla_pedidos)

        # Configurar encabezados
        self.tabla_pedidos.heading('id', text='ID')
        self.tabla_pedidos.heading('cliente', text='Cliente')
        self.tabla_pedidos.heading('fecha', text='Fecha')
        self.tabla_pedidos.heading('estado', text='Estado')

        # Configurar anchos
        self.tabla_pedidos.column('id', width=40, anchor=tk.CENTER)
        self.tabla_pedidos.column('cliente', width=140)
        self.tabla_pedidos.column('fecha', width=80, anchor=tk.CENTER)
        self.tabla_pedidos.column('estado', width=100, anchor=tk.CENTER)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_pedidos.yview)
        self.tabla_pedidos.configure(yscrollcommand=scrollbar.set)

        # Empaquetar tabla y scrollbar
        self.tabla_pedidos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Vincular evento de selección
        self.tabla_pedidos.bind("<<TreeviewSelect>>", self.mostrar_detalles_pedido)

        # Cargar pedidos iniciales
        self.cargar_pedidos()

    def configurar_panel_derecho(self):
        """Configura el panel derecho con los detalles del pedido"""
        # Etiqueta de título
        self.lbl_titulo_pedido = tk.Label(
            self.panel_derecho,
            text="Detalles del Pedido",
            font=("Helvetica", 14, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        )
        self.lbl_titulo_pedido.pack(pady=(0, 10))

        # Frame para información del pedido
        frame_info = tk.Frame(self.panel_derecho, bg="#f5f5f5")
        frame_info.pack(fill=tk.X, pady=5)

        # Variables para mostrar información
        self.var_cliente = tk.StringVar(value="")
        self.var_fecha = tk.StringVar(value="")
        self.var_estado = tk.StringVar(value="")
        self.var_total = tk.StringVar(value="")

        # Grid para información
        tk.Label(frame_info, text="Cliente:", font=("Helvetica", 11, "bold"), bg="#f5f5f5").grid(row=0, column=0,
                                                                                                 sticky=tk.W, padx=5,
                                                                                                 pady=3)
        tk.Label(frame_info, textvariable=self.var_cliente, font=("Helvetica", 11), bg="#f5f5f5").grid(row=0, column=1,
                                                                                                       sticky=tk.W,
                                                                                                       padx=5, pady=3)

        tk.Label(frame_info, text="Fecha:", font=("Helvetica", 11, "bold"), bg="#f5f5f5").grid(row=1, column=0,
                                                                                               sticky=tk.W, padx=5,
                                                                                               pady=3)
        tk.Label(frame_info, textvariable=self.var_fecha, font=("Helvetica", 11), bg="#f5f5f5").grid(row=1, column=1,
                                                                                                     sticky=tk.W,
                                                                                                     padx=5, pady=3)

        tk.Label(frame_info, text="Estado:", font=("Helvetica", 11, "bold"), bg="#f5f5f5").grid(row=2, column=0,
                                                                                                sticky=tk.W, padx=5,
                                                                                                pady=3)
        self.lbl_estado = tk.Label(frame_info, textvariable=self.var_estado, font=("Helvetica", 11), bg="#f5f5f5")
        self.lbl_estado.grid(row=2, column=1, sticky=tk.W, padx=5, pady=3)

        tk.Label(frame_info, text="Total:", font=("Helvetica", 11, "bold"), bg="#f5f5f5").grid(row=3, column=0,
                                                                                               sticky=tk.W, padx=5,
                                                                                               pady=3)
        tk.Label(frame_info, textvariable=self.var_total, font=("Helvetica", 11, "bold"), bg="#f5f5f5",
                 fg="#3a7ff6").grid(row=3, column=1, sticky=tk.W, padx=5, pady=3)

        # Separador
        ttk.Separator(self.panel_derecho, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Timeline del pedido
        frame_timeline = tk.Frame(self.panel_derecho, bg="#f5f5f5")
        frame_timeline.pack(fill=tk.X, pady=10)

        tk.Label(
            frame_timeline,
            text="Seguimiento del Pedido",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        ).pack(anchor=tk.W, pady=(0, 10))

        # Canvas para la línea de tiempo
        self.canvas_timeline = tk.Canvas(frame_timeline, width=550, height=120, bg="#f5f5f5", highlightthickness=0)
        self.canvas_timeline.pack(fill=tk.X, padx=10)

        # Separador
        ttk.Separator(self.panel_derecho, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Frame para detalles del pedido
        frame_detalles = tk.Frame(self.panel_derecho, bg="#f5f5f5")
        frame_detalles.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Label(
            frame_detalles,
            text="Items del Pedido",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        ).pack(anchor=tk.W, pady=(0, 10))

        # Tabla de items
        columnas_items = ('servicio', 'cantidad', 'precio_unitario', 'subtotal')

        self.tabla_items = ttk.Treeview(frame_detalles, columns=columnas_items, show='headings', height=8)

        # Configurar encabezados
        self.tabla_items.heading('servicio', text='Servicio')
        self.tabla_items.heading('cantidad', text='Cantidad')
        self.tabla_items.heading('precio_unitario', text='Precio Unit.')
        self.tabla_items.heading('subtotal', text='Subtotal')

        # Configurar anchos
        self.tabla_items.column('servicio', width=250)
        self.tabla_items.column('cantidad', width=80, anchor=tk.CENTER)
        self.tabla_items.column('precio_unitario', width=100, anchor=tk.CENTER)
        self.tabla_items.column('subtotal', width=100, anchor=tk.CENTER)

        # Scrollbar para la tabla
        scrollbar_items = ttk.Scrollbar(frame_detalles, orient=tk.VERTICAL, command=self.tabla_items.yview)
        self.tabla_items.configure(yscrollcommand=scrollbar_items.set)

        # Empaquetar tabla y scrollbar
        self.tabla_items.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_items.pack(side=tk.RIGHT, fill=tk.Y)

        # Observaciones
        frame_obs = tk.Frame(self.panel_derecho, bg="#f5f5f5")
        frame_obs.pack(fill=tk.X, pady=10)

        tk.Label(
            frame_obs,
            text="Observaciones:",
            font=("Helvetica", 11, "bold"),
            bg="#f5f5f5"
        ).pack(anchor=tk.W)

        self.txt_observaciones = tk.Text(frame_obs, height=3, width=50, font=("Helvetica", 10))
        self.txt_observaciones.pack(fill=tk.X, pady=5)
        self.txt_observaciones.config(state=tk.DISABLED)

        # Frame para botones de acción
        frame_acciones = tk.Frame(self.panel_derecho, bg="#f5f5f5")
        frame_acciones.pack(fill=tk.X, pady=10)

        # Botón para cambiar estado
        self.btn_cambiar_estado = tk.Button(
            frame_acciones,
            text="Cambiar Estado",
            font=("Helvetica", 11),
            bg="#3a7ff6",
            fg="white",
            width=15,
            cursor="hand2",
            command=self.cambiar_estado,
            state=tk.DISABLED
        )
        self.btn_cambiar_estado.pack(side=tk.LEFT, padx=5)

        # Botón para notificar al cliente
        self.btn_notificar = tk.Button(
            frame_acciones,
            text="Notificar Cliente",
            font=("Helvetica", 11),
            bg="#3a7ff6",
            fg="white",
            width=15,
            cursor="hand2",
            command=self.notificar_cliente,
            state=tk.DISABLED
        )
        self.btn_notificar.pack(side=tk.LEFT, padx=5)

        # Botón para imprimir ticket
        self.btn_imprimir = tk.Button(
            frame_acciones,
            text="Imprimir Ticket",
            font=("Helvetica", 11),
            bg="#3a7ff6",
            fg="white",
            width=15,
            cursor="hand2",
            command=self.imprimir_ticket,
            state=tk.DISABLED
        )
        self.btn_imprimir.pack(side=tk.LEFT, padx=5)

    def cargar_pedidos(self):
        """Carga los pedidos según los filtros seleccionados"""
        # Limpiar tabla
        for item in self.tabla_pedidos.get_children():
            self.tabla_pedidos.delete(item)

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Obtener filtros
            filtro_estado = self.combo_estado.get()
            filtro_periodo = self.combo_periodo.get()

            # Construir consulta base
            consulta = """
            SELECT p.id_pedido, c.nombre, p.fecha_pedido, p.estado
            FROM pedidos p
            INNER JOIN clientes c ON p.id_cliente = c.id_cliente
            WHERE 1=1
            """

            parametros = []

            # Aplicar filtro de estado
            if filtro_estado != "Todos":
                consulta += " AND p.estado = %s"
                parametros.append(filtro_estado)

            # Aplicar filtro de periodo
            if filtro_periodo != "Todos":
                hoy = datetime.now().date()
                if filtro_periodo == "Hoy":
                    consulta += " AND DATE(p.fecha_pedido) = %s"
                    parametros.append(hoy)
                elif filtro_periodo == "Ayer":
                    consulta += " AND DATE(p.fecha_pedido) = %s"
                    parametros.append(hoy - timedelta(days=1))
                elif filtro_periodo == "Esta semana":
                    # Inicio de la semana (lunes)
                    inicio_semana = hoy - timedelta(days=hoy.weekday())
                    consulta += " AND DATE(p.fecha_pedido) >= %s"
                    parametros.append(inicio_semana)
                elif filtro_periodo == "Este mes":
                    # Inicio del mes
                    inicio_mes = hoy.replace(day=1)
                    consulta += " AND DATE(p.fecha_pedido) >= %s"
                    parametros.append(inicio_mes)

            # Ordenar por fecha descendente
            consulta += " ORDER BY p.fecha_pedido DESC"

            # Ejecutar consulta
            cursor.execute(consulta, parametros)

            for pedido in cursor.fetchall():
                # Formatear fecha para mostrar
                fecha_formateada = utl.formatear_fecha(pedido[2], '%d/%m/%Y')

                valores = (
                    pedido[0],  # ID
                    pedido[1],  # Cliente
                    fecha_formateada,  # Fecha
                    pedido[3]  # Estado
                )

                # Insertar en la tabla con etiqueta de estado para el color
                item_id = self.tabla_pedidos.insert('', tk.END, values=valores, tags=(pedido[3],))

            # Configurar colores según estado
            for estado, color in self.colores_estado.items():
                self.tabla_pedidos.tag_configure(estado, background=color)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los pedidos: {str(e)}")

    def buscar_por_cliente(self):
        """Abre ventana para buscar pedidos por cliente"""
        # Crear ventana para buscar
        ventana_buscar = tk.Toplevel(self.ventana)
        ventana_buscar.title("Buscar por Cliente")
        ventana_buscar.geometry("400x150")
        ventana_buscar.config(bg="#f5f5f5")
        ventana_buscar.grab_set()  # Hacer modal

        # Centrar ventana
        utl.centrar_ventana(ventana_buscar, 400, 150)

        # Frame principal
        frame_principal = tk.Frame(ventana_buscar, bg="#f5f5f5")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Etiqueta
        tk.Label(
            frame_principal,
            text="Ingrese el nombre del cliente:",
            font=("Helvetica", 12),
            bg="#f5f5f5"
        ).pack(pady=(0, 10))

        # Campo de búsqueda
        entry_busqueda = tk.Entry(frame_principal, font=("Helvetica", 12), width=30)
        entry_busqueda.pack(pady=10)
        entry_busqueda.focus_set()  # Enfocar al abrir

        # Función para buscar
        def realizar_busqueda():
            texto = entry_busqueda.get().strip()
            if not texto:
                messagebox.showwarning("Campo vacío", "Por favor ingrese un nombre para buscar")
                return

            ventana_buscar.destroy()
            self.buscar_pedidos_cliente(texto)

        # Botones
        frame_botones = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_botones.pack(pady=10)

        # Botón buscar
        btn_buscar = tk.Button(
            frame_botones,
            text="Buscar",
            font=("Helvetica", 11),
            bg="#3a7ff6",
            fg="white",
            width=10,
            command=realizar_busqueda
        )
        btn_buscar.pack(side=tk.LEFT, padx=5)

        # Vincular Enter para buscar
        entry_busqueda.bind("<Return>", lambda event: realizar_busqueda())

        # Botón cancelar
        btn_cancelar = tk.Button(
            frame_botones,
            text="Cancelar",
            font=("Helvetica", 11),
            bg="#e53935",
            fg="white",
            width=10,
            command=ventana_buscar.destroy
        )
        btn_cancelar.pack(side=tk.LEFT, padx=5)

    def buscar_pedidos_cliente(self, texto_busqueda):
        """Busca pedidos por nombre del cliente"""
        # Limpiar tabla
        for item in self.tabla_pedidos.get_children():
            self.tabla_pedidos.delete(item)

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Consulta con filtro por nombre de cliente
            consulta = """
            SELECT p.id_pedido, c.nombre, p.fecha_pedido, p.estado
            FROM pedidos p
            INNER JOIN clientes c ON p.id_cliente = c.id_cliente
            WHERE c.nombre LIKE %s
            ORDER BY p.fecha_pedido DESC
            """

            cursor.execute(consulta, (f"%{texto_busqueda}%",))

            for pedido in cursor.fetchall():
                # Formatear fecha para mostrar
                fecha_formateada = utl.formatear_fecha(pedido[2], '%d/%m/%Y')

                valores = (
                    pedido[0],  # ID
                    pedido[1],  # Cliente
                    fecha_formateada,  # Fecha
                    pedido[3]  # Estado
                )

                # Insertar en la tabla con etiqueta de estado para el color
                item_id = self.tabla_pedidos.insert('', tk.END, values=valores, tags=(pedido[3],))

            # Configurar colores según estado
            for estado, color in self.colores_estado.items():
                self.tabla_pedidos.tag_configure(estado, background=color)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar pedidos: {str(e)}")

    def mostrar_detalles_pedido(self, event):
        """Muestra los detalles del pedido seleccionado"""
        # Obtener el pedido seleccionado
        seleccion = self.tabla_pedidos.selection()
        if not seleccion:
            return

        # Obtener ID del pedido
        valores = self.tabla_pedidos.item(seleccion[0], 'values')
        id_pedido = valores[0]

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Obtener datos del pedido
            consulta_pedido = """
            SELECT p.id_pedido, c.nombre, p.fecha_pedido, p.estado, 
                   (SELECT SUM(dp.cantidad * dp.precio_unitario) 
                    FROM detalle_pedido dp 
                    WHERE dp.id_pedido = p.id_pedido) as total,
                   p.observaciones,
                   c.correo
            FROM pedidos p
            INNER JOIN clientes c ON p.id_cliente = c.id_cliente
            WHERE p.id_pedido = %s
            """
            cursor.execute(consulta_pedido, (id_pedido,))
            pedido = cursor.fetchone()

            if not pedido:
                messagebox.showerror("Error", "No se encontró el pedido seleccionado")
                return

            # Guardar el pedido actual
            self.pedido_actual = {
                'id': pedido[0],
                'cliente': pedido[1],
                'fecha': pedido[2],
                'estado': pedido[3],
                'total': pedido[4] or 0,
                'observaciones': pedido[5] or "",
                'correo_cliente': pedido[6] or ""
            }

            # Actualizar título del panel
            self.lbl_titulo_pedido.config(text=f"Pedido #{id_pedido}")

            # Actualizar información
            self.var_cliente.set(self.pedido_actual['cliente'])
            self.var_fecha.set(utl.formatear_fecha(self.pedido_actual['fecha'], '%d/%m/%Y %H:%M'))
            self.var_estado.set(self.pedido_actual['estado'])
            self.var_total.set(f"${float(self.pedido_actual['total']):.2f}")

            # Actualizar color del estado
            if self.pedido_actual['estado'] in self.colores_estado:
                self.lbl_estado.config(fg=self.colores_estado[self.pedido_actual['estado']])

            # Actualizar observaciones
            self.txt_observaciones.config(state=tk.NORMAL)
            self.txt_observaciones.delete('1.0', tk.END)
            self.txt_observaciones.insert('1.0', self.pedido_actual['observaciones'])
            self.txt_observaciones.config(state=tk.DISABLED)

            # Cargar items del pedido
            self.cargar_items_pedido(id_pedido)

            # Dibujar timeline
            self.dibujar_timeline()

            # Habilitar botones
            self.btn_cambiar_estado.config(state=tk.NORMAL)
            # Solo habilitar notificación si hay correo de cliente
            if self.pedido_actual['correo_cliente']:
                self.btn_notificar.config(state=tk.NORMAL)
            else:
                self.btn_notificar.config(state=tk.DISABLED)

            self.btn_imprimir.config(state=tk.NORMAL)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los detalles del pedido: {str(e)}")

    def cargar_items_pedido(self, id_pedido):
        """Carga los items del pedido seleccionado"""
        # Limpiar tabla
        for item in self.tabla_items.get_children():
            self.tabla_items.delete(item)

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Obtener items del pedido
            consulta = """
            SELECT s.nombre, dp.cantidad, dp.precio_unitario, 
                   (dp.cantidad * dp.precio_unitario) as subtotal
            FROM detalle_pedido dp
            JOIN servicios s ON dp.id_item = s.id_servicio
            WHERE dp.id_pedido = %s AND dp.tipo_item = 'servicio'
            """

            cursor.execute(consulta, (id_pedido,))

            for item in cursor.fetchall():
                valores = (
                    item[0],  # Servicio
                    item[1],  # Cantidad
                    f"${float(item[2]):.2f}",  # Precio unitario
                    f"${float(item[3]):.2f}"  # Subtotal
                )
                self.tabla_items.insert('', tk.END, values=valores)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los items del pedido: {str(e)}")

    def dibujar_timeline(self):
        """Dibuja la línea de tiempo del pedido"""
        if not self.pedido_actual:
            return

        # Limpiar canvas
        self.canvas_timeline.delete("all")

        # Estados posibles en orden
        estados = ["Recibido", "En proceso", "Listo para entrega", "Entregado"]
        estado_actual = self.pedido_actual['estado']

        # Configuración del timeline
        ancho = self.canvas_timeline.winfo_width() - 20
        alto = self.canvas_timeline.winfo_height()
        radio_circulo = 15
        y_centro = alto // 2

        # Calcular espaciado
        espaciado = ancho // (len(estados) - 1) if len(estados) > 1 else ancho

        # Dibujar línea de progreso
        self.canvas_timeline.create_line(
            10, y_centro, ancho + 10, y_centro,
            fill="#e0e0e0", width=3
        )

        # Calcular hasta dónde está completado
        indice_actual = estados.index(estado_actual) if estado_actual in estados else -1

        if indice_actual >= 0:
            # Dibujar línea completada
            self.canvas_timeline.create_line(
                10, y_centro,
                10 + (indice_actual * espaciado), y_centro,
                fill="#4caf50", width=5
            )

        # Dibujar círculos para cada estado
        for i, estado in enumerate(estados):
            x = 10 + (i * espaciado)

            # Color del círculo según si está completado o no
            if estados.index(estado) <= indice_actual:
                color_circulo = self.colores_estado.get(estado, "#64b5f6")
                color_texto = "white"
            else:
                color_circulo = "#e0e0e0"
                color_texto = "#666666"

            # Dibujar círculo
            self.canvas_timeline.create_oval(
                x - radio_circulo, y_centro - radio_circulo,
                x + radio_circulo, y_centro + radio_circulo,
                fill=color_circulo, outline=""
            )

            # Dibujar número
            self.canvas_timeline.create_text(
                x, y_centro, text=str(i + 1),
                fill=color_texto, font=("Helvetica", 10, "bold")
            )

            # Dibujar etiqueta
            self.canvas_timeline.create_text(
                x, y_centro + radio_circulo + 15, text=estado,
                fill="#333333", font=("Helvetica", 9)
            )

    def cambiar_estado(self):
        """Abre ventana para cambiar el estado del pedido"""
        if not self.pedido_actual:
            return

        # Estados posibles en orden
        estados = ["Recibido", "En proceso", "Listo para entrega", "Entregado"]

        # Estado actual
        estado_actual = self.pedido_actual['estado']
        indice_actual = estados.index(estado_actual) if estado_actual in estados else -1

        # Determinar posibles estados siguientes
        # Sólo permite avanzar al siguiente estado o retroceder al anterior
        estados_posibles = []
        if indice_actual > 0:
            estados_posibles.append(estados[indice_actual - 1])  # Estado anterior
        if indice_actual < len(estados) - 1:
            estados_posibles.append(estados[indice_actual + 1])  # Estado siguiente

        if not estados_posibles:
            messagebox.showinfo("Información", "No hay estados disponibles para cambiar")
            return

        # Crear ventana para cambiar estado
        ventana_estado = tk.Toplevel(self.ventana)
        ventana_estado.title(f"Cambiar Estado del Pedido #{self.pedido_actual['id']}")
        ventana_estado.geometry("400x250")
        ventana_estado.config(bg="#f5f5f5")
        ventana_estado.grab_set()  # Hacer modal

        # Centrar ventana
        utl.centrar_ventana(ventana_estado, 400, 250)

        # Frame principal
        frame_principal = tk.Frame(ventana_estado, bg="#f5f5f5")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        tk.Label(
            frame_principal,
            text=f"CAMBIAR ESTADO DEL PEDIDO #{self.pedido_actual['id']}",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        ).pack(pady=(0, 20))

        # Estado actual
        frame_actual = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_actual.pack(fill=tk.X, pady=10)

        tk.Label(
            frame_actual,
            text="Estado actual:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        lbl_estado_actual = tk.Label(
            frame_actual,
            text=estado_actual,
            font=("Helvetica", 11, "bold"),
            bg="#f5f5f5",
            fg=self.colores_estado.get(estado_actual, "#333333")
        )
        lbl_estado_actual.pack(side=tk.LEFT, padx=5)

        # Nuevo estado
        frame_nuevo = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_nuevo.pack(fill=tk.X, pady=10)

        tk.Label(
            frame_nuevo,
            text="Nuevo estado:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        combo_nuevo_estado = ttk.Combobox(
            frame_nuevo,
            values=estados_posibles,
            width=15,
            state="readonly"
        )
        combo_nuevo_estado.pack(side=tk.LEFT, padx=5)
        combo_nuevo_estado.current(0)  # Seleccionar primer estado disponible

        # Botones
        frame_botones = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_botones.pack(fill=tk.X, pady=20)

        def actualizar_estado():
            nuevo_estado = combo_nuevo_estado.get()

            if not nuevo_estado:
                messagebox.showwarning("Estado requerido", "Por favor, selecciona un nuevo estado")
                return

            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()

                # Actualizar estado del pedido
                consulta = "UPDATE pedidos SET estado = %s WHERE id_pedido = %s"
                cursor.execute(consulta, (nuevo_estado, self.pedido_actual['id']))

                conexion.commit()
                conexion.close()

                messagebox.showinfo("Éxito", f"Estado del pedido actualizado a: {nuevo_estado}")
                ventana_estado.destroy()

                # Actualizar la vista
                self.cargar_pedidos()

                # Si hay algún pedido seleccionado después de recargar, mostrar sus detalles
                if self.tabla_pedidos.selection():
                    self.mostrar_detalles_pedido(None)
                else:
                    # Limpiar detalles si no hay selección
                    self.lbl_titulo_pedido.config(text="Detalles del Pedido")
                    self.var_cliente.set("")
                    self.var_fecha.set("")
                    self.var_estado.set("")
                    self.var_total.set("")
                    self.txt_observaciones.config(state=tk.NORMAL)
                    self.txt_observaciones.delete('1.0', tk.END)
                    self.txt_observaciones.config(state=tk.DISABLED)
                    self.pedido_actual = None

                    # Deshabilitar botones
                    self.btn_cambiar_estado.config(state=tk.DISABLED)
                    self.btn_notificar.config(state=tk.DISABLED)
                    self.btn_imprimir.config(state=tk.DISABLED)

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el estado: {str(e)}")

        btn_actualizar = tk.Button(
            frame_botones,
            text="Actualizar",
            font=("Helvetica", 11),
            bg="#3a7ff6",
            fg="white",
            width=10,
            cursor="hand2",
            command=actualizar_estado
        )
        btn_actualizar.pack(side=tk.LEFT, padx=5)

        btn_cancelar = tk.Button(
            frame_botones,
            text="Cancelar",
            font=("Helvetica", 11),
            bg="#e53935",
            fg="white",
            width=10,
            cursor="hand2",
            command=ventana_estado.destroy
        )
        btn_cancelar.pack(side=tk.RIGHT, padx=5)

    def notificar_cliente(self):
        """Envía una notificación por correo al cliente sobre el estado del pedido"""
        if not self.pedido_actual or not self.pedido_actual['correo_cliente']:
            messagebox.showwarning("Acción no disponible", "No se puede notificar al cliente (correo no disponible)")
            return

        # Crear ventana para enviar notificación
        ventana_notificar = tk.Toplevel(self.ventana)
        ventana_notificar.title(f"Notificar Cliente - Pedido #{self.pedido_actual['id']}")
        ventana_notificar.geometry("500x400")
        ventana_notificar.config(bg="#f5f5f5")
        ventana_notificar.grab_set()  # Hacer modal

        # Centrar ventana
        utl.centrar_ventana(ventana_notificar, 500, 400)

        # Frame principal
        frame_principal = tk.Frame(ventana_notificar, bg="#f5f5f5")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        tk.Label(
            frame_principal,
            text=f"NOTIFICAR CLIENTE - PEDIDO #{self.pedido_actual['id']}",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        ).pack(pady=(0, 20))

        # Información del cliente
        frame_cliente = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_cliente.pack(fill=tk.X, pady=10)

        tk.Label(
            frame_cliente,
            text=f"Cliente: {self.pedido_actual['cliente']}",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(anchor=tk.W)

        tk.Label(
            frame_cliente,
            text=f"Correo: {self.pedido_actual['correo_cliente']}",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(anchor=tk.W)

        # Tipo de notificación
        frame_tipo = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_tipo.pack(fill=tk.X, pady=10)

        tk.Label(
            frame_tipo,
            text="Tipo de notificación:",
            font=("Helvetica", 11, "bold"),
            bg="#f5f5f5"
        ).pack(anchor=tk.W)

        tipo_notificacion = tk.StringVar(value="estado")

        tk.Radiobutton(
            frame_tipo,
            text=f"Notificación de estado: {self.pedido_actual['estado']}",
            variable=tipo_notificacion,
            value="estado",
            bg="#f5f5f5",
            font=("Helvetica", 10)
        ).pack(anchor=tk.W, pady=2)

        tk.Radiobutton(
            frame_tipo,
            text="Recordatorio de recogida",
            variable=tipo_notificacion,
            value="recordatorio",
            bg="#f5f5f5",
            font=("Helvetica", 10)
        ).pack(anchor=tk.W, pady=2)

        tk.Radiobutton(
            frame_tipo,
            text="Mensaje personalizado",
            variable=tipo_notificacion,
            value="personalizado",
            bg="#f5f5f5",
            font=("Helvetica", 10)
        ).pack(anchor=tk.W, pady=2)

        # Mensaje personalizado
        frame_mensaje = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_mensaje.pack(fill=tk.X, pady=10)

        tk.Label(
            frame_mensaje,
            text="Mensaje adicional (opcional):",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(anchor=tk.W)

        txt_mensaje = tk.Text(frame_mensaje, height=6, width=50, font=("Helvetica", 10))
        txt_mensaje.pack(fill=tk.X, pady=5)

        # Botones
        frame_botones = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_botones.pack(fill=tk.X, pady=10)

        def enviar_notificacion():
            # Aquí implementarías la lógica para enviar el correo
            # Usando las funciones del módulo email_sender_mejorado.py

            # Simulamos el envío para esta demo
            tipo = tipo_notificacion.get()
            mensaje_adicional = txt_mensaje.get("1.0", tk.END).strip()

            messagebox.showinfo(
                "Notificación enviada",
                f"Se ha enviado la notificación tipo '{tipo}' al cliente {self.pedido_actual['cliente']}."
            )
            ventana_notificar.destroy()

        btn_enviar = tk.Button(
            frame_botones,
            text="Enviar Notificación",
            font=("Helvetica", 11),
            bg="#3a7ff6",
            fg="white",
            width=15,
            cursor="hand2",
            command=enviar_notificacion
        )
        btn_enviar.pack(side=tk.LEFT, padx=5)

        btn_cancelar = tk.Button(
            frame_botones,
            text="Cancelar",
            font=("Helvetica", 11),
            bg="#e53935",
            fg="white",
            width=10,
            cursor="hand2",
            command=ventana_notificar.destroy
        )
        btn_cancelar.pack(side=tk.RIGHT, padx=5)

    def imprimir_ticket(self):
        """Genera un ticket para el pedido seleccionado"""
        if not self.pedido_actual:
            return

        # Simulamos la impresión del ticket mostrando un preview
        ventana_ticket = tk.Toplevel(self.ventana)
        ventana_ticket.title(f"Ticket - Pedido #{self.pedido_actual['id']}")
        ventana_ticket.geometry("400x600")
        ventana_ticket.config(bg="white")
        ventana_ticket.grab_set()  # Hacer modal

        # Centrar ventana
        utl.centrar_ventana(ventana_ticket, 400, 600)

        # Frame principal
        frame_principal = tk.Frame(ventana_ticket, bg="white")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Contenido del ticket (simulado)
        tk.Label(
            frame_principal,
            text="LAVANDERÍA",
            font=("Helvetica", 16, "bold"),
            bg="white"
        ).pack(pady=(0, 5))

        tk.Label(
            frame_principal,
            text="Sistema de Gestión",
            font=("Helvetica", 12),
            bg="white"
        ).pack(pady=(0, 20))

        ttk.Separator(frame_principal, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        tk.Label(
            frame_principal,
            text=f"PEDIDO #{self.pedido_actual['id']}",
            font=("Helvetica", 14, "bold"),
            bg="white"
        ).pack(pady=5)

        tk.Label(
            frame_principal,
            text=f"Fecha: {utl.formatear_fecha(self.pedido_actual['fecha'], '%d/%m/%Y %H:%M')}",
            font=("Helvetica", 10),
            bg="white"
        ).pack(anchor=tk.W)

        tk.Label(
            frame_principal,
            text=f"Cliente: {self.pedido_actual['cliente']}",
            font=("Helvetica", 10),
            bg="white"
        ).pack(anchor=tk.W)

        tk.Label(
            frame_principal,
            text=f"Estado: {self.pedido_actual['estado']}",
            font=("Helvetica", 10),
            bg="white"
        ).pack(anchor=tk.W, pady=(0, 10))

        ttk.Separator(frame_principal, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Crear un frame para los items
        frame_items = tk.Frame(frame_principal, bg="white")
        frame_items.pack(fill=tk.X, pady=10)

        # Encabezados
        tk.Label(
            frame_items,
            text="Servicio",
            font=("Helvetica", 10, "bold"),
            bg="white"
        ).grid(row=0, column=0, sticky=tk.W, padx=5)

        tk.Label(
            frame_items,
            text="Cant.",
            font=("Helvetica", 10, "bold"),
            bg="white"
        ).grid(row=0, column=1, sticky=tk.E, padx=5)

        tk.Label(
            frame_items,
            text="Precio",
            font=("Helvetica", 10, "bold"),
            bg="white"
        ).grid(row=0, column=2, sticky=tk.E, padx=5)

        tk.Label(
            frame_items,
            text="Subtotal",
            font=("Helvetica", 10, "bold"),
            bg="white"
        ).grid(row=0, column=3, sticky=tk.E, padx=5)

        ttk.Separator(frame_principal, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        # Agregar items
        for i, item in enumerate(self.tabla_items.get_children()):
            valores = self.tabla_items.item(item, 'values')

            # Nombre servicio
            tk.Label(
                frame_items,
                text=valores[0],
                font=("Helvetica", 9),
                bg="white"
            ).grid(row=i + 1, column=0, sticky=tk.W, padx=5, pady=2)

            # Cantidad
            tk.Label(
                frame_items,
                text=valores[1],
                font=("Helvetica", 9),
                bg="white"
            ).grid(row=i + 1, column=1, sticky=tk.E, padx=5, pady=2)

            # Precio unitario
            tk.Label(
                frame_items,
                text=valores[2],
                font=("Helvetica", 9),
                bg="white"
            ).grid(row=i + 1, column=2, sticky=tk.E, padx=5, pady=2)

            # Subtotal
            tk.Label(
                frame_items,
                text=valores[3],
                font=("Helvetica", 9),
                bg="white"
            ).grid(row=i + 1, column=3, sticky=tk.E, padx=5, pady=2)

        ttk.Separator(frame_principal, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Total
        frame_total = tk.Frame(frame_principal, bg="white")
        frame_total.pack(fill=tk.X, pady=5)

        tk.Label(
            frame_total,
            text="TOTAL:",
            font=("Helvetica", 12, "bold"),
            bg="white"
        ).pack(side=tk.LEFT, padx=5)

        tk.Label(
            frame_total,
            text=f"${float(self.pedido_actual['total']):.2f}",
            font=("Helvetica", 12, "bold"),
            bg="white"
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Separator(frame_principal, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Observaciones
        if self.pedido_actual['observaciones']:
            tk.Label(
                frame_principal,
                text="Observaciones:",
                font=("Helvetica", 10, "bold"),
                bg="white"
            ).pack(anchor=tk.W)

            tk.Label(
                frame_principal,
                text=self.pedido_actual['observaciones'],
                font=("Helvetica", 9),
                bg="white",
                wraplength=350,
                justify=tk.LEFT
            ).pack(anchor=tk.W, pady=(0, 10))

        ttk.Separator(frame_principal, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Pie del ticket
        tk.Label(
            frame_principal,
            text="¡Gracias por su preferencia!",
            font=("Helvetica", 10, "bold"),
            bg="white"
        ).pack(pady=5)

        tk.Label(
            frame_principal,
            text=f"Fecha de impresión: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            font=("Helvetica", 8),
            bg="white"
        ).pack(pady=(10, 0))

        # Botones
        frame_botones = tk.Frame(frame_principal, bg="white")
        frame_botones.pack(pady=20)

        btn_imprimir = tk.Button(
            frame_botones,
            text="Imprimir",
            font=("Helvetica", 11),
            bg="#3a7ff6",
            fg="white",
            width=10,
            cursor="hand2",
            command=lambda: messagebox.showinfo("Impresión", "Enviando a impresora...")
        )
        btn_imprimir.pack(side=tk.LEFT, padx=5)

        btn_cerrar = tk.Button(
            frame_botones,
            text="Cerrar",
            font=("Helvetica", 11),
            bg="#e53935",
            fg="white",
            width=10,
            cursor="hand2",
            command=ventana_ticket.destroy
        )
        btn_cerrar.pack(side=tk.LEFT, padx=5)


# Para probar de forma independiente
if __name__ == "__main__":
    SeguimientoPedidos()