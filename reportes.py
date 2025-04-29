import tkinter as tk   
elif tipo_seleccionado == "Clientes Frecuentes":
    columnas = ('id_cliente', 'nombre', 'visitas', 'gasto_total', 'puntos', 'ultima_visita')
    self.tabla_reporte['columns'] = columnas

    # Configurar encabezados
    self.tabla_reporte.heading('id_cliente', text='ID')
    self.tabla_reporte.heading('nombre', text='Cliente')
    self.tabla_reporte.heading('visitas', text='Visitas')
    self.tabla_reporte.heading('gasto_total', text='Gasto Total')
    self.tabla_reporte.heading('puntos', text='Puntos')
    self.tabla_reporte.heading('ultima_visita', text='Última Visita')

    # Configurar anchos
    self.tabla_reporte.column('id_cliente', width=50, anchor=tk.CENTER)
    self.tabla_reporte.column('nombre', width=200)
    self.tabla_reporte.column('visitas', width=80, anchor=tk.CENTER)
    self.tabla_reporte.column('gasto_total', width=100, anchor=tk.E)
    self.tabla_reporte.column('puntos', width=80, anchor=tk.CENTER)
    self.tabla_reporte.column('ultima_visita', width=120, anchor=tk.CENTER)

elif tipo_seleccionado == "Ingresos Mensuales":
    columnas = ('mes', 'ventas', 'total_ventas', 'servicios', 'total_servicios', 'total_general')
    self.tabla_reporte['columns'] = columnas

    # Configurar encabezados
    self.tabla_reporte.heading('mes', text='Mes')
    self.tabla_reporte.heading('ventas', text='Cant. Ventas')
    self.tabla_reporte.heading('total_ventas', text='Total Ventas')
    self.tabla_reporte.heading('servicios', text='Cant. Servicios')
    self.tabla_reporte.heading('total_servicios', text='Total Servicios')
    self.tabla_reporte.heading('total_general', text='Total General')

    # Configurar anchos
    self.tabla_reporte.column('mes', width=100, anchor=tk.W)
    self.tabla_reporte.column('ventas', width=100, anchor=tk.CENTER)
    self.tabla_reporte.column('total_ventas', width=120, anchor=tk.E)
    self.tabla_reporte.column('servicios', width=120, anchor=tk.CENTER)
    self.tabla_reporte.column('total_servicios', width=120, anchor=tk.E)
    self.tabla_reporte.column('total_general', width=120, anchor=tk.E)

elif tipo_seleccionado == "Pedidos por Estado":
    columnas = ('estado', 'cantidad', 'porcentaje')
    self.tabla_reporte['columns'] = columnas

    # Configurar encabezados
    self.tabla_reporte.heading('estado', text='Estado')
    self.tabla_reporte.heading('cantidad', text='Cantidad')
    self.tabla_reporte.heading('porcentaje', text='Porcentaje')

    # Configurar anchos
    self.tabla_reporte.column('estado', width=150, anchor=tk.W)
    self.tabla_reporte.column('cantidad', width=100, anchor=tk.CENTER)
    self.tabla_reporte.column('porcentaje', width=100, anchor=tk.CENTER)

# Aplicar el periodo actual
self.cambiar_periodo()


def cambiar_periodo(self, event=None):
    """Actualiza las fechas según el periodo seleccionado"""
    periodo = self.periodo.get()

    # Ocultar o mostrar frame de fechas personalizadas
    if periodo == "Personalizado":
        self.frame_fechas_personalizadas.pack(side=tk.LEFT, padx=10)
    else:
        self.frame_fechas_personalizadas.pack_forget()

        # Calcular fechas según el periodo seleccionado
        hoy = date.today()

        if periodo == "Hoy":
            self.fecha_inicio.set(hoy.strftime("%Y-%m-%d"))
            self.fecha_fin.set(hoy.strftime("%Y-%m-%d"))

        elif periodo == "Ayer":
            ayer = hoy - timedelta(days=1)
            self.fecha_inicio.set(ayer.strftime("%Y-%m-%d"))
            self.fecha_fin.set(ayer.strftime("%Y-%m-%d"))

        elif periodo == "Esta Semana":
            # Lunes de esta semana
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            self.fecha_inicio.set(inicio_semana.strftime("%Y-%m-%d"))
            self.fecha_fin.set(hoy.strftime("%Y-%m-%d"))

        elif periodo == "Semana Pasada":
            # Lunes de la semana pasada
            inicio_semana_pasada = hoy - timedelta(days=hoy.weekday() + 7)
            # Domingo de la semana pasada
            fin_semana_pasada = inicio_semana_pasada + timedelta(days=6)
            self.fecha_inicio.set(inicio_semana_pasada.strftime("%Y-%m-%d"))
            self.fecha_fin.set(fin_semana_pasada.strftime("%Y-%m-%d"))

        elif periodo == "Este Mes":
            # Primer día del mes actual
            inicio_mes = hoy.replace(day=1)
            self.fecha_inicio.set(inicio_mes.strftime("%Y-%m-%d"))
            self.fecha_fin.set(hoy.strftime("%Y-%m-%d"))

        elif periodo == "Mes Pasado":
            # Primer día del mes pasado
            if hoy.month == 1:
                inicio_mes_pasado = hoy.replace(year=hoy.year - 1, month=12, day=1)
            else:
                inicio_mes_pasado = hoy.replace(month=hoy.month - 1, day=1)

            # Último día del mes pasado
            ultimo_dia = hoy.replace(day=1) - timedelta(days=1)
            self.fecha_inicio.set(inicio_mes_pasado.strftime("%Y-%m-%d"))
            self.fecha_fin.set(ultimo_dia.strftime("%Y-%m-%d"))

        elif periodo == "Último Trimestre":
            # Hace tres meses
            mes_inicio = hoy.month - 3
            año_inicio = hoy.year
            if mes_inicio <= 0:
                mes_inicio += 12
                año_inicio -= 1

            inicio_trimestre = hoy.replace(year=año_inicio, month=mes_inicio, day=1)
            self.fecha_inicio.set(inicio_trimestre.strftime("%Y-%m-%d"))
            self.fecha_fin.set(hoy.strftime("%Y-%m-%d"))

        elif periodo == "Este Año":
            # Primer día del año
            inicio_año = hoy.replace(month=1, day=1)
            self.fecha_inicio.set(inicio_año.strftime("%Y-%m-%d"))
            self.fecha_fin.set(hoy.strftime("%Y-%m-%d"))


def generar_reporte(self):
    """Genera el reporte según el tipo y fecha seleccionados"""
    tipo_reporte = self.tipo_reporte.get()
    fecha_inicio = self.fecha_inicio.get()
    fecha_fin = self.fecha_fin.get()

    # Validar fechas
    try:
        date.fromisoformat(fecha_inicio)
        date.fromisoformat(fecha_fin)
    except ValueError:
        messagebox.showwarning("Formato incorrecto", "Las fechas deben tener el formato YYYY-MM-DD")
        return

    # Limpiar tabla
    for item in self.tabla_reporte.get_children():
        self.tabla_reporte.delete(item)

    # Limpiar resumen
    for widget in self.frame_resumen.winfo_children():
        widget.destroy()

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        # Generar reporte según el tipo seleccionado
        if tipo_reporte == "Ventas por Periodo":
            self.generar_reporte_ventas(cursor, fecha_inicio, fecha_fin)

        elif tipo_reporte == "Productos Más Vendidos":
            self.generar_reporte_productos(cursor, fecha_inicio, fecha_fin)

        elif tipo_reporte == "Servicios Más Solicitados":
            self.generar_reporte_servicios(cursor, fecha_inicio, fecha_fin)

        elif tipo_reporte == "Clientes Frecuentes":
            self.generar_reporte_clientes(cursor, fecha_inicio, fecha_fin)

        elif tipo_reporte == "Ingresos Mensuales":
            self.generar_reporte_ingresos_mensuales(cursor, fecha_inicio, fecha_fin)

        elif tipo_reporte == "Pedidos por Estado":
            self.generar_reporte_pedidos_estado(cursor, fecha_inicio, fecha_fin)

        conexion.close()

        # Actualizar gráfico
        self.actualizar_grafico()

    except Exception as e:
        messagebox.showerror("Error", f"Error al generar el reporte: {str(e)}")


