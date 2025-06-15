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