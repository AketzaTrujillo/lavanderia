"""
Script para generar datos de prueba para el Sistema de Gestión de Lavandería
Este script inserta datos realistas en todas las tablas principales de la base de datos
para permitir pruebas completas del sistema.

Modo de uso:
- Asegúrate de tener la base de datos creada con las tablas definidas
- Ejecuta este script una sola vez para llenar la base de datos con datos de prueba
- Si deseas reiniciar, deberás eliminar todos los datos y ejecutar el script nuevamente

Tablas que se llenarán:
- usuarios
- clientes
- servicios
- productos
- pedidos
- detalle_pedido
- ventas
- detalle_venta
- caja
- movimientos_caja
- pagos
"""

import mysql.connector
import random
from datetime import datetime, timedelta
import hashlib
import sys
import os
from decimal import Decimal

# Configuración de la conexión a la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',       # Reemplaza con tu usuario de MySQL
    'password': 'tired2019',       # Reemplaza con tu contraseña de MySQL
    'database': 'lavanderiadb'
}

# Datos de prueba
NOMBRES = [
    "María", "José", "Juan", "Ana", "Carlos", "Laura", "Pedro", "Sofía", "Miguel", "Luisa",
    "Javier", "Patricia", "Roberto", "Diana", "Fernando", "Mónica", "Alberto", "Carmen", "Eduardo", "Silvia",
    "Daniel", "Alejandra", "David", "Gabriela", "Jorge", "Verónica", "Ricardo", "Elena", "Francisco", "Adriana"
]

APELLIDOS = [
    "García", "Rodríguez", "López", "Martínez", "González", "Pérez", "Sánchez", "Ramírez", "Torres", "Flores",
    "Rivera", "Gómez", "Díaz", "Cruz", "Hernández", "Reyes", "Morales", "Jiménez", "Ortiz", "Mendoza",
    "Vargas", "Castillo", "Romero", "Álvarez", "Ruiz", "Navarro", "Ramos", "Moreno", "Vega", "Gutiérrez"
]

DOMICILIOS = [
    "Calle Principal #123", "Av. Revolución #456", "Paseo de la Reforma #789", "Insurgentes Sur #234",
    "Av. Chapultepec #567", "Calle Madero #890", "Blvd. Aeropuerto #321", "Av. Universidad #654",
    "Calzada de Tlalpan #987", "Periférico Sur #210", "Av. Constituyentes #543", "Eje Central #876",
    "Av. Patriotismo #109", "Calle Durango #432", "Av. Juárez #765", "Paseo de la Condesa #098",
    "Av. Coyoacán #345", "Calle Tamaulipas #678", "Av. División del Norte #901", "Circuito Interior #234"
]

COLONIAS = [
    "Centro", "Polanco", "Del Valle", "Condesa", "Roma", "Coyoacán", "Narvarte", "Napoles",
    "San Ángel", "Tlalpan", "Anzures", "Juárez", "Doctores", "Santa Fe", "Pedregal",
    "Lindavista", "Insurgentes", "Portales", "Nápoles", "San Jerónimo"
]

NOMBRES_PRODUCTOS = [
    "Detergente líquido", "Suavizante textil", "Quitamanchas", "Jabón para prendas delicadas",
    "Detergente en polvo", "Blanqueador", "Desmanchador para ropa blanca", "Jabón de barra",
    "Perfume para ropa", "Bolsas para lavandería", "Protector de color", "Detergente para ropa oscura",
    "Ganchos de plástico", "Cesto para ropa", "Bolsas de tintorería", "Almidón para planchar",
    "Aceite para máquina", "Pastillas desodorantes", "Kit de limpieza", "Quita pelusas"
]

NOMBRES_SERVICIOS = [
    "Lavado Normal", "Lavado Express", "Lavado en Seco", "Planchado", "Teñido",
    "Lavado de Edredones", "Lavado de Cobijas", "Lavado de Cortinas", "Lavado de Tapetes",
    "Lavado de Zapatillas", "Desmanchado Especial", "Suavizado Premium",
    "Planchado Express", "Lavado y Planchado", "Lavar y Doblar"
]

CONCEPTOS_MOVIMIENTOS = [
    "Pago de servicio", "Cobro a cliente", "Compra de suministros", "Pago a proveedor",
    "Venta de productos", "Gasto de mantenimiento", "Servicio técnico", "Pago de servicios básicos",
    "Ajuste de caja", "Devolución a cliente", "Adelanto de cliente", "Pago de pedido",
    "Abono a cuenta", "Compra de insumos", "Adelanto para envío", "Gasto de transporte"
]