def generar_reporte_ventas(self, cursor, fecha_inicio, fecha_fin):
    """Genera reporte de ventas en el periodo seleccionado"""
    condiciones = ["v.fecha >= %s", "v.fecha <= %s"]
    parametros = [fecha_inicio, fecha_fin]

    # Filtro método de pago
    if self.filtro_pago.get() != "Todos":
        condiciones.append("v.metodo_pago = %s")
        parametros.append(self.filtro_pago.get())

    # Filtro cliente
    if self.filtro_cliente.get().strip() != "":
        condiciones.append("c.nombre LIKE %s")
        parametros.append(f"%{self.filtro_cliente.get().strip()}%")

    # Filtro vendedor
    if self.filtro_vendedor.get().strip() != "":
        condiciones.append("u.nombre LIKE %s")
        parametros.append(f"%{self.filtro_vendedor.get().strip()}%")

    # Unir condiciones y generar consulta final
    where_clause = " AND ".join(condiciones)

    consulta = f"""
        SELECT DATE(v.fecha) as fecha, v.id_venta, c.nombre, v.total, v.metodo_pago, u.nombre as vendedor
        FROM ventas v
        LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
        LEFT JOIN usuarios u ON v.id_usuario = u.id_usuario
        WHERE {where_clause}
        ORDER BY v.fecha DESC
    """
    cursor.execute(consulta, parametros) 
    ventas = cursor.fetchall()

    # Variables para el resumen
    total_ventas = 0
    cantidad_ventas = 0
    metodos_pago = {}

    # Insertar datos en la tabla
    for venta in ventas:
        fecha, id_venta, cliente, total, metodo_pago, vendedor = venta

        # Formatear datos
        fecha_formateada = fecha.strftime("%d/%m/%Y")
        cliente_nombre = cliente if cliente else "Cliente General"
        total_formateado = f"${float(total):.2f}"

        # Insertar en la tabla
        self.tabla_reporte.insert('', tk.END, values=(
            fecha_formateada, id_venta, cliente_nombre, total_formateado, metodo_pago, vendedor
        ))

        # Actualizar totales
        total_ventas += float(total)
        cantidad_ventas += 1

        # Contar métodos de pago
        if metodo_pago in metodos_pago:
            metodos_pago[metodo_pago] += 1
        else:
            metodos_pago[metodo_pago] = 1

    # Mostrar resumen en el frame de resumen
    lbl_total = tk.Label(
        self.frame_resumen,
        text=f"Total Ventas: ${total_ventas:.2f}",
        font=("Helvetica", 11, "bold"),
        bg="#f5f5f5"
    )
    lbl_total.pack(side=tk.LEFT, padx=20, pady=5)

    lbl_cantidad = tk.Label(
        self.frame_resumen,
        text=f"Cantidad: {cantidad_ventas}",
        font=("Helvetica", 11),
        bg="#f5f5f5"
    )
    lbl_cantidad.pack(side=tk.LEFT, padx=20, pady=5)

    lbl_promedio = tk.Label(
        self.frame_resumen,
        text=f"Promedio: ${(total_ventas / cantidad_ventas if cantidad_ventas > 0 else 0):.2f}",
        font=("Helvetica", 11),
        bg="#f5f5f5"
    )
    lbl_promedio.pack(side=tk.LEFT, padx=20, pady=5)

    # Guardar datos para gráficos
    self.datos_grafico = {
        'tipo': 'ventas',
        'ventas': ventas,
        'total': total_ventas,
        'cantidad': cantidad_ventas,
        'metodos_pago': metodos_pago
    }


def generar_reporte_productos(self, cursor, fecha_inicio, fecha_fin):
    """Genera reporte de productos más vendidos"""
    # Consulta SQL para obtener productos más vendidos
    consulta = """
            SELECT p.id_producto, p.nombre, 
                SUM(dv.cantidad) as cantidad_total,
                SUM(dv.subtotal) as ingresos_total
            FROM detalle_venta dv
            JOIN productos p ON dv.id_item = p.id_producto
            JOIN ventas v ON dv.id_venta = v.id_venta
            WHERE dv.tipo_item = 'producto'
            AND DATE(v.fecha) BETWEEN %s AND %s
            GROUP BY p.id_producto, p.nombre
            ORDER BY cantidad_total DESC
        """

    cursor.execute(consulta, (fecha_inicio, fecha_fin))
    productos = cursor.fetchall()

    # Variables para el resumen
    total_ingresos = 0
    total_unidades = 0

    # Insertar datos en la tabla
    for producto in productos:
        id_producto, nombre, cantidad, ingresos = producto

        # Formatear datos
        cantidad_formateada = int(cantidad)
        ingresos_formateados = f"${float(ingresos):.2f}"

        # Insertar en la tabla
        self.tabla_reporte.insert('', tk.END, values=(
            id_producto, nombre, cantidad_formateada, ingresos_formateados
        ))

        # Actualizar totales
        total_ingresos += float(ingresos)
        total_unidades += int(cantidad)

    # Mostrar resumen en el frame de resumen
    lbl_total_ingresos = tk.Label(
        self.frame_resumen,
        text=f"Total Ingresos: ${total_ingresos:.2f}",
        font=("Helvetica", 11, "bold"),
        bg="#f5f5f5"
    )
    lbl_total_ingresos.pack(side=tk.LEFT, padx=20, pady=5)

    lbl_total_unidades = tk.Label(
        self.frame_resumen,
        text=f"Total Unidades: {total_unidades}",
        font=("Helvetica", 11),
        bg="#f5f5f5"
    )
    lbl_total_unidades.pack(side=tk.LEFT, padx=20, pady=5)

    lbl_productos = tk.Label(
        self.frame_resumen,
        text=f"Productos Diferentes: {len(productos)}",
        font=("Helvetica", 11),
        bg="#f5f5f5"
    )
    lbl_productos.pack(side=tk.LEFT, padx=20, pady=5)

    # Guardar datos para gráficos
    self.datos_grafico = {
        'tipo': 'productos',
        'productos': productos,
        'total_ingresos': total_ingresos,
        'total_unidades': total_unidades
    }


def generar_reporte_servicios(self, cursor, fecha_inicio, fecha_fin):
    """Genera reporte de servicios más solicitados"""
    # Consulta SQL para obtener servicios más solicitados
    consulta = """
            SELECT s.id_servicio, s.nombre, 
                SUM(dv.cantidad) as cantidad_total,
                SUM(dv.subtotal) as ingresos_total
            FROM detalle_venta dv
            JOIN servicios s ON dv.id_item = s.id_servicio
            JOIN ventas v ON dv.id_venta = v.id_venta
            WHERE dv.tipo_item = 'servicio'
            AND DATE(v.fecha) BETWEEN %s AND %s
            GROUP BY s.id_servicio, s.nombre
            ORDER BY cantidad_total DESC
        """

    cursor.execute(consulta, (fecha_inicio, fecha_fin))
    servicios = cursor.fetchall()

    # Variables para el resumen
    total_ingresos = 0
    total_servicios = 0

    # Insertar datos en la tabla
    for servicio in servicios:
        id_servicio, nombre, cantidad, ingresos = servicio

        # Formatear datos
        cantidad_formateada = int(cantidad)
        ingresos_formateados = f"${float(ingresos):.2f}"

        # Insertar en la tabla
        self.tabla_reporte.insert('', tk.END, values=(
            id_servicio, nombre, cantidad_formateada, ingresos_formateados
        ))

        # Actualizar totales
        total_ingresos += float(ingresos)
        total_servicios += int(cantidad)

    # Mostrar resumen en el frame de resumen
    lbl_total_ingresos = tk.Label(
        self.frame_resumen,
        text=f"Total Ingresos: ${total_ingresos:.2f}",
        font=("Helvetica", 11, "bold"),
        bg="#f5f5f5"
    )
    lbl_total_ingresos.pack(side=tk.LEFT, padx=20, pady=5)

    lbl_total_servicios = tk.Label(
        self.frame_resumen,
        text=f"Total Servicios: {total_servicios}",
        font=("Helvetica", 11),
        bg="#f5f5f5"
    )
    lbl_total_servicios.pack(side=tk.LEFT, padx=20, pady=5)

    lbl_servicios = tk.Label(
        self.frame_resumen,
        text=f"Servicios Diferentes: {len(servicios)}",
        font=("Helvetica", 11),
        bg="#f5f5f5"
    )
    lbl_servicios.pack(side=tk.LEFT, padx=20, pady=5)

    # Guardar datos para gráficos
    self.datos_grafico = {
        'tipo': 'servicios',
        'servicios': servicios,
        'total_ingresos': total_ingresos,
        'total_servicios': total_servicios
    }


