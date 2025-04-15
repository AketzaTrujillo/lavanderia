import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from conexion import conectar_bd
import utileria as utl


class GestionProductos:
    def __init__(self, ventana_padre=None):
        # Si hay una ventana padre, crear Toplevel en lugar de Tk
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Gestión de Productos - Lavandería")
        self.ventana.geometry("800x600")
        self.ventana.config(bg="#f0f4c3")
        self.ventana.resizable(False, False)

        if ventana_padre:
            # Centrar la ventana si existe una ventana padre
            utl.centrar_ventana(self.ventana, 800, 600)
            # Hacer esta ventana modal
            self.ventana.transient(ventana_padre)
            self.ventana.grab_set()

        self.construir_interfaz()

        if not ventana_padre:
            self.ventana.mainloop()

    def construir_interfaz(self):
        # Frame principal
        self.frame_principal = tk.Frame(self.ventana, bg="#f0f4c3")
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        titulo = tk.Label(
            self.frame_principal,
            text="Gestión de Productos",
            font=("Helvetica", 20, "bold"),
            bg="#f0f4c3",
            fg="#33691e"
        )
        titulo.pack(pady=10)

        # Frame para botones de acción
        frame_botones = tk.Frame(self.frame_principal, bg="#f0f4c3")
        frame_botones.pack(pady=10)

        # Botones de acción
        botones = [
            ("Nuevo Producto", self.nuevo_producto),
            ("Editar Producto", self.editar_producto),
            ("Eliminar Producto", self.eliminar_producto),
            ("Actualizar Stock", self.actualizar_stock)
        ]

        for texto, comando in botones:
            b = tk.Button(
                frame_botones,
                text=texto,
                font=("Helvetica", 12),
                bg="#558b2f",
                fg="white",
                width=15,
                command=comando
            )
            b.pack(side=tk.LEFT, padx=5)

        # Frame para el buscador
        frame_busqueda = tk.Frame(self.frame_principal, bg="#f0f4c3")
        frame_busqueda.pack(fill=tk.X, pady=10)

        lbl_buscar = tk.Label(
            frame_busqueda,
            text="Buscar:",
            font=("Helvetica", 12),
            bg="#f0f4c3"
        )
        lbl_buscar.pack(side=tk.LEFT, padx=5)

        self.entry_buscar = tk.Entry(frame_busqueda, width=30, font=("Helvetica", 12))
        self.entry_buscar.pack(side=tk.LEFT, padx=5)

        btn_buscar = tk.Button(
            frame_busqueda,
            text="Buscar",
            font=("Helvetica", 12),
            bg="#558b2f",
            fg="white",
            command=self.buscar_productos
        )
        btn_buscar.pack(side=tk.LEFT, padx=5)

        # Frame para la tabla de productos
        frame_tabla = tk.Frame(self.frame_principal, bg="#f0f4c3")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10)

        # Tabla de productos (TreeView)
        columnas = ('id', 'nombre', 'precio', 'stock')

        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show='headings')

        # Configurar encabezados de columnas
        self.tabla.heading('id', text='ID')
        self.tabla.heading('nombre', text='Nombre')
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

        # Botón para refrescar la tabla
        btn_refrescar = tk.Button(
            self.frame_principal,
            text="Refrescar",
            font=("Helvetica", 12),
            bg="#558b2f",
            fg="white",
            command=self.cargar_productos
        )
        btn_refrescar.pack(pady=10)

        # Botón para volver
        btn_volver = tk.Button(
            self.frame_principal,
            text="Volver",
            font=("Helvetica", 12),
            bg="#c62828",
            fg="white",
            command=self.ventana.destroy
        )
        btn_volver.pack(pady=5)

        # Cargar productos iniciales
        self.cargar_productos()

    def cargar_productos(self):
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("SELECT id_producto, nombre, precio, stock FROM productos ORDER BY nombre")

            for producto in cursor.fetchall():
                self.tabla.insert('', tk.END, values=producto)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los productos: {str(e)}")

    def buscar_productos(self):
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
                self.tabla.insert('', tk.END, values=producto)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar productos: {str(e)}")

    def nuevo_producto(self):
        # Crear una nueva ventana para añadir producto
        ventana_nuevo = tk.Toplevel(self.ventana)
        ventana_nuevo.title("Nuevo Producto")
        ventana_nuevo.geometry("400x300")
        ventana_nuevo.config(bg="#f0f4c3")
        ventana_nuevo.grab_set()  # Hacer modal

        # Frame para el formulario
        frame_form = tk.Frame(ventana_nuevo, bg="#f0f4c3")
        frame_form.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Etiquetas y campos
        campos = [
            ("Nombre:", "nombre"),
            ("Precio ($):", "precio"),
            ("Stock inicial:", "stock")
        ]

        entradas = {}

        for i, (etiqueta, campo) in enumerate(campos):
            lbl = tk.Label(frame_form, text=etiqueta, font=("Helvetica", 12), bg="#f0f4c3")
            lbl.grid(row=i, column=0, sticky=tk.W, pady=5)

            entry = tk.Entry(frame_form, font=("Helvetica", 12))
            entry.grid(row=i, column=1, sticky=tk.W + tk.E, pady=5, padx=5)

            entradas[campo] = entry

        # Botones
        frame_botones = tk.Frame(ventana_nuevo, bg="#f0f4c3")
        frame_botones.pack(pady=10)

        def guardar_producto():
            # Validar campos
            nombre = entradas["nombre"].get().strip()
            precio_texto = entradas["precio"].get().strip()
            stock_texto = entradas["stock"].get().strip()

            if not nombre:
                messagebox.showwarning("Campo incompleto", "El nombre del producto es obligatorio")
                return

            # Validar precio
            try:
                precio = float(precio_texto)
                if precio <= 0:
                    messagebox.showwarning("Valor inválido", "El precio debe ser mayor que cero")
                    return
            except ValueError:
                messagebox.showwarning("Valor inválido", "El precio debe ser un número")
                return

            # Validar stock
            try:
                stock = int(stock_texto) if stock_texto else 0
                if stock < 0:
                    messagebox.showwarning("Valor inválido", "El stock no puede ser negativo")
                    return
            except ValueError:
                messagebox.showwarning("Valor inválido", "El stock debe ser un número entero")
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
            text="Guardar",
            font=("Helvetica", 12),
            bg="#558b2f",
            fg="white",
            command=guardar_producto
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

    def editar_producto(self):
        # Obtener el producto seleccionado
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un producto para editar")
            return

        # Obtener datos del producto seleccionado
        valores = self.tabla.item(seleccion[0], 'values')
        id_producto = valores[0]
        nombre_actual = valores[1]
        precio_actual = valores[2]
        stock_actual = valores[3]

        # Crear ventana de edición
        ventana_editar = tk.Toplevel(self.ventana)
        ventana_editar.title("Editar Producto")
        ventana_editar.geometry("400x300")
        ventana_editar.config(bg="#f0f4c3")
        ventana_editar.grab_set()  # Hacer modal

        # Frame para el formulario
        frame_form = tk.Frame(ventana_editar, bg="#f0f4c3")
        frame_form.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Etiquetas y campos
        lbl_nombre = tk.Label(frame_form, text="Nombre:", font=("Helvetica", 12), bg="#f0f4c3")
        lbl_nombre.grid(row=0, column=0, sticky=tk.W, pady=5)

        entry_nombre = tk.Entry(frame_form, font=("Helvetica", 12))
        entry_nombre.grid(row=0, column=1, sticky=tk.W + tk.E, pady=5, padx=5)
        entry_nombre.insert(0, nombre_actual)

        lbl_precio = tk.Label(frame_form, text="Precio ($):", font=("Helvetica", 12), bg="#f0f4c3")
        lbl_precio.grid(row=1, column=0, sticky=tk.W, pady=5)

        entry_precio = tk.Entry(frame_form, font=("Helvetica", 12))
        entry_precio.grid(row=1, column=1, sticky=tk.W + tk.E, pady=5, padx=5)
        entry_precio.insert(0, precio_actual)

        lbl_stock = tk.Label(frame_form, text="Stock:", font=("Helvetica", 12), bg="#f0f4c3")
        lbl_stock.grid(row=2, column=0, sticky=tk.W, pady=5)

        entry_stock = tk.Entry(frame_form, font=("Helvetica", 12))
        entry_stock.grid(row=2, column=1, sticky=tk.W + tk.E, pady=5, padx=5)
        entry_stock.insert(0, stock_actual)

        # Botones
        frame_botones = tk.Frame(ventana_editar, bg="#f0f4c3")
        frame_botones.pack(pady=10)

        def actualizar_producto():
            # Validar campos
            nuevo_nombre = entry_nombre.get().strip()
            precio_texto = entry_precio.get().strip()
            stock_texto = entry_stock.get().strip()

            if not nuevo_nombre:
                messagebox.showwarning("Campo incompleto", "El nombre del producto es obligatorio")
                return

            # Validar precio
            try:
                nuevo_precio = float(precio_texto)
                if nuevo_precio <= 0:
                    messagebox.showwarning("Valor inválido", "El precio debe ser mayor que cero")
                    return
            except ValueError:
                messagebox.showwarning("Valor inválido", "El precio debe ser un número")
                return

            # Validar stock
            try:
                nuevo_stock = int(stock_texto)
                if nuevo_stock < 0:
                    messagebox.showwarning("Valor inválido", "El stock no puede ser negativo")
                    return
            except ValueError:
                messagebox.showwarning("Valor inválido", "El stock debe ser un número entero")
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
            text="Actualizar",
            font=("Helvetica", 12),
            bg="#558b2f",
            fg="white",
            command=actualizar_producto
        )
        btn_actualizar.pack(side=tk.LEFT, padx=5)

        btn_cancelar = tk.Button(
            frame_botones,
            text="Cancelar",
            font=("Helvetica", 12),
            bg="#c62828",
            fg="white",
            command=ventana_editar.destroy
        )
        btn_cancelar.pack(side=tk.LEFT, padx=5)

    def eliminar_producto(self):
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

        # Pedir cantidad a añadir/restar
        ventana_stock = tk.Toplevel(self.ventana)
        ventana_stock.title("Actualizar Stock")
        ventana_stock.geometry("400x250")
        ventana_stock.config(bg="#f0f4c3")
        ventana_stock.grab_set()  # Hacer modal

        # Frame para el formulario
        frame_form = tk.Frame(ventana_stock, bg="#f0f4c3")
        frame_form.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Información del producto
        tk.Label(
            frame_form,
            text=f"Producto: {nombre_producto}",
            font=("Helvetica", 12, "bold"),
            bg="#f0f4c3"
        ).pack(anchor=tk.W, pady=5)

        tk.Label(
            frame_form,
            text=f"Stock actual: {stock_actual}",
            font=("Helvetica", 12),
            bg="#f0f4c3"
        ).pack(anchor=tk.W, pady=5)

        # Frame para opciones de entrada y salida
        frame_opciones = tk.Frame(frame_form, bg="#f0f4c3")
        frame_opciones.pack(fill=tk.X, pady=10)

        # Variable para radio buttons
        operacion = tk.StringVar(value="entrada")

        tk.Radiobutton(
            frame_opciones,
            text="Entrada de stock",
            variable=operacion,
            value="entrada",
            bg="#f0f4c3",
            font=("Helvetica", 11)
        ).pack(anchor=tk.W)

        tk.Radiobutton(
            frame_opciones,
            text="Salida de stock",
            variable=operacion,
            value="salida",
            bg="#f0f4c3",
            font=("Helvetica", 11)
        ).pack(anchor=tk.W)

        # Frame para cantidad
        frame_cantidad = tk.Frame(frame_form, bg="#f0f4c3")
        frame_cantidad.pack(fill=tk.X, pady=10)

        tk.Label(
            frame_cantidad,
            text="Cantidad:",
            font=("Helvetica", 12),
            bg="#f0f4c3"
        ).pack(side=tk.LEFT, padx=5)

        entry_cantidad = tk.Entry(frame_cantidad, font=("Helvetica", 12), width=10)
        entry_cantidad.pack(side=tk.LEFT, padx=5)

        # Botones
        frame_botones = tk.Frame(ventana_stock, bg="#f0f4c3")
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
            text="Aplicar",
            font=("Helvetica", 12),
            bg="#558b2f",
            fg="white",
            command=aplicar_cambio_stock
        )
        btn_aplicar.pack(side=tk.LEFT, padx=5)

        btn_cancelar = tk.Button(
            frame_botones,
            text="Cancelar",
            font=("Helvetica", 12),
            bg="#c62828",
            fg="white",
            command=ventana_stock.destroy
        )
        btn_cancelar.pack(side=tk.LEFT, padx=5)


# Para probar de forma independiente
if __name__ == "__main__":
    GestionProductos()