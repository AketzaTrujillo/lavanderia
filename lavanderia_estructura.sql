CREATE DATABASE lavanderiadb;
USE lavanderiadb;
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'cajero') NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(15),
    correo VARCHAR(100),
    puntos INT DEFAULT 0,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0
);

CREATE TABLE pedidos (
    id_pedido INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT,
    fecha_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('Recibido', 'En proceso', 'Listo para entrega', 'Entregado') DEFAULT 'Recibido',
    observaciones TEXT,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);


CREATE TABLE detalle_pedido (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido INT NOT NULL,
    tipo_item ENUM('producto', 'servicio') NOT NULL,
    id_item INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido)
);


CREATE TABLE ventas (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    id_cliente INT,
    total DECIMAL(10,2),
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    metodo_pago VARCHAR(50),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);


CREATE TABLE detalle_venta (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT NOT NULL,
    tipo_item ENUM('producto', 'servicio') NOT NULL,
    id_item INT NOT NULL,
    cantidad INT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta)
);

CREATE TABLE caja (
    id_caja INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    hora_apertura TIME,
    hora_cierre TIME,
    total_ingresos DECIMAL(10,2) DEFAULT 0,
    total_egresos DECIMAL(10,2) DEFAULT 0,
    saldo_final DECIMAL(10,2) DEFAULT 0,
    responsable INT,
    FOREIGN KEY (responsable) REFERENCES usuarios(id_usuario)
);

CREATE TABLE servicios (
    id_servicio INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL,
    tiempo_estimado INT, -- Estimated time in minutes
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE pagos (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT,
    monto DECIMAL(10,2) NOT NULL,
    metodo_pago ENUM('Efectivo', 'Tarjeta', 'Transferencia', 'Otro') NOT NULL,
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    referencia VARCHAR(100),
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta)
);

