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


class Ventas:
    def __init__(self, ventana_padre=None):
        # Crear ventana
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Módulo de Ventas - Lavandería")
        self.ventana.geometry("1000x700")
        self.ventana.config(bg="#e0f7fa")
        self.ventana.resizable(False, False)

        if ventana_padre:
            utl.centrar_ventana(self.ventana, 1000, 700)
            self.ventana.transient(ventana_padre)
            self.ventana.grab_set()

        # Variables
        self.items_venta = []
        self.cliente_actual = None
        self.total_venta = 0.0
        self.id_usuario_actual = 1

        # Construir la interfaz
        self.construir_interfaz()

        if not ventana_padre:
            self.ventana.mainloop()

    def construir_interfaz(self):
        # Frame principal
        self.frame_principal = tk.Frame(self.ventana, bg="#e0f7fa")
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        titulo = tk.Label(
            self.frame_principal,
            text="Registro de Ventas",
            font=("Helvetica", 20, "bold"),
            bg="#e0f7fa",
            fg="#00796b"
        )
        titulo.pack(pady=10)

        # Frame de cliente
        frame_cliente = tk.Frame(self.frame_principal, bg="#e0f7fa")
        frame_cliente.pack(fill=tk.X, pady=10)

        lbl_cliente = tk.Label(frame_cliente, text="Cliente:", font=("Helvetica", 12), bg="#e0f7fa")
        lbl_cliente.pack(side=tk.LEFT, padx=5)

        self.lbl_cliente_seleccionado = tk.Label(frame_cliente, text="No seleccionado", font=("Helvetica", 12), bg="#e0f7fa", fg="#777777")
        self.lbl_cliente_seleccionado.pack(side=tk.LEFT, padx=5)

        btn_seleccionar_cliente = tk.Button(
            frame_cliente, text="Seleccionar Cliente", font=("Helvetica", 10),
            bg="#00796b", fg="white", command=self.seleccionar_cliente
        )
        btn_seleccionar_cliente.pack(side=tk.LEFT, padx=10)

        # Notebook
        self.notebook = ttk.Notebook(self.frame_principal)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        tab_productos = tk.Frame(self.notebook, bg="#e0f7fa")
        tab_servicios = tk.Frame(self.notebook, bg="#e0f7fa")

        self.notebook.add(tab_productos, text="Productos")
        self.notebook.add(tab_servicios, text="Servicios")

        # Configurar pestañas
        self.configurar_tab_productos(tab_productos)
        self.configurar_tab_servicios(tab_servicios)

        # Tabla de items seleccionados
        self.tabla_items = ttk.Treeview(self.frame_principal, columns=('tipo', 'nombre', 'cantidad', 'precio_unitario', 'subtotal'), show='headings', height=7)
        for col in ('tipo', 'nombre', 'cantidad', 'precio_unitario', 'subtotal'):
            self.tabla_items.heading(col, text=col.capitalize())
            self.tabla_items.column(col, width=100, anchor=tk.CENTER)
        self.tabla_items.pack(fill=tk.BOTH, expand=True)

        # Botones de control
        frame_control = tk.Frame(self.frame_principal, bg="#e0f7fa")
        frame_control.pack(fill=tk.X, pady=5)

        tk.Button(frame_control, text="Quitar Item", font=("Helvetica", 10), bg="#e57373", fg="white", command=self.quitar_item).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_control, text="Limpiar Todo", font=("Helvetica", 10), bg="#c62828", fg="white", command=self.limpiar_venta).pack(side=tk.LEFT, padx=5)

        # Total y botón de procesar
        frame_total = tk.Frame(self.frame_principal, bg="#e0f7fa")
        frame_total.pack(fill=tk.X, pady=10)

        lbl_total = tk.Label(frame_total, text="TOTAL:", font=("Helvetica", 14, "bold"), bg="#e0f7fa")
        lbl_total.pack(side=tk.LEFT, padx=5)

        self.lbl_total = tk.Label(frame_total, text="$0.00", font=("Helvetica", 14, "bold"), bg="#e0f7fa", fg="#00796b")
        self.lbl_total.pack(side=tk.LEFT, padx=5)

        tk.Button(frame_total, text="Procesar Pago", font=("Helvetica", 12, "bold"), bg="#00796b", fg="white", command=self.procesar_pago).pack(side=tk.RIGHT, padx=10)

        tk.Button(self.frame_principal, text="Volver", font=("Helvetica", 12), bg="#c62828", fg="white", command=self.ventana.destroy).pack(pady=10)

        # Cargar datos
        self.cargar_productos()
        self.cargar_servicios()


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
        columnas = ('id', 'nombre', 'precio', 'stock')
        self.tabla_productos = ttk.Treeview(tab, columns=columnas, show='headings', height=7)
        for col in columnas:
            self.tabla_productos.heading(col, text=col.capitalize())
            self.tabla_productos.column(col, width=100, anchor=tk.CENTER)
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
        columnas = ('id', 'nombre', 'descripcion', 'precio', 'tiempo')
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
        
    def cargar_productos(self):
        for item in self.tabla_productos.get_children():
            self.tabla_productos.delete(item)

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("SELECT id_producto, nombre, precio, stock FROM productos WHERE stock > 0 ORDER BY nombre")

            for producto in cursor.fetchall():
                precio_formateado = f"${float(producto[2]):.2f}"
                valores = (producto[0], producto[1], precio_formateado, producto[3])
                self.tabla_productos.insert('', tk.END, values=valores)

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

            consulta = """
            SELECT id_producto, nombre, precio, stock 
            FROM productos 
            WHERE stock > 0 AND (nombre LIKE %s OR id_producto = %s)
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
                self.tabla_productos.insert('', tk.END, values=valores)

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

        subtotal = precio_producto * cantidad

        item = {
            'tipo': 'producto',
            'id': id_producto,
            'nombre': nombre_producto,
            'cantidad': cantidad,
            'precio_unitario': precio_producto,
            'subtotal': subtotal
        }

        existe = False
        for i, it in enumerate(self.items_venta):
            if it['tipo'] == 'producto' and it['id'] == id_producto:
                nueva_cantidad = it['cantidad'] + cantidad
                if nueva_cantidad > stock_disponible:
                    messagebox.showwarning("Stock insuficiente", f"No se puede agregar {cantidad} más. Stock disponible: {stock_disponible}")
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
                       CONCAT(tiempo_estimado, ' min') as tiempo 
                FROM servicios 
                WHERE activo = 1 
                ORDER BY nombre
            """)

            for servicio in cursor.fetchall():
                precio_formateado = f"${float(servicio[3]):.2f}"
                valores = (servicio[0], servicio[1], servicio[2], precio_formateado, servicio[4])
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
            'subtotal': subtotal
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