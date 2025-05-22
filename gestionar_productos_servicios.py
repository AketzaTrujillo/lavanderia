"""
Módulo de Gestión de Productos y Servicios para el Sistema de Lavandería
Versión mejorada que permite gestionar tanto productos como servicios
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import utileria as utl

# Asegurar que podamos importar módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Importar módulo de conexión
from conexion import conectar_bd


class GestionProductosServicios:
    """Clase para gestionar productos y servicios del sistema"""

    def __init__(self, ventana_padre=None):
        # Si hay una ventana padre, crear Toplevel en lugar de Tk
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Gestión de Productos y Servicios - Lavandería")
        self.ventana.geometry("1000x700")
        self.ventana.config(bg="#f5f5f5")
        self.ventana.resizable(True, True)

        if ventana_padre:
            # Centrar la ventana si existe una ventana padre
            utl.centrar_ventana(self.ventana, 1000, 700)
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

    def construir_interfaz(self):
        """Construye la interfaz gráfica del módulo"""
        # Frame principal con padding
        self.frame_principal = tk.Frame(self.ventana, bg="#f5f5f5", padx=20, pady=20)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)

        # Título con estilo
        titulo_frame = tk.Frame(self.frame_principal, bg="#f5f5f5")
        titulo_frame.pack(fill=tk.X, pady=(0, 20))

        titulo = tk.Label(
            titulo_frame,
            text="GESTIÓN DE PRODUCTOS Y SERVICIOS",
            font=("Helvetica", 18, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        )
        titulo.pack()

        # Separador
        separador = ttk.Separator(self.frame_principal, orient="horizontal")
        separador.pack(fill=tk.X, pady=(0, 20))

        # Crear notebook para pestañas
        self.notebook = ttk.Notebook(self.frame_principal)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Crear pestañas
        self.tab_productos = tk.Frame(self.notebook, bg="#f5f5f5")
        self.tab_servicios = tk.Frame(self.notebook, bg="#f5f5f5")

        self.notebook.add(self.tab_productos, text="🛍️ PRODUCTOS")
        self.notebook.add(self.tab_servicios, text="🧺 SERVICIOS")

        # Configurar cada pestaña
        self.configurar_tab_productos()
        self.configurar_tab_servicios()

        # Botón para volver (en el frame principal)
        frame_volver = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_volver.pack(fill=tk.X, pady=(10, 0))

        btn_volver = tk.Button(
            frame_volver,
            text="↩ Volver",
            font=("Helvetica", 12),
            bg="#e53935",
            fg="white",
            padx=20,
            cursor="hand2",
            command=self.ventana.destroy
        )
        btn_volver.pack(side=tk.RIGHT)

        # Efecto hover
        btn_volver.bind("<Enter>", lambda e: btn_volver.config(bg="#c62828"))
        btn_volver.bind("<Leave>", lambda e: btn_volver.config(bg="#e53935"))

    def configurar_tab_productos(self):
        """Configura la pestaña de productos"""
        # Frame para botones de acción
        frame_botones = tk.Frame(self.tab_productos, bg="#f5f5f5")
        frame_botones.pack(pady=10)

        # Botones de acción para productos
        botones_productos = [
            ("Nuevo Producto", self.nuevo_producto, "➕"),
            ("Editar Producto", self.editar_producto, "✏️"),
            ("Eliminar Producto", self.eliminar_producto, "🗑️"),
            ("Actualizar Stock", self.actualizar_stock, "🔄")
        ]

        for texto, comando, icono in botones_productos:
            b = tk.Button(
                frame_botones,
                text=f"{icono} {texto}",
                font=("Helvetica", 11),
                bg="#3a7ff6",
                fg="white",
                width=16,
                height=2,
                cursor="hand2",
                command=comando
            )
            b.pack(side=tk.LEFT, padx=5)

            # Efecto hover
            b.bind("<Enter>", lambda e, b=b: b.config(bg="#1a5fce"))
            b.bind("<Leave>", lambda e, b=b: b.config(bg="#3a7ff6"))

        # Frame para el buscador de productos
        frame_busqueda = tk.Frame(self.tab_productos, bg="#f5f5f5")
        frame_busqueda.pack(fill=tk.X, pady=15)

        lbl_buscar = tk.Label(
            frame_busqueda,
            text="Buscar producto:",
            font=("Helvetica", 12),
            bg="#f5f5f5"
        )
        lbl_buscar.pack(side=tk.LEFT, padx=5)

        self.entry_buscar_producto = tk.Entry(frame_busqueda, width=30, font=("Helvetica", 12))
        self.entry_buscar_producto.pack(side=tk.LEFT, padx=5)
        self.entry_buscar_producto.bind("<Return>", lambda event: self.buscar_productos())

        btn_buscar = tk.Button(
            frame_busqueda,
            text="🔍 Buscar",
            font=("Helvetica", 10),
            bg="#3a7ff6",
            fg="white",
            padx=10,
            cursor="hand2",
            command=self.buscar_productos
        )
        btn_buscar.pack(side=tk.LEFT, padx=5)

        btn_buscar.bind("<Enter>", lambda e: btn_buscar.config(bg="#1a5fce"))
        btn_buscar.bind("<Leave>", lambda e: btn_buscar.config(bg="#3a7ff6"))

        # Tabla de productos
        frame_tabla_productos = tk.Frame(self.tab_productos, bg="#f5f5f5")
        frame_tabla_productos.pack(fill=tk.BOTH, expand=True, pady=10)

        columnas_productos = ('id', 'nombre', 'precio', 'stock')
        self.tabla_productos = ttk.Treeview(frame_tabla_productos, columns=columnas_productos, show='headings', height=12)

        utl.aplicar_estilo_tabla(self.tabla_productos)

        self.tabla_productos.heading('id', text='ID')
        self.tabla_productos.heading('nombre', text='Nombre del Producto')
        self.tabla_productos.heading('precio', text='Precio ($)')
        self.tabla_productos.heading('stock', text='Stock')

        self.tabla_productos.column('id', width=50, anchor=tk.CENTER)
        self.tabla_productos.column('nombre', width=400)
        self.tabla_productos.column('precio', width=120, anchor=tk.CENTER)
        self.tabla_productos.column('stock', width=100, anchor=tk.CENTER)

        scrollbar_productos = ttk.Scrollbar(frame_tabla_productos, orient=tk.VERTICAL, command=self.tabla_productos.yview)
        self.tabla_productos.configure(yscrollcommand=scrollbar_productos.set)

        self.tabla_productos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_productos.pack(side=tk.RIGHT, fill=tk.Y)

        # Refrescar productos
        btn_refrescar_productos = tk.Button(
            self.tab_productos,
            text="🔄 Refrescar Productos",
            font=("Helvetica", 10),
            bg="#4CAF50",
            fg="white",
            padx=10,
            cursor="hand2",
            command=self.cargar_productos
        )
        btn_refrescar_productos.pack(pady=5)

        # Cargar productos iniciales
        self.cargar_productos()

    def configurar_tab_servicios(self):
        """Configura la pestaña de servicios"""
        # Frame para botones de acción
        frame_botones = tk.Frame(self.tab_servicios, bg="#f5f5f5")
        frame_botones.pack(pady=10)

        # Botones de acción para servicios
        botones_servicios = [
            ("Nuevo Servicio", self.nuevo_servicio, "➕"),
            ("Editar Servicio", self.editar_servicio, "✏️"),
            ("Eliminar Servicio", self.eliminar_servicio, "🗑️"),
            ("Activar/Desactivar", self.toggle_servicio, "🔄")
        ]

        for texto, comando, icono in botones_servicios:
            b = tk.Button(
                frame_botones,
                text=f"{icono} {texto}",
                font=("Helvetica", 11),
                bg="#FF9800",
                fg="white",
                width=16,
                height=2,
                cursor="hand2",
                command=comando
            )
            b.pack(side=tk.LEFT, padx=5)

            # Efecto hover
            b.bind("<Enter>", lambda e, b=b: b.config(bg="#F57C00"))
            b.bind("<Leave>", lambda e, b=b: b.config(bg="#FF9800"))

        # Frame para el buscador de servicios
        frame_busqueda = tk.Frame(self.tab_servicios, bg="#f5f5f5")
        frame_busqueda.pack(fill=tk.X, pady=15)

        lbl_buscar = tk.Label(
            frame_busqueda,
            text="Buscar servicio:",
            font=("Helvetica", 12),
            bg="#f5f5f5"
        )
        lbl_buscar.pack(side=tk.LEFT, padx=5)

        self.entry_buscar_servicio = tk.Entry(frame_busqueda, width=30, font=("Helvetica", 12))
        self.entry_buscar_servicio.pack(side=tk.LEFT, padx=5)
        self.entry_buscar_servicio.bind("<Return>", lambda event: self.buscar_servicios())

        btn_buscar = tk.Button(
            frame_busqueda,
            text="🔍 Buscar",
            font=("Helvetica", 10),
            bg="#FF9800",
            fg="white",
            padx=10,
            cursor="hand2",
            command=self.buscar_servicios
        )
        btn_buscar.pack(side=tk.LEFT, padx=5)

        btn_buscar.bind("<Enter>", lambda e: btn_buscar.config(bg="#F57C00"))
        btn_buscar.bind("<Leave>", lambda e: btn_buscar.config(bg="#FF9800"))

        # Tabla de servicios
        frame_tabla_servicios = tk.Frame(self.tab_servicios, bg="#f5f5f5")
        frame_tabla_servicios.pack(fill=tk.BOTH, expand=True, pady=10)

        columnas_servicios = ('id', 'nombre', 'descripcion', 'precio', 'tiempo', 'activo')
        self.tabla_servicios = ttk.Treeview(frame_tabla_servicios, columns=columnas_servicios, show='headings', height=12)

        utl.aplicar_estilo_tabla(self.tabla_servicios)

        self.tabla_servicios.heading('id', text='ID')
        self.tabla_servicios.heading('nombre', text='Nombre del Servicio')
        self.tabla_servicios.heading('descripcion', text='Descripción')
        self.tabla_servicios.heading('precio', text='Precio ($)')
        self.tabla_servicios.heading('tiempo', text='Tiempo (min)')
        self.tabla_servicios.heading('activo', text='Estado')

        self.tabla_servicios.column('id', width=50, anchor=tk.CENTER)
        self.tabla_servicios.column('nombre', width=200)
        self.tabla_servicios.column('descripcion', width=250)
        self.tabla_servicios.column('precio', width=100, anchor=tk.CENTER)
        self.tabla_servicios.column('tiempo', width=100, anchor=tk.CENTER)
        self.tabla_servicios.column('activo', width=80, anchor=tk.CENTER)

        scrollbar_servicios = ttk.Scrollbar(frame_tabla_servicios, orient=tk.VERTICAL, command=self.tabla_servicios.yview)
        self.tabla_servicios.configure(yscrollcommand=scrollbar_servicios.set)

        self.tabla_servicios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_servicios.pack(side=tk.RIGHT, fill=tk.Y)

        # Refrescar servicios
        btn_refrescar_servicios = tk.Button(
            self.tab_servicios,
            text="🔄 Refrescar Servicios",
            font=("Helvetica", 10),
            bg="#4CAF50",
            fg="white",
            padx=10,
            cursor="hand2",
            command=self.cargar_servicios
        )
        btn_refrescar_servicios.pack(pady=5)

        # Cargar servicios iniciales
        self.cargar_servicios()

    # ===============================
    # MÉTODOS PARA PRODUCTOS
    # ===============================

    def cargar_productos(self):
        """Carga todos los productos en la tabla"""
        for item in self.tabla_productos.get_children():
            self.tabla_productos.delete(item)

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("SELECT id_producto, nombre, precio, stock FROM productos ORDER BY nombre")

            for producto in cursor.fetchall():
                precio_formateado = f"${float(producto[2]):.2f}"
                self.tabla_productos.insert('', tk.END, values=(producto[0], producto[1], precio_formateado, producto[3]))

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los productos: {str(e)}")

    def buscar_productos(self):
        """Busca productos según el texto ingresado"""
        texto_busqueda = self.entry_buscar_producto.get().strip()

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
                self.tabla_productos.insert('', tk.END, values=(producto[0], producto[1], precio_formateado, producto[3]))

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar productos: {str(e)}")

    def nuevo_producto(self):
        """Abre ventana para crear un nuevo producto"""
        self.ventana_producto_form(modo="nuevo")

    def editar_producto(self):
        """Abre ventana para editar un producto seleccionado"""
        seleccion = self.tabla_productos.selection()
        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un producto para editar")
            return

        valores = self.tabla_productos.item(seleccion[0], 'values')
        datos_producto = {
            'id': valores[0],
            'nombre': valores[1],
            'precio': valores[2].replace('$', '').replace(',', ''),
            'stock': valores[3]
        }
        self.ventana_producto_form(modo="editar", datos=datos_producto)

    def eliminar_producto(self):
        """Elimina un producto seleccionado"""
        seleccion = self.tabla_productos.selection()
        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un producto para eliminar")
            return

        valores = self.tabla_productos.item(seleccion[0], 'values')
        id_producto = valores[0]
        nombre_producto = valores[1]

        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de eliminar el producto '{nombre_producto}'?"
        )

        if not confirmacion:
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Verificar si el producto está en uso
            cursor.execute("""
                SELECT COUNT(*) FROM detalle_venta WHERE tipo_item = 'producto' AND id_item = %s
                UNION ALL
                SELECT COUNT(*) FROM detalle_pedido WHERE tipo_item = 'producto' AND id_item = %s
            """, (id_producto, id_producto))

            resultados = cursor.fetchall()
            if resultados[0][0] > 0 or (len(resultados) > 1 and resultados[1][0] > 0):
                messagebox.showwarning(
                    "No se puede eliminar",
                    "Este producto está asociado a ventas o pedidos y no puede eliminarse."
                )
                return

            cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
            conexion.commit()
            conexion.close()

            messagebox.showinfo("Éxito", "Producto eliminado correctamente")
            self.cargar_productos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el producto: {str(e)}")

    def actualizar_stock(self):
        """Abre ventana para actualizar el stock de un producto"""
        seleccion = self.tabla_productos.selection()
        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un producto para actualizar stock")
            return

        valores = self.tabla_productos.item(seleccion[0], 'values')
        self.ventana_stock_form(valores[0], valores[1], int(valores[3]))

    # ===============================
    # MÉTODOS PARA SERVICIOS
    # ===============================

    def cargar_servicios(self):
        """Carga todos los servicios en la tabla"""
        for item in self.tabla_servicios.get_children():
            self.tabla_servicios.delete(item)

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_servicio, nombre, descripcion, precio, tiempo_estimado, activo 
                FROM servicios ORDER BY nombre
            """)

            for servicio in cursor.fetchall():
                precio_formateado = f"${float(servicio[3]):.2f}"
                estado = "Activo" if servicio[5] else "Inactivo"

                # Insertar con color diferente según el estado
                item_id = self.tabla_servicios.insert('', tk.END, values=(
                    servicio[0], servicio[1], servicio[2], precio_formateado, servicio[4], estado
                ))

                # Aplicar color para servicios inactivos
                if not servicio[5]:
                    self.tabla_servicios.set(item_id, 'activo', 'Inactivo')

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los servicios: {str(e)}")

    def buscar_servicios(self):
        """Busca servicios según el texto ingresado"""
        texto_busqueda = self.entry_buscar_servicio.get().strip()

        for item in self.tabla_servicios.get_children():
            self.tabla_servicios.delete(item)

        if not texto_busqueda:
            self.cargar_servicios()
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            consulta = """
            SELECT id_servicio, nombre, descripcion, precio, tiempo_estimado, activo 
            FROM servicios 
            WHERE nombre LIKE %s OR descripcion LIKE %s OR id_servicio = %s
            ORDER BY nombre
            """

            try:
                id_busqueda = int(texto_busqueda)
            except ValueError:
                id_busqueda = -1

            cursor.execute(consulta, (f"%{texto_busqueda}%", f"%{texto_busqueda}%", id_busqueda))

            for servicio in cursor.fetchall():
                precio_formateado = f"${float(servicio[3]):.2f}"
                estado = "Activo" if servicio[5] else "Inactivo"
                self.tabla_servicios.insert('', tk.END, values=(
                    servicio[0], servicio[1], servicio[2], precio_formateado, servicio[4], estado
                ))

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar servicios: {str(e)}")

    def nuevo_servicio(self):
        """Abre ventana para crear un nuevo servicio"""
        self.ventana_servicio_form(modo="nuevo")

    def editar_servicio(self):
        """Abre ventana para editar un servicio seleccionado"""
        seleccion = self.tabla_servicios.selection()
        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un servicio para editar")
            return

        valores = self.tabla_servicios.item(seleccion[0], 'values')
        datos_servicio = {
            'id': valores[0],
            'nombre': valores[1],
            'descripcion': valores[2],
            'precio': valores[3].replace('$', '').replace(',', ''),
            'tiempo': valores[4],
            'activo': valores[5] == "Activo"
        }
        self.ventana_servicio_form(modo="editar", datos=datos_servicio)

    def eliminar_servicio(self):
        """Elimina un servicio seleccionado"""
        seleccion = self.tabla_servicios.selection()
        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un servicio para eliminar")
            return

        valores = self.tabla_servicios.item(seleccion[0], 'values')
        id_servicio = valores[0]
        nombre_servicio = valores[1]

        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de eliminar el servicio '{nombre_servicio}'?"
        )

        if not confirmacion:
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Verificar si el servicio está en uso
            cursor.execute("""
                SELECT COUNT(*) FROM detalle_venta WHERE tipo_item = 'servicio' AND id_item = %s
                UNION ALL
                SELECT COUNT(*) FROM detalle_pedido WHERE tipo_item = 'servicio' AND id_item = %s
            """, (id_servicio, id_servicio))

            resultados = cursor.fetchall()
            if resultados[0][0] > 0 or (len(resultados) > 1 and resultados[1][0] > 0):
                messagebox.showwarning(
                    "No se puede eliminar",
                    "Este servicio está asociado a ventas o pedidos y no puede eliminarse."
                )
                return

            cursor.execute("DELETE FROM servicios WHERE id_servicio = %s", (id_servicio,))
            conexion.commit()
            conexion.close()

            messagebox.showinfo("Éxito", "Servicio eliminado correctamente")
            self.cargar_servicios()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el servicio: {str(e)}")

    def toggle_servicio(self):
        """Activa o desactiva un servicio"""
        seleccion = self.tabla_servicios.selection()
        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un servicio")
            return

        valores = self.tabla_servicios.item(seleccion[0], 'values')
        id_servicio = valores[0]
        nombre_servicio = valores[1]
        estado_actual = valores[5] == "Activo"

        nuevo_estado = not estado_actual
        accion = "activar" if nuevo_estado else "desactivar"

        confirmacion = messagebox.askyesno(
            f"Confirmar {accion}",
            f"¿Estás seguro de {accion} el servicio '{nombre_servicio}'?"
        )

        if not confirmacion:
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("UPDATE servicios SET activo = %s WHERE id_servicio = %s", (nuevo_estado, id_servicio))
            conexion.commit()
            conexion.close()

            mensaje = f"Servicio {'activado' if nuevo_estado else 'desactivado'} correctamente"
            messagebox.showinfo("Éxito", mensaje)
            self.cargar_servicios()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar el estado del servicio: {str(e)}")

    # ===============================
    # FORMULARIOS
    # ===============================

    def ventana_producto_form(self, modo="nuevo", datos=None):
        """Ventana de formulario para productos"""
        ventana = tk.Toplevel(self.ventana)
        titulo = "Nuevo Producto" if modo == "nuevo" else "Editar Producto"
        ventana.title(titulo)
        ventana.geometry("450x350")
        ventana.config(bg="#f5f5f5")
        ventana.grab_set()
        utl.centrar_ventana(ventana, 450, 350)

        # Título
        tk.Label(ventana, text=titulo.upper(), font=("Helvetica", 14, "bold"),
                bg="#f5f5f5", fg="#3a7ff6").pack(pady=20)

        # Frame del formulario
        frame_form = tk.Frame(ventana, bg="#f5f5f5")
        frame_form.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Campos
        tk.Label(frame_form, text="Nombre:", font=("Helvetica", 12), bg="#f5f5f5").grid(row=0, column=0, sticky=tk.W, pady=10)
        entry_nombre = tk.Entry(frame_form, font=("Helvetica", 12), width=25)
        entry_nombre.grid(row=0, column=1, pady=10, padx=10)

        tk.Label(frame_form, text="Precio ($):", font=("Helvetica", 12), bg="#f5f5f5").grid(row=1, column=0, sticky=tk.W, pady=10)
        entry_precio = tk.Entry(frame_form, font=("Helvetica", 12), width=25)
        entry_precio.grid(row=1, column=1, pady=10, padx=10)

        tk.Label(frame_form, text="Stock:", font=("Helvetica", 12), bg="#f5f5f5").grid(row=2, column=0, sticky=tk.W, pady=10)
        entry_stock = tk.Entry(frame_form, font=("Helvetica", 12), width=25)
        entry_stock.grid(row=2, column=1, pady=10, padx=10)

        # Si es edición, llenar los campos
        if modo == "editar" and datos:
            entry_nombre.insert(0, datos['nombre'])
            entry_precio.insert(0, datos['precio'])
            entry_stock.insert(0, datos['stock'])

        # Botones
        frame_botones = tk.Frame(ventana, bg="#f5f5f5")
        frame_botones.pack(pady=20)

        def guardar():
            try:
                nombre = entry_nombre.get().strip()
                precio = float(entry_precio.get().strip())
                stock = int(entry_stock.get().strip())

                if not nombre:
                    messagebox.showwarning("Error", "El nombre es obligatorio")
                    return
                if precio <= 0:
                    messagebox.showwarning("Error", "El precio debe ser mayor que cero")
                    return
                if stock < 0:
                    messagebox.showwarning("Error", "El stock no puede ser negativo")
                    return

                conexion = conectar_bd()
                cursor = conexion.cursor()

                if modo == "nuevo":
                    # Verificar nombre duplicado
                    cursor.execute("SELECT COUNT(*) FROM productos WHERE nombre = %s", (nombre,))
                    if cursor.fetchone()[0] > 0:
                        messagebox.showwarning("Error", "Ya existe un producto con ese nombre")
                        return

                    cursor.execute("INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s)",
                                 (nombre, precio, stock))
                    mensaje = "Producto creado correctamente"
                else:
                    # Verificar nombre duplicado (excluyendo el actual)
                    cursor.execute("SELECT COUNT(*) FROM productos WHERE nombre = %s AND id_producto != %s",
                                 (nombre, datos['id']))
                    if cursor.fetchone()[0] > 0:
                        messagebox.showwarning("Error", "Ya existe otro producto con ese nombre")
                        return

                    cursor.execute("UPDATE productos SET nombre = %s, precio = %s, stock = %s WHERE id_producto = %s",
                                 (nombre, precio, stock, datos['id']))
                    mensaje = "Producto actualizado correctamente"

                conexion.commit()
                conexion.close()
                messagebox.showinfo("Éxito", mensaje)
                ventana.destroy()
                self.cargar_productos()

            except ValueError:
                messagebox.showwarning("Error", "Precio y stock deben ser números válidos")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        btn_guardar = tk.Button(frame_botones, text="💾 Guardar", font=("Helvetica", 11),
                               bg="#3a7ff6", fg="white", width=12, cursor="hand2", command=guardar)
        btn_guardar.pack(side=tk.LEFT, padx=5)

        btn_cancelar = tk.Button(frame_botones, text="❌ Cancelar", font=("Helvetica", 11),
                               bg="#e53935", fg="white", width=12, cursor="hand2", command=ventana.destroy)
        btn_cancelar.pack(side=tk.LEFT, padx=5)

    def ventana_servicio_form(self, modo="nuevo", datos=None):
        """Ventana de formulario para servicios"""
        ventana = tk.Toplevel(self.ventana)
        titulo = "Nuevo Servicio" if modo == "nuevo" else "Editar Servicio"
        ventana.title(titulo)
        ventana.geometry("500x450")
        ventana.config(bg="#f5f5f5")
        ventana.grab_set()
        utl.centrar_ventana(ventana, 500, 450)

        # Título
        tk.Label(ventana, text=titulo.upper(), font=("Helvetica", 14, "bold"),
                bg="#f5f5f5", fg="#FF9800").pack(pady=20)

        # Frame del formulario
        frame_form = tk.Frame(ventana, bg="#f5f5f5")
        frame_form.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Campos
        tk.Label(frame_form, text="Nombre:", font=("Helvetica", 12), bg="#f5f5f5").grid(row=0, column=0, sticky=tk.W, pady=10)
        entry_nombre = tk.Entry(frame_form, font=("Helvetica", 12), width=30)
        entry_nombre.grid(row=0, column=1, pady=10, padx=10)

        tk.Label(frame_form, text="Descripción:", font=("Helvetica", 12), bg="#f5f5f5").grid(row=1, column=0, sticky=tk.NW, pady=10)
        text_descripcion = tk.Text(frame_form, font=("Helvetica", 11), width=30, height=4)
        text_descripcion.grid(row=1, column=1, pady=10, padx=10)

        tk.Label(frame_form, text="Precio ($):", font=("Helvetica", 12), bg="#f5f5f5").grid(row=2, column=0, sticky=tk.W, pady=10)
        entry_precio = tk.Entry(frame_form, font=("Helvetica", 12), width=30)
        entry_precio.grid(row=2, column=1, pady=10, padx=10)

        tk.Label(frame_form, text="Tiempo (minutos):", font=("Helvetica", 12), bg="#f5f5f5").grid(row=3, column=0, sticky=tk.W, pady=10)
        entry_tiempo = tk.Entry(frame_form, font=("Helvetica", 12), width=30)
        entry_tiempo.grid(row=3, column=1, pady=10, padx=10)

        # Checkbox para activo
        var_activo = tk.BooleanVar(value=True)
        check_activo = tk.Checkbutton(frame_form, text="Servicio activo", variable=var_activo,
                                    font=("Helvetica", 12), bg="#f5f5f5")
        check_activo.grid(row=4, column=1, sticky=tk.W, pady=10, padx=10)

        # Si es edición, llenar los campos
        if modo == "editar" and datos:
            entry_nombre.insert(0, datos['nombre'])
            text_descripcion.insert(tk.END, datos['descripcion'])
            entry_precio.insert(0, datos['precio'])
            entry_tiempo.insert(0, datos['tiempo'])
            var_activo.set(datos['activo'])

        # Botones
        frame_botones = tk.Frame(ventana, bg="#f5f5f5")
        frame_botones.pack(pady=20)

        def guardar():
            try:
                nombre = entry_nombre.get().strip()
                descripcion = text_descripcion.get("1.0", tk.END).strip()
                precio = float(entry_precio.get().strip())
                tiempo = int(entry_tiempo.get().strip())
                activo = var_activo.get()

                if not nombre:
                    messagebox.showwarning("Error", "El nombre es obligatorio")
                    return
                if precio <= 0:
                    messagebox.showwarning("Error", "El precio debe ser mayor que cero")
                    return
                if tiempo <= 0:
                    messagebox.showwarning("Error", "El tiempo debe ser mayor que cero")
                    return

                conexion = conectar_bd()
                cursor = conexion.cursor()

                if modo == "nuevo":
                    # Verificar nombre duplicado
                    cursor.execute("SELECT COUNT(*) FROM servicios WHERE nombre = %s", (nombre,))
                    if cursor.fetchone()[0] > 0:
                        messagebox.showwarning("Error", "Ya existe un servicio con ese nombre")
                        return

                    cursor.execute("""
                        INSERT INTO servicios (nombre, descripcion, precio, tiempo_estimado, activo) 
                        VALUES (%s, %s, %s, %s, %s)
                    """, (nombre, descripcion, precio, tiempo, activo))
                    mensaje = "Servicio creado correctamente"
                else:
                    # Verificar nombre duplicado (excluyendo el actual)
                    cursor.execute("SELECT COUNT(*) FROM servicios WHERE nombre = %s AND id_servicio != %s",
                                 (nombre, datos['id']))
                    if cursor.fetchone()[0] > 0:
                        messagebox.showwarning("Error", "Ya existe otro servicio con ese nombre")
                        return

                    cursor.execute("""
                        UPDATE servicios 
                        SET nombre = %s, descripcion = %s, precio = %s, tiempo_estimado = %s, activo = %s 
                        WHERE id_servicio = %s
                    """, (nombre, descripcion, precio, tiempo, activo, datos['id']))
                    mensaje = "Servicio actualizado correctamente"

                conexion.commit()
                conexion.close()
                messagebox.showinfo("Éxito", mensaje)
                ventana.destroy()
                self.cargar_servicios()

            except ValueError:
                messagebox.showwarning("Error", "Precio y tiempo deben ser números válidos")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        btn_guardar = tk.Button(frame_botones, text="💾 Guardar", font=("Helvetica", 11),
                               bg="#FF9800", fg="white", width=12, cursor="hand2", command=guardar)
        btn_guardar.pack(side=tk.LEFT, padx=5)

        btn_cancelar = tk.Button(frame_botones, text="❌ Cancelar", font=("Helvetica", 11),
                               bg="#e53935", fg="white", width=12, cursor="hand2", command=ventana.destroy)
        btn_cancelar.pack(side=tk.LEFT, padx=5)

    def ventana_stock_form(self, id_producto, nombre_producto, stock_actual):
        """Ventana para actualizar stock de productos"""
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Actualizar Stock")
        ventana.geometry("400x300")
        ventana.config(bg="#f5f5f5")
        ventana.grab_set()
        utl.centrar_ventana(ventana, 400, 300)

        # Título
        tk.Label(ventana, text="ACTUALIZAR STOCK", font=("Helvetica", 14, "bold"),
                bg="#f5f5f5", fg="#3a7ff6").pack(pady=20)

        # Info del producto
        tk.Label(ventana, text=f"Producto: {nombre_producto}", font=("Helvetica", 12, "bold"),
                bg="#f5f5f5").pack(pady=5)
        tk.Label(ventana, text=f"Stock actual: {stock_actual}", font=("Helvetica", 12),
                bg="#f5f5f5").pack(pady=5)

        # Opciones
        frame_opciones = tk.Frame(ventana, bg="#f5f5f5")
        frame_opciones.pack(pady=20)

        operacion = tk.StringVar(value="entrada")
        tk.Radiobutton(frame_opciones, text="Entrada de stock", variable=operacion, value="entrada",
                      bg="#f5f5f5", font=("Helvetica", 11)).pack(anchor=tk.W)
        tk.Radiobutton(frame_opciones, text="Salida de stock", variable=operacion, value="salida",
                      bg="#f5f5f5", font=("Helvetica", 11)).pack(anchor=tk.W)

        # Cantidad
        frame_cantidad = tk.Frame(ventana, bg="#f5f5f5")
        frame_cantidad.pack(pady=10)

        tk.Label(frame_cantidad, text="Cantidad:", font=("Helvetica", 12), bg="#f5f5f5").pack(side=tk.LEFT, padx=5)
        entry_cantidad = tk.Entry(frame_cantidad, font=("Helvetica", 12), width=10)
        entry_cantidad.pack(side=tk.LEFT, padx=5)

        # Botones
        frame_botones = tk.Frame(ventana, bg="#f5f5f5")
        frame_botones.pack(pady=20)

        def aplicar_cambio():
            try:
                cantidad = int(entry_cantidad.get().strip())
                if cantidad <= 0:
                    messagebox.showwarning("Error", "La cantidad debe ser un número positivo")
                    return

                if operacion.get() == "entrada":
                    nuevo_stock = stock_actual + cantidad
                else:
                    nuevo_stock = stock_actual - cantidad
                    if nuevo_stock < 0:
                        messagebox.showwarning("Error", f"No hay suficiente stock. Stock actual: {stock_actual}")
                        return

                conexion = conectar_bd()
                cursor = conexion.cursor()
                cursor.execute("UPDATE productos SET stock = %s WHERE id_producto = %s", (nuevo_stock, id_producto))
                conexion.commit()
                conexion.close()

                accion = "agregaron" if operacion.get() == "entrada" else "retiraron"
                messagebox.showinfo("Éxito", f"Se {accion} {cantidad} unidades. Nuevo stock: {nuevo_stock}")
                ventana.destroy()
                self.cargar_productos()

            except ValueError:
                messagebox.showwarning("Error", "La cantidad debe ser un número entero")
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar stock: {str(e)}")

        btn_aplicar = tk.Button(frame_botones, text="✓ Aplicar", font=("Helvetica", 11),
                               bg="#3a7ff6", fg="white", width=10, cursor="hand2", command=aplicar_cambio)
        btn_aplicar.pack(side=tk.LEFT, padx=5)

        btn_cancelar = tk.Button(frame_botones, text="❌ Cancelar", font=("Helvetica", 11),
                               bg="#e53935", fg="white", width=10, cursor="hand2", command=ventana.destroy)
        btn_cancelar.pack(side=tk.LEFT, padx=5)


# Para probar de forma independiente
if __name__ == "__main__":
    GestionProductosServicios()