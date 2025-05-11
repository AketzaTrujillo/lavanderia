"""
Script para generar datos de prueba de ventas para el sistema de lavandería.
Crea múltiples ventas con variedad de clientes, productos y servicios
para el período del 1 al 10 de mayo de 2025.
"""

import random
from datetime import datetime, timedelta
import mysql.connector
from decimal import Decimal
import sys
import os

# Configuración de la base de datos (ajusta según tu configuración)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'tired2019',  # Cambia esto por tu contraseña
    'database': 'lavanderiadb'
}

# Definir fechas de inicio y fin
FECHA_INICIO = datetime(2025, 5, 1)
FECHA_FIN = datetime(2025, 5, 10)

# Número de ventas a generar por día (mínimo y máximo)
MIN_VENTAS_POR_DIA = 5
MAX_VENTAS_POR_DIA = 15

# Métodos de pago disponibles
METODOS_PAGO = ['Efectivo', 'Tarjeta', 'Transferencia']

def conectar_bd():
    """Conecta a la base de datos y devuelve la conexión"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        sys.exit(1)

def obtener_clientes(cursor):
    """Obtiene lista de IDs de clientes"""
    cursor.execute("SELECT id_cliente FROM clientes")
    return [row[0] for row in cursor.fetchall()]

def obtener_usuarios(cursor):
    """Obtiene lista de IDs de usuarios"""
    cursor.execute("SELECT id_usuario FROM usuarios")
    return [row[0] for row in cursor.fetchall()]

def obtener_productos(cursor):
    """Obtiene productos con sus precios"""
    cursor.execute("SELECT id_producto, precio FROM productos WHERE stock > 0")
    return cursor.fetchall()

def obtener_servicios(cursor):
    """Obtiene servicios con sus precios"""
    cursor.execute("SELECT id_servicio, precio FROM servicios")
    return cursor.fetchall()

def obtener_id_caja(cursor, fecha):
    """Obtiene ID de caja para una fecha específica. Crea caja si no existe."""
    fecha_str = fecha.strftime('%Y-%m-%d')

    # Verificar si existe caja para la fecha
    cursor.execute("SELECT id_caja FROM caja WHERE fecha = %s AND hora_cierre IS NULL", (fecha_str,))
    resultado = cursor.fetchone()

    if resultado:
        return resultado[0]

    # Si no existe, crear caja
    # Obtener usuario administrador (id=1) o cualquier otro usuario
    cursor.execute("SELECT id_usuario FROM usuarios WHERE rol = 'admin' LIMIT 1")
    admin_id = cursor.fetchone()

    if not admin_id:
        cursor.execute("SELECT id_usuario FROM usuarios LIMIT 1")
        admin_id = cursor.fetchone()

    admin_id = admin_id[0] if admin_id else 1

    # Insertar nueva caja - utilizando la estructura correcta según tu SQL
    cursor.execute("""
        INSERT INTO caja (fecha, hora_apertura, responsable, monto_inicial, total_ingresos, total_egresos, saldo_final)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        fecha_str,
        fecha.strftime('%H:%M:%S'),
        admin_id,
        1000.00,  # monto_inicial (según tu estructura)
        0.00,     # Total ingresos
        0.00,     # Total egresos
        1000.00   # Saldo final
    ))

    # Obtener ID de la caja recién creada
    cursor.execute("SELECT LAST_INSERT_ID()")
    return cursor.fetchone()[0]

