self.tabla_cortes.column('id', width=50, anchor=tk.CENTER)
self.tabla_cortes.column('fecha', width=100, anchor=tk.CENTER)
self.tabla_cortes.column('apertura', width=80, anchor=tk.CENTER)
self.tabla_cortes.column('cierre', width=80, anchor=tk.CENTER)
self.tabla_cortes.column('ingresos', width=100, anchor=tk.E)
self.tabla_cortes.column('egresos', width=100, anchor=tk.E)
self.tabla_cortes.column('saldo', width=100, anchor=tk.E)
self.tabla_cortes.column('responsable', width=150)

# Scrollbar para la tabla
scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_cortes.yview)
self.tabla_cortes.configure(yscrollcommand=scrollbar.set)

# Empaquetar tabla y scrollbar
self.tabla_cortes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Frame para botones de acción
frame_acciones = tk.Frame(self.tab_cortes, bg="#f5f5f5")
frame_acciones.pack(fill=tk.X, pady=10)

btn_ver_detalle = tk.Button(
    frame_acciones,
    text="Ver Detalle",
    font=("Helvetica", 11),
    bg="#3f51b5",
    fg="white",
    width=15,
    cursor="hand2",
    command=self.ver_detalle_corte
)
btn_ver_detalle.pack(side=tk.LEFT, padx=5)

btn_imprimir_corte = tk.Button(
    frame_acciones,
    text="Imprimir Corte",
    font=("Helvetica", 11),
    bg="#3f51b5",
    fg="white",
    width=15,
    cursor="hand2",
    command=self.imprimir_corte
)
btn_imprimir_corte.pack(side=tk.LEFT, padx=5)

# Cargar cortes iniciales
self.cargar_cortes()


def abrir_caja(self):
    """Abre la caja registrando la hora de apertura y el monto inicial"""
    if self.caja_abierta:
        messagebox.showwarning("Aviso", "Ya hay una caja abierta para el día de hoy")
        return

    # Solicitar monto inicial
    monto_inicial = simpledialog.askfloat(
        "Apertura de Caja",
        "Ingrese el monto inicial de caja:",
        minvalue=0.0
    )

    if monto_inicial is None:  # Usuario canceló
        return

    try:
        # Verificar que el usuario tenga ID asignado
        if not self.id_usuario:
            messagebox.showerror("Error", "No se ha identificado al usuario actual")
            return

        conexion = conectar_bd()
        cursor = conexion.cursor()

        # Insertar registro de apertura de caja
        fecha_actual = date.today().strftime("%Y-%m-%d")
        hora_actual = datetime.now().time()

        # Crear registro de caja
        cursor.execute("""
                INSERT INTO caja (fecha, hora_apertura, total_ingresos, total_egresos, saldo_final, responsable)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (fecha_actual, hora_actual, monto_inicial, 0, monto_inicial, self.id_usuario))

        # Obtener el ID de la caja recién creada
        cursor.execute("SELECT LAST_INSERT_ID()")
        self.id_caja_actual = cursor.fetchone()[0]

        # Registrar el monto inicial como un movimiento de ingreso
        cursor.execute("""
                INSERT INTO movimientos_caja (id_caja, tipo, concepto, monto, hora, id_usuario)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
        self.id_caja_actual, "ingreso", "Monto inicial de caja", monto_inicial, datetime.now(), self.id_usuario))

        conexion.commit()
        conexion.close()

        # Actualizar estado
        self.caja_abierta = True
        self.responsable_caja = self.id_usuario

        messagebox.showinfo("Éxito", f"Caja abierta correctamente con monto inicial de ${monto_inicial:.2f}")

        # Actualizar interfaz
        self.actualizar_estado_caja()
        self.configurar_tab_operaciones()  # Reconstruir pestaña de operaciones
        self.cargar_movimientos()

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la caja: {str(e)}")


def cerrar_caja(self):
    """Cierra la caja registrando la hora de cierre y generando el corte"""
    if not self.caja_abierta:
        messagebox.showwarning("Aviso", "No hay una caja abierta para cerrar")
        return

    # Confirmar cierre
    confirmar = messagebox.askyesno(
        "Confirmar cierre",
        "¿Está seguro de cerrar la caja? Esta acción no se puede deshacer."
    )

    if not confirmar:
        return

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        # Obtener totales actuales
        cursor.execute("""
                SELECT SUM(CASE WHEN tipo = 'ingreso' THEN monto ELSE 0 END) as ingresos,
                       SUM(CASE WHEN tipo = 'egreso' THEN monto ELSE 0 END) as egresos
                FROM movimientos_caja
                WHERE id_caja = %s
            """, (self.id_caja_actual,))

        resultado = cursor.fetchone()

        if resultado:
            total_ingresos, total_egresos = resultado
            # Calcular saldo final
            saldo_final = total_ingresos - total_egresos

            # Actualizar registro de caja con hora de cierre y totales finales
            cursor.execute("""
                    UPDATE caja 
                    SET hora_cierre = %s, total_ingresos = %s, total_egresos = %s, saldo_final = %s
                    WHERE id_caja = %s
                """, (datetime.now().time(), total_ingresos, total_egresos, saldo_final, self.id_caja_actual))

            conexion.commit()

            # Mostrar resumen del cierre
            messagebox.showinfo(
                "Cierre de Caja",
                f"Caja cerrada correctamente\n\n"
                f"Total Ingresos: ${total_ingresos:.2f}\n"
                f"Total Egresos: ${total_egresos:.2f}\n"
                f"Saldo Final: ${saldo_final:.2f}\n\n"
                "Se ha generado un corte de caja."
            )

            # Preguntar si desea imprimir el corte
            if messagebox.askyesno("Imprimir Corte", "¿Desea imprimir el corte de caja?"):
                self.imprimir_corte(self.id_caja_actual)

            # Actualizar estado
            self.caja_abierta = False
            self.id_caja_actual = None
            self.responsable_caja = None

            # Actualizar interfaz
            self.actualizar_estado_caja()
            self.configurar_tab_operaciones()  # Reconstruir pestaña de operaciones
            self.cargar_cortes()

        else:
            messagebox.showerror("Error", "No se pudieron obtener los totales de la caja")

        conexion.close()

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cerrar la caja: {str(e)}")


