"""
Módulo de Seguimiento de Pedidos Mejorado para el Sistema de Gestión de Lavandería
Permite visualizar, actualizar y gestionar el estado de los pedidos de manera más intuitiva y eficiente
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import os
import sys
import utileria as utl
from decimal import Decimal
from tkinter import simpledialog

# Asegurar que podamos importar módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

from conexion import conectar_bd


class SeguimientoPedidos:
    """Clase para el seguimiento integral de pedidos"""

    def __init__(self, ventana_padre=None, id_usuario=None, rol_usuario='admin'):
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Seguimiento de Pedidos - Lavandería")
        self.ventana.geometry("1200x800")
        self.ventana.config(bg="#f5f5f5")
        self.ventana.resizable(True, True)

        if ventana_padre:
            utl.centrar_ventana(self.ventana, 1200, 800)
            self.ventana.transient(ventana_padre)
            self.ventana.grab_set()

        # Variables de sesión
        self.id_usuario = id_usuario or 1
        self.rol_usuario = rol_usuario
        self.pedido_actual = None
        self.pedidos_data = []

        # Colores para estados
        self.colores_estado = {
            "Recibido": "#64b5f6",
            "En proceso": "#ffb74d",
            "Listo para entrega": "#81c784",
            "Entregado": "#4caf50",
            "Cancelado": "#e57373"
        }

        # Estados en orden cronológico
        self.estados_orden = ["Recibido", "En proceso", "Listo para entrega", "Entregado"]

        self.construir_interfaz()

        if not ventana_padre:
            self.ventana.mainloop()

    def construir_interfaz(self):
        """Construye la interfaz principal del módulo"""
        # Frame principal
        self.frame_principal = tk.Frame(self.ventana, bg="#f5f5f5")
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Encabezado
        self.crear_encabezado()

        # Panel principal con dos secciones
        self.panel_principal = tk.PanedWindow(self.frame_principal, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        self.panel_principal.pack(fill=tk.BOTH, expand=True, pady=10)

        # Panel izquierdo: Lista de pedidos y filtros
        self.panel_izquierdo = tk.Frame(self.panel_principal, bg="#f5f5f5", width=400)
        self.panel_principal.add(self.panel_izquierdo)

        # Panel derecho: Detalles del pedido
        self.panel_derecho = tk.Frame(self.panel_principal, bg="#f5f5f5")
        self.panel_principal.add(self.panel_derecho)

        # Configurar los paneles
        self.configurar_panel_izquierdo()
        self.configurar_panel_derecho()

        # Footer
        self.crear_footer()

    def crear_encabezado(self):
        """Crea el encabezado del módulo"""
        header_frame = tk.Frame(self.frame_principal, bg="#3a7ff6", relief=tk.RAISED, bd=1)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Título
        titulo = tk.Label(
            header_frame,
            text="SEGUIMIENTO DE PEDIDOS",
            font=("Helvetica", 18, "bold"),
            bg="#3a7ff6",
            fg="white"
        )
        titulo.pack(pady=10)

        # Resumen de pedidos
        self.resumen_frame = tk.Frame(header_frame, bg="#3a7ff6")
        self.resumen_frame.pack(fill=tk.X, padx=20, pady=5)

        # Labels para resumen
        self.lbl_total_pedidos = tk.Label(self.resumen_frame, text="Total: 0", bg="#3a7ff6", fg="white", font=("Helvetica", 12))
        self.lbl_total_pedidos.pack(side=tk.LEFT, padx=20)

        self.lbl_pendientes = tk.Label(self.resumen_frame, text="Pendientes: 0", bg="#3a7ff6", fg="white", font=("Helvetica", 12))
        self.lbl_pendientes.pack(side=tk.LEFT, padx=20)

        self.lbl_en_proceso = tk.Label(self.resumen_frame, text="En Proceso: 0", bg="#3a7ff6", fg="white", font=("Helvetica", 12))
        self.lbl_en_proceso.pack(side=tk.LEFT, padx=20)

        self.lbl_listos = tk.Label(self.resumen_frame, text="Listos: 0", bg="#3a7ff6", fg="white", font=("Helvetica", 12))
        self.lbl_listos.pack(side=tk.LEFT, padx=20)

    def cambiar_estado(self):
        """Cambia el estado del pedido actual y maneja automáticamente la conversión a venta"""
        if not self.pedido_actual:
            return

        # Crear ventana para cambiar estado
        ventana_estado = tk.Toplevel(self.ventana)
        ventana_estado.title("Cambiar Estado del Pedido")
        ventana_estado.geometry("400x350")
        ventana_estado.config(bg="#f5f5f5")
        ventana_estado.grab_set()

        utl.centrar_ventana(ventana_estado, 400, 350)

        frame_main = tk.Frame(ventana_estado, bg="#f5f5f5", padx=20, pady=20)
        frame_main.pack(fill=tk.BOTH, expand=True)

        titulo = tk.Label(frame_main, text=f"Pedido #{self.pedido_actual['id']}",
                          font=("Helvetica", 14, "bold"), bg="#f5f5f5")
        titulo.pack(pady=(0, 10))

        estado_actual = self.pedido_actual['estado']
        frame_actual = tk.Frame(frame_main, bg="#f5f5f5")
        frame_actual.pack(fill=tk.X, pady=10)

        tk.Label(frame_actual, text="Estado actual:", bg="#f5f5f5", font=("Helvetica", 11)).pack(side=tk.LEFT, padx=5)
        lbl_estado_actual = tk.Label(frame_actual, text=estado_actual, bg="#f5f5f5",
                                     font=("Helvetica", 11, "bold"),
                                     fg=self.colores_estado.get(estado_actual, "#000000"))
        lbl_estado_actual.pack(side=tk.LEFT, padx=5)

        frame_nuevo = tk.Frame(frame_main, bg="#f5f5f5")
        frame_nuevo.pack(fill=tk.X, pady=10)

        tk.Label(frame_nuevo, text="Nuevo estado:", bg="#f5f5f5", font=("Helvetica", 11)).pack(anchor=tk.W, padx=5)

        estados_disponibles = ["Recibido", "En proceso", "Listo para entrega", "Entregado", "Cancelado"]
        var_estado = tk.StringVar(value=estado_actual)

        for estado in estados_disponibles:
            rb = tk.Radiobutton(frame_nuevo, text=estado, value=estado, variable=var_estado,
                                bg="#f5f5f5", font=("Helvetica", 10))
            rb.pack(anchor=tk.W, padx=20)

        frame_obs = tk.Frame(frame_main, bg="#f5f5f5")
        frame_obs.pack(fill=tk.X, pady=10)

        tk.Label(frame_obs, text="Observaciones (opcional):", bg="#f5f5f5", font=("Helvetica", 11)).pack(anchor=tk.W)
        txt_obs = tk.Text(frame_obs, height=3, font=("Helvetica", 10))
        txt_obs.pack(fill=tk.X, pady=5)

        frame_botones = tk.Frame(frame_main, bg="#f5f5f5")
        frame_botones.pack(pady=20)

        def guardar_cambio():
            nuevo_estado = var_estado.get()
            observacion = txt_obs.get(1.0, tk.END).strip()

            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()

                cursor.execute("UPDATE pedidos SET estado = %s WHERE id_pedido = %s",
                               (nuevo_estado, self.pedido_actual['id']))

                try:
                    cursor.execute("""
                        INSERT INTO historial_estados_pedido 
                        (id_pedido, estado_anterior, estado_nuevo, observacion, id_usuario)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (self.pedido_actual['id'], estado_actual, nuevo_estado, observacion, self.id_usuario))
                except:
                    pass

                conexion.commit()
                conexion.close()

                # Si el nuevo estado es "Entregado", ofrecer convertir a venta
                if nuevo_estado == "Entregado":
                    self.finalizar_pedido_a_venta()

                messagebox.showinfo("Éxito", "Estado actualizado correctamente")
                ventana_estado.destroy()
                self.aplicar_filtros()

            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar estado: {str(e)}")

        btn_guardar = tk.Button(frame_botones, text="Guardar", bg="#3a7ff6", fg="white",
                                width=10, command=guardar_cambio)
        btn_guardar.pack(side=tk.LEFT, padx=5)

        btn_cancelar = tk.Button(frame_botones, text="Cancelar", bg="#e53935", fg="white",
                                 width=10, command=ventana_estado.destroy)
        btn_cancelar.pack(side=tk.LEFT, padx=5)

    def finalizar_pedido_a_venta(self):
        """Convierte un pedido entregado en una venta automáticamente"""
        if not self.pedido_actual:
            return

        confirmacion = messagebox.askyesno(
            "Registrar Venta",
            f"¿Desea registrar el pedido #{self.pedido_actual['id']} como una venta?"
        )

        if not confirmacion:
            return

        try:
            metodo_pago = simpledialog.askstring(
                "Método de pago",
                "Ingresa el método de pago (Efectivo, Tarjeta, Transferencia, Otro):"
            )

            if not metodo_pago:
                return

            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Verificar que hay una caja abierta
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("SELECT id_caja FROM caja WHERE fecha = %s AND hora_cierre IS NULL", (fecha_actual,))
            caja_abierta = cursor.fetchone()

            if not caja_abierta:
                messagebox.showerror("Error", "No hay una caja abierta para procesar la venta.")
                conexion.close()
                return

            id_caja_actual = caja_abierta[0]

            # Iniciar transacción
            cursor.execute("START TRANSACTION")

            # Crear venta a partir del pedido
            cursor.execute("""
                INSERT INTO ventas (id_usuario, id_cliente, total, metodo_pago)
                VALUES (%s, (SELECT id_cliente FROM pedidos WHERE id_pedido = %s), %s, %s)
            """, (
                self.id_usuario,
                self.pedido_actual['id'],
                self.pedido_actual['total'],
                metodo_pago
            ))

            id_venta = cursor.lastrowid

            # Copiar detalles del pedido a la venta
            cursor.execute("""
                INSERT INTO detalle_venta (id_venta, tipo_item, id_item, cantidad, subtotal)
                SELECT %s, dp.tipo_item, dp.id_item, dp.cantidad, 
                       (dp.cantidad * dp.precio_unitario) as subtotal
                FROM detalle_pedido dp
                WHERE dp.id_pedido = %s
            """, (id_venta, self.pedido_actual['id']))

            # Registrar pago
            cursor.execute("""
                INSERT INTO pagos (id_venta, monto, metodo_pago)
                VALUES (%s, %s, %s)
            """, (
                id_venta,
                self.pedido_actual['total'],
                metodo_pago
            ))

            # Actualizar puntos del cliente (1 punto por cada 10 pesos)
            puntos_ganados = int(float(self.pedido_actual['total']) / 10)
            cursor.execute("""
                UPDATE clientes 
                SET puntos = puntos + %s 
                WHERE id_cliente = (SELECT id_cliente FROM pedidos WHERE id_pedido = %s)
            """, (puntos_ganados, self.pedido_actual['id']))

            # Registrar la venta como ingreso en caja
            cursor.execute("""
                INSERT INTO movimientos_caja (id_caja, tipo, concepto, monto, hora, id_usuario)
                VALUES (%s, 'ingreso', %s, %s, %s, %s)
            """, (
                id_caja_actual,
                f'Venta #{id_venta} (Pedido #{self.pedido_actual["id"]})',
                self.pedido_actual['total'],
                datetime.now(),
                self.id_usuario
            ))

            # Actualizar totales de caja
            cursor.execute("""
                UPDATE caja 
                SET total_ingresos = total_ingresos + %s,
                    saldo_final = saldo_final + %s
                WHERE id_caja = %s
            """, (self.pedido_actual['total'], self.pedido_actual['total'], id_caja_actual))

            # Commit de la transacción
            cursor.execute("COMMIT")
            conexion.close()

            # Generar ticket
            try:
                from ticket import imprimir_ticket_venta
                imprimir_ticket_venta(id_venta, vista_previa=True, imprimir=True)
            except Exception as e:
                messagebox.showwarning("Advertencia", f"Venta registrada pero error al imprimir: {str(e)}")

            messagebox.showinfo(
                "Venta registrada",
                f"El pedido ha sido convertido a venta (ID: {id_venta})\n" +
                f"Puntos ganados: {puntos_ganados}\n" +
                f"La venta ha sido registrada en caja automáticamente."
            )

        except Exception as e:
            if 'conexion' in locals():
                conexion.rollback()
            messagebox.showerror("Error", f"No se pudo convertir el pedido a venta: {str(e)}")

    def configurar_panel_izquierdo(self):
        """Configura el panel izquierdo con filtros y lista de pedidos"""
        # Título del panel
        tk.Label(
            self.panel_izquierdo,
            text="Listado de Pedidos",
            font=("Helvetica", 14, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        ).pack(pady=(0, 10))

        # Frame de filtros
        frame_filtros = tk.LabelFrame(self.panel_izquierdo, text="Filtros", bg="#f5f5f5", padx=10, pady=10)
        frame_filtros.pack(fill=tk.X, padx=10, pady=5)

        # Fila 1: Estado y Periodo
        fila1 = tk.Frame(frame_filtros, bg="#f5f5f5")
        fila1.pack(fill=tk.X, pady=2)

        tk.Label(fila1, text="Estado:", bg="#f5f5f5").pack(side=tk.LEFT, padx=5)
        self.combo_estado = ttk.Combobox(
            fila1,
            values=["Todos"] + list(self.colores_estado.keys()),
            state="readonly",
            width=15
        )
        self.combo_estado.set("Todos")
        self.combo_estado.pack(side=tk.LEFT, padx=5)

        tk.Label(fila1, text="Periodo:", bg="#f5f5f5").pack(side=tk.LEFT, padx=5)
        self.combo_periodo = ttk.Combobox(
            fila1,
            values=["Hoy", "Ayer", "Esta semana", "Este mes", "Todos"],
            state="readonly",
            width=10
        )
        self.combo_periodo.set("Hoy")
        self.combo_periodo.pack(side=tk.LEFT, padx=5)

        # Fila 2: Búsqueda de cliente
        fila2 = tk.Frame(frame_filtros, bg="#f5f5f5")
        fila2.pack(fill=tk.X, pady=2)

        tk.Label(fila2, text="Cliente:", bg="#f5f5f5").pack(side=tk.LEFT, padx=5)
        self.entry_cliente = tk.Entry(fila2, width=25)
        self.entry_cliente.pack(side=tk.LEFT, padx=5)

        # Botones de filtro
        frame_botones_filtro = tk.Frame(frame_filtros, bg="#f5f5f5")
        frame_botones_filtro.pack(fill=tk.X, pady=5)

        btn_aplicar = tk.Button(
            frame_botones_filtro,
            text="🔍 Aplicar",
            bg="#3a7ff6",
            fg="white",
            command=self.aplicar_filtros
        )
        btn_aplicar.pack(side=tk.LEFT, padx=5)

        btn_limpiar = tk.Button(
            frame_botones_filtro,
            text="🔄 Limpiar",
            bg="#ff9800",
            fg="white",
            command=self.limpiar_filtros
        )
        btn_limpiar.pack(side=tk.LEFT, padx=5)

        # Tabla de pedidos
        frame_tabla = tk.Frame(self.panel_izquierdo, bg="#f5f5f5")
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columnas = ('id', 'cliente', 'fecha', 'estado', 'total', 'prioridad')
        self.tabla_pedidos = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=15)

        # Configurar columnas
        self.tabla_pedidos.heading('id', text='ID')
        self.tabla_pedidos.heading('cliente', text='Cliente')
        self.tabla_pedidos.heading('fecha', text='Fecha')
        self.tabla_pedidos.heading('estado', text='Estado')
        self.tabla_pedidos.heading('total', text='Total')
        self.tabla_pedidos.heading('prioridad', text='Prioridad')

        self.tabla_pedidos.column('id', width=50, anchor=tk.CENTER)
        self.tabla_pedidos.column('cliente', width=150)
        self.tabla_pedidos.column('fecha', width=100, anchor=tk.CENTER)
        self.tabla_pedidos.column('estado', width=120, anchor=tk.CENTER)
        self.tabla_pedidos.column('total', width=80, anchor=tk.E)
        self.tabla_pedidos.column('prioridad', width=80, anchor=tk.CENTER)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_pedidos.yview)
        self.tabla_pedidos.configure(yscrollcommand=scrollbar.set)

        self.tabla_pedidos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind para selección
        self.tabla_pedidos.bind('<<TreeviewSelect>>', self.mostrar_detalles)

        # Aplicar estilos a la tabla
        utl.aplicar_estilo_tabla(self.tabla_pedidos)

        # Cargar pedidos inicial
        self.aplicar_filtros()

    def configurar_panel_derecho(self):
        """Configura el panel derecho con detalles del pedido"""
        # Título del panel
        self.lbl_pedido_titulo = tk.Label(
            self.panel_derecho,
            text="Selecciona un pedido",
            font=("Helvetica", 14, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        )
        self.lbl_pedido_titulo.pack(pady=(10, 0))

        # Información general del pedido
        self.frame_info_pedido = tk.LabelFrame(self.panel_derecho, text="Información General", bg="#f5f5f5", padx=10, pady=10)
        self.frame_info_pedido.pack(fill=tk.X, padx=10, pady=10)

        # Variables para información
        self.var_cliente = tk.StringVar()
        self.var_fecha = tk.StringVar()
        self.var_estado = tk.StringVar()
        self.var_total = tk.StringVar()
        self.var_vendedor = tk.StringVar()
        self.var_prioridad = tk.StringVar()

        # Grid de información
        info_grid = tk.Frame(self.frame_info_pedido, bg="#f5f5f5")
        info_grid.pack(fill=tk.X)

        tk.Label(info_grid, text="Cliente:", font=("Helvetica", 11, "bold"), bg="#f5f5f5").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Label(info_grid, textvariable=self.var_cliente, font=("Helvetica", 11), bg="#f5f5f5").grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        tk.Label(info_grid, text="Fecha:", font=("Helvetica", 11, "bold"), bg="#f5f5f5").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Label(info_grid, textvariable=self.var_fecha, font=("Helvetica", 11), bg="#f5f5f5").grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

        tk.Label(info_grid, text="Estado:", font=("Helvetica", 11, "bold"), bg="#f5f5f5").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.lbl_estado = tk.Label(info_grid, textvariable=self.var_estado, font=("Helvetica", 11), bg="#f5f5f5")
        self.lbl_estado.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)

        tk.Label(info_grid, text="Vendedor:", font=("Helvetica", 11, "bold"), bg="#f5f5f5").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Label(info_grid, textvariable=self.var_vendedor, font=("Helvetica", 11), bg="#f5f5f5").grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)

        tk.Label(info_grid, text="Prioridad:", font=("Helvetica", 11, "bold"), bg="#f5f5f5").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Label(info_grid, textvariable=self.var_prioridad, font=("Helvetica", 11), bg="#f5f5f5").grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)

        tk.Label(info_grid, text="Total:", font=("Helvetica", 11, "bold"), bg="#f5f5f5").grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Label(info_grid, textvariable=self.var_total, font=("Helvetica", 14, "bold"), bg="#f5f5f5", fg="#3a7ff6").grid(row=5, column=1, sticky=tk.W, padx=5, pady=2)

        # Timeline visual del pedido
        self.frame_timeline = tk.LabelFrame(self.panel_derecho, text="Seguimiento", bg="#f5f5f5", padx=10, pady=10)
        self.frame_timeline.pack(fill=tk.X, padx=10, pady=10)

        self.canvas_timeline = tk.Canvas(self.frame_timeline, height=100, bg="#f5f5f5", highlightthickness=0)
        self.canvas_timeline.pack(fill=tk.X, padx=10, pady=10)

        # Detalles del pedido
        self.frame_detalles = tk.LabelFrame(self.panel_derecho, text="Items del Pedido", bg="#f5f5f5", padx=10, pady=10)
        self.frame_detalles.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columnas_detalles = ('servicio', 'cantidad', 'precio_unitario', 'subtotal')
        self.tabla_detalles = ttk.Treeview(self.frame_detalles, columns=columnas_detalles, show='headings', height=8)

        self.tabla_detalles.heading('servicio', text='Servicio')
        self.tabla_detalles.heading('cantidad', text='Cantidad')
        self.tabla_detalles.heading('precio_unitario', text='Precio Unit.')
        self.tabla_detalles.heading('subtotal', text='Subtotal')

        self.tabla_detalles.column('servicio', width=250)
        self.tabla_detalles.column('cantidad', width=80, anchor=tk.CENTER)
        self.tabla_detalles.column('precio_unitario', width=100, anchor=tk.E)
        self.tabla_detalles.column('subtotal', width=100, anchor=tk.E)

        self.tabla_detalles.pack(fill=tk.BOTH, expand=True)

        # Observaciones
        self.frame_observaciones = tk.LabelFrame(self.panel_derecho, text="Observaciones", bg="#f5f5f5", padx=10, pady=10)
        self.frame_observaciones.pack(fill=tk.X, padx=10, pady=10)

        self.txt_observaciones = tk.Text(self.frame_observaciones, height=3, font=("Helvetica", 11))
        self.txt_observaciones.pack(fill=tk.X, pady=5)
        self.txt_observaciones.config(state=tk.DISABLED)

        # Botones de acción
        self.frame_acciones = tk.Frame(self.panel_derecho, bg="#f5f5f5")
        self.frame_acciones.pack(fill=tk.X, padx=10, pady=10)

        # Primera fila de botones
        fila1_btn = tk.Frame(self.frame_acciones, bg="#f5f5f5")
        fila1_btn.pack(fill=tk.X, pady=2)

        self.btn_cambiar_estado = tk.Button(
            fila1_btn,
            text="Cambiar Estado",
            bg="#3a7ff6",
            fg="white",
            width=15,
            command=self.cambiar_estado,
            state=tk.DISABLED
        )
        self.btn_cambiar_estado.pack(side=tk.LEFT, padx=5)

        self.btn_cambiar_prioridad = tk.Button(
            fila1_btn,
            text="Cambiar Prioridad",
            bg="#ff9800",
            fg="white",
            width=15,
            command=self.cambiar_prioridad,
            state=tk.DISABLED
        )
        self.btn_cambiar_prioridad.pack(side=tk.LEFT, padx=5)

        self.btn_notificar = tk.Button(
            fila1_btn,
            text="Notificar Cliente",
            bg="#4caf50",
            fg="white",
            width=15,
            command=self.notificar_cliente,
            state=tk.DISABLED
        )
        self.btn_notificar.pack(side=tk.LEFT, padx=5)

        # Segunda fila de botones
        fila2_btn = tk.Frame(self.frame_acciones, bg="#f5f5f5")
        fila2_btn.pack(fill=tk.X, pady=2)

        self.btn_imprimir = tk.Button(
            fila2_btn,
            text="Imprimir Ticket",
            bg="#9c27b0",
            fg="white",
            width=15,
            command=self.imprimir_ticket,
            state=tk.DISABLED
        )
        self.btn_imprimir.pack(side=tk.LEFT, padx=5)



        self.btn_editar = tk.Button(
            fila2_btn,
            text="Editar Pedido",
            bg="#607d8b",
            fg="white",
            width=15,
            command=self.editar_pedido,
            state=tk.DISABLED
        )

        self.btn_finalizar_venta = tk.Button(
            fila2_btn,
            text="Finalizar a Venta",
            bg="#2196f3",
            fg="white",
            width=15,
            command=self.finalizar_pedido_a_venta,
            state=tk.DISABLED
        )
        self.btn_finalizar_venta.pack(side=tk.LEFT, padx=5)


        self.btn_editar.pack(side=tk.LEFT, padx=5)

        self.btn_eliminar = tk.Button(
            fila2_btn,
            text="Eliminar Pedido",
            bg="#f44336",
            fg="white",
            width=15,
            command=self.eliminar_pedido,
            state=tk.DISABLED
        )
        self.btn_eliminar.pack(side=tk.LEFT, padx=5)

        # Controlar permisos según rol
        if self.rol_usuario != 'admin':
            self.btn_eliminar.config(state=tk.DISABLED)

    def crear_footer(self):
        """Crea el footer con botones de navegación"""
        footer_frame = tk.Frame(self.frame_principal, bg="#f5f5f5", relief=tk.RAISED, bd=1)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

        # Botón volver
        btn_volver = tk.Button(
            footer_frame,
            text="← Volver",
            bg="#e53935",
            fg="white",
            font=("Helvetica", 11),
            width=10,
            command=self.ventana.destroy
        )
        btn_volver.pack(side=tk.RIGHT, padx=10, pady=5)

        # Botón actualizar
        btn_actualizar = tk.Button(
            footer_frame,
            text="🔄 Actualizar",
            bg="#4caf50",
            fg="white",
            font=("Helvetica", 11),
            width=12,
            command=self.aplicar_filtros
        )
        btn_actualizar.pack(side=tk.RIGHT, padx=10, pady=5)

    def aplicar_filtros(self):
        """Aplica los filtros seleccionados y carga los pedidos"""
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Construir consulta
            consulta = """
            SELECT p.id_pedido, c.nombre, p.fecha_pedido, p.estado, 
                   (SELECT SUM(dp.cantidad * dp.precio_unitario) 
                    FROM detalle_pedido dp 
                    WHERE dp.id_pedido = p.id_pedido) as total,
                   p.prioridad
            FROM pedidos p
            INNER JOIN clientes c ON p.id_cliente = c.id_cliente
            WHERE 1=1
            """

            parametros = []

            # Filtro de estado
            if self.combo_estado.get() != "Todos":
                consulta += " AND p.estado = %s"
                parametros.append(self.combo_estado.get())

            # Filtro de periodo
            periodo = self.combo_periodo.get()
            hoy = datetime.now().date()

            if periodo == "Hoy":
                consulta += " AND DATE(p.fecha_pedido) = %s"
                parametros.append(hoy)
            elif periodo == "Ayer":
                consulta += " AND DATE(p.fecha_pedido) = %s"
                parametros.append(hoy - timedelta(days=1))
            elif periodo == "Esta semana":
                inicio_semana = hoy - timedelta(days=hoy.weekday())
                consulta += " AND DATE(p.fecha_pedido) >= %s"
                parametros.append(inicio_semana)
            elif periodo == "Este mes":
                inicio_mes = hoy.replace(day=1)
                consulta += " AND DATE(p.fecha_pedido) >= %s"
                parametros.append(inicio_mes)

            # Filtro de cliente
            if self.entry_cliente.get().strip():
                consulta += " AND c.nombre LIKE %s"
                parametros.append(f"%{self.entry_cliente.get().strip()}%")

            consulta += " ORDER BY p.fecha_pedido DESC"

            # Ejecutar consulta
            cursor.execute(consulta, parametros)
            pedidos = cursor.fetchall()

            # Limpiar tabla
            for item in self.tabla_pedidos.get_children():
                self.tabla_pedidos.delete(item)

            # Cargar pedidos
            self.pedidos_data = []
            for pedido in pedidos:
                # Formatear valores
                fecha_formateada = utl.formatear_fecha(pedido[2], '%d/%m/%Y')
                total_formateado = f"${float(pedido[4] or 0):.2f}"
                prioridad = pedido[5] or "Normal"

                # Guardar data
                self.pedidos_data.append({
                    'id': pedido[0],
                    'cliente': pedido[1],
                    'fecha': pedido[2],
                    'estado': pedido[3],
                    'total': pedido[4],
                    'prioridad': prioridad
                })

                # Insertar en tabla
                item_id = self.tabla_pedidos.insert('', tk.END, values=(
                    pedido[0],
                    pedido[1],
                    fecha_formateada,
                    pedido[3],
                    total_formateado,
                    prioridad
                ), tags=(pedido[3],))

            # Aplicar colores
            for estado, color in self.colores_estado.items():
                self.tabla_pedidos.tag_configure(estado, background=color)

            # Actualizar resumen
            self.actualizar_resumen()

            conexion.close()

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar pedidos: {str(e)}")

    def actualizar_resumen(self):
        """Actualiza los contadores en el encabezado"""
        total = len(self.pedidos_data)
        pendientes = sum(1 for p in self.pedidos_data if p['estado'] == 'Recibido')
        en_proceso = sum(1 for p in self.pedidos_data if p['estado'] == 'En proceso')
        listos = sum(1 for p in self.pedidos_data if p['estado'] == 'Listo para entrega')

        self.lbl_total_pedidos.config(text=f"Total: {total}")
        self.lbl_pendientes.config(text=f"Pendientes: {pendientes}")
        self.lbl_en_proceso.config(text=f"En Proceso: {en_proceso}")
        self.lbl_listos.config(text=f"Listos: {listos}")

    def limpiar_filtros(self):
        """Limpia los filtros y recarga todos los pedidos"""
        self.combo_estado.set("Todos")
        self.combo_periodo.set("Hoy")
        self.entry_cliente.delete(0, tk.END)
        self.aplicar_filtros()

    def mostrar_detalles(self, event):
        """Muestra los detalles del pedido seleccionado"""
        seleccion = self.tabla_pedidos.selection()
        if not seleccion:
            return

        valores = self.tabla_pedidos.item(seleccion[0], 'values')
        id_pedido = valores[0]

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Obtener datos completos del pedido
            consulta = """
            SELECT p.id_pedido, c.nombre, c.correo, p.fecha_pedido, p.estado, 
                   (SELECT SUM(dp.cantidad * dp.precio_unitario) 
                    FROM detalle_pedido dp 
                    WHERE dp.id_pedido = p.id_pedido) as total,
                   p.observaciones, u.nombre, p.prioridad
            FROM pedidos p
            INNER JOIN clientes c ON p.id_cliente = c.id_cliente
            LEFT JOIN ventas v ON v.id_venta = p.id_pedido
            LEFT JOIN usuarios u ON v.id_usuario = u.id_usuario
            WHERE p.id_pedido = %s
            """
            cursor.execute(consulta, (id_pedido,))
            pedido = cursor.fetchone()

            if pedido:
                # Actualizar información general
                self.pedido_actual = {
                    'id': pedido[0],
                    'cliente': pedido[1],
                    'correo': pedido[2],
                    'fecha': pedido[3],
                    'estado': pedido[4],
                    'total': pedido[5],
                    'observaciones': pedido[6],
                    'vendedor': pedido[7] or "No asignado",
                    'prioridad': pedido[8] or "Normal"
                }

                self.lbl_pedido_titulo.config(text=f"Pedido #{id_pedido}")
                self.var_cliente.set(self.pedido_actual['cliente'])
                self.var_fecha.set(utl.formatear_fecha(self.pedido_actual['fecha'], '%d/%m/%Y %H:%M'))
                self.var_estado.set(self.pedido_actual['estado'])
                self.var_total.set(f"${float(self.pedido_actual['total'] or 0):.2f}")
                self.var_vendedor.set(self.pedido_actual['vendedor'])
                self.var_prioridad.set(self.pedido_actual['prioridad'])

                # Actualizar color del estado
                if self.pedido_actual['estado'] in self.colores_estado:
                    self.lbl_estado.config(fg=self.colores_estado[self.pedido_actual['estado']])

                # Cargar detalles del pedido
                self.cargar_detalles_items(id_pedido)

                # Actualizar observaciones
                self.txt_observaciones.config(state=tk.NORMAL)
                self.txt_observaciones.delete(1.0, tk.END)
                self.txt_observaciones.insert(tk.END, self.pedido_actual['observaciones'] or "")
                self.txt_observaciones.config(state=tk.DISABLED)

                # Dibujar timeline
                self.dibujar_timeline()

                # Habilitar botones
                self.habilitar_botones()

            conexion.close()

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles: {str(e)}")

    def cargar_detalles_items(self, id_pedido):
        """Carga los items del pedido en la tabla"""
        try:
            for item in self.tabla_detalles.get_children():
                self.tabla_detalles.delete(item)

            conexion = conectar_bd()
            cursor = conexion.cursor()

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
                    item[0],
                    item[1],
                    f"${float(item[2]):.2f}",
                    f"${float(item[3]):.2f}"
                )
                self.tabla_detalles.insert('', tk.END, values=valores)

            conexion.close()

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar items: {str(e)}")

    def dibujar_timeline(self):
        """Dibuja la línea de tiempo visual del pedido"""
        self.canvas_timeline.delete("all")

        if not self.pedido_actual:
            return

        # Obtener estado actual y su índice
        estado_actual = self.pedido_actual['estado']
        try:
            indice_actual = self.estados_orden.index(estado_actual)
        except ValueError:
            indice_actual = -1

        # Configuración
        width = self.canvas_timeline.winfo_width() - 20
        height = self.canvas_timeline.winfo_height()
        y_center = height // 2
        circle_radius = 15
        padding = 60

        # Dibujar línea base
        self.canvas_timeline.create_line(padding, y_center, width - padding, y_center,
                                       fill="#e0e0e0", width=4)

        # Dibujar línea de progreso
        if indice_actual >= 0:
            progress_x = padding + (width - 2*padding) * indice_actual / (len(self.estados_orden) - 1)
            self.canvas_timeline.create_line(padding, y_center, progress_x, y_center,
                                           fill="#3a7ff6", width=6)

        # Dibujar puntos para cada estado
        for i, estado in enumerate(self.estados_orden):
            x = padding + (width - 2*padding) * i / (len(self.estados_orden) - 1)

            # Determinar color del círculo
            if i <= indice_actual:
                fill_color = self.colores_estado.get(estado, "#3a7ff6")
                outline_color = "#ffffff"
                text_color = "#ffffff"
                font_weight = "bold"
            else:
                fill_color = "#e0e0e0"
                outline_color = "#cccccc"
                text_color = "#666666"
                font_weight = "normal"

            # Dibujar círculo
            self.canvas_timeline.create_oval(x - circle_radius, y_center - circle_radius,
                                           x + circle_radius, y_center + circle_radius,
                                           fill=fill_color, outline=outline_color, width=2)

            # Dibujar número
            self.canvas_timeline.create_text(x, y_center, text=str(i + 1),
                                           fill=text_color if i <= indice_actual else "#666666",
                                           font=("Helvetica", 10, font_weight))


            #print("Método usado:", self.canvas_timeline.create_text)

            # Dibujar etiqueta
            self.canvas_timeline.create_text(
                x,
                y_center + circle_radius + 20,
                text=estado,
                fill="#333333",
                font=("Helvetica", 9),
                width=80,  # ✅ reemplaza wraplength por width
                justify=tk.CENTER
            )



    def habilitar_botones(self):
        """Habilita los botones según el estado y permisos"""
        if self.pedido_actual:
            # Cambiar estado siempre habilitado
            self.btn_cambiar_estado.config(state=tk.NORMAL)

            # Cambiar prioridad habilitado para admin y cajero
            self.btn_cambiar_prioridad.config(state=tk.NORMAL)

            # Notificar solo si hay correo
            if self.pedido_actual.get('correo'):
                self.btn_notificar.config(state=tk.NORMAL)
            else:
                self.btn_notificar.config(state=tk.DISABLED)

            # Imprimir siempre habilitado
            self.btn_imprimir.config(state=tk.NORMAL)

            # Editar solo si no está entregado o cancelado
            if self.pedido_actual['estado'] not in ['Entregado', 'Cancelado']:
                self.btn_editar.config(state=tk.NORMAL)
            else:
                self.btn_editar.config(state=tk.DISABLED)

            # Eliminar solo para admin
            if self.rol_usuario == 'admin':
                self.btn_eliminar.config(state=tk.NORMAL)
            else:
                self.btn_eliminar.config(state=tk.DISABLED)

            if self.pedido_actual['estado'] == 'Entregado':
                self.btn_finalizar_venta.config(state=tk.NORMAL)
            else:
                self.btn_finalizar_venta.config(state=tk.DISABLED)

    def cambiar_estado(self):
        """Cambia el estado del pedido actual"""
        if not self.pedido_actual:
            return

        # Crear ventana para cambiar estado
        ventana_estado = tk.Toplevel(self.ventana)
        ventana_estado.title("Cambiar Estado del Pedido")
        ventana_estado.geometry("400x350")
        ventana_estado.config(bg="#f5f5f5")
        ventana_estado.grab_set()

        # Centrar ventana
        utl.centrar_ventana(ventana_estado, 400, 350)

        # Frame principal
        frame_main = tk.Frame(ventana_estado, bg="#f5f5f5", padx=20, pady=20)
        frame_main.pack(fill=tk.BOTH, expand=True)

        # Título
        titulo = tk.Label(frame_main, text=f"Pedido #{self.pedido_actual['id']}",
                         font=("Helvetica", 14, "bold"), bg="#f5f5f5")
        titulo.pack(pady=(0, 10))

        # Estado actual
        estado_actual = self.pedido_actual['estado']
        frame_actual = tk.Frame(frame_main, bg="#f5f5f5")
        frame_actual.pack(fill=tk.X, pady=10)

        tk.Label(frame_actual, text="Estado actual:", bg="#f5f5f5", font=("Helvetica", 11)).pack(side=tk.LEFT, padx=5)
        lbl_estado_actual = tk.Label(frame_actual, text=estado_actual, bg="#f5f5f5",
                                    font=("Helvetica", 11, "bold"),
                                    fg=self.colores_estado.get(estado_actual, "#000000"))
        lbl_estado_actual.pack(side=tk.LEFT, padx=5)

        # Nuevo estado
        frame_nuevo = tk.Frame(frame_main, bg="#f5f5f5")
        frame_nuevo.pack(fill=tk.X, pady=10)

        tk.Label(frame_nuevo, text="Nuevo estado:", bg="#f5f5f5", font=("Helvetica", 11)).pack(anchor=tk.W, padx=5)

        # Opciones de estado
        estados_disponibles = ["Recibido", "En proceso", "Listo para entrega", "Entregado", "Cancelado"]
        var_estado = tk.StringVar(value=estado_actual)

        for estado in estados_disponibles:
            rb = tk.Radiobutton(frame_nuevo, text=estado, value=estado, variable=var_estado,
                              bg="#f5f5f5", font=("Helvetica", 10))
            rb.pack(anchor=tk.W, padx=20)

        # Observaciones adicionales
        frame_obs = tk.Frame(frame_main, bg="#f5f5f5")
        frame_obs.pack(fill=tk.X, pady=10)

        tk.Label(frame_obs, text="Observaciones (opcional):", bg="#f5f5f5", font=("Helvetica", 11)).pack(anchor=tk.W)
        txt_obs = tk.Text(frame_obs, height=3, font=("Helvetica", 10))
        txt_obs.pack(fill=tk.X, pady=5)

        # Botones
        frame_botones = tk.Frame(frame_main, bg="#f5f5f5")
        frame_botones.pack(pady=20)

        def guardar_cambio():
            nuevo_estado = var_estado.get()
            observacion = txt_obs.get(1.0, tk.END).strip()

            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()

                # Actualizar estado
                cursor.execute("UPDATE pedidos SET estado = %s WHERE id_pedido = %s",
                              (nuevo_estado, self.pedido_actual['id']))

                # Registrar historial si existe la tabla
                try:
                    cursor.execute("""
                        INSERT INTO historial_estados_pedido 
                        (id_pedido, estado_anterior, estado_nuevo, observacion, id_usuario)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (self.pedido_actual['id'], estado_actual, nuevo_estado, observacion, self.id_usuario))
                except:
                    pass  # La tabla podría no existir

                conexion.commit()
                conexion.close()

                messagebox.showinfo("Éxito", "Estado actualizado correctamente")
                ventana_estado.destroy()
                self.aplicar_filtros()

            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar estado: {str(e)}")

        btn_guardar = tk.Button(frame_botones, text="Guardar", bg="#3a7ff6", fg="white",
                               width=10, command=guardar_cambio)
        btn_guardar.pack(side=tk.LEFT, padx=5)

        btn_cancelar = tk.Button(frame_botones, text="Cancelar", bg="#e53935", fg="white",
                                width=10, command=ventana_estado.destroy)
        btn_cancelar.pack(side=tk.LEFT, padx=5)

    def cambiar_prioridad(self):
        """Cambia la prioridad del pedido"""
        if not self.pedido_actual:
            return

        ventana_prioridad = tk.Toplevel(self.ventana)
        ventana_prioridad.title("Cambiar Prioridad")
        ventana_prioridad.geometry("300x250")
        ventana_prioridad.config(bg="#f5f5f5")
        ventana_prioridad.grab_set()

        utl.centrar_ventana(ventana_prioridad, 300, 250)

        frame_main = tk.Frame(ventana_prioridad, bg="#f5f5f5", padx=20, pady=20)
        frame_main.pack(fill=tk.BOTH, expand=True)

        titulo = tk.Label(frame_main, text=f"Pedido #{self.pedido_actual['id']}",
                         font=("Helvetica", 14, "bold"), bg="#f5f5f5")
        titulo.pack(pady=(0, 20))

        prioridades = ["Normal", "Urgente", "Alta"]
        var_prioridad = tk.StringVar(value=self.pedido_actual.get('prioridad', 'Normal'))

        for prioridad in prioridades:
            rb = tk.Radiobutton(frame_main, text=prioridad, value=prioridad, variable=var_prioridad,
                              bg="#f5f5f5", font=("Helvetica", 11))
            rb.pack(anchor=tk.W, pady=5)

        frame_botones = tk.Frame(frame_main, bg="#f5f5f5")
        frame_botones.pack(pady=20)

        def guardar_prioridad():
            nueva_prioridad = var_prioridad.get()
            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()
                cursor.execute("UPDATE pedidos SET prioridad = %s WHERE id_pedido = %s",
                              (nueva_prioridad, self.pedido_actual['id']))
                conexion.commit()
                conexion.close()

                messagebox.showinfo("Éxito", "Prioridad actualizada")
                ventana_prioridad.destroy()
                self.aplicar_filtros()

            except Exception as e:
                messagebox.showerror("Error", f"Error: {str(e)}")

        btn_guardar = tk.Button(frame_botones, text="Guardar", bg="#3a7ff6", fg="white",
                               width=10, command=guardar_prioridad)
        btn_guardar.pack(side=tk.LEFT, padx=5)

        btn_cancelar = tk.Button(frame_botones, text="Cancelar", bg="#e53935", fg="white",
                                width=10, command=ventana_prioridad.destroy)
        btn_cancelar.pack(side=tk.LEFT, padx=5)

    def notificar_cliente(self):
        """Envía notificación por correo al cliente"""
        if not self.pedido_actual or not self.pedido_actual.get('correo'):
            return

        try:
            from email_sender_mejorado import enviar_correo_html

            # Crear notificación HTML
            estado = self.pedido_actual['estado']
            html = f"""
            <h2>Actualización de su Pedido #{self.pedido_actual['id']}</h2>
            <p>Estimado/a {self.pedido_actual['cliente']},</p>
            <p>El estado de su pedido ha cambiado a: <strong>{estado}</strong></p>
            <hr>
            <h3>Detalles del Pedido:</h3>
            <p>ID del Pedido: {self.pedido_actual['id']}</p>
            <p>Fecha: {utl.formatear_fecha(self.pedido_actual['fecha'], '%d/%m/%Y %H:%M')}</p>
            <p>Total: ${float(self.pedido_actual['total'] or 0):.2f}</p>
            
            {f'<h3>Observaciones:</h3><p>{self.pedido_actual["observaciones"]}</p>' if self.pedido_actual.get('observaciones') else ''}
            
            <p>¡Gracias por confiar en nosotros!</p>
            <p><small>Este es un mensaje automático, por favor no responda.</small></p>
            """

            enviar_correo_html(
                self.pedido_actual['correo'],
                f"Actualización de Pedido #{self.pedido_actual['id']}",
                html
            )

            messagebox.showinfo("Éxito", "Notificación enviada correctamente")

        except Exception as e:
            messagebox.showerror("Error", f"Error al enviar notificación: {str(e)}")

    def imprimir_ticket(self):
        """Imprime el ticket del pedido"""
        if not self.pedido_actual:
            return

        try:
            from ticket import imprimir_ticket_pedido

            imprimir_ticket_pedido(
                self.pedido_actual['id'],
                vista_previa=True,
                imprimir=True
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al imprimir: {str(e)}")

    def editar_pedido(self):
        """Abre el módulo de pedidos para editar el pedido actual"""
        if not self.pedido_actual:
            return

        try:
            from pedidos import Pedidos
            # Crear instancia del módulo de pedidos
            pedidos_window = Pedidos(self.ventana)
            # Aquí podrías implementar la lógica para cargar el pedido actual en el editor

        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir editor: {str(e)}")

    def eliminar_pedido(self):
        """Elimina el pedido actual (solo admin)"""
        if not self.pedido_actual or self.rol_usuario != 'admin':
            return

        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de eliminar el pedido #{self.pedido_actual['id']}?\n\n"
            "Esta acción no se puede deshacer.",
            icon='warning'
        )

        if not confirmacion:
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Eliminar detalles del pedido
            cursor.execute("DELETE FROM detalle_pedido WHERE id_pedido = %s",
                          (self.pedido_actual['id'],))

            # Eliminar pedido
            cursor.execute("DELETE FROM pedidos WHERE id_pedido = %s",
                          (self.pedido_actual['id'],))

            conexion.commit()
            conexion.close()

            messagebox.showinfo("Éxito", "Pedido eliminado correctamente")
            self.aplicar_filtros()

        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar: {str(e)}")


# Función para abrir el módulo desde otras partes del sistema
def abrir_seguimiento_pedidos(ventana_padre=None, id_usuario=None, rol_usuario='admin'):
    return SeguimientoPedidos(ventana_padre, id_usuario, rol_usuario)



# Para pruebas independientes
if __name__ == "__main__":
    # Crear ventana para probar
    SeguimientoPedidos()