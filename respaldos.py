lbl_instrucciones = tk.Label(
    frame_instrucciones,
    text="Seleccione un respaldo de la lista o utilice un archivo SQL externo para restaurar la base de datos.",
    font=("Helvetica", 12),
    bg="#f5f5f5",
    justify=tk.LEFT,
    wraplength=700
)
lbl_instrucciones.pack(anchor=tk.W, pady=5)

lbl_advertencia = tk.Label(
    frame_instrucciones,
    text="⚠️ ADVERTENCIA: La restauración sobrescribirá TODOS los datos actuales. Asegúrese de crear un respaldo antes de continuar.",
    font=("Helvetica", 12, "bold"),
    bg="#ffecb3",
    fg="#e65100",
    padx=10,
    pady=10,
    wraplength=700
)
lbl_advertencia.pack(fill=tk.X, pady=10)

# Frame para selección de respaldo
frame_seleccion = tk.Frame(self.tab_restauracion, bg="#f5f5f5", padx=20)
frame_seleccion.pack(fill=tk.BOTH, expand=True)

# Opción 1: Restaurar desde respaldo interno
lbl_opcion1 = tk.Label(
    frame_seleccion,
    text="Opción 1: Restaurar desde respaldo interno",
    font=("Helvetica", 12, "bold"),
    bg="#f5f5f5"
)
lbl_opcion1.pack(anchor=tk.W, pady=10)

# Combobox con lista de respaldos
frame_respaldos = tk.Frame(frame_seleccion, bg="#f5f5f5")
frame_respaldos.pack(fill=tk.X, pady=5)

lbl_respaldo = tk.Label(
    frame_respaldos,
    text="Seleccionar respaldo:",
    font=("Helvetica", 11),
    bg="#f5f5f5"
)
lbl_respaldo.pack(side=tk.LEFT, padx=5)

self.var_respaldo = tk.StringVar()
self.combo_respaldos = ttk.Combobox(
    frame_respaldos,
    textvariable=self.var_respaldo,
    font=("Helvetica", 11),
    width=40,
    state="readonly"
)
self.combo_respaldos.pack(side=tk.LEFT, padx=5)

btn_restaurar_interno = tk.Button(
    frame_respaldos,
    text="Restaurar",
    font=("Helvetica", 11),
    bg="#ff9800",
    fg="white",
    command=self.restaurar_desde_interno
)
btn_restaurar_interno.pack(side=tk.LEFT, padx=20)

# Opción 2: Restaurar desde archivo externo
lbl_opcion2 = tk.Label(
    frame_seleccion,
    text="Opción 2: Restaurar desde archivo SQL externo",
    font=("Helvetica", 12, "bold"),
    bg="#f5f5f5"
)
lbl_opcion2.pack(anchor=tk.W, pady=10)

frame_archivo = tk.Frame(frame_seleccion, bg="#f5f5f5")
frame_archivo.pack(fill=tk.X, pady=5)

lbl_archivo = tk.Label(
    frame_archivo,
    text="Archivo SQL:",
    font=("Helvetica", 11),
    bg="#f5f5f5"
)
lbl_archivo.pack(side=tk.LEFT, padx=5)

self.var_archivo = tk.StringVar()
entry_archivo = tk.Entry(
    frame_archivo,
    textvariable=self.var_archivo,
    font=("Helvetica", 11),
    width=40
)
entry_archivo.pack(side=tk.LEFT, padx=5)

btn_examinar = tk.Button(
    frame_archivo,
    text="Examinar",
    font=("Helvetica", 11),
    command=self.seleccionar_archivo_sql
)
btn_examinar.pack(side=tk.LEFT, padx=5)

btn_restaurar_externo = tk.Button(
    frame_archivo,
    text="Restaurar",
    font=("Helvetica", 11),
    bg="#ff9800",
    fg="white",
    command=self.restaurar_desde_externo
)
btn_restaurar_externo.pack(side=tk.LEFT, padx=20)

# Cargar lista de respaldos
self.actualizar_lista_respaldos()


def cargar_historial_respaldos(self):
    """Carga el historial de respaldos en la tabla"""
    # Limpiar tabla
    for item in self.tabla_respaldos.get_children():
        self.tabla_respaldos.delete(item)

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        consulta = """
                SELECT r.id_respaldo, r.fecha_hora, r.tamanio, u.nombre, r.ruta
                FROM respaldos r
                LEFT JOIN usuarios u ON r.id_usuario = u.id_usuario
                ORDER BY r.fecha_hora DESC
            """

        cursor.execute(consulta)
        respaldos = cursor.fetchall()

        for respaldo in respaldos:
            id_respaldo, fecha_hora, tamanio, usuario, ruta = respaldo

            # Formatear fecha y tamaño
            fecha_formateada = utl.formatear_fecha(fecha_hora, '%d/%m/%Y %H:%M:%S')
            tamanio_formateado = self.formatear_tamanio(tamanio)

            self.tabla_respaldos.insert('', tk.END, values=(
                id_respaldo,
                fecha_formateada,
                tamanio_formateado,
                usuario or "Sistema",
                ruta
            ))

        conexion.close()

    except Exception as e:
        print(f"Error al cargar historial de respaldos: {e}")


def formatear_tamanio(self, tamanio):
    """Formatea el tamaño del archivo en unidades legibles"""
    if tamanio is None:
        return "Desconocido"

    # Convertir a KB, MB, GB según corresponda
    if tamanio < 1024:
        return f"{tamanio} bytes"
    elif tamanio < 1024 ** 2:
        return f"{tamanio / 1024:.2f} KB"
    elif tamanio < 1024 ** 3:
        return f"{tamanio / (1024 ** 2):.2f} MB"
    else:
        return f"{tamanio / (1024 ** 3):.2f} GB"


