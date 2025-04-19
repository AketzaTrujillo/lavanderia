"""
Módulo de Gestión de Productos para el Sistema de Lavandería
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


class GestionProductos:
    """Clase para gestionar los productos del sistema"""

    def __init__(self, ventana_padre=None):
        # Si hay una ventana padre, crear Toplevel en lugar de Tk
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Gestión de Productos - Lavandería")
        self.ventana.geometry("800x600")
        self.ventana.config(bg="#f5f5f5")
        self.ventana.resizable(False, False)

        if ventana_padre:
            # Centrar la ventana si existe una ventana padre
            utl.centrar_ventana(self.ventana, 800, 600)
            # Hacer esta ventana modal
            self.ventana.transient(ventana_padre)
            self.ventana.grab_set()

        # Establecer ícono si existe
        try:
            if os.path.exists("Img/lavadora.ico"):
                self.ventana.iconbitmap("Img/lavadora.ico")
        except Exception:
            pass  # Si no se puede cargar el ícono, continuar sin él

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
            text="GESTIÓN DE PRODUCTOS",
            font=("Helvetica", 18, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        )
        titulo.pack()

        # Separador
        separador = ttk.Separator(self.frame_principal, orient="horizontal")
        separador.pack(fill=tk.X, pady=(0, 20))

        # Frame para botones de acción
        frame_botones = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_botones.pack(pady=10)

        # Botones de acción con íconos
        botones = [
            ("Nuevo Producto", self.nuevo_producto, "➕"),
            ("Editar Producto", self.editar_producto, "✏️"),
            ("Eliminar Producto", self.eliminar_producto, "🗑️"),
            ("Actualizar Stock", self.actualizar_stock, "🔄")
        ]

        for texto, comando, icono in botones:
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

        # Frame para el buscador
        frame_busqueda = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_busqueda.pack(fill=tk.X, pady=15)

        lbl_buscar = tk.Label(
            frame_busqueda,
            text="Buscar producto:",
            font=("Helvetica", 12),
            bg="#f5f5f5"
        )
        lbl_buscar.pack(side=tk.LEFT, padx=5)

        self.entry_buscar = tk.Entry(frame_busqueda, width=30, font=("Helvetica", 12))
        self.entry_buscar.pack(side=tk.LEFT, padx=5)

        # Vincular tecla Enter al buscador
        self.entry_buscar.bind("<Return>", lambda event: self.buscar_productos())

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

        # Efecto hover
        btn_buscar.bind("<Enter>", lambda e: btn_buscar.config(bg="#1a5fce"))
        btn_buscar.bind("<Leave>", lambda e: btn_buscar.config(bg="#3a7ff6"))

        # Frame para la tabla de productos
        frame_tabla = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10)

        # Tabla de productos (TreeView)
        columnas = ('id', 'nombre', 'precio', 'stock')

        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=15)

        # Aplicar estilo a la tabla
        utl.aplicar_estilo_tabla(self.tabla)

        # Configurar encabezados de columnas
        self.tabla.heading('id', text='ID')
        self.tabla.heading('nombre', text='Nombre del Producto')
        self.tabla.heading('precio', text='Precio ($)')
        self.tabla.heading('stock', text='Stock')

        # Configurar anchos de columnas
        self.tabla.column('id', width=50, anchor=tk.CENTER)
        self.tabla.column('nombre', width=300)
        self.tabla.column('precio', width=100, anchor=tk.CENTER)
        self.tabla.column('stock', width=100, anchor=tk.CENTER)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        # Empaquetar tabla y scrollbar
        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Barra de estado y botones inferiores
        frame_estado = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_estado.pack(fill=tk.X, pady=10)

        # Botón para refrescar la tabla
        btn_refrescar = tk.Button(
            frame_estado,
            text="🔄 Refrescar",
            font=("Helvetica", 10),
            bg="#3a7ff6",
            fg="white",
            padx=10,
            cursor="hand2",
            command=self.cargar_productos
        )
        btn_refrescar.pack(side=tk.LEFT, padx=5)

        # Efecto hover
        btn_refrescar.bind("<Enter>", lambda e: btn_refrescar.config(bg="#1a5fce"))
        btn_refrescar.bind("<Leave>", lambda e: btn_refrescar.config(bg="#3a7ff6"))

        # Separador flexible para distribuir espacio
        tk.Frame(frame_estado, bg="#f5f5f5").pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Botón para volver
        btn_volver = tk.Button(
            frame_estado,
            text="↩ Volver",
            font=("Helvetica", 10),
            bg="#e53935",
            fg="white",
            padx=10,
            cursor="hand2",
            command=self.ventana.destroy
        )
        btn_volver.pack(side=tk.RIGHT, padx=5)

        # Efecto hover
        btn_volver.bind("<Enter>", lambda e: btn_volver.config(bg="#c62828"))
        btn_volver.bind("<Leave>", lambda e: btn_volver.config(bg="#e53935"))

        # Cargar productos iniciales
        self.cargar_productos()

    def cargar_productos(self):
        """Carga todos los productos en la tabla"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("SELECT id_producto, nombre, precio, stock FROM productos ORDER BY nombre")

            for producto in cursor.fetchall():
                # Formatear precio y stock
                precio_formateado = f"${float(producto[2]):.2f}"
                self.tabla.insert('', tk.END, values=(producto[0], producto[1], precio_formateado, producto[3]))

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los productos: {str(e)}")

    def buscar_productos(self):
        """Busca productos según el texto ingresado"""
        texto_busqueda = self.entry_buscar.get().strip()

        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

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
            WHERE nombre LIKE %s OR id_producto = %s
            ORDER BY nombre
            """

            # Intenta convertir el texto de búsqueda a un número para buscar por ID
            try:
                id_busqueda = int(texto_busqueda)
            except ValueError:
                id_busqueda = -1  # Valor que no existirá como ID

            cursor.execute(consulta, (f"%{texto_busqueda}%", id_busqueda))

            for producto in cursor.fetchall():
                # Formatear precio
                precio_formateado = f"${float(producto[2]):.2f}"
                self.tabla.insert('', tk.END, values=(producto[0], producto[1], precio_formateado, producto[3]))

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar productos: {str(e)}")

    def nuevo_producto(self):
        """Abre ventana para crear un nuevo producto"""
        # Crear una nueva ventana para añadir producto
        ventana_nuevo = tk.Toplevel(self.ventana)
        ventana_nuevo.title("Nuevo Producto")
        ventana_nuevo.geometry("400x320")
        ventana_nuevo.config(bg="#f5f5f5")
        ventana_nuevo.grab_set()  # Hacer modal

        # Centrar ventana
        utl.centrar_ventana(ventana_nuevo, 400, 320)

        # Establecer ícono si existe
        try:
            if os.path.exists("Img/lavadora.ico"):
                ventana_nuevo.iconbitmap("Img/lavadora.ico")
        except Exception:
            pass

        # Título
        tk.Label(
            ventana_nuevo,
            text="REGISTRAR NUEVO PRODUCTO",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        ).pack(pady=(20, 10))

        # Separador
        ttk.Separator(ventana_nuevo, orient="horizontal").pack(fill=tk.X, padx=20)

        # Frame para el formulario
        frame_form = tk.Frame(ventana_nuevo, bg="#f5f5f5")
        frame_form.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Etiquetas y campos
        campos = [
            ("Nombre:", "nombre"),
            ("Precio ($):", "precio"),
            ("Stock inicial:", "stock")
        ]

        entradas = {}

        for i, (etiqueta, campo) in enumerate(campos):
            lbl = tk.Label(frame_form, text=etiqueta, font=("Helvetica", 12), bg="#f5f5f5")
            lbl.grid(row=i, column=0, sticky=tk.W, pady=10)

            entry = tk.Entry(frame_form, font=("Helvetica", 12), width=25)
            entry.grid(row=i, column=1, sticky=tk.W + tk.E, pady=10, padx=10)

            entradas[campo] = entry

        # Botones
        frame_botones = tk.Frame(ventana_nuevo, bg="#f5f5f5")
        frame_botones.pack(pady=20)

        def guardar_producto():
            # Validar campos
            nombre = entradas["nombre"].get().strip()
            precio_texto = entradas["precio"].get().strip()
            stock_texto = entradas["stock"].get().strip()

            if not nombre:
                messagebox.showwarning("Campo incompleto", "El nombre del producto es obligatorio")
                return

            # Validar precio
            if not utl.validar_numero(precio_texto):
                messagebox.showwarning("Valor inválido", "El precio debe ser un número válido")
                return

            precio = float(precio_texto.replace(",", "."))
            if precio <= 0:
                messagebox.showwarning("Valor inválido", "El precio debe ser mayor que cero")
                return

            # Validar stock
            if stock_texto and not stock_texto.isdigit():
                messagebox.showwarning("Valor inválido", "El stock debe ser un número entero")
                return

            stock = int(stock_texto) if stock_texto else 0
            if stock < 0:
                messagebox.showwarning("Valor inválido", "El stock no puede ser negativo")
                return

            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()

                # Verificar si ya existe un producto con ese nombre
                cursor.execute("SELECT COUNT(*) FROM productos WHERE nombre = %s", (nombre,))
                if cursor.fetchone()[0] > 0:
                    messagebox.showwarning("Nombre duplicado", "Ya existe un producto con ese nombre")
                    return

                # Insertar nuevo producto
                consulta = "INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s)"
                cursor.execute(consulta, (nombre, precio, stock))

                conexion.commit()
                conexion.close()

                messagebox.showinfo("Éxito", "Producto registrado correctamente")
                ventana_nuevo.destroy()
                self.cargar_productos()  # Refrescar tabla
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo registrar el producto: {str(e)}")

        btn_guardar = tk.Button(
            frame_botones,
            text="💾 Guardar",
            font=("Helvetica", 11),
            bg="#3a7ff6",
            fg="white",
            width=10,
            cursor="hand2",
            command=guardar_producto
        )
        btn_guardar.pack(side=tk.LEFT, padx=5)

        # Efecto hover
        btn_guardar.bind("<Enter>", lambda e: btn_guardar.config(bg="#1a5fce"))
        btn_guardar.bind("<Leave>", lambda e: btn_guardar.config(bg="#3a7ff6"))

        btn_cancelar = tk.Button(
            frame_botones,
            text="❌ Cancelar",
            font=("Helvetica", 11),
            bg="#e53935",
            fg="white",
            width=10,
            cursor="hand2",
            command=ventana_nuevo.destroy
        )
        btn_cancelar.pack(side=tk.LEFT, padx=5)

        # Efecto hover
        btn_cancelar.bind("<Enter>", lambda e: btn_cancelar.config(bg="#c62828"))
        btn_cancelar.bind("<Leave>", lambda e: btn_cancelar.config(bg="#e53935"))

    def editar_producto(self):
        """Abre ventana para editar un producto seleccionado"""
        # Obtener el producto seleccionado
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un producto para editar")
            return

        # Obtener datos del producto seleccionado
        valores = self.tabla.item(seleccion[0], 'values')
        id_producto = valores[0]
        nombre_actual = valores[1]
        precio_actual = valores[2].replace('$', '').replace(',', '')  # Limpiar formato
        stock_actual = valores[3]

        # Crear ventana de edición
        ventana_editar = tk.Toplevel(self.ventana)
        ventana_editar.title("Editar Producto")
        ventana_editar.geometry("400x320")
        ventana_editar.config(bg="#f5f5f5")
        ventana_editar.grab_set()  # Hacer modal

        # Centrar ventana
        utl.centrar_ventana(ventana_editar, 400, 320)

        # Establecer ícono si existe
        try:
            if os.path.exists("Img/lavadora.ico"):
                ventana_editar.iconbitmap("Img/lavadora.ico")
        except Exception:
            pass

        # Título
        tk.Label(
            ventana_editar,
            text=f"EDITAR PRODUCTO #{id_producto}",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        ).pack(pady=(20, 10))

        # Separador
        ttk.Separator(ventana_editar, orient="horizontal").pack(fill=tk.X, padx=20)

        # Frame para el formulario
        frame_form = tk.Frame(ventana_editar, bg="#f5f5f5")
        frame_form.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Etiquetas y campos
        tk.Label(frame_form, text="Nombre:", font=("Helvetica", 12), bg="#f5f5f5").grid(row=0, column=0, sticky=tk.W,
                                                                                        pady=10)
        entry_nombre = tk.Entry(frame_form, font=("Helvetica", 12), width=25)
        entry_nombre.grid(row=0, column=1, sticky=tk.W + tk.E, pady=10, padx=10)
        entry_nombre.insert(0, nombre_actual)

        tk.Label(frame_form, text="Precio ($):", font=("Helvetica", 12), bg="#f5f5f5").grid(row=1, column=0,
                                                                                            sticky=tk.W, pady=10)
        entry_precio = tk.Entry(frame_form, font=("Helvetica", 12), width=25)
        entry_precio.grid(row=1, column=1, sticky=tk.W + tk.E, pady=10, padx=10)
        entry_precio.insert(0, precio_actual)

        tk.Label(frame_form, text="Stock:", font=("Helvetica", 12), bg="#f5f5f5").grid(row=2, column=0, sticky=tk.W,
                                                                                       pady=10)
        entry_stock = tk.Entry(frame_form, font=("Helvetica", 12), width=25)
        entry_stock.grid(row=2, column=1, sticky=tk.W + tk.E, pady=10, padx=10)
        entry_stock.insert(0, stock_actual)

        # Botones
        frame_botones = tk.Frame(ventana_editar, bg="#f5f5f5")
        frame_botones.pack(pady=20)

        def actualizar_producto():
            # Validar campos
            nuevo_nombre = entry_nombre.get().strip()
            precio_texto = entry_precio.get().strip()
            stock_texto = entry_stock.get().strip()

            if not nuevo_nombre:
                messagebox.showwarning("Campo incompleto", "El nombre del producto es obligatorio")
                return

            # Validar precio
            if not utl.validar_numero(precio_texto):
                messagebox.showwarning("Valor inválido", "El precio debe ser un número válido")
                return

            nuevo_precio = float(precio_texto.replace(",", "."))
            if nuevo_precio <= 0:
                messagebox.showwarning("Valor inválido", "El precio debe ser mayor que cero")
                return

            # Validar stock
            if not stock_texto.isdigit():
                messagebox.showwarning("Valor inválido", "El stock debe ser un número entero")
                return

            nuevo_stock = int(stock_texto)
            if nuevo_stock < 0:
                messagebox.showwarning("Valor inválido", "El stock no puede ser negativo")
                return

            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()

                # Verificar si ya existe otro producto con ese nombre
                cursor.execute(
                    "SELECT COUNT(*) FROM productos WHERE nombre = %s AND id_producto != %s",
                    (nuevo_nombre, id_producto)
                )
                if cursor.fetchone()[0] > 0:
                    messagebox.showwarning("Nombre duplicado", "Ya existe otro producto con ese nombre")
                    return

                # Actualizar producto
                consulta = """
                UPDATE productos SET nombre = %s, precio = %s, stock = %s 
                WHERE id_producto = %s
                """
                cursor.execute(consulta, (nuevo_nombre, nuevo_precio, nuevo_stock, id_producto))

                conexion.commit()
                conexion.close()

                messagebox.showinfo("Éxito", "Producto actualizado correctamente")
                ventana_editar.destroy()
                self.cargar_productos()  # Refrescar tabla
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el producto: {str(e)}")

        btn_actualizar = tk.Button(
            frame_botones,
            text="💾 Actualizar",
            font=("Helvetica", 11),
            bg="#3a7ff6",
            fg="white",
            width=10,
            cursor="hand2",
            command=actualizar_producto
        )
        btn_actualizar.pack(side=tk.LEFT, padx=5)

        # Efecto hover
        btn_actualizar.bind("<Enter>", lambda e: btn_actualizar.config(bg="#1a5fce"))
        btn_actualizar.bind("<Leave>", lambda e: btn_actualizar.config(bg="#3a7ff6"))

        btn_cancelar = tk.Button(
            frame_botones,
            text="❌ Cancelar",
            font=("Helvetica", 11),
            bg="#e53935",
            fg="white",
            width=10,
            cursor="hand2",
            command=ventana_editar.destroy
        )
        btn_cancelar.pack(side=tk.LEFT, padx=5)

        # Efecto hover
        btn_cancelar.bind("<Enter>", lambda e: btn_cancelar.config(bg="#c62828"))
        btn_cancelar.bind("<Leave>", lambda e: btn_cancelar.config(bg="#e53935"))

    def eliminar_producto(self):
        """Elimina un producto seleccionado"""
        # Obtener el producto seleccionado
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un producto para eliminar")
            return

        # Obtener datos del producto seleccionado
        valores = self.tabla.item(seleccion[0], 'values')
        id_producto = valores[0]
        nombre_producto = valores[1]

        # Confirmar eliminación
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de eliminar el producto '{nombre_producto}'?"
        )

        if not confirmacion:
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Verificar si el producto está en uso en alguna venta o pedido
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

            # Eliminar producto
            cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))

            conexion.commit()
            conexion.close()

            messagebox.showinfo("Éxito", "Producto eliminado correctamente")
            self.cargar_productos()  # Refrescar tabla
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el producto: {str(e)}")

    def actualizar_stock(self):
        """Abre ventana para actualizar el stock de un producto"""
        # Obtener el producto seleccionado
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un producto para actualizar stock")
            return

        # Obtener datos del producto seleccionado
        valores = self.tabla.item(seleccion[0], 'values')
        id_producto = valores[0]
        nombre_producto = valores[1]
        stock_actual = int(valores[3])

        # Crear ventana para actualizar stock
        ventana_stock = tk.Toplevel(self.ventana)
        ventana_stock.title("Actualizar Stock")
        ventana_stock.geometry("400x280")
        ventana_stock.config(bg="#f5f5f5")
        ventana_stock.grab_set()  # Hacer modal

        # Centrar ventana
        utl.centrar_ventana(ventana_stock, 400, 280)

        # Establecer ícono si existe
        try:
            if os.path.exists("Img/lavadora.ico"):
                ventana_stock.iconbitmap("Img/lavadora.ico")
        except Exception:
            pass

        # Título
        tk.Label(
            ventana_stock,
            text="ACTUALIZAR STOCK",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        ).pack(pady=(20, 10))

        # Separador
        ttk.Separator(ventana_stock, orient="horizontal").pack(fill=tk.X, padx=20)

        # Frame para el formulario
        frame_form = tk.Frame(ventana_stock, bg="#f5f5f5")
        frame_form.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Información del producto
        tk.Label(
            frame_form,
            text=f"Producto: {nombre_producto}",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5"
        ).pack(anchor=tk.W, pady=5)

        tk.Label(
            frame_form,
            text=f"Stock actual: {stock_actual}",
            font=("Helvetica", 12),
            bg="#f5f5f5"
        ).pack(anchor=tk.W, pady=5)

        # Frame para opciones de entrada y salida
        frame_opciones = tk.Frame(frame_form, bg="#f5f5f5")
        frame_opciones.pack(fill=tk.X, pady=10)

        # Variable para radio buttons
        operacion = tk.StringVar(value="entrada")

        tk.Radiobutton(
            frame_opciones,
            text="Entrada de stock",
            variable=operacion,
            value="entrada",
            bg="#f5f5f5",
            font=("Helvetica", 11)
        ).pack(anchor=tk.W)

        tk.Radiobutton(
            frame_opciones,
            text="Salida de stock",
            variable=operacion,
            value="salida",
            bg="#f5f5f5",
            font=("Helvetica", 11)
        ).pack(anchor=tk.W)

        # Frame para cantidad
        frame_cantidad = tk.Frame(frame_form, bg="#f5f5f5")
        frame_cantidad.pack(fill=tk.X, pady=10)

        tk.Label(
            frame_cantidad,
            text="Cantidad:",
            font=("Helvetica", 12),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        entry_cantidad = tk.Entry(frame_cantidad, font=("Helvetica", 12), width=10)
        entry_cantidad.pack(side=tk.LEFT, padx=5)

        # Botones
        frame_botones = tk.Frame(ventana_stock, bg="#f5f5f5")
        frame_botones.pack(pady=10)

        def aplicar_cambio_stock():
            try:
                cantidad = int(entry_cantidad.get().strip())
                if cantidad <= 0:
                    messagebox.showwarning("Valor inválido", "La cantidad debe ser un número positivo")
                    return

                # Calcular nuevo stock
                if operacion.get() == "entrada":
                    nuevo_stock = stock_actual + cantidad
                else:  # salida
                    nuevo_stock = stock_actual - cantidad
                    if nuevo_stock < 0:
                        messagebox.showwarning(
                            "Stock insuficiente",
                            f"No hay suficiente stock. Stock actual: {stock_actual}"
                        )
                        return

                conexion = conectar_bd()
                cursor = conexion.cursor()

                # Actualizar stock
                cursor.execute(
                    "UPDATE productos SET stock = %s WHERE id_producto = %s",
                    (nuevo_stock, id_producto)
                )

                conexion.commit()
                conexion.close()

                # Notificar al usuario
                if operacion.get() == "entrada":
                    mensaje = f"Se agregaron {cantidad} unidades al stock"
                else:
                    mensaje = f"Se retiraron {cantidad} unidades del stock"

                messagebox.showinfo("Éxito", f"{mensaje}. Nuevo stock: {nuevo_stock}")
                ventana_stock.destroy()
                self.cargar_productos()  # Refrescar tabla

            except ValueError:
                messagebox.showwarning("Valor inválido", "Por favor ingresa un número entero")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el stock: {str(e)}")

        btn_aplicar = tk.Button(
            frame_botones,
            text="✓ Aplicar",
            font=("Helvetica", 11),
            bg="#3a7ff6",
            fg="white",
            width=10,
            cursor="hand2",
            command=aplicar_cambio_stock
        )
        btn_aplicar.pack(side=tk.LEFT, padx=5)

        # Efecto hover
        btn_aplicar.bind("<Enter>", lambda e: btn_aplicar.config(bg="#1a5fce"))
        btn_aplicar.bind("<Leave>", lambda e: btn_aplicar.config(bg="#3a7ff6"))

        btn_cancelar = tk.Button(
            frame_botones,
            text="❌ Cancelar",
            font=("Helvetica", 11),
            bg="#e53935",
            fg="white",
            width=10,
            cursor="hand2",
            command=ventana_stock.destroy
        )
        btn_cancelar.pack(side=tk.LEFT, padx=5)

        # Efecto hover
        btn_cancelar.bind("<Enter>", lambda e: btn_cancelar.config(bg="#c62828"))
        btn_cancelar.bind("<Leave>", lambda e: btn_cancelar.config(bg="#e53935"))


# Para probar de forma independiente
if __name__ == "__main__":
    GestionProductos()