# Función para conectar a la base de datos
def conectar_bd():
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        return conexion
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        sys.exit(1)

# Función para ejecutar consultas SQL
def ejecutar_consulta(conexion, consulta, parametros=None):
    cursor = conexion.cursor()
    try:
        if parametros:
            cursor.execute(consulta, parametros)
        else:
            cursor.execute(consulta)
        conexion.commit()
        return cursor
    except mysql.connector.Error as err:
        print(f"Error al ejecutar consulta: {err}")
        print(f"Consulta: {consulta}")
        print(f"Parámetros: {parametros}")
        conexion.rollback()
        return None

# Función para obtener el ID de la última inserción
def obtener_ultimo_id(conexion):
    cursor = conexion.cursor()
    cursor.execute("SELECT LAST_INSERT_ID()")
    return cursor.fetchone()[0]

# Función para generar una contraseña aleatoria
def generar_contrasena():
    return ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for _ in range(8))

# Función principal para generar todos los datos de prueba
def generar_datos_prueba():
    conexion = conectar_bd()
    print("Conectado a la base de datos")

    # 1. Verificar si ya hay datos en las tablas principales
    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    num_usuarios = cursor.fetchone()[0]

    if num_usuarios > 1:
        print("La base de datos ya tiene datos. ¿Deseas continuar y agregar más datos? (s/n)")
        respuesta = input().lower()
        if respuesta != 's':
            print("Operación cancelada")
            conexion.close()
            return

    # 2. Insertar usuarios
    print("Insertando usuarios...")
    insertar_usuarios(conexion)

    # 3. Insertar clientes
    print("Insertando clientes...")
    insertar_clientes(conexion)

    # 4. Insertar productos
    print("Insertando productos...")
    insertar_productos(conexion)

    # 5. Insertar servicios
    print("Insertando servicios...")
    insertar_servicios(conexion)

    # 6. Insertar cajas
    print("Insertando cajas...")
    insertar_cajas(conexion)

    # 7. Insertar pedidos y ventas
    print("Insertando pedidos, ventas y movimientos...")
    insertar_pedidos_ventas(conexion)

    print("¡Datos de prueba generados correctamente!")
    conexion.close()

def insertar_usuarios(conexion):
    # Asegurarse de que exista el administrador principal
    cursor = conexion.cursor()
    cursor.execute("SELECT id_usuario FROM usuarios WHERE correo = 'admin@lavanderia.com'")
    if not cursor.fetchone():
        consulta = """
        INSERT INTO usuarios (nombre, correo, contraseña, rol)
        VALUES ('Administrador', 'admin@lavanderia.com', '1234', 'admin')
        """
        ejecutar_consulta(conexion, consulta)

    # Insertar cajeros
    nombres_cajeros = [
        "Ana Gutiérrez", "Carlos Ramírez", "Laura Mendoza", "Roberto Vargas", "Patricia Soto"
    ]

    for i, nombre in enumerate(nombres_cajeros):
        parts = nombre.split()
        correo = f"{parts[0].lower()}.{parts[1].lower()}@lavanderia.com"
        contrasena = "1234"  # En un sistema real usar hash

        consulta = """
        INSERT INTO usuarios (nombre, correo, contraseña, rol)
        VALUES (%s, %s, %s, 'cajero')
        """
        ejecutar_consulta(conexion, consulta, (nombre, correo, contrasena))
        print(f"  Usuario insertado: {nombre} ({correo})")

def insertar_clientes(conexion):
    # Generar clientes aleatorios
    num_clientes = 50

    for i in range(num_clientes):
        nombre = random.choice(NOMBRES)
        apellido1 = random.choice(APELLIDOS)
        apellido2 = random.choice(APELLIDOS)
        nombre_completo = f"{nombre} {apellido1} {apellido2}"

        # Generar teléfono aleatorio
        telefono = f"55{random.randint(10000000, 99999999)}"

        # Generar correo
        dominio = random.choice(["gmail.com", "hotmail.com", "yahoo.com", "outlook.com"])
        correo = f"{nombre.lower()}.{apellido1.lower()}{random.randint(1, 99)}@{dominio}"

        # Puntos aleatorios
        puntos = random.randint(0, 500)

        # Fecha de registro aleatoria en los últimos 2 años
        dias_atras = random.randint(1, 730)
        fecha_registro = (datetime.now() - timedelta(days=dias_atras)).strftime("%Y-%m-%d %H:%M:%S")

        consulta = """
        INSERT INTO clientes (nombre, telefono, correo, puntos, fecha_registro)
        VALUES (%s, %s, %s, %s, %s)
        """
        ejecutar_consulta(conexion, consulta, (nombre_completo, telefono, correo, puntos, fecha_registro))

    print(f"  {num_clientes} clientes insertados")