def registrar_ingreso(self):
    """Registra un ingreso en la caja actual"""
    if not self.caja_abierta:
        messagebox.showwarning("Aviso", "No hay una caja abierta. Abra la caja primero.")
        return

    # Ventana para ingresar datos
    ventana_ingreso = tk.Toplevel(self.ventana)
    ventana_ingreso.title("Registrar Ingreso")
    ventana_ingreso.geometry("400x250")
    ventana_ingreso.config(bg="#f5f5f5")
    ventana_ingreso.resizable(False, False)
    ventana_ingreso.grab_set()  # Hacer modal

    # Centrar ventana
    utl.centrar_ventana(ventana_ingreso, 400, 250)

    # Frame para el formulario
    frame_form = tk.Frame(ventana_ingreso, bg="#f5f5f5", padx=20, pady=20)
    frame_form.pack(fill=tk.BOTH, expand=True)

    # Etiquetas y campos
    tk.Label(
        frame_form,
        text="Concepto:",
        font=("Helvetica", 11),
        bg="#f5f5f5"
    ).grid(row=0, column=0, sticky=tk.W, pady=10)

    entry_concepto = tk.Entry(frame_form, font=("Helvetica", 11), width=30)
    entry_concepto.grid(row=0, column=1, sticky=tk.W, pady=10, padx=5)

    tk.Label(
        frame_form,
        text="Monto ($):",
        font=("Helvetica", 11),
        bg="#f5f5f5"
    ).grid(row=1, column=0, sticky=tk.W, pady=10)

    entry_monto = tk.Entry(frame_form, font=("Helvetica", 11), width=15)
    entry_monto.grid(row=1, column=1, sticky=tk.W, pady=10, padx=5)

    # Frame para botones
    frame_botones = tk.Frame(frame_form, bg="#f5f5f5")
    frame_botones.grid(row=2, column=0, columnspan=2, pady=20)

    def guardar_ingreso():
        # Validar campos
        concepto = entry_concepto.get().strip()
        monto_texto = entry_monto.get().strip().replace(',', '.')

        if not concepto:
            messagebox.showwarning("Campo incompleto", "El concepto es obligatorio")
            return

        try:
            monto = float(monto_texto)
            if monto <= 0:
                messagebox.showwarning("Valor inválido", "El monto debe ser un número positivo")
                return
        except ValueError:
            messagebox.showwarning("Valor inválido", "El monto debe ser un número válido")
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Registrar movimiento
            cursor.execute("""
                    INSERT INTO movimientos_caja (id_caja, tipo, concepto, monto, hora, id_usuario)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (self.id_caja_actual, "ingreso", concepto, monto, datetime.now(), self.id_usuario))

            # Actualizar totales en la caja (opcional, se puede hacer en el cierre)
            cursor.execute("""
                    UPDATE caja 
                    SET total_ingresos = total_ingresos + %s, saldo_final = saldo_final + %s
                    WHERE id_caja = %s
                """, (monto, monto, self.id_caja_actual))

            conexion.commit()
            conexion.close()

            messagebox.showinfo("Éxito", f"Ingreso registrado correctamente por ${monto:.2f}")
            ventana_ingreso.destroy()

            # Actualizar interfaz
            self.actualizar_estado_caja()
            self.cargar_movimientos()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el ingreso: {str(e)}")

    btn_guardar = tk.Button(
        frame_botones,
        text="Guardar",
        font=("Helvetica", 11),
        bg="#4caf50",
        fg="white",
        width=10,
        cursor="hand2",
        command=guardar_ingreso
    )
    btn_guardar.pack(side=tk.LEFT, padx=5)

    btn_cancelar = tk.Button(
        frame_botones,
        text="Cancelar",
        font=("Helvetica", 11),
        bg="#f44336",
        fg="white",
        width=10,
        cursor="hand2",
        command=ventana_ingreso.destroy
    )
    btn_cancelar.pack(side=tk.LEFT, padx=5)


def registrar_egreso(self):
    """Registra un egreso en la caja actual"""
    if not self.caja_abierta:
        messagebox.showwarning("Aviso", "No hay una caja abierta. Abra la caja primero.")
        return

    # Ventana para ingresar datos
    ventana_egreso = tk.Toplevel(self.ventana)
    ventana_egreso.title("Registrar Egreso")
    ventana_egreso.geometry("400x250")
    ventana_egreso.config(bg="#f5f5f5")
    ventana_egreso.resizable(False, False)
    ventana_egreso.grab_set()  # Hacer modal

    # Centrar ventana
    utl.centrar_ventana(ventana_egreso, 400, 250)

    # Frame para el formulario
    frame_form = tk.Frame(ventana_egreso, bg="#f5f5f5", padx=20, pady=20)
    frame_form.pack(fill=tk.BOTH, expand=True)

    # Etiquetas y campos
    tk.Label(
        frame_form,
        text="Concepto:",
        font=("Helvetica", 11),
        bg="#f5f5f5"
    ).grid(row=0, column=0, sticky=tk.W, pady=10)

    entry_concepto = tk.Entry(frame_form, font=("Helvetica", 11), width=30)
    entry_concepto.grid(row=0, column=1, sticky=tk.W, pady=10, padx=5)

    tk.Label(
        frame_form,
        text="Monto ($):",
        font=("Helvetica", 11),
        bg="#f5f5f5"
    ).grid(row=1, column=0, sticky=tk.W, pady=10)

    entry_monto = tk.Entry(frame_form, font=("Helvetica", 11), width=15)
    entry_monto.grid(row=1, column=1, sticky=tk.W, pady=10, padx=5)

    # Frame para botones
    frame_botones = tk.Frame(frame_form, bg="#f5f5f5")
    frame_botones.grid(row=2, column=0, columnspan=2, pady=20)

    def guardar_egreso():
        # Validar campos
        concepto = entry_concepto.get().strip()
        monto_texto = entry_monto.get().strip().replace(',', '.')

        if not concepto:
            messagebox.showwarning("Campo incompleto", "El concepto es obligatorio")
            return

        try:
            monto = float(monto_texto)
            if monto <= 0:
                messagebox.showwarning("Valor inválido", "El monto debe ser un número positivo")
                return
        except ValueError:
            messagebox.showwarning("Valor inválido", "El monto debe ser un número válido")
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Verificar saldo disponible
            cursor.execute("SELECT saldo_final FROM caja WHERE id_caja = %s", (self.id_caja_actual,))
            saldo_actual = cursor.fetchone()[0]

            if saldo_actual < monto:
                messagebox.showwarning(
                    "Saldo insuficiente",
                    f"No hay suficiente saldo en caja. Saldo actual: ${saldo_actual:.2f}"
                )
                return

            # Registrar movimiento
            cursor.execute("""
                    INSERT INTO movimientos_caja (id_caja, tipo, concepto, monto, hora, id_usuario)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (self.id_caja_actual, "egreso", concepto, monto, datetime.now(), self.id_usuario))

            # Actualizar totales en la caja
            cursor.execute("""
                    UPDATE caja 
                    SET total_egresos = total_egresos + %s, saldo_final = saldo_final - %s
                    WHERE id_caja = %s
                """, (monto, monto, self.id_caja_actual))

            conexion.commit()
            conexion.close()

            messagebox.showinfo("Éxito", f"Egreso registrado correctamente por ${monto:.2f}")
            ventana_egreso.destroy()

            # Actualizar interfaz
            self.actualizar_estado_caja()
            self.cargar_movimientos()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el egreso: {str(e)}")

    btn_guardar = tk.Button(
        frame_botones,
        text="Guardar",
        font=("Helvetica", 11),
        bg="#4caf50",
        fg="white",
        width=10,
        cursor="hand2",
        command=guardar_egreso
    )
    btn_guardar.pack(side=tk.LEFT, padx=5)

    btn_cancelar = tk.Button(
        frame_botones,
        text="Cancelar",
        font=("Helvetica", 11),
        bg="#f44336",
        fg="white",
        width=10,
        cursor="hand2",
        command=ventana_egreso.destroy
    )
    btn_cancelar.pack(side=tk.LEFT, padx=5)