def generar_reporte_clientes(self, cursor, fecha_inicio, fecha_fin):
    """Genera reporte de clientes frecuentes"""
    # Consulta SQL para obtener clientes frecuentes
    consulta = """
            SELECT c.id_cliente, c.nombre, 
                COUNT(DISTINCT v.id_venta) as visitas,
                SUM(v.total) as gasto_total,
                c.puntos,
                MAX(v.fecha) as ultima_visita
            FROM clientes c
            JOIN ventas v ON c.id_cliente = v.id_cliente
            WHERE DATE(v.fecha) BETWEEN %s AND %s
            GROUP BY c.id_cliente, c.nombre, c.puntos
            ORDER BY visitas DESC, gasto_total DESC
        """

    cursor.execute(consulta, (fecha_inicio, fecha_fin))
    clientes = cursor.fetchall()

    # Variables para el resumen
    total_clientes = len(clientes)
    total_visitas = 0
    total_gasto = 0

    # Insertar datos en la tabla
    for cliente in clientes:
        id_cliente, nombre, visitas, gasto, puntos, ultima_visita = cliente

        # Formatear datos
        gasto_formateado = f"${float(gasto):.2f}"
        ultima_visita_formateada = ultima_visita.strftime("%d/%m/%Y")

        # Insertar en la tabla
        self.tabla_reporte.insert('', tk.END, values=(
            id_cliente, nombre, visitas, gasto_formateado, puntos, ultima_visita_formateada
        ))

        # Actualizar totales
        total_visitas += int(visitas)
        total_gasto += float(gasto)

    # Mostrar resumen en el frame de resumen
    lbl_total_clientes = tk.Label(
        self.frame_resumen,
        text=f"Total Clientes: {total_clientes}",
        font=("Helvetica", 11, "bold"),
        bg="#f5f5f5"
    )
    lbl_total_clientes.pack(side=tk.LEFT, padx=20, pady=5)

    lbl_total_visitas = tk.Label(
        self.frame_resumen,
        text=f"Total Visitas: {total_visitas}",
        font=("Helvetica", 11),
        bg="#f5f5f5"
    )
    lbl_total_visitas.pack(side=tk.LEFT, padx=20, pady=5)

    lbl_total_gasto = tk.Label(
        self.frame_resumen,
        text=f"Gasto Total: ${total_gasto:.2f}",
        font=("Helvetica", 11),
        bg="#f5f5f5"
    )
    lbl_total_gasto.pack(side=tk.LEFT, padx=20, pady=5)

    if total_clientes > 0:
        lbl_promedio = tk.Label(
            self.frame_resumen,
            text=f"Promedio por Cliente: ${(total_gasto / total_clientes):.2f}",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        lbl_promedio.pack(side=tk.LEFT, padx=20, pady=5)

    # Guardar datos para gráficos
    self.datos_grafico = {
        'tipo': 'clientes',
        'clientes': clientes,
        'total_clientes': total_clientes,
        'total_visitas': total_visitas,
        'total_gasto': total_gasto
    }


def generar_reporte_ingresos_mensuales(self, cursor, fecha_inicio, fecha_fin):
    """Genera reporte de ingresos mensuales"""
    # Consulta SQL para obtener ingresos por mes
    consulta_ventas = """
            SELECT YEAR(v.fecha) as año, MONTH(v.fecha) as mes,
                COUNT(v.id_venta) as cant_ventas,
                SUM(v.total) as total_ventas
            FROM ventas v
            WHERE DATE(v.fecha) BETWEEN %s AND %s
            GROUP BY YEAR(v.fecha), MONTH(v.fecha)
            ORDER BY YEAR(v.fecha), MONTH(v.fecha)
        """

    consulta_servicios = """
            SELECT YEAR(v.fecha) as año, MONTH(v.fecha) as mes,
                   COUNT(DISTINCT dv.id_detalle) as cant_servicios,
                   SUM(dv.subtotal) as total_servicios
            FROM detalle_venta dv
            JOIN ventas v ON dv.id_venta = v.id_venta
            WHERE dv.tipo_item = 'servicio'
            AND DATE(v.fecha) BETWEEN %s AND %s
            GROUP BY YEAR(v.fecha), MONTH(v.fecha)
            ORDER BY YEAR(v.fecha), MONTH(v.fecha)
        """

    cursor.execute(consulta_ventas, (fecha_inicio, fecha_fin))
    ventas_por_mes = cursor.fetchall()

    cursor.execute(consulta_servicios, (fecha_inicio, fecha_fin))
    servicios_por_mes = cursor.fetchall()

    # Crear diccionario para combinar datos
    datos_por_mes = {}

    # Procesar ventas
    for venta in ventas_por_mes:
        año, mes, cant_ventas, total_ventas = venta
        clave = f"{año}-{mes}"

        if clave not in datos_por_mes:
            datos_por_mes[clave] = {
                'año': año,
                'mes': mes,
                'cant_ventas': cant_ventas,
                'total_ventas': total_ventas,
                'cant_servicios': 0,
                'total_servicios': 0
            }
        else:
            datos_por_mes[clave]['cant_ventas'] = cant_ventas
            datos_por_mes[clave]['total_ventas'] = total_ventas

    # Procesar servicios
    for servicio in servicios_por_mes:
        año, mes, cant_servicios, total_servicios = servicio
        clave = f"{año}-{mes}"

        if clave not in datos_por_mes:
            datos_por_mes[clave] = {
                'año': año,
                'mes': mes,
                'cant_ventas': 0,
                'total_ventas': 0,
                'cant_servicios': cant_servicios,
                'total_servicios': total_servicios
            }
        else:
            datos_por_mes[clave]['cant_servicios'] = cant_servicios
            datos_por_mes[clave]['total_servicios'] = total_servicios

    # Variables para el resumen
    total_general = 0
    total_ventas = 0
    total_servicios = 0

    # Insertar datos en la tabla
    for clave in sorted(datos_por_mes.keys()):
        datos = datos_por_mes[clave]

        # Obtener nombre del mes
        try:
            nombre_mes = calendar.month_name[datos['mes']]
        except:
            nombre_mes = f"Mes {datos['mes']}"

        # Calcular total general del mes
        total_general_mes = float(datos['total_ventas']) + float(datos['total_servicios'])

        # Formatear datos
        mes_formateado = f"{nombre_mes} {datos['año']}"
        total_ventas_formateado = f"${float(datos['total_ventas']):.2f}"
        total_servicios_formateado = f"${float(datos['total_servicios']):.2f}"
        total_general_formateado = f"${total_general_mes:.2f}"

        # Insertar en la tabla
        self.tabla_reporte.insert('', tk.END, values=(
            mes_formateado,
            datos['cant_ventas'],
            total_ventas_formateado,
            datos['cant_servicios'],
            total_servicios_formateado,
            total_general_formateado
        ))

        # Actualizar totales
        total_general += total_general_mes
        total_ventas += float(datos['total_ventas'])
        total_servicios += float(datos['total_servicios'])

    # Mostrar resumen en el frame de resumen
    lbl_total_general = tk.Label(
        self.frame_resumen,
        text=f"Total General: ${total_general:.2f}",
        font=("Helvetica", 11, "bold"),
        bg="#f5f5f5"
    )
    lbl_total_general.pack(side=tk.LEFT, padx=20, pady=5)

    lbl_total_ventas = tk.Label(
        self.frame_resumen,
        text=f"Total Ventas: ${total_ventas:.2f}",
        font=("Helvetica", 11),
        bg="#f5f5f5"
    )
    lbl_total_ventas.pack(side=tk.LEFT, padx=20, pady=5)

    lbl_total_servicios = tk.Label(
        self.frame_resumen,
        text=f"Total Servicios: ${total_servicios:.2f}",
        font=("Helvetica", 11),
        bg="#f5f5f5"
    )
    lbl_total_servicios.pack(side=tk.LEFT, padx=20, pady=5)

    # Guardar datos para gráficos
    self.datos_grafico = {
        'tipo': 'ingresos_mensuales',
        'datos_por_mes': datos_por_mes,
        'total_general': total_general,
        'total_ventas': total_ventas,
        'total_servicios': total_servicios
    }


def generar_reporte_pedidos_estado(self, cursor, fecha_inicio, fecha_fin):
    """Genera reporte de pedidos por estado"""
    # Consulta SQL para obtener pedidos por estado
    consulta = """
            SELECT estado, COUNT(*) as cantidad
            FROM pedidos
            WHERE DATE(fecha_pedido) BETWEEN %s AND %s
            GROUP BY estado
            ORDER BY cantidad DESC
        """

    cursor.execute(consulta, (fecha_inicio, fecha_fin))
    pedidos_por_estado = cursor.fetchall()

    # Calcular total para porcentajes
    total_pedidos = sum(estado[1] for estado in pedidos_por_estado)

    # Variables para el resumen
    estados = {}

    # Insertar datos en la tabla
    for estado in pedidos_por_estado:
        nombre_estado, cantidad = estado

        # Calcular porcentaje
        porcentaje = (cantidad / total_pedidos * 100) if total_pedidos > 0 else 0

        # Formatear datos
        porcentaje_formateado = f"{porcentaje:.2f}%"

        # Insertar en la tabla
        self.tabla_reporte.insert('', tk.END, values=(
            nombre_estado, cantidad, porcentaje_formateado
        ))

        # Guardar para el resumen
        estados[nombre_estado] = cantidad

    # Mostrar resumen en el frame de resumen
    lbl_total_pedidos = tk.Label(
        self.frame_resumen,
        text=f"Total Pedidos: {total_pedidos}",
        font=("Helvetica", 11, "bold"),
        bg="#f5f5f5"
    )
    lbl_total_pedidos.pack(side=tk.LEFT, padx=20, pady=5)

    # Mostrar cantidad de cada estado importante
    estados_importantes = ["Recibido", "En proceso", "Listo para entrega", "Entregado"]
    for estado in estados_importantes:
        cantidad = estados.get(estado, 0)
        porcentaje = (cantidad / total_pedidos * 100) if total_pedidos > 0 else 0

        lbl_estado = tk.Label(
            self.frame_resumen,
            text=f"{estado}: {cantidad} ({porcentaje:.1f}%)",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        lbl_estado.pack(side=tk.LEFT, padx=10, pady=5)

    # Guardar datos para gráficos
    self.datos_grafico = {
        'tipo': 'pedidos_estado',
        'pedidos_por_estado': pedidos_por_estado,
        'total_pedidos': total_pedidos
    }


def actualizar_grafico(self):
    """Actualiza el gráfico según los datos y tipo seleccionado"""
    # Verificar si hay datos para graficar
    if not hasattr(self, 'datos_grafico'):
        return

    # Limpiar figura actual
    self.fig.clear()

    # Obtener tipo de gráfico seleccionado
    tipo_grafico = self.tipo_grafico.get()

    # Crear subplot
    ax = self.fig.add_subplot(111)

    # Generar gráfico según el tipo de reporte
    if self.datos_grafico['tipo'] == 'ventas':
        self.graficar_ventas(ax, tipo_grafico)

    elif self.datos_grafico['tipo'] == 'productos':
        self.graficar_productos(ax, tipo_grafico)

    elif self.datos_grafico['tipo'] == 'servicios':
        self.graficar_servicios(ax, tipo_grafico)

    elif self.datos_grafico['tipo'] == 'clientes':
        self.graficar_clientes(ax, tipo_grafico)

    elif self.datos_grafico['tipo'] == 'ingresos_mensuales':
        self.graficar_ingresos_mensuales(ax, tipo_grafico)

    elif self.datos_grafico['tipo'] == 'pedidos_estado':
        self.graficar_pedidos_estado(ax, tipo_grafico)

    # Ajustar layout y redimensionar
    self.fig.tight_layout()

    # Actualizar canvas
    self.canvas.draw()


def graficar_ventas(self, ax, tipo_grafico):
    """Genera gráfico de ventas"""
    ventas = self.datos_grafico['ventas']

    # Agrupar ventas por fecha para gráfico
    ventas_por_fecha = {}
    for venta in ventas:
        fecha = venta[0].strftime("%d/%m/%Y")
        if fecha in ventas_por_fecha:
            ventas_por_fecha[fecha] += float(venta[3])  # Sumar al total
        else:
            ventas_por_fecha[fecha] = float(venta[3])

    # Ordenar por fecha
    fechas = sorted(ventas_por_fecha.keys())
    totales = [ventas_por_fecha[fecha] for fecha in fechas]

    # Crear gráfico según tipo seleccionado
    if tipo_grafico == "Barras":
        ax.bar(fechas, totales, color='skyblue')

    elif tipo_grafico == "Líneas":
        ax.plot(fechas, totales, marker='o', linestyle='-', color='blue')

    elif tipo_grafico == "Área":
        ax.fill_between(fechas, totales, color='skyblue', alpha=0.5)
        ax.plot(fechas, totales, color='blue')

    elif tipo_grafico == "Pastel":
        # Para gráfico de pastel, mostrar por método de pago
        metodos_pago = self.datos_grafico['metodos_pago']
        labels = list(metodos_pago.keys())
        sizes = list(metodos_pago.values())

        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle

    # Configuración del gráfico
    if tipo_grafico != "Pastel":
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Total ($)')
        ax.set_title('Ventas por Fecha')

        # Rotar etiquetas si hay muchas fechas
        if len(fechas) > 5:
            plt.xticks(rotation=45, ha='right')
    else:
        ax.set_title('Ventas por Método de Pago')


def graficar_productos(self, ax, tipo_grafico):
    """Genera gráfico de productos más vendidos"""
    productos = self.datos_grafico['productos']

    # Limitar a los 10 productos más vendidos para mejor visualización
    top_productos = productos[:10] if len(productos) > 10 else productos

    nombres = [producto[1] for producto in top_productos]
    cantidades = [int(producto[2]) for producto in top_productos]
    ingresos = [float(producto[3]) for producto in top_productos]

    # Acortar nombres largos
    nombres_cortos = [nombre[:20] + "..." if len(nombre) > 20 else nombre for nombre in nombres]

    # Crear gráfico según tipo seleccionado
    if tipo_grafico == "Barras":
        # Gráfico de barras con dos series
        x = range(len(nombres_cortos))
        width = 0.35

        ax.bar([i - width / 2 for i in x], cantidades, width, label='Cantidad', color='skyblue')

        # Crear eje secundario para ingresos
        ax2 = ax.twinx()
        ax2.bar([i + width / 2 for i in x], ingresos, width, label='Ingresos ($)', color='salmon')

        ax.set_xticks(x)
        ax.set_xticklabels(nombres_cortos, rotation=45, ha='right')

        ax.set_ylabel('Cantidad')
        ax2.set_ylabel('Ingresos ($)')

        # Leyendas
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')

    elif tipo_grafico == "Líneas":
        ax.plot(nombres_cortos, cantidades, marker='o', linestyle='-', color='blue', label='Cantidad')

        # Crear eje secundario para ingresos
        ax2 = ax.twinx()
        ax2.plot(nombres_cortos, ingresos, marker='s', linestyle='--', color='red', label='Ingresos ($)')

        plt.xticks(rotation=45, ha='right')

        ax.set_ylabel('Cantidad')
        ax2.set_ylabel('Ingresos ($)')

        # Leyendas
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')

    elif tipo_grafico == "Pastel":
        # Para gráfico de pastel, mostrar por cantidades
        ax.pie(cantidades, labels=nombres_cortos, autopct='%1.1f%%', startangle=90, colors=plt.cm.tab20.colors)
        ax.axis('equal')

    elif tipo_grafico == "Área":
        # Área no es ideal para esta comparación, usar barras apiladas
        x = range(len(nombres_cortos))

        # Normalizar ingresos para que estén en escala similar a cantidades
        factor = max(cantidades) / max(ingresos) if max(ingresos) > 0 else 1
        ingresos_normalizados = [i * factor for i in ingresos]

        ax.fill_between(x, cantidades, color='skyblue', alpha=0.5, label='Cantidad')
        ax.fill_between(x, ingresos_normalizados, color='salmon', alpha=0.5, label='Ingresos (normalizado)')

        ax.set_xticks(x)
        ax.set_xticklabels(nombres_cortos, rotation=45, ha='right')

        ax.legend()

    # Título general
    if tipo_grafico != "Pastel":
        ax.set_title('Top Productos por Cantidad y Ventas')
    else:
        ax.set_title('Distribución de Productos Vendidos')


def graficar_servicios(self, ax, tipo_grafico):
    """Genera gráfico de servicios más solicitados"""
    servicios = self.datos_grafico['servicios']

    # Limitar a los 10 servicios más solicitados para mejor visualización
    top_servicios = servicios[:10] if len(servicios) > 10 else servicios

    nombres = [servicio[1] for servicio in top_servicios]
    cantidades = [int(servicio[2]) for servicio in top_servicios]
    ingresos = [float(servicio[3]) for servicio in top_servicios]

    # Acortar nombres largos
    nombres_cortos = [nombre[:20] + "..." if len(nombre) > 20 else nombre for nombre in nombres]

    # Crear gráfico según tipo seleccionado
    if tipo_grafico == "Barras":
        # Gráfico de barras con dos series
        x = range(len(nombres_cortos))
        width = 0.35

        ax.bar([i - width / 2 for i in x], cantidades, width, label='Cantidad', color='lightgreen')

        # Crear eje secundario para ingresos
        ax2 = ax.twinx()
        ax2.bar([i + width / 2 for i in x], ingresos, width, label='Ingresos ($)', color='orange')

        ax.set_xticks(x)
        ax.set_xticklabels(nombres_cortos, rotation=45, ha='right')

        ax.set_ylabel('Cantidad')
        ax2.set_ylabel('Ingresos ($)')

        # Leyendas
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')

    elif tipo_grafico == "Líneas":
        ax.plot(nombres_cortos, cantidades, marker='o', linestyle='-', color='green', label='Cantidad')

        # Crear eje secundario para ingresos
        ax2 = ax.twinx()
        ax2.plot(nombres_cortos, ingresos, marker='s', linestyle='--', color='orange', label='Ingresos ($)')

        plt.xticks(rotation=45, ha='right')

        ax.set_ylabel('Cantidad')
        ax2.set_ylabel('Ingresos ($)')

        # Leyendas
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')

    elif tipo_grafico == "Pastel":
        # Para gráfico de pastel, mostrar por cantidades
        ax.pie(cantidades, labels=nombres_cortos, autopct='%1.1f%%', startangle=90, colors=plt.cm.Set3.colors)
        ax.axis('equal')

    elif tipo_grafico == "Área":
        # Área no es ideal para esta comparación, usar barras apiladas
        x = range(len(nombres_cortos))

        # Normalizar ingresos para que estén en escala similar a cantidades
        factor = max(cantidades) / max(ingresos) if max(ingresos) > 0 else 1
        ingresos_normalizados = [i * factor for i in ingresos]

        ax.fill_between(x, cantidades, color='lightgreen', alpha=0.5, label='Cantidad')
        ax.fill_between(x, ingresos_normalizados, color='orange', alpha=0.5, label='Ingresos (normalizado)')

        ax.set_xticks(x)
        ax.set_xticklabels(nombres_cortos, rotation=45, ha='right')

        ax.legend()

    # Título general
    if tipo_grafico != "Pastel":
        ax.set_title('Top Servicios por Cantidad y Ventas')
    else:
        ax.set_title('Distribución de Servicios Solicitados')


def graficar_clientes(self, ax, tipo_grafico):
    """Genera gráfico de clientes frecuentes"""
    clientes = self.datos_grafico['clientes']

    # Limitar a los 10 clientes más frecuentes para mejor visualización
    top_clientes = clientes[:10] if len(clientes) > 10 else clientes

    nombres = [cliente[1] for cliente in top_clientes]
    visitas = [int(cliente[2]) for cliente in top_clientes]
    gastos = [float(cliente[3]) for cliente in top_clientes]
    puntos = [int(cliente[4]) for cliente in top_clientes]

    # Acortar nombres largos
    nombres_cortos = [nombre[:15] + "..." if len(nombre) > 15 else nombre for nombre in nombres]

    # Crear gráfico según tipo seleccionado
    if tipo_grafico == "Barras":
        # Gráfico de barras agrupadas
        x = range(len(nombres_cortos))
        width = 0.25

        ax.bar([i - width for i in x], visitas, width, label='Visitas', color='royalblue')
        ax.bar(x, puntos, width, label='Puntos', color='mediumseagreen')

        # Crear eje secundario para gastos
        ax2 = ax.twinx()
        ax2.bar([i + width for i in x], gastos, width, label='Gasto ($)', color='tomato')

        ax.set_xticks(x)
        ax.set_xticklabels(nombres_cortos, rotation=45, ha='right')

        ax.set_ylabel('Cantidad')
        ax2.set_ylabel('Gasto Total ($)')

        # Leyendas
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')

    elif tipo_grafico == "Líneas":
        ax.plot(nombres_cortos, visitas, marker='o', linestyle='-', color='blue', label='Visitas')
        ax.plot(nombres_cortos, puntos, marker='^', linestyle='-', color='green', label='Puntos')

        # Crear eje secundario para gastos
        ax2 = ax.twinx()
        ax2.plot(nombres_cortos, gastos, marker='s', linestyle='--', color='red', label='Gasto ($)')

        plt.xticks(rotation=45, ha='right')

        ax.set_ylabel('Cantidad')
        ax2.set_ylabel('Gasto Total ($)')

        # Leyendas
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')

    elif tipo_grafico == "Pastel":
        # Para gráfico de pastel, mostrar por gastos
        ax.pie(gastos, labels=nombres_cortos, autopct='%1.1f%%', startangle=90, colors=plt.cm.tab20c.colors)
        ax.axis('equal')

    elif tipo_grafico == "Área":
        # Gráfico de área para visitas y puntos
        x = range(len(nombres_cortos))

        ax.fill_between(x, visitas, color='royalblue', alpha=0.5, label='Visitas')
        ax.fill_between(x, puntos, color='mediumseagreen', alpha=0.5, label='Puntos')

        # Crear eje secundario para gastos
        ax2 = ax.twinx()
        ax2.plot(x, gastos, marker='o', linestyle='-', color='tomato', label='Gasto ($)')

        ax.set_xticks(x)
        ax.set_xticklabels(nombres_cortos, rotation=45, ha='right')

        ax.set_ylabel('Cantidad')
        ax2.set_ylabel('Gasto Total ($)')

        # Leyendas
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')

    # Título general
    if tipo_grafico != "Pastel":
        ax.set_title('Top Clientes por Frecuencia y Gasto')
    else:
        ax.set_title('Distribución de Gastos por Cliente')


def graficar_ingresos_mensuales(self, ax, tipo_grafico):
    """Genera gráfico de ingresos mensuales"""
    datos_por_mes = self.datos_grafico['datos_por_mes']

    # Ordenar por fecha
    claves_ordenadas = sorted(datos_por_mes.keys())

    # Preparar datos para gráfico
    meses = []
    totales_ventas = []
    totales_servicios = []

    for clave in claves_ordenadas:
        datos = datos_por_mes[clave]

        # Crear etiqueta de mes
        try:
            nombre_mes = calendar.month_name[datos['mes']]
        except:
            nombre_mes = f"Mes {datos['mes']}"

        etiqueta = f"{nombre_mes[:3]} {str(datos['año'])[-2:]}"
        meses.append(etiqueta)

        # Agregar valores
        totales_ventas.append(float(datos['total_ventas']))
        totales_servicios.append(float(datos['total_servicios']))

    # Crear gráfico según tipo seleccionado
    if tipo_grafico == "Barras":
        # Gráfico de barras apiladas
        ax.bar(meses, totales_ventas, label='Ventas', color='royalblue')
        ax.bar(meses, totales_servicios, bottom=totales_ventas, label='Servicios', color='lightgreen')

        ax.set_xlabel('Mes')
        ax.set_ylabel('Ingresos ($)')
        ax.legend()

    elif tipo_grafico == "Líneas":
        # Gráfico de líneas
        ax.plot(meses, totales_ventas, marker='o', linestyle='-', color='blue', label='Ventas')
        ax.plot(meses, totales_servicios, marker='^', linestyle='-', color='green', label='Servicios')

        # Línea para el total
        totales = [v + s for v, s in zip(totales_ventas, totales_servicios)]
        ax.plot(meses, totales, marker='s', linestyle='--', color='red', label='Total')

        ax.set_xlabel('Mes')
        ax.set_ylabel('Ingresos ($)')
        ax.legend()

    elif tipo_grafico == "Área":
        # Gráfico de área apilada
        ax.fill_between(meses, totales_ventas, color='royalblue', alpha=0.5, label='Ventas')

        # Calcular totales para apilar correctamente
        totales = [v + s for v, s in zip(totales_ventas, totales_servicios)]

        ax.fill_between(meses, totales, y1=totales_ventas, color='lightgreen', alpha=0.5, label='Servicios')

        ax.set_xlabel('Mes')
        ax.set_ylabel('Ingresos ($)')
        ax.legend()

    elif tipo_grafico == "Pastel":
        # Para gráfico de pastel, mostrar la suma total por mes
        totales = [v + s for v, s in zip(totales_ventas, totales_servicios)]

        ax.pie(totales, labels=meses, autopct='%1.1f%%', startangle=90, colors=plt.cm.tab20b.colors)
        ax.axis('equal')

    # Título general
    if tipo_grafico != "Pastel":
        ax.set_title('Ingresos Mensuales')
    else:
        ax.set_title('Distribución de Ingresos por Mes')

    # Rotar etiquetas para mejor visualización
    if tipo_grafico != "Pastel":
        plt.xticks(rotation=45)


def graficar_pedidos_estado(self, ax, tipo_grafico):
    """Genera gráfico de pedidos por estado"""
    pedidos_por_estado = self.datos_grafico['pedidos_por_estado']

    # Preparar datos para gráfico
    estados = [estado[0] for estado in pedidos_por_estado]
    cantidades = [estado[1] for estado in pedidos_por_estado]

    # Crear gráfico según tipo seleccionado
    if tipo_grafico == "Barras":
        # Asignar colores según el estado
        colores = []
        for estado in estados:
            if estado == "Recibido":
                colores.append('skyblue')
            elif estado == "En proceso":
                colores.append('orange')
            elif estado == "Listo para entrega":
                colores.append('lightgreen')
            elif estado == "Entregado":
                colores.append('mediumseagreen')
            else:
                colores.append('gray')

        ax.bar(estados, cantidades, color=colores)

        ax.set_xlabel('Estado')
        ax.set_ylabel('Cantidad de Pedidos')

    elif tipo_grafico == "Líneas":
        ax.plot(estados, cantidades, marker='o', linestyle='-', color='blue')

        ax.set_xlabel('Estado')
        ax.set_ylabel('Cantidad de Pedidos')

    elif tipo_grafico == "Pastel":
        # Asignar colores según el estado
        colores = []
        for estado in estados:
            if estado == "Recibido":
                colores.append('skyblue')
            elif estado == "En proceso":
                colores.append('orange')
            elif estado == "Listo para entrega":
                colores.append('lightgreen')
            elif estado == "Entregado":
                colores.append('mediumseagreen')
            else:
                colores.append('gray')

        ax.pie(cantidades, labels=estados, autopct='%1.1f%%', startangle=90, colors=colores)
        ax.axis('equal')

    elif tipo_grafico == "Área":
        # No es el mejor tipo para estos datos, usar barras
        ax.fill_between(range(len(estados)), cantidades, color='skyblue', alpha=0.5)
        ax.plot(range(len(estados)), cantidades, marker='o', color='blue')

        ax.set_xticks(range(len(estados)))
        ax.set_xticklabels(estados)

        ax.set_xlabel('Estado')
        ax.set_ylabel('Cantidad de Pedidos')

    # Título general
    if tipo_grafico != "Pastel":
        ax.set_title('Pedidos por Estado')
    else:
        ax.set_title('Distribución de Pedidos por Estado')


def personalizar_colores(self):
    """Permite al usuario personalizar los colores del gráfico"""
    # Simplemente mostrar un selector de color y cambiar el esquema de colores
    # En una implementación real, se permitiría una personalización más detallada
    color = colorchooser.askcolor(title="Seleccionar color principal")

    if color[1]:  # Si se seleccionó un color
        messagebox.showinfo("Color seleccionado", f"Se ha seleccionado el color {color[1]}")

        # Actualizar el gráfico con el nuevo color
        self.actualizar_grafico()
        
def guardar_plantilla(self):
    """Guarda la configuración actual del reporte como una plantilla .json"""
    import json
    tipo = self.tipo_reporte.get().replace(" ", "_").lower()
    periodo = self.periodo.get().replace(" ", "_").lower()
    nombre_archivo = f"{tipo}_{periodo}.json"

    datos = {
        "tipo_reporte": self.tipo_reporte.get(),
        "periodo": self.periodo.get(),
        "fecha_inicio": self.fecha_inicio.get(),
        "fecha_fin": self.fecha_fin.get()
    }

    try:
        ruta = os.path.join(self.directorio_reportes, nombre_archivo)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)

        messagebox.showinfo("Plantilla guardada", f"Se guardó como:\n{nombre_archivo}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar la plantilla:\n{e}")


def exportar_reporte(self):
    """Exporta el reporte actual a Excel o PDF"""
    # Verificar si hay datos para exportar
    if not hasattr(self, 'datos_grafico'):
        messagebox.showwarning("Sin datos", "No hay datos para exportar")
        return

    # Preguntar formato y ubicación
    formatos = [
        ("Excel", "*.xlsx"),
        ("CSV", "*.csv"),
        ("PDF", "*.pdf")
    ]

    ruta_archivo = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=formatos,
        title="Guardar reporte como"
    )

    if not ruta_archivo:
        return  # Usuario canceló

    try:
        extension = os.path.splitext(ruta_archivo)[1].lower()

        if extension == '.xlsx':
            self.exportar_excel(ruta_archivo)
        elif extension == '.csv':
            self.exportar_csv(ruta_archivo)
        elif extension == '.pdf':
            self.exportar_pdf(ruta_archivo)

        messagebox.showinfo("Éxito", f"Reporte exportado exitosamente a {ruta_archivo}")

        # Abrir el archivo
        if messagebox.askyesno("Abrir archivo", "¿Desea abrir el archivo exportado?"):
            os.startfile(ruta_archivo)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar el reporte: {str(e)}")


