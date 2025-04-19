import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from conexion import conectar_bd
import utileria as utl
from datetime import datetime


class Pedidos:
    def __init__(self, ventana_padre=None):
        # Si hay una ventana padre, crear Toplevel en lugar de Tk
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Módulo de Pedidos - Lavandería")
        self.ventana.geometry("1000x700")
        self.ventana.config(bg="#f5f5f5")
        self.ventana.resizable(False, False)

        if ventana_padre:
            # Centrar la ventana si existe una ventana padre
            utl.centrar_ventana(self.ventana, 1000, 700)
            # Hacer esta ventana modal
            self.ventana.transient(ventana_padre)
            self.ventana.grab_set()

        # Variables para el pedido
        self.items_pedido = []
        self.cliente_actual = None
        self.total_pedido = 0.0

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
        # Crear un notebook (pestañas)
        self.notebook = ttk.Notebook(self.ventana)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Pestaña para Nuevo Pedido
        self.tab_nuevo = tk.Frame(self.notebook, bg="#f5f5f5")
        self.notebook.add(self.tab_nuevo, text="Nuevo Pedido")

        # Pestaña para Lista de Pedidos
        self.tab_lista = tk.Frame(self.notebook, bg="#f5f5f5")
        self.notebook.add(self.tab_lista, text="Lista de Pedidos")

        # Configurar las pestañas
        self.configurar_tab_nuevo()
        self.configurar_tab_lista()

    def configurar_tab_nuevo(self):
        """Configura la pestaña para crear nuevos pedidos"""
        # Frame principal
        frame_principal = tk.Frame(self.tab_nuevo, bg="#f5f5f5")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        titulo = tk.Label(
            frame_principal,
            text="Nuevo Pedido",
            font=("Helvetica", 20, "bold"),
            bg="#f5f5f5",
            fg="#303f9f"
        )
        titulo.pack(pady=10)

        # Frame superior para selección de cliente
        frame_cliente = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_cliente.pack(fill=tk.X, pady=10)

        lbl_cliente = tk.Label(
            frame_cliente,
            text="Cliente:",
            font=("Helvetica", 12),
            bg="#f5f5f5"
        )
        lbl_cliente.pack(side=tk.LEFT, padx=5)

        self.lbl_cliente_seleccionado = tk.Label(
            frame_cliente,
            text="No seleccionado",
            font=("Helvetica", 12),
            bg="#f5f5f5",
            fg="#777777"
        )
        self.lbl_cliente_seleccionado.pack(side=tk.LEFT, padx=5)

        btn_seleccionar_cliente = tk.Button(
            frame_cliente,
            text="Seleccionar Cliente",
            font=("Helvetica", 10),
            bg="#303f9f",
            fg="white",
            command=self.seleccionar_cliente
        )
        btn_seleccionar_cliente.pack(side=tk.LEFT, padx=10)

        # Frame para servicios disponibles
        frame_servicios = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_servicios.pack(fill=tk.BOTH, expand=True, pady=10)

        lbl_servicios = tk.Label(
            frame_servicios,
            text="Servicios disponibles:",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5"
        )
        lbl_servicios.pack(anchor=tk.W, pady=5)

        # Frame para búsqueda
        frame_busqueda = tk.Frame(frame_servicios, bg="#f5f5f5")
        frame_busqueda.pack(fill=tk.X, pady=5)

        lbl_buscar = tk.Label(
            frame_busqueda,
            text="Buscar:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        lbl_buscar.pack(side=tk.LEFT, padx=5)

        self.entry_buscar_servicio = tk.Entry(frame_busqueda, width=30, font=("Helvetica", 11))
        self.entry_buscar_servicio.pack(side=tk.LEFT, padx=5)

        btn_buscar = tk.Button(
            frame_busqueda,
            text="Buscar",
            font=("Helvetica", 10),
            bg="#303f9f",
            fg="white",
            command=lambda: self.buscar_servicios(self.entry_buscar_servicio.get().strip())
        )
        btn_buscar.pack(side=tk.LEFT, padx=5)

        # Tabla de servicios
        frame_tabla_servicios = tk.Frame(frame_servicios, bg="#f5f5f5")
        frame_tabla_servicios.pack(fill=tk.BOTH, expand=True, pady=5)

        columnas = ('id', 'nombre', 'descripcion', 'precio', 'tiempo')

        self.tabla_servicios = ttk.Treeview(frame_tabla_servicios, columns=columnas, show='headings', height=6)

        # Configurar encabezados
        self.tabla_servicios.heading('id', text='ID')
        self.tabla_servicios.heading('nombre', text='Nombre')
        self.tabla_servicios.heading('descripcion', text='Descripción')
        self.tabla_servicios.heading('precio', text='Precio')
        self.tabla_servicios.heading('tiempo', text='Tiempo Est.')

        # Configurar anchos
        self.tabla_servicios.column('id', width=50, anchor=tk.CENTER)
        self.tabla_servicios.column('nombre', width=150)
        self.tabla_servicios.column('descripcion', width=300)
        self.tabla_servicios.column('precio', width=100, anchor=tk.CENTER)
        self.tabla_servicios.column('tiempo', width=100, anchor=tk.CENTER)

        # Scrollbar para la tabla
        scrollbar_servicios = ttk.Scrollbar(frame_tabla_servicios, orient=tk.VERTICAL,
                                            command=self.tabla_servicios.yview)
        self.tabla_servicios.configure(yscrollcommand=scrollbar_servicios.set)

        # Empaquetar tabla y scrollbar
        self.tabla_servicios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_servicios.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame para agregar servicio
        frame_agregar = tk.Frame(frame_servicios, bg="#f5f5f5")
        frame_agregar.pack(fill=tk.X, pady=10)

        lbl_cantidad = tk.Label(
            frame_agregar,
            text="Cantidad:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        lbl_cantidad.pack(side=tk.LEFT, padx=5)

        self.entry_cantidad = tk.Entry(frame_agregar, width=5, font=("Helvetica", 11))
        self.entry_cantidad.pack(side=tk.LEFT, padx=5)
        self.entry_cantidad.insert(0, "1")  # Valor por defecto

        btn_agregar = tk.Button(
            frame_agregar,
            text="Agregar al pedido",
            font=("Helvetica", 10),
            bg="#303f9f",
            fg="white",
            command=self.agregar_servicio
        )
        btn_agregar.pack(side=tk.LEFT, padx=10)

        # Frame para detalles del pedido
        frame_detalles = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_detalles.pack(fill=tk.BOTH, expand=True, pady=10)

        lbl_detalles = tk.Label(
            frame_detalles,
            text="Detalles del pedido:",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5"
        )
        lbl_detalles.pack(anchor=tk.W, pady=5)

        # Tabla de detalles
        frame_tabla_detalles = tk.Frame(frame_detalles, bg="#f5f5f5")
        frame_tabla_detalles.pack(fill=tk.BOTH, expand=True, pady=5)

        columnas_detalle = ('servicio', 'cantidad', 'precio_unitario', 'subtotal')

        self.tabla_detalles = ttk.Treeview(frame_tabla_detalles, columns=columnas_detalle, show='headings', height=5)

        # Configurar encabezados
        self.tabla_detalles.heading('servicio', text='Servicio')
        self.tabla_detalles.heading('cantidad', text='Cantidad')
        self.tabla_detalles.heading('precio_unitario', text='Precio Unit.')
        self.tabla_detalles.heading('subtotal', text='Subtotal')

        # Configurar anchos
        self.tabla_detalles.column('servicio', width=300)
        self.tabla_detalles.column('cantidad', width=100, anchor=tk.CENTER)
        self.tabla_detalles.column('precio_unitario', width=100, anchor=tk.CENTER)
        self.tabla_detalles.column('subtotal', width=100, anchor=tk.CENTER)

        # Scrollbar para la tabla
        scrollbar_detalles = ttk.Scrollbar(frame_tabla_detalles, orient=tk.VERTICAL, command=self.tabla_detalles.yview)
        self.tabla_detalles.configure(yscrollcommand=scrollbar_detalles.set)

        # Empaquetar tabla y scrollbar
        self.tabla_detalles.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_detalles.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame para botones de acción sobre detalles
        frame_accion = tk.Frame(frame_detalles, bg="#f5f5f5")
        frame_accion.pack(fill=tk.X, pady=5)

        btn_quitar = tk.Button(
            frame_accion,
            text="Quitar item",
            font=("Helvetica", 10),
            bg="#e53935",
            fg="white",
            command=self.quitar_item
        )
        btn_quitar.pack(side=tk.LEFT, padx=5)

        btn_limpiar = tk.Button(
            frame_accion,
            text="Limpiar todo",
            font=("Helvetica", 10),
            bg="#e53935",
            fg="white",
            command=self.limpiar_pedido
        )
        btn_limpiar.pack(side=tk.LEFT, padx=5)

        # Frame para observaciones y total
        frame_observaciones = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_observaciones.pack(fill=tk.X, pady=10)

        lbl_observaciones = tk.Label(
            frame_observaciones,
            text="Observaciones:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        lbl_observaciones.pack(anchor=tk.W, pady=5)

        self.txt_observaciones = tk.Text(frame_observaciones, height=3, font=("Helvetica", 11))
        self.txt_observaciones.pack(fill=tk.X, pady=5)

        # Frame para total y guardar
        frame_total = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_total.pack(fill=tk.X, pady=10)

        lbl_total_titulo = tk.Label(
            frame_total,
            text="TOTAL:",
            font=("Helvetica", 14, "bold"),
            bg="#f5f5f5"
        )
        lbl_total_titulo.pack(side=tk.LEFT, padx=5)

        self.lbl_total = tk.Label(
            frame_total,
            text="$0.00",
            font=("Helvetica", 14, "bold"),
            bg="#f5f5f5",
            fg="#303f9f"
        )
        self.lbl_total.pack(side=tk.LEFT, padx=5)

        btn_guardar = tk.Button(
            frame_total,
            text="Guardar Pedido",
            font=("Helvetica", 12, "bold"),
            bg="#303f9f",
            fg="white",
            command=self.guardar_pedido
        )
        btn_guardar.pack(side=tk.RIGHT, padx=10)