def cargar_movimientos(self):
    """Carga los movimientos de caja según los filtros aplicados"""
    # Limpiar tabla
    for item in self.tabla_movimientos.get_children():
        self.tabla_movimientos.delete(item)

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        # Obtener fecha de filtro
        fecha = self.fecha_movimientos.get()
        tipo = self.tipo_movimiento.get()

        # Construir consulta según filtros
        if tipo == "Todos":
            consulta = """
                    SELECT m.id_movimiento, m.hora, m.tipo, m.concepto, m.monto, u.nombre
                    FROM movimientos_caja m
                    JOIN caja c ON m.id_caja = c.id_caja
                    LEFT JOIN usuarios u ON m.id_usuario = u.id_usuario
                    WHERE DATE(c.fecha) = %s
                    ORDER BY m.hora
                """
            cursor.execute(consulta, (fecha,))
        else:
            # Convertir nombre del filtro a valor en la base de datos
            tipo_bd = tipo.lower()

            consulta = """
                    SELECT m.id_movimiento, m.hora, m.tipo, m.concepto, m.monto, u.nombre
                    FROM movimientos_caja m
                    JOIN caja c ON m.id_caja = c.id_caja
                    LEFT JOIN usuarios u ON m.id_usuario = u.id_usuario
                    WHERE DATE(c.fecha) = %s AND m.tipo = %s
                    ORDER BY m.hora
                """
            cursor.execute(consulta, (fecha, tipo_bd))

        # Variables para calcular totales
        total_ing = 0.0
        total_egr = 0.0

        # Insertar datos en la tabla
        for movimiento in cursor.fetchall():
            id_mov, hora, tipo_mov, concepto, monto, usuario = movimiento

            # Formatear hora
            hora_formateada = hora.strftime("%H:%M:%S") if hora else ""

            # Formatear tipo
            tipo_formateado = tipo_mov.capitalize()

            # Formatear monto
            monto_formateado = f"${float(monto):.2f}"

            # Actualizar totales
            if tipo_mov == "ingreso":
                total_ing += float(monto)
                tag_color = "ingreso"
            else:
                total_egr += float(monto)
                tag_color = "egreso"

            # Insertar en la tabla con color según tipo
            self.tabla_movimientos.insert(
                '', tk.END,
                values=(id_mov, hora_formateada, tipo_formateado, concepto, monto_formateado, usuario or ""),
                tags=(tag_color,)
            )

        # Configurar colores para los tipos
        self.tabla_movimientos.tag_configure("ingreso", background="#e8f5e9")
        self.tabla_movimientos.tag_configure("egreso", background="#ffebee")

        # Actualizar totales mostrados
        self.total_ingresos.set(f"${total_ing:.2f}")
        self.total_egresos.set(f"${total_egr:.2f}")
        self.saldo_del_dia.set(f"${(total_ing - total_egr):.2f}")

        conexion.close()

    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar movimientos: {str(e)}")


