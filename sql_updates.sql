-- Seleccionar la base de datos antes de ejecutar los scripts
USE lavanderiadb;

-- Scripts para actualizar la base de datos y soportar el seguimiento de pedidos mejorado

-- Primero, verificar si existe el soporte para ALTER TABLE en MariaDB
-- Agregar columna de prioridad a la tabla de pedidos (solo si no existe)
SET @query = IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
     WHERE TABLE_NAME = 'pedidos'
     AND COLUMN_NAME = 'prioridad'
     AND TABLE_SCHEMA = DATABASE()) = 0,
    'ALTER TABLE pedidos ADD COLUMN prioridad ENUM(\'Normal\', \'Alta\', \'Urgente\') DEFAULT \'Normal\'',
    'SELECT 1'
);
PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Crear tabla para historial de cambios de estado (opcional)
DROP TABLE IF EXISTS historial_estados_pedido;
CREATE TABLE IF NOT EXISTS historial_estados_pedido (
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

-- Agregar columna de fecha de entrega estimada si no existe
SET @query2 = IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
     WHERE TABLE_NAME = 'pedidos'
     AND COLUMN_NAME = 'fecha_entrega_estimada'
     AND TABLE_SCHEMA = DATABASE()) = 0,
    'ALTER TABLE pedidos ADD COLUMN fecha_entrega_estimada DATE',
    'SELECT 1'
);
PREPARE stmt2 FROM @query2;
EXECUTE stmt2;
DEALLOCATE PREPARE stmt2;

-- Crear vista para resumen de pedidos por estado (útil para reportes)
DROP VIEW IF EXISTS resumen_pedidos_estado;
CREATE VIEW resumen_pedidos_estado AS
SELECT
    estado,
    COUNT(*) as cantidad,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM pedidos), 2) as porcentaje,
    SUM(
        (SELECT SUM(dp.cantidad * dp.precio_unitario)
         FROM detalle_pedido dp
         WHERE dp.id_pedido = p.id_pedido)
    ) as total_ventas
FROM pedidos p
GROUP BY estado;

-- Crear vista para pedidos con información completa
DROP VIEW IF EXISTS vista_pedidos_completos;
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
    (SELECT SUM(dp.cantidad * dp.precio_unitario)
     FROM detalle_pedido dp
     WHERE dp.id_pedido = p.id_pedido) as total
FROM pedidos p
INNER JOIN clientes c ON p.id_cliente = c.id_cliente
LEFT JOIN ventas v ON v.id_venta = p.id_pedido
LEFT JOIN usuarios u ON v.id_usuario = u.id_usuario;

-- Índices para mejorar el rendimiento
-- Crear índices solo si no existen
CREATE INDEX idx_pedidos_estado ON pedidos(estado);
CREATE INDEX idx_pedidos_fecha ON pedidos(fecha_pedido);
CREATE INDEX idx_pedidos_prioridad ON pedidos(prioridad);
CREATE INDEX idx_historial_pedido ON historial_estados_pedido(id_pedido);

-- Datos de ejemplo (ejecutar solo en desarrollo)
-- NOTA: Comentar esta sección en producción
-- Actualizar algunos pedidos existentes con prioridad
UPDATE pedidos SET prioridad = 'Alta' WHERE id_pedido IN (SELECT id FROM (SELECT id_pedido as id FROM pedidos LIMIT 2) AS tmp);
UPDATE pedidos SET prioridad = 'Urgente' WHERE id_pedido IN (SELECT id FROM (SELECT id_pedido as id FROM pedidos LIMIT 1 OFFSET 2) AS tmp);

-- Agregar fechas de entrega estimadas
UPDATE pedidos
SET fecha_entrega_estimada = DATE_ADD(fecha_pedido, INTERVAL 2 DAY)
WHERE fecha_entrega_estimada IS NULL;

-- Verificar que las columnas se hayan creado correctamente
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'pedidos'
  AND TABLE_SCHEMA = DATABASE()
  AND COLUMN_NAME IN ('prioridad', 'fecha_entrega_estimada');

-- Mostrar mensaje de finalización
SELECT 'Base de datos actualizada correctamente para el módulo de seguimiento de pedidos' as mensaje;