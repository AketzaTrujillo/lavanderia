-- =========================================================
-- SCRIPT COMPLETO Y UNIFICADO - SISTEMA LAVANDERÍA
-- =========================================================
-- Versión: 2.0 - SIMPLIFICADA Y SIN DUPLICACIONES
-- Fecha: 2024
-- Descripción: Script completo que BORRA TODO Y RECREA desde cero
-- IMPORTANTE: Este script ELIMINA toda la base de datos existente
-- =========================================================

-- =========================================================
-- PASO 1: ELIMINAR TODO (SI EXISTE)
-- =========================================================

-- Eliminar base de datos completa si existe
DROP DATABASE IF EXISTS lavanderiadb;

-- Crear nueva base de datos
CREATE DATABASE lavanderiadb;
USE lavanderiadb;

-- =========================================================
-- PASO 2: CREAR TODAS LAS TABLAS
-- =========================================================

-- Tabla usuarios
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'cajero') NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla clientes
CREATE TABLE clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(15),
    correo VARCHAR(100),
    puntos INT DEFAULT 0,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla productos
CREATE TABLE productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    precio DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0
);

-- Tabla servicios
CREATE TABLE servicios (
    id_servicio INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL,
    tiempo_estimado INT NOT NULL,
    activo TINYINT(1) DEFAULT 1
);

-- Tabla pedidos
CREATE TABLE pedidos (
    id_pedido INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    fecha_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('Recibido', 'En proceso', 'Listo para entrega', 'Entregado') DEFAULT 'Recibido',
    prioridad ENUM('Baja', 'Normal', 'Alta', 'Urgente') DEFAULT 'Normal',
    observaciones TEXT,
    fecha_entrega_estimada DATE,
    convertido_a_venta BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE CASCADE
);

-- Tabla detalle_pedido
CREATE TABLE detalle_pedido (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido INT NOT NULL,
    tipo_item ENUM('producto', 'servicio') NOT NULL,
    id_item INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido) ON DELETE CASCADE
);

-- Tabla ventas (SIN campo registrado_en_caja - SIMPLIFICADA)
CREATE TABLE ventas (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_cliente INT NOT NULL,
    id_pedido INT DEFAULT NULL,
    total DECIMAL(10,2) NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    metodo_pago VARCHAR(50),
    descuento_aplicado DECIMAL(10,2) DEFAULT 0,
    puntos_ganados INT DEFAULT 0,
    puntos_utilizados INT DEFAULT 0,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido)
);

-- Tabla detalle_venta
CREATE TABLE detalle_venta (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT NOT NULL,
    tipo_item ENUM('producto', 'servicio') NOT NULL,
    id_item INT NOT NULL,
    cantidad INT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE CASCADE
);

-- Tabla caja
CREATE TABLE caja (
    id_caja INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    hora_apertura TIME,
    hora_cierre TIME,
    monto_inicial DECIMAL(10,2) DEFAULT 0.00,
    total_ingresos DECIMAL(10,2) DEFAULT 0,
    total_egresos DECIMAL(10,2) DEFAULT 0,
    saldo_final DECIMAL(10,2) DEFAULT 0,
    responsable INT NOT NULL,
    FOREIGN KEY (responsable) REFERENCES usuarios(id_usuario)
);

-- Tabla movimientos_caja
CREATE TABLE movimientos_caja (
    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    id_caja INT NOT NULL,
    tipo ENUM('ingreso', 'egreso') NOT NULL,
    concepto VARCHAR(100) NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_usuario INT NOT NULL,
    FOREIGN KEY (id_caja) REFERENCES caja(id_caja),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- Tabla pagos
CREATE TABLE pagos (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    metodo_pago ENUM('Efectivo', 'Tarjeta', 'Transferencia', 'Otro') NOT NULL,
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    referencia VARCHAR(100),
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta)
);

