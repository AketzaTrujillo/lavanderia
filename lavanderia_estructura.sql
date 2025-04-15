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


INSERT INTO usuarios (nombre, correo, contraseña, rol)
VALUES ('Aketzaly', 'admin@lavanderia.com', '1234', 'admin');