def insertar_productos(conexion):
    # Generar productos aleatorios
    for nombre in NOMBRES_PRODUCTOS:
        precio = round(random.uniform(15.0, 200.0), 2)
        stock = random.randint(10, 100)

        consulta = """
        INSERT INTO productos (nombre, precio, stock)
        VALUES (%s, %s, %s)
        """
        ejecutar_consulta(conexion, consulta, (nombre, precio, stock))

    print(f"  {len(NOMBRES_PRODUCTOS)} productos insertados")

def insertar_servicios(conexion):
    # Verificar si ya hay servicios
    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM servicios")
    if cursor.fetchone()[0] > 0:
        print("  Ya existen servicios en la base de datos. Omitiendo...")
        return

    # Precios base y tiempos para cada servicio
    precios_base = {
        "Lavado Normal": 60.0,
        "Lavado Express": 90.0,
        "Lavado en Seco": 120.0,
        "Planchado": 40.0,
        "Teñido": 150.0,
        "Lavado de Edredones": 180.0,
        "Lavado de Cobijas": 130.0,
        "Lavado de Cortinas": 160.0,
        "Lavado de Tapetes": 200.0,
        "Lavado de Zapatillas": 110.0,
        "Desmanchado Especial": 70.0,
        "Suavizado Premium": 50.0,
        "Planchado Express": 60.0,
        "Lavado y Planchado": 100.0,
        "Lavar y Doblar": 80.0
    }

    tiempos_base = {
        "Lavado Normal": 60,
        "Lavado Express": 30,
        "Lavado en Seco": 90,
        "Planchado": 45,
        "Teñido": 120,
        "Lavado de Edredones": 120,
        "Lavado de Cobijas": 90,
        "Lavado de Cortinas": 120,
        "Lavado de Tapetes": 150,
        "Lavado de Zapatillas": 90,
        "Desmanchado Especial": 60,
        "Suavizado Premium": 45,
        "Planchado Express": 30,
        "Lavado y Planchado": 100,
        "Lavar y Doblar": 75
    }

    for nombre in NOMBRES_SERVICIOS:
        precio_base = precios_base.get(nombre, 50.0)  # Si no está en el diccionario, usar 50.0
        # Aplicar variación aleatoria al precio
        precio = round(precio_base * random.uniform(0.9, 1.1), 2)

        tiempo_base = tiempos_base.get(nombre, 60)  # Si no está en el diccionario, usar 60
        tiempo_estimado = tiempo_base

        descripcion = f"Servicio de {nombre.lower()} profesional para todo tipo de prendas."

        consulta = """
        INSERT INTO servicios (nombre, descripcion, precio, tiempo_estimado, activo)
        VALUES (%s, %s, %s, %s, 1)
        """
        ejecutar_consulta(conexion, consulta, (nombre, descripcion, precio, tiempo_estimado))

    print(f"  {len(NOMBRES_SERVICIOS)} servicios insertados")