def cargar_cortes(self):
    """Carga los cortes de caja según la fecha filtrada"""
    # Limpiar tabla
    for item in self.tabla_cortes.get_children():
        self.tabla_cortes.delete(item)

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        # Obtener fecha de filtro
        fecha = self.fecha_cortes.get()

        # Consultar cortes de caja (cajas cerradas)
        consulta = """
                SELECT c.id_caja, c.fecha, c.hora_apertura, c.hora_cierre, 
                       c.total_ingresos, c.total_egresos, c.saldo_final, u.nombre
                FROM caja c
                LEFT JOIN usuarios u ON c.responsable = u.id_usuario
                WHERE DATE(c.fecha) = %s AND c.hora_cierre IS NOT NULL
                ORDER BY c.hora_apertura
            """

        cursor.execute(consulta, (fecha,))

        for corte in cursor.fetchall():
            id_caja, fecha, hora_apertura, hora_cierre, ingresos, egresos, saldo, responsable = corte

            # Formatear datos
            fecha_formateada = utl.formatear_fecha(fecha)
            hora_apertura_str = hora_apertura.strftime("%H:%M") if hora_apertura else ""
            hora_cierre_str = hora_cierre.strftime("%H:%M") if hora_cierre else ""

            # Formatear montos
            ingresos_str = f"${float(ingresos):.2f}"
            egresos_str = f"${float(egresos):.2f}"
            saldo_str = f"${float(saldo):.2f}"

            # Insertar en tabla
            self.tabla_cortes.insert(
                '', tk.END,
                values=(
                    id_caja,
                    fecha_formateada,
                    hora_apertura_str,
                    hora_cierre_str,
                    ingresos_str,
                    egresos_str,
                    saldo_str,
                    responsable or ""
                )
            )

        conexion.close()

    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar cortes de caja: {str(e)}")


def ver_ultimo_corte(self):
    """Muestra el último corte de caja realizado"""
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        # Obtener el último corte de caja (la última caja cerrada)
        consulta = """
                SELECT c.id_caja, c.fecha, c.hora_apertura, c.hora_cierre, 
                       c.total_ingresos, c.total_egresos, c.saldo_final, u.nombre
                FROM caja c
                LEFT JOIN usuarios u ON c.responsable = u.id_usuario
                WHERE c.hora_cierre IS NOT NULL
                ORDER BY c.fecha DESC, c.hora_cierre DESC
                LIMIT 1
            """

        cursor.execute(consulta)
        ultimo_corte = cursor.fetchone()

        if not ultimo_corte:
            messagebox.showinfo("Información", "No hay cortes de caja registrados")
            conexion.close()
            return

        # Mostrar detalles del último corte
        id_caja, fecha, hora_apertura, hora_cierre, ingresos, egresos, saldo, responsable = ultimo_corte

        # Formatear datos
        fecha_formateada = utl.formatear_fecha(fecha)
        hora_apertura_str = hora_apertura.strftime("%H:%M:%S") if hora_apertura else ""
        hora_cierre_str = hora_cierre.strftime("%H:%M:%S") if hora_cierre else ""

        mensaje = f"""Último Corte de Caja:

ID Caja: {id_caja}
Fecha: {fecha_formateada}
Apertura: {hora_apertura_str}
Cierre: {hora_cierre_str}
Responsable: {responsable}

Ingresos: ${float(ingresos):.2f}
Egresos: ${float(egresos):.2f}
Saldo Final: ${float(saldo):.2f}

¿Desea ver los movimientos detallados de este corte?"""

        if messagebox.askyesno("Último Corte", mensaje):
            # Cambiar a la pestaña de movimientos y cargar la fecha correspondiente
            self.fecha_movimientos.set(fecha.strftime("%Y-%m-%d"))
            self.notebook.select(1)  # Seleccionar pestaña de movimientos
            self.cargar_movimientos()

        conexion.close()

    except Exception as e:
        messagebox.showerror("Error", f"Error al obtener último corte: {str(e)}")


def ver_detalle_corte(self):
    """Muestra el detalle de un corte de caja seleccionado"""
    seleccion = self.tabla_cortes.selection()

    if not seleccion:
        messagebox.showwarning("Selección requerida", "Por favor, seleccione un corte para ver su detalle")
        return

    # Obtener ID del corte seleccionado
    valores = self.tabla_cortes.item(seleccion[0], 'values')
    id_corte = valores[0]
    fecha = valores[1]  # La fecha formateada

    # Cambiar a la pestaña de movimientos y cargar los movimientos de ese corte
    try:
        # Convertir la fecha formateada de nuevo al formato YYYY-MM-DD
        partes_fecha = fecha.split('/')
        if len(partes_fecha) == 3:
            fecha_iso = f"{partes_fecha[2]}-{partes_fecha[1]}-{partes_fecha[0]}"
            self.fecha_movimientos.set(fecha_iso)
            self.notebook.select(1)  # Seleccionar pestaña de movimientos
            self.cargar_movimientos()

            # Informar al usuario
            messagebox.showinfo(
                "Detalle de Corte",
                f"Mostrando movimientos del corte #{id_corte} realizado el {fecha}"
            )
        else:
            messagebox.showerror("Error", "Formato de fecha incorrecto")

    except Exception as e:
        messagebox.showerror("Error", f"Error al mostrar detalle del corte: {str(e)}")


def imprimir_estado_caja(self):
    """Imprime el estado actual de la caja"""
    if not self.caja_abierta:
        messagebox.showwarning("Aviso", "No hay una caja abierta actualmente")
        return

    # En una implementación real, aquí se generaría un PDF o se enviaría a la impresora
    # Usaríamos el módulo ticket.py para esto

    # Por ahora, solo mostramos un mensaje
    messagebox.showinfo(
        "Impresión de Estado",
        "En una implementación real, aquí se imprimiría el estado actual de la caja.\n\n"
        "Se incluiría la fecha, hora de apertura, responsable, ingresos, egresos y saldo actual."
    )