def exportar_excel(self, ruta_archivo):
    """Exporta los datos a un archivo Excel"""
    # Obtener datos de la tabla
    datos = []
    columnas = []

    # Obtener nombres de columnas
    for col in self.tabla_reporte['columns']:
        columnas.append(self.tabla_reporte.heading(col)['text'])

    # Obtener datos de filas
    for item in self.tabla_reporte.get_children():
        valores = self.tabla_reporte.item(item)['values']
        datos.append(valores)

    # Crear DataFrame
    df = pd.DataFrame(datos, columns=columnas)

    # Guardar como Excel
    df.to_excel(ruta_archivo, index=False)


def exportar_csv(self, ruta_archivo):
    """Exporta los datos a un archivo CSV"""
    # Obtener datos de la tabla
    datos = []
    columnas = []

    # Obtener nombres de columnas
    for col in self.tabla_reporte['columns']:
        columnas.append(self.tabla_reporte.heading(col)['text'])

    # Obtener datos de filas
    for item in self.tabla_reporte.get_children():
        valores = self.tabla_reporte.item(item)['values']
        datos.append(valores)

    # Crear DataFrame
    df = pd.DataFrame(datos, columns=columnas)

    # Guardar como CSV
    df.to_csv(ruta_archivo, index=False)


def exportar_pdf(self, ruta_archivo):
    """Exporta los datos a un archivo PDF"""
    # En una implementación real, aquí se utilizaría reportlab o similar
    # para generar un PDF completo con la tabla y el gráfico

    # Por ahora, simplemente guardar la figura actual como PDF
    self.fig.savefig(ruta_archivo)