def insertar_cajas(conexion):
    # Verificar si ya hay cajas
    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM caja")
    if cursor.fetchone()[0] > 0:
        print("  Ya existen cajas en la base de datos. Omitiendo...")
        return

    # Obtener IDs de usuarios
    cursor.execute("SELECT id_usuario FROM usuarios WHERE rol = 'cajero' OR rol = 'admin'")
    usuarios = [row[0] for row in cursor.fetchall()]

    if not usuarios:
        print("  No hay usuarios para asignar como responsables de caja")
        return

    # Generar cajas para los últimos 30 días
    for i in range(30, 0, -1):
        fecha = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")

        # Hora de apertura y cierre (la caja del día actual estará abierta)
        hora_apertura = "08:00:00"
        hora_cierre = None if i == 1 else "20:00:00"

        # Monto inicial
        monto_inicial = random.uniform(500.0, 1000.0)

        # Ingresos y egresos aleatorios
        if i > 1:  # Solo para cajas cerradas
            total_ingresos = round(random.uniform(2000.0, 8000.0), 2)
            total_egresos = round(random.uniform(300.0, 1000.0), 2)
            saldo_final = monto_inicial + total_ingresos - total_egresos
        else:  # Caja actual (abierta)
            total_ingresos = 0.0
            total_egresos = 0.0
            saldo_final = monto_inicial

        # Responsable aleatorio
        responsable = random.choice(usuarios)

        # Insertar caja
        consulta = """
        INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        parametros = (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable)
        ejecutar_consulta(conexion, consulta, parametros)

        id_caja = obtener_ultimo_id(conexion)

        # Insertar movimiento inicial
        consulta_mov = """
        INSERT INTO movimientos_caja (id_caja, tipo, concepto, monto, hora, id_usuario)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        fecha_hora = f"{fecha} {hora_apertura}"
        ejecutar_consulta(conexion, consulta_mov, (id_caja, "ingreso", "Saldo inicial", monto_inicial, fecha_hora, responsable))

        # Insertar movimientos aleatorios para cajas cerradas
        if i > 1:
            # Número de movimientos aleatorio
            num_movimientos = random.randint(5, 15)

            for j in range(num_movimientos):
                tipo = random.choice(["ingreso", "egreso"])
                concepto = random.choice(CONCEPTOS_MOVIMIENTOS)

                # El monto depende del tipo
                if tipo == "ingreso":
                    monto = round(random.uniform(100.0, 500.0), 2)
                else:
                    monto = round(random.uniform(50.0, 200.0), 2)

                # Hora aleatoria entre apertura y cierre
                hora_mov = f"{random.randint(8, 19)}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
                fecha_hora_mov = f"{fecha} {hora_mov}"

                ejecutar_consulta(conexion, consulta_mov, (id_caja, tipo, concepto, monto, fecha_hora_mov, responsable))

    print(f"  30 cajas insertadas con sus movimientos")

