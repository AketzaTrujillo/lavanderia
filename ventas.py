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
    def __init__(self, ventana_padre=None):
        # Crear ventana
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Módulo de Ventas - Lavandería")
        self.ventana.geometry("1100x900")
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
        self.id_usuario_actual = 1

        # Construir la interfaz
        self.construir_interfaz()

        if not ventana_padre:
            self.ventana.mainloop()

    def construir_interfaz(self):
        # Frame principal
        self.frame_principal = tk.Frame(self.ventana, bg="#e0f7fa")
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        tk.Label(
            self.frame_principal,
            text="Registro de Ventas",
            font=("Helvetica", 20, "bold"),
            bg="#e0f7fa",
            fg="#00796b"
        ).pack(pady=10)

        # =================== CLIENTE ====================
        frame_cliente = tk.Frame(self.frame_principal, bg="#e0f7fa")
        frame_cliente.pack(fill=tk.X, pady=10)

        tk.Label(frame_cliente, text="Cliente:", font=("Helvetica", 12), bg="#e0f7fa").pack(side=tk.LEFT, padx=5)

        self.lbl_cliente_seleccionado = tk.Label(frame_cliente, text="No seleccionado", font=("Helvetica", 12), bg="#e0f7fa", fg="#777777")
        self.lbl_cliente_seleccionado.pack(side=tk.LEFT, padx=5)

        btn_seleccionar_cliente = tk.Button(
            frame_cliente, text="Seleccionar Cliente", font=("Helvetica", 10),
            bg="#00796b", fg="white", command=self.seleccionar_cliente
        )
        btn_seleccionar_cliente.pack(side=tk.LEFT, padx=10)

        # =================== TABS ====================
        self.notebook = ttk.Notebook(self.frame_principal)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        tab_productos = tk.Frame(self.notebook, bg="#e0f7fa")
        tab_servicios = tk.Frame(self.notebook, bg="#e0f7fa")

        self.notebook.add(tab_productos, text="Productos")
        self.notebook.add(tab_servicios, text="Servicios")

        self.configurar_tab_productos(tab_productos)
        self.configurar_tab_servicios(tab_servicios)

        # =================== TABLA ITEMS ====================
        self.tabla_items = ttk.Treeview(self.frame_principal, columns=('tipo', 'nombre', 'cantidad', 'precio_unitario', 'subtotal'), show='headings', height=7)
        for col in ('tipo', 'nombre', 'cantidad', 'precio_unitario', 'subtotal'):
            self.tabla_items.heading(col, text=col.capitalize())
            self.tabla_items.column(col, width=100, anchor=tk.CENTER)
        self.tabla_items.pack(fill=tk.BOTH, expand=True)

        # =================== BOTONES DE CONTROL ====================
        frame_botones = tk.Frame(self.frame_principal, bg="#e0f7fa")
        frame_botones.pack(fill=tk.X, pady=5)

        tk.Button(frame_botones, text="Quitar Item", font=("Helvetica", 10), bg="#e57373", fg="white", command=self.quitar_item).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_botones, text="Limpiar Todo", font=("Helvetica", 10), bg="#c62828", fg="white", command=self.limpiar_venta).pack(side=tk.LEFT, padx=5)

        # =================== TOTAL Y PROCESAR ====================
        frame_total = tk.Frame(self.frame_principal, bg="#e0f7fa")
        frame_total.pack(fill=tk.X, pady=10)

        tk.Label(frame_total, text="TOTAL:", font=("Helvetica", 14, "bold"), bg="#e0f7fa").pack(side=tk.LEFT, padx=5)

        self.lbl_total = tk.Label(frame_total, text="$0.00", font=("Helvetica", 14, "bold"), bg="#e0f7fa", fg="#00796b")
        self.lbl_total.pack(side=tk.LEFT, padx=5)

        tk.Button(frame_total, text="Procesar Pago", font=("Helvetica", 12, "bold"), bg="#00796b", fg="white", command=self.procesar_pago).pack(side=tk.RIGHT, padx=10)

        # =================== VOLVER ====================
        frame_volver = tk.Frame(self.frame_principal, bg="#e0f7fa")
        frame_volver.pack(fill=tk.X, pady=10)

        tk.Button(frame_volver, text="Volver", font=("Helvetica", 12), bg="#c62828", fg="white", command=self.ventana.destroy).pack(side=tk.RIGHT, padx=10)





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

        #Cargar servicios al iniciar 
        self.cargar_servicios()
        
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


    # Actualizar Items a comprar 

    def actualizar_tabla_items(self):
        # Limpiar tabla
        for item in self.tabla_items.get_children():
            self.tabla_items.delete(item)

        # Agregar los nuevos
        for item in self.items_venta:
            valores = (
                item['tipo'],
                item['nombre'],
                item['cantidad'],
                f"${item['precio_unitario']:.2f}",
                f"${item['subtotal']:.2f}"
            )
            self.tabla_items.insert('', tk.END, values=valores)
    
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

        metodo_pago = simpledialog.askstring("Método de pago", "Ingresa el método de pago (Efectivo, Tarjeta, Transferencia, Otro):")
        if not metodo_pago:
            messagebox.showwarning("Método de pago", "Debes indicar un método de pago.")
            return
        
        self.calcular_total()
        print("TOTAL ACTUAL:", self.total_venta)


        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Insertar en tabla ventas
            cursor.execute("""
                INSERT INTO ventas (id_usuario, id_cliente, total, metodo_pago)
                VALUES (%s, %s, %s, %s)
            """, (
                self.id_usuario_actual,
                self.cliente_actual['id'],
                self.total_venta,
                metodo_pago
            ))

            id_venta = cursor.lastrowid  # Obtener ID de venta recién creada

            # Insertar en detalle_venta
            for item in self.items_venta:
                cursor.execute("""
                    INSERT INTO detalle_venta (id_venta, tipo_item, id_item, cantidad, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    id_venta,
                    item['tipo'],
                    item['id'],
                    item['cantidad'],
                    item['subtotal']
                ))

                # Descontar del stock si es producto
                if item['tipo'] == 'producto':
                    cursor.execute("UPDATE productos SET stock = stock - %s WHERE id_producto = %s", (
                        item['cantidad'], item['id']
                    ))

            # Insertar pago en tabla pagos
            cursor.execute("""
                INSERT INTO pagos (id_venta, monto, metodo_pago)
                VALUES (%s, %s, %s)
            """, (
                id_venta,
                self.total_venta,
                metodo_pago
            ))
            
            ruta_ticket = self.generar_ticket_html(id_venta)

            conexion.commit()
            conexion.close()

            messagebox.showinfo("Venta registrada", f"La venta (ID: {id_venta}) fue registrada exitosamente.")
            self.limpiar_venta()

            
            webbrowser.open(ruta_ticket)

            

        except Exception as e:
            if conexion:
                conexion.rollback()
            messagebox.showerror("Error", f"No se pudo registrar la venta:\n{e}")


    def generar_ticket_html(self, id_venta):
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cliente = self.cliente_actual.get("nombre", "Cliente")
        cuerpo_items = ""

        for item in self.items_venta:
            cuerpo_items += f"""
            <tr>
                <td>{item['nombre']}</td>
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
        # Crear ventana para seleccionar cliente
        ventana_clientes = tk.Toplevel(self.ventana)
        ventana_clientes.title("Seleccionar Cliente")
        ventana_clientes.geometry("700x500")
        ventana_clientes.config(bg="#f5f5f5")

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

        tabla_clientes = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=15)

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
        command=lambda: seleccionar_cliente_accion(tabla_clientes, ventana_clientes)
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
        # Cargar clientes al iniciar
        cargar_clientes()


        # Función para seleccionar cliente
        def seleccionar_cliente_accion(tabla, ventana_clientes):

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

    # Hacer modal sin bloquear con wait_window
        ventana_clientes.transient(self.ventana)
        ventana_clientes.grab_set()
