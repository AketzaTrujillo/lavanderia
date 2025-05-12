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

    # Insertar nueva caja con la estructura correcta según tu SQL
    # Según tu archivo lavanderia_estructura.sql, la estructura de caja es:
    # CREATE TABLE caja (
    #    id_caja INT AUTO_INCREMENT PRIMARY KEY,
    #    fecha DATE NOT NULL,
    #    hora_apertura TIME,
    #    hora_cierre TIME,
    #    total_ingresos DECIMAL(10,2) DEFAULT 0,
    #    total_egresos DECIMAL(10,2) DEFAULT 0,
    #    saldo_final DECIMAL(10,2) DEFAULT 0,
    #    responsable INT,
    #    FOREIGN KEY (responsable) REFERENCES usuarios(id_usuario)
    # );

    cursor.execute("""
        INSERT INTO caja (fecha, hora_apertura, total_ingresos, total_egresos, saldo_final, responsable)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        fecha_str,
        fecha.strftime('%H:%M:%S'), # hora_apertura es TIME
        0.00,     # Total ingresos
        0.00,     # Total egresos
        1000.00,  # Saldo final
        admin_id  # responsable
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

                # Crear venta
                # Según tu SQL, la estructura de ventas es:
                # CREATE TABLE ventas (
                #    id_venta INT AUTO_INCREMENT PRIMARY KEY,
                #    id_usuario INT,
                #    id_cliente INT,
                #    total DECIMAL(10,2),
                #    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                #    metodo_pago VARCHAR(50),
                #    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
                #    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
                # );
                cursor.execute("""
                    INSERT INTO ventas (id_usuario, id_cliente, total, fecha, metodo_pago)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    id_usuario,
                    id_cliente,
                    0,  # Total inicial, se actualizará después
                    fecha_hora_venta.strftime('%Y-%m-%d %H:%M:%S'),
                    metodo_pago
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
                # Según tu SQL, la estructura de movimientos_caja es:
                # CREATE TABLE movimientos_caja (
                #    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
                #    id_caja INT NOT NULL,
                #    tipo ENUM('ingreso', 'egreso') NOT NULL,
                #    concepto VARCHAR(100) NOT NULL,
                #    monto DECIMAL(10,2) NOT NULL,
                #    hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                #    id_usuario INT,
                #    FOREIGN KEY (id_caja) REFERENCES caja(id_caja),
                #    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
                # );
                cursor.execute("""
                    INSERT INTO movimientos_caja (id_caja, tipo, concepto, monto, hora, id_usuario)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    id_caja,
                    'ingreso',
                    f'Venta #{id_venta}',
                    total_venta,
                    fecha_hora_venta.strftime('%Y-%m-%d %H:%M:%S'),  # hora es DATETIME
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
                # Según tu SQL, la estructura de pagos es:
                # CREATE TABLE pagos (
                #    id_pago INT AUTO_INCREMENT PRIMARY KEY,
                #    id_venta INT,
                #    monto DECIMAL(10,2) NOT NULL,
                #    metodo_pago ENUM('Efectivo', 'Tarjeta', 'Transferencia', 'Otro') NOT NULL,
                #    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                #    referencia VARCHAR(100),
                #    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta)
                # );
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