def insertar_pedidos_ventas(conexion):
    # Obtener IDs de clientes
    cursor = conexion.cursor()
    cursor.execute("SELECT id_cliente FROM clientes")
    clientes = [row[0] for row in cursor.fetchall()]

    if not clientes:
        print("  No hay clientes para asignar pedidos")
        return

    # Obtener IDs de usuarios
    cursor.execute("SELECT id_usuario FROM usuarios WHERE rol = 'cajero' OR rol = 'admin'")
    usuarios = [row[0] for row in cursor.fetchall()]

    if not usuarios:
        print("  No hay usuarios para asignar como responsables")
        return

    # Obtener IDs de productos
    cursor.execute("SELECT id_producto, precio FROM productos")
    productos = [(row[0], float(row[1])) for row in cursor.fetchall()]  # Convertir Decimal a float

    # Obtener IDs de servicios
    cursor.execute("SELECT id_servicio, precio FROM servicios")
    servicios = [(row[0], float(row[1])) for row in cursor.fetchall()]  # Convertir Decimal a float

    # Obtener IDs de cajas
    cursor.execute("SELECT id_caja, fecha FROM caja")
    cajas = [(row[0], row[1]) for row in cursor.fetchall()]

    if not cajas:
        print("  No hay cajas para registrar ventas")
        return

    # Generar entre 50 y 100 pedidos
    num_pedidos = random.randint(50, 100)

    # Estados posibles para pedidos
    estados = ["Recibido", "En proceso", "Listo para entrega", "Entregado"]
    prioridades = ["Normal", "Alta", "Urgente"]

    # Para cada caja, generar pedidos y ventas
    pedidos_creados = 0
    ventas_creadas = 0

    for id_caja, fecha_caja in cajas:
        # Convertir fecha_caja a objeto datetime
        fecha_obj = datetime.strptime(str(fecha_caja), "%Y-%m-%d")

        # Número de pedidos para esta caja
        num_pedidos_caja = random.randint(2, 8)

        for _ in range(num_pedidos_caja):
            if pedidos_creados >= num_pedidos:
                break

            # Datos del pedido
            id_cliente = random.choice(clientes)
            estado = random.choice(estados)
            fecha_pedido = f"{fecha_caja} {random.randint(8, 19)}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
            prioridad = random.choice(prioridades)

            # Observaciones aleatorias
            observaciones_opciones = [
                "Cliente solicita entrega urgente",
                "Manchas difíciles en algunas prendas",
                "Cliente pagará al recoger",
                "Usar detergente hipoalergénico",
                "No usar suavizante",
                None  # Posibilidad de no tener observaciones
            ]
            observaciones = random.choice(observaciones_opciones)

            # Fecha de entrega estimada (2-5 días después)
            dias_entrega = random.randint(2, 5)
            fecha_entrega = (fecha_obj + timedelta(days=dias_entrega)).strftime("%Y-%m-%d")

            # Insertar pedido
            consulta_pedido = """
            INSERT INTO pedidos (id_cliente, fecha_pedido, estado, prioridad, observaciones, fecha_entrega_estimada, convertido_a_venta)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            convertido = True if estado == "Entregado" else False

            ejecutar_consulta(conexion, consulta_pedido, (id_cliente, fecha_pedido, estado, prioridad, observaciones, fecha_entrega, convertido))
            id_pedido = obtener_ultimo_id(conexion)

            # Insertar detalles del pedido (1-5 items)
            num_items = random.randint(1, 5)
            total_pedido = 0.0  # Inicializar como float

            for _ in range(num_items):
                # Decidir si es producto o servicio
                tipo_item = random.choice(["producto", "servicio"])

                if tipo_item == "producto" and productos:
                    id_item, precio = random.choice(productos)
                    cantidad = random.randint(1, 3)
                elif servicios:
                    tipo_item = "servicio"  # Forzar servicio si no hay productos
                    id_item, precio = random.choice(servicios)
                    cantidad = random.randint(1, 5)
                else:
                    continue  # Saltar si no hay productos ni servicios

                # Asegurarse de que precio y cantidad sean float
                precio_float = float(precio)
                cantidad_float = float(cantidad)
                subtotal = precio_float * cantidad_float
                total_pedido += subtotal

                consulta_detalle = """
                INSERT INTO detalle_pedido (id_pedido, tipo_item, id_item, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s, %s)
                """
                ejecutar_consulta(conexion, consulta_detalle, (id_pedido, tipo_item, id_item, cantidad, precio_float))

            # Si el pedido está entregado, crear una venta asociada
            if estado == "Entregado" and convertido:
                id_usuario = random.choice(usuarios)
                metodo_pago = random.choice(["Efectivo", "Tarjeta", "Transferencia"])

                # Crear venta
                consulta_venta = """
                INSERT INTO ventas (id_usuario, id_cliente, total, metodo_pago, id_pedido, fecha, registrado_en_caja)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """

                fecha_venta = f"{fecha_caja} {random.randint(8, 19)}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"

                ejecutar_consulta(conexion, consulta_venta, (id_usuario, id_cliente, total_pedido, metodo_pago, id_pedido, fecha_venta, True))
                id_venta = obtener_ultimo_id(conexion)

                # Copiar detalles a la venta
                consulta_copiar = """
                INSERT INTO detalle_venta (id_venta, tipo_item, id_item, cantidad, subtotal)
                SELECT %s, tipo_item, id_item, cantidad, (cantidad * precio_unitario)
                FROM detalle_pedido
                WHERE id_pedido = %s
                """
                ejecutar_consulta(conexion, consulta_copiar, (id_venta, id_pedido))

                # Registrar pago
                consulta_pago = """
                INSERT INTO pagos (id_venta, monto, metodo_pago, fecha_hora)
                VALUES (%s, %s, %s, %s)
                """
                ejecutar_consulta(conexion, consulta_pago, (id_venta, total_pedido, metodo_pago, fecha_venta))

                # Registrar movimiento en caja
                consulta_mov = """
                INSERT INTO movimientos_caja (id_caja, tipo, concepto, monto, hora, id_usuario)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                ejecutar_consulta(conexion, consulta_mov, (id_caja, "ingreso", f"Venta #{id_venta} (Pedido #{id_pedido})", total_pedido, fecha_venta, id_usuario))

                ventas_creadas += 1

            pedidos_creados += 1

            if pedidos_creados % 10 == 0:
                print(f"  {pedidos_creados} pedidos creados...")

    print(f"  {pedidos_creados} pedidos y {ventas_creadas} ventas creadas")

# Ejecutar el script si se llama directamente
if __name__ == "__main__":
    print("Script de generación de datos de prueba para el Sistema de Gestión de Lavandería")
    print("Este script insertará datos aleatorios en la base de datos.")
    print()
    print("ADVERTENCIA: Este script debe ejecutarse solo una vez en un entorno de pruebas.")
    print("             Ejecutarlo múltiples veces puede generar datos duplicados.")
    print()

    respuesta = input("¿Deseas continuar? (s/n): ").lower()
    if respuesta == 's':
        generar_datos_prueba()
    else:
        print("Operación cancelada")