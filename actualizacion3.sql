-- Script SQL para corregir problemas y actualizar estructura

-- 1. Agregar campo para evitar duplicación de ventas en movimientos
ALTER TABLE ventas ADD COLUMN IF NOT EXISTS registrado_en_caja BOOLEAN DEFAULT FALSE;

-- 2. Actualizar ventas existentes para marcarlas como registradas
UPDATE ventas SET registrado_en_caja = TRUE
WHERE id_venta IN (
    SELECT DISTINCT SUBSTRING_INDEX(SUBSTRING_INDEX(concepto, '#', -1), ' ', 1)
    FROM movimientos_caja
    WHERE concepto LIKE 'Venta #%'
);

-- 3. Crear tabla para arqueos si no existe
CREATE TABLE IF NOT EXISTS arqueos_caja (
    id_arqueo INT AUTO_INCREMENT PRIMARY KEY,
    id_caja INT NOT NULL,
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_sistema DECIMAL(10,2) NOT NULL,
    total_fisico DECIMAL(10,2) NOT NULL,
    diferencia DECIMAL(10,2) NOT NULL,
    id_usuario INT NOT NULL,
    observaciones TEXT,
    FOREIGN KEY (id_caja) REFERENCES caja(id_caja),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- 4. Verificar y corregir estructura de la tabla caja
ALTER TABLE caja
    MODIFY COLUMN responsable INT NOT NULL,
    ADD COLUMN IF NOT EXISTS monto_inicial DECIMAL(10,2) DEFAULT 0.00;

-- 5. Verificar y corregir estructura de la tabla movimientos_caja
ALTER TABLE movimientos_caja
    MODIFY COLUMN id_usuario INT NOT NULL;

-- 6. Crear índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_movimientos_caja_id_caja ON movimientos_caja(id_caja);
CREATE INDEX IF NOT EXISTS idx_movimientos_caja_tipo ON movimientos_caja(tipo);
CREATE INDEX IF NOT EXISTS idx_ventas_registrado ON ventas(registrado_en_caja);

-- 7. Crear vista para resumen de caja
CREATE OR REPLACE VIEW vista_resumen_caja AS
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
    (SELECT COUNT(*) FROM ventas v
     JOIN movimientos_caja m ON m.concepto LIKE CONCAT('Venta #', v.id_venta, '%')
     WHERE m.id_caja = c.id_caja) AS num_ventas,
    (c.hora_cierre IS NULL) AS caja_abierta
FROM caja c
JOIN usuarios u ON c.responsable = u.id_usuario;