def imprimir_movimientos(self):
    """Imprime los movimientos de caja del día seleccionado"""
    # Verificar si hay movimientos
    if not self.tabla_movimientos.get_children():
        messagebox.showwarning("Sin datos", "No hay movimientos para imprimir")
        return

    # En una implementación real, aquí se generaría un PDF o se enviaría a la impresora
    # Usaríamos el módulo ticket.py para esto

    # Por ahora, solo mostramos un mensaje
    fecha = self.fecha_movimientos.get()
    ingresos = self.total_ingresos.get()
    egresos = self.total_egresos.get()
    saldo = self.saldo_del_dia.get()

    messagebox.showinfo(
        "Impresión de Movimientos",
        f"En una implementación real, aquí se imprimirían los movimientos del {fecha}.\n\n"
        f"Total Ingresos: {ingresos}\n"
        f"Total Egresos: {egresos}\n"
        f"Saldo del Día: {saldo}"
    )


def imprimir_corte(self, id_corte=None):
    """Imprime un corte de caja específico"""
    # Si no se proporciona ID, obtenerlo de la selección de la tabla
    if id_corte is None:
        seleccion = self.tabla_cortes.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, seleccione un corte para imprimir")
            return

        # Obtener ID del corte seleccionado
        valores = self.tabla_cortes.item(seleccion[0], 'values')
        id_corte = valores[0]

    # En una implementación real, aquí se generaría un PDF o se enviaría a la impresora
    # Usaríamos el módulo ticket.py para esto

    # Por ahora, solo mostramos un mensaje
    messagebox.showinfo(
        "Impresión de Corte",
        f"En una implementación real, aquí se imprimiría el corte de caja #{id_corte}.\n\n"
        "Se incluiría un reporte detallado con fecha, hora, responsable, ingresos, egresos y saldo final."
    )


# Función para abrir la gestión de caja desde otras partes del sistema
def abrir_caja(ventana_padre=None, id_usuario=None):
    return GestionCaja(ventana_padre, id_usuario)


