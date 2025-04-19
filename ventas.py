import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from conexion import conectar_bd
import utileria as utl
from datetime import datetime


class Ventas:
    def __init__(self, ventana_padre=None):
        # Si hay una ventana padre, crear Toplevel en lugar de Tk
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Módulo de Ventas - Lavandería")
        self.ventana.geometry("1000x700")
        self.ventana.config(bg="#e0f7fa")
        self.ventana.resizable(False, False)

        if ventana_padre:
            # Centrar la ventana si existe una ventana padre
            utl.centrar_ventana(self.ventana, 1000, 700)
            # Hacer esta ventana modal
            self.ventana.transient(ventana_padre)
            self.ventana.grab_set()

        # Variables para la venta
        self.items_venta = []
        self.cliente_actual = None
        self.total_venta = 0.0

        self.construir_interfaz()

        if not ventana_padre:
            self.ventana.mainloop()

    def construir_interfaz(self):
        # Frame principal
        self.frame_principal = tk.Frame(self.ventana, bg="#e0f7fa")
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        titulo = tk.Label(
            self.frame_principal,
            text="Registro de Ventas",
            font=("Helvetica", 20, "bold"),
            bg="#e0f7fa",
            fg="#00796b"
        )
        titulo.pack(pady=10)

        # Frame superior para selección de cliente
        frame_cliente = tk.Frame(self.frame_principal, bg="#e0f7fa")
        frame_cliente.pack(fill=tk.X, pady=10)

        lbl_cliente = tk.Label(
            frame_cliente,
            text="Cliente:",
            font=("Helvetica", 12),
            bg="#e0f7fa"
        )
        lbl_cliente.pack(side=tk.LEFT, padx=5)

        self.lbl_cliente_seleccionado = tk.Label(
            frame_cliente,
            text="No seleccionado",
            font=("Helvetica", 12),
            bg="#e0f7fa",
            fg="#777777"
        )
        self.lbl_cliente_seleccionado.pack(side=tk.LEFT, padx=5)

        btn_seleccionar_cliente = tk.Button(
            frame_cliente,
            text="Seleccionar Cliente",
            font=("Helvetica", 10),
            bg="#00796b",
            fg="white",
            command=self.seleccionar_cliente
        )
        btn_seleccionar_cliente.pack(side=tk.LEFT, padx=10)

        # Frame para pestañas (productos y servicios)
        self.notebook = ttk.Notebook(self.frame_principal)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Pestaña de productos
        tab_productos = tk.Frame(self.notebook, bg="#e0f7fa")
        self.notebook.add(tab_productos, text="Productos")

        # Pestaña de servicios
        tab_servicios = tk.Frame(self.notebook, bg="#e0f7fa")
        self.notebook.add(tab_servicios, text="Servicios")

        # Configurar pestaña de productos
        self.configurar_tab_productos(tab_productos)

        # Configurar pestaña de servicios
        self.configurar_tab_servicios(tab_servicios)

        # Frame para mostrar items seleccionados
        frame_items = tk.Frame(self.frame_principal, bg="#e0f7fa")
        frame_items.pack(fill=tk.BOTH, expand=True, pady=10)

        lbl_items = tk.Label(
            frame_items,
            text="Items seleccionados:",
            font=("Helvetica", 12, "bold"),
            bg="#e0f7fa"
        )
        lbl_items.pack(anchor=tk.W, pady=5)

        # Tabla de items seleccionados
        columnas = ('tipo', 'nombre', 'cantidad', 'precio_unitario', 'subtotal')

        self.tabla_items = ttk.Treeview(frame_items, columns=columnas, show='headings', height=7)

        # Configurar encabezados
        self.tabla_items.heading('tipo', text='Tipo')
        self.tabla_items.heading('nombre', text='Descripción')
        self.tabla_items.heading('cantidad', text='Cantidad')
        self.tabla_items.heading('precio_unitario', text='Precio Unit.')
        self.tabla_items.heading('subtotal', text='Subtotal')

        # Configurar anchos
        self.tabla_items.column('tipo', width=100, anchor=tk.CENTER)
        self.tabla_items.column('nombre', width=300)
        self.tabla_items.column('cantidad', width=80, anchor=tk.CENTER)
        self.tabla_items.column('precio_unitario', width=100, anchor=tk.CENTER)
        self.tabla_items.column('subtotal', width=100, anchor=tk.CENTER)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_items, orient=tk.VERTICAL, command=self.tabla_items.yview)
        self.tabla_items.configure(yscrollcommand=scrollbar.set)

        # Empaquetar tabla y scrollbar
        self.tabla_items.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame para botones de control de items
        frame_control_items = tk.Frame(self.frame_principal, bg="#e0f7fa")
        frame_control_items.pack(fill=tk.X, pady=5)

        btn_quitar_item = tk.Button(
            frame_control_items,
            text="Quitar Item",
            font=("Helvetica", 10),
            bg="#e57373",
            fg="white",
            command=self.quitar_item
        )
        btn_quitar_item.pack(side=tk.LEFT, padx=5)

        btn_limpiar = tk.Button(
            frame_control_items,
            text="Limpiar Todo",
            font=("Helvetica", 10),
            bg="#c62828",
            fg="white",
            command=self.limpiar_venta
        )
        btn_limpiar.pack(side=tk.LEFT, padx=5)

        # Frame para el total y botón de pago
        frame_total = tk.Frame(self.frame_principal, bg="#e0f7fa")
        frame_total.pack(fill=tk.X, pady=10)

        lbl_total_titulo = tk.Label(
            frame_total,
            text="TOTAL:",
            font=("Helvetica", 14, "bold"),
            bg="#e0f7fa"
        )
        lbl_total_titulo.pack(side=tk.LEFT, padx=5)

        self.lbl_total = tk.Label(
            frame_total,
            text="$0.00",
            font=("Helvetica", 14, "bold"),
            bg="#e0f7fa",
            fg="#00796b"
        )
        self.lbl_total.pack(side=tk.LEFT, padx=5)

        btn_procesar_pago = tk.Button(
            frame_total,
            text="Procesar Pago",
            font=("Helvetica", 12, "bold"),
            bg="#00796b",
            fg="white",
            command=self.procesar_pago
        )
        btn_procesar_pago.pack(side=tk.RIGHT, padx=10)

        # Botón para volver
        btn_volver = tk.Button(
            self.frame_principal,
            text="Volver",
            font=("Helvetica", 12),
            bg="#c62828",
            fg="white",
            command=self.ventana.destroy
        )
        btn_volver.pack(pady=10)

        # Cargar datos iniciales
        self.cargar_productos()
        self.cargar_servicios()

    def configurar_tab_productos(self, tab):
        # Frame para búsqueda
        frame_busqueda = tk.Frame(tab, bg="#e0f7fa")
        frame_busqueda.pack(fill=tk.X, pady=10)

        lbl_buscar = tk.Label(
            frame_busqueda,
            text="Buscar producto:",
            font=("Helvetica", 11),
            bg="#e0f7fa"
        )
        lbl_buscar.pack(side=tk.LEFT, padx=5)

        self.entry_buscar_producto = tk.Entry(frame_busqueda, width=30, font=("Helvetica", 11))
        self.entry_buscar_producto.pack(side=tk.LEFT, padx=5)

        btn_buscar_producto = tk.Button(
            frame_busqueda,
            text="Buscar",
            font=("Helvetica", 10),
            bg="#00796b",
            fg="white",
            command=lambda: self.buscar_productos(self.entry_buscar_producto.get().strip())
        )
        btn_buscar_producto.pack(side=tk.LEFT, padx=5)

        # Tabla de productos
        frame_tabla = tk.Frame(tab, bg="#e0f7fa")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=5)

        columnas = ('id', 'nombre', 'precio', 'stock')

        self.tabla_productos = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=7)

        # Configurar encabezados
        self.tabla_productos.heading('id', text='ID')
        self.tabla_productos.heading('nombre', text='Nombre')
        self.tabla_productos.heading('precio', text='Precio')
        self.tabla_productos.heading('stock', text='Stock')

        # Configurar anchos
        self.tabla_productos.column('id', width=50, anchor=tk.CENTER)
        self.tabla_productos.column('nombre', width=300)
        self.tabla_productos.column('precio', width=100, anchor=tk.CENTER)
        self.tabla_productos.column('stock', width=100, anchor=tk.CENTER)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_productos.yview)
        self.tabla_productos.configure(yscrollcommand=scrollbar.set)

        # Empaquetar tabla y scrollbar
        self.tabla_productos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame para agregar producto
        frame_agregar = tk.Frame(tab, bg="#e0f7fa")
        frame_agregar.pack(fill=tk.X, pady=10)

        lbl_cantidad = tk.Label(
            frame_agregar,
            text="Cantidad:",
            font=("Helvetica", 11),
            bg="#e0f7fa"
        )
        lbl_cantidad.pack(side=tk.LEFT, padx=5)

        self.entry_cantidad_producto = tk.Entry(frame_agregar, width=5, font=("Helvetica", 11))
        self.entry_cantidad_producto.pack(side=tk.LEFT, padx=5)
        self.entry_cantidad_producto.insert(0, "1")  # Valor por defecto

        btn_agregar_producto = tk.Button(
            frame_agregar,
            text="Agregar a la venta",
            font=("Helvetica", 10),
            bg="#00796b",
            fg="white",
            command=self.agregar_producto_seleccionado
        )
        btn_agregar_producto.pack(side=tk.LEFT, padx=10)

    def configurar_tab_servicios(self, tab):
        # Frame para búsqueda
        frame_busqueda = tk.Frame(tab, bg="#e0f7fa")
        frame_busqueda.pack(fill=tk.X, pady=10)

        lbl_buscar = tk.Label(
            frame_busqueda,
            text="Buscar servicio:",
            font=("Helvetica", 11),
            bg="#e0f7fa"
        )
        lbl_buscar.pack(side=tk.LEFT, padx=5)

        self.entry_buscar_servicio = tk.Entry(frame_busqueda, width=30, font=("Helvetica", 11))
        self.entry_buscar_servicio.pack(side=tk.LEFT, padx=5)

        btn_buscar_servicio = tk.Button(
            frame_busqueda,
            text="Buscar",
            font=("Helvetica", 10),
            bg="#00796b",
            fg="white",
            command=lambda: self.buscar_servicios(self.entry_buscar_servicio.get().strip())
        )
        btn_buscar_servicio.pack(side=tk.LEFT, padx=5)

        # Tabla de servicios
        frame_tabla = tk.Frame(tab, bg="#e0f7fa")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=5)

        columnas = ('id', 'nombre', 'descripcion', 'precio', 'tiempo')

        self.tabla_servicios = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=7)

        # Configurar encabezados
        self.tabla_servicios.heading('id', text='ID')
        self.tabla_servicios.heading('nombre', text='Nombre')
        self.tabla_servicios.heading('descripcion', text='Descripción')
        self.tabla_servicios.heading('precio', text='Precio')
        self.tabla_servicios.heading('tiempo', text='Tiempo Est.')

        # Configurar anchos
        self.tabla_servicios.column('id', width=50, anchor=tk.CENTER)
        self.tabla_servicios.column('nombre', width=150)
        self.tabla_servicios.column('descripcion', width=200)
        self.tabla_servicios.column('precio', width=100, anchor=tk.CENTER)
        self.tabla_servicios.column('tiempo', width=100, anchor=tk.CENTER)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_servicios.yview)
        self.tabla_servicios.configure(yscrollcommand=scrollbar.set)

        # Empaquetar tabla y scrollbar
        self.tabla_servicios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame para agregar servicio
        frame_agregar = tk.Frame(tab, bg="#e0f7fa")
        frame_agregar.pack(fill=tk.X, pady=10)

        lbl_cantidad = tk.Label(
            frame_agregar,
            text="Cantidad:",
            font=("Helvetica", 11),
            bg="#e0f7fa"
        )
        lbl_cantidad.pack(side=tk.LEFT, padx=5)

        self.entry_cantidad_servicio = tk.Entry(frame_agregar, width=5, font=("Helvetica", 11))
        self.entry_cantidad_servicio.pack(side=tk.LEFT, padx=5)
        self.entry_cantidad_servicio.insert(0, "1")  # Valor por defecto

        btn_agregar_servicio = tk.Button(
            frame_agregar,
            text="Agregar a la venta",
            font=("Helvetica", 10),
            bg="#00796b",
            fg="white",
            command=self.agregar_servicio_seleccionado
        )
        btn_agregar_servicio.pack(side=tk.LEFT, padx=10)

    def cargar_productos(self):
        # Limpiar tabla
        for item in self.tabla_productos.get_children():
            self.tabla_productos.delete(item)

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("SELECT id_producto, nombre, precio, stock FROM productos WHERE stock > 0 ORDER BY nombre")

            for producto in cursor.fetchall():
                self.tabla_productos.insert('', tk.END, values=producto)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los productos: {str(e)}")

    def cargar_servicios(self):
        # Limpiar tabla
        for item in self.tabla_servicios.get_children():
            self.tabla_servicios.delete(item)

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_servicio, nombre, descripcion, precio, 
                       CONCAT(tiempo_estimado, ' min') as tiempo 
                FROM servicios 
                WHERE activo = 1 
                ORDER BY nombre
            """)

            for servicio in cursor.fetchall():
                self.tabla_servicios.insert('', tk.END, values=servicio)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los servicios: {str(e)}")

    def buscar_productos(self, texto_busqueda):
        # Limpiar tabla
        for item in self.tabla_productos.get_children():
            self.tabla_productos.delete(item)

        if not texto_busqueda:
            self.cargar_productos()
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Búsqueda por nombre o ID
            consulta = """
            SELECT id_producto, nombre, precio, stock 
            FROM productos 
            WHERE stock > 0 AND (nombre LIKE %s OR id_producto = %s)
            ORDER BY nombre
            """

            # Intenta convertir el texto de búsqueda a un número para buscar por ID
            try:
                id_busqueda = int(texto_busqueda)
            except ValueError:
                id_busqueda = -1  # Valor que no existirá como ID

            cursor.execute(consulta, (f"%{texto_busqueda}%", id_busqueda))

            for producto in cursor.fetchall():
                self.tabla_productos.insert('', tk.END, values=producto)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar productos: {str(e)}")

    def buscar_servicios(self, texto_busqueda):
        # Limpiar tabla
        for item in self.tabla_servicios.get_children():
            self.tabla_servicios.delete(item)

        if not texto_busqueda:
            self.cargar_servicios()
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Búsqueda por nombre, descripción o ID
            consulta = """
            SELECT id_servicio, nombre, descripcion, precio, 
                   CONCAT(tiempo_estimado, ' min') as tiempo 
            FROM servicios 
            WHERE activo = 1 AND (nombre LIKE %s OR descripcion LIKE %s OR id_servicio = %s)
            ORDER BY nombre
            """

            # Intenta convertir el texto de búsqueda a un número para buscar por ID
            try:
                id_busqueda = int(texto_busqueda)
            except ValueError:
                id_busqueda = -1  # Valor que no existirá como ID

            cursor.execute(consulta, (f"%{texto_busqueda}%", f"%{texto_busqueda}%", id_busqueda))

            for servicio in cursor.fetchall():
                self.tabla_servicios.insert('', tk.END, values=servicio)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar servicios: {str(e)}")

    def agregar_producto_seleccionado(self):
        # Obtener el producto seleccionado
        seleccion = self.tabla_productos.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un producto para agregar")
            return

        # Obtener datos del producto seleccionado
        valores = self.tabla_productos.item(seleccion[0], 'values')
        id_producto = valores[0]
        nombre_producto = valores[1]
        precio_producto = float(valores[2])
        stock_disponible = int(valores[3])

        # Obtener cantidad deseada
        try:
            cantidad = int(self.entry_cantidad_producto.get().strip())
            if cantidad <= 0:
                messagebox.showwarning("Valor inválido", "La cantidad debe ser un número positivo")
                return
            if cantidad > stock_disponible:
                messagebox.showwarning("Stock insuficiente", f"Solo hay {stock_disponible} unidades disponibles")
                return
        except ValueError:
            messagebox.showwarning("Valor inválido", "La cantidad debe ser un número entero")
            return

        # Calcular subtotal
        subtotal = precio_producto * cantidad

        # Agregar a la lista de items
        item = {
            'tipo': 'producto',
            'id': id_producto,
            'nombre': nombre_producto,
            'cantidad': cantidad,
            'precio_unitario': precio_producto,
            'subtotal': subtotal
        }

        # Verificar si ya existe este producto en la lista y actualizar cantidad si es el caso
        existe = False
        for i, it in enumerate(self.items_venta):
            if it['tipo'] == 'producto' and it['id'] == id_producto:
                # Actualizar cantidad y subtotal
                nueva_cantidad = it['cantidad'] + cantidad
                if nueva_cantidad > stock_disponible:
                    messagebox.showwarning("Stock insuficiente",
                                           f"No se puede agregar {cantidad} más. Stock disponible: {stock_disponible}")
                    return
                self.items_venta[i]['cantidad'] = nueva_cantidad
                self.items_venta[i]['subtotal'] = precio_producto * nueva_cantidad
                existe = True
                break

        if not existe:
            self.items_venta.append(item)

        # Actualizar tabla y total
        self.actualizar_tabla_items()
        self.calcular_total()

    def agregar_servicio_seleccionado(self):
        # Obtener el servicio seleccionado
        seleccion = self.tabla_servicios.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un servicio para agregar")
            return

        # Obtener datos del servicio seleccionado
        valores = self.tabla_servicios.item(seleccion[0], 'values')
        id_servicio = valores[0]
        nombre_servicio = valores[1]
        precio_servicio = float(valores[3])

        # Obtener cantidad deseada
        try:
            cantidad = int(self.entry_cantidad_servicio.get().strip())
            if cantidad <= 0:
                messagebox.showwarning("Valor inválido", "La cantidad debe ser un número positivo")
                return
        except ValueError:
            messagebox.showwarning("Valor inválido", "La cantidad debe ser un número entero")
            return

        # Calcular subtotal
        subtotal = precio_servicio * cantidad

        # Agregar a la lista de items
        item = {
            'tipo': 'servicio',
            'id': id_servicio,
            'nombre': nombre_servicio,
            'cantidad': cantidad,
            'precio_unitario': precio_servicio,
            'subtotal': subtotal
        }

        # Verificar si ya existe este servicio en la lista y actualizar cantidad si es el caso
        existe = False
        for i, it in enumerate(self.items_venta):
            if it['tipo'] == 'servicio' and it['id'] == id_servicio:
                # Actualizar cantidad y subtotal
                nueva_cantidad = it['cantidad'] + cantidad
                self.items_venta[i]['cantidad'] = nueva_cantidad
                self.items_venta[i]['subtotal'] = precio_servicio * nueva_cantidad
                existe = True
                break

        if not existe:
            self.items_venta.append(item)

        # Actualizar tabla y total
        self.actualizar_tabla_items()
        self.calcular_total()

    def actualizar_tabla_items(self):
        # Limpiar tabla
        for item in self.tabla_items.get_children():
            self.tabla_items.delete(item)

        # Agregar items a la tabla
        for item in self.items_venta:
            valores = (
                item['tipo'].capitalize(),
                item['nombre'],
                item['cantidad'],
                f"${item['precio_unitario']:.2f}",
                f"${item['subtotal']:.2f}"
            )
            self.tabla_items.insert('', tk.END, values=valores)

    def calcular_total(self):
        # Calcular total de la venta
        self.total_venta = sum(item['subtotal'] for item in self.items_venta)
        self.lbl_total.config(text=f"${self.total_venta:.2f}")

    def quitar_item(self):
        # Obtener el item seleccionado
        seleccion = self.tabla_items.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un item para quitar")
            return

        # Eliminar de la lista
        indice = self.tabla_items.index(seleccion[0])
        del self.items_venta[indice]

        # Actualizar tabla y total
        self.actualizar_tabla_items()
        self.calcular_total()

    def limpiar_venta(self):
        # Confirmar acción
        if messagebox.askyesno("Confirmar", "¿Estás seguro de limpiar todos los items?"):
            self.items_venta = []
            self.actualizar_tabla_items()
            self.calcular_total()

    def seleccionar_cliente(self):
        # Abrir ventana para buscar y seleccionar cliente
        ventana_buscar = tk.Toplevel(self.ventana)
        ventana_buscar.title("Seleccionar Cliente")
        ventana_buscar.geometry("700x500")
        ventana_buscar.config(bg="#e0f7fa")
        ventana_buscar.grab_set()  # Hacer modal

        # Frame principal
        frame_principal = tk.Frame(ventana_buscar, bg="#e0f7fa")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        titulo = tk.Label(
            frame_principal,
            text="Buscar y Seleccionar Cliente",
            font=("Helvetica", 16, "bold"),
            bg="#e0f7fa",
            fg="#00796b"
        )
        titulo.pack(pady=10)

        # Frame para búsqueda
        frame_busqueda = tk.Frame(frame_principal, bg="#e0f7fa")
        frame_busqueda.pack(fill=tk.X, pady=10)

        lbl_buscar = tk.Label(
            frame_busqueda,
            text="Buscar:",
            font=("Helvetica", 12),
            bg="#e0f7fa"
        )
        lbl_buscar.pack(side=tk.LEFT, padx=5)

        entry_buscar = tk.Entry(frame_busqueda, width=30, font=("Helvetica", 12))
        entry_buscar.pack(side=tk.LEFT, padx=5)

        btn_buscar = tk.Button(
            frame_busqueda,
            text="Buscar",
            font=("Helvetica", 12),
            bg="#00796b",
            fg="white",
            command=lambda: buscar_clientes(entry_buscar.get().strip())
        )
        btn_buscar.pack(side=tk.LEFT, padx=5)

        # Frame para la tabla
        frame_tabla = tk.Frame(frame_principal, bg="#e0f7fa")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10)

        # Tabla de clientes
        columnas = ('id', 'nombre', 'telefono', 'correo', 'puntos')

        tabla_clientes = ttk.Treeview(frame_tabla, columns=columnas, show='headings')

        # Configurar encabezados
        tabla_clientes.heading('id', text='ID')
        tabla_clientes.heading('nombre', text='Nombre')
        tabla_clientes.heading('telefono', text='Teléfono')
        tabla_clientes.heading('correo', text='Correo')
        tabla_clientes.heading('puntos', text='Puntos')

        # Configurar anchos
        tabla_clientes.column('id', width=50, anchor=tk.CENTER)
        tabla_clientes.column('nombre', width=200)
        tabla_clientes.column('telefono', width=100, anchor=tk.CENTER)
        tabla_clientes.column('correo', width=150)
        tabla_clientes.column('puntos', width=80, anchor=tk.CENTER)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=tabla_clientes.yview)
        tabla_clientes.configure(yscrollcommand=scrollbar.set)

        # Empaquetar tabla y scrollbar
        tabla_clientes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Botones de acción
        frame_botones = tk.Frame(frame_principal, bg="#e0f7fa")
        frame_botones.pack(pady=10)

        btn_seleccionar = tk.Button(
            frame_botones,
            text="Seleccionar",
            font=("Helvetica", 12),
            bg="#00796b",
            fg="white",
            command=lambda: seleccionar_cliente_accion()
        )
        btn_seleccionar.pack(side=tk.LEFT, padx=5)

        btn_nuevo_cliente = tk.Button(
            frame_botones,
            text="Nuevo Cliente",
            font=("Helvetica", 12),
            bg="#00796b",
            fg="white",
            command=nuevo_cliente
        )
        btn_nuevo_cliente.pack(side=tk.LEFT, padx=5)

        btn_cancelar = tk.Button(
            frame_botones,
            text="Cancelar",
            font=("Helvetica", 12),
            bg="#c62828",
            fg="white",
            command=ventana_buscar.destroy
        )
        btn_cancelar.pack(side=tk.LEFT, padx=5)

        # Función para cargar clientes
        def cargar_clientes():
            # Limpiar tabla
            for item in tabla_clientes.get_children():
                tabla_clientes.delete(item)

            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()
                cursor.execute(
                    "SELECT id_cliente, nombre, telefono, correo, puntos FROM clientes ORDER BY nombre")

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

                # Búsqueda por nombre, teléfono o correo
                consulta = """
                SELECT id_cliente, nombre, telefono, correo, puntos 
                FROM clientes 
                WHERE nombre LIKE %s OR telefono LIKE %s OR correo LIKE %s
                ORDER BY nombre
                """

                cursor.execute(consulta, (f"%{texto_busqueda}%", f"%{texto_busqueda}%", f"%{texto_busqueda}%"))

                for cliente in cursor.fetchall():
                    tabla_clientes.insert('', tk.END, values=cliente)

                conexion.close()
            except Exception as e:
                messagebox.showerror("Error", f"Error al buscar clientes: {str(e)}")

        # Función para seleccionar cliente
        def seleccionar_cliente_accion():
            seleccion = tabla_clientes.selection()

            if not seleccion:
                messagebox.showwarning("Selección requerida", "Por favor, selecciona un cliente")
                return

            # Obtener datos del cliente seleccionado
            valores = tabla_clientes.item(seleccion[0], 'values')
            self.cliente_actual = {
                'id': valores[0],
                'nombre': valores[1],
                'puntos': valores[4]
            }

            # Actualizar etiqueta de cliente seleccionado
            self.lbl_cliente_seleccionado.config(
                text=f"{self.cliente_actual['nombre']} (Puntos: {self.cliente_actual['puntos']})",
                fg="#00796b"
            )

            # Cerrar ventana
            ventana_buscar.destroy()

        # Función para agregar nuevo cliente (versión simplificada)
        def nuevo_cliente():
            ventana_nuevo = tk.Toplevel(ventana_buscar)
            ventana_nuevo.title("Nuevo Cliente")
            ventana_nuevo.geometry("400x300")
            ventana_nuevo.config(bg="#e0f7fa")
            ventana_nuevo.grab_set()  # Hacer modal

            # Frame para el formulario
            frame_form = tk.Frame(ventana_nuevo, bg="#e0f7fa")
            frame_form.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

            # Campos del formulario
            tk.Label(frame_form, text="Nombre:", font=("Helvetica", 12), bg="#e0f7fa").grid(row=0, column=0,
                                                                                            sticky=tk.W, pady=5)
            entry_nombre = tk.Entry(frame_form, font=("Helvetica", 12))
            entry_nombre.grid(row=0, column=1, sticky=tk.W + tk.E, pady=5, padx=5)

            tk.Label(frame_form, text="Teléfono:", font=("Helvetica", 12), bg="#e0f7fa").grid(row=1, column=0,
                                                                                              sticky=tk.W, pady=5)
            entry_telefono = tk.Entry(frame_form, font=("Helvetica", 12))
            entry_telefono.grid(row=1, column=1, sticky=tk.W + tk.E, pady=5, padx=5)

            tk.Label(frame_form, text="Correo:", font=("Helvetica", 12), bg="#e0f7fa").grid(row=2, column=0,
                                                                                            sticky=tk.W, pady=5)
            entry_correo = tk.Entry(frame_form, font=("Helvetica", 12))
            entry_correo.grid(row=2, column=1, sticky=tk.W + tk.E, pady=5, padx=5)

            frame_botones = tk.Frame(ventana_nuevo, bg="#e0f7fa")
            frame_botones.pack(pady=10)

            def guardar_nuevo_cliente():
                nombre = entry_nombre.get().strip()
                telefono = entry_telefono.get().strip()
                correo = entry_correo.get().strip()

                if not nombre:
                    messagebox.showwarning("Dato requerido", "El nombre es obligatorio")
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

                    # Seleccionar automáticamente al nuevo cliente
                    self.cliente_actual = {
                        'id': id_cliente,
                        'nombre': nombre,
                        'puntos': 0
                    }

                    # Actualizar etiqueta
                    self.lbl_cliente_seleccionado.config(
                        text=f"{nombre} (Puntos: 0)",
                        fg="#00796b"
                    )

                    messagebox.showinfo("Éxito", "Cliente registrado correctamente")
                    ventana_nuevo.destroy()
                    ventana_buscar.destroy()

                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo registrar el cliente: {str(e)}")

            btn_guardar = tk.Button(
                frame_botones,
                text="Guardar",
                font=("Helvetica", 12),
                bg="#00796b",
                fg="white",
                command=guardar_nuevo_cliente
            )
            btn_guardar.pack(side=tk.LEFT, padx=5)

            btn_cancelar = tk.Button(
                frame_botones,
                text="Cancelar",
                font=("Helvetica", 12),
                bg="#c62828",
                fg="white",
                command=ventana_nuevo.destroy
            )
            btn_cancelar.pack(side=tk.LEFT, padx=5)

        # Cargar clientes al iniciar
        cargar_clientes()