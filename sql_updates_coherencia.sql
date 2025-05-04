-- sql_updates_coherencia_correcto.sql
-- Script adaptado para MySQL con sintaxis correcta

USE lavanderiadb;

-- 1. Agregar columnas necesarias (con verificación previa)
-- Para la tabla ventas
SET @dbname = DATABASE();
SET @tablename = 'ventas';
SET @columnname = 'id_pedido';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE
    (TABLE_SCHEMA = @dbname)
    AND (TABLE_NAME = @tablename)
    AND (COLUMN_NAME = @columnname)
  ) > 0,
  'SELECT 1',
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' INT DEFAULT NULL')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Para la tabla pedidos
SET @tablename = 'pedidos';
SET @columnname = 'convertido_a_venta';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE
    (TABLE_SCHEMA = @dbname)
    AND (TABLE_NAME = @tablename)
    AND (COLUMN_NAME = @columnname)
  ) > 0,
  'SELECT 1',
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' BOOLEAN DEFAULT FALSE')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 2. Agregar restricción de clave foránea (con verificación previa)
SET @constraintname = 'fk_venta_pedido';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS WHERE
    (TABLE_SCHEMA = @dbname)
    AND (TABLE_NAME = 'ventas')
    AND (CONSTRAINT_NAME = @constraintname)
  ) > 0,
  'SELECT 1',
  CONCAT('ALTER TABLE ventas ADD CONSTRAINT ', @constraintname,
         ' FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido)')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 3. Crear vistas
-- Vista para resumen de ventas por caja
DROP VIEW IF EXISTS vista_ventas_por_caja;
CREATE VIEW vista_ventas_por_caja AS
SELECT
    c.id_caja,
    c.fecha,
    c.responsable,
    COUNT(DISTINCT v.id_venta) as total_ventas,
    COUNT(DISTINCT v.id_cliente) as clientes_atendidos,
    SUM(v.total) as total_facturado,
    SUM(
        CASE WHEN v.metodo_pago = 'Efectivo' THEN v.total ELSE 0 END
    ) as total_efectivo,
    SUM(
        CASE WHEN v.metodo_pago = 'Tarjeta' THEN v.total ELSE 0 END
    ) as total_tarjeta,
    SUM(
        CASE WHEN v.metodo_pago = 'Transferencia' THEN v.total ELSE 0 END
    ) as total_transferencia
FROM caja c
INNER JOIN movimientos_caja mc ON c.id_caja = mc.id_caja
INNER JOIN ventas v ON mc.concepto LIKE CONCAT('Venta #', v.id_venta, '%')
WHERE mc.tipo = 'ingreso'
GROUP BY c.id_caja, c.fecha, c.responsable;

-- Vista para pedidos convertibles a venta
DROP VIEW IF EXISTS vista_pedidos_entregados;
CREATE VIEW vista_pedidos_entregados AS
SELECT
    p.id_pedido,
    p.fecha_pedido,
    p.estado,
    p.id_cliente,
    c.nombre as cliente,
    c.correo,
    (SELECT SUM(dp.cantidad * dp.precio_unitario)
     FROM detalle_pedido dp
     WHERE dp.id_pedido = p.id_pedido) as total,
    IFNULL(p.convertido_a_venta, FALSE) as convertido_a_venta,
    u.nombre as responsable
FROM pedidos p
INNER JOIN clientes c ON p.id_cliente = c.id_cliente
LEFT JOIN ventas v ON v.id_pedido = p.id_pedido
LEFT JOIN usuarios u ON v.id_usuario = u.id_usuario
WHERE p.estado = 'Entregado'
  AND IFNULL(p.convertido_a_venta, FALSE) = FALSE;

