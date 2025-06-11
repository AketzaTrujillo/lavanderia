import tkinter as tk
from tkinter import ttk, messagebox
import utileria as utl
from conexion import conectar_bd

class PromosDescuentosVentana:
    def __init__(self, ventana_padre=None, id_usuario=None):
        # Crear ventana
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Promociones y Descuentos - Lavandería")
        self.ventana.geometry("1000x700")
        self.ventana.minsize(900, 600)
        self.ventana.config(bg="#f5f7fa")
        self.ventana.resizable(True, True)

        if ventana_padre:
            utl.centrar_ventana(self.ventana, 1000, 700)
            self.ventana.transient(ventana_padre)
            self.ventana.grab_set()

        # Tabs para productos y servicios
        notebook = ttk.Notebook(self.ventana)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.tab_productos = tk.Frame(notebook, bg="#f5f7fa")
        self.tab_servicios = tk.Frame(notebook, bg="#f5f7fa")
        notebook.add(self.tab_productos, text="🛍️ Productos")
        notebook.add(self.tab_servicios, text="🧺 Servicios")

        # Construir cada tab
        self.construir_tab(self.tab_productos, tipo="producto")
        self.construir_tab(self.tab_servicios, tipo="servicio")

        # Botón cerrar
        frame_cerrar = tk.Frame(self.ventana, bg="#f5f7fa")
        frame_cerrar.pack(fill=tk.X, pady=(0, 10), padx=20)
        btn_cerrar = tk.Button(
            frame_cerrar, text="Cerrar", font=("Helvetica", 11),
            bg="#e53935", fg="white", width=12, cursor="hand2", command=self.ventana.destroy
        )
        btn_cerrar.pack(side=tk.RIGHT)
        btn_cerrar.bind("<Enter>", lambda e: btn_cerrar.config(bg="#c62828"))
        btn_cerrar.bind("<Leave>", lambda e: btn_cerrar.config(bg="#e53935"))

        if not ventana_padre:
            self.ventana.mainloop()

    def construir_tab(self, tab, tipo):
        # Título
        titulo = "PRODUCTOS EN VENTA" if tipo == "producto" else "SERVICIOS OFERTADOS"
        tk.Label(tab, text=titulo, font=("Helvetica", 16, "bold"), bg="#f5f7fa", fg="#1976D2").pack(pady=(10, 10))

        # Frame de búsqueda
        frame_busqueda = tk.Frame(tab, bg="#f5f7fa")
        frame_busqueda.pack(fill=tk.X, pady=(0, 10), padx=10)
        tk.Label(frame_busqueda, text="Buscar:", font=("Helvetica", 11), bg="#f5f7fa").pack(side=tk.LEFT, padx=5)
        entry_buscar = tk.Entry(frame_busqueda, width=30, font=("Helvetica", 11))
        entry_buscar.pack(side=tk.LEFT, padx=5)
        btn_buscar = tk.Button(
            frame_busqueda, text="Buscar", font=("Helvetica", 10, "bold"),
            bg="#1976D2", fg="white", relief="flat", cursor="hand2",
            command=lambda: self.cargar_tabla(tab, tipo, entry_buscar.get().strip())
        )
        btn_buscar.pack(side=tk.LEFT, padx=5)

        # Tabla
        columnas = ("id", "nombre", "precio", "promo_desc", "nuevo_precio")
        tabla = ttk.Treeview(tab, columns=columnas, show="headings", height=12)
        tabla.heading("id", text="ID")
        tabla.heading("nombre", text="Nombre")
        tabla.heading("precio", text="Precio")
        tabla.heading("promo_desc", text="Promoción/Descuento")
        tabla.heading("nuevo_precio", text="Precio Final")
        tabla.column("id", width=60, anchor=tk.CENTER)
        tabla.column("nombre", width=300)
        tabla.column("precio", width=100, anchor=tk.CENTER)
        tabla.column("promo_desc", width=180, anchor=tk.CENTER)
        tabla.column("nuevo_precio", width=120, anchor=tk.CENTER)
        tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=tabla.yview)
        tabla.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10))

        # Guardar referencia
        if tipo == "producto":
            self.tabla_productos = tabla
            self.entry_buscar_producto = entry_buscar
        else:
            self.tabla_servicios = tabla
            self.entry_buscar_servicio = entry_buscar

        # Frame para aplicar/quitar promoción/descuento
        frame_form = tk.Frame(tab, bg="#f5f7fa")
        frame_form.pack(fill=tk.X, pady=5, padx=10)

        # Descuento
        tk.Label(frame_form, text="Descuento (%):", font=("Helvetica", 11), bg="#f5f7fa").pack(side=tk.LEFT, padx=5)
        entry_descuento = tk.Entry(frame_form, width=8, font=("Helvetica", 11))
        entry_descuento.pack(side=tk.LEFT, padx=5)

        # Promoción
        tk.Label(frame_form, text="Promoción (ej: 2x1, Regalo):", font=("Helvetica", 11), bg="#f5f7fa").pack(side=tk.LEFT, padx=5)
        entry_promocion = tk.Entry(frame_form, width=18, font=("Helvetica", 11))
        entry_promocion.pack(side=tk.LEFT, padx=5)

        btn_aplicar = tk.Button(
            frame_form, text="Aplicar", font=("Helvetica", 10, "bold"),
            bg="#059669", fg="white", relief="flat", cursor="hand2",
            command=lambda: self.aplicar_promocion(tabla, tipo, entry_descuento, entry_promocion)
        )
        btn_aplicar.pack(side=tk.LEFT, padx=10)
        btn_quitar = tk.Button(
            frame_form, text="Quitar Promoción/Descuento", font=("Helvetica", 10, "bold"),
            bg="#e53935", fg="white", relief="flat", cursor="hand2",
            command=lambda: self.quitar_promocion(tabla, tipo)
        )
        btn_quitar.pack(side=tk.LEFT, padx=10)

        # Cargar datos iniciales
        self.cargar_tabla(tab, tipo)

    def cargar_tabla(self, tab, tipo, filtro=""):
        tabla = self.tabla_productos if tipo == "producto" else self.tabla_servicios
        for item in tabla.get_children():
            tabla.delete(item)
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            if tipo == "producto":
                consulta = "SELECT id_producto, nombre, precio, promo_desc, nuevo_precio FROM productos"
                params = ()
                if filtro:
                    consulta += " WHERE nombre LIKE %s OR id_producto = %s"
                    try:
                        id_busqueda = int(filtro)
                    except ValueError:
                        id_busqueda = -1
                    params = (f"%{filtro}%", id_busqueda)
                cursor.execute(consulta, params)
            else:
                consulta = "SELECT id_servicio, nombre, precio, promo_desc, nuevo_precio FROM servicios"
                params = ()
                if filtro:
                    consulta += " WHERE nombre LIKE %s OR id_servicio = %s"
                    try:
                        id_busqueda = int(filtro)
                    except ValueError:
                        id_busqueda = -1
                    params = (f"%{filtro}%", id_busqueda)
                cursor.execute(consulta, params)
            for row in cursor.fetchall():
                id_, nombre, precio, promo_desc, nuevo_precio = row
                tabla.insert("", tk.END, values=(
                    id_, nombre, f"${float(precio):.2f}",
                    promo_desc if promo_desc else "",
                    f"${float(nuevo_precio) if nuevo_precio else float(precio):.2f}"
                ))
            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar {'productos' if tipo == 'producto' else 'servicios'}: {str(e)}")

    def aplicar_promocion(self, tabla, tipo, entry_descuento, entry_promocion):
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Selecciona un elemento", "Debes seleccionar un producto o servicio.")
            return
        descuento = entry_descuento.get().strip()
        promocion = entry_promocion.get().strip()
        if not descuento and not promocion:
            messagebox.showwarning("Campo vacío", "Ingresa un descuento o promoción.")
            return
        item = tabla.item(seleccion[0], "values")
        id_item = item[0]
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            # Obtener precio original
            if tipo == "producto":
                cursor.execute("SELECT precio FROM productos WHERE id_producto = %s", (id_item,))
            else:
                cursor.execute("SELECT precio FROM servicios WHERE id_servicio = %s", (id_item,))
            precio = float(cursor.fetchone()[0])
            promo_desc = ""
            nuevo_precio = None
            # Si hay descuento
            if descuento:
                try:
                    porc = float(descuento)
                    promo_desc = f"{porc:.0f}%"
                    nuevo_precio = round(precio * (1 - porc / 100), 2)
                except Exception:
                    messagebox.showerror("Error", "Descuento inválido.")
                    return
            # Si hay promoción de texto
            if promocion:
                if promo_desc:
                    promo_desc += f" + {promocion}"
                else:
                    promo_desc = promocion
            # Si no hay descuento, el precio promocional es el original
            if not nuevo_precio:
                nuevo_precio = precio
            # Guardar en base de datos
            if tipo == "producto":
                cursor.execute(
                    "UPDATE productos SET promo_desc = %s, nuevo_precio = %s WHERE id_producto = %s",
                    (promo_desc, nuevo_precio, id_item)
                )
            else:
                cursor.execute(
                    "UPDATE servicios SET promo_desc = %s, nuevo_precio = %s WHERE id_servicio = %s",
                    (promo_desc, nuevo_precio, id_item)
                )
            conexion.commit()
            conexion.close()
            self.cargar_tabla(tabla.master, tipo)
            entry_descuento.delete(0, tk.END)
            entry_promocion.delete(0, tk.END)
            messagebox.showinfo("Éxito", "Promoción/descuento aplicado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo aplicar la promoción: {str(e)}")

    def quitar_promocion(self, tabla, tipo):
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Selecciona un elemento", "Debes seleccionar un producto o servicio.")
            return
        item = tabla.item(seleccion[0], "values")
        id_item = item[0]
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            # Quitar promoción y restaurar precio original
            if tipo == "producto":
                cursor.execute(
                    "UPDATE productos SET promo_desc = NULL, nuevo_precio = NULL WHERE id_producto = %s",
                    (id_item,)
                )
            else:
                cursor.execute(
                    "UPDATE servicios SET promo_desc = NULL, nuevo_precio = NULL WHERE id_servicio = %s",
                    (id_item,)
                )
            conexion.commit()
            conexion.close()
            self.cargar_tabla(tabla.master, tipo)
            messagebox.showinfo("Éxito", "Promoción/descuento eliminada.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo quitar la promoción: {str(e)}")