# Para pruebas independientes
if __name__ == "__main__":
    # Para pruebas, asignar un ID de usuario fijo
    id_usuario_prueba = 1
    GestionCaja(id_usuario=id_usuario_prueba)
    """
Módulo de Caja para el Sistema de Gestión de Lavandería
Permite gestionar apertura y cierre de caja, registrar movimientos,
y generar reportes de cortes de caja.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import sys
import utileria as utl
from datetime import datetime, date, timedelta
import decimal

# Asegurar que podamos importar módulos del sistema
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

try:
    from conexion import conectar_bd
    # Intentar importar el módulo de tickets si está disponible
    from ticket import Ticket
except ImportError as e:
    print(f"Error al importar módulos: {e}")


class GestionCaja:
    """Clase para gestionar las operaciones de caja"""

    def __init__(self, ventana_padre=None, id_usuario=None):
        # Si hay una ventana padre, crear Toplevel en lugar de Tk
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Gestión de Caja - Lavandería")
        self.ventana.geometry("900x650")
        self.ventana.config(bg="#f5f5f5")
        self.ventana.resizable(False, False)

        # ID del usuario actual (para registrar quién hace las operaciones)
        self.id_usuario = id_usuario

        # ID y estado de la caja actual
        self.id_caja_actual = None
        self.caja_abierta = False

        if ventana_padre:
            # Centrar la ventana si existe una ventana padre
            utl.centrar_ventana(self.ventana, 900, 650)
            # Hacer esta ventana modal
            self.ventana.transient(ventana_padre)
            self.ventana.grab_set()

        # Establecer ícono si existe
        try:
            if os.path.exists("Img/lavadora.ico"):
                self.ventana.iconbitmap("Img/lavadora.ico")
        except Exception:
            pass  # Si no se puede cargar el ícono, continuar sin él

        # Verificar estado de la caja al iniciar
        self.verificar_estado_caja()

        # Construir la interfaz
        self.construir_interfaz()

        if not ventana_padre:
            self.ventana.mainloop()

    def construir_interfaz(self):
        """Construye la interfaz gráfica del módulo de caja"""
        # Frame principal con padding
        self.frame_principal = tk.Frame(self.ventana, bg="#f5f5f5", padx=20, pady=20)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)

        # Título con estilo
        titulo_frame = tk.Frame(self.frame_principal, bg="#f5f5f5")
        titulo_frame.pack(fill=tk.X, pady=(0, 20))

        titulo = tk.Label(
            titulo_frame,
            text="GESTIÓN DE CAJA",
            font=("Helvetica", 18, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        )
        titulo.pack()

        # Separador
        separador = ttk.Separator(self.frame_principal, orient="horizontal")
        separador.pack(fill=tk.X, pady=(0, 20))

        # Frame para mostrar estado actual de la caja
        self.frame_estado = tk.Frame(self.frame_principal, bg="#f5f5f5", relief=tk.GROOVE, bd=1)
        self.frame_estado.pack(fill=tk.X, pady=10, padx=5)

        # Mostrar estado de caja actual
        self.actualizar_estado_caja()

        # Crear notebook (pestañas)
        self.notebook = ttk.Notebook(self.frame_principal)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Pestañas
        self.tab_operaciones = tk.Frame(self.notebook, bg="#f5f5f5")
        self.tab_movimientos = tk.Frame(self.notebook, bg="#f5f5f5")
        self.tab_cortes = tk.Frame(self.notebook, bg="#f5f5f5")

        self.notebook.add(self.tab_operaciones, text="Operaciones de Caja")
        self.notebook.add(self.tab_movimientos, text="Movimientos")
        self.notebook.add(self.tab_cortes, text="Cortes de Caja")

        # Configurar las pestañas
        self.configurar_tab_operaciones()
        self.configurar_tab_movimientos()
        self.configurar_tab_cortes()

        # Botón para volver
        btn_volver = tk.Button(
            self.frame_principal,
            text="Volver",
            font=("Helvetica", 11),
            bg="#e53935",
            fg="white",
            width=10,
            cursor="hand2",
            command=self.ventana.destroy
        )
        btn_volver.pack(pady=10, anchor=tk.SE)

    def actualizar_estado_caja(self):
        """Actualiza la visualización del estado actual de la caja"""
        # Limpiar frame de estado
        for widget in self.frame_estado.winfo_children():
            widget.destroy()

        if self.caja_abierta:
            # Obtener información detallada de la caja actual
            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()

                cursor.execute("""
                    SELECT c.fecha, c.hora_apertura, u.nombre, c.total_ingresos, c.total_egresos, c.saldo_final
                    FROM caja c
                    JOIN usuarios u ON c.responsable = u.id_usuario
                    WHERE c.id_caja = %s
                """, (self.id_caja_actual,))

                caja = cursor.fetchone()
                conexion.close()

                if caja:
                    fecha, hora_apertura, responsable, ingresos, egresos, saldo = caja
                    fecha_formateada = utl.formatear_fecha(fecha)
                    hora_formateada = hora_apertura.strftime("%H:%M:%S") if hora_apertura else ""

                    # Mostrar información de caja abierta
                    lbl_estado = tk.Label(
                        self.frame_estado,
                        text="CAJA ABIERTA",
                        font=("Helvetica", 14, "bold"),
                        bg="#b2ff59",
                        fg="#33691e",
                        padx=15,
                        pady=5
                    )
                    lbl_estado.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

                    tk.Label(
                        self.frame_estado,
                        text=f"Fecha: {fecha_formateada}",
                        font=("Helvetica", 12),
                        bg="#f5f5f5"
                    ).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

                    tk.Label(
                        self.frame_estado,
                        text=f"Hora apertura: {hora_formateada}",
                        font=("Helvetica", 12),
                        bg="#f5f5f5"
                    ).grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)

                    tk.Label(
                        self.frame_estado,
                        text=f"Responsable: {responsable}",
                        font=("Helvetica", 12),
                        bg="#f5f5f5"
                    ).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

                    # Mostrar ingresos, egresos y saldo actual
                    tk.Label(
                        self.frame_estado,
                        text=f"Ingresos: ${ingresos:.2f}",
                        font=("Helvetica", 12),
                        bg="#f5f5f5",
                        fg="#388e3c"
                    ).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)

                    tk.Label(
                        self.frame_estado,
                        text=f"Egresos: ${egresos:.2f}",
                        font=("Helvetica", 12),
                        bg="#f5f5f5",
                        fg="#d32f2f"
                    ).grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)

                    tk.Label(
                        self.frame_estado,
                        text=f"Saldo: ${saldo:.2f}",
                        font=("Helvetica", 12, "bold"),
                        bg="#f5f5f5"
                    ).grid(row=0, column=4, rowspan=2, sticky=tk.W, padx=15, pady=2)

            except Exception as e:
                # Si hay error, mostrar un estado simplificado
                lbl_estado = tk.Label(
                    self.frame_estado,
                    text="CAJA ABIERTA",
                    font=("Helvetica", 14, "bold"),
                    bg="#b2ff59",
                    fg="#33691e",
                    padx=15,
                    pady=5
                )
                lbl_estado.pack(side=tk.LEFT, padx=10, pady=10)

                tk.Label(
                    self.frame_estado,
                    text=f"ID Caja: {self.id_caja_actual}",
                    font=("Helvetica", 12),
                    bg="#f5f5f5"
                ).pack(side=tk.LEFT, padx=15, pady=10)

                print(f"Error al obtener detalles de caja: {e}")
        else:
            # Mostrar que la caja está cerrada
            lbl_estado = tk.Label(
                self.frame_estado,
                text="CAJA CERRADA",
                font=("Helvetica", 14, "bold"),
                bg="#ffcdd2",
                fg="#c62828",
                padx=15,
                pady=5
            )
            lbl_estado.pack(side=tk.LEFT, padx=10, pady=10)

            tk.Label(
                self.frame_estado,
                text="Debe abrir la caja para operar",
                font=("Helvetica", 12),
                bg="#f5f5f5"
            ).pack(side=tk.LEFT, padx=15, pady=10)

    def configurar_tab_operaciones(self):
        """Configura la pestaña de operaciones de caja"""
        frame_botones = tk.Frame(self.tab_operaciones, bg="#f5f5f5")
        frame_botones.pack(pady=20)

        # Botones principales de operación de caja
        if not self.caja_abierta:
            # Si la caja está cerrada, mostrar botón de apertura
            btn_abrir = tk.Button(
                frame_botones,
                text="Abrir Caja",
                font=("Helvetica", 12, "bold"),
                bg="#4caf50",
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                command=self.abrir_caja
            )
            btn_abrir.pack(padx=20, pady=10)
        else:
            # Si la caja está abierta, mostrar botones de operación
            btn_ingreso = tk.Button(
                frame_botones,
                text="Registrar Ingreso",
                font=("Helvetica", 12),
                bg="#4caf50",
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                command=self.registrar_ingreso
            )
            btn_ingreso.grid(row=0, column=0, padx=10, pady=10)

            btn_egreso = tk.Button(
                frame_botones,
                text="Registrar Egreso",
                font=("Helvetica", 12),
                bg="#f44336",
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                command=self.registrar_egreso
            )
            btn_egreso.grid(row=0, column=1, padx=10, pady=10)

            btn_cerrar = tk.Button(
                frame_botones,
                text="Cerrar Caja",
                font=("Helvetica", 12, "bold"),
                bg="#ff5722",
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                command=self.cerrar_caja
            )
            btn_cerrar.grid(row=1, column=0, columnspan=2, padx=10, pady=20)

        # Frame para operaciones especiales
        frame_especial = tk.Frame(self.tab_operaciones, bg="#f5f5f5", padx=20, pady=10)
        frame_especial.pack(fill=tk.X, pady=10)

        ttk.Separator(self.tab_operaciones, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=20)

        lbl_operaciones = tk.Label(
            frame_especial,
            text="Operaciones Especiales",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5"
        )
        lbl_operaciones.pack(anchor=tk.W, pady=5)

        frame_botones_especiales = tk.Frame(frame_especial, bg="#f5f5f5")
        frame_botones_especiales.pack(fill=tk.X)

        btn_ultimo_corte = tk.Button(
            frame_botones_especiales,
            text="Ver Último Corte",
            font=("Helvetica", 11),
            bg="#3f51b5",
            fg="white",
            width=15,
            cursor="hand2",
            command=self.ver_ultimo_corte
        )
        btn_ultimo_corte.grid(row=0, column=0, padx=5, pady=5)

        btn_imprimir = tk.Button(
            frame_botones_especiales,
            text="Imprimir Estado",
            font=("Helvetica", 11),
            bg="#3f51b5",
            fg="white",
            width=15,
            cursor="hand2",
            command=self.imprimir_estado_caja
        )
        btn_imprimir.grid(row=0, column=1, padx=5, pady=5)

        # Frame informativo
        frame_info = tk.Frame(self.tab_operaciones, bg="#f0f7ff", padx=20, pady=10, relief=tk.GROOVE, bd=1)
        frame_info.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)

        lbl_info_titulo = tk.Label(
            frame_info,
            text="Información de Uso",
            font=("Helvetica", 12, "bold"),
            bg="#f0f7ff"
        )
        lbl_info_titulo.pack(anchor=tk.W, pady=5)

        info_text = """
