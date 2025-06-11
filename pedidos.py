"""
Módulo de Pedidos para el Sistema de Gestión de Lavandería
Permite crear, visualizar y gestionar el estado de los pedidos
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import sys
import utileria as utl
from datetime import datetime

# Asegurar que podamos importar módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Importar módulo de conexión
from conexion import conectar_bd


class Pedidos:
    def __init__(self, ventana_padre=None, id_usuario=None):
        # Si hay una ventana padre, crear Toplevel en lugar de Tk
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.id_usuario_actual = id_usuario if id_usuario is not None else 1
        print(f"DEBUG - ID usuario en pedidos: {self.id_usuario_actual}")

        self.ventana.title("Módulo de Pedidos - Lavandería")

        self.ventana.geometry("1400x800")
        self.ventana.config(bg="#f5f5f5")
        self.ventana.resizable(True, True)

        if ventana_padre:
            # Centrar la ventana si existe una ventana padre
            utl.centrar_ventana(self.ventana, 1400, 800)
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
        self.tab_nuevo = tk.Frame(self.notebook, bg="#f5f7fa")
        self.notebook.add(self.tab_nuevo, text="Nuevo Pedido")

        # Pestaña para Lista de Pedidos
        self.tab_lista = tk.Frame(self.notebook, bg="#f5f7fa")
        self.notebook.add(self.tab_lista, text="Lista de Pedidos")

        # Configurar las pestañas
        self.configurar_tab_nuevo()
        self.configurar_tab_lista()

    def configurar_tab_nuevo(self):
        # Frame principal con dos columnas
        frame_principal = tk.Frame(self.tab_nuevo, bg="#f5f7fa")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        tk.Label(
            frame_principal,
            text="Nuevo Pedido",
            font=("Helvetica", 22, "bold"),
            bg="#f5f7fa",
            fg="#1976D2"
        ).pack(pady=(0, 18))

        # Frame de columnas
        frame_columnas = tk.Frame(frame_principal, bg="#f5f7fa")
        frame_columnas.pack(fill=tk.BOTH, expand=True)

        # ==================== COLUMNA IZQUIERDA ====================
        col_izq = tk.Frame(frame_columnas, bg="#f5f7fa")
        col_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Cliente
        frame_cliente = tk.Frame(col_izq, bg="#e3f2fd", bd=1, relief="solid")
        frame_cliente.pack(fill=tk.X, pady=(0, 18), padx=5)

        tk.Label(frame_cliente, text="Cliente:", font=("Helvetica", 13, "bold"), bg="#e3f2fd", fg="#1565C0").pack(side=tk.LEFT, padx=10, pady=8)
        self.lbl_cliente_seleccionado = tk.Label(frame_cliente, text="No seleccionado", font=("Helvetica", 13), bg="#e3f2fd", fg="#757575")
        self.lbl_cliente_seleccionado.pack(side=tk.LEFT, padx=10)
        btn_seleccionar_cliente = tk.Button(
            frame_cliente, text="Seleccionar Cliente", font=("Helvetica", 11, "bold"),
            bg="#1976D2", fg="white", activebackground="#1565C0", activeforeground="white",
            relief="flat", cursor="hand2", command=self.seleccionar_cliente
        )
        btn_seleccionar_cliente.pack(side=tk.RIGHT, padx=10, pady=8)

        # Servicios disponibles
        frame_servicios = tk.LabelFrame(col_izq, text="Servicios disponibles", font=("Helvetica", 12, "bold"), bg="#f5f7fa", fg="#1976D2", bd=1, relief="solid")
        frame_servicios.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)

        # Búsqueda
        frame_busqueda = tk.Frame(frame_servicios, bg="#f5f7fa")
        frame_busqueda.pack(fill=tk.X, pady=5)
        tk.Label(frame_busqueda, text="Buscar:", font=("Helvetica", 11), bg="#f5f7fa").pack(side=tk.LEFT, padx=5)
        self.entry_buscar_servicio = tk.Entry(frame_busqueda, width=30, font=("Helvetica", 11))
        self.entry_buscar_servicio.pack(side=tk.LEFT, padx=5)
        btn_buscar = tk.Button(
            frame_busqueda, text="Buscar", font=("Helvetica", 10, "bold"),
            bg="#1976D2", fg="white", activebackground="#1565C0", activeforeground="white",
            relief="flat", cursor="hand2",
            command=lambda: self.buscar_servicios(self.entry_buscar_servicio.get().strip())
        )
        btn_buscar.pack(side=tk.LEFT, padx=5)

        # Tabla de servicios
        frame_tabla_servicios = tk.Frame(frame_servicios, bg="#f5f7fa")
        frame_tabla_servicios.pack(fill=tk.BOTH, expand=True, pady=5)
        columnas = ('id', 'nombre', 'descripcion', 'precio', 'tiempo', 'promo')
        self.tabla_servicios = ttk.Treeview(frame_tabla_servicios, columns=columnas, show='headings', height=7)
        for col, ancho in zip(columnas, [50, 150, 300, 100, 100, 120]):
            self.tabla_servicios.heading(col, text=col.capitalize())
            self.tabla_servicios.column(col, width=ancho, anchor=tk.CENTER if col in ('id', 'precio', 'tiempo') else tk.W)
        self.tabla_servicios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_servicios = ttk.Scrollbar(frame_tabla_servicios, orient=tk.VERTICAL, command=self.tabla_servicios.yview)
        self.tabla_servicios.configure(yscrollcommand=scrollbar_servicios.set)
        scrollbar_servicios.pack(side=tk.RIGHT, fill=tk.Y)

        # Agregar servicio
        frame_agregar = tk.Frame(frame_servicios, bg="#f5f7fa")
        frame_agregar.pack(fill=tk.X, pady=10)
        tk.Label(frame_agregar, text="Cantidad:", font=("Helvetica", 11), bg="#f5f7fa").pack(side=tk.LEFT, padx=5)
        self.entry_cantidad = tk.Entry(frame_agregar, width=5, font=("Helvetica", 11))
        self.entry_cantidad.pack(side=tk.LEFT, padx=5)
        self.entry_cantidad.insert(0, "1")
        btn_agregar = tk.Button(
            frame_agregar, text="Agregar al pedido", font=("Helvetica", 10, "bold"),
            bg="#1976D2", fg="white", activebackground="#1565C0", activeforeground="white",
            relief="flat", cursor="hand2", command=self.agregar_servicio
        )
        btn_agregar.pack(side=tk.LEFT, padx=10)

        # ==================== COLUMNA DERECHA ====================
        col_der = tk.Frame(frame_columnas, bg="#f5f7fa")
        col_der.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Detalles del pedido
        frame_detalles = tk.LabelFrame(col_der, text="Detalles del pedido", font=("Helvetica", 12, "bold"), bg="#f5f7fa", fg="#1976D2", bd=1, relief="solid")
        frame_detalles.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        frame_tabla_detalles = tk.Frame(frame_detalles, bg="#f5f7fa")
        frame_tabla_detalles.pack(fill=tk.BOTH, expand=True, pady=5)
        columnas_detalle = ('servicio', 'cantidad', 'precio_unitario', 'subtotal')
        self.tabla_detalles = ttk.Treeview(frame_tabla_detalles, columns=columnas_detalle, show='headings', height=7)
        for col, ancho in zip(columnas_detalle, [200, 80, 80, 80]):
            self.tabla_detalles.heading(col, text=col.replace('_', ' ').capitalize())
            self.tabla_detalles.column(col, width=ancho, anchor=tk.CENTER if col != 'servicio' else tk.W)
        self.tabla_detalles.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_detalles = ttk.Scrollbar(frame_tabla_detalles, orient=tk.VERTICAL, command=self.tabla_detalles.yview)
        self.tabla_detalles.configure(yscrollcommand=scrollbar_detalles.set)
        scrollbar_detalles.pack(side=tk.RIGHT, fill=tk.Y)

        # Botones de acción sobre detalles
        frame_accion = tk.Frame(frame_detalles, bg="#f5f7fa")
        frame_accion.pack(fill=tk.X, pady=5)
        tk.Button(
            frame_accion, text="Quitar item", font=("Helvetica", 10, "bold"),
            bg="#e53935", fg="white", relief="flat", cursor="hand2", command=self.quitar_item
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            frame_accion, text="Limpiar todo", font=("Helvetica", 10, "bold"),
            bg="#e53935", fg="white", relief="flat", cursor="hand2", command=self.limpiar_pedido
        ).pack(side=tk.LEFT, padx=5)

        # Observaciones
        frame_observaciones = tk.LabelFrame(col_der, text="Observaciones", font=("Helvetica", 11, "bold"), bg="#f5f7fa", fg="#1976D2", bd=1, relief="solid")
        frame_observaciones.pack(fill=tk.X, pady=5, padx=5)
        self.txt_observaciones = tk.Text(frame_observaciones, height=3, font=("Helvetica", 11))
        self.txt_observaciones.pack(fill=tk.X, pady=5, padx=5)

        # Total y guardar (siempre abajo)
        frame_total = tk.Frame(col_der, bg="#e3f2fd", bd=1, relief="solid")
        frame_total.pack(fill=tk.X, pady=10, padx=5)
        tk.Label(
            frame_total, text="TOTAL:", font=("Helvetica", 15, "bold"),
            bg="#e3f2fd", fg="#1565C0"
        ).pack(side=tk.LEFT, padx=10, pady=10)
        self.lbl_total = tk.Label(
            frame_total, text="$0.00", font=("Helvetica", 18, "bold"),
            bg="#e3f2fd", fg="#2E7D32"
        )
        self.lbl_total.pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(
            frame_total, text="Guardar Pedido", font=("Helvetica", 13, "bold"),
            bg="#1976D2", fg="white", activebackground="#1565C0", activeforeground="white",
            relief="flat", cursor="hand2", command=self.procesar_pago
        ).pack(side=tk.RIGHT, padx=10, pady=10)

        # Cargar servicios al iniciar
        self.cargar_servicios()

    def configurar_tab_lista(self):
        frame_principal = tk.Frame(self.tab_lista, bg="#f5f7fa")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        tk.Label(
            frame_principal,
            text="Listado de Pedidos",
            font=("Helvetica", 22, "bold"),
            bg="#f5f7fa",
            fg="#1976D2"
        ).pack(pady=(0, 18))

        # Filtros
        frame_filtros = tk.Frame(frame_principal, bg="#e3f2fd", bd=1, relief="solid")
        frame_filtros.pack(fill=tk.X, pady=(0, 18), padx=10)
        tk.Label(frame_filtros, text="Filtrar por estado:", font=("Helvetica", 11, "bold"), bg="#e3f2fd", fg="#1565C0").pack(side=tk.LEFT, padx=10, pady=8)
        self.combo_estado = ttk.Combobox(
            frame_filtros,
            values=["Todos", "Recibido", "En proceso", "Listo para entrega", "Entregado"],
            width=15,
            state="readonly"
        )
        self.combo_estado.pack(side=tk.LEFT, padx=5)
        self.combo_estado.current(0)
        self.combo_estado.bind("<<ComboboxSelected>>", lambda _: self.cargar_pedidos())
        tk.Label(frame_filtros, text="Buscar por cliente:", font=("Helvetica", 11, "bold"), bg="#e3f2fd", fg="#1565C0").pack(side=tk.LEFT, padx=(20, 5))
        self.entry_buscar_cliente = tk.Entry(frame_filtros, width=20, font=("Helvetica", 11))
        self.entry_buscar_cliente.pack(side=tk.LEFT, padx=5)
        tk.Button(
            frame_filtros, text="Buscar", font=("Helvetica", 10, "bold"),
            bg="#1976D2", fg="white", activebackground="#1565C0", activeforeground="white",
            relief="flat", cursor="hand2", command=self.buscar_pedidos_cliente
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            frame_filtros, text="🔄 Refrescar", font=("Helvetica", 10, "bold"),
            bg="#1976D2", fg="white", activebackground="#1565C0", activeforeground="white",
            relief="flat", cursor="hand2", command=self.cargar_pedidos
        ).pack(side=tk.RIGHT, padx=10)

        # Tabla de pedidos
        frame_tabla = tk.Frame(frame_principal, bg="#f5f7fa")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10)
        columnas = ('id', 'cliente', 'fecha', 'total', 'estado', 'observaciones')
        self.tabla_pedidos = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=10)
        utl.aplicar_estilo_tabla(self.tabla_pedidos)
        for col, ancho in zip(columnas, [50, 200, 150, 100, 120, 250]):
            self.tabla_pedidos.heading(col, text=col.capitalize())
            self.tabla_pedidos.column(col, width=ancho, anchor=tk.CENTER if col in ('id', 'fecha', 'total', 'estado') else tk.W)
        self.tabla_pedidos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_pedidos.yview)
        self.tabla_pedidos.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Botones de acción
        frame_acciones = tk.Frame(frame_principal, bg="#f5f7fa")
        frame_acciones.pack(fill=tk.X, pady=10)
        tk.Button(
            frame_acciones, text="Ver Detalles", font=("Helvetica", 11, "bold"),
            bg="#1976D2", fg="white", relief="flat", cursor="hand2", command=self.ver_detalles_pedido
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            frame_acciones, text="Cambiar Estado", font=("Helvetica", 11, "bold"),
            bg="#1976D2", fg="white", relief="flat", cursor="hand2", command=self.cambiar_estado_pedido
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            frame_acciones, text="Eliminar", font=("Helvetica", 11, "bold"),
            bg="#e53935", fg="white", relief="flat", cursor="hand2", command=self.eliminar_pedido
        ).pack(side=tk.LEFT, padx=5)

        # Cargar pedidos al iniciar
        self.cargar_pedidos()

        for estado, color in self.colores_estado.items():
            self.tabla_pedidos.tag_configure(estado, background=color)

    def seleccionar_cliente(self):
        """Abre ventana para seleccionar un cliente"""
        # Crear ventana para seleccionar cliente
        ventana_clientes = tk.Toplevel(self.ventana)
        ventana_clientes.title("Seleccionar Cliente")
        ventana_clientes.geometry("700x500")
        ventana_clientes.config(bg="#f5f5f5")
        ventana_clientes.grab_set()  # Hacer modal

        # Centrar ventana
        utl.centrar_ventana(ventana_clientes, 700, 500)

        # Frame principal
        frame_principal = tk.Frame(ventana_clientes, bg="#f5f5f5")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        tk.Label(
            frame_principal,
            text="SELECCIONAR CLIENTE",
            font=("Helvetica", 16, "bold"),
            bg="#f5f5f5",
            fg="#303f9f"
        ).pack(pady=(0, 20))

        # Frame para búsqueda
        frame_busqueda = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_busqueda.pack(fill=tk.X, pady=10)

        tk.Label(
            frame_busqueda,
            text="Buscar cliente:",
            font=("Helvetica", 12),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        entry_buscar = tk.Entry(frame_busqueda, width=30, font=("Helvetica", 12))
        entry_buscar.pack(side=tk.LEFT, padx=5)

        # Vincular tecla Enter al buscador
        entry_buscar.bind("<Return>", lambda event: buscar_clientes(entry_buscar.get().strip()))

        btn_buscar = tk.Button(
            frame_busqueda,
            text="🔍 Buscar",
            font=("Helvetica", 10),
            bg="#303f9f",
            fg="white",
            padx=10,
            cursor="hand2",
            command=lambda: buscar_clientes(entry_buscar.get().strip())
        )
        btn_buscar.pack(side=tk.LEFT, padx=5)

        # Frame para la tabla
        frame_tabla = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10)

        # Tabla de clientes
        columnas = ('id', 'nombre', 'telefono', 'puntos')

        tabla_clientes = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=10)

        # Aplicar estilo a la tabla
        utl.aplicar_estilo_tabla(tabla_clientes)

        # Configurar encabezados
        tabla_clientes.heading('id', text='ID')
        tabla_clientes.heading('nombre', text='Nombre')
        tabla_clientes.heading('telefono', text='Teléfono')
        tabla_clientes.heading('puntos', text='Puntos')

        # Configurar anchos
        tabla_clientes.column('id', width=50, anchor=tk.CENTER)
        tabla_clientes.column('nombre', width=300)
        tabla_clientes.column('telefono', width=150, anchor=tk.CENTER)
        tabla_clientes.column('puntos', width=100, anchor=tk.CENTER)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=tabla_clientes.yview)
        tabla_clientes.configure(yscrollcommand=scrollbar.set)

        # Empaquetar tabla y scrollbar
        tabla_clientes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame para botones
        frame_botones = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_botones.pack(fill=tk.X, pady=10)

        # Botones
        btn_seleccionar = tk.Button(
            frame_botones,
            text="Seleccionar",
            font=("Helvetica", 11),
            bg="#303f9f",
            fg="white",
            width=12,
            cursor="hand2",
            command=lambda: seleccionar_cliente_accion(tabla_clientes)
        )
        btn_seleccionar.pack(side=tk.LEFT, padx=5)

        btn_nuevo = tk.Button(
            frame_botones,
            text="Nuevo Cliente",
            font=("Helvetica", 11),
            bg="#303f9f",
            fg="white",
            width=12,
            cursor="hand2",
            command=lambda: abrir_nuevo_cliente(ventana_clientes)
        )
        btn_nuevo.pack(side=tk.LEFT, padx=5)

        btn_cancelar = tk.Button(
            frame_botones,
            text="Cancelar",
            font=("Helvetica", 11),
            bg="#e53935",
            fg="white",
            width=10,
            cursor="hand2",
            command=ventana_clientes.destroy
        )
        btn_cancelar.pack(side=tk.RIGHT, padx=5)

        # Función para cargar clientes
        def cargar_clientes():
            # Limpiar tabla
            for item in tabla_clientes.get_children():
                tabla_clientes.delete(item)

            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()
                cursor.execute(
                    "SELECT id_cliente, nombre, telefono, puntos FROM clientes ORDER BY nombre")

                for cliente in cursor.fetchall():
                    tabla_clientes.insert('', tk.END, values=cliente)

                conexion.close()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar los clientes: {str(e)}")

        # Función para buscar clientes
        def buscar_clientes(texto_busqueda):
            # Limpiar tabla
            for item in tabla_clientes.get_children():
                tabla_clientes.delete(item)

            if not texto_busqueda:
                cargar_clientes()
                return

            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()

                # Búsqueda por nombre o teléfono
                consulta = """
                SELECT id_cliente, nombre, telefono, puntos FROM clientes 
                WHERE nombre LIKE %s OR telefono LIKE %s
                ORDER BY nombre
                """

                cursor.execute(consulta, (f"%{texto_busqueda}%", f"%{texto_busqueda}%"))

                for cliente in cursor.fetchall():
                    tabla_clientes.insert('', tk.END, values=cliente)

                conexion.close()
            except Exception as e:
                messagebox.showerror("Error", f"Error al buscar clientes: {str(e)}")

        # Función para seleccionar cliente
        def seleccionar_cliente_accion(tabla):
            seleccion = tabla.selection()

            if not seleccion:
                messagebox.showwarning("Selección requerida", "Por favor, selecciona un cliente")
                return

            # Obtener datos del cliente seleccionado
            valores = tabla.item(seleccion[0], 'values')
            self.cliente_actual = {
                'id': valores[0],
                'nombre': valores[1]
            }

            # Actualizar etiqueta en la ventana principal
            self.lbl_cliente_seleccionado.config(
                text=f"{self.cliente_actual['nombre']}",
                fg="#303f9f"
            )

            # Cerrar ventana
            ventana_clientes.destroy()

        # Función para abrir formulario de nuevo cliente
        def abrir_nuevo_cliente(ventana_padre):
            # Crear ventana para nuevo cliente
            ventana_nuevo = tk.Toplevel(ventana_padre)
            ventana_nuevo.title("Nuevo Cliente")
            ventana_nuevo.geometry("400x300")
            ventana_nuevo.config(bg="#f5f5f5")
            ventana_nuevo.grab_set()  # Hacer modal

            # Centrar ventana
            utl.centrar_ventana(ventana_nuevo, 400, 300)

            # Frame principal
            frame_principal = tk.Frame(ventana_nuevo, bg="#f5f5f5")
            frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # Título
            tk.Label(
                frame_principal,
                text="NUEVO CLIENTE",
                font=("Helvetica", 14, "bold"),
                bg="#f5f5f5",
                fg="#303f9f"
            ).pack(pady=(0, 20))

            # Frame para formulario
            frame_form = tk.Frame(frame_principal, bg="#f5f5f5")
            frame_form.pack(fill=tk.X, pady=10)

            # Campos del formulario
            tk.Label(frame_form, text="Nombre:", font=("Helvetica", 12), bg="#f5f5f5").grid(row=0, column=0, sticky=tk.W, pady=5)
            entry_nombre = tk.Entry(frame_form, font=("Helvetica", 12), width=25)
            entry_nombre.grid(row=0, column=1, sticky=tk.W, pady=5)

            tk.Label(frame_form, text="Teléfono:", font=("Helvetica", 12), bg="#f5f5f5").grid(row=1, column=0, sticky=tk.W, pady=5)
            entry_telefono = tk.Entry(frame_form, font=("Helvetica", 12), width=25)
            entry_telefono.grid(row=1, column=1, sticky=tk.W, pady=5)

            tk.Label(frame_form, text="Correo:", font=("Helvetica", 12), bg="#f5f5f5").grid(row=2, column=0, sticky=tk.W, pady=5)
            entry_correo = tk.Entry(frame_form, font=("Helvetica", 12), width=25)
            entry_correo.grid(row=2, column=1, sticky=tk.W, pady=5)

            # Frame para botones
            frame_botones = tk.Frame(frame_principal, bg="#f5f5f5")
            frame_botones.pack(fill=tk.X, pady=20)

            # Función para guardar nuevo cliente
            def guardar_cliente():
                nombre = entry_nombre.get().strip()
                telefono = entry_telefono.get().strip()
                correo = entry_correo.get().strip()

                if not nombre:
                    messagebox.showwarning("Dato requerido", "El nombre del cliente es obligatorio")
                    return

                try:
                    conexion = conectar_bd()
                    cursor = conexion.cursor()
                    consulta = "INSERT INTO clientes (nombre, telefono, correo, puntos) VALUES (%s, %s, %s, 0)"
                    cursor.execute(consulta, (nombre, telefono, correo))

                    # Obtener el ID del cliente recién insertado
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    id_cliente = cursor.fetchone()[0]

                    conexion.commit()
                    conexion.close()

                    # Seleccionar el cliente recién creado
                    self.cliente_actual = {
                        'id': id_cliente,
                        'nombre': nombre
                    }

                    # Actualizar etiqueta en la ventana principal
                    self.lbl_cliente_seleccionado.config(
                        text=f"{nombre}",
                        fg="#303f9f"
                    )

                    messagebox.showinfo("Éxito", "Cliente registrado correctamente")
                    ventana_nuevo.destroy()
                    ventana_clientes.destroy()

                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo registrar el cliente: {str(e)}")

            # Botones
            btn_guardar = tk.Button(
                frame_botones,
                text="Guardar",
                font=("Helvetica", 11),
                bg="#303f9f",
                fg="white",
                width=10,
                cursor="hand2",
                command=guardar_cliente
            )
            btn_guardar.pack(side=tk.LEFT, padx=5)

            btn_cancelar = tk.Button(
                frame_botones,
                text="Cancelar",
                font=("Helvetica", 11),
                bg="#e53935",
                fg="white",
                width=10,
                cursor="hand2",
                command=ventana_nuevo.destroy
            )
            btn_cancelar.pack(side=tk.LEFT, padx=5)

        # Cargar clientes al iniciar
        cargar_clientes()

    def cargar_servicios(self):
        """Carga los servicios disponibles en la tabla, mostrando descuentos/promos"""
        for item in self.tabla_servicios.get_children():
            self.tabla_servicios.delete(item)

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            consulta = """
            SELECT id_servicio, nombre, descripcion, precio, 
                   CONCAT(tiempo_estimado, ' min') as tiempo,
                   promo_desc, nuevo_precio
            FROM servicios 
            WHERE activo = 1 
            ORDER BY nombre
            """
            cursor.execute(consulta)
            for servicio in cursor.fetchall():
                precio_final = float(servicio[6]) if servicio[6] is not None else float(servicio[3])
                precio_formateado = f"${precio_final:.2f}"
                promo = servicio[5] if servicio[5] else ""
                valores = (servicio[0], servicio[1], servicio[2], precio_formateado, servicio[4], promo)
                self.tabla_servicios.insert('', tk.END, values=valores)
            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los servicios: {str(e)}")

    def buscar_servicios(self, texto_busqueda):
        """Busca servicios por nombre o descripción"""
        # Limpiar tabla
        for item in self.tabla_servicios.get_children():
            self.tabla_servicios.delete(item)

        if not texto_busqueda:
            self.cargar_servicios()
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Búsqueda por nombre o descripción
            consulta = """
            SELECT id_servicio, nombre, descripcion, precio, 
                   CONCAT(tiempo_estimado, ' min') as tiempo 
            FROM servicios 
            WHERE activo = 1 
                  AND (nombre LIKE %s OR descripcion LIKE %s)
            ORDER BY nombre
            """

            cursor.execute(consulta, (f"%{texto_busqueda}%", f"%{texto_busqueda}%"))

            for servicio in cursor.fetchall():
                # Formatear precio
                precio_formateado = f"${float(servicio[3]):.2f}"
                valores = (servicio[0], servicio[1], servicio[2], precio_formateado, servicio[4])
                self.tabla_servicios.insert('', tk.END, values=valores)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar servicios: {str(e)}")

    def agregar_servicio(self):
        """Agrega un servicio al pedido actual, usando el precio promocional si existe"""
        if not self.cliente_actual:
            messagebox.showwarning("Cliente requerido", "Por favor, selecciona un cliente primero")
            return

        seleccion = self.tabla_servicios.selection()
        if not seleccion:
            messagebox.showwarning("Selección requerida", "Selecciona un servicio para agregar")
            return

        valores = self.tabla_servicios.item(seleccion[0], 'values')
        id_servicio = int(valores[0])
        nombre_servicio = valores[1]
        precio_str = valores[3].replace('$', '').replace(',', '').strip()
        promo = valores[5] if len(valores) > 5 else ""

        try:
            precio_unitario = float(precio_str)
            try:
                cantidad = int(self.entry_cantidad.get().strip())
                if cantidad <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Cantidad inválida", "La cantidad debe ser un número entero positivo")
                return

            subtotal = precio_unitario * cantidad
            existe = False

            for i, item in enumerate(self.items_pedido):
                if item['id'] == id_servicio and item['tipo'] == 'servicio':
                    nueva_cantidad = item['cantidad'] + cantidad
                    self.items_pedido[i]['cantidad'] = nueva_cantidad
                    self.items_pedido[i]['subtotal'] = precio_unitario * nueva_cantidad
                    existe = True
                    break

            if not existe:
                self.items_pedido.append({
                    'id': id_servicio,
                    'tipo': 'servicio',
                    'nombre': nombre_servicio,
                    'cantidad': cantidad,
                    'precio_unitario': precio_unitario,
                    'subtotal': subtotal,
                    'promo': promo
                })

            self.actualizar_tabla_detalles()
            self.calcular_total()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el servicio:\n{e}")


    def actualizar_tabla_detalles(self):
        """Actualiza la tabla de detalles del pedido"""
        # Limpiar tabla
        for item in self.tabla_detalles.get_children():
            self.tabla_detalles.delete(item)

        # Agregar cada item a la tabla
        for item in self.items_pedido:
            valores = (
                item['nombre'],
                item['cantidad'],
                f"${item['precio_unitario']:.2f}",
                f"${item['subtotal']:.2f}"
            )
            self.tabla_detalles.insert('', tk.END, values=valores)

    def calcular_total(self):
        """Calcula y muestra el total del pedido"""
        self.total_pedido = sum(item['subtotal'] for item in self.items_pedido)
        self.lbl_total.config(text=f"${self.total_pedido:.2f}")

    def quitar_item(self):
        """Quita un item seleccionado del pedido"""
        seleccion = self.tabla_detalles.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un servicio para quitar")
            return

        # Obtener índice del item seleccionado
        indice = self.tabla_detalles.index(seleccion[0])

        # Eliminar el item de la lista
        if 0 <= indice < len(self.items_pedido):
            del self.items_pedido[indice]

            # Actualizar tabla y total
            self.actualizar_tabla_detalles()
            self.calcular_total()

    def limpiar_pedido(self):
        """Limpia todos los items del pedido"""
        if messagebox.askyesno("Confirmar", "¿Deseas limpiar todos los items del pedido?"):
            self.items_pedido = []
            self.actualizar_tabla_detalles()
            self.calcular_total()

    def procesar_pago(self):
        """Proceso para cobrar los servicios del pedido"""
        # 1) Validaciones
        if not self.items_pedido:
            messagebox.showwarning("Pedido vacío", "Agrega servicios antes de procesar el pago.")
            return
        if not self.cliente_actual:
            messagebox.showwarning("Cliente requerido", "Selecciona un cliente para este pedido.")
            return

        # 2) Crear ventana modal
        ventana_pago = tk.Toplevel(self.ventana)
        ventana_pago.title("Procesar Pago")
        ventana_pago.geometry("400x450")
        ventana_pago.config(bg="#f5f5f5")
        ventana_pago.resizable(False, False)
        ventana_pago.transient(self.ventana)
        ventana_pago.grab_set()
        utl.centrar_ventana(ventana_pago, 400, 450)

        # 3) Variable de método de pago
        metodo_var = tk.StringVar(value="Efectivo")

        # 4) Botones fijos abajo
        frame_btn = tk.Frame(ventana_pago, bg="#f5f5f5")
        frame_btn.pack(side="bottom", fill="x", pady=10, padx=20)
        tk.Button(
            frame_btn,
            text="Procesar Pago",
            font=("Helvetica", 12, "bold"),
            bg="#00796b", fg="white",
            width=15, cursor="hand2",
            command=lambda: self.finalizar_pago(ventana_pago, metodo_var, entry_rec)
        ).pack(side="left", padx=5)
        tk.Button(
            frame_btn,
            text="Cancelar",
            font=("Helvetica", 12),
            bg="#e53935", fg="white",
            width=15, cursor="hand2",
            command=ventana_pago.destroy
        ).pack(side="left", padx=5)

        # 5) Canvas + Scrollbar
        canvas = tk.Canvas(ventana_pago, bg="#f5f5f5", highlightthickness=0)
        scrollbar = ttk.Scrollbar(ventana_pago, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg="#f5f5f5")
        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 6) Contenedor principal dentro del scroll
        frame = tk.Frame(scrollable, bg="#f5f5f5", padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        # 7) Mostrar total
        tk.Label(
            frame,
            text="TOTAL A PAGAR:",
            font=("Helvetica", 14, "bold"),
            bg="#f5f5f5"
        ).pack(pady=(0, 5))
        tk.Label(
            frame,
            text=f"${self.total_pedido:.2f}",
            font=("Helvetica", 18, "bold"),
            bg="#f5f5f5",
            fg="#00796b"
        ).pack(pady=(0, 20))

        # 8) Método de pago
        tk.Label(
            frame,
            text="Método de pago:",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5"
        ).pack(anchor="w", pady=(0, 5))
        frame_rb = tk.Frame(frame, bg="#f5f5f5")
        frame_rb.pack(fill="x", pady=5)

        # 9) Precrear frame_efec y lbl_cambio
        frame_efec = tk.Frame(frame, bg="#f5f5f5")
        frame_efec.pack(fill="x", pady=10)
        tk.Label(
            frame_efec,
            text="Efectivo recibido:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).grid(row=0, column=0, sticky="w", pady=5)
        entry_rec = tk.Entry(frame_efec, font=("Helvetica", 11), width=15)
        entry_rec.grid(row=0, column=1, padx=5)
        tk.Label(
            frame_efec,
            text="Cambio:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).grid(row=1, column=0, sticky="w", pady=5)
        lbl_cambio = tk.Label(
            frame_efec,
            text="$0.00",
            font=("Helvetica", 11, "bold"),
            bg="#f5f5f5",
            fg="#d32f2f"
        )
        lbl_cambio.grid(row=1, column=1, sticky="w", padx=5)

        # 10) Radiobuttons con callback
        for m in ["Efectivo", "Tarjeta", "Transferencia"]:
            tk.Radiobutton(
                frame_rb,
                text=m,
                variable=metodo_var,
                value=m,
                bg="#f5f5f5",
                font=("Helvetica", 11),
                command=lambda mm=m: self.actualizar_pago_efectivo(mm, frame_efec, entry_rec, lbl_cambio)
            ).pack(side="left", padx=5, pady=2)

        # 11) Bind para recalcular cambio
        entry_rec.bind("<KeyRelease>", lambda e: self.calcular_cambio(entry_rec, lbl_cambio))

        # 12) Ajustar visibilidad inicial
        self.actualizar_pago_efectivo(metodo_var.get(), frame_efec, entry_rec, lbl_cambio)


            
    def actualizar_pago_efectivo(self, metodo, frame_efectivo, entry_recibido, lbl_cambio):
            """Muestra/oculta campos según el método de pago"""
            if metodo == "Efectivo":
                frame_efectivo.pack(fill=tk.X, pady=10)
            else:
                frame_efectivo.pack_forget()

    def calcular_cambio(self, entry_recibido, lbl_cambio):
        """Calcula el cambio en tiempo real"""
        try:
            recibido = float(entry_recibido.get())
            cambio = recibido - self.total_pedido
            if cambio >= 0:
                lbl_cambio.config(text=f"${cambio:.2f}", fg="#388e3c")
            else:
                lbl_cambio.config(text=f"${cambio:.2f}", fg="#d32f2f")
        except ValueError:
            lbl_cambio.config(text="$0.00", fg="#666666")


            

    def guardar_pedido(self):
        """
        Guarda el pedido en pedidos y detalle_pedido.
        Devuelve el id_pedido generado o None si hay un error.
        """
        if not self.cliente_actual:
            messagebox.showwarning("Cliente requerido", "Selecciona un cliente para el pedido")
            return None
        if not self.items_pedido:
            messagebox.showwarning("Pedido vacío", "Agrega servicios al pedido")
            return None

        observaciones = self.txt_observaciones.get("1.0", tk.END).strip()
        try:
            conn = conectar_bd()
            cur = conn.cursor()

            # 1) Insertar encabezado (pedidos no tiene id_usuario)
            cur.execute(
                """
                INSERT INTO pedidos
                (id_cliente, fecha_pedido, estado, observaciones)
                VALUES
                (%s, NOW(), 'Recibido', %s)
                """,
                (self.cliente_actual['id'], observaciones)
            )
            cur.execute("SELECT LAST_INSERT_ID()")
            id_pedido = cur.fetchone()[0]

            # 2) Insertar detalle_pedido
            for item in self.items_pedido:
                cur.execute(
                    """
                    INSERT INTO detalle_pedido
                    (id_pedido, tipo_item, id_item, cantidad, precio_unitario)
                    VALUES (%s, 'servicio', %s, %s, %s)
                    """,
                    (id_pedido, item['id'], item['cantidad'], item['precio_unitario'])
                )

            conn.commit()
            conn.close()
            return id_pedido

        except Exception as e:
            messagebox.showerror("Error al guardar pedido", str(e))
            return None


    def finalizar_pago(self, ventana_pago, metodo_pago_var, entry_rec):
        """
        Flujo completo de un pedido con actualización de caja:
        1) calcular cambio/monto
        2) guardar pedido → id_pedido
        3) insertar en ventas → id_venta
        4) detalle_venta
        5) pagos
        6) registrar movimientos en caja
        7) marcar pedido como entregado
        8) limpiar UI + ticket
        """
        metodo = metodo_pago_var.get()
        try:
            # 1) Calcular monto y cambio
            if metodo == "Efectivo":
                recibido = float(entry_rec.get())
                if recibido < self.total_pedido:
                    return messagebox.showwarning(
                        "Efectivo insuficiente",
                        "El monto recibido es menor al total a pagar."
                    )
                cambio = recibido - self.total_pedido
                monto = self.total_pedido
            else:
                recibido = 0.0
                cambio = 0.0
                monto = self.total_pedido

            # 2) Guardar pedido
            id_pedido = self.guardar_pedido()
            if id_pedido is None:
                return

            conn = conectar_bd()
            cur  = conn.cursor()

            # 2.1) Calcular puntos de fidelidad para este pedido
            puntos_ganados = int(self.total_pedido / 10)

            # 3) Insertar en ventas, incluyendo id_pedido y puntos_ganados
            cur.execute("""
                INSERT INTO ventas
                (id_usuario, id_cliente, id_pedido, total, fecha, metodo_pago, puntos_ganados)
                VALUES (%s, %s, %s, %s, NOW(), %s, %s)
            """, (
                self.id_usuario_actual,
                self.cliente_actual['id'],
                id_pedido,
                self.total_pedido,
                metodo,
                puntos_ganados
            ))
            cur.execute("SELECT LAST_INSERT_ID()")
            id_venta = cur.fetchone()[0]


            # 4) Insertar detalle_venta 
            for item in self.items_pedido:
                subtotal = item.get('subtotal', item['cantidad'] * item['precio_unitario'])
                cur.execute(
                    """
                    INSERT INTO detalle_venta
                    (id_venta, tipo_item, id_item, cantidad, subtotal)
                    VALUES (%s, 'servicio', %s, %s, %s)
                    """,
                    (id_venta, item['id'], item['cantidad'], subtotal)
                )

            # 5) Insertar en pagos
            cur.execute(
                """
                INSERT INTO pagos
                (id_venta, monto, metodo_pago, fecha_hora)
                VALUES (%s, %s, %s, NOW())
                """,
                (id_venta, monto, metodo)
            )

            # 6) *** Aquí registramos los movimientos en caja ***
            #    6.1) Obtener la caja abierta
            cur.execute("""
                SELECT id_caja, responsable
                FROM caja
                WHERE fecha = CURDATE()
                AND hora_cierre IS NULL
                LIMIT 1
            """)
            fila = cur.fetchone()
            if fila:
                id_caja_act, resp = fila

                # 6.2) Registrar solo el total de la venta como ingreso, sin egreso por cambio
                concepto = f"Pedido #{id_pedido} – {metodo}"
                cur.execute("""
                    INSERT INTO movimientos_caja
                    (id_caja, tipo, concepto, monto, hora, id_usuario)
                    VALUES (%s, 'ingreso', %s, %s, NOW(), %s)
                """, (id_caja_act, concepto, monto, resp))
                cur.execute("""
                    UPDATE caja
                    SET total_ingresos = total_ingresos + %s,
                        saldo_final    = saldo_final    + %s
                    WHERE id_caja = %s
                """, (monto, monto, id_caja_act))

            # 7) Marcar pedido como recibido
            cur.execute(
                "UPDATE pedidos SET estado = 'Recibido' WHERE id_pedido = %s",
                (id_pedido,)
            )

            # 7.2) **Actualizar puntos totales del cliente**
            cur.execute("""
                UPDATE clientes
                SET puntos = puntos + %s
                WHERE id_cliente = %s
            """, (puntos_ganados, self.cliente_actual['id']))

            conn.commit()
            conn.close()

            # 8) Mensaje final con puntos
            ventana_pago.destroy()
            ruta_ticket = self.generar_ticket_pedido(
                id_pedido,        # el pedido que se acaba de pagar
                id_venta,         # la venta asociada
                metodo,           # método de pago
                recibido,         # efectivo recibido (0 si no aplica)
                cambio            # cambio a devolver (0 si no aplica)
            )

            mensajes = [
                f"✅ Pedido #{id_pedido} pagado correctamente.",
                f"Total: ${self.total_pedido:.2f}",
                f"Método: {metodo}",
                f"🎁 Puntos ganados: {puntos_ganados}"
            ]
            if metodo == "Efectivo":
                mensajes.append(f"💵 Recibido: ${recibido:.2f}")
                if cambio > 0:
                    mensajes.append(f"💰 Cambio: ${cambio:.2f}")

            messagebox.showinfo("Pago Registrado", "\n".join(mensajes), parent=self.ventana)

            # 8) Limpiar la interfaz de Pedidos
            self.items_pedido.clear()
            self.actualizar_tabla_detalles()
            self.calcular_total()
            self.txt_observaciones.delete("1.0", tk.END)
            self.lbl_cliente_seleccionado.config(text="No seleccionado", fg="#777777")
            self.cliente_actual = None
            self.notebook.select(self.tab_lista)
            self.cargar_pedidos()

            # 9) Abrir el ticket generado
            try:
                import webbrowser, os
                webbrowser.open(f"file://{os.path.abspath(ruta_ticket)}")
            except Exception:
                pass

        except ValueError:
            messagebox.showwarning("Error", "El monto ingresado no es un número válido.")
        except Exception as e:
            messagebox.showerror("Error al procesar el pago", str(e))


    def generar_ticket_pedido(self, id_pedido, id_venta, metodo_pago, recibido, cambio):
        """
        Genera un ticket HTML para un pedido y devuelve la ruta del archivo.
        Formato compacto, listo para impresora térmica.
        """
        ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cliente = self.cliente_actual.get("nombre", "Cliente")
        folio = f"LP{datetime.now().strftime('%Y%m%d%H%M%S')}"
        ruta_archivo = f"tickets/ticket_pedido_{id_pedido}.html"

        # Crear carpeta tickets si no existe
        os.makedirs("tickets", exist_ok=True)

        # Cuerpo de los ítems
        cuerpo_items = ""
        for item in self.items_pedido:
            promo_text = f" <span style='color:#1976D2;'>[{item['promo']}]</span>" if item.get('promo') else ""
            cuerpo_items += f"""
            <tr>
                <td>{item.get('nombre', '')}{promo_text}</td>
                <td class="precio">{item.get('cantidad', 0)} x {item.get('precio_unitario', 0.0):.2f}</td>
                <td class="subtotal">${item.get('subtotal', 0.0):.2f}</td>
            </tr>
            """

        total_formateado = f"${self.total_pedido:.2f}"

        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Ticket Pedido #{id_pedido}</title>
            <style>
                body {{
                    width: 230px;
                    font-family: 'Courier New', monospace;
                    font-size: 12px;
                    margin: 0 auto;
                    color: #000;
                }}
                h2, p {{
                    text-align: center;
                    margin: 4px 0;
                }}
                .separador {{
                    border-top: 1px dashed #000;
                    margin: 5px 0;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                td {{
                    padding: 2px;
                }}
                td.precio, td.subtotal {{
                    text-align: right;
                }}
            </style>
        </head>
        <body>
            <h2>Lavandería Exprés</h2>
            <p>Calle Principal #123</p>
            <p>Colonia Centro</p>
            <p>Tel: 555-123-4567</p>
            <div class="separador"></div>
            <p><strong>Fecha:</strong> {ahora}</p>
            <p><strong>Pedido #:</strong> {id_pedido} &nbsp;&nbsp; <strong>Venta #:</strong> {id_venta}</p>
            <p><strong>Cliente:</strong> {cliente}</p>
            <div class="separador"></div>
            <table>
                {cuerpo_items}
            </table>
            <div class="separador"></div>
            <p><strong>TOTAL: {total_formateado}</strong></p>
            <p><strong>Método:</strong> {metodo_pago}</p>
        """

        if metodo_pago == "Efectivo":
            html += f"""
            <p><strong>Recibido:</strong> ${recibido:.2f} &nbsp; <strong>Cambio:</strong> ${cambio:.2f}</p>
            """

        html += f"""
            <div class="separador"></div>
            <p>Folio: {folio}</p>
            <p>¡Gracias por su preferencia!</p>
            <p>Conserve su ticket</p>
        </body>
        </html>
        """

        with open(ruta_archivo, "w", encoding="utf-8") as file:
            file.write(html)

        return ruta_archivo

    def cargar_pedidos(self):
        """Carga los pedidos en la tabla de la pestaña 'Lista de Pedidos'"""
        for item in self.tabla_pedidos.get_children():
            self.tabla_pedidos.delete(item)

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            estado_filtro = self.combo_estado.get()
            where_clause = ""
            if estado_filtro != "Todos":
                where_clause = "WHERE p.estado = %s"
            
            consulta = f"""
            SELECT p.id_pedido, c.nombre, p.fecha_pedido, p.estado, p.observaciones,
                   (SELECT SUM(dp.cantidad * dp.precio_unitario) FROM detalle_pedido dp WHERE dp.id_pedido = p.id_pedido) as total
            FROM pedidos p
            JOIN clientes c ON p.id_cliente = c.id_cliente
            {where_clause}
            ORDER BY p.fecha_pedido DESC
            """

            if estado_filtro != "Todos":
                cursor.execute(consulta, (estado_filtro,))
            else:
                cursor.execute(consulta)

            for row in cursor.fetchall():
                id_pedido, cliente, fecha, estado, observaciones, total = row
                self.tabla_pedidos.insert(
                    '', tk.END,
                    values=(
                        id_pedido, cliente, fecha.strftime("%d/%m/%Y %H:%M"), 
                        f"${total:.2f}" if total else "$0.00", estado, observaciones
                    ),
                    tags=(estado,)  # <-- Esto aplica el color según el estado
                )
            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los pedidos: {str(e)}")

    def buscar_pedidos_cliente(self):
        """Filtra la lista de pedidos por el nombre del cliente ingresado."""
        texto = self.entry_buscar_cliente.get().strip()
        if not texto:
            self.cargar_pedidos()
            return
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            consulta = """
                SELECT p.id_pedido, c.nombre, p.fecha_pedido, p.estado, p.observaciones,
                       (SELECT SUM(dp.cantidad * dp.precio_unitario) FROM detalle_pedido dp WHERE dp.id_pedido = p.id_pedido) as total
                FROM pedidos p
                JOIN clientes c ON p.id_cliente = c.id_cliente
                WHERE c.nombre LIKE %s
                ORDER BY p.fecha_pedido DESC
            """
            cursor.execute(consulta, (f"%{texto}%",))
            self.tabla_pedidos.delete(*self.tabla_pedidos.get_children())
            for row in cursor.fetchall():
                id_pedido, cliente, fecha, estado, observaciones, total = row
                self.tabla_pedidos.insert('', tk.END, values=(
                    id_pedido, cliente, fecha.strftime("%d/%m/%Y %H:%M"), 
                    f"${total:.2f}" if total else "$0.00", estado, observaciones
                ))
            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo buscar pedidos: {str(e)}")

    def ver_detalles_pedido(self):
        """Muestra los detalles de un pedido seleccionado en una nueva ventana"""
        seleccion = self.tabla_pedidos.selection()
        if not seleccion:
            messagebox.showwarning("Selección requerida", "Selecciona un pedido para ver los detalles")
            return

        # Obtener ID del pedido seleccionado
        id_pedido = self.tabla_pedidos.item(seleccion[0], 'values')[0]

        # Crear ventana de detalles
        ventana_detalles = tk.Toplevel(self.ventana)
        ventana_detalles.title(f"Detalles del Pedido #{id_pedido}")
        ventana_detalles.geometry("600x400")
        ventana_detalles.config(bg="#f5f5f5")
        ventana_detalles.grab_set()  # Hacer modal

        # Centrar ventana
        utl.centrar_ventana(ventana_detalles, 600, 400)

        # Frame principal
        frame_principal = tk.Frame(ventana_detalles, bg="#f5f5f5")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        tk.Label(
            frame_principal,
            text=f"DETALLES DEL PEDIDO #{id_pedido}",
            font=("Helvetica", 16, "bold"),
            bg="#f5f5f5",
            fg="#303f9f"
        ).pack(pady=(0, 20))

        # Tabla de detalles
        frame_tabla = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10)

        columnas_detalle = ('Servicio', 'Cantidad', 'Precio Unitario', 'Subtotal')
        tabla_detalles = ttk.Treeview(frame_tabla, columns=columnas_detalle, show='headings', height=10)
        utl.aplicar_estilo_tabla(tabla_detalles)
        for col, ancho in zip(columnas_detalle, [250, 80, 100, 100]):
            tabla_detalles.heading(col, text=col)
            tabla_detalles.column(col, width=ancho, anchor=tk.CENTER if col != 'Servicio' else tk.W)
        tabla_detalles.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=tabla_detalles.yview)
        tabla_detalles.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Cargar detalles del pedido
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            consulta = """
                SELECT s.nombre, dp.cantidad, dp.precio_unitario, (dp.cantidad * dp.precio_unitario) as subtotal
                FROM detalle_pedido dp
                JOIN servicios s ON dp.id_item = s.id_servicio
                WHERE dp.id_pedido = %s
            """
            cursor.execute(consulta, (id_pedido,))
            for row in cursor.fetchall():
                tabla_detalles.insert('', tk.END, values=(
                    row[0], row[1], f"${row[2]:.2f}", f"${row[3]:.2f}"
                ))
            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los detalles del pedido: {str(e)}")

        # Botón cerrar
        tk.Button(
            frame_principal,
            text="Cerrar",
            font=("Helvetica", 11),
            bg="#e53935",
            fg="white",
            cursor="hand2",
            command=ventana_detalles.destroy
        ).pack(side=tk.BOTTOM, pady=10)

    def cambiar_estado_pedido(self):
        """Cambia el estado del pedido seleccionado"""
        seleccion = self.tabla_pedidos.selection()
        if not seleccion:
            messagebox.showwarning("Selección requerida", "Selecciona un pedido para cambiar el estado")
            return

        id_pedido = self.tabla_pedidos.item(seleccion[0], 'values')[0]

        # Obtener estado actual
        estado_actual = self.tabla_pedidos.item(seleccion[0], 'values')[4]

        # Definir siguiente estado
        estados = ["Recibido", "En proceso", "Listo para entrega", "Entregado"]
        try:
            nuevo_estado = estados[estados.index(estado_actual) + 1]
        except IndexError:
            nuevo_estado = estados[0]  # Volver al primer estado si está en el último

        # Confirmar cambio
        if messagebox.askyesno("Confirmar", f"Cambiar estado a '{nuevo_estado}'?"):
            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()
                cursor.execute(
                    "UPDATE pedidos SET estado = %s WHERE id_pedido = %s",
                    (nuevo_estado, id_pedido)
                )
                conexion.commit()
                conexion.close()
                messagebox.showinfo("Éxito", f"Estado cambiado a '{nuevo_estado}'")
                self.cargar_pedidos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cambiar el estado: {str(e)}")

    def eliminar_pedido(self):
        """Elimina un pedido seleccionado"""
        seleccion = self.tabla_pedidos.selection()
        if not seleccion:
            messagebox.showwarning("Selección requerida", "Selecciona un pedido para eliminar")
            return

        id_pedido = self.tabla_pedidos.item(seleccion[0], 'values')[0]

        # Confirmar eliminación
        if messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este pedido?"):
            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()
                cursor.execute(
                    "DELETE FROM pedidos WHERE id_pedido = %s",
                    (id_pedido,)
                )
                conexion.commit()
                conexion.close()
                messagebox.showinfo("Éxito", "Pedido eliminado correctamente")
                self.cargar_pedidos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el pedido: {str(e)}")