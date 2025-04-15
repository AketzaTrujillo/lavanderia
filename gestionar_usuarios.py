import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from conexion import conectar_bd
import utileria as utl


class GestionUsuarios:
    def __init__(self, ventana_padre=None):
        # Si hay una ventana padre, crear Toplevel en lugar de Tk
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Gestión de Usuarios - Lavandería")
        self.ventana.geometry("900x600")
        self.ventana.config(bg="#f0f4c3")
        self.ventana.resizable(False, False)

        if ventana_padre:
            # Centrar la ventana si existe una ventana padre
            utl.centrar_ventana(self.ventana, 900, 600)
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
            text="Gestión de Usuarios",
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
            ("Nuevo Usuario", self.nuevo_usuario),
            ("Editar Usuario", self.editar_usuario),
            ("Eliminar Usuario", self.eliminar_usuario)
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
            command=self.buscar_usuarios
        )
        btn_buscar.pack(side=tk.LEFT, padx=5)

        # Frame para la tabla de usuarios
        frame_tabla = tk.Frame(self.frame_principal, bg="#f0f4c3")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10)

        # Tabla de usuarios (TreeView)
        columnas = ('id', 'nombre', 'correo', 'rol', 'fecha_registro')

        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show='headings')

        # Configurar encabezados de columnas
        self.tabla.heading('id', text='ID')
        self.tabla.heading('nombre', text='Nombre')
        self.tabla.heading('correo', text='Correo')
        self.tabla.heading('rol', text='Rol')
        self.tabla.heading('fecha_registro', text='Fecha Registro')

        # Configurar anchos de columnas
        self.tabla.column('id', width=50, anchor=tk.CENTER)
        self.tabla.column('nombre', width=200)
        self.tabla.column('correo', width=200)
        self.tabla.column('rol', width=100, anchor=tk.CENTER)
        self.tabla.column('fecha_registro', width=150, anchor=tk.CENTER)

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
            command=self.cargar_usuarios
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

        # Cargar usuarios iniciales
        self.cargar_usuarios()

    def cargar_usuarios(self):
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("SELECT id_usuario, nombre, correo, rol, fecha_registro FROM usuarios ORDER BY id_usuario")

            for usuario in cursor.fetchall():
                self.tabla.insert('', tk.END, values=usuario)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los usuarios: {str(e)}")

    def buscar_usuarios(self):
        texto_busqueda = self.entry_buscar.get().strip()

        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        if not texto_busqueda:
            self.cargar_usuarios()
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Búsqueda por nombre o correo
            consulta = """
            SELECT id_usuario, nombre, correo, rol, fecha_registro 
            FROM usuarios 
            WHERE nombre LIKE %s OR correo LIKE %s
            ORDER BY id_usuario
            """

            cursor.execute(consulta, (f"%{texto_busqueda}%", f"%{texto_busqueda}%"))

            for usuario in cursor.fetchall():
                self.tabla.insert('', tk.END, values=usuario)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar usuarios: {str(e)}")

    def nuevo_usuario(self):
        # Crear una nueva ventana para añadir usuario
        ventana_nuevo = tk.Toplevel(self.ventana)
        ventana_nuevo.title("Nuevo Usuario")
        ventana_nuevo.geometry("400x300")
        ventana_nuevo.config(bg="#f0f4c3")
        ventana_nuevo.grab_set()  # Hacer modal

        # Frame para el formulario
        frame_form = tk.Frame(ventana_nuevo, bg="#f0f4c3")
        frame_form.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Etiquetas y campos
        campos = [
            ("Nombre:", "nombre"),
            ("Correo:", "correo"),
            ("Contraseña:", "contrasena"),
        ]

        entradas = {}

        for i, (etiqueta, campo) in enumerate(campos):
            lbl = tk.Label(frame_form, text=etiqueta, font=("Helvetica", 12), bg="#f0f4c3")
            lbl.grid(row=i, column=0, sticky=tk.W, pady=5)

            # Si es contraseña, ocultar texto
            show = "*" if campo == "contrasena" else ""

            entry = tk.Entry(frame_form, font=("Helvetica", 12), show=show)
            entry.grid(row=i, column=1, sticky=tk.W + tk.E, pady=5, padx=5)

            entradas[campo] = entry

        # Rol (combobox)
        lbl_rol = tk.Label(frame_form, text="Rol:", font=("Helvetica", 12), bg="#f0f4c3")
        lbl_rol.grid(row=len(campos), column=0, sticky=tk.W, pady=5)

        combo_rol = ttk.Combobox(frame_form, values=["admin", "cajero"], state="readonly")
        combo_rol.grid(row=len(campos), column=1, sticky=tk.W + tk.E, pady=5, padx=5)
        combo_rol.current(1)  # Por defecto, seleccionar "cajero"

        # Botones
        frame_botones = tk.Frame(ventana_nuevo, bg="#f0f4c3")
        frame_botones.pack(pady=10)

        def guardar_usuario():
            # Validar campos
            nombre = entradas["nombre"].get().strip()
            correo = entradas["correo"].get().strip()
            contrasena = entradas["contrasena"].get().strip()
            rol = combo_rol.get()

            if not nombre or not correo or not contrasena or not rol:
                messagebox.showwarning("Campos incompletos", "Todos los campos son obligatorios")
                return

            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()

                # Verificar si ya existe un usuario con ese correo
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE correo = %s", (correo,))
                if cursor.fetchone()[0] > 0:
                    messagebox.showwarning("Correo duplicado", "Ya existe un usuario con ese correo")
                    return

                # Insertar nuevo usuario
                consulta = "INSERT INTO usuarios (nombre, correo, contraseña, rol) VALUES (%s, %s, %s, %s)"
                cursor.execute(consulta, (nombre, correo, contrasena, rol))

                conexion.commit()
                conexion.close()

                messagebox.showinfo("Éxito", "Usuario registrado correctamente")
                ventana_nuevo.destroy()
                self.cargar_usuarios()  # Refrescar tabla
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo registrar el usuario: {str(e)}")

        btn_guardar = tk.Button(
            frame_botones,
            text="Guardar",
            font=("Helvetica", 12),
            bg="#558b2f",
            fg="white",
            command=guardar_usuario
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

    def editar_usuario(self):
        # Obtener el usuario seleccionado
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un usuario para editar")
            return

        # Obtener datos del usuario seleccionado
        valores = self.tabla.item(seleccion[0], 'values')
        id_usuario = valores[0]

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Obtener datos completos del usuario
            cursor.execute("SELECT nombre, correo, rol FROM usuarios WHERE id_usuario = %s", (id_usuario,))
            usuario = cursor.fetchone()

            if not usuario:
                messagebox.showerror("Error", "No se pudo obtener la información del usuario")
                return

            nombre, correo, rol = usuario

            # Crear ventana de edición
            ventana_editar = tk.Toplevel(self.ventana)
            ventana_editar.title("Editar Usuario")
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
            entry_nombre.insert(0, nombre)

            lbl_correo = tk.Label(frame_form, text="Correo:", font=("Helvetica", 12), bg="#f0f4c3")
            lbl_correo.grid(row=1, column=0, sticky=tk.W, pady=5)

            entry_correo = tk.Entry(frame_form, font=("Helvetica", 12))
            entry_correo.grid(row=1, column=1, sticky=tk.W + tk.E, pady=5, padx=5)
            entry_correo.insert(0, correo)

            lbl_pass = tk.Label(frame_form, text="Nueva Contraseña:", font=("Helvetica", 12), bg="#f0f4c3")
            lbl_pass.grid(row=2, column=0, sticky=tk.W, pady=5)

            entry_pass = tk.Entry(frame_form, font=("Helvetica", 12), show="*")
            entry_pass.grid(row=2, column=1, sticky=tk.W + tk.E, pady=5, padx=5)

            # Rol (combobox)
            lbl_rol = tk.Label(frame_form, text="Rol:", font=("Helvetica", 12), bg="#f0f4c3")
            lbl_rol.grid(row=3, column=0, sticky=tk.W, pady=5)

            combo_rol = ttk.Combobox(frame_form, values=["admin", "cajero"], state="readonly")
            combo_rol.grid(row=3, column=1, sticky=tk.W + tk.E, pady=5, padx=5)
            combo_rol.set(rol)  # Seleccionar el rol actual

            # Botones
            frame_botones = tk.Frame(ventana_editar, bg="#f0f4c3")
            frame_botones.pack(pady=10)

            def actualizar_usuario():
                # Validar campos
                nuevo_nombre = entry_nombre.get().strip()
                nuevo_correo = entry_correo.get().strip()
                nueva_contrasena = entry_pass.get().strip()
                nuevo_rol = combo_rol.get()

                if not nuevo_nombre or not nuevo_correo or not nuevo_rol:
                    messagebox.showwarning("Campos incompletos", "Nombre, correo y rol son obligatorios")
                    return

                try:
                    conexion = conectar_bd()
                    cursor = conexion.cursor()

                    # Verificar si ya existe otro usuario con ese correo
                    cursor.execute(
                        "SELECT COUNT(*) FROM usuarios WHERE correo = %s AND id_usuario != %s",
                        (nuevo_correo, id_usuario)
                    )
                    if cursor.fetchone()[0] > 0:
                        messagebox.showwarning("Correo duplicado", "Ya existe otro usuario con ese correo")
                        return

                    # Actualizar usuario
                    if nueva_contrasena:
                        # Si se proporcionó nueva contraseña
                        consulta = """
                        UPDATE usuarios SET nombre = %s, correo = %s, contraseña = %s, rol = %s 
                        WHERE id_usuario = %s
                        """
                        cursor.execute(consulta, (nuevo_nombre, nuevo_correo, nueva_contrasena, nuevo_rol, id_usuario))
                    else:
                        # Si no se proporcionó nueva contraseña
                        consulta = """
                        UPDATE usuarios SET nombre = %s, correo = %s, rol = %s 
                        WHERE id_usuario = %s
                        """
                        cursor.execute(consulta, (nuevo_nombre, nuevo_correo, nuevo_rol, id_usuario))

                    conexion.commit()
                    conexion.close()

                    messagebox.showinfo("Éxito", "Usuario actualizado correctamente")
                    ventana_editar.destroy()
                    self.cargar_usuarios()  # Refrescar tabla
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo actualizar el usuario: {str(e)}")

            btn_actualizar = tk.Button(
                frame_botones,
                text="Actualizar",
                font=("Helvetica", 12),
                bg="#558b2f",
                fg="white",
                command=actualizar_usuario
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

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la información del usuario: {str(e)}")

    def eliminar_usuario(self):
        # Obtener el usuario seleccionado
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un usuario para eliminar")
            return

        # Obtener datos del usuario seleccionado
        valores = self.tabla.item(seleccion[0], 'values')
        id_usuario = valores[0]
        nombre_usuario = valores[1]

        # Confirmar eliminación
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de eliminar al usuario {nombre_usuario}?"
        )

        if not confirmacion:
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Eliminar usuario
            cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))

            conexion.commit()
            conexion.close()

            messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
            self.cargar_usuarios()  # Refrescar tabla
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el usuario: {str(e)}")


# Para probar de forma independiente
if __name__ == "__main__":
    GestionUsuarios()