def generar_ventas():
    """Función principal para generar ventas de prueba"""
    conn = conectar_bd()
    cursor = conn.cursor(buffered=True)

    # Obtener datos necesarios
    clientes = obtener_clientes(cursor)
    usuarios = obtener_usuarios(cursor)
    productos = obtener_productos(cursor)
    servicios = obtener_servicios(cursor)

    # Verificar que existan datos
    if not clientes:
        print("No hay clientes en la base de datos")
        return
    if not usuarios:
        print("No hay usuarios en la base de datos")
        return
    if not productos:
        print("No hay productos en la base de datos")
        return
    if not servicios:
        print("No hay servicios en la base de datos")
        return

    # Contador de ventas generadas
    total_ventas = 0

    try:
        # Recorrer cada día en el rango
        fecha_actual = FECHA_INICIO
        while fecha_actual <= FECHA_FIN:
            # Determinar cuántas ventas generar hoy
            ventas_hoy = random.randint(MIN_VENTAS_POR_DIA, MAX_VENTAS_POR_DIA)

            # Obtener id_caja para el día actual
            id_caja = obtener_id_caja(cursor, fecha_actual)

            # Generar ventas para el día
            for _ in range(ventas_hoy):
                # Seleccionar cliente y usuario aleatorios
                id_cliente = random.choice(clientes)
                id_usuario = random.choice(usuarios)

                # Generar hora aleatoria entre 8am y 8pm
                hora_random = random.randint(8, 20)
                minuto_random = random.randint(0, 59)
                fecha_hora_venta = fecha_actual.replace(hour=hora_random, minute=minuto_random)

                # Método de pago aleatorio
                metodo_pago = random.choice(METODOS_PAGO)

                # Crear venta - según la estructura de tu SQL
                cursor.execute("""
                    INSERT INTO ventas (id_usuario, id_cliente, total, metodo_pago, fecha, registrado_en_caja)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    id_usuario,
                    id_cliente,
                    0,  # Total inicial, se actualizará después
                    metodo_pago,
                    fecha_hora_venta.strftime('%Y-%m-%d %H:%M:%S'),
                    True
                ))

                id_venta = cursor.lastrowid

                # Determinar si incluir productos, servicios o ambos
                incluir_productos = random.random() > 0.2  # 80% de probabilidad
                incluir_servicios = random.random() > 0.1  # 90% de probabilidad

                total_venta = Decimal('0.00')

                # Agregar productos
                if incluir_productos and productos:
                    num_productos = random.randint(1, 3)
                    for _ in range(num_productos):
                        # Seleccionar producto aleatorio
                        id_producto, precio = random.choice(productos)
                        cantidad = random.randint(1, 3)
                        subtotal = Decimal(str(precio)) * Decimal(str(cantidad))

                        # Agregar producto a la venta
                        cursor.execute("""
                            INSERT INTO detalle_venta (id_venta, tipo_item, id_item, cantidad, subtotal)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            id_venta,
                            'producto',
                            id_producto,
                            cantidad,
                            subtotal
                        ))

                        total_venta += subtotal

                # Agregar servicios
                if incluir_servicios and servicios:
                    num_servicios = random.randint(1, 4)
                    for _ in range(num_servicios):
                        # Seleccionar servicio aleatorio
                        id_servicio, precio = random.choice(servicios)
                        cantidad = random.randint(1, 5)
                        subtotal = Decimal(str(precio)) * Decimal(str(cantidad))

                        # Agregar servicio a la venta
                        cursor.execute("""
                            INSERT INTO detalle_venta (id_venta, tipo_item, id_item, cantidad, subtotal)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            id_venta,
                            'servicio',
                            id_servicio,
                            cantidad,
                            subtotal
                        ))

                        total_venta += subtotal

                # Actualizar total de la venta
                cursor.execute("""
                    UPDATE ventas SET total = %s WHERE id_venta = %s
                """, (
                    total_venta,
                    id_venta
                ))

                # Registrar movimiento en caja
                cursor.execute("""
                    INSERT INTO movimientos_caja (id_caja, tipo, concepto, monto, hora, id_usuario)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    id_caja,
                    'ingreso',
                    f'Venta #{id_venta}',
                    total_venta,
                    fecha_hora_venta.strftime('%H:%M:%S'),
                    id_usuario
                ))

                # Actualizar totales de caja
                cursor.execute("""
                    UPDATE caja 
                    SET total_ingresos = total_ingresos + %s,
                        saldo_final = saldo_final + %s
                    WHERE id_caja = %s
                """, (
                    total_venta,
                    total_venta,
                    id_caja
                ))

                # Registrar pago
                cursor.execute("""
                    INSERT INTO pagos (id_venta, monto, metodo_pago, fecha_hora)
                    VALUES (%s, %s, %s, %s)
                """, (
                    id_venta,
                    total_venta,
                    metodo_pago,
                    fecha_hora_venta.strftime('%Y-%m-%d %H:%M:%S')
                ))

                # Actualizar puntos del cliente (1 punto por cada 10 pesos)
                puntos_ganados = int(float(total_venta) / 10)
                cursor.execute("""
                    UPDATE clientes SET puntos = puntos + %s WHERE id_cliente = %s
                """, (
                    puntos_ganados,
                    id_cliente
                ))

                # Crear también un pedido para algunas ventas (60% de probabilidad)
                if random.random() < 0.6:
                    # Estados posibles para el pedido
                    estados = ["Recibido", "En proceso", "Listo para entrega", "Entregado"]
                    # Fecha de pedido es un poco anterior a la venta
                    fecha_pedido = fecha_hora_venta - timedelta(days=random.randint(1, 3))

                    # Estado aleatorio
                    estado = random.choice(estados)

                    # Crear pedido
                    cursor.execute("""
                        INSERT INTO pedidos 
                        (id_cliente, fecha_pedido, estado, observaciones, prioridad, fecha_entrega_estimada, convertido_a_venta)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        id_cliente,
                        fecha_pedido.strftime('%Y-%m-%d %H:%M:%S'),
                        estado,
                        "Pedido generado automáticamente para pruebas",
                        random.choice(["Normal", "Alta", "Urgente"]),
                        (fecha_pedido + timedelta(days=random.randint(2, 5))).strftime('%Y-%m-%d'),
                        True if estado == "Entregado" else False
                    ))

                    id_pedido = cursor.lastrowid

                    # Copia los mismos detalles de la venta al pedido (solo servicios)
                    cursor.execute("""
                        INSERT INTO detalle_pedido (id_pedido, tipo_item, id_item, cantidad, precio_unitario)
                        SELECT %s, dv.tipo_item, dv.id_item, dv.cantidad, dv.subtotal / dv.cantidad
                        FROM detalle_venta dv
                        WHERE dv.id_venta = %s AND dv.tipo_item = 'servicio'
                    """, (
                        id_pedido,
                        id_venta
                    ))

                    # Verificar si existe la tabla historial_estados_pedido
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM information_schema.tables 
                        WHERE table_schema = DATABASE() 
                        AND table_name = 'historial_estados_pedido'
                    """)

                    if cursor.fetchone()[0] > 0:
                        # La tabla existe, podemos usarla
                        # Registrar historial de estados
                        if random.random() < 0.7 and id_pedido:  # 70% de probabilidad
                            # Determinar cuántos cambios de estado ha habido
                            if estado == "Recibido":
                                estados_previos = []
                            elif estado == "En proceso":
                                estados_previos = ["Recibido"]
                            elif estado == "Listo para entrega":
                                estados_previos = ["Recibido", "En proceso"]
                            else:  # Entregado
                                estados_previos = ["Recibido", "En proceso", "Listo para entrega"]

                            estado_anterior = None
                            # Para cada cambio de estado, registrar entrada en historial
                            for i, estado_nuevo in enumerate(estados_previos + [estado]):
                                if i > 0:  # Saltamos el primer estado que no tiene anterior
                                    # Fecha del cambio de estado (entre fecha_pedido y fecha_actual)
                                    dias_desde_pedido = random.randint(1, 3) * i
                                    fecha_cambio = fecha_pedido + timedelta(days=dias_desde_pedido)
                                    if fecha_cambio > fecha_actual:
                                        fecha_cambio = fecha_actual

                                    # Insertar registro en historial
                                    cursor.execute("""
                                        INSERT INTO historial_estados_pedido 
                                        (id_pedido, estado_anterior, estado_nuevo, observacion, id_usuario, fecha_cambio)
                                        VALUES (%s, %s, %s, %s, %s, %s)
                                    """, (
                                        id_pedido,
                                        estados_previos[i-1],  # Estado anterior
                                        estado_nuevo,
                                        f"Cambio de estado automático para pruebas",
                                        id_usuario,
                                        fecha_cambio.strftime('%Y-%m-%d %H:%M:%S')
                                    ))

                total_ventas += 1

                # Mostrar progreso
                if total_ventas % 10 == 0:
                    print(f"Generadas {total_ventas} ventas...")

            # Pasar al siguiente día
            fecha_actual += timedelta(days=1)

        # Confirmar cambios
        conn.commit()
        print(f"\n¡Completado! Se generaron {total_ventas} ventas de prueba.")

    except Exception as e:
        conn.rollback()
        print(f"Error al generar ventas: {e}")
        import traceback
        traceback.print_exc()

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Generando datos de prueba de ventas...")
    generar_ventas()
    print("Proceso completado.")