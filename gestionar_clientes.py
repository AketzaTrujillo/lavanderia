import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from conexion import conectar_bd
import utileria as utl
from datetime import datetime


class GestionClientes:
    def __init__(self, ventana_padre=None):
        # Si hay una ventana padre, crear Toplevel en lugar de Tk
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Gestión de Clientes - Lavandería")
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
            text="Gestión de Clientes",
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
            ("Nuevo Cliente", self.nuevo_cliente),
            ("Editar Cliente", self.editar_cliente),
            ("Ver Historial", self.ver_historial),
            ("Gestionar Puntos", self.gestionar_puntos),
            ("Eliminar Cliente", self.eliminar_cliente)
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
            command=self.buscar_clientes
        )
        btn_buscar.pack(side=tk.LEFT, padx=5)

        # Frame para la tabla de clientes
        frame_tabla = tk.Frame(self.frame_principal, bg="#f0f4c3")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10)

        # Tabla de clientes (TreeView)
        columnas = ('id', 'nombre', 'telefono', 'correo', 'puntos', 'fecha_registro')

        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show='headings')

        # Configurar encabezados de columnas
        self.tabla.heading('id', text='ID')
        self.tabla.heading('nombre', text='Nombre')
        self.tabla.heading('telefono', text='Teléfono')
        self.tabla.heading('correo', text='Correo')
        self.tabla.heading('puntos', text='Puntos')
        self.tabla.heading('fecha_registro', text='Fecha Registro')

        # Configurar anchos de columnas
        self.tabla.column('id', width=50, anchor=tk.CENTER)
        self.tabla.column('nombre', width=200)
        self.tabla.column('telefono', width=100, anchor=tk.CENTER)
        self.tabla.column('correo', width=150)
        self.tabla.column('puntos', width=80, anchor=tk.CENTER)
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
            command=self.cargar_clientes
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

        # Cargar clientes iniciales
        self.cargar_clientes()

    def cargar_clientes(self):
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT id_cliente, nombre, telefono, correo, puntos, fecha_registro FROM clientes ORDER BY nombre")

            for cliente in cursor.fetchall():
                self.tabla.insert('', tk.END, values=cliente)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los clientes: {str(e)}")

    def buscar_clientes(self):
        texto_busqueda = self.entry_buscar.get().strip()

        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        if not texto_busqueda:
            self.cargar_clientes()
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Búsqueda por nombre, teléfono o correo
            consulta = """
            SELECT id_cliente, nombre, telefono, correo, puntos, fecha_registro 
            FROM clientes 
            WHERE nombre LIKE %s OR telefono LIKE %s OR correo LIKE %s
            ORDER BY nombre
            """

            cursor.execute(consulta, (f"%{texto_busqueda}%", f"%{texto_busqueda}%", f"%{texto_busqueda}%"))

            for cliente in cursor.fetchall():
                self.tabla.insert('', tk.END, values=cliente)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar clientes: {str(e)}")

    def enviar_notificacion(self, tipo, destinatario, datos):
        """
        Envía una notificación al cliente según el tipo especificado.

        Args:
            tipo: Tipo de notificación ('alta', 'puntos', 'baja')
            destinatario: Diccionario con 'tipo' (correo/telefono) y 'valor'
            datos: Datos adicionales según el tipo de notificación
        """
        try:
            # Preparar datos comunes para cualquier tipo de notificación
            nombre_cliente = datos['nombre']

            # 1. ENVÍO POR CORREO ELECTRÓNICO
            if destinatario['tipo'] == 'correo' and destinatario['valor']:
                correo_cliente = destinatario['valor']

                # Intentamos usar el método más simple primero, que tiene menos probabilidades de error
                try:
                    # Importar función simple de envío
                    from email_sender_mejorado import enviar_correo_simple

                    # Preparar contenido del correo según el tipo
                    if tipo == 'alta':
                        asunto = "Bienvenido a Lavanderia"
                        cuerpo = "Hola " + nombre_cliente + ",\n\n"
                        cuerpo += "Has sido registrado exitosamente en nuestro sistema.\n"
                        cuerpo += "Tu cuenta ha sido creada con los siguientes datos:\n\n"
                        cuerpo += "Nombre: " + nombre_cliente + "\n"
                        cuerpo += "Correo: " + correo_cliente + "\n"
                        cuerpo += "Puntos iniciales: 0\n\n"
                        cuerpo += "Gracias por preferirnos!"
                    elif tipo == 'puntos':
                        asunto = "Actualizacion de Puntos"
                        cuerpo = "Hola " + nombre_cliente + ",\n\n"
                        cuerpo += "Tus puntos de fidelidad han sido actualizados.\n\n"
                        cuerpo += datos.get('mensaje', '') + "\n"
                        cuerpo += "Puntos actuales: " + str(datos.get('puntos_nuevos', 0)) + "\n\n"
                        cuerpo += "Motivo: " + datos.get('motivo', '') + "\n\n"
                        cuerpo += "Gracias por preferirnos!"
                    elif tipo == 'baja':
                        asunto = "Confirmacion de Baja"
                        cuerpo = "Hola " + nombre_cliente + ",\n\n"
                        cuerpo += "Te informamos que tu cuenta ha sido dada de baja en nuestro sistema.\n\n"
                        cuerpo += "Queremos agradecerte por haber sido cliente de nuestra lavanderia.\n"
                        cuerpo += "Si en algun momento deseas volver a utilizar nuestros servicios, siempre seras bienvenido.\n\n"
                        cuerpo += "Si consideras que esto ha sido un error, por favor contactanos.\n\n"
                        cuerpo += "Gracias por tu preferencia."

                    # Enviar correo simple (texto plano)
                    envio_exitoso = enviar_correo_simple(correo_cliente, asunto, cuerpo)

                    if envio_exitoso:
                        messagebox.showinfo("Correo enviado", f"Se envió notificación al correo {correo_cliente}")
                    else:
                        raise Exception("No se pudo enviar el correo simple")

                except Exception as simple_error:
                    # Si falla el método simple, probar con HTML
                    try:
                        from email_sender_mejorado import enviar_correo_html, obtener_plantilla_alta_cliente, \
                            obtener_plantilla_actualizacion_puntos, obtener_plantilla_baja_cliente

                        # Preparar contenido HTML según el tipo
                        if tipo == 'alta':
                            asunto = "Bienvenido a Lavanderia"
                            contenido_html = obtener_plantilla_alta_cliente(nombre_cliente, correo_cliente)
                        elif tipo == 'puntos':
                            asunto = "Actualizacion de Puntos"
                            contenido_html = obtener_plantilla_actualizacion_puntos(
                                nombre_cliente,
                                datos.get('mensaje', 'Se actualizaron tus puntos.'),
                                datos.get('puntos_nuevos', 0),
                                datos.get('motivo', 'Actualización de sistema')
                            )
                        elif tipo == 'baja':
                            asunto = "Confirmacion de Baja"
                            contenido_html = obtener_plantilla_baja_cliente(nombre_cliente)

                        # Enviar correo HTML
                        envio_html = enviar_correo_html(correo_cliente, asunto, contenido_html)

                        if envio_html:
                            messagebox.showinfo("Correo HTML enviado",
                                                f"Se envió notificación HTML al correo {correo_cliente}")
                        else:
                            raise Exception("Falló el envío de correo HTML")

                    except Exception as html_error:
                        # Mostrar error si fallan ambos métodos
                        messagebox.showwarning(
                            "Error al enviar correo",
                            f"No se pudo enviar correo a {correo_cliente}.\n"
                            f"Error: {str(html_error)}\n\n"
                            "Verifica la configuración en el archivo email_sender_mejorado.py"
                        )

            # 2. ENVÍO POR WHATSAPP
            if destinatario['tipo'] == 'telefono' and destinatario['valor']:
                numero_telefono = destinatario['valor']

                # Preparar mensaje según el tipo
                if tipo == 'alta':
                    mensaje_whatsapp = f"Hola {nombre_cliente}, has sido registrado exitosamente en nuestro sistema de lavanderia. Gracias por preferirnos!"
                elif tipo == 'puntos':
                    mensaje_whatsapp = f"Hola {nombre_cliente}, tus puntos han sido actualizados. {datos.get('mensaje', '')} Puntos actuales: {datos.get('puntos_nuevos', 0)}. Motivo: {datos.get('motivo', '')}"
                elif tipo == 'baja':
                    mensaje_whatsapp = f"Hola {nombre_cliente}, te informamos que tu cuenta ha sido dada de baja en nuestro sistema. Gracias por confiar en nosotros. Si deseas volver a registrarte, contactanos."
                else:
                    # Tipo de notificación no reconocido
                    return False

                try:
                    # Método directo mediante URL (no requiere instalación)
                    import webbrowser
                    import urllib.parse

                    # Limpiar y formatear número
                    numero_limpio = ''.join(c for c in numero_telefono if c.isdigit())

                    # Asegurar código de país
                    if len(numero_limpio) == 10:  # México - 10 dígitos
                        numero_completo = "52" + numero_limpio
                    else:
                        numero_completo = numero_limpio

                    # Codificar mensaje para URL
                    mensaje_codificado = urllib.parse.quote(mensaje_whatsapp)

                    # Construir URL y abrir
                    url = f"https://wa.me/{numero_completo}?text={mensaje_codificado}"

                    webbrowser.open(url)

                    messagebox.showinfo(
                        "WhatsApp",
                        f"Se ha abierto WhatsApp para enviar mensaje al número {numero_telefono}.\n"
                        "Complete el envío haciendo clic en el botón de enviar."
                    )

                except Exception as whatsapp_error:
                    messagebox.showwarning(
                        "Error WhatsApp",
                        f"No se pudo abrir WhatsApp: {str(whatsapp_error)}"
                    )

            # Si no hay datos de contacto, mostrar advertencia
            if (destinatario['tipo'] == 'correo' and not destinatario['valor']) or \
                    (destinatario['tipo'] == 'telefono' and not destinatario['valor']):
                messagebox.showwarning(
                    "Sin datos de contacto",
                    f"No se puede enviar notificación: no hay {destinatario['tipo']} registrado para {nombre_cliente}"
                )

        except Exception as e:
            messagebox.showwarning(
                "Error en notificación",
                f"No se pudo completar el envío de la notificación: {str(e)}"
            )

        return True

    def nuevo_cliente(self):
        # Crear una nueva ventana para añadir cliente
        ventana_nuevo = tk.Toplevel(self.ventana)
        ventana_nuevo.title("Nuevo Cliente")
        ventana_nuevo.geometry("500x400")
        ventana_nuevo.config(bg="#f0f4c3")
        ventana_nuevo.grab_set()  # Hacer modal

        # Frame para el formulario
        frame_form = tk.Frame(ventana_nuevo, bg="#f0f4c3")
        frame_form.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Título del formulario
        titulo = tk.Label(
            frame_form,
            text="Registro de Nuevo Cliente",
            font=("Helvetica", 14, "bold"),
            bg="#f0f4c3",
            fg="#33691e"
        )
        titulo.grid(row=0, column=0, columnspan=2, pady=10, sticky=tk.W)

        # Etiquetas y campos básicos (nombre siempre obligatorio)
        lbl_nombre = tk.Label(frame_form, text="Nombre:", font=("Helvetica", 12), bg="#f0f4c3")
        lbl_nombre.grid(row=1, column=0, sticky=tk.W, pady=5)

        entry_nombre = tk.Entry(frame_form, font=("Helvetica", 12))
        entry_nombre.grid(row=1, column=1, sticky=tk.W + tk.E, pady=5, padx=5)

        # Separador
        ttk.Separator(frame_form, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky=tk.E + tk.W, pady=10)

        # Variables para controlar el tipo de contacto
        tipo_contacto = tk.StringVar(value="ambos")

        # Frame para opciones de contacto
        frame_opciones = tk.Frame(frame_form, bg="#f0f4c3")
        frame_opciones.grid(row=3, column=0, columnspan=2, sticky=tk.W + tk.E, pady=5)

        lbl_contacto = tk.Label(
            frame_opciones,
            text="Información de contacto:",
            font=("Helvetica", 12, "bold"),
            bg="#f0f4c3"
        )
        lbl_contacto.pack(anchor=tk.W, pady=5)

        rb_ambos = tk.Radiobutton(
            frame_opciones,
            text="Registrar teléfono y correo",
            variable=tipo_contacto,
            value="ambos",
            bg="#f0f4c3",
            font=("Helvetica", 11)
        )
        rb_ambos.pack(anchor=tk.W)

        rb_telefono = tk.Radiobutton(
            frame_opciones,
            text="Solo registrar teléfono",
            variable=tipo_contacto,
            value="telefono",
            bg="#f0f4c3",
            font=("Helvetica", 11)
        )
        rb_telefono.pack(anchor=tk.W)

        rb_correo = tk.Radiobutton(
            frame_opciones,
            text="Solo registrar correo",
            variable=tipo_contacto,
            value="correo",
            bg="#f0f4c3",
            font=("Helvetica", 11)
        )
        rb_correo.pack(anchor=tk.W)

        # Campos de teléfono y correo
        frame_contacto = tk.Frame(frame_form, bg="#f0f4c3")
        frame_contacto.grid(row=4, column=0, columnspan=2, sticky=tk.W + tk.E, pady=10)

        lbl_telefono = tk.Label(frame_contacto, text="Teléfono:", font=("Helvetica", 12), bg="#f0f4c3")
        lbl_telefono.grid(row=0, column=0, sticky=tk.W, pady=5)

        entry_telefono = tk.Entry(frame_contacto, font=("Helvetica", 12))
        entry_telefono.grid(row=0, column=1, sticky=tk.W + tk.E, pady=5, padx=5)

        lbl_correo = tk.Label(frame_contacto, text="Correo:", font=("Helvetica", 12), bg="#f0f4c3")
        lbl_correo.grid(row=1, column=0, sticky=tk.W, pady=5)

        entry_correo = tk.Entry(frame_contacto, font=("Helvetica", 12))
        entry_correo.grid(row=1, column=1, sticky=tk.W + tk.E, pady=5, padx=5)

        # Opción para enviar notificación
        frame_notificacion = tk.Frame(frame_form, bg="#f0f4c3")
        frame_notificacion.grid(row=5, column=0, columnspan=2, sticky=tk.W + tk.E, pady=5)

        notificar = tk.BooleanVar(value=True)

        chk_notificar = tk.Checkbutton(
            frame_notificacion,
            text="Enviar notificación al cliente sobre su registro",
            variable=notificar,
            bg="#f0f4c3",
            font=("Helvetica", 11)
        )
        chk_notificar.pack(anchor=tk.W)

        # Botones
        frame_botones = tk.Frame(ventana_nuevo, bg="#f0f4c3")
        frame_botones.pack(pady=10)

        def actualizar_campos_contacto(*args):
            # Actualizar visibilidad de campos según el tipo de contacto seleccionado
            if tipo_contacto.get() == "telefono":
                entry_correo.config(state=tk.DISABLED)
                entry_telefono.config(state=tk.NORMAL)
            elif tipo_contacto.get() == "correo":
                entry_telefono.config(state=tk.DISABLED)
                entry_correo.config(state=tk.NORMAL)
            else:  # ambos
                entry_telefono.config(state=tk.NORMAL)
                entry_correo.config(state=tk.NORMAL)

        # Vincular la función al cambio de variable
        tipo_contacto.trace("w", actualizar_campos_contacto)

        def guardar_cliente():
            # Validar campos
            nombre = entry_nombre.get().strip()
            telefono = entry_telefono.get().strip()
            correo = entry_correo.get().strip()

            if not nombre:
                messagebox.showwarning("Campo incompleto", "El nombre del cliente es obligatorio")
                return

            # Validar según tipo de contacto seleccionado
            if tipo_contacto.get() == "telefono" and not telefono:
                messagebox.showwarning("Campo incompleto", "El teléfono es obligatorio con esta opción")
                return
            elif tipo_contacto.get() == "correo" and not correo:
                messagebox.showwarning("Campo incompleto", "El correo es obligatorio con esta opción")
                return
            elif tipo_contacto.get() == "ambos" and not telefono and not correo:
                messagebox.showwarning("Campo incompleto", "Debes proporcionar al menos un método de contacto")
                return

            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()

                # Insertar nuevo cliente con 0 puntos iniciales
                consulta = "INSERT INTO clientes (nombre, telefono, correo, puntos) VALUES (%s, %s, %s, 0)"
                cursor.execute(consulta, (nombre, telefono, correo))

                # Obtener el ID del cliente recién insertado
                cursor.execute("SELECT LAST_INSERT_ID()")
                id_cliente = cursor.fetchone()[0]

                conexion.commit()
                conexion.close()

                # Enviar notificación si está activada la opción
                if notificar.get():
                    datos_cliente = {
                        'nombre': nombre,
                        'id': id_cliente
                    }

                    # Enviar notificaciones por todos los canales disponibles
                    if telefono:
                        self.enviar_notificacion(
                            'alta',
                            {'tipo': 'telefono', 'valor': telefono},
                            datos_cliente
                        )

                    if correo:
                        self.enviar_notificacion(
                            'alta',
                            {'tipo': 'correo', 'valor': correo},
                            datos_cliente
                        )

                messagebox.showinfo("Éxito", "Cliente registrado correctamente")
                ventana_nuevo.destroy()
                self.cargar_clientes()  # Refrescar tabla
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo registrar el cliente: {str(e)}")

        btn_guardar = tk.Button(
            frame_botones,
            text="Guardar",
            font=("Helvetica", 12),
            bg="#558b2f",
            fg="white",
            command=guardar_cliente
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

        # Inicializar estado de los campos
        actualizar_campos_contacto()

    def editar_cliente(self):
        # Obtener el cliente seleccionado
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un cliente para editar")
            return

        # Obtener datos del cliente seleccionado
        valores = self.tabla.item(seleccion[0], 'values')
        id_cliente = valores[0]
        nombre_actual = valores[1]
        telefono_actual = valores[2]
        correo_actual = valores[3]

        # Crear ventana de edición
        ventana_editar = tk.Toplevel(self.ventana)
        ventana_editar.title("Editar Cliente")
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

        lbl_telefono = tk.Label(frame_form, text="Teléfono:", font=("Helvetica", 12), bg="#f0f4c3")
        lbl_telefono.grid(row=1, column=0, sticky=tk.W, pady=5)

        entry_telefono = tk.Entry(frame_form, font=("Helvetica", 12))
        entry_telefono.grid(row=1, column=1, sticky=tk.W + tk.E, pady=5, padx=5)
        entry_telefono.insert(0, telefono_actual if telefono_actual else "")

        lbl_correo = tk.Label(frame_form, text="Correo:", font=("Helvetica", 12), bg="#f0f4c3")
        lbl_correo.grid(row=2, column=0, sticky=tk.W, pady=5)

        entry_correo = tk.Entry(frame_form, font=("Helvetica", 12))
        entry_correo.grid(row=2, column=1, sticky=tk.W + tk.E, pady=5, padx=5)
        entry_correo.insert(0, correo_actual if correo_actual else "")

        # Botones
        frame_botones = tk.Frame(ventana_editar, bg="#f0f4c3")
        frame_botones.pack(pady=10)

        def actualizar_cliente():
            # Validar campos
            nuevo_nombre = entry_nombre.get().strip()
            nuevo_telefono = entry_telefono.get().strip()
            nuevo_correo = entry_correo.get().strip()

            if not nuevo_nombre:
                messagebox.showwarning("Campo incompleto", "El nombre del cliente es obligatorio")
                return

            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()

                # Actualizar cliente
                consulta = """
                UPDATE clientes SET nombre = %s, telefono = %s, correo = %s
                WHERE id_cliente = %s
                """
                cursor.execute(consulta, (nuevo_nombre, nuevo_telefono, nuevo_correo, id_cliente))

                conexion.commit()
                conexion.close()

                messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
                ventana_editar.destroy()
                self.cargar_clientes()  # Refrescar tabla
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el cliente: {str(e)}")

        btn_actualizar = tk.Button(
            frame_botones,
            text="Actualizar",
            font=("Helvetica", 12),
            bg="#558b2f",
            fg="white",
            command=actualizar_cliente
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

    def ver_historial(self):
        # Obtener el cliente seleccionado
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un cliente para ver su historial")
            return

        # Obtener datos del cliente seleccionado
        valores = self.tabla.item(seleccion[0], 'values')
        id_cliente = valores[0]
        nombre_cliente = valores[1]

        # Crear ventana para mostrar historial
        ventana_historial = tk.Toplevel(self.ventana)
        ventana_historial.title(f"Historial de {nombre_cliente}")
        ventana_historial.geometry("900x500")
        ventana_historial.config(bg="#f0f4c3")
        ventana_historial.grab_set()  # Hacer modal

        # Frame principal
        frame_principal = tk.Frame(ventana_historial, bg="#f0f4c3")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        titulo = tk.Label(
            frame_principal,
            text=f"Historial de servicios de {nombre_cliente}",
            font=("Helvetica", 16, "bold"),
            bg="#f0f4c3",
            fg="#33691e"
        )
        titulo.pack(pady=10)

        # Pestañas para mostrar pedidos y ventas
        notebook = ttk.Notebook(frame_principal)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Pestaña de pedidos
        tab_pedidos = tk.Frame(notebook, bg="#f0f4c3")
        notebook.add(tab_pedidos, text="Pedidos")

        # Tabla de pedidos
        columnas_pedidos = ('id', 'fecha', 'estado', 'observaciones')

        tabla_pedidos = ttk.Treeview(tab_pedidos, columns=columnas_pedidos, show='headings')

        # Configurar encabezados
        tabla_pedidos.heading('id', text='ID Pedido')
        tabla_pedidos.heading('fecha', text='Fecha')
        tabla_pedidos.heading('estado', text='Estado')
        tabla_pedidos.heading('observaciones', text='Observaciones')

        # Configurar anchos
        tabla_pedidos.column('id', width=80, anchor=tk.CENTER)
        tabla_pedidos.column('fecha', width=150, anchor=tk.CENTER)
        tabla_pedidos.column('estado', width=120, anchor=tk.CENTER)
        tabla_pedidos.column('observaciones', width=400)

        # Scrollbar para la tabla de pedidos
        scrollbar_pedidos = ttk.Scrollbar(tab_pedidos, orient=tk.VERTICAL, command=tabla_pedidos.yview)
        tabla_pedidos.configure(yscrollcommand=scrollbar_pedidos.set)

        # Empaquetar tabla y scrollbar
        tabla_pedidos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar_pedidos.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Pestaña de detalles
        tab_detalles = tk.Frame(notebook, bg="#f0f4c3")
        notebook.add(tab_detalles, text="Detalle de pedido")

        # Texto informativo
        lbl_info = tk.Label(
            tab_detalles,
            text="Selecciona un pedido en la pestaña anterior para ver sus detalles",
            font=("Helvetica", 12),
            bg="#f0f4c3"
        )
        lbl_info.pack(pady=20)

        # Tabla para detalles del pedido
        columnas_detalles = ('tipo', 'nombre', 'cantidad', 'precio')

        tabla_detalles = ttk.Treeview(tab_detalles, columns=columnas_detalles, show='headings')

        # Configurar encabezados
        tabla_detalles.heading('tipo', text='Tipo')
        tabla_detalles.heading('nombre', text='Descripción')
        tabla_detalles.heading('cantidad', text='Cantidad')
        tabla_detalles.heading('precio', text='Precio unit.')

        # Configurar anchos
        tabla_detalles.column('tipo', width=100, anchor=tk.CENTER)
        tabla_detalles.column('nombre', width=300)
        tabla_detalles.column('cantidad', width=100, anchor=tk.CENTER)
        tabla_detalles.column('precio', width=100, anchor=tk.CENTER)

        # Scrollbar para la tabla de detalles
        scrollbar_detalles = ttk.Scrollbar(tab_detalles, orient=tk.VERTICAL, command=tabla_detalles.yview)
        tabla_detalles.configure(yscrollcommand=scrollbar_detalles.set)

        # Empaquetar tabla y scrollbar
        tabla_detalles.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar_detalles.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Función para mostrar detalles del pedido seleccionado
        def mostrar_detalles_pedido(event):
            # Limpiar tabla de detalles
            for item in tabla_detalles.get_children():
                tabla_detalles.delete(item)

            # Obtener pedido seleccionado
            seleccion = tabla_pedidos.selection()

            if not seleccion:
                return

            # Obtener ID del pedido seleccionado
            id_pedido = tabla_pedidos.item(seleccion[0], 'values')[0]

            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()

                # Consultar detalles del pedido
                consulta_detalles = """
                SELECT dp.tipo_item, 
                       CASE 
                           WHEN dp.tipo_item = 'producto' THEN p.nombre
                           WHEN dp.tipo_item = 'servicio' THEN s.nombre
                       END as descripcion,
                       dp.cantidad, 
                       dp.precio_unitario
                FROM detalle_pedido dp
                LEFT JOIN productos p ON dp.tipo_item = 'producto' AND dp.id_item = p.id_producto
                LEFT JOIN servicios s ON dp.tipo_item = 'servicio' AND dp.id_item = s.id_servicio
                WHERE dp.id_pedido = %s
                """

                cursor.execute(consulta_detalles, (id_pedido,))

                for detalle in cursor.fetchall():
                    tabla_detalles.insert('', tk.END, values=detalle)

                conexion.close()

                # Cambiar a la pestaña de detalles
                notebook.select(1)

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar los detalles del pedido: {str(e)}")

        # Vincular evento de selección en la tabla de pedidos
        tabla_pedidos.bind('<<TreeviewSelect>>', mostrar_detalles_pedido)

        # Cargar pedidos del cliente
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Consultar pedidos del cliente
            consulta_pedidos = """
            SELECT id_pedido, fecha_pedido, estado, observaciones
            FROM pedidos
            WHERE id_cliente = %s
            ORDER BY fecha_pedido DESC
            """

            cursor.execute(consulta_pedidos, (id_cliente,))

            for pedido in cursor.fetchall():
                tabla_pedidos.insert('', tk.END, values=pedido)

            conexion.close()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el historial de pedidos: {str(e)}")

        # Botón para volver
        btn_volver = tk.Button(
            frame_principal,
            text="Volver",
            font=("Helvetica", 12),
            bg="#c62828",
            fg="white",
            command=ventana_historial.destroy
        )
        btn_volver.pack(pady=10)

    def gestionar_puntos(self):
        # Obtener el cliente seleccionado
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un cliente para gestionar sus puntos")
            return

        # Obtener datos del cliente seleccionado
        valores = self.tabla.item(seleccion[0], 'values')
        id_cliente = valores[0]
        nombre_cliente = valores[1]
        puntos_actuales = int(valores[4])

        # Crear ventana para gestionar puntos
        ventana_puntos = tk.Toplevel(self.ventana)
        ventana_puntos.title(f"Gestionar Puntos - {nombre_cliente}")
        ventana_puntos.geometry("400x300")
        ventana_puntos.config(bg="#f0f4c3")
        ventana_puntos.grab_set()  # Hacer modal

        # Frame para el contenido
        frame_contenido = tk.Frame(ventana_puntos, bg="#f0f4c3")
        frame_contenido.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Información del cliente
        lbl_cliente = tk.Label(
            frame_contenido,
            text=f"Cliente: {nombre_cliente}",
            font=("Helvetica", 14, "bold"),
            bg="#f0f4c3"
        )
        lbl_cliente.pack(anchor=tk.W, pady=5)

        lbl_puntos = tk.Label(
            frame_contenido,
            text=f"Puntos actuales: {puntos_actuales}",
            font=("Helvetica", 12),
            bg="#f0f4c3"
        )
        lbl_puntos.pack(anchor=tk.W, pady=5)

        # Separador
        ttk.Separator(frame_contenido, orient='horizontal').pack(fill=tk.X, pady=10)

        # Frame para ajustar puntos
        frame_ajuste = tk.Frame(frame_contenido, bg="#f0f4c3")
        frame_ajuste.pack(fill=tk.X, pady=10)

        # Opciones para sumar o restar puntos
        operacion = tk.StringVar(value="sumar")

        rb_sumar = tk.Radiobutton(
            frame_ajuste,
            text="Sumar puntos",
            variable=operacion,
            value="sumar",
            bg="#f0f4c3",
            font=("Helvetica", 11)
        )
        rb_sumar.pack(anchor=tk.W)

        rb_restar = tk.Radiobutton(
            frame_ajuste,
            text="Restar puntos",
            variable=operacion,
            value="restar",
            bg="#f0f4c3",
            font=("Helvetica", 11)
        )
        rb_restar.pack(anchor=tk.W)

        # Frame para la cantidad
        frame_cantidad = tk.Frame(frame_contenido, bg="#f0f4c3")
        frame_cantidad.pack(fill=tk.X, pady=10)

        lbl_cantidad = tk.Label(
            frame_cantidad,
            text="Cantidad:",
            font=("Helvetica", 12),
            bg="#f0f4c3"
        )
        lbl_cantidad.pack(side=tk.LEFT, padx=5)

        entry_cantidad = tk.Entry(frame_cantidad, font=("Helvetica", 12), width=10)
        entry_cantidad.pack(side=tk.LEFT, padx=5)

        # Motivo del ajuste
        frame_motivo = tk.Frame(frame_contenido, bg="#f0f4c3")
        frame_motivo.pack(fill=tk.X, pady=10)

        lbl_motivo = tk.Label(
            frame_motivo,
            text="Motivo:",
            font=("Helvetica", 12),
            bg="#f0f4c3"
        )
        lbl_motivo.pack(side=tk.LEFT, padx=5)

        entry_motivo = tk.Entry(frame_motivo, font=("Helvetica", 12))
        entry_motivo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Opción para enviar notificación
        frame_notificar = tk.Frame(frame_contenido, bg="#f0f4c3")
        frame_notificar.pack(fill=tk.X, pady=5)

        notificar = tk.BooleanVar(value=True)

        chk_notificar = tk.Checkbutton(
            frame_notificar,
            text="Notificar al cliente sobre el cambio",
            variable=notificar,
            bg="#f0f4c3",
            font=("Helvetica", 11)
        )
        chk_notificar.pack(anchor=tk.W)

        # Botones
        frame_botones = tk.Frame(ventana_puntos, bg="#f0f4c3")
        frame_botones.pack(pady=10)

        def aplicar_ajuste_puntos():
            try:
                cantidad = int(entry_cantidad.get().strip())
                if cantidad <= 0:
                    messagebox.showwarning("Valor inválido", "La cantidad debe ser un número positivo")
                    return

                motivo = entry_motivo.get().strip()
                if not motivo:
                    messagebox.showwarning("Campo requerido", "Por favor ingresa un motivo para el ajuste")
                    return

                # Calcular nuevos puntos
                if operacion.get() == "sumar":
                    nuevos_puntos = puntos_actuales + cantidad
                    mensaje_cambio = f"Se agregaron {cantidad} puntos."
                else:  # restar
                    nuevos_puntos = puntos_actuales - cantidad
                    if nuevos_puntos < 0:
                        messagebox.showwarning(
                            "Puntos insuficientes",
                            f"El cliente solo tiene {puntos_actuales} puntos disponibles"
                        )
                        return
                    mensaje_cambio = f"Se descontaron {cantidad} puntos."

                conexion = conectar_bd()
                cursor = conexion.cursor()

                # Actualizar puntos del cliente
                cursor.execute(
                    "UPDATE clientes SET puntos = %s WHERE id_cliente = %s",
                    (nuevos_puntos, id_cliente)
                )

                # Obtener información de contacto del cliente
                cursor.execute(
                    "SELECT telefono, correo FROM clientes WHERE id_cliente = %s",
                    (id_cliente,)
                )
                telefono, correo = cursor.fetchone()

                conexion.commit()
                conexion.close()

                # Enviar notificación si está marcada la opción
                if notificar.get():
                    datos_notificacion = {
                        'nombre': nombre_cliente,
                        'mensaje': mensaje_cambio,
                        'puntos_nuevos': nuevos_puntos,
                        'motivo': motivo
                    }

                    # Enviar notificaciones por todos los canales disponibles
                    if telefono:
                        self.enviar_notificacion(
                            'puntos',
                            {'tipo': 'telefono', 'valor': telefono},
                            datos_notificacion
                        )

                    if correo:
                        self.enviar_notificacion(
                            'puntos',
                            {'tipo': 'correo', 'valor': correo},
                            datos_notificacion
                        )

                messagebox.showinfo("Éxito", f"{mensaje_cambio} Nuevos puntos: {nuevos_puntos}")
                ventana_puntos.destroy()
                self.cargar_clientes()  # Refrescar tabla

            except ValueError:
                messagebox.showwarning("Valor inválido", "Por favor ingresa un número entero")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo ajustar los puntos: {str(e)}")

        # Botón Aplicar
        btn_aplicar = tk.Button(
            frame_botones,
            text="Aplicar",
            font=("Helvetica", 12),
            bg="#558b2f",
            fg="white",
            command=aplicar_ajuste_puntos
        )
        btn_aplicar.pack(side=tk.LEFT, padx=5)

        # Botón Aceptar (funcionalidad idéntica a Aplicar)
        btn_aceptar = tk.Button(
            frame_botones,
            text="Aceptar",
            font=("Helvetica", 12),
            bg="#558b2f",
            fg="white",
            command=aplicar_ajuste_puntos
        )
        btn_aceptar.pack(side=tk.LEFT, padx=5)

        # Botón Cancelar
        btn_cancelar = tk.Button(
            frame_botones,
            text="Cancelar",
            font=("Helvetica", 12),
            bg="#c62828",
            fg="white",
            command=ventana_puntos.destroy
        )
        btn_cancelar.pack(side=tk.LEFT, padx=5)

        # Vincular la tecla Enter para aplicar los cambios
        entry_cantidad.bind("<Return>", lambda event: aplicar_ajuste_puntos())
        entry_motivo.bind("<Return>", lambda event: aplicar_ajuste_puntos())

        # Asegurarnos que los botones sean visibles
        frame_botones.update()

    def eliminar_cliente(self):
        # Obtener el cliente seleccionado
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un cliente para eliminar")
            return

        # Obtener datos del cliente seleccionado
        valores = self.tabla.item(seleccion[0], 'values')
        id_cliente = valores[0]
        nombre_cliente = valores[1]

        # Confirmar eliminación
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de eliminar al cliente '{nombre_cliente}'?"
        )

        if not confirmacion:
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Obtener información de contacto para enviar notificación
            cursor.execute("SELECT telefono, correo FROM clientes WHERE id_cliente = %s", (id_cliente,))
            telefono, correo = cursor.fetchone()

            # Verificar si el cliente tiene pedidos o ventas asociadas
            cursor.execute("""
                SELECT COUNT(*) FROM pedidos WHERE id_cliente = %s
                UNION ALL
                SELECT COUNT(*) FROM ventas WHERE id_cliente = %s
            """, (id_cliente, id_cliente))

            resultados = cursor.fetchall()

            if resultados[0][0] > 0 or (len(resultados) > 1 and resultados[1][0] > 0):
                messagebox.showwarning(
                    "No se puede eliminar",
                    "Este cliente tiene pedidos o ventas asociadas y no puede eliminarse."
                )
                return

            # Eliminar cliente
            cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))

            conexion.commit()
            conexion.close()

            # Enviar notificación de baja
            if correo or telefono:
                # Preparar datos para la notificación
                datos_cliente = {
                    'nombre': nombre_cliente,
                    'id': id_cliente
                }

                # Enviar notificación por correo si hay correo disponible
                if correo:
                    self.enviar_notificacion(
                        'baja',
                        {'tipo': 'correo', 'valor': correo},
                        datos_cliente
                    )

                # Enviar notificación por WhatsApp si hay teléfono disponible
                if telefono:
                    self.enviar_notificacion(
                        'baja',
                        {'tipo': 'telefono', 'valor': telefono},
                        datos_cliente
                    )

            messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
            self.cargar_clientes()  # Refrescar tabla
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el cliente: {str(e)}")


# Para probar de forma independiente
if __name__ == "__main__":
    GestionClientes()