-- 4. Procedimiento almacenado para convertir pedido a venta
DROP PROCEDURE IF EXISTS ConvertirPedidoAVenta;
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

    -- Obtener información del pedido
    SELECT id_cliente INTO v_id_cliente
    FROM pedidos
    WHERE id_pedido = p_id_pedido;

    SELECT SUM(cantidad * precio_unitario) INTO v_total
    FROM detalle_pedido
    WHERE id_pedido = p_id_pedido;

    -- Verificar que hay una caja abierta
    SELECT id_caja INTO v_id_caja
    FROM caja
    WHERE fecha = CURDATE() AND hora_cierre IS NULL
    LIMIT 1;

    IF v_id_caja IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'No hay una caja abierta';
    END IF;

    -- Crear la venta
    INSERT INTO ventas (id_usuario, id_cliente, total, metodo_pago, id_pedido, fecha)
    VALUES (p_id_usuario, v_id_cliente, v_total, p_metodo_pago, p_id_pedido, NOW());

    SET p_id_venta = LAST_INSERT_ID();

    -- Copiar detalles del pedido a detalle de venta
    INSERT INTO detalle_venta (id_venta, tipo_item, id_item, cantidad, subtotal)
    SELECT p_id_venta, dp.tipo_item, dp.id_item, dp.cantidad,
           (dp.cantidad * dp.precio_unitario)
    FROM detalle_pedido dp
    WHERE dp.id_pedido = p_id_pedido;

    -- Registrar el pago
    INSERT INTO pagos (id_venta, monto, metodo_pago, fecha)
    VALUES (p_id_venta, v_total, p_metodo_pago, NOW());

    -- Actualizar puntos del cliente
    UPDATE clientes
    SET puntos = puntos + FLOOR(v_total / 10)
    WHERE id_cliente = v_id_cliente;

    -- Registrar el movimiento en caja
    INSERT INTO movimientos_caja (id_caja, tipo, concepto, monto, hora, id_usuario)
    VALUES (v_id_caja, 'ingreso',
            CONCAT('Venta #', p_id_venta, ' (Pedido #', p_id_pedido, ')'),
            v_total, NOW(), p_id_usuario);

    -- Actualizar totales de caja
    UPDATE caja
    SET total_ingresos = total_ingresos + v_total,
        saldo_final = saldo_final + v_total
    WHERE id_caja = v_id_caja;

    -- Marcar el pedido como convertido
    UPDATE pedidos
    SET convertido_a_venta = TRUE
    WHERE id_pedido = p_id_pedido;

    COMMIT;
END //
DELIMITER ;

-- 5. Crear índices
CREATE INDEX idx_ventas_pedido ON ventas(id_pedido);
CREATE INDEX idx_pedidos_convertido ON pedidos(convertido_a_venta);
CREATE INDEX idx_movimientos_concepto ON movimientos_caja(concepto);

-- 6. Vista para el dashboard de coherencia de datos
DROP VIEW IF EXISTS vista_coherencia_sistema;
CREATE VIEW vista_coherencia_sistema AS
SELECT
    'Ventas sin caja' as tipo_problema,
    COUNT(*) as cantidad,
    GROUP_CONCAT(v.id_venta) as ids_afectados
FROM ventas v
LEFT JOIN movimientos_caja mc ON mc.concepto LIKE CONCAT('Venta #', v.id_venta, '%')
WHERE mc.id_movimiento IS NULL
UNION ALL
SELECT
    'Pedidos entregados sin venta' as tipo_problema,
    COUNT(*) as cantidad,
    GROUP_CONCAT(p.id_pedido) as ids_afectados
FROM pedidos p
WHERE p.estado = 'Entregado'
  AND IFNULL(p.convertido_a_venta, FALSE) = FALSE
UNION ALL
SELECT
    'Ventas sin pago registrado' as tipo_problema,
    COUNT(*) as cantidad,
    GROUP_CONCAT(v.id_venta) as ids_afectados
FROM ventas v
LEFT JOIN pagos p ON v.id_venta = p.id_venta
WHERE p.id_pago IS NULL
UNION ALL
SELECT
    'Cajas con saldo inconsistente' as tipo_problema,
    COUNT(*) as cantidad,
    GROUP_CONCAT(c.id_caja) as ids_afectados