def crear_respaldo_manual(self):
    """Crea un respaldo manual de la base de datos"""
    # Preguntar por descripción opcional
    descripcion = simpledialog.askstring(
        "Descripción del respaldo",
        "Ingrese una descripción para este respaldo (opcional):",
        parent=self.ventana
    )

    # Preguntar por ubicación personalizada
    guardar_en = messagebox.askyesno(
        "Ubicación",
        "¿Desea guardar el respaldo en una ubicación personalizada?\n\n"
        "De lo contrario, se guardará en la carpeta predeterminada."
    )

    ruta_respaldo = None
    if guardar_en:
        ruta_respaldo = filedialog.askdirectory(
            title="Seleccione la carpeta para guardar el respaldo"
        )
        if not ruta_respaldo:  # Usuario canceló
            ruta_respaldo = None

    # Mostrar diálogo de progreso
    ventana_progreso = tk.Toplevel(self.ventana)
    ventana_progreso.title("Creando respaldo")
    ventana_progreso.geometry("300x100")
    utl.centrar_ventana(ventana_progreso, 300, 100)
    ventana_progreso.resizable(False, False)
    ventana_progreso.transient(self.ventana)
    ventana_progreso.grab_set()

    lbl_progreso = tk.Label(
        ventana_progreso,
        text="Creando respaldo, por favor espere...",
        font=("Helvetica", 12)
    )
    lbl_progreso.pack(pady=20)

    barra_progreso = ttk.Progressbar(
        ventana_progreso,
        mode='indeterminate'
    )
    barra_progreso.pack(fill=tk.X, padx=20)
    barra_progreso.start(10)

    # Actualizar la interfaz
    self.ventana.update()

    # Crear respaldo en un hilo aparte para no bloquear la interfaz
    def crear_respaldo_thread():
        resultado = self.crear_respaldo(ruta_respaldo, descripcion)

        # Cerrar ventana de progreso
        ventana_progreso.destroy()

        if resultado:
            messagebox.showinfo(
                "Éxito",
                f"El respaldo se ha creado correctamente.\n"
                f"Ubicación: {resultado}"
            )

            # Actualizar la lista de respaldos
            self.cargar_historial_respaldos()
            self.actualizar_lista_respaldos()
        else:
            messagebox.showerror(
                "Error",
                "No se pudo crear el respaldo. Verifique los permisos y la configuración."
            )

    # Iniciar hilo
    threading.Thread(target=crear_respaldo_thread).start()


def crear_respaldo(self, ruta_personalizada=None, descripcion=None):
    """
    Crea un respaldo de la base de datos

    Args:
        ruta_personalizada: Ruta donde guardar el respaldo
        descripcion: Descripción del respaldo

    Returns:
        str: Ruta del archivo de respaldo creado, o None si hubo errores
    """
    try:
        # Obtener configuración
        config = self.config_db

        # Nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"respaldo_{config['database']}_{timestamp}.sql"

        # Determinar ruta de guardado
        if ruta_personalizada:
            ruta_completa = os.path.join(ruta_personalizada, nombre_archivo)
        else:
            ruta_completa = os.path.join(self.directorio_respaldos, nombre_archivo)

        # Comando para mysqldump
        comando = [
            "mysqldump",
            f"--host={config['host']}",
            f"--user={config['user']}",
            f"--password={config['password']}",
            "--databases", config['database'],
            "--add-drop-database",
            "--routines",
            "--events",
            "--triggers",
            "--single-transaction",
            f"--result-file={ruta_completa}"
        ]

        # Ejecutar comando
        resultado = subprocess.run(comando, capture_output=True, text=True)

        if resultado.returncode != 0:
            print(f"Error en mysqldump: {resultado.stderr}")
            return None

        # Verificar si el archivo se creó correctamente
        if not os.path.exists(ruta_completa):
            print("El archivo de respaldo no se creó")
            return None

        # Obtener tamaño del archivo
        tamanio_archivo = os.path.getsize(ruta_completa)

        # Registrar en la base de datos
        conexion = conectar_bd()
        cursor = conexion.cursor()

        consulta = """
                INSERT INTO respaldos (fecha_hora, ruta, tamanio, id_usuario, descripcion)
                VALUES (%s, %s, %s, %s, %s)
            """

        cursor.execute(consulta, (
            datetime.now(),
            ruta_completa,
            tamanio_archivo,
            self.id_usuario,
            descripcion
        ))

        conexion.commit()
        conexion.close()

        return ruta_completa

    except Exception as e:
        print(f"Error al crear respaldo: {e}")
        return None


def abrir_ubicacion_respaldo(self):
    """Abre el explorador de archivos en la ubicación del respaldo seleccionado"""
    seleccion = self.tabla_respaldos.selection()

    if not seleccion:
        messagebox.showwarning("Selección requerida", "Por favor, seleccione un respaldo")
        return

    # Obtener ruta del respaldo seleccionado
    valores = self.tabla_respaldos.item(seleccion[0], "values")
    ruta = valores[4]

    # Verificar si existe
    if not os.path.exists(ruta):
        messagebox.showerror(
            "Archivo no encontrado",
            "El archivo de respaldo no existe en la ubicación especificada."
        )
        return

    # Abrir el explorador en la carpeta contenedora
    carpeta = os.path.dirname(ruta)
    try:
        os.startfile(carpeta)
    except:
        # Alternativa para Linux o Mac
        try:
            subprocess.run(["xdg-open", carpeta])
        except:
            messagebox.showerror(
                "Error",
                "No se pudo abrir la ubicación del respaldo."
            )