• La Apertura de Caja debe realizarse al inicio del día.
• El Cierre de Caja debe realizarse al final del día.
• Los ingresos corresponden a entradas de dinero (ventas, pagos, etc.).
• Los egresos corresponden a salidas de dinero (compras, gastos, etc.).
• Al realizar el cierre se genera automáticamente un corte de caja.
• Es responsabilidad del usuario mantener cuadrada la caja física.
        """

        lbl_info = tk.Label(
            frame_info,
            text=info_text,
            font=("Helvetica", 11),
            bg="#f0f7ff",
            justify=tk.LEFT
        )
        lbl_info.pack(anchor=tk.W, pady=5)

    def configurar_tab_movimientos(self):
        """Configura la pestaña de movimientos de caja"""
        # Frame para filtros
        frame_filtros = tk.Frame(self.tab_movimientos, bg="#f5f5f5")
        frame_filtros.pack(fill=tk.X, pady=10)

        # Filtro por fecha
        tk.Label(
            frame_filtros,
            text="Fecha:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).grid(row=0, column=0, padx=5, pady=5)

        self.fecha_movimientos = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))

        entry_fecha = tk.Entry(
            frame_filtros,
            textvariable=self.fecha_movimientos,
            font=("Helvetica", 11),
            width=12
        )
        entry_fecha.grid(row=0, column=1, padx=5, pady=5)

        # Botón para seleccionar fecha con un calendario (simplificado sin implementar un selector real)
        btn_fecha = tk.Button(
            frame_filtros,
            text="📅",
            font=("Helvetica", 11),
            bg="#3f51b5",
            fg="white",
            cursor="hand2",
            command=lambda: messagebox.showinfo("Calendario",
                                                "En una implementación real, se mostraría un selector de fecha")
        )
        btn_fecha.grid(row=0, column=2, padx=2, pady=5)

        # Filtro por tipo
        tk.Label(
            frame_filtros,
            text="Tipo:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).grid(row=0, column=3, padx=5, pady=5)

        self.tipo_movimiento = tk.StringVar(value="Todos")
        combo_tipo = ttk.Combobox(
            frame_filtros,
            textvariable=self.tipo_movimiento,
            values=["Todos", "Ingreso", "Egreso"],
            width=10,
            state="readonly"
        )
        combo_tipo.grid(row=0, column=4, padx=5, pady=5)

        # Botón de búsqueda
        btn_buscar = tk.Button(
            frame_filtros,
            text="Buscar",
            font=("Helvetica", 11),
            bg="#3f51b5",
            fg="white",
            width=8,
            cursor="hand2",
            command=self.cargar_movimientos
        )
        btn_buscar.grid(row=0, column=5, padx=15, pady=5)

        # Tabla de movimientos
        frame_tabla = tk.Frame(self.tab_movimientos, bg="#f5f5f5")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)

        # Columnas de la tabla
        columnas = ('id', 'hora', 'tipo', 'concepto', 'monto', 'usuario')

        self.tabla_movimientos = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=15)

        # Aplicar estilo a la tabla
        utl.aplicar_estilo_tabla(self.tabla_movimientos)

        # Configurar encabezados
        self.tabla_movimientos.heading('id', text='ID')
        self.tabla_movimientos.heading('hora', text='Hora')
        self.tabla_movimientos.heading('tipo', text='Tipo')
        self.tabla_movimientos.heading('concepto', text='Concepto')
        self.tabla_movimientos.heading('monto', text='Monto')
        self.tabla_movimientos.heading('usuario', text='Usuario')

        # Configurar anchos
        self.tabla_movimientos.column('id', width=50, anchor=tk.CENTER)
        self.tabla_movimientos.column('hora', width=100, anchor=tk.CENTER)
        self.tabla_movimientos.column('tipo', width=100, anchor=tk.CENTER)
        self.tabla_movimientos.column('concepto', width=300)
        self.tabla_movimientos.column('monto', width=100, anchor=tk.E)
        self.tabla_movimientos.column('usuario', width=150)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_movimientos.yview)
        self.tabla_movimientos.configure(yscrollcommand=scrollbar.set)

        # Empaquetar tabla y scrollbar
        self.tabla_movimientos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame para resumen
        frame_resumen = tk.Frame(self.tab_movimientos, bg="#f5f5f5", relief=tk.GROOVE, bd=1)
        frame_resumen.pack(fill=tk.X, pady=10, padx=5)

        # Variables para los totales
        self.total_ingresos = tk.StringVar(value="$0.00")
        self.total_egresos = tk.StringVar(value="$0.00")
        self.saldo_del_dia = tk.StringVar(value="$0.00")

        # Mostrar resumen
        tk.Label(
            frame_resumen,
            text="Total Ingresos:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        tk.Label(
            frame_resumen,
            textvariable=self.total_ingresos,
            font=("Helvetica", 11, "bold"),
            bg="#f5f5f5",
            fg="#388e3c"
        ).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(
            frame_resumen,
            text="Total Egresos:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).grid(row=0, column=2, padx=20, pady=5, sticky=tk.W)

        tk.Label(
            frame_resumen,
            textvariable=self.total_egresos,
            font=("Helvetica", 11, "bold"),
            bg="#f5f5f5",
            fg="#d32f2f"
        ).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        tk.Label(
            frame_resumen,
            text="Saldo del Día:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).grid(row=0, column=4, padx=20, pady=5, sticky=tk.W)

        tk.Label(
            frame_resumen,
            textvariable=self.saldo_del_dia,
            font=("Helvetica", 11, "bold"),
            bg="#f5f5f5"
        ).grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)

        # Botón para imprimir movimientos
        btn_imprimir = tk.Button(
            frame_resumen,
            text="Imprimir Movimientos",
            font=("Helvetica", 11),
            bg="#3f51b5",
            fg="white",
            cursor="hand2",
            command=self.imprimir_movimientos
        )
        btn_imprimir.grid(row=0, column=6, padx=20, pady=5)

        # Cargar movimientos iniciales
        self.cargar_movimientos()

    def configurar_tab_cortes(self):
        """Configura la pestaña de cortes de caja"""
        # Frame para filtros
        frame_filtros = tk.Frame(self.tab_cortes, bg="#f5f5f5")
        frame_filtros.pack(fill=tk.X, pady=10)

        # Filtro por fecha
        tk.Label(
            frame_filtros,
            text="Fecha:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).grid(row=0, column=0, padx=5, pady=5)

        self.fecha_cortes = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))

        entry_fecha_cortes = tk.Entry(
            frame_filtros,
            textvariable=self.fecha_cortes,
            font=("Helvetica", 11),
            width=12
        )
        entry_fecha_cortes.grid(row=0, column=1, padx=5, pady=5)

        # Botón para seleccionar fecha con un calendario (simplificado)
        btn_fecha_cortes = tk.Button(
            frame_filtros,
            text="📅",
            font=("Helvetica", 11),
            bg="#3f51b5",
            fg="white",
            cursor="hand2",
            command=lambda: messagebox.showinfo("Calendario",
                                                "En una implementación real, se mostraría un selector de fecha")
        )
        btn_fecha_cortes.grid(row=0, column=2, padx=2, pady=5)

        # Botón de búsqueda
        btn_buscar_cortes = tk.Button(
            frame_filtros,
            text="Buscar",
            font=("Helvetica", 11),
            bg="#3f51b5",
            fg="white",
            width=8,
            cursor="hand2",
            command=self.cargar_cortes
        )
        btn_buscar_cortes.grid(row=0, column=3, padx=15, pady=5)

        # Tabla de cortes
        frame_tabla = tk.Frame(self.tab_cortes, bg="#f5f5f5")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)

        # Columnas de la tabla
        columnas = ('id', 'fecha', 'apertura', 'cierre', 'ingresos', 'egresos', 'saldo', 'responsable')

        self.tabla_cortes = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=15)

        # Aplicar estilo a la tabla
        utl.aplicar_estilo_tabla(self.tabla_cortes)

        # Configurar encabezados
        self.tabla_cortes.heading('id', text='ID')
        self.tabla_cortes.heading('fecha', text='Fecha')
        self.tabla_cortes.heading('apertura', text='Apertura')
        self.tabla_cortes.heading('cierre', text='Cierre')
        self.tabla_cortes.heading('ingresos', text='Ingresos')
        self.tabla_cortes.heading('egresos', text='Egresos')
        self.tabla_cortes.heading('saldo', text='Saldo Final')
        self.tabla_cortes.heading('responsable', text='Responsable')



    def verificar_estado_caja(self):
        """Verifica si hay una caja abierta para la fecha actual"""
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Consultar si hay una caja abierta para hoy (hora_cierre es NULL)
            fecha_actual = date.today().strftime("%Y-%m-%d")
            cursor.execute(
                "SELECT id_caja, responsable FROM caja WHERE fecha = %s AND hora_cierre IS NULL",
                (fecha_actual,)
            )

            resultado = cursor.fetchone()

            if resultado:
                self.id_caja_actual = resultado[0]
                self.responsable_caja = resultado[1]
                self.caja_abierta = True
            else:
                self.id_caja_actual = None
                self.responsable_caja = None
                self.caja_abierta = False

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al verificar estado de caja: {str(e)}")
            self.caja_abierta = False