# Función para abrir el módulo de reportes desde otras partes del sistema
def abrir_reportes(ventana_padre=None):
    return Reportes(ventana_padre)


# Para pruebas independientes
if __name__ == "__main__":
    Reportes()
    """
Módulo de Reportes para el Sistema de Gestión de Lavandería
Permite generar reportes de ventas, productos, pedidos y clientes
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import utileria as utl
from datetime import datetime, date, timedelta
import decimal
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import colorchooser
import calendar
import locale

# Intentar configurar el locale para formato de fechas en español
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')
    except:
        pass  # Si no funciona, se usará el locale por defecto

# Asegurar que podamos importar módulos del sistema
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

try:
    from conexion import conectar_bd
except ImportError as e:
    print(f"Error al importar módulos: {e}")


class Reportes:
    """Clase para gestionar la generación de reportes"""

    def __init__(self, ventana_padre=None):
        # Si hay una ventana padre, crear Toplevel en lugar de Tk
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Reportes - Lavandería")
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
            pass  # Si no se puede cargar el ícono, continuar sin él

        # Crear directorio para guardar reportes si no existe
        self.directorio_reportes = os.path.join(script_dir, "reportes")
        if not os.path.exists(self.directorio_reportes):
            os.makedirs(self.directorio_reportes)

        # Construir la interfaz
        self.construir_interfaz()

        if not ventana_padre:
            self.ventana.mainloop()

    def construir_interfaz(self):
        """Construye la interfaz gráfica del módulo de reportes"""
        # Frame principal con padding
        self.frame_principal = tk.Frame(self.ventana, bg="#f5f5f5", padx=20, pady=20)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)

        # Título con estilo
        titulo_frame = tk.Frame(self.frame_principal, bg="#f5f5f5")
        titulo_frame.pack(fill=tk.X, pady=(0, 20))

        titulo = tk.Label(
            titulo_frame,
            text="REPORTES Y ESTADÍSTICAS",
            font=("Helvetica", 18, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        )
        titulo.pack()

        # Separador
        separador = ttk.Separator(self.frame_principal, orient="horizontal")
        separador.pack(fill=tk.X, pady=(0, 20))

        # Frame para filtros y controles
        frame_controles = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_controles.pack(fill=tk.X, pady=10)

        # Frame para selección de tipo de reporte
        frame_tipo = tk.Frame(frame_controles, bg="#f5f5f5")
        frame_tipo.pack(side=tk.LEFT, padx=10)

        tk.Label(
            frame_tipo,
            text="Tipo de Reporte:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        # Opciones de reportes disponibles
        opciones_reportes = [
            "Ventas por Periodo",
            "Productos Más Vendidos",
            "Servicios Más Solicitados",
            "Clientes Frecuentes",
            "Ingresos Mensuales",
            "Pedidos por Estado"
        ]

        self.tipo_reporte = tk.StringVar(value=opciones_reportes[0])
        combo_tipo = ttk.Combobox(
            frame_tipo,
            textvariable=self.tipo_reporte,
            values=opciones_reportes,
            width=20,
            state="readonly"
        )
        combo_tipo.pack(side=tk.LEFT, padx=5)
        combo_tipo.bind("<<ComboboxSelected>>", self.cambiar_tipo_reporte)

        # Frame para filtros de fecha
        frame_fecha = tk.Frame(frame_controles, bg="#f5f5f5")
        frame_fecha.pack(side=tk.LEFT, padx=20)

        tk.Label(
            frame_fecha,
            text="Período:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        # Opciones de períodos
        opciones_periodos = [
            "Hoy",
            "Ayer",
            "Esta Semana",
            "Semana Pasada",
            "Este Mes",
            "Mes Pasado",
            "Último Trimestre",
            "Este Año",
            "Personalizado"
        ]

        self.periodo = tk.StringVar(value=opciones_periodos[4])  # Por defecto "Este Mes"
        combo_periodo = ttk.Combobox(
            frame_fecha,
            textvariable=self.periodo,
            values=opciones_periodos,
            width=15,
            state="readonly"
        )
        combo_periodo.pack(side=tk.LEFT, padx=5)
        combo_periodo.bind("<<ComboboxSelected>>", self.cambiar_periodo)

        # Frame para fechas personalizadas (inicialmente oculto)
        self.frame_fechas_personalizadas = tk.Frame(frame_controles, bg="#f5f5f5")

        tk.Label(
            self.frame_fechas_personalizadas,
            text="Desde:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        # Fecha de inicio del rango
        self.fecha_inicio = tk.StringVar(value=date.today().replace(day=1).strftime("%Y-%m-%d"))
        entry_fecha_inicio = tk.Entry(
            self.frame_fechas_personalizadas,
            textvariable=self.fecha_inicio,
            font=("Helvetica", 11),
            width=10
        )
        entry_fecha_inicio.pack(side=tk.LEFT, padx=2)

        tk.Label(
            self.frame_fechas_personalizadas,
            text="Hasta:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        # Fecha de fin del rango
        self.fecha_fin = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        entry_fecha_fin = tk.Entry(
            self.frame_fechas_personalizadas,
            textvariable=self.fecha_fin,
            font=("Helvetica", 11),
            width=10
        )
        entry_fecha_fin.pack(side=tk.LEFT, padx=2)

        # Botón para generar reporte
        btn_generar = tk.Button(
            frame_controles,
            text="Generar Reporte",
            font=("Helvetica", 11),
            bg="#3a7ff6",
            fg="white",
            padx=10,
            cursor="hand2",
            command=self.generar_reporte
        )
        btn_generar.pack(side=tk.RIGHT, padx=10)

        # Botón para exportar
        btn_exportar = tk.Button(
            frame_controles,
            text="Exportar",
            font=("Helvetica", 11),
            bg="#4caf50",
            fg="white",
            padx=10,
            cursor="hand2",
            command=self.exportar_reporte
        )
        btn_exportar.pack(side=tk.RIGHT, padx=5)
        
        # Botón para guardar configuración como plantilla
        btn_guardar_plantilla = tk.Button(
            frame_controles,
            text="Guardar como Plantilla",
            font=("Helvetica", 11),
            bg="#ff9800",
            fg="white",
            padx=10,
            cursor="hand2",
            command=self.guardar_plantilla
        )
        btn_guardar_plantilla.pack(side=tk.RIGHT, padx=5)

        # Crear notebook (pestañas)
        self.notebook = ttk.Notebook(self.frame_principal)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Pestañas
        self.tab_tabla = tk.Frame(self.notebook, bg="#f5f5f5")
        self.tab_grafico = tk.Frame(self.notebook, bg="#f5f5f5")

        self.notebook.add(self.tab_tabla, text="Datos")
        self.notebook.add(self.tab_grafico, text="Gráfico")

        # Configurar pestaña de tabla
        self.configurar_tab_tabla()

        # Configurar pestaña de gráfico
        self.configurar_tab_grafico()

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

        # Inicializar con el primer tipo de reporte
        self.cambiar_tipo_reporte()

    def configurar_tab_tabla(self):
        """Configura la pestaña de visualización en tabla"""
        # Frame para la tabla
        frame_tabla = tk.Frame(self.tab_tabla, bg="#f5f5f5")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)

        # Crear tabla con scrollbar
        self.tabla_reporte = ttk.Treeview(frame_tabla)

        # Aplicar estilo a la tabla
        utl.aplicar_estilo_tabla(self.tabla_reporte)

        # Scrollbar vertical
        scrollbar_y = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_reporte.yview)
        self.tabla_reporte.configure(yscrollcommand=scrollbar_y.set)

        # Scrollbar horizontal
        scrollbar_x = ttk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL, command=self.tabla_reporte.xview)
        self.tabla_reporte.configure(xscrollcommand=scrollbar_x.set)

        # Empaquetar elementos
        self.tabla_reporte.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Frame para resumen
        self.frame_resumen = tk.Frame(self.tab_tabla, bg="#f5f5f5", relief=tk.GROOVE, bd=1)
        self.frame_resumen.pack(fill=tk.X, pady=10, padx=5)

    def configurar_tab_grafico(self):
        """Configura la pestaña de visualización gráfica"""
        # Frame para controles del gráfico
        frame_controles_grafico = tk.Frame(self.tab_grafico, bg="#f5f5f5")
        frame_controles_grafico.pack(fill=tk.X, pady=5)

        # Tipo de gráfico
        tk.Label(
            frame_controles_grafico,
            text="Tipo de Gráfico:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        self.tipo_grafico = tk.StringVar(value="Barras")
        combo_grafico = ttk.Combobox(
            frame_controles_grafico,
            textvariable=self.tipo_grafico,
            values=["Barras", "Líneas", "Pastel", "Área"],
            width=10,
            state="readonly"
        )
        combo_grafico.pack(side=tk.LEFT, padx=5)
        combo_grafico.bind("<<ComboboxSelected>>", lambda e: self.actualizar_grafico())

        # Botón para personalizar colores
        btn_colores = tk.Button(
            frame_controles_grafico,
            text="Colores",
            font=("Helvetica", 10),
            bg="#3a7ff6",
            fg="white",
            command=self.personalizar_colores
        )
        btn_colores.pack(side=tk.LEFT, padx=10)

        # Frame para el gráfico
        self.frame_grafico = tk.Frame(self.tab_grafico, bg="white")
        self.frame_grafico.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)

        # Figura inicial vacía
        self.fig = plt.Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, self.frame_grafico)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def cambiar_tipo_reporte(self, event=None):
    tipo_seleccionado = self.tipo_reporte.get()

    # Limpiar tabla existente
    for item in self.tabla_reporte.get_children():
        self.tabla_reporte.delete(item)

    # Configurar columnas según el tipo de reporte
    if tipo_seleccionado == "Ventas por Periodo":
        columnas = ('fecha', 'id_venta', 'cliente', 'total', 'metodo_pago', 'usuario')
        self.tabla_reporte['columns'] = columnas

        # Configurar encabezados
        self.tabla_reporte.heading('fecha', text='Fecha')
        self.tabla_reporte.heading('id_venta', text='ID Venta')
        self.tabla_reporte.heading('cliente', text='Cliente')
        self.tabla_reporte.heading('total', text='Total')
        self.tabla_reporte.heading('metodo_pago', text='Método de Pago')
        self.tabla_reporte.heading('usuario', text='Vendedor')

        # Configurar anchos
        self.tabla_reporte.column('fecha', width=100, anchor=tk.CENTER)
        self.tabla_reporte.column('id_venta', width=70, anchor=tk.CENTER)
        self.tabla_reporte.column('cliente', width=200)
        self.tabla_reporte.column('total', width=100, anchor=tk.E)
        self.tabla_reporte.column('metodo_pago', width=120, anchor=tk.CENTER)
        self.tabla_reporte.column('usuario', width=150)

    elif tipo_seleccionado == "Productos Más Vendidos":
        columnas = ('id_producto', 'nombre', 'cantidad_total', 'ingresos_total')
        self.tabla_reporte['columns'] = columnas

        self.tabla_reporte.heading('id_producto', text='ID')
        self.tabla_reporte.heading('nombre', text='Producto')
        self.tabla_reporte.heading('cantidad_total', text='Cantidad Vendida')
        self.tabla_reporte.heading('ingresos_total', text='Ingresos Generados')

        self.tabla_reporte.column('id_producto', width=50, anchor=tk.CENTER)
        self.tabla_reporte.column('nombre', width=300)
        self.tabla_reporte.column('cantidad_total', width=120, anchor=tk.CENTER)
        self.tabla_reporte.column('ingresos_total', width=150, anchor=tk.E)

    elif tipo_seleccionado == "Servicios Más Solicitados":
        columnas = ('id_servicio', 'nombre', 'cantidad_total', 'ingresos_total')
        self.tabla_reporte['columns'] = columnas

        self.tabla_reporte.heading('id_servicio', text='ID')
        self.tabla_reporte.heading('nombre', text='Servicio')
        self.tabla_reporte.heading('cantidad_total', text='Cantidad Solicitada')
        self.tabla_reporte.heading('ingresos_total', text='Ingresos Generados')

        self.tabla_reporte.column('id_servicio', width=50, anchor=tk.CENTER)
        self.tabla_reporte.column('nombre', width=300)
        self.tabla_reporte.column('cantidad_total', width=120, anchor=tk.CENTER)
        self.tabla_reporte.column('ingresos_total', width=150, anchor=tk.E)

    elif tipo_seleccionado == "Clientes Frecuentes":
        columnas = ('id_cliente', 'nombre', 'visitas', 'gasto_total', 'puntos', 'ultima_visita')
        self.tabla_reporte['columns'] = columnas

        self.tabla_reporte.heading('id_cliente', text='ID')
        self.tabla_reporte.heading('nombre', text='Cliente')
        self.tabla_reporte.heading('visitas', text='Visitas')
        self.tabla_reporte.heading('gasto_total', text='Gasto Total')
        self.tabla_reporte.heading('puntos', text='Puntos')
        self.tabla_reporte.heading('ultima_visita', text='Última Visita')

        self.tabla_reporte.column('id_cliente', width=50, anchor=tk.CENTER)
        self.tabla_reporte.column('nombre', width=200)
        self.tabla_reporte.column('visitas', width=80, anchor=tk.CENTER)
        self.tabla_reporte.column('gasto_total', width=100, anchor=tk.E)
        self.tabla_reporte.column('puntos', width=80, anchor=tk.CENTER)
        self.tabla_reporte.column('ultima_visita', width=120, anchor=tk.CENTER)

    elif tipo_seleccionado == "Ingresos Mensuales":
        columnas = ('mes', 'ventas', 'total_ventas', 'servicios', 'total_servicios', 'total_general')
        self.tabla_reporte['columns'] = columnas

        self.tabla_reporte.heading('mes', text='Mes')
        self.tabla_reporte.heading('ventas', text='Cant. Ventas')
        self.tabla_reporte.heading('total_ventas', text='Total Ventas')
        self.tabla_reporte.heading('servicios', text='Cant. Servicios')
        self.tabla_reporte.heading('total_servicios', text='Total Servicios')
        self.tabla_reporte.heading('total_general', text='Total General')

        self.tabla_reporte.column('mes', width=100, anchor=tk.W)
        self.tabla_reporte.column('ventas', width=100, anchor=tk.CENTER)
        self.tabla_reporte.column('total_ventas', width=120, anchor=tk.E)
        self.tabla_reporte.column('servicios', width=120, anchor=tk.CENTER)
        self.tabla_reporte.column('total_servicios', width=120, anchor=tk.E)
        self.tabla_reporte.column('total_general', width=120, anchor=tk.E)

    elif tipo_seleccionado == "Pedidos por Estado":
        columnas = ('estado', 'cantidad', 'porcentaje')
        self.tabla_reporte['columns'] = columnas

        self.tabla_reporte.heading('estado', text='Estado')
        self.tabla_reporte.heading('cantidad', text='Cantidad')
        self.tabla_reporte.heading('porcentaje', text='Porcentaje')

        self.tabla_reporte.column('estado', width=150, anchor=tk.W)
        self.tabla_reporte.column('cantidad', width=100, anchor=tk.CENTER)
        self.tabla_reporte.column('porcentaje', width=100, anchor=tk.CENTER)

    # Aplicar el periodo actual (por si el cambio de tipo también requiere actualizar fechas)
    self.cambiar_periodo()