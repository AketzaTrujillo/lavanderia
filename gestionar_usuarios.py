"""
Módulo de Gestión de Usuarios para el Sistema de Lavandería
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import sys
import utileria as utl

# Asegurar que podamos importar módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Importar módulo de conexión
from conexion import conectar_bd


class GestionUsuarios:
    """Clase para gestionar los usuarios del sistema"""

    def __init__(self, ventana_padre=None):
        # Si hay una ventana padre, crear Toplevel en lugar de Tk
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Gestión de Usuarios - Lavandería")
        self.ventana.geometry("900x600")
        self.ventana.config(bg="#f5f5f5")
        self.ventana.resizable(False, False)

        if ventana_padre:
            # Centrar la ventana si existe una ventana padre
            utl.centrar_ventana(self.ventana, 900, 600)
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
            text="GESTIÓN DE USUARIOS",
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
            ("Nuevo Usuario", self.nuevo_usuario, "➕"),
            ("Editar Usuario", self.editar_usuario, "✏️"),
            ("Eliminar Usuario", self.eliminar_usuario, "🗑️")
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

        tk.Label(
            frame_busqueda,
            text="Buscar usuario:",
            font=("Helvetica", 12),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        self.entry_buscar = tk.Entry(frame_busqueda, width=30, font=("Helvetica", 12))
        self.entry_buscar.pack(side=tk.LEFT, padx=5)

        # Vincular tecla Enter al buscador
        self.entry_buscar.bind("<Return>", lambda event: self.buscar_usuarios())

        btn_buscar = tk.Button(
            frame_busqueda,
            text="🔍 Buscar",
            font=("Helvetica", 10),
            bg="#3a7ff6",
            fg="white",
            padx=10,
            cursor="hand2",
            command=self.buscar_usuarios
        )
        btn_buscar.pack(side=tk.LEFT, padx=5)

        # Efecto hover
        btn_buscar.bind("<Enter>", lambda e: btn_buscar.config(bg="#1a5fce"))
        btn_buscar.bind("<Leave>", lambda e: btn_buscar.config(bg="#3a7ff6"))

        # Frame para la tabla de usuarios
        frame_tabla = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10)

        # Tabla de usuarios (TreeView)
        columnas = ('id', 'nombre', 'correo', 'rol', 'fecha_registro')

        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=15)

        # Aplicar estilo a la tabla
        utl.aplicar_estilo_tabla(self.tabla)

        # Configurar encabezados de columnas
        self.tabla.heading('id', text='ID')
        self.tabla.heading('nombre', text='Nombre')
        self.tabla.heading('correo', text='Correo')
        self.tabla.heading('rol', text='Rol')
        self.tabla.heading('fecha_registro', text='Fecha Registro')

        # Configurar anchos de columnas
        self.tabla.column('id', width=50, anchor=tk.CENTER)
        self.tabla.column('nombre', width=200)
        self.tabla.column('correo', width=250)
        self.tabla.column('rol', width=100, anchor=tk.CENTER)
        self.tabla.column('fecha_registro', width=150, anchor=tk.CENTER)

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
            command=self.cargar_usuarios
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

        # Cargar usuarios iniciales
        self.cargar_usuarios()

    def cargar_usuarios(self):
        """Carga todos los usuarios en la tabla"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("SELECT id_usuario, nombre, correo, rol, fecha_registro FROM usuarios ORDER BY nombre")

            for usuario in cursor.fetchall():
                # Formatear fecha
                fecha = utl.formatear_fecha(usuario[4]) if usuario[4] else ""
                valores = (usuario[0], usuario[1], usuario[2], usuario[3].capitalize(), fecha)
                self.tabla.insert('', tk.END, values=valores)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los usuarios: {str(e)}")

    def buscar_usuarios(self):
        """Busca usuarios según el texto ingresado"""
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
            ORDER BY nombre
            """

            cursor.execute(consulta, (f"%{texto_busqueda}%", f"%{texto_busqueda}%"))

            for usuario in cursor.fetchall():
                # Formatear fecha
                fecha = utl.formatear_fecha(usuario[4]) if usuario[4] else ""
                valores = (usuario[0], usuario[1], usuario[2], usuario[3].capitalize(), fecha)
                self.tabla.insert('', tk.END, values=valores)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar usuarios: {str(e)}")

    def nuevo_usuario(self):
        """Abre ventana para crear un nuevo usuario"""
        # Crear una nueva ventana para añadir usuario
        ventana_nuevo = tk.Toplevel(self.ventana)
        ventana_nuevo.title("Nuevo Usuario")
        ventana_nuevo.geometry("500x350")
        ventana_nuevo.config(bg="#f5f5f5")
        ventana_nuevo.grab_set()  # Hacer modal

        # Centrar ventana
        utl.centrar_ventana(ventana_nuevo, 500, 350)

        # Establecer ícono si existe
        try:
            if os.path.exists("Img/lavadora.ico"):
                ventana_nuevo.iconbitmap("Img/lavadora.ico")
        except Exception:
            pass

        # Título
        tk.Label(
            ventana_nuevo,
            text="REGISTRO DE NUEVO USUARIO",
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
        tk.Label(frame_form, text="Nombre:", font=("Helvetica", 12), bg="#f5f5f5").grid(row=0, column=0, sticky=tk.W,
                                                                                        pady=10)
        entry_nombre = tk.Entry(frame_form, font=("Helvetica", 12), width=30)
        entry_nombre.grid(row=0, column=1, sticky=tk.W + tk.E, pady=10, padx=10)

        tk.Label(frame_form, text="Correo:", font=("Helvetica", 12), bg="#f5f5f5").grid(row=1, column=0, sticky=tk.W,
                                                                                        pady=10)
        entry_correo = tk.Entry(frame_form, font=("Helvetica", 12), width=30)
        entry_correo.grid(row=1, column=1, sticky=tk.W + tk.E, pady=10, padx=10)

        tk.Label(frame_form, text="Contraseña:", font=("Helvetica", 12), bg="#f5f5f5").grid(row=2, column=0,
                                                                                            sticky=tk.W, pady=10)
        entry_contrasena = tk.Entry(frame_form, font=("Helvetica", 12), width=30, show="*")
        entry_contrasena.grid(row=2, column=1, sticky=tk.W + tk.E, pady=10, padx=10)

        tk.Label(frame_form, text="Rol:", font=("Helvetica", 12), bg="#f5f5f5").grid(row=3, column=0, sticky=tk.W,
                                                                                     pady=10)
        combo_rol = ttk.Combobox(frame_form, values=["admin", "cajero"], font=("Helvetica", 12), state="readonly",
                                 width=28)
        combo_rol.grid(row=3, column=1, sticky=tk.W + tk.E, pady=10, padx=10)
        combo_rol.current(1)  # Por defecto, seleccionar "cajero"

        # Botones
        frame_botones = tk.Frame(ventana_nuevo, bg="#f5f5f5")
        frame_botones.pack(pady=20)

        def guardar_usuario():
            # Validar campos
            nombre = entry_nombre.get().strip()
            correo = entry_correo.get().strip()
            contrasena = entry_contrasena.get().strip()
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
            text="💾 Guardar",
            font=("Helvetica", 11),
            bg="#3a7ff6",
            fg="white",
            width=10,
            cursor="hand2",
            command=guardar_usuario
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

    def editar_usuario(self):
        """Abre ventana para editar un usuario seleccionado"""
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

            nombre_actual, correo_actual, rol_actual = usuario

            # Crear ventana de edición
            ventana_editar = tk.Toplevel(self.ventana)
            ventana_editar.title("Editar Usuario")
            ventana_editar.geometry("500x350")
            ventana_editar.config(bg="#f5f5f5")
            ventana_editar.grab_set()  # Hacer modal

            # Centrar ventana
            utl.centrar_ventana(ventana_editar, 500, 350)

            # Establecer ícono si existe
            try:
                if os.path.exists("Img/lavadora.ico"):
                    ventana_editar.iconbitmap("Img/lavadora.ico")
            except Exception:
                pass

            # Título
            tk.Label(
                ventana_editar,
                text=f"EDITAR USUARIO #{id_usuario}",
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
            tk.Label(frame_form, text="Nombre:", font=("Helvetica", 12), bg="#f5f5f5").grid(row=0, column=0,
                                                                                            sticky=tk.W, pady=10)
            entry_nombre = tk.Entry(frame_form, font=("Helvetica", 12), width=30)
            entry_nombre.grid(row=0, column=1, sticky=tk.W + tk.E, pady=10, padx=10)
            entry_nombre.insert(0, nombre_actual)

            tk.Label(frame_form, text="Correo:", font=("Helvetica", 12), bg="#f5f5f5").grid(row=1, column=0,
                                                                                            sticky=tk.W, pady=10)
            entry_correo = tk.Entry(frame_form, font=("Helvetica", 12), width=30)
            entry_correo.grid(row=1, column=1, sticky=tk.W + tk.E, pady=10, padx=10)
            entry_correo.insert(0, correo_actual)

            tk.Label(frame_form, text="Nueva Contraseña:", font=("Helvetica", 12), bg="#f5f5f5").grid(row=2, column=0,
                                                                                                      sticky=tk.W,
                                                                                                      pady=10)
            entry_contrasena = tk.Entry(frame_form, font=("Helvetica", 12), width=30, show="*")
            entry_contrasena.grid(row=2, column=1, sticky=tk.W + tk.E, pady=10, padx=10)

            tk.Label(
                frame_form,
                text="(Dejar en blanco para mantener la actual)",
                font=("Helvetica", 8),
                bg="#f5f5f5",
                fg="#666"
            ).grid(row=2, column=1, sticky=tk.E, pady=(0, 0), padx=10)

            tk.Label(frame_form, text="Rol:", font=("Helvetica", 12), bg="#f5f5f5").grid(row=3, column=0, sticky=tk.W,
                                                                                         pady=10)
            combo_rol = ttk.Combobox(frame_form, values=["admin", "cajero"], font=("Helvetica", 12), state="readonly",
                                     width=28)
            combo_rol.grid(row=3, column=1, sticky=tk.W + tk.E, pady=10, padx=10)
            combo_rol.set(rol_actual)  # Seleccionar el rol actual

            # Botones
            frame_botones = tk.Frame(ventana_editar, bg="#f5f5f5")
            frame_botones.pack(pady=20)

            def actualizar_usuario():
                # Validar campos
                nuevo_nombre = entry_nombre.get().strip()
                nuevo_correo = entry_correo.get().strip()
                nueva_contrasena = entry_contrasena.get().strip()
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
                text="💾 Actualizar",
                font=("Helvetica", 11),
                bg="#3a7ff6",
                fg="white",
                width=10,
                cursor="hand2",
                command=actualizar_usuario
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

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la información del usuario: {str(e)}")

    def eliminar_usuario(self):
        """Elimina un usuario seleccionado"""
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
            f"¿Estás seguro de eliminar al usuario '{nombre_usuario}'?\n\nEsta acción no se puede deshacer."
        )

        if not confirmacion:
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Verificar si es el último administrador
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'admin'")
            total_admins = cursor.fetchone()[0]

            cursor.execute("SELECT rol FROM usuarios WHERE id_usuario = %s", (id_usuario,))
            rol_usuario = cursor.fetchone()[0]

            if rol_usuario == 'admin' and total_admins <= 1:
                messagebox.showwarning(
                    "No se puede eliminar",
                    "No se puede eliminar el último administrador del sistema."
                )
                conexion.close()
                return

            # Eliminar usuario
            cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))

            conexion.commit()
            conexion.close()

            messagebox.showinfo("Éxito", f"Usuario '{nombre_usuario}' eliminado correctamente")
            self.cargar_usuarios()  # Refrescar tabla
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el usuario: {str(e)}")


# Para probar de forma independiente
if __name__ == "__main__":
    GestionUsuarios()