-- Tabla gastos
CREATE TABLE gastos (
    id_gasto INT AUTO_INCREMENT PRIMARY KEY,
    concepto VARCHAR(100) NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    fecha DATE NOT NULL,
    id_usuario INT NOT NULL,
    comprobante VARCHAR(255),
    observaciones TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- Tabla arqueos_caja
CREATE TABLE arqueos_caja (
    id_arqueo INT AUTO_INCREMENT PRIMARY KEY,
    id_caja INT NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    saldo_sistema DECIMAL(10,2) NOT NULL,
    efectivo_contado DECIMAL(10,2) NOT NULL,
    diferencia DECIMAL(10,2) NOT NULL,
    observaciones TEXT,
    id_usuario INT NOT NULL,
    FOREIGN KEY (id_caja) REFERENCES caja(id_caja),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- Tabla configuracion
CREATE TABLE configuracion (
    id_configuracion INT AUTO_INCREMENT PRIMARY KEY,
    nombre_empresa VARCHAR(100) NOT NULL,
    direccion VARCHAR(200),
    telefono VARCHAR(20),
    rfc VARCHAR(20),
    logo VARCHAR(255),
    impresora_predeterminada VARCHAR(100),
    moneda VARCHAR(3) DEFAULT 'MXN',
    iva DECIMAL(5,2) DEFAULT 16.00,
    puntos_por_compra INT DEFAULT 1,
    valor_punto_en_dinero DECIMAL(10,2) DEFAULT 0.10
);

-- Tabla promociones
CREATE TABLE promociones (
    id_promocion INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    tipo ENUM('porcentaje', 'monto_fijo', 'puntos') NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    id_usuario_creador INT,
    FOREIGN KEY (id_usuario_creador) REFERENCES usuarios(id_usuario)
);

-- Tabla respaldos
CREATE TABLE respaldos (
    id_respaldo INT AUTO_INCREMENT PRIMARY KEY,
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    ruta VARCHAR(255) NOT NULL,
    tamanio BIGINT,
    id_usuario INT,
    descripcion TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- Tabla historial_estados_pedido
CREATE TABLE historial_estados_pedido (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido INT NOT NULL,
    estado_anterior VARCHAR(50),
    estado_nuevo VARCHAR(50),
    observacion TEXT,
    id_usuario INT,
    fecha_cambio DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- =========================================================
-- PASO 3: CREAR ÍNDICES (INCLUYENDO ÚNICOS PARA PREVENIR DUPLICADOS)
-- =========================================================

-- Índices básicos para rendimiento
CREATE INDEX idx_pedidos_estado ON pedidos(estado);
CREATE INDEX idx_pedidos_fecha ON pedidos(fecha_pedido);
CREATE INDEX idx_pedidos_prioridad ON pedidos(prioridad);
CREATE INDEX idx_ventas_fecha ON ventas(fecha);
CREATE INDEX idx_ventas_pedido ON ventas(id_pedido);
CREATE INDEX idx_caja_fecha ON caja(fecha);
CREATE INDEX idx_movimientos_caja_id_caja ON movimientos_caja(id_caja);
CREATE INDEX idx_movimientos_caja_tipo ON movimientos_caja(tipo);
CREATE INDEX idx_clientes_nombre ON clientes(nombre);
CREATE INDEX idx_historial_pedido ON historial_estados_pedido(id_pedido);

-- Índices únicos para PREVENIR DUPLICADOS
CREATE UNIQUE INDEX idx_productos_nombre_unico ON productos(nombre);
CREATE UNIQUE INDEX idx_movimientos_venta_unico ON movimientos_caja(concepto, id_caja);

-- =========================================================
-- PASO 4: CREAR VISTAS
-- =========================================================

-- Vista para resumen de pedidos por estado
CREATE VIEW resumen_pedidos_estado AS
SELECT
    estado,
    COUNT(*) as cantidad,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM pedidos), 2) as porcentaje,
    COALESCE(SUM(
        (SELECT SUM(dp.cantidad * dp.precio_unitario)
         FROM detalle_pedido dp
         WHERE dp.id_pedido = p.id_pedido)
    ), 0) as total_ventas
FROM pedidos p
GROUP BY estado;

-- Vista para pedidos con información completa
CREATE VIEW vista_pedidos_completos AS
SELECT
    p.id_pedido,
    p.fecha_pedido,
    p.estado,
    p.prioridad,
    p.observaciones,
    p.fecha_entrega_estimada,
    c.id_cliente,
    c.nombre as cliente,
    c.telefono as telefono_cliente,
    c.correo as correo_cliente,
    u.id_usuario,
    u.nombre as usuario,
    COALESCE((SELECT SUM(dp.cantidad * dp.precio_unitario)
     FROM detalle_pedido dp
     WHERE dp.id_pedido = p.id_pedido), 0) as total
FROM pedidos p
INNER JOIN clientes c ON p.id_cliente = c.id_cliente
LEFT JOIN ventas v ON v.id_pedido = p.id_pedido
LEFT JOIN usuarios u ON v.id_usuario = u.id_usuario;

-- Vista para resumen de caja
CREATE VIEW vista_resumen_caja AS
SELECT
    c.id_caja,
    c.fecha,
    c.hora_apertura,
    c.hora_cierre,
    c.total_ingresos,
    c.total_egresos,
    c.saldo_final,
    u.nombre AS responsable,
    (SELECT COUNT(*) FROM movimientos_caja m WHERE m.id_caja = c.id_caja AND m.tipo = 'ingreso') AS num_ingresos,
    (SELECT COUNT(*) FROM movimientos_caja m WHERE m.id_caja = c.id_caja AND m.tipo = 'egreso') AS num_egresos,
    (SELECT COUNT(DISTINCT SUBSTRING_INDEX(SUBSTRING_INDEX(concepto, '#', -1), ' ', 1))
     FROM movimientos_caja m WHERE m.id_caja = c.id_caja AND m.concepto LIKE 'Venta #%') AS num_ventas,
    (c.hora_cierre IS NULL) AS caja_abierta
FROM caja c
JOIN usuarios u ON c.responsable = u.id_usuario;

-- Vista para pedidos entregados pendientes de conversión a venta
CREATE VIEW vista_pedidos_entregados AS
SELECT
    p.id_pedido,
    p.fecha_pedido,
    p.estado,
    p.id_cliente,
    c.nombre as cliente,
    c.correo,
    COALESCE((SELECT SUM(dp.cantidad * dp.precio_unitario)
     FROM detalle_pedido dp
     WHERE dp.id_pedido = p.id_pedido), 0) as total,
    p.convertido_a_venta,
    u.nombre as responsable
FROM pedidos p
INNER JOIN clientes c ON p.id_cliente = c.id_cliente
LEFT JOIN ventas v ON v.id_pedido = p.id_pedido
LEFT JOIN usuarios u ON v.id_usuario = u.id_usuario
WHERE p.estado = 'Entregado' AND p.convertido_a_venta = FALSE;

-- Vista para rentabilidad de servicios
CREATE VIEW vista_rentabilidad_servicios AS
SELECT
    dv.tipo_item,
    dv.id_item,
    CASE
        WHEN dv.tipo_item = 'producto' THEN p.nombre
        WHEN dv.tipo_item = 'servicio' THEN s.nombre
        ELSE 'Desconocido'
    END as nombre_item,
    COUNT(*) as veces_vendido,
    SUM(dv.cantidad) as cantidad_total,
    SUM(dv.subtotal) as ingreso_total,
    AVG(dv.subtotal) as promedio_por_venta,
    DATE_FORMAT(v.fecha, '%Y-%m') as mes_anio
FROM detalle_venta dv
INNER JOIN ventas v ON dv.id_venta = v.id_venta
LEFT JOIN productos p ON dv.tipo_item = 'producto' AND dv.id_item = p.id_producto
LEFT JOIN servicios s ON dv.tipo_item = 'servicio' AND dv.id_item = s.id_servicio
GROUP BY dv.tipo_item, dv.id_item, DATE_FORMAT(v.fecha, '%Y-%m')
ORDER BY ingreso_total DESC;

-- Vista para verificar coherencia del sistema
CREATE VIEW vista_coherencia_sistema AS
SELECT
    'Ventas sin movimiento en caja' as tipo_problema,
    COUNT(*) as cantidad,
    GROUP_CONCAT(v.id_venta SEPARATOR ', ') as ids_afectados
FROM ventas v
LEFT JOIN movimientos_caja mc ON mc.concepto LIKE CONCAT('Venta #', v.id_venta, '%')
WHERE mc.id_movimiento IS NULL

UNION ALL

SELECT
    'Movimientos duplicados por venta' as tipo_problema,
    COUNT(*) as cantidad,
    GROUP_CONCAT(concepto SEPARATOR ', ') as ids_afectados
FROM (
    SELECT concepto
    FROM movimientos_caja
    WHERE concepto LIKE 'Venta #%'
    GROUP BY concepto, id_caja
    HAVING COUNT(*) > 1
) duplicados

UNION ALL

SELECT
    'Pedidos entregados sin venta' as tipo_problema,
    COUNT(*) as cantidad,
    GROUP_CONCAT(p.id_pedido SEPARATOR ', ') as ids_afectados
FROM pedidos p
WHERE p.estado = 'Entregado' AND p.convertido_a_venta = FALSE

UNION ALL

SELECT
    'Ventas sin pago registrado' as tipo_problema,
    COUNT(*) as cantidad,
    GROUP_CONCAT(v.id_venta SEPARATOR ', ') as ids_afectados
FROM ventas v
LEFT JOIN pagos p ON v.id_venta = p.id_venta
WHERE p.id_pago IS NULL

UNION ALL

SELECT
    'Cajas con saldo inconsistente' as tipo_problema,
    COUNT(*) as cantidad,
    GROUP_CONCAT(c.id_caja SEPARATOR ', ') as ids_afectados
FROM caja c
WHERE ABS(c.saldo_final - (c.total_ingresos - c.total_egresos)) > 0.01;

-- =========================================================
-- PASO 5: CREAR PROCEDIMIENTOS ALMACENADOS
-- =========================================================

-- Procedimiento para convertir pedido a venta
DELIMITER //
CREATE PROCEDURE ConvertirPedidoAVenta(
    IN p_id_pedido INT,
    IN p_id_usuario INT,
    IN p_metodo_pago VARCHAR(50),
    OUT p_id_venta INT
)
BEGIN
    DECLARE v_id_cliente INT;
    DECLARE v_total DECIMAL(10,2);
    DECLARE v_id_caja INT;
    DECLARE v_error_msg VARCHAR(255);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1 v_error_msg = MESSAGE_TEXT;
        ROLLBACK;
        SET p_id_venta = -1;
        SELECT CONCAT('Error al convertir pedido a venta: ', v_error_msg) AS mensaje_error;
    END;

    START TRANSACTION;

    -- Verificar que el pedido existe y no ha sido convertido
    SELECT id_cliente, convertido_a_venta INTO v_id_cliente, @convertido
    FROM pedidos WHERE id_pedido = p_id_pedido;

    IF v_id_cliente IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Pedido no encontrado';
    END IF;

    IF @convertido = TRUE THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Pedido ya fue convertido a venta';
    END IF;

    -- Calcular total del pedido
    SELECT SUM(cantidad * precio_unitario) INTO v_total
    FROM detalle_pedido WHERE id_pedido = p_id_pedido;

    -- Crear la venta
    INSERT INTO ventas (id_usuario, id_cliente, total, metodo_pago, id_pedido, fecha)
    VALUES (p_id_usuario, v_id_cliente, v_total, p_metodo_pago, p_id_pedido, NOW());

    SET p_id_venta = LAST_INSERT_ID();

    -- Copiar detalles del pedido a detalle de venta
    INSERT INTO detalle_venta (id_venta, tipo_item, id_item, cantidad, subtotal)
    SELECT p_id_venta, dp.tipo_item, dp.id_item, dp.cantidad,
           (dp.cantidad * dp.precio_unitario)
    FROM detalle_pedido dp WHERE dp.id_pedido = p_id_pedido;

    -- Actualizar puntos del cliente
    UPDATE clientes SET puntos = puntos + FLOOR(v_total / 10)
    WHERE id_cliente = v_id_cliente;

    -- Marcar el pedido como convertido
    UPDATE pedidos SET convertido_a_venta = TRUE WHERE id_pedido = p_id_pedido;

    COMMIT;
END //
DELIMITER ;

-- =========================================================
-- PASO 6: CREAR FUNCIONES
-- =========================================================

-- Función para calcular puntos
DELIMITER //
CREATE FUNCTION CalcularPuntos(p_total DECIMAL(10,2))
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_puntos_por_compra INT DEFAULT 1;

    -- Obtener configuración de puntos si existe
    SELECT COALESCE(puntos_por_compra, 1) INTO v_puntos_por_compra
    FROM configuracion LIMIT 1;

    RETURN FLOOR(p_total / 10) * v_puntos_por_compra;
END //
DELIMITER ;

-- =========================================================
-- PASO 7: CREAR TRIGGER AUTOMÁTICO (SIMPLE Y EFECTIVO)
-- =========================================================

DELIMITER //
CREATE TRIGGER trigger_venta_a_caja
AFTER INSERT ON ventas
FOR EACH ROW
BEGIN
    DECLARE v_id_caja INT;

    -- Buscar caja abierta para la fecha de la venta
    SELECT id_caja INTO v_id_caja
    FROM caja
    WHERE fecha = DATE(NEW.fecha) AND hora_cierre IS NULL
    LIMIT 1;

    -- Si hay caja abierta, registrar el movimiento
    IF v_id_caja IS NOT NULL THEN
        -- Insertar movimiento de ingreso (con manejo de duplicados)
        INSERT IGNORE INTO movimientos_caja (id_caja, tipo, concepto, monto, hora, id_usuario)
        VALUES (v_id_caja, 'ingreso',
                CONCAT('Venta #', NEW.id_venta, ' - ', COALESCE(NEW.metodo_pago, 'N/A')),
                NEW.total, NEW.fecha, NEW.id_usuario);

        -- Actualizar totales de caja
        IF NEW.metodo_pago = 'Efectivo' THEN
            -- Para efectivo: aumentar ingresos Y saldo físico
            UPDATE caja
            SET total_ingresos = total_ingresos + NEW.total,
                saldo_final = saldo_final + NEW.total
            WHERE id_caja = v_id_caja;
        ELSE
            -- Para pagos electrónicos: solo aumentar ingresos (contabilidad)
            UPDATE caja
            SET total_ingresos = total_ingresos + NEW.total
            WHERE id_caja = v_id_caja;
        END IF;
    END IF;
END //
DELIMITER ;

-- =========================================================
-- PASO 8: INSERTAR DATOS INICIALES
-- =========================================================

-- Usuario administrador por defecto
INSERT INTO usuarios (nombre, correo, contraseña, rol)
VALUES ('Aketzaly', 'admin@lavanderia.com', '1234', 'admin');

INSERT INTO usuarios (nombre, correo, contraseña, rol)
VALUES ('Ulises', '1', '1234', 'admin');


-- Configuración inicial de la empresa
INSERT INTO configuracion (
    nombre_empresa, direccion, telefono, rfc, moneda, iva,
    puntos_por_compra, valor_punto_en_dinero
) VALUES (
    'Lavandería Exprés',
    'Calle Principal #123, Colonia Centro',
    '555-123-4567',
    'XAXX010101000',
    'MXN',
    16.00,
    1,
    0.10
);

-- Servicios por defecto
INSERT INTO servicios (nombre, descripcion, precio, tiempo_estimado, activo) VALUES
('Lavado Normal', 'Lavado estándar de ropa', 10.00, 60, 1),
('Lavado Express', 'Lavado rápido', 15.00, 30, 1),
('Planchado', 'Servicio de planchado', 8.00, 45, 1),
('Lavado en Seco', 'Lavado especial para prendas delicadas', 20.00, 90, 1),
('Teñido', 'Servicio de teñido de prendas', 25.00, 120, 1);

-- Productos de ejemplo
INSERT INTO productos (nombre, precio, stock) VALUES
('Detergente 1kg', 35.00, 50),
('Suavizante 500ml', 25.00, 30),
('Blanqueador 1L', 15.00, 25),
('Perfume para ropa', 45.00, 20);

-- Cliente de ejemplo
INSERT INTO clientes (nombre, telefono, correo, puntos) VALUES
('Cliente General', '555-000-0001', 'cliente@ejemplo.com', 0);


ALTER TABLE productos
    ADD COLUMN promo_desc VARCHAR(100) NULL,
    ADD COLUMN nuevo_precio DECIMAL(10,2) NULL;

ALTER TABLE servicios
    ADD COLUMN promo_desc VARCHAR(100) NULL,
    ADD COLUMN nuevo_precio DECIMAL(10,2) NULLe

CREATE TABLE cuentas_abiertas (
    id_cuenta INT AUTO_INCREMENT PRIMARY KEY,
    numero_cuenta VARCHAR(20) UNIQUE NOT NULL, -- Mesa 1, Cliente A, etc.
    nombre_cliente VARCHAR(100) NOT NULL,
    id_cliente INT NULL, -- Referencia opcional a clientes registrados
    fecha_apertura DATETIME DEFAULT CURRENT_TIMESTAMP,
    hora_apertura TIME DEFAULT (CURRENT_TIME),
    estado ENUM('abierta', 'cerrada', 'pausada') DEFAULT 'abierta',
    subtotal DECIMAL(10,2) DEFAULT 0.00,
    descuento DECIMAL(10,2) DEFAULT 0.00,
    total DECIMAL(10,2) DEFAULT 0.00,
    observaciones TEXT,
    id_usuario_apertura INT NOT NULL, -- Quién abrió la cuenta
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE SET NULL,
    FOREIGN KEY (id_usuario_apertura) REFERENCES usuarios(id_usuario)
);

-- Crear tabla para los items de las cuentas abiertas
CREATE TABLE items_cuenta_abierta (
    id_item INT AUTO_INCREMENT PRIMARY KEY,
    id_cuenta INT NOT NULL,
    tipo_item ENUM('producto', 'servicio') NOT NULL,
    id_item_ref INT NOT NULL, -- ID del producto o servicio
    nombre_item VARCHAR(200) NOT NULL, -- Nombre al momento de la venta
    cantidad INT NOT NULL DEFAULT 1,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    fecha_agregado DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_usuario INT NOT NULL, -- Quién agregó el item
    observaciones VARCHAR(500),

    FOREIGN KEY (id_cuenta) REFERENCES cuentas_abiertas(id_cuenta) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- Modificar tabla ventas para relacionar con cuentas abiertas
ALTER TABLE ventas
ADD COLUMN id_cuenta_abierta INT NULL,
ADD FOREIGN KEY (id_cuenta_abierta) REFERENCES cuentas_abiertas(id_cuenta);

-- Crear índices para mejor rendimiento
CREATE INDEX idx_cuentas_estado ON cuentas_abiertas(estado);
CREATE INDEX idx_cuentas_fecha ON cuentas_abiertas(fecha_apertura);
CREATE INDEX idx_items_cuenta ON items_cuenta_abierta(id_cuenta);

-- Crear trigger para actualizar totales de cuenta automáticamente
DELIMITER //
CREATE TRIGGER actualizar_total_cuenta_insert
AFTER INSERT ON items_cuenta_abierta
FOR EACH ROW
BEGIN
    UPDATE cuentas_abiertas
    SET subtotal = (
        SELECT COALESCE(SUM(subtotal), 0)
        FROM items_cuenta_abierta
        WHERE id_cuenta = NEW.id_cuenta
    ),
    total = subtotal - descuento
    WHERE id_cuenta = NEW.id_cuenta;
END //

CREATE TRIGGER actualizar_total_cuenta_update
AFTER UPDATE ON items_cuenta_abierta
FOR EACH ROW
BEGIN
    UPDATE cuentas_abiertas
    SET subtotal = (
        SELECT COALESCE(SUM(subtotal), 0)
        FROM items_cuenta_abierta
        WHERE id_cuenta = NEW.id_cuenta
    ),
    total = subtotal - descuento
    WHERE id_cuenta = NEW.id_cuenta;
END //

CREATE TRIGGER actualizar_total_cuenta_delete
AFTER DELETE ON items_cuenta_abierta
FOR EACH ROW
BEGIN
    UPDATE cuentas_abiertas
    SET subtotal = (
        SELECT COALESCE(SUM(subtotal), 0)
        FROM items_cuenta_abierta
        WHERE id_cuenta = OLD.id_cuenta
    ),
    total = subtotal - descuento
    WHERE id_cuenta = OLD.id_cuenta;
END //
DELIMITER ;

-- Vista para consultar cuentas abiertas con detalles
CREATE VIEW vista_cuentas_abiertas AS
SELECT
    ca.id_cuenta,
    ca.numero_cuenta,
    ca.nombre_cliente,
    c.telefono as telefono_cliente,
    ca.fecha_apertura,
    ca.hora_apertura,
    ca.estado,
    ca.subtotal,
    ca.descuento,
    ca.total,
    ca.observaciones,
    u.nombre as usuario_apertura,
    COUNT(ica.id_item) as cantidad_items,
    TIMESTAMPDIFF(MINUTE, ca.fecha_apertura, NOW()) as minutos_abierta
FROM cuentas_abiertas ca
LEFT JOIN clientes c ON ca.id_cliente = c.id_cliente
LEFT JOIN usuarios u ON ca.id_usuario_apertura = u.id_usuario
LEFT JOIN items_cuenta_abierta ica ON ca.id_cuenta = ica.id_cuenta
GROUP BY ca.id_cuenta
ORDER BY ca.fecha_apertura DESC;

-- Vista para el detalle de items en cuentas abiertas
CREATE VIEW vista_detalle_cuentas_abiertas AS
SELECT
    ica.id_item,
    ica.id_cuenta,
    ca.numero_cuenta,
    ca.nombre_cliente,
    ica.tipo_item,
    ica.nombre_item,
    ica.cantidad,
    ica.precio_unitario,
    ica.subtotal,
    ica.fecha_agregado,
    u.nombre as usuario_que_agrego,
    ica.observaciones
FROM items_cuenta_abierta ica
JOIN cuentas_abiertas ca ON ica.id_cuenta = ca.id_cuenta
JOIN usuarios u ON ica.id_usuario = u.id_usuario
ORDER BY ica.fecha_agregado DESC;

-- =====================================================
-- EJECUTAR EN MySQL PARA CREAR TABLAS DE CUENTAS ABIERTAS
-- =====================================================

USE lavanderiadb;

-- 1. Crear tabla cuentas_abiertas
CREATE TABLE IF NOT EXISTS cuentas_abiertas (
    id_cuenta INT AUTO_INCREMENT PRIMARY KEY,
    numero_cuenta VARCHAR(20) UNIQUE NOT NULL,
    nombre_cliente VARCHAR(100) NOT NULL,
    id_cliente INT NULL,
    fecha_apertura DATETIME DEFAULT CURRENT_TIMESTAMP,
    hora_apertura TIME DEFAULT (CURRENT_TIME),
    estado ENUM('abierta', 'cerrada', 'pausada') DEFAULT 'abierta',
    subtotal DECIMAL(10,2) DEFAULT 0.00,
    descuento DECIMAL(10,2) DEFAULT 0.00,
    total DECIMAL(10,2) DEFAULT 0.00,
    observaciones TEXT,
    id_usuario_apertura INT NOT NULL,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE SET NULL,
    FOREIGN KEY (id_usuario_apertura) REFERENCES usuarios(id_usuario)
);

-- 2. Crear tabla items_cuenta_abierta
CREATE TABLE IF NOT EXISTS items_cuenta_abierta (
    id_item INT AUTO_INCREMENT PRIMARY KEY,
    id_cuenta INT NOT NULL,
    tipo_item ENUM('producto', 'servicio') NOT NULL,
    id_item_ref INT NOT NULL,
    nombre_item VARCHAR(200) NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    fecha_agregado DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_usuario INT NOT NULL,
    observaciones VARCHAR(500),

    FOREIGN KEY (id_cuenta) REFERENCES cuentas_abiertas(id_cuenta) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- 3. Modificar tabla ventas (solo si no existe la columna)
ALTER TABLE ventas
ADD COLUMN IF NOT EXISTS id_cuenta_abierta INT NULL;

-- 4. Crear índices
CREATE INDEX IF NOT EXISTS idx_cuentas_estado ON cuentas_abiertas(estado);
CREATE INDEX IF NOT EXISTS idx_cuentas_fecha ON cuentas_abiertas(fecha_apertura);
CREATE INDEX IF NOT EXISTS idx_items_cuenta ON items_cuenta_abierta(id_cuenta);

-- 5. Crear vista para cuentas abiertas
CREATE OR REPLACE VIEW vista_cuentas_abiertas AS
SELECT
    ca.id_cuenta,
    ca.numero_cuenta,
    ca.nombre_cliente,
    c.telefono as telefono_cliente,
    ca.fecha_apertura,
    ca.hora_apertura,
    ca.estado,
    ca.subtotal,
    ca.descuento,
    ca.total,
    ca.observaciones,
    u.nombre as usuario_apertura,
    COUNT(ica.id_item) as cantidad_items,
    TIMESTAMPDIFF(MINUTE, ca.fecha_apertura, NOW()) as minutos_abierta
FROM cuentas_abiertas ca
LEFT JOIN clientes c ON ca.id_cliente = c.id_cliente
LEFT JOIN usuarios u ON ca.id_usuario_apertura = u.id_usuario
LEFT JOIN items_cuenta_abierta ica ON ca.id_cuenta = ica.id_cuenta
GROUP BY ca.id_cuenta
ORDER BY ca.fecha_apertura DESC;

SELECT 'Tablas de cuentas abiertas creadas exitosamente' as Resultado;