def exportar_respaldo(self):
    """Exporta el respaldo seleccionado a otra ubicación"""
    seleccion = self.tabla_respaldos.selection()

    if not seleccion:
        messagebox.showwarning("Selección requerida", "Por favor, seleccione un respaldo")
        return

    # Obtener ruta del respaldo seleccionado
    valores = self.tabla_respaldos.item(seleccion[0], "values")
    ruta_original = valores[4]

    # Verificar si existe
    if not os.path.exists(ruta_original):
        messagebox.showerror(
            "Archivo no encontrado",
            "El archivo de respaldo no existe en la ubicación especificada."
        )
        return

    # Solicitar nueva ubicación
    nombre_archivo = os.path.basename(ruta_original)
    ruta_destino = filedialog.asksaveasfilename(
        title="Guardar respaldo como",
        initialfile=nombre_archivo,
        defaultextension=".sql",
        filetypes=[("Archivos SQL", "*.sql")]
    )

    if not ruta_destino:  # Usuario canceló
        return

    # Copiar archivo
    try:
        shutil.copy2(ruta_original, ruta_destino)
        messagebox.showinfo(
            "Éxito",
            f"El respaldo ha sido exportado correctamente a:\n{ruta_destino}"
        )
    except Exception as e:
        messagebox.showerror(
            "Error",
            f"No se pudo exportar el respaldo: {str(e)}"
        )


def eliminar_respaldo(self):
    """Elimina el respaldo seleccionado"""
    seleccion = self.tabla_respaldos.selection()

    if not seleccion:
        messagebox.showwarning("Selección requerida", "Por favor, seleccione un respaldo")
        return

    # Confirmar eliminación
    confirmar = messagebox.askyesno(
        "Confirmar eliminación",
        "¿Está seguro de que desea eliminar este respaldo?\n"
        "Esta acción no se puede deshacer.",
        icon='warning'
    )

    if not confirmar:
        return

    # Obtener ID y ruta del respaldo seleccionado
    valores = self.tabla_respaldos.item(seleccion[0], "values")
    id_respaldo = valores[0]
    ruta = valores[4]

    try:
        # Eliminar archivo físico si existe
        if os.path.exists(ruta):
            os.remove(ruta)

        # Eliminar registro de la base de datos
        conexion = conectar_bd()
        cursor = conexion.cursor()

        consulta = "DELETE FROM respaldos WHERE id_respaldo = %s"
        cursor.execute(consulta, (id_respaldo,))

        conexion.commit()
        conexion.close()

        messagebox.showinfo(
            "Éxito",
            "El respaldo ha sido eliminado correctamente."
        )

        # Actualizar la lista de respaldos
        self.cargar_historial_respaldos()
        self.actualizar_lista_respaldos()

    except Exception as e:
        messagebox.showerror(
            "Error",
            f"No se pudo eliminar el respaldo: {str(e)}"
        )


def actualizar_opciones_frecuencia(self):
    """Actualiza la visibilidad de opciones según la frecuencia seleccionada"""
    frecuencia = self.var_frecuencia.get()

    # Obtener widgets por su grid_info
    for widget in self.tab_programacion.winfo_children():
        if widget.winfo_class() == 'Frame':
            for child in widget.winfo_children():
                if hasattr(child, 'grid_info'):
                    info = child.grid_info()
                    if info:  # Si está en el grid
                        # Mostrar/ocultar opciones de día de la semana
                        if 'row' in info and info['row'] == 4:
                            if frecuencia == 'semanal':
                                child.grid()
                            else:
                                child.grid_remove()

                        # Mostrar/ocultar opciones de día del mes
                        if 'row' in info and info['row'] == 5:
                            if frecuencia == 'mensual':
                                child.grid()
                            else:
                                child.grid_remove()


def seleccionar_ruta_respaldo(self):
    """Abre diálogo para seleccionar ruta de respaldos automáticos"""
    ruta = filedialog.askdirectory(
        title="Seleccione la carpeta para respaldos automáticos"
    )

    if ruta:  # Si el usuario no canceló
        self.var_ruta.set(ruta)


def guardar_configuracion_respaldos(self):
    """Guarda la configuración de respaldos programados"""
    try:
        # Actualizar configuración con valores actuales
        self.config_respaldos["activo"] = self.var_activo.get()
        self.config_respaldos["frecuencia"] = self.var_frecuencia.get()
        self.config_respaldos["hora"] = self.var_hora.get()
        self.config_respaldos["dia_semana"] = self.var_dia_semana.get()
        self.config_respaldos["dia_mes"] = self.var_dia_mes.get()
        self.config_respaldos["mantener_ultimos"] = self.var_mantener.get()
        self.config_respaldos["ruta_personalizada"] = self.var_ruta.get()

        # Validar formato de hora
        hora = self.config_respaldos["hora"]
        try:
            horas, minutos = hora.split(":")
            int(horas)
            int(minutos)
        except:
            messagebox.showwarning(
                "Formato incorrecto",
                "El formato de hora debe ser HH:MM (ejemplo: 23:30)"
            )
            return False

        # Guardar en archivo
        if self.guardar_config_respaldos():
            # Actualizar programación
            self.actualizar_estado_programacion()

            messagebox.showinfo(
                "Éxito",
                "La configuración de respaldos automáticos ha sido guardada correctamente."
            )
            return True
        else:
            messagebox.showerror(
                "Error",
                "No se pudo guardar la configuración."
            )
            return False

    except Exception as e:
        messagebox.showerror(
            "Error",
            f"Error al guardar la configuración: {str(e)}"
        )
        return False


def actualizar_estado_programacion(self):
    """Actualiza el estado de la programación de respaldos"""
    # Detener hilo de programación existente si hay uno
    if self.thread_programacion and self.thread_programacion.is_alive():
        self.seguir_ejecutando = False
        self.thread_programacion.join(timeout=1)

    # Si se activa la programación, iniciar un nuevo hilo
    if self.var_activo.get():
        self.seguir_ejecutando = True
        self.thread_programacion = threading.Thread(target=self.ejecutar_programacion)
        self.thread_programacion.daemon = True
        self.thread_programacion.start()


def ejecutar_programacion(self):
    """Función que corre en un hilo para mantener la programación de respaldos"""
    # Limpiar programación existente
    schedule.clear()

    # Configurar programación según frecuencia
    frecuencia = self.var_frecuencia.get()
    hora = self.var_hora.get()

    if frecuencia == "diaria":
        schedule.every().day.at(hora).do(self.ejecutar_respaldo_automatico)

    elif frecuencia == "semanal":
        dia = int(self.var_dia_semana.get())
        dias = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        getattr(schedule.every(), dias[dia]).at(hora).do(self.ejecutar_respaldo_automatico)

    elif frecuencia == "mensual":
        dia = int(self.var_dia_mes.get())

        # No hay un método directo para programar mensualmente, usar un manejador personalizado
        def deberia_ejecutar_mensual():
            ahora = datetime.now()
            return ahora.day == dia

        schedule.every().day.at(hora).do(
            lambda: self.ejecutar_respaldo_automatico() if deberia_ejecutar_mensual() else None
        )

    # Bucle principal de programación
    while self.seguir_ejecutando:
        schedule.run_pending()
        time.sleep(60)  # Verificar cada minuto


def ejecutar_respaldo_automatico(self):
    """Ejecuta el respaldo programado automáticamente"""
    try:
        # Determinar ruta
        ruta_personalizada = self.config_respaldos["ruta_personalizada"]
        if not ruta_personalizada or not os.path.exists(ruta_personalizada):
            ruta_personalizada = None

        # Crear respaldo
        resultado = self.crear_respaldo(
            ruta_personalizada,
            "Respaldo automático programado"
        )

        # Actualizar último respaldo
        if resultado:
            self.config_respaldos["ultimo_respaldo"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self.guardar_config_respaldos()

            # Actualizar etiqueta si la ventana está abierta
            if hasattr(self, 'lbl_ultimo_respaldo'):
                self.lbl_ultimo_respaldo.config(text=self.config_respaldos["ultimo_respaldo"])

            # Eliminar respaldos antiguos si es necesario
            self.limpiar_respaldos_antiguos()

        return resultado

    except Exception as e:
        print(f"Error en respaldo automático: {e}")
        return None


def limpiar_respaldos_antiguos(self):
    """Elimina respaldos antiguos según la configuración"""
    try:
        mantener = self.config_respaldos["mantener_ultimos"]

        # Obtener lista de respaldos ordenados por fecha
        conexion = conectar_bd()
        cursor = conexion.cursor()

        consulta = """
                SELECT id_respaldo, ruta, fecha_hora
                FROM respaldos
                ORDER BY fecha_hora DESC
            """

        cursor.execute(consulta)
        respaldos = cursor.fetchall()

        # Si hay más respaldos que el límite, eliminar los más antiguos
        if len(respaldos) > mantener:
            for respaldo in respaldos[mantener:]:
                id_respaldo, ruta, _ = respaldo

                # Eliminar archivo físico si existe
                if os.path.exists(ruta):
                    os.remove(ruta)

                # Eliminar registro de la base de datos
                cursor.execute("DELETE FROM respaldos WHERE id_respaldo = %s", (id_respaldo,))

            conexion.commit()

        conexion.close()

    except Exception as e:
        print(f"Error al limpiar respaldos antiguos: {e}")


def probar_configuracion(self):
    """Prueba la configuración de respaldos programados"""
    # Primero guardar la configuración
    if not self.guardar_configuracion_respaldos():
        return

    # Preguntar al usuario si desea crear un respaldo de prueba
    confirmar = messagebox.askyesno(
        "Confirmar prueba",
        "Esta operación creará un respaldo de prueba con la configuración actual.\n"
        "¿Desea continuar?"
    )

    if not confirmar:
        return

    # Mostrar diálogo de progreso
    ventana_progreso = tk.Toplevel(self.ventana)
    ventana_progreso.title("Prueba de configuración")
    ventana_progreso.geometry("300x100")
    utl.centrar_ventana(ventana_progreso, 300, 100)
    ventana_progreso.resizable(False, False)
    ventana_progreso.transient(self.ventana)
    ventana_progreso.grab_set()

    lbl_progreso = tk.Label(
        ventana_progreso,
        text="Creando respaldo de prueba...",
        font=("Helvetica", 12)
    )
    lbl_progreso.pack(pady=20)

    barra_progreso = ttk.Progressbar(
        ventana_progreso,
        mode='indeterminate'
    )
    barra_progreso.pack(fill=tk.X, padx=20)
    barra_progreso.start(10)

    # Actualizar la interfaz
    self.ventana.update()

    # Crear respaldo en un hilo aparte
    def probar_thread():
        # Determinar ruta
        ruta_personalizada = self.config_respaldos["ruta_personalizada"]
        if not ruta_personalizada or not os.path.exists(ruta_personalizada):
            ruta_personalizada = None

        # Crear respaldo
        resultado = self.crear_respaldo(
            ruta_personalizada,
            "Respaldo de prueba de configuración"
        )

        # Cerrar ventana de progreso
        ventana_progreso.destroy()

        if resultado:
            messagebox.showinfo(
                "Éxito",
                f"La prueba de configuración ha sido exitosa.\n"
                f"Se ha creado un respaldo en:\n{resultado}"
            )

            # Actualizar listas
            self.cargar_historial_respaldos()
            self.actualizar_lista_respaldos()
        else:
            messagebox.showerror(
                "Error",
                "La prueba ha fallado. Verifique los permisos y la configuración."
            )

    # Iniciar hilo
    threading.Thread(target=probar_thread).start()


def actualizar_lista_respaldos(self):
    """Actualiza la lista de respaldos disponibles para restauración"""
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        consulta = """
                SELECT id_respaldo, DATE_FORMAT(fecha_hora, '%d/%m/%Y %H:%i:%s') as fecha, ruta
                FROM respaldos
                ORDER BY fecha_hora DESC
            """

        cursor.execute(consulta)
        respaldos = cursor.fetchall()

        # Preparar lista para combobox
        lista_respaldos = []
        for respaldo in respaldos:
            id_respaldo, fecha, ruta = respaldo
            lista_respaldos.append(f"{id_respaldo} - {fecha} - {os.path.basename(ruta)}")

        # Actualizar combobox
        self.combo_respaldos['values'] = lista_respaldos
        if lista_respaldos:
            self.combo_respaldos.current(0)

        conexion.close()

    except Exception as e:
        print(f"Error al actualizar lista de respaldos: {e}")


def seleccionar_archivo_sql(self):
    """Abre diálogo para seleccionar archivo SQL externo"""
    archivo = filedialog.askopenfilename(
        title="Seleccionar archivo SQL",
        filetypes=[("Archivos SQL", "*.sql")]
    )

    if archivo:  # Si el usuario no canceló
        self.var_archivo.set(archivo)


def restaurar_desde_interno(self):
    """Restaura la base de datos desde un respaldo interno"""
    if not self.var_respaldo.get():
        messagebox.showwarning("Selección requerida", "Por favor, seleccione un respaldo")
        return

    # Extraer ID del respaldo seleccionado
    id_respaldo = self.var_respaldo.get().split(" - ")[0]

    # Confirmar restauración
    confirmar = messagebox.askyesno(
        "Confirmar restauración",
        "⚠️ ADVERTENCIA: Esta operación sobrescribirá TODOS los datos actuales de la base de datos.\n\n"
        "¿Está seguro de que desea continuar? Se recomienda crear un respaldo antes de restaurar.",
        icon='warning'
    )

    if not confirmar:
        return

    # Obtener ruta del respaldo
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        consulta = "SELECT ruta FROM respaldos WHERE id_respaldo = %s"
        cursor.execute(consulta, (id_respaldo,))

        resultado = cursor.fetchone()
        conexion.close()

        if not resultado:
            messagebox.showerror("Error", "No se encontró el respaldo seleccionado")
            return

        ruta_respaldo = resultado[0]

        # Verificar si el archivo existe
        if not os.path.exists(ruta_respaldo):
            messagebox.showerror(
                "Archivo no encontrado",
                "El archivo de respaldo no existe en la ubicación especificada."
            )
            return

        # Ejecutar restauración
        self.restaurar_base_datos(ruta_respaldo)

    except Exception as e:
        messagebox.showerror(
            "Error",
            f"Error al preparar la restauración: {str(e)}"
        )


def restaurar_desde_externo(self):
    """Restaura la base de datos desde un archivo SQL externo"""
    ruta_archivo = self.var_archivo.get()

    if not ruta_archivo or not os.path.exists(ruta_archivo):
        messagebox.showwarning(
            "Archivo no encontrado",
            "Por favor, seleccione un archivo SQL válido"
        )
        return

    # Confirmar restauración
    confirmar = messagebox.askyesno(
        "Confirmar restauración",
        "⚠️ ADVERTENCIA: Esta operación sobrescribirá TODOS los datos actuales de la base de datos.\n\n"
        "¿Está seguro de que desea continuar? Se recomienda crear un respaldo antes de restaurar.",
        icon='warning'
    )

    if not confirmar:
        return

    # Ejecutar restauración
    self.restaurar_base_datos(ruta_archivo)


def restaurar_base_datos(self, ruta_archivo):
    """
    Restaura la base de datos desde un archivo SQL

    Args:
        ruta_archivo: Ruta al archivo SQL de respaldo
    """
    # Mostrar diálogo de progreso
    ventana_progreso = tk.Toplevel(self.ventana)
    ventana_progreso.title("Restaurando base de datos")
    ventana_progreso.geometry("300x100")
    utl.centrar_ventana(ventana_progreso, 300, 100)
    ventana_progreso.resizable(False, False)
    ventana_progreso.transient(self.ventana)
    ventana_progreso.grab_set()

    lbl_progreso = tk.Label(
        ventana_progreso,
        text="Restaurando base de datos, por favor espere...",
        font=("Helvetica", 12),
        wraplength=280
    )
    lbl_progreso.pack(pady=20)

    barra_progreso = ttk.Progressbar(
        ventana_progreso,
        mode='indeterminate'
    )
    barra_progreso.pack(fill=tk.X, padx=20)
    barra_progreso.start(10)

    # Actualizar la interfaz
    self.ventana.update()

    # Ejecutar restauración en un hilo aparte
    def restaurar_thread():
        resultado = False
        mensaje_error = ""

        try:
            # Obtener configuración
            config = self.config_db

            # Comando para mysql
            comando = [
                "mysql",
                f"--host={config['host']}",
                f"--user={config['user']}",
                f"--password={config['password']}"
            ]

            # Ejecutar comando
            with open(ruta_archivo, 'r') as archivo:
                proceso = subprocess.Popen(
                    comando,
                    stdin=archivo,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                salida, error = proceso.communicate()

                if proceso.returncode != 0:
                    mensaje_error = f"Error en mysql: {error}"
                    resultado = False
                else:
                    resultado = True

        except Exception as e:
            mensaje_error = str(e)
            resultado = False

        # Cerrar ventana de progreso
        ventana_progreso.destroy()

        if resultado:
            messagebox.showinfo(
                "Éxito",
                "La base de datos ha sido restaurada correctamente.\n"
                "Se recomienda reiniciar la aplicación para reflejar los cambios."
            )
        else:
            messagebox.showerror(
                "Error",
                f"No se pudo restaurar la base de datos:\n{mensaje_error}"
            )

    # Iniciar hilo
    threading.Thread(target=restaurar_thread).start()


def salir(self):
    """Cierra la ventana y detiene los hilos"""
    # Detener hilo de programación si está activo
    if self.thread_programacion and self.thread_programacion.is_alive():
        self.seguir_ejecutando = False

    self.ventana.destroy()


# Función para abrir la gestión de respaldos desde otras partes del sistema
def abrir_respaldos(ventana_padre=None, id_usuario=None):
    return GestionRespaldos(ventana_padre, id_usuario)


# Para pruebas independientes
if __name__ == "__main__":
    # Para pruebas, asignar un ID de usuario fijo
    id_usuario_prueba = 1
    GestionRespaldos(id_usuario=id_usuario_prueba)
    """
Módulo de Respaldos para el Sistema de Gestión de Lavandería
Permite crear, programar y restaurar copias de seguridad de la base de datos
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import utileria as utl
from datetime import datetime, date, timedelta
import subprocess
import shutil
import threading
import time
import schedule
import json

# Asegurar que podamos importar módulos del sistema
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

try:
    from conexion import conectar_bd, cargar_configuracion
except ImportError as e:
    print(f"Error al importar módulos: {e}")


class GestionRespaldos:
    """Clase para gestionar las copias de seguridad de la base de datos"""

    def __init__(self, ventana_padre=None, id_usuario=None):
        # Si hay una ventana padre, crear Toplevel en lugar de Tk
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Gestión de Respaldos - Lavandería")
        self.ventana.geometry("800x600")
        self.ventana.config(bg="#f5f5f5")
        self.ventana.resizable(False, False)

        # ID del usuario actual
        self.id_usuario = id_usuario

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

        # Crear directorio para respaldos si no existe
        self.directorio_respaldos = os.path.join(script_dir, "respaldos")
        if not os.path.exists(self.directorio_respaldos):
            os.makedirs(self.directorio_respaldos)

        # Archivo de configuración de respaldos programados
        self.archivo_config = os.path.join(self.directorio_respaldos, "config_respaldos.json")

        # Cargar configuración de MySQL
        self.config_db = cargar_configuracion()

        # Inicializar configuración de respaldos programados
        self.cargar_config_respaldos()

        # Hilo para programación de respaldos
        self.thread_programacion = None
        self.seguir_ejecutando = False

        # Construir la interfaz
        self.construir_interfaz()

        if not ventana_padre:
            self.ventana.mainloop()

    def cargar_config_respaldos(self):
        """Carga la configuración de respaldos programados desde archivo JSON"""
        self.config_respaldos = {
            "activo": False,
            "frecuencia": "diaria",  # diaria, semanal, mensual
            "hora": "03:00",
            "dia_semana": 1,  # 0=lunes, 6=domingo
            "dia_mes": 1,
            "mantener_ultimos": 7,
            "ruta_personalizada": "",
            "ultimo_respaldo": None
        }

        try:
            if os.path.exists(self.archivo_config):
                with open(self.archivo_config, 'r') as f:
                    config_cargada = json.load(f)
                    self.config_respaldos.update(config_cargada)
        except Exception as e:
            print(f"Error al cargar configuración de respaldos: {e}")

    def guardar_config_respaldos(self):
        """Guarda la configuración de respaldos programados en archivo JSON"""
        try:
            with open(self.archivo_config, 'w') as f:
                json.dump(self.config_respaldos, f, indent=4)
            return True
        except Exception as e:
            print(f"Error al guardar configuración de respaldos: {e}")
            return False

    def construir_interfaz(self):
        """Construye la interfaz gráfica del módulo de respaldos"""
        # Frame principal con padding
        self.frame_principal = tk.Frame(self.ventana, bg="#f5f5f5", padx=20, pady=20)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)

        # Título con estilo
        titulo_frame = tk.Frame(self.frame_principal, bg="#f5f5f5")
        titulo_frame.pack(fill=tk.X, pady=(0, 20))

        titulo = tk.Label(
            titulo_frame,
            text="GESTIÓN DE RESPALDOS",
            font=("Helvetica", 18, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        )
        titulo.pack()

        # Separador
        separador = ttk.Separator(self.frame_principal, orient="horizontal")
        separador.pack(fill=tk.X, pady=(0, 20))

        # Crear notebook (pestañas)
        self.notebook = ttk.Notebook(self.frame_principal)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Pestañas
        self.tab_respaldos = tk.Frame(self.notebook, bg="#f5f5f5")
        self.tab_programacion = tk.Frame(self.notebook, bg="#f5f5f5")
        self.tab_restauracion = tk.Frame(self.notebook, bg="#f5f5f5")

        self.notebook.add(self.tab_respaldos, text="Respaldos Manuales")
        self.notebook.add(self.tab_programacion, text="Respaldos Programados")
        self.notebook.add(self.tab_restauracion, text="Restauración")

        # Configurar pestañas
        self.configurar_tab_respaldos()
        self.configurar_tab_programacion()
        self.configurar_tab_restauracion()

        # Botón para volver
        btn_volver = tk.Button(
            self.frame_principal,
            text="Volver",
            font=("Helvetica", 11),
            bg="#e53935",
            fg="white",
            width=10,
            cursor="hand2",
            command=self.salir
        )
        btn_volver.pack(pady=10, anchor=tk.SE)

    def configurar_tab_respaldos(self):
        """Configura la pestaña de respaldos manuales"""
        # Frame para botones de acción
        frame_acciones = tk.Frame(self.tab_respaldos, bg="#f5f5f5")
        frame_acciones.pack(pady=20)

        btn_crear = tk.Button(
            frame_acciones,
            text="Crear Respaldo Ahora",
            font=("Helvetica", 12, "bold"),
            bg="#4caf50",
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.crear_respaldo_manual
        )
        btn_crear.pack(pady=10)

        # Frame para historial de respaldos
        frame_historial = tk.Frame(self.tab_respaldos, bg="#f5f5f5")
        frame_historial.pack(fill=tk.BOTH, expand=True, pady=10)

        lbl_historial = tk.Label(
            frame_historial,
            text="Historial de Respaldos:",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5"
        )
        lbl_historial.pack(anchor=tk.W, pady=5)

        # Tabla de historial
        frame_tabla = tk.Frame(frame_historial, bg="#f5f5f5")
        frame_tabla.pack(fill=tk.BOTH, expand=True)

        columnas = ('id', 'fecha', 'tamanio', 'usuario', 'ruta')

        self.tabla_respaldos = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=10)

        # Aplicar estilo a la tabla
        utl.aplicar_estilo_tabla(self.tabla_respaldos)

        # Configurar encabezados
        self.tabla_respaldos.heading('id', text='ID')
        self.tabla_respaldos.heading('fecha', text='Fecha y Hora')
        self.tabla_respaldos.heading('tamanio', text='Tamaño')
        self.tabla_respaldos.heading('usuario', text='Usuario')
        self.tabla_respaldos.heading('ruta', text='Ubicación')

        # Configurar anchos
        self.tabla_respaldos.column('id', width=50, anchor=tk.CENTER)
        self.tabla_respaldos.column('fecha', width=150, anchor=tk.CENTER)
        self.tabla_respaldos.column('tamanio', width=100, anchor=tk.CENTER)
        self.tabla_respaldos.column('usuario', width=150)
        self.tabla_respaldos.column('ruta', width=300)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_respaldos.yview)
        self.tabla_respaldos.configure(yscrollcommand=scrollbar.set)

        # Empaquetar tabla y scrollbar
        self.tabla_respaldos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame para botones de acción sobre respaldos
        frame_botones = tk.Frame(frame_historial, bg="#f5f5f5")
        frame_botones.pack(fill=tk.X, pady=10)

        btn_abrir = tk.Button(
            frame_botones,
            text="Abrir Ubicación",
            font=("Helvetica", 11),
            bg="#3a7ff6",
            fg="white",
            cursor="hand2",
            command=self.abrir_ubicacion_respaldo
        )
        btn_abrir.pack(side=tk.LEFT, padx=5)

        btn_exportar = tk.Button(
            frame_botones,
            text="Exportar Respaldo",
            font=("Helvetica", 11),
            bg="#3a7ff6",
            fg="white",
            cursor="hand2",
            command=self.exportar_respaldo
        )
        btn_exportar.pack(side=tk.LEFT, padx=5)

        btn_eliminar = tk.Button(
            frame_botones,
            text="Eliminar Respaldo",
            font=("Helvetica", 11),
            bg="#e53935",
            fg="white",
            cursor="hand2",
            command=self.eliminar_respaldo
        )
        btn_eliminar.pack(side=tk.LEFT, padx=5)

        # Botón para refrescar la tabla
        btn_refrescar = tk.Button(
            frame_botones,
            text="Refrescar Lista",
            font=("Helvetica", 11),
            bg="#3a7ff6",
            fg="white",
            cursor="hand2",
            command=self.cargar_historial_respaldos
        )
        btn_refrescar.pack(side=tk.RIGHT, padx=5)

        # Cargar historial inicial
        self.cargar_historial_respaldos()

    def configurar_tab_programacion(self):
        """Configura la pestaña de respaldos programados"""
        # Frame para configuración
        frame_config = tk.Frame(self.tab_programacion, bg="#f5f5f5", padx=20, pady=20)
        frame_config.pack(fill=tk.BOTH, expand=True)

        # Título
        lbl_titulo = tk.Label(
            frame_config,
            text="Configuración de Respaldos Automáticos",
            font=("Helvetica", 14, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        )
        lbl_titulo.grid(row=0, column=0, columnspan=3, pady=10, sticky=tk.W)

        # Activar/Desactivar respaldos programados
        self.var_activo = tk.BooleanVar(value=self.config_respaldos["activo"])
        chk_activo = tk.Checkbutton(
            frame_config,
            text="Activar respaldos programados",
            variable=self.var_activo,
            font=("Helvetica", 12),
            bg="#f5f5f5",
            command=self.actualizar_estado_programacion
        )
        chk_activo.grid(row=1, column=0, columnspan=3, pady=10, sticky=tk.W)

        # Frecuencia
        lbl_frecuencia = tk.Label(
            frame_config,
            text="Frecuencia:",
            font=("Helvetica", 12),
            bg="#f5f5f5"
        )
        lbl_frecuencia.grid(row=2, column=0, padx=5, pady=10, sticky=tk.W)

        self.var_frecuencia = tk.StringVar(value=self.config_respaldos["frecuencia"])
        opciones_frecuencia = [
            ("Diaria", "diaria"),
            ("Semanal", "semanal"),
            ("Mensual", "mensual")
        ]

        for i, (texto, valor) in enumerate(opciones_frecuencia):
            rb = tk.Radiobutton(
                frame_config,
                text=texto,
                variable=self.var_frecuencia,
                value=valor,
                font=("Helvetica", 12),
                bg="#f5f5f5",
                command=self.actualizar_opciones_frecuencia
            )
            rb.grid(row=2, column=i + 1, padx=10, pady=10, sticky=tk.W)

        # Hora
        lbl_hora = tk.Label(
            frame_config,
            text="Hora:",
            font=("Helvetica", 12),
            bg="#f5f5f5"
        )
        lbl_hora.grid(row=3, column=0, padx=5, pady=10, sticky=tk.W)

        self.var_hora = tk.StringVar(value=self.config_respaldos["hora"])
        entry_hora = tk.Entry(
            frame_config,
            textvariable=self.var_hora,
            font=("Helvetica", 12),
            width=10
        )
        entry_hora.grid(row=3, column=1, padx=5, pady=10, sticky=tk.W)

        lbl_formato = tk.Label(
            frame_config,
            text="(Formato 24h, ej: 23:30)",
            font=("Helvetica", 10),
            bg="#f5f5f5",
            fg="#666"
        )
        lbl_formato.grid(row=3, column=2, padx=5, pady=10, sticky=tk.W)

        # Día de la semana (visible solo si frecuencia es semanal)
        lbl_dia_semana = tk.Label(
            frame_config,
            text="Día de la semana:",
            font=("Helvetica", 12),
            bg="#f5f5f5"
        )
        lbl_dia_semana.grid(row=4, column=0, padx=5, pady=10, sticky=tk.W)

        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        self.var_dia_semana = tk.IntVar(value=self.config_respaldos["dia_semana"])
        combo_dia_semana = ttk.Combobox(
            frame_config,
            textvariable=self.var_dia_semana,
            values=list(range(len(dias_semana))),
            font=("Helvetica", 12),
            width=10,
            state="readonly"
        )
        combo_dia_semana.grid(row=4, column=1, padx=5, pady=10, sticky=tk.W)

        lbl_dia_semana_texto = tk.Label(
            frame_config,
            text=dias_semana[self.var_dia_semana.get()],
            font=("Helvetica", 12),
            bg="#f5f5f5"
        )
        lbl_dia_semana_texto.grid(row=4, column=2, padx=5, pady=10, sticky=tk.W)

        # Actualizar texto del día al cambiar selección
        def actualizar_texto_dia(event):
            lbl_dia_semana_texto.config(text=dias_semana[self.var_dia_semana.get()])

        combo_dia_semana.bind("<<ComboboxSelected>>", actualizar_texto_dia)

        # Día del mes (visible solo si frecuencia es mensual)
        lbl_dia_mes = tk.Label(
            frame_config,
            text="Día del mes:",
            font=("Helvetica", 12),
            bg="#f5f5f5"
        )
        lbl_dia_mes.grid(row=5, column=0, padx=5, pady=10, sticky=tk.W)

        self.var_dia_mes = tk.IntVar(value=self.config_respaldos["dia_mes"])
        spin_dia_mes = tk.Spinbox(
            frame_config,
            from_=1,
            to=28,
            textvariable=self.var_dia_mes,
            font=("Helvetica", 12),
            width=5
        )
        spin_dia_mes.grid(row=5, column=1, padx=5, pady=10, sticky=tk.W)

        # Mantener últimos N respaldos
        lbl_mantener = tk.Label(
            frame_config,
            text="Mantener últimos:",
            font=("Helvetica", 12),
            bg="#f5f5f5"
        )
        lbl_mantener.grid(row=6, column=0, padx=5, pady=10, sticky=tk.W)

        self.var_mantener = tk.IntVar(value=self.config_respaldos["mantener_ultimos"])
        spin_mantener = tk.Spinbox(
            frame_config,
            from_=1,
            to=30,
            textvariable=self.var_mantener,
            font=("Helvetica", 12),
            width=5
        )
        spin_mantener.grid(row=6, column=1, padx=5, pady=10, sticky=tk.W)

        lbl_mantener_info = tk.Label(
            frame_config,
            text="respaldos (los más antiguos se eliminarán)",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        lbl_mantener_info.grid(row=6, column=2, padx=5, pady=10, sticky=tk.W)

        # Ruta personalizada
        lbl_ruta = tk.Label(
            frame_config,
            text="Ruta personalizada:",
            font=("Helvetica", 12),
            bg="#f5f5f5"
        )
        lbl_ruta.grid(row=7, column=0, padx=5, pady=10, sticky=tk.W)

        self.var_ruta = tk.StringVar(value=self.config_respaldos["ruta_personalizada"])
        entry_ruta = tk.Entry(
            frame_config,
            textvariable=self.var_ruta,
            font=("Helvetica", 12),
            width=30
        )
        entry_ruta.grid(row=7, column=1, columnspan=2, padx=5, pady=10, sticky=tk.W + tk.E)

        btn_examinar = tk.Button(
            frame_config,
            text="Examinar...",
            font=("Helvetica", 10),
            command=self.seleccionar_ruta_respaldo
        )
        btn_examinar.grid(row=7, column=3, padx=5, pady=10)

        # Información de último respaldo
        lbl_ultimo = tk.Label(
            frame_config,
            text="Último respaldo automático:",
            font=("Helvetica", 12),
            bg="#f5f5f5"
        )
        lbl_ultimo.grid(row=8, column=0, padx=5, pady=20, sticky=tk.W)

        self.lbl_ultimo_respaldo = tk.Label(
            frame_config,
            text="Ninguno" if not self.config_respaldos["ultimo_respaldo"] else self.config_respaldos[
                "ultimo_respaldo"],
            font=("Helvetica", 12),
            bg="#f5f5f5",
            fg="#666"
        )
        self.lbl_ultimo_respaldo.grid(row=8, column=1, columnspan=3, padx=5, pady=20, sticky=tk.W)

        # Botones de acción
        frame_botones = tk.Frame(frame_config, bg="#f5f5f5")
        frame_botones.grid(row=9, column=0, columnspan=4, pady=20)

        btn_guardar = tk.Button(
            frame_botones,
            text="Guardar Configuración",
            font=("Helvetica", 12),
            bg="#4caf50",
            fg="white",
            padx=10,
            cursor="hand2",
            command=self.guardar_configuracion_respaldos
        )
        btn_guardar.pack(side=tk.LEFT, padx=10)

        btn_probar = tk.Button(
            frame_botones,
            text="Probar Configuración",
            font=("Helvetica", 12),
            bg="#3a7ff6",
            fg="white",
            padx=10,
            cursor="hand2",
            command=self.probar_configuracion
        )
        btn_probar.pack(side=tk.LEFT, padx=10)

        # Inicialmente, configurar visibilidad según frecuencia
        self.actualizar_opciones_frecuencia()

    def configurar_tab_restauracion(self):
        """Configura la pestaña de restauración de respaldos"""
        # Frame para instrucciones
        frame_instrucciones = tk.Frame(self.tab_restauracion, bg="#f5f5f5", padx=20, pady=20)
        frame_instrucciones.pack(fill=tk.X)

        lbl_titulo = tk.Label(
            frame_instrucciones,
            text="Restauración de Base de Datos",
            font=("Helvetica", 14, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        )
        lbl_titulo.pack(anchor=tk.W, pady=5)

        lbl_instrucciones = tk.Label(
            frame_instrucciones,
            text="Seleccione un respaldo de la lista o utilice un archivo SQL externo para restaurar la base de datos.",
            font=("Helvetica", 12),
            bg="#f5f5f5",
            justify=tk.LEFT,
            wraplength=700
        )
        lbl_instrucciones.pack(anchor=tk.W, pady=5)