CREATE TABLE gastos (
    id_gasto INT AUTO_INCREMENT PRIMARY KEY,
    concepto VARCHAR(100) NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    fecha DATE NOT NULL,
    id_usuario INT,
    comprobante VARCHAR(255),
    observaciones TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE movimientos_caja (
    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    id_caja INT NOT NULL,
    tipo ENUM('ingreso', 'egreso') NOT NULL,
    concepto VARCHAR(100) NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_usuario INT,
    FOREIGN KEY (id_caja) REFERENCES caja(id_caja),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE IF NOT EXISTS servicios (
    id_servicio INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL,
    tiempo_estimado INT NOT NULL,
    activo TINYINT(1) DEFAULT 1
);

CREATE TABLE IF NOT EXISTS caja (
    id_caja INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    hora_apertura TIME,
    hora_cierre TIME,
    total_ingresos DECIMAL(10,2) DEFAULT 0,
    total_egresos DECIMAL(10,2) DEFAULT 0,
    saldo_final DECIMAL(10,2) DEFAULT 0,
    responsable INT,
    FOREIGN KEY (responsable) REFERENCES usuarios(id_usuario)
);

-- Tabla para los movimientos de caja
CREATE TABLE IF NOT EXISTS movimientos_caja (
    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    id_caja INT NOT NULL,
    tipo ENUM('ingreso', 'egreso') NOT NULL,
    concepto VARCHAR(100) NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_usuario INT,
    FOREIGN KEY (id_caja) REFERENCES caja(id_caja),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- Tabla para gastos
CREATE TABLE IF NOT EXISTS gastos (
    id_gasto INT AUTO_INCREMENT PRIMARY KEY,
    concepto VARCHAR(100) NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    fecha DATE NOT NULL,
    id_usuario INT,
    comprobante VARCHAR(255),
    observaciones TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- Tabla para configuración del sistema
CREATE TABLE IF NOT EXISTS configuracion (
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

-- Tabla para descuentos y promociones
CREATE TABLE IF NOT EXISTS promociones (
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

-- Tabla para pagos, vinculada a ventas
CREATE TABLE IF NOT EXISTS pagos (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT,
    monto DECIMAL(10,2) NOT NULL,
    metodo_pago ENUM('Efectivo', 'Tarjeta', 'Transferencia', 'Otro') NOT NULL,
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    referencia VARCHAR(100),
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta)
);

-- Tabla para respaldos del sistema
CREATE TABLE IF NOT EXISTS respaldos (
    id_respaldo INT AUTO_INCREMENT PRIMARY KEY,
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    ruta VARCHAR(255) NOT NULL,
    tamanio BIGINT,
    id_usuario INT,
    descripcion TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

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
ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS fecha_entrega_estimada DATE;

-- Crear vista para resumen de pedidos por estado (útil para reportes)
CREATE OR REPLACE VIEW resumen_pedidos_estado AS
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
CREATE OR REPLACE VIEW vista_pedidos_completos AS
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
CREATE INDEX IF NOT EXISTS idx_pedidos_estado ON pedidos(estado);
CREATE INDEX IF NOT EXISTS idx_pedidos_fecha ON pedidos(fecha_pedido);
CREATE INDEX IF NOT EXISTS idx_pedidos_prioridad ON pedidos(prioridad);
CREATE INDEX IF NOT EXISTS idx_historial_pedido ON historial_estados_pedido(id_pedido);

-- Datos de ejemplo (ejecutar solo en desarrollo)
-- NOTA: Comentar esta sección en producción
/*
-- Actualizar algunos pedidos existentes con prioridad
UPDATE pedidos SET prioridad = 'Alta' WHERE id_pedido IN (SELECT id_pedido FROM pedidos ORDER BY RAND() LIMIT 2);
UPDATE pedidos SET prioridad = 'Urgente' WHERE id_pedido IN (SELECT id_pedido FROM pedidos ORDER BY RAND() LIMIT 1);

-- Agregar fechas de entrega estimadas
UPDATE pedidos
SET fecha_entrega_estimada = DATE_ADD(fecha_pedido, INTERVAL 2 DAY)
WHERE fecha_entrega_estimada IS NULL;
*/

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
-- Agregar columnas faltantes a tablas existentes si es necesario

-- Verificar si la columna puntos existe en la tabla clientes
ALTER TABLE clientes
ADD COLUMN IF NOT EXISTS telefono VARCHAR(15),
ADD COLUMN IF NOT EXISTS correo VARCHAR(100),
ADD COLUMN IF NOT EXISTS puntos INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP;

-- Verificar si la columna metodo_pago existe en la tabla ventas
ALTER TABLE ventas
ADD COLUMN IF NOT EXISTS metodo_pago VARCHAR(50),
ADD COLUMN IF NOT EXISTS descuento_aplicado DECIMAL(10,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS puntos_ganados INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS puntos_utilizados INT DEFAULT 0;

-- Verificar si la columna observaciones existe en la tabla pedidos
ALTER TABLE pedidos
ADD COLUMN IF NOT EXISTS observaciones TEXT,
ADD COLUMN IF NOT EXISTS fecha_entrega_estimada DATE,
ADD COLUMN IF NOT EXISTS prioridad ENUM('Baja', 'Normal', 'Alta', 'Urgente') DEFAULT 'Normal';

-- Agregar datos iniciales a la tabla de configuración si está vacía
INSERT INTO configuracion (nombre_empresa, direccion, telefono, rfc)
SELECT 'Lavandería Exprés', 'Calle Principal #123, Colonia Centro', '555-123-4567', 'XAXX010101000'
WHERE NOT EXISTS (SELECT 1 FROM configuracion LIMIT 1);

-- Crear índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_caja_fecha ON caja (fecha);
CREATE INDEX IF NOT EXISTS idx_movimientos_id_caja ON movimientos_caja (id_caja);
CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas (fecha);
CREATE INDEX IF NOT EXISTS idx_pedidos_fecha ON pedidos (fecha_pedido);
CREATE INDEX IF NOT EXISTS idx_clientes_nombre ON clientes (nombre);

-- Mensaje de finalización
SELECT 'La base de datos ha sido actualizada correctamente.' AS mensaje;

-- Insertar algunos servicios por defecto (opcional)
INSERT INTO servicios (nombre, descripcion, precio, tiempo_estimado, activo) VALUES
('Lavado Normal', 'Lavado estándar de ropa', 10.00, 60, 1),
('Lavado Express', 'Lavado rápido', 15.00, 30, 1),
('Planchado', 'Servicio de planchado', 8.00, 45, 1),
('Lavado en Seco', 'Lavado especial para prendas delicadas', 20.00, 90, 1),
('Teñido', 'Servicio de teñido de prendas', 25.00, 120, 1);


INSERT INTO usuarios (nombre, correo, contraseña, rol)
VALUES ('Aketzaly', 'admin@lavanderia.com', '1234', 'admin');

