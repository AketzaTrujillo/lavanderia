"""
Módulo de Ventas para el Sistema de Gestión de Lavandería
Permite registrar ventas de productos y servicios, calcular totales,
y generar tickets.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import BOLD
import os
import sys
import utileria as utl
from datetime import datetime
from conexion import conectar_bd
from tkinter import simpledialog
import webbrowser



class Ventas:
    def __init__(self, ventana_padre=None, id_usuario=None):
        # Crear ventana
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Módulo de Ventas - Lavandería")
        self.ventana.geometry("1200x900")  # Hacer la ventana más alta
        self.ventana.minsize(1200, 900)  # Establecer tamaño mínimo
        self.ventana.config(bg="#e0f7fa")
        self.ventana.resizable(True, True)

        if ventana_padre:
            utl.centrar_ventana(self.ventana, 1100, 900)
            self.ventana.transient(ventana_padre)
            self.ventana.grab_set()

        # Variables
        self.items_venta = []
        self.cliente_actual = None
        self.total_venta = 0.0
        self.id_usuario_actual = id_usuario if id_usuario is not None else 1
        print(f"DEBUG - ID usuario en ventas: {self.id_usuario_actual}")

        # Construir la interfaz
        self.construir_interfaz()

        if not ventana_padre:
            self.ventana.mainloop()

    def construir_interfaz(self):
        # Frame principal
        self.frame_principal = tk.Frame(self.ventana, bg="#f5f7fa")
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        tk.Label(
            self.frame_principal,
            text="Registro de Ventas",
            font=("Helvetica", 22, "bold"),
            bg="#f5f7fa",
            fg="#1976D2"
        ).pack(pady=(0, 18))

        # =================== CLIENTE ====================
        frame_cliente = tk.Frame(self.frame_principal, bg="#e3f2fd", bd=1, relief="solid")
        frame_cliente.pack(fill=tk.X, pady=(0, 18), padx=10)

        tk.Label(frame_cliente, text="Cliente:", font=("Helvetica", 13, "bold"), bg="#e3f2fd", fg="#1565C0").pack(side=tk.LEFT, padx=10, pady=8)

        self.lbl_cliente_seleccionado = tk.Label(frame_cliente, text="No seleccionado", font=("Helvetica", 13), bg="#e3f2fd", fg="#757575")
        self.lbl_cliente_seleccionado.pack(side=tk.LEFT, padx=10)

        btn_seleccionar_cliente = tk.Button(
            frame_cliente, text="Seleccionar Cliente", font=("Helvetica", 11, "bold"),
            bg="#1976D2", fg="white", activebackground="#1565C0", activeforeground="white",
            relief="flat", cursor="hand2", command=self.seleccionar_cliente
        )
        btn_seleccionar_cliente.pack(side=tk.RIGHT, padx=10, pady=8)

        # =================== TABS ====================
        self.notebook = ttk.Notebook(self.frame_principal)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 18), padx=10)

        tab_productos = tk.Frame(self.notebook, bg="#f5f7fa")
        tab_servicios = tk.Frame(self.notebook, bg="#f5f7fa")

        self.notebook.add(tab_productos, text="Productos")
        self.notebook.add(tab_servicios, text="Servicios")

        self.configurar_tab_productos(tab_productos)
        self.configurar_tab_servicios(tab_servicios)

        # =================== TABLA ITEMS ====================
        frame_tabla = tk.Frame(self.frame_principal, bg="#f5f7fa")
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.tabla_items = ttk.Treeview(
            frame_tabla,
            columns=('tipo', 'nombre', 'cantidad', 'precio_unitario', 'subtotal'),
            show='headings',
            height=8
        )
        for col in ('tipo', 'nombre', 'cantidad', 'precio_unitario', 'subtotal'):
            self.tabla_items.heading(col, text=col.capitalize())
            self.tabla_items.column(col, width=120, anchor=tk.CENTER)
        self.tabla_items.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_items.yview)
        self.tabla_items.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # =================== BOTONES DE CONTROL ====================
        frame_botones = tk.Frame(self.frame_principal, bg="#f5f7fa")
        frame_botones.pack(fill=tk.X, pady=(0, 8), padx=10)

        tk.Button(
            frame_botones, text="Quitar Item", font=("Helvetica", 11),
            bg="#e57373", fg="white", activebackground="#d32f2f", activeforeground="white",
            relief="flat", cursor="hand2", command=self.quitar_item
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            frame_botones, text="Limpiar Todo", font=("Helvetica", 11),
            bg="#c62828", fg="white", activebackground="#b71c1c", activeforeground="white",
            relief="flat", cursor="hand2", command=self.limpiar_venta
        ).pack(side=tk.LEFT, padx=5)

        # =================== TOTAL Y PROCESAR ====================
        frame_total = tk.Frame(self.frame_principal, bg="#e3f2fd", bd=1, relief="solid")
        frame_total.pack(fill=tk.X, pady=(0, 8), padx=10)

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
            frame_total, text="Procesar Pago", font=("Helvetica", 13, "bold"),
            bg="#1976D2", fg="white", activebackground="#1565C0", activeforeground="white",
            relief="flat", cursor="hand2", command=self.procesar_pago
        ).pack(side=tk.RIGHT, padx=10, pady=10)

        # =================== VOLVER ====================
        frame_volver = tk.Frame(self.frame_principal, bg="#f5f7fa")
        frame_volver.pack(fill=tk.X, pady=(0, 5), padx=10)

        tk.Button(
            frame_volver, text="Volver", font=("Helvetica", 12),
            bg="#c62828", fg="white", activebackground="#b71c1c", activeforeground="white",
            relief="flat", cursor="hand2", command=self.ventana.destroy
        ).pack(side=tk.RIGHT, padx=10, pady=5)




    def configurar_tab_productos(self, tab):
        frame_busqueda = tk.Frame(tab, bg="#e0f7fa")
        frame_busqueda.pack(fill=tk.X, pady=10)

        lbl_buscar = tk.Label(frame_busqueda, text="Buscar producto:", font=("Helvetica", 11), bg="#e0f7fa")
        lbl_buscar.pack(side=tk.LEFT, padx=5)

        self.entry_buscar_producto = tk.Entry(frame_busqueda, width=30, font=("Helvetica", 11))
        self.entry_buscar_producto.pack(side=tk.LEFT, padx=5)

        self.entry_buscar_producto.bind("<Return>", lambda event: self.buscar_productos(self.entry_buscar_producto.get().strip()))

        btn_buscar_producto = tk.Button(
            frame_busqueda, text="Buscar", font=("Helvetica", 10),
            bg="#00796b", fg="white", command=lambda: self.buscar_productos(self.entry_buscar_producto.get().strip())
        )
        btn_buscar_producto.pack(side=tk.LEFT, padx=5)

        # Tabla de productos
        columnas = ('id', 'nombre', 'precio', 'stock', 'promo')
        self.tabla_productos = ttk.Treeview(tab, columns=columnas, show='headings', height=7)

        # Configurar encabezados más claros y con anchos adecuados
        self.tabla_productos.heading('id', text='ID')
        self.tabla_productos.heading('nombre', text='PRODUCTO')
        self.tabla_productos.heading('precio', text='PRECIO')
        self.tabla_productos.heading('stock', text='STOCK')
        self.tabla_productos.heading('promo', text='PROMO')

        # Configurar anchos adecuados
        self.tabla_productos.column('id', width=50, anchor=tk.CENTER)
        self.tabla_productos.column('nombre', width=250, anchor=tk.W)
        self.tabla_productos.column('precio', width=100, anchor=tk.CENTER)
        self.tabla_productos.column('stock', width=80, anchor=tk.CENTER)
        self.tabla_productos.column('promo', width=120, anchor=tk.CENTER)

        # Aplicar estilo a la tabla
        utl.aplicar_estilo_tabla(self.tabla_productos)

        self.tabla_productos.pack(fill=tk.BOTH, expand=True, pady=10)
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.tabla_productos.yview)
        self.tabla_productos.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame agregar
        frame_agregar = tk.Frame(tab, bg="#e0f7fa")
        frame_agregar.pack(fill=tk.X, pady=10)

        lbl_cantidad = tk.Label(frame_agregar, text="Cantidad:", font=("Helvetica", 11), bg="#e0f7fa")
        lbl_cantidad.pack(side=tk.LEFT, padx=5)

        self.entry_cantidad_producto = tk.Entry(frame_agregar, width=5, font=("Helvetica", 11))
        self.entry_cantidad_producto.pack(side=tk.LEFT, padx=5)
        self.entry_cantidad_producto.insert(0, "1")

        btn_agregar_producto = tk.Button(
            frame_agregar, text="Agregar a la venta", font=("Helvetica", 10),
            bg="#00796b", fg="white", command=self.agregar_producto_seleccionado
        )
        btn_agregar_producto.pack(side=tk.LEFT, padx=10)

        # Aquí cargas los productos inmediatamente
        self.cargar_productos()

    def configurar_tab_servicios(self, tab):
        frame_busqueda = tk.Frame(tab, bg="#e0f7fa")
        frame_busqueda.pack(fill=tk.X, pady=10)

        lbl_buscar = tk.Label(frame_busqueda, text="Buscar servicio:", font=("Helvetica", 11), bg="#e0f7fa")
        lbl_buscar.pack(side=tk.LEFT, padx=5)

        self.entry_buscar_servicio = tk.Entry(frame_busqueda, width=30, font=("Helvetica", 11))
        self.entry_buscar_servicio.pack(side=tk.LEFT, padx=5)

        self.entry_buscar_servicio.bind("<Return>", lambda event: self.buscar_servicios(self.entry_buscar_servicio.get().strip()))

        btn_buscar_servicio = tk.Button(
            frame_busqueda, text="Buscar", font=("Helvetica", 10),
            bg="#00796b", fg="white", command=lambda: self.buscar_servicios(self.entry_buscar_servicio.get().strip())
        )
        btn_buscar_servicio.pack(side=tk.LEFT, padx=5)

        # Tabla de servicios
        columnas = ('id', 'nombre', 'descripcion', 'precio', 'tiempo', 'promo')
        self.tabla_servicios = ttk.Treeview(tab, columns=columnas, show='headings', height=7)
        for col in columnas:
            self.tabla_servicios.heading(col, text=col.capitalize())
            self.tabla_servicios.column(col, width=100, anchor=tk.CENTER)
        self.tabla_servicios.pack(fill=tk.BOTH, expand=True, pady=10)

        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.tabla_servicios.yview)
        self.tabla_servicios.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame agregar
        frame_agregar = tk.Frame(tab, bg="#e0f7fa")
        frame_agregar.pack(fill=tk.X, pady=10)

        lbl_cantidad = tk.Label(frame_agregar, text="Cantidad:", font=("Helvetica", 11), bg="#e0f7fa")
        lbl_cantidad.pack(side=tk.LEFT, padx=5)

        self.entry_cantidad_servicio = tk.Entry(frame_agregar, width=5, font=("Helvetica", 11))
        self.entry_cantidad_servicio.pack(side=tk.LEFT, padx=5)
        self.entry_cantidad_servicio.insert(0, "1")

        btn_agregar_servicio = tk.Button(
            frame_agregar, text="Agregar a la venta", font=("Helvetica", 10),
            bg="#00796b", fg="white", command=self.agregar_servicio_seleccionado
        )
        btn_agregar_servicio.pack(side=tk.LEFT, padx=10)

        #Cargar servicios al iniciar
        self.cargar_servicios()

    def cargar_productos(self):
        for item in self.tabla_productos.get_children():
            self.tabla_productos.delete(item)

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            # Ahora también traemos promo_desc y nuevo_precio
            cursor.execute("SELECT id_producto, nombre, precio, stock, promo_desc, nuevo_precio FROM productos ORDER BY nombre")

            for producto in cursor.fetchall():
                # Usar el precio promocional si existe
                precio_final = float(producto[5]) if producto[5] is not None else float(producto[2])
                precio_formateado = f"${precio_final:.2f}"
                promo = producto[4] if producto[4] else ""
                valores = (producto[0], producto[1], precio_formateado, producto[3], promo)

                # Insertar productos sin stock con una etiqueta especial
                if producto[3] <= 0:
                    item_id = self.tabla_productos.insert('', tk.END, values=valores, tags=('sin_stock',))
                else:
                    item_id = self.tabla_productos.insert('', tk.END, values=valores)

            # Configurar color para productos sin stock
            self.tabla_productos.tag_configure('sin_stock', background='#ffcccb', foreground='#8b0000')

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los productos: {str(e)}")

    def buscar_productos(self, texto_busqueda):
        for item in self.tabla_productos.get_children():
            self.tabla_productos.delete(item)

        if not texto_busqueda:
            self.cargar_productos()
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Búsqueda en todos los productos, no solo los que tienen stock
            consulta = """
            SELECT id_producto, nombre, precio, stock 
            FROM productos 
            WHERE nombre LIKE %s OR id_producto = %s
            ORDER BY nombre
            """

            try:
                id_busqueda = int(texto_busqueda)
            except ValueError:
                id_busqueda = -1

            cursor.execute(consulta, (f"%{texto_busqueda}%", id_busqueda))

            for producto in cursor.fetchall():
                precio_formateado = f"${float(producto[2]):.2f}"
                valores = (producto[0], producto[1], precio_formateado, producto[3])

                # Marcar productos sin stock
                if producto[3] <= 0:
                    item_id = self.tabla_productos.insert('', tk.END, values=valores, tags=('sin_stock',))
                else:
                    item_id = self.tabla_productos.insert('', tk.END, values=valores)

            # Configurar color para productos sin stock
            self.tabla_productos.tag_configure('sin_stock', background='#ffcccb', foreground='#8b0000')

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar productos: {str(e)}")

    def agregar_producto_seleccionado(self):
        seleccion = self.tabla_productos.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un producto para agregar")
            return

        valores = self.tabla_productos.item(seleccion[0], 'values')
        id_producto = valores[0]
        nombre_producto = valores[1]
        precio_producto = float(valores[2].replace('$', '').replace(',', ''))
        stock_disponible = int(valores[3])
        promo = valores[4] if len(valores) > 4 else ""

        # Advertir si el producto no tiene stock
        if stock_disponible <= 0:
            if not messagebox.askyesno("Sin Stock",
                                       f"El producto '{nombre_producto}' no tiene stock disponible.\n¿Deseas agregarlo de todas formas?"):
                return

        try:
            cantidad = int(self.entry_cantidad_producto.get().strip())
            if cantidad <= 0:
                messagebox.showwarning("Valor inválido", "La cantidad debe ser un número positivo")
                return

            # Solo verificar stock si hay stock disponible
            if stock_disponible > 0 and cantidad > stock_disponible:
                messagebox.showwarning("Stock insuficiente", f"Solo hay {stock_disponible} unidades disponibles")
                return
        except ValueError:
            messagebox.showwarning("Valor inválido", "La cantidad debe ser un número entero")
            return

        subtotal = precio_producto * cantidad

        item = {
            'tipo': 'producto',
            'id': id_producto,
            'nombre': nombre_producto,
            'cantidad': cantidad,
            'precio_unitario': precio_producto,
            'subtotal': subtotal,
            'promo': promo
        }

        existe = False
        for i, it in enumerate(self.items_venta):
            if it['tipo'] == 'producto' and it['id'] == id_producto:
                nueva_cantidad = it['cantidad'] + cantidad
                if stock_disponible > 0 and nueva_cantidad > stock_disponible:
                    messagebox.showwarning("Stock insuficiente",
                                           f"No se puede agregar {cantidad} más. Stock disponible: {stock_disponible}")
                    return
                self.items_venta[i]['cantidad'] = nueva_cantidad
                self.items_venta[i]['subtotal'] = precio_producto * nueva_cantidad
                existe = True
                break

        if not existe:
            self.items_venta.append(item)

        self.actualizar_tabla_items()
        self.calcular_total()


    def cargar_servicios(self):
        for item in self.tabla_servicios.get_children():
            self.tabla_servicios.delete(item)

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_servicio, nombre, descripcion, precio, 
                       CONCAT(tiempo_estimado, ' min') as tiempo,
                       promo_desc, nuevo_precio
                FROM servicios 
                WHERE activo = 1 
                ORDER BY nombre
            """)

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
        for item in self.tabla_servicios.get_children():
            self.tabla_servicios.delete(item)

        if not texto_busqueda:
            self.cargar_servicios()
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            consulta = """
            SELECT id_servicio, nombre, descripcion, precio, 
                   CONCAT(tiempo_estimado, ' min') as tiempo 
            FROM servicios 
            WHERE activo = 1 AND (nombre LIKE %s OR descripcion LIKE %s OR id_servicio = %s)
            ORDER BY nombre
            """

            try:
                id_busqueda = int(texto_busqueda)
            except ValueError:
                id_busqueda = -1

            cursor.execute(consulta, (f"%{texto_busqueda}%", f"%{texto_busqueda}%", id_busqueda))

            for servicio in cursor.fetchall():
                precio_formateado = f"${float(servicio[3]):.2f}"
                valores = (servicio[0], servicio[1], servicio[2], precio_formateado, servicio[4])
                self.tabla_servicios.insert('', tk.END, values=valores)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar servicios: {str(e)}")



    def agregar_servicio_seleccionado(self):
        seleccion = self.tabla_servicios.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un servicio para agregar")
            return

        valores = self.tabla_servicios.item(seleccion[0], 'values')
        id_servicio = valores[0]
        nombre_servicio = valores[1]
        precio_servicio = float(valores[3].replace('$', '').replace(',', ''))
        promo = valores[5] if len(valores) > 5 else ""

        try:
            cantidad = int(self.entry_cantidad_servicio.get().strip())
            if cantidad <= 0:
                messagebox.showwarning("Valor inválido", "La cantidad debe ser un número positivo")
                return
        except ValueError:
            messagebox.showwarning("Valor inválido", "La cantidad debe ser un número entero")
            return

        subtotal = precio_servicio * cantidad

        item = {
            'tipo': 'servicio',
            'id': id_servicio,
            'nombre': nombre_servicio,
            'cantidad': cantidad,
            'precio_unitario': precio_servicio,
            'subtotal': subtotal,
            'promo': promo
        }
        existe = False
        for i, it in enumerate(self.items_venta):
                if it['tipo'] == 'servicio' and it['id'] == id_servicio:
                    nueva_cantidad = it['cantidad'] + cantidad
                    self.items_venta[i]['cantidad'] = nueva_cantidad
                    self.items_venta[i]['subtotal'] = precio_servicio * nueva_cantidad
                    existe = True
                    break

        if not existe:
                self.items_venta.append(item)

        self.actualizar_tabla_items()
        self.calcular_total()


    # Actualizar Items a comprar

    def actualizar_tabla_items(self):
        # Limpiar tabla
        for item in self.tabla_items.get_children():
            self.tabla_items.delete(item)

        # Agregar los nuevos
        for item in self.items_venta:
            nombre = item['nombre']
            if 'promo' in item and item['promo']:
                nombre = f"{nombre} ({item['promo']})"
            valores = (
                item['tipo'].capitalize(),
                nombre,
                item['cantidad'],
                f"${item['precio_unitario']:.2f}",
                f"${item['subtotal']:.2f}"
            )
            self.tabla_items.insert('', tk.END, values=valores)

        # Aplicar estilo
        utl.aplicar_estilo_tabla(self.tabla_items)

    def calcular_total(self):
        total = sum(item['subtotal'] for item in self.items_venta)
        self.total_venta = total
        self.lbl_total.config(text=f"${total:.2f}")


    def quitar_item(self):
        seleccion = self.tabla_items.selection()
        if not seleccion:
            messagebox.showwarning("Selección requerida", "Selecciona un item para quitar")
            return

        index = self.tabla_items.index(seleccion[0])
        del self.items_venta[index]

        self.actualizar_tabla_items()
        self.calcular_total()


    def limpiar_venta(self):
        self.items_venta.clear()
        self.actualizar_tabla_items()
        self.calcular_total()


    #Proceso para guardar las ventas
    def procesar_pago(self):
        if not self.items_venta:
            messagebox.showwarning("Venta vacía", "Agrega productos o servicios antes de procesar el pago.")
            return

        if not self.cliente_actual:
            messagebox.showwarning("Cliente requerido", "Selecciona un cliente para esta venta.")
            return

        # Crear ventana para procesar pago
        ventana_pago = tk.Toplevel(self.ventana)
        ventana_pago.title("Procesar Pago")
        ventana_pago.geometry("400x450")  # Aumentado para asegurar que los botones se vean
        ventana_pago.config(bg="#f5f5f5")
        ventana_pago.resizable(False, False)
        ventana_pago.grab_set()

        utl.centrar_ventana(ventana_pago, 400, 450)

        # Frame principal con scroll por si acaso
        canvas = tk.Canvas(ventana_pago, bg="#f5f5f5")
        scrollbar = ttk.Scrollbar(ventana_pago, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f5f5f5")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Para permitir scroll con la rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Frame para contenido
        frame_principal = tk.Frame(scrollable_frame, bg="#f5f5f5", padx=20, pady=20)
        frame_principal.pack(fill=tk.BOTH, expand=True)

        # Total a pagar
        tk.Label(
            frame_principal,
            text="TOTAL A PAGAR:",
            font=("Helvetica", 14, "bold"),
            bg="#f5f5f5"
        ).pack(pady=(0, 5))

        tk.Label(
            frame_principal,
            text=f"${self.total_venta:.2f}",
            font=("Helvetica", 18, "bold"),
            bg="#f5f5f5",
            fg="#00796b"
        ).pack(pady=(0, 20))

        # Métodos de pago
        tk.Label(
            frame_principal,
            text="Método de pago:",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5"
        ).pack(anchor=tk.W)

        metodo_pago_var = tk.StringVar(value="Efectivo")

        # Frame para radio buttons
        frame_metodos = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_metodos.pack(fill=tk.X, pady=10)

        # Opciones sin "Combinado"
        metodos = ["Efectivo", "Tarjeta", "Transferencia"]
        for i, metodo in enumerate(metodos):
            rb = tk.Radiobutton(
                frame_metodos,
                text=metodo,
                variable=metodo_pago_var,
                value=metodo,
                bg="#f5f5f5",
                font=("Helvetica", 11),
                command=lambda m=metodo: self.actualizar_pago_efectivo(m, frame_efectivo, entry_recibido, lbl_cambio)
            )
            rb.grid(row=i // 2, column=i % 2, sticky=tk.W, padx=5, pady=5)

        # Frame para pago en efectivo
        frame_efectivo = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_efectivo.pack(fill=tk.X, pady=10)

        tk.Label(
            frame_efectivo,
            text="Efectivo recibido:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).grid(row=0, column=0, sticky=tk.W, pady=5)

        entry_recibido = tk.Entry(frame_efectivo, font=("Helvetica", 11), width=15)
        entry_recibido.grid(row=0, column=1, sticky=tk.W, padx=5)
        entry_recibido.bind("<KeyRelease>", lambda event: self.calcular_cambio(entry_recibido, lbl_cambio))

        tk.Label(
            frame_efectivo,
            text="Cambio:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).grid(row=1, column=0, sticky=tk.W, pady=5)

        lbl_cambio = tk.Label(
            frame_efectivo,
            text="$0.00",
            font=("Helvetica", 11, "bold"),
            bg="#f5f5f5",
            fg="#d32f2f"
        )
        lbl_cambio.grid(row=1, column=1, sticky=tk.W, padx=5)

        # Espacio antes de botones
        tk.Frame(frame_principal, height=20, bg="#f5f5f5").pack(fill=tk.X)

        # Frame para botones (FIJO en la parte de abajo)
        frame_botones = tk.Frame(ventana_pago, bg="#f5f5f5")
        frame_botones.pack(side=tk.BOTTOM, pady=20)

        btn_procesar = tk.Button(
            frame_botones,
            text="Procesar Pago",
            font=("Helvetica", 12, "bold"),
            bg="#00796b",
            fg="white",
            width=15,
            cursor="hand2",
            command=lambda: self.finalizar_pago(ventana_pago, metodo_pago_var, entry_recibido)
        )
        btn_procesar.pack(side=tk.LEFT, padx=10)

        btn_cancelar = tk.Button(
            frame_botones,
            text="Cancelar",
            font=("Helvetica", 12),
            bg="#e53935",
            fg="white",
            width=15,
            cursor="hand2",
            command=ventana_pago.destroy
        )
        btn_cancelar.pack(side=tk.LEFT, padx=10)

        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

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
            cambio = recibido - self.total_venta
            if cambio >= 0:
                lbl_cambio.config(text=f"${cambio:.2f}", fg="#388e3c")
            else:
                lbl_cambio.config(text=f"${cambio:.2f}", fg="#d32f2f")
        except ValueError:
            lbl_cambio.config(text="$0.00", fg="#666666")

    def finalizar_pago(self, ventana_pago, metodo_pago_var, entry_recibido):
        """Procesa el pago final: registra ingreso por efectivo recibido y cambio."""
        metodo_pago = metodo_pago_var.get()
        cambio = 0.0
        monto_recibido = 0.0

        try:
            if metodo_pago == "Efectivo":
                try:
                    recibido = float(entry_recibido.get())
                except ValueError:
                    messagebox.showwarning(
                        "Error", 
                        "El monto en efectivo debe ser un número válido.",
                        parent=self.ventana
                    )
                    return

                if recibido < self.total_venta:
                    messagebox.showwarning(
                        "Efectivo insuficiente",
                        "El monto recibido es menor al total a pagar.",
                        parent=self.ventana
                    )
                    return

                cambio = recibido - self.total_venta
                monto_recibido = recibido

            # Llamamos con el efectivo recibido y el cambio calculado
            self.guardar_venta(metodo_pago, cambio, monto_recibido)

            ventana_pago.destroy()

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al procesar el pago:\n{e}",
                parent=self.ventana
            )
            print(f"Error en finalizar_pago: {e}")


    def guardar_venta(self, metodo_pago, cambio, monto_recibido):
        """Guarda la venta y registra movimientos de caja correctamente."""
        try:
            # 0) Conexión y timeouts
            conexion = conectar_bd()
            if not conexion:
                messagebox.showerror(
                    "Error", "No se pudo conectar a la base de datos", parent=self.ventana
                )
                return
            cursor = conexion.cursor()
            cursor.execute("SET SESSION wait_timeout = 28800")
            cursor.execute("SET SESSION interactive_timeout = 28800")

            # 1) Obtener caja abierta hoy
            hoy = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                "SELECT id_caja, responsable FROM caja WHERE fecha=%s AND hora_cierre IS NULL",
                (hoy,)
            )
            fila = cursor.fetchone()
            if not fila:
                messagebox.showerror(
                    "Error", "No hay una caja abierta para procesar la venta.", parent=self.ventana
                )
                cursor.close()
                conexion.close()
                return
            id_caja_actual, responsable_caja = fila

            # 2) Calcular puntos de fidelidad
            puntos_ganados = int(self.total_venta / 10)

            # 3) Iniciar transacción
            cursor.execute("START TRANSACTION")
            try:
                # 3.1) Insertar venta
                cursor.execute("""
                    INSERT INTO ventas
                    (id_usuario, id_cliente, total, metodo_pago, fecha, puntos_ganados)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    self.id_usuario_actual,
                    self.cliente_actual['id'],
                    self.total_venta,
                    metodo_pago,
                    datetime.now(),
                    puntos_ganados
                ))
                id_venta = cursor.lastrowid

                # 3.2) Detalle de venta y ajuste de stock
                for it in self.items_venta:
                    cursor.execute("""
                        INSERT INTO detalle_venta
                        (id_venta, tipo_item, id_item, cantidad, subtotal)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        id_venta, it['tipo'], it['id'], it['cantidad'], it['subtotal']
                    ))
                    if it['tipo'] == 'producto':
                        cursor.execute("""
                            UPDATE productos
                            SET stock = stock - %s
                            WHERE id_producto = %s
                        """, (it['cantidad'], it['id']))

                # 3.3) Actualizar puntos del cliente
                cursor.execute("""
                    UPDATE clientes
                    SET puntos = puntos + %s
                    WHERE id_cliente = %s
                """, (puntos_ganados, self.cliente_actual['id']))

                # 3.4) Movimientos en caja
                if metodo_pago == "Efectivo":
                    # Solo registrar el total de la venta como ingreso
                    cursor.execute("""
                        INSERT INTO movimientos_caja
                        (id_caja, tipo, concepto, monto, hora, id_usuario)
                        VALUES (%s, 'ingreso', %s, %s, NOW(), %s)
                    """, (
                        id_caja_actual,
                        f"Venta #{id_venta} – Efectivo",
                        self.total_venta,
                        responsable_caja
                    ))
                    cursor.execute("""
                        UPDATE caja
                        SET total_ingresos = total_ingresos + %s,
                            saldo_final    = saldo_final    + %s
                        WHERE id_caja = %s
                    """, (self.total_venta, self.total_venta, id_caja_actual))
                else:
                    # Tarjeta/Transferencia (igual que antes)
                    cursor.execute("""
                        INSERT INTO movimientos_caja
                        (id_caja, tipo, concepto, monto, hora, id_usuario)
                        VALUES (%s, 'ingreso', %s, %s, NOW(), %s)
                    """, (
                        id_caja_actual,
                        f"Venta #{id_venta} – {metodo_pago}",
                        self.total_venta,
                        responsable_caja
                    ))
                    cursor.execute("""
                        UPDATE caja
                        SET total_ingresos = total_ingresos + %s,
                            saldo_final    = saldo_final    + %s
                        WHERE id_caja = %s
                    """, (self.total_venta, self.total_venta, id_caja_actual))

                # 3.5) Registrar en pagos
                cursor.execute("""
                    INSERT INTO pagos
                    (id_venta, monto, metodo_pago, fecha_hora)
                    VALUES (%s, %s, %s, NOW())
                """, (id_venta, self.total_venta, metodo_pago))

                # 3.6) Commit
                cursor.execute("COMMIT")

                # 3.7) Obtener puntos finales del cliente
                cursor.execute(
                    "SELECT puntos FROM clientes WHERE id_cliente = %s",
                    (self.cliente_actual['id'],)
                )
                puntos_finales = cursor.fetchone()[0]

            except Exception:
                cursor.execute("ROLLBACK")
                raise
            finally:
                cursor.close()
                conexion.close()

            # 4) Generar ticket y preparar mensaje final
            ruta_ticket = self.generar_ticket_html(id_venta)
            mensajes = [
                f"✅ Venta ID {id_venta} registrada.",
                f"Cliente: {self.cliente_actual['nombre']}",
                f"Total venta: ${self.total_venta:.2f}",
                f"Método: {metodo_pago}",
                f"🎁 Puntos ganados: {puntos_ganados}",
                f"🎯 Puntos totales: {puntos_finales}"
            ]
            if metodo_pago == "Efectivo":
                mensajes.append(f"💵 Recibido: ${monto_recibido:.2f}")
                if cambio > 0:
                    mensajes.append(f"💰 Cambio: ${cambio:.2f}")

            messagebox.showinfo("Venta Registrada", "\n".join(mensajes), parent=self.ventana)

            # 5) Limpiar la interfaz y abrir el ticket
            self.limpiar_venta()
            try:
                import webbrowser
                webbrowser.open(ruta_ticket)
            except:
                pass

        except Exception as e:
            # Manejo de errores de conexión y transacción
            err = str(e).lower()
            if "lost connection" in err or "mysql server has gone away" in err:
                messagebox.showerror(
                    "Error de Conexión",
                    "Se perdió la conexión con la base de datos.",
                    parent=self.ventana
                )
            elif "lock wait timeout" in err:
                messagebox.showerror(
                    "Error de Base de Datos",
                    "La operación tardó demasiado y fue cancelada.",
                    parent=self.ventana
                )
            else:
                messagebox.showerror("Error al guardar venta", str(e), parent=self.ventana)
            import traceback; traceback.print_exc()






    def generar_ticket_html(self, id_venta):
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cliente = self.cliente_actual.get("nombre", "Cliente")
        cuerpo_items = ""

        for item in self.items_venta:
            promo_text = f" <span style='color:#1976D2;'>[{item['promo']}]</span>" if item.get('promo') else ""
            cuerpo_items += f"""
            <tr>
                <td>{item['nombre']}{promo_text}</td>
                <td class="precio">{item['cantidad']} x {item['precio_unitario']:.2f}</td>
                <td class="subtotal">${item['subtotal']:.2f}</td>
            </tr>
            """

        total_formateado = f"${self.total_venta:.2f}"
        codigo_seguimiento = datetime.now().strftime("LV%Y%m%d%H%M%S")

        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Ticket Venta {id_venta}</title>
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
            <p>RFC: XAXX010101000</p>

            <div class="separador"></div>

            <p><strong>Fecha:</strong> {fecha}</p>
            <p><strong>Cliente:</strong> {cliente}</p>

            <div class="separador"></div>

            <table>
                {cuerpo_items}
            </table>

            <div class="separador"></div>
            <p><strong>TOTAL: {total_formateado}</strong></p>

            <div class="separador"></div>

            <p>¡Gracias por su preferencia!</p>
            <p>Folio: {codigo_seguimiento}</p>
            <p>Conserve su ticket</p>

        </body>
        </html>
        """

        ruta = f"ticket_venta_{id_venta}.html"
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(html)

        return ruta


    def seleccionar_cliente(self):
        """Abre ventana para seleccionar un cliente"""
        ventana_clientes = tk.Toplevel(self.ventana)
        ventana_clientes.title("Seleccionar Cliente")
        ventana_clientes.geometry("820x550")  # más ancho para los botones
        ventana_clientes.config(bg="#f5f5f5")
        ventana_clientes.minsize(700, 550)
        ventana_clientes.resizable(True, True)

        frame_principal = tk.Frame(ventana_clientes, bg="#f5f5f5")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            frame_principal,
            text="SELECCIONAR CLIENTE",
            font=("Helvetica", 16, "bold"),
            bg="#f5f5f5",
            fg="#303f9f"
        ).pack(pady=(0, 20))

        frame_busqueda = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_busqueda.pack(fill=tk.X, pady=10)

        tk.Label(frame_busqueda, text="Buscar cliente:", font=("Helvetica", 12), bg="#f5f5f5").pack(side=tk.LEFT,
                                                                                                    padx=5)

        entry_buscar = tk.Entry(frame_busqueda, width=30, font=("Helvetica", 12))
        entry_buscar.pack(side=tk.LEFT, padx=5)

        # Tabla de clientes
        columnas = ('id', 'nombre', 'telefono', 'puntos')
        tabla_clientes = ttk.Treeview(frame_principal, columns=columnas, show='headings', height=15)
        tabla_clientes.heading('id', text='ID')
        tabla_clientes.heading('nombre', text='Nombre')
        tabla_clientes.heading('telefono', text='Teléfono')
        tabla_clientes.heading('puntos', text='Puntos')
        tabla_clientes.column('id', width=50, anchor=tk.CENTER)
        tabla_clientes.column('nombre', width=300)
        tabla_clientes.column('telefono', width=150, anchor=tk.CENTER)
        tabla_clientes.column('puntos', width=100, anchor=tk.CENTER)
        utl.aplicar_estilo_tabla(tabla_clientes)

        scrollbar = ttk.Scrollbar(frame_principal, orient=tk.VERTICAL, command=tabla_clientes.yview)
        tabla_clientes.configure(yscrollcommand=scrollbar.set)

        frame_tabla = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10)
        tabla_clientes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def buscar_clientes(texto_busqueda):
            for item in tabla_clientes.get_children():
                tabla_clientes.delete(item)

            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()
                if not texto_busqueda:
                    cursor.execute("SELECT id_cliente, nombre, telefono, puntos FROM clientes ORDER BY nombre")
                else:
                    cursor.execute("""
                        SELECT id_cliente, nombre, telefono, puntos FROM clientes 
                        WHERE nombre LIKE %s OR telefono LIKE %s
                        ORDER BY nombre
                    """, (f"%{texto_busqueda}%", f"%{texto_busqueda}%"))

                for cliente in cursor.fetchall():
                    tabla_clientes.insert('', tk.END, values=cliente)
                conexion.close()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar los clientes: {str(e)}")

        # Función para cargar clientes
        def cargar_clientes():
            # Limpiar tabla
            for item in tabla_clientes.get_children():
                tabla_clientes.delete(item)

            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()
                cursor.execute("SELECT id_cliente, nombre, telefono, puntos FROM clientes ORDER BY nombre")

                for cliente in cursor.fetchall():
                    tabla_clientes.insert('', tk.END, values=cliente)

                conexion.close()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar los clientes: {str(e)}")

        entry_buscar.bind("<Return>", lambda event: buscar_clientes(entry_buscar.get().strip()))
        tk.Button(
            frame_busqueda, text="🔍 Buscar", font=("Helvetica", 10),
            bg="#303f9f", fg="white", padx=10, cursor="hand2",
            command=lambda: buscar_clientes(entry_buscar.get().strip())
        ).pack(side=tk.LEFT, padx=5)

        frame_botones = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_botones.pack(fill=tk.X, pady=10)

        btn_seleccionar = tk.Button(
            frame_botones, text="Seleccionar", font=("Helvetica", 11),
            bg="#303f9f", fg="white", width=12, cursor="hand2",
            command=lambda: self.seleccionar_cliente_accion(tabla_clientes, ventana_clientes)
        )
        btn_seleccionar.pack(side=tk.LEFT, padx=5)

        # BOTÓN MODIFICADO: Abre el módulo completo de gestión de clientes
        btn_gestion = tk.Button(
            frame_botones,
            text="Gestión de Clientes",
            font=("Helvetica", 11),
            bg="#4CAF50",  # Color verde para diferenciarlo
            fg="white",
            width=15,  # Aumentamos el ancho para que quepa el texto
            cursor="hand2",
            command=lambda: self.abrir_gestion_clientes(ventana_clientes, cargar_clientes)
        )
        btn_gestion.pack(side=tk.LEFT, padx=5)

        btn_cancelar = tk.Button(
            frame_botones, text="Cancelar", font=("Helvetica", 11),
            bg="#e53935", fg="white", width=10, cursor="hand2",
            command=ventana_clientes.destroy
        )
        btn_cancelar.pack(side=tk.RIGHT, padx=5)

                # Cargar clientes al iniciar
        cargar_clientes()

        # Forzar ajuste al contenido
        ventana_clientes.update_idletasks()  # Asegura que todo esté renderizado
        ventana_clientes.geometry("")        # Ajusta el tamaño al contenido visible

        # Centrar la ventana (opcional si tienes la función)
        utl.centrar_ventana(ventana_clientes, ventana_clientes.winfo_width(), ventana_clientes.winfo_height())

        # Hacer modal sin bloquear
        ventana_clientes.transient(self.ventana)
        ventana_clientes.grab_set()
        
        ventana_clientes.update_idletasks()
        ancho = ventana_clientes.winfo_reqwidth() + 50  # margen extra para scrollbar y botones
        alto = ventana_clientes.winfo_reqheight() + 50
        ventana_clientes.geometry(f"{ancho}x{alto}")

    def abrir_gestion_clientes(self, ventana_padre, callback_actualizar):
        """Abre el módulo completo de gestión de clientes"""
        try:
            # Importar el módulo de gestión de clientes
            from clientes import GestionClientes

            # Crear una instancia del módulo de clientes
            # Le pasamos ventana_padre para que sea modal
            gestion_clientes = GestionClientes(ventana_padre)

            # Función para actualizar la tabla cuando se cierre la ventana de clientes
            def on_close():
                # Recargar la tabla de clientes en la ventana de selección
                callback_actualizar()

            # Conectar el evento de cierre (si el módulo de clientes lo soporta)
            # Nota: Esto dependería de cómo esté implementado el módulo de clientes

            # También podemos usar un timer para actualizar periódicamente
            def verificar_y_actualizar():
                try:
                    # Verificar si la ventana de gestión de clientes sigue abierta
                    # Si se cerró, actualizar la tabla
                    ventana_padre.after(1000, verificar_y_actualizar)  # Verificar cada segundo
                    callback_actualizar()
                except:
                    pass

            # Iniciar la verificación
            ventana_padre.after(500, verificar_y_actualizar)

        except ImportError:
            messagebox.showerror(
                "Error de importación",
                "No se pudo importar el módulo de gestión de clientes.\n"
                "Verifique que el archivo 'clientes.py' existe."
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo abrir el módulo de gestión de clientes: {str(e)}"
            )

    # Función para seleccionar cliente (mantiene igual)
    def seleccionar_cliente_accion(self, tabla, ventana_clientes):
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

        self.frame_principal.update_idletasks()
        print("Cliente seleccionado:", self.cliente_actual)
        ventana_clientes.destroy()
        print("Ventana cliente cerrada")