FROM caja c
WHERE c.saldo_final != (c.total_ingresos - c.total_egresos);

-- 7. Trigger para mantener coherencia automáticamente
DROP TRIGGER IF EXISTS trigger_actualizar_caja_venta;
DELIMITER //
CREATE TRIGGER trigger_actualizar_caja_venta
AFTER INSERT ON ventas
FOR EACH ROW
BEGIN
    DECLARE v_id_caja INT;
    DECLARE v_error_msg VARCHAR(255);

    -- Buscar caja abierta
    SELECT id_caja INTO v_id_caja
    FROM caja
    WHERE fecha = DATE(NEW.fecha) AND hora_cierre IS NULL
    LIMIT 1;

    IF v_id_caja IS NOT NULL THEN
        -- Insertar movimiento automáticamente
        INSERT INTO movimientos_caja (id_caja, tipo, concepto, monto, hora, id_usuario)
        VALUES (v_id_caja, 'ingreso',
                CONCAT('Venta #', NEW.id_venta),
                NEW.total, NOW(), NEW.id_usuario);

        -- Actualizar totales de caja
        UPDATE caja
        SET total_ingresos = total_ingresos + NEW.total,
            saldo_final = saldo_final + NEW.total
        WHERE id_caja = v_id_caja;
    END IF;
END //
DELIMITER ;

-- 8. Vista para reportes de rentabilidad
DROP VIEW IF EXISTS vista_rentabilidad_servicios;
CREATE VIEW vista_rentabilidad_servicios AS
SELECT
    dv.tipo_item,
    dv.id_item,
    CASE
        WHEN dv.tipo_item = 'producto' THEN p.nombre
        WHEN dv.tipo_item = 'servicio' THEN s.nombre
    END as nombre_item,
    COUNT(*) as veces_vendido,
    SUM(dv.cantidad) as cantidad_total,
    SUM(dv.subtotal) as ingreso_total,
    SUM(dv.subtotal) / COUNT(*) as promedio_por_venta,
    DATE_FORMAT(v.fecha, '%Y-%m') as mes_anio
FROM detalle_venta dv
INNER JOIN ventas v ON dv.id_venta = v.id_venta
LEFT JOIN productos p ON dv.tipo_item = 'producto' AND dv.id_item = p.id_producto
LEFT JOIN servicios s ON dv.tipo_item = 'servicio' AND dv.id_item = s.id_servicio
GROUP BY dv.tipo_item, dv.id_item, DATE_FORMAT(v.fecha, '%Y-%m')
ORDER BY ingreso_total DESC;

-- 9. Función para calcular puntos
DROP FUNCTION IF EXISTS CalcularPuntos;
DELIMITER //
CREATE FUNCTION CalcularPuntos(p_total DECIMAL(10,2))
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_puntos_por_compra INT DEFAULT 1;

    -- Obtener configuración de puntos si existe
    IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES
               WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'configuracion') THEN
        SELECT IFNULL(puntos_por_compra, 1) INTO v_puntos_por_compra
        FROM configuracion
        LIMIT 1;
    END IF;

    RETURN FLOOR(p_total / 10) * v_puntos_por_compra;
END //
DELIMITER ;

-- 10. Configuración por defecto
INSERT INTO configuracion (
    nombre_empresa, direccion, telefono, rfc, moneda, iva,
    puntos_por_compra, valor_punto_en_dinero
)
SELECT
    'Lavandería Exprés',
    'Calle Principal #123, Colonia Centro',
    '555-123-4567',
    'XAXX010101000',
    'MXN',
    16.00,
    1,
    0.10
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM configuracion LIMIT 1);

-- Mensaje de finalización
SELECT 'Base de datos actualizada correctamente para coherencia entre módulos' as mensaje;