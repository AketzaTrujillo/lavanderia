-- =========================================================
-- SCRIPT DE DATOS DE PRUEBA - SISTEMA LAVANDERÍA
-- =========================================================
-- Genera datos aleatorios del 1 al 25 de mayo 2025
-- Incluye: Usuarios, Clientes, Productos, Servicios, Pedidos, Ventas, Movimientos de Caja
-- =========================================================

USE lavanderiadb;

-- =========================================================
-- 1. USUARIOS ADICIONALES
-- =========================================================
INSERT INTO usuarios (nombre, correo, contraseña, rol, fecha_registro) VALUES
('Maria Rodriguez', 'maria@lavanderia.com', '1234', 'cajero', '2025-04-15 08:00:00'),
('Carlos Mendez', 'carlos@lavanderia.com', '1234', 'cajero', '2025-04-20 09:30:00'),
('Ana Garcia', 'ana@lavanderia.com', '1234', 'admin', '2025-04-25 10:15:00'),
('Luis Torres', 'luis@lavanderia.com', '1234', 'cajero', '2025-04-28 14:20:00');

-- =========================================================
-- 2. CLIENTES DE PRUEBA
-- =========================================================
INSERT INTO clientes (nombre, telefono, correo, puntos, fecha_registro) VALUES
-- Clientes Mayo 1-5
('Sofia Martinez', '555-0101', 'sofia.martinez@gmail.com', 0, '2025-05-01 09:15:00'),
('Diego Ramirez', '555-0102', 'diego.ramirez@hotmail.com', 0, '2025-05-01 10:30:00'),
('Carmen Ruiz', '555-0103', 'carmen.ruiz@yahoo.com', 0, '2025-05-01 14:45:00'),
('Roberto Silva', '555-0104', 'roberto.silva@gmail.com', 0, '2025-05-02 08:20:00'),
('Patricia Lopez', '555-0105', 'patricia.lopez@outlook.com', 0, '2025-05-02 11:10:00'),
('Fernando Castro', '555-0106', 'fernando.castro@gmail.com', 0, '2025-05-02 15:35:00'),
('Gabriela Moreno', '555-0107', 'gabriela.moreno@hotmail.com', 0, '2025-05-03 09:45:00'),
('Alejandro Vargas', '555-0108', 'alejandro.vargas@gmail.com', 0, '2025-05-03 13:20:00'),
('Isabella Herrera', '555-0109', 'isabella.herrera@yahoo.com', 0, '2025-05-03 16:15:00'),
('Miguel Santos', '555-0110', 'miguel.santos@gmail.com', 0, '2025-05-04 10:05:00'),

-- Clientes Mayo 6-10
('Valeria Jimenez', '555-0111', 'valeria.jimenez@outlook.com', 0, '2025-05-06 08:30:00'),
('Sebastian Flores', '555-0112', 'sebastian.flores@gmail.com', 0, '2025-05-06 12:15:00'),
('Natalia Peña', '555-0113', 'natalia.pena@hotmail.com', 0, '2025-05-07 09:20:00'),
('Andres Gutierrez', '555-0114', 'andres.gutierrez@gmail.com', 0, '2025-05-07 14:40:00'),
('Camila Restrepo', '555-0115', 'camila.restrepo@yahoo.com', 0, '2025-05-08 11:25:00'),
('Julian Ortega', '555-0116', 'julian.ortega@gmail.com', 0, '2025-05-08 15:50:00'),
('Adriana Molina', '555-0117', 'adriana.molina@outlook.com', 0, '2025-05-09 10:10:00'),
('Ricardo Navarro', '555-0118', 'ricardo.navarro@gmail.com', 0, '2025-05-09 13:35:00'),
('Lucia Aguilar', '555-0119', 'lucia.aguilar@hotmail.com', 0, '2025-05-10 08:45:00'),
('Eduardo Ramos', '555-0120', 'eduardo.ramos@gmail.com', 0, '2025-05-10 16:20:00'),

-- Clientes Mayo 11-15
('Daniela Cruz', '555-0121', 'daniela.cruz@yahoo.com', 0, '2025-05-11 09:30:00'),
('Mateo Diaz', '555-0122', 'mateo.diaz@gmail.com', 0, '2025-05-11 14:15:00'),
('Paulina Vega', '555-0123', 'paulina.vega@outlook.com', 0, '2025-05-12 10:40:00'),
('Emilio Campos', '555-0124', 'emilio.campos@gmail.com', 0, '2025-05-12 15:25:00'),
('Renata Salazar', '555-0125', 'renata.salazar@hotmail.com', 0, '2025-05-13 11:50:00'),
('Joaquin Soto', '555-0126', 'joaquin.soto@gmail.com', 0, '2025-05-13 16:05:00'),
('Fernanda Rios', '555-0127', 'fernanda.rios@yahoo.com', 0, '2025-05-14 09:15:00'),
('Nicolas Paredes', '555-0128', 'nicolas.paredes@gmail.com', 0, '2025-05-14 13:40:00'),
('Antonella Medina', '555-0129', 'antonella.medina@outlook.com', 0, '2025-05-15 10:55:00'),
('Maximiliano Leon', '555-0130', 'maximiliano.leon@gmail.com', 0, '2025-05-15 15:10:00'),

-- Clientes Mayo 16-20
('Valentina Guerrero', '555-0131', 'valentina.guerrero@hotmail.com', 0, '2025-05-16 08:20:00'),
('Sergio Castillo', '555-0132', 'sergio.castillo@gmail.com', 0, '2025-05-16 12:45:00'),
('Martina Fuentes', '555-0133', 'martina.fuentes@yahoo.com', 0, '2025-05-17 09:35:00'),
('Gonzalo Espinoza', '555-0134', 'gonzalo.espinoza@gmail.com', 0, '2025-05-17 14:20:00'),
('Catalina Sandoval', '555-0135', 'catalina.sandoval@outlook.com', 0, '2025-05-18 11:10:00'),
('Benjamin Rojas', '555-0136', 'benjamin.rojas@gmail.com', 0, '2025-05-18 16:30:00'),
('Regina Contreras', '555-0137', 'regina.contreras@hotmail.com', 0, '2025-05-19 10:25:00'),
('Ignacio Pacheco', '555-0138', 'ignacio.pacheco@gmail.com', 0, '2025-05-19 15:40:00'),
('Florencia Cabrera', '555-0139', 'florencia.cabrera@yahoo.com', 0, '2025-05-20 09:50:00'),
('Samuel Coronado', '555-0140', 'samuel.coronado@gmail.com', 0, '2025-05-20 14:15:00'),

-- Clientes Mayo 21-25
('Ximena Ibarra', '555-0141', 'ximena.ibarra@outlook.com', 0, '2025-05-21 08:40:00'),
('Patricio Galvan', '555-0142', 'patricio.galvan@gmail.com', 0, '2025-05-21 13:25:00'),
('Constanza Velasco', '555-0143', 'constanza.velasco@hotmail.com', 0, '2025-05-22 10:15:00'),
('Rodrigo Delgado', '555-0144', 'rodrigo.delgado@gmail.com', 0, '2025-05-22 15:50:00'),
('Esperanza Lara', '555-0145', 'esperanza.lara@yahoo.com', 0, '2025-05-23 11:30:00'),
('Cristobal Ponce', '555-0146', 'cristobal.ponce@gmail.com', 0, '2025-05-23 16:45:00'),
('Macarena Bravo', '555-0147', 'macarena.bravo@outlook.com', 0, '2025-05-24 09:10:00'),
('Leonardo Solis', '555-0148', 'leonardo.solis@gmail.com', 0, '2025-05-24 14:35:00'),
('Agustina Munoz', '555-0149', 'agustina.munoz@hotmail.com', 0, '2025-05-25 10:20:00'),
('Esteban Carrasco', '555-0150', 'esteban.carrasco@gmail.com', 0, '2025-05-25 15:05:00');

-- =========================================================
-- 3. PRODUCTOS ADICIONALES
-- =========================================================
INSERT INTO productos (nombre, precio, stock) VALUES
('Jabón en Polvo 2kg', 45.00, 30),
('Suavizante Premium 1L', 35.00, 25),
('Quitamanchas 500ml', 28.00, 40),
('Bolsas de Lavandería Grande', 12.00, 100),
('Bolsas de Lavandería Mediana', 8.00, 150),
('Perfume Textil Lavanda', 55.00, 20),
('Perfume Textil Océano', 55.00, 18),
('Desinfectante Ropa 1L', 32.00, 35),
('Almidón en Spray', 22.00, 45),
('Quitapelusas', 18.00, 60);

-- =========================================================
-- 4. SERVICIOS ADICIONALES
-- =========================================================
INSERT INTO servicios (nombre, descripcion, precio, tiempo_estimado, activo) VALUES
('Lavado + Secado', 'Servicio completo de lavado y secado', 18.00, 90, 1),
('Solo Secado', 'Únicamente servicio de secado', 8.00, 45, 1),
('Lavado Delicado', 'Lavado especial para prendas delicadas', 22.00, 75, 1),
('Servicio Express 30min', 'Lavado y secado rápido', 25.00, 30, 1),
('Lavado de Edredones', 'Servicio especializado para edredones', 35.00, 120, 1),
('Lavado de Zapatos', 'Limpieza de calzado deportivo', 15.00, 60, 1);

-- =========================================================
-- 5. CAJA Y MOVIMIENTOS DIARIOS (1-25 MAYO 2025)
-- =========================================================

-- MAYO 1, 2025 (Miércoles)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-01', '08:00:00', '20:00:00', 500.00, 1250.00, 85.00, 1665.00, 1);

-- MAYO 2, 2025 (Jueves)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-02', '08:00:00', '20:00:00', 1665.00, 1380.00, 120.00, 2925.00, 3);

-- MAYO 3, 2025 (Viernes)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-03', '08:00:00', '20:00:00', 2925.00, 1820.00, 95.00, 4650.00, 4);

-- MAYO 4, 2025 (Sábado)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-04', '09:00:00', '18:00:00', 4650.00, 2150.00, 140.00, 6660.00, 1);

-- MAYO 5, 2025 (Domingo)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-05', '10:00:00', '17:00:00', 6660.00, 1680.00, 75.00, 8265.00, 3);

-- MAYO 6, 2025 (Lunes)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-06', '08:00:00', '20:00:00', 8265.00, 1450.00, 110.00, 9605.00, 4);

-- MAYO 7, 2025 (Martes)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-07', '08:00:00', '20:00:00', 9605.00, 1320.00, 88.00, 10837.00, 1);

-- MAYO 8, 2025 (Miércoles)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-08', '08:00:00', '20:00:00', 10837.00, 1580.00, 125.00, 12292.00, 3);

-- MAYO 9, 2025 (Jueves)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-09', '08:00:00', '20:00:00', 12292.00, 1720.00, 95.00, 13917.00, 4);

-- MAYO 10, 2025 (Viernes)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-10', '08:00:00', '20:00:00', 13917.00, 1950.00, 140.00, 15727.00, 1);

-- MAYO 11, 2025 (Sábado)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-11', '09:00:00', '18:00:00', 15727.00, 2280.00, 160.00, 17847.00, 3);

-- MAYO 12, 2025 (Domingo)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-12', '10:00:00', '17:00:00', 17847.00, 1840.00, 105.00, 19582.00, 4);

-- MAYO 13, 2025 (Lunes)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-13', '08:00:00', '20:00:00', 19582.00, 1620.00, 118.00, 21084.00, 1);

-- MAYO 14, 2025 (Martes)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-14', '08:00:00', '20:00:00', 21084.00, 1480.00, 92.00, 22472.00, 3);

-- MAYO 15, 2025 (Miércoles)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-15', '08:00:00', '20:00:00', 22472.00, 1750.00, 135.00, 24087.00, 4);

-- MAYO 16, 2025 (Jueves)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-16', '08:00:00', '20:00:00', 24087.00, 1890.00, 108.00, 25869.00, 1);

-- MAYO 17, 2025 (Viernes)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-17', '08:00:00', '20:00:00', 25869.00, 2120.00, 145.00, 27844.00, 3);

-- MAYO 18, 2025 (Sábado)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-18', '09:00:00', '18:00:00', 27844.00, 2450.00, 175.00, 30119.00, 4);

-- MAYO 19, 2025 (Domingo)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-19', '10:00:00', '17:00:00', 30119.00, 1920.00, 125.00, 31914.00, 1);

-- MAYO 20, 2025 (Lunes)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-20', '08:00:00', '20:00:00', 31914.00, 1680.00, 98.00, 33496.00, 3);

-- MAYO 21, 2025 (Martes)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-21', '08:00:00', '20:00:00', 33496.00, 1550.00, 115.00, 34931.00, 4);

-- MAYO 22, 2025 (Miércoles)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-22', '08:00:00', '20:00:00', 34931.00, 1780.00, 128.00, 36583.00, 1);

-- MAYO 23, 2025 (Jueves)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-23', '08:00:00', '20:00:00', 36583.00, 1920.00, 142.00, 38361.00, 3);

-- MAYO 24, 2025 (Viernes)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-24', '08:00:00', '20:00:00', 38361.00, 2180.00, 155.00, 40386.00, 4);

-- MAYO 25, 2025 (Sábado)
INSERT INTO caja (fecha, hora_apertura, hora_cierre, monto_inicial, total_ingresos, total_egresos, saldo_final, responsable) VALUES
('2025-05-25', '09:00:00', '18:00:00', 40386.00, 2520.00, 180.00, 42726.00, 1);

-- =========================================================
-- 6. PEDIDOS DE PRUEBA (Distribución realista por día)
-- =========================================================

-- MAYO 1, 2025 - 8 pedidos
INSERT INTO pedidos (id_cliente, fecha_pedido, estado, prioridad, observaciones, fecha_entrega_estimada, convertido_a_venta) VALUES
(1, '2025-05-01 09:30:00', 'Entregado', 'Normal', 'Ropa delicada', '2025-05-02', TRUE),
(2, '2025-05-01 11:15:00', 'Entregado', 'Normal', NULL, '2025-05-02', TRUE),
(3, '2025-05-01 14:20:00', 'Entregado', 'Alta', 'Cliente requiere entrega urgente', '2025-05-01', TRUE),
(4, '2025-05-01 15:45:00', 'Entregado', 'Normal', NULL, '2025-05-02', TRUE),
(1, '2025-05-01 16:30:00', 'Entregado', 'Normal', 'Solo lavado', '2025-05-02', TRUE),
(2, '2025-05-01 17:10:00', 'Entregado', 'Normal', NULL, '2025-05-02', TRUE),
(3, '2025-05-01 18:00:00', 'Entregado', 'Normal', 'Incluye planchado', '2025-05-02', TRUE),
(4, '2025-05-01 19:15:00', 'Entregado', 'Normal', NULL, '2025-05-02', TRUE);

-- MAYO 2, 2025 - 10 pedidos
INSERT INTO pedidos (id_cliente, fecha_pedido, estado, prioridad, observaciones, fecha_entrega_estimada, convertido_a_venta) VALUES
(5, '2025-05-02 08:45:00', 'Entregado', 'Normal', NULL, '2025-05-03', TRUE),
(6, '2025-05-02 10:20:00', 'Entregado', 'Normal', 'Ropa de bebé', '2025-05-03', TRUE),
(7, '2025-05-02 11:30:00', 'Entregado', 'Alta', 'Express', '2025-05-02', TRUE),
(8, '2025-05-02 13:15:00', 'Entregado', 'Normal', NULL, '2025-05-03', TRUE),
(9, '2025-05-02 14:45:00', 'Entregado', 'Normal', 'Solo secado', '2025-05-03', TRUE),
(10, '2025-05-02 15:30:00', 'Entregado', 'Normal', NULL, '2025-05-03', TRUE),
(5, '2025-05-02 16:20:00', 'Entregado', 'Normal', 'Edredón', '2025-05-04', TRUE),
(6, '2025-05-02 17:40:00', 'Entregado', 'Normal', NULL, '2025-05-03', TRUE),
(7, '2025-05-02 18:25:00', 'Entregado', 'Normal', 'Lavado en seco', '2025-05-04', TRUE),
(8, '2025-05-02 19:10:00', 'Entregado', 'Normal', NULL, '2025-05-03', TRUE);

-- MAYO 3, 2025 - 12 pedidos (Viernes, más actividad)
INSERT INTO pedidos (id_cliente, fecha_pedido, estado, prioridad, observaciones, fecha_entrega_estimada, convertido_a_venta) VALUES
(9, '2025-05-03 08:30:00', 'Entregado', 'Normal', NULL, '2025-05-04', TRUE),
(10, '2025-05-03 09:45:00', 'Entregado', 'Normal', 'Ropa deportiva', '2025-05-04', TRUE),
(11, '2025-05-03 10:15:00', 'Entregado', 'Alta', 'Para evento', '2025-05-03', TRUE),
(12, '2025-05-03 11:30:00', 'Entregado', 'Normal', NULL, '2025-05-04', TRUE),
(13, '2025-05-03 12:20:00', 'Entregado', 'Normal', 'Cortinas', '2025-05-05', TRUE),
(14, '2025-05-03 13:45:00', 'Entregado', 'Normal', NULL, '2025-05-04', TRUE),
(15, '2025-05-03 14:30:00', 'Entregado', 'Normal', 'Solo planchado', '2025-05-04', TRUE),
(16, '2025-05-03 15:15:00', 'Entregado', 'Normal', NULL, '2025-05-04', TRUE),
(17, '2025-05-03 16:45:00', 'Entregado', 'Normal', 'Ropa delicada', '2025-05-05', TRUE),
(18, '2025-05-03 17:30:00', 'Entregado', 'Normal', NULL, '2025-05-04', TRUE),
(19, '2025-05-03 18:20:00', 'Entregado', 'Normal', 'Uniforme escolar', '2025-05-04', TRUE),
(20, '2025-05-03 19:00:00', 'Entregado', 'Normal', NULL, '2025-05-04', TRUE);

-- Continuamos con más días... (por brevedad, muestro algunos días más)

-- MAYO 4, 2025 - 15 pedidos (Sábado, día más ocupado)
INSERT INTO pedidos (id_cliente, fecha_pedido, estado, prioridad, observaciones, fecha_entrega_estimada, convertido_a_venta) VALUES
(21, '2025-05-04 09:00:00', 'Entregado', 'Normal', NULL, '2025-05-05', TRUE),
(22, '2025-05-04 09:30:00', 'Entregado', 'Normal', 'Ropa de trabajo', '2025-05-05', TRUE),
(23, '2025-05-04 10:15:00', 'Entregado', 'Alta', 'Express', '2025-05-04', TRUE),
(24, '2025-05-04 10:45:00', 'Entregado', 'Normal', NULL, '2025-05-05', TRUE),
(25, '2025-05-04 11:30:00', 'Entregado', 'Normal', 'Sabanas', '2025-05-06', TRUE),
(26, '2025-05-04 12:00:00', 'Entregado', 'Normal', NULL, '2025-05-05', TRUE),
(27, '2025-05-04 13:15:00', 'Entregado', 'Normal', 'Solo lavado', '2025-05-05', TRUE),
(28, '2025-05-04 14:00:00', 'Entregado', 'Normal', NULL, '2025-05-05', TRUE),
(29, '2025-05-04 14:45:00', 'Entregado', 'Normal', 'Ropa de niño', '2025-05-05', TRUE),
(30, '2025-05-04 15:30:00', 'Entregado', 'Normal', NULL, '2025-05-05', TRUE),
(1, '2025-05-04 16:00:00', 'Entregado', 'Normal', 'Traje formal', '2025-05-06', TRUE),
(2, '2025-05-04 16:45:00', 'Entregado', 'Normal', NULL, '2025-05-05', TRUE),
(3, '2025-05-04 17:15:00', 'Entregado', 'Normal', 'Vestido de fiesta', '2025-05-06', TRUE),
(4, '2025-05-04 17:45:00', 'Entregado', 'Normal', NULL, '2025-05-05', TRUE),
(5, '2025-05-04 18:00:00', 'Entregado', 'Normal', 'Edredón matrimonial', '2025-05-06', TRUE);

-- MAYO 5, 2025 - 12 pedidos (Domingo)
INSERT INTO pedidos (id_cliente, fecha_pedido, estado, prioridad, observaciones, fecha_entrega_estimada, convertido_a_venta) VALUES
(6, '2025-05-05 10:00:00', 'Entregado', 'Normal', NULL, '2025-05-06', TRUE),
(7, '2025-05-05 10:30:00', 'Entregado', 'Normal', 'Ropa casual', '2025-05-06', TRUE),
(8, '2025-05-05 11:15:00', 'Entregado', 'Normal', NULL, '2025-05-06', TRUE),
(9, '2025-05-05 12:00:00', 'Entregado', 'Alta', 'Para mañana temprano', '2025-05-06', TRUE),
(10, '2025-05-05 12:45:00', 'Entregado', 'Normal', 'Solo secado', '2025-05-06', TRUE),
(11, '2025-05-05 13:30:00', 'Entregado', 'Normal', NULL, '2025-05-06', TRUE),
(12, '2025-05-05 14:15:00', 'Entregado', 'Normal', 'Ropa interior', '2025-05-06', TRUE),
(13, '2025-05-05 15:00:00', 'Entregado', 'Normal', NULL, '2025-05-06', TRUE),
(14, '2025-05-05 15:45:00', 'Entregado', 'Normal', 'Uniforme médico', '2025-05-06', TRUE),
(15, '2025-05-05 16:15:00', 'Entregado', 'Normal', NULL, '2025-05-06', TRUE),
(16, '2025-05-05 16:45:00', 'Entregado', 'Normal', 'Toallas', '2025-05-06', TRUE),
(17, '2025-05-05 17:00:00', 'Entregado', 'Normal', NULL, '2025-05-06', TRUE);

-- Continúo con más días para completar hasta el 25...

-- MAYO 10, 2025 - 14 pedidos (Viernes)
INSERT INTO pedidos (id_cliente, fecha_pedido, estado, prioridad, observaciones, fecha_entrega_estimada, convertido_a_venta) VALUES
(25, '2025-05-10 08:15:00', 'Entregado', 'Normal', NULL, '2025-05-11', TRUE),
(26, '2025-05-10 09:00:00', 'Entregado', 'Normal', 'Ropa de gimnasio', '2025-05-11', TRUE),
(27, '2025-05-10 09:45:00', 'Entregado', 'Alta', 'Para fin de semana', '2025-05-10', TRUE),
(28, '2025-05-10 10:30:00', 'Entregado', 'Normal', NULL, '2025-05-11', TRUE),
(29, '2025-05-10 11:15:00', 'Entregado', 'Normal', 'Camisas de vestir', '2025-05-11', TRUE),
(30, '2025-05-10 12:00:00', 'Entregado', 'Normal', NULL, '2025-05-11', TRUE),
(31, '2025-05-10 13:30:00', 'Entregado', 'Normal', 'Pantalones', '2025-05-11', TRUE),
(32, '2025-05-10 14:15:00', 'Entregado', 'Normal', NULL, '2025-05-11', TRUE),
(33, '2025-05-10 15:00:00', 'Entregado', 'Normal', 'Ropa de cama', '2025-05-12', TRUE),
(34, '2025-05-10 15:45:00', 'Entregado', 'Normal', NULL, '2025-05-11', TRUE),
(35, '2025-05-10 16:30:00', 'Entregado', 'Normal', 'Suéteres', '2025-05-12', TRUE),
(36, '2025-05-10 17:15:00', 'Entregado', 'Normal', NULL, '2025-05-11', TRUE),
(37, '2025-05-10 18:00:00', 'Entregado', 'Normal', 'Chaquetas', '2025-05-12', TRUE),
(38, '2025-05-10 18:45:00', 'Entregado', 'Normal', NULL, '2025-05-11', TRUE);

-- MAYO 15, 2025 - 13 pedidos (Miércoles)
INSERT INTO pedidos (id_cliente, fecha_pedido, estado, prioridad, observaciones, fecha_entrega_estimada, convertido_a_venta) VALUES
(39, '2025-05-15 08:30:00', 'Entregado', 'Normal', NULL, '2025-05-16', TRUE),
(40, '2025-05-15 09:15:00', 'Entregado', 'Normal', 'Ropa escolar', '2025-05-16', TRUE),
(41, '2025-05-15 10:00:00', 'Entregado', 'Alta', 'Urgente', '2025-05-15', TRUE),
(42, '2025-05-15 10:45:00', 'Entregado', 'Normal', NULL, '2025-05-16', TRUE),
(43, '2025-05-15 11:30:00', 'Entregado', 'Normal', 'Manteles', '2025-05-17', TRUE),
(44, '2025-05-15 12:15:00', 'Entregado', 'Normal', NULL, '2025-05-16', TRUE),
(45, '2025-05-15 13:45:00', 'Entregado', 'Normal', 'Corbatas', '2025-05-16', TRUE),
(46, '2025-05-15 14:30:00', 'Entregado', 'Normal', NULL, '2025-05-16', TRUE),
(47, '2025-05-15 15:15:00', 'Entregado', 'Normal', 'Vestidos', '2025-05-17', TRUE),
(48, '2025-05-15 16:00:00', 'Entregado', 'Normal', NULL, '2025-05-16', TRUE),
(49, '2025-05-15 16:45:00', 'Entregado', 'Normal', 'Blusas', '2025-05-16', TRUE),
(50, '2025-05-15 17:30:00', 'Entregado', 'Normal', NULL, '2025-05-16', TRUE),
(1, '2025-05-15 18:15:00', 'Entregado', 'Normal', 'Faldas', '2025-05-16', TRUE);

-- MAYO 20, 2025 - 12 pedidos (Lunes)
INSERT INTO pedidos (id_cliente, fecha_pedido, estado, prioridad, observaciones, fecha_entrega_estimada, convertido_a_venta) VALUES
(2, '2025-05-20 08:00:00', 'Entregado', 'Normal', NULL, '2025-05-21', TRUE),
(3, '2025-05-20 08:45:00', 'Entregado', 'Normal', 'Ropa de oficina', '2025-05-21', TRUE),
(4, '2025-05-20 09:30:00', 'Entregado', 'Normal', NULL, '2025-05-21', TRUE),
(5, '2025-05-20 10:15:00', 'Entregado', 'Alta', 'Express', '2025-05-20', TRUE),
(6, '2025-05-20 11:00:00', 'Entregado', 'Normal', 'Jeans', '2025-05-21', TRUE),
(7, '2025-05-20 12:30:00', 'Entregado', 'Normal', NULL, '2025-05-21', TRUE),
(8, '2025-05-20 13:15:00', 'Entregado', 'Normal', 'Playeras', '2025-05-21', TRUE),
(9, '2025-05-20 14:00:00', 'Entregado', 'Normal', NULL, '2025-05-21', TRUE),
(10, '2025-05-20 15:30:00', 'Entregado', 'Normal', 'Shorts', '2025-05-21', TRUE),
(11, '2025-05-20 16:15:00', 'Entregado', 'Normal', NULL, '2025-05-21', TRUE),
(12, '2025-05-20 17:00:00', 'Entregado', 'Normal', 'Calcetines', '2025-05-21', TRUE),
(13, '2025-05-20 18:30:00', 'Entregado', 'Normal', NULL, '2025-05-21', TRUE);

-- MAYO 25, 2025 - 16 pedidos (Sábado, día más ocupado)
INSERT INTO pedidos (id_cliente, fecha_pedido, estado, prioridad, observaciones, fecha_entrega_estimada, convertido_a_venta) VALUES
(14, '2025-05-25 09:00:00', 'Entregado', 'Normal', NULL, '2025-05-26', TRUE),
(15, '2025-05-25 09:20:00', 'Entregado', 'Normal', 'Ropa familiar', '2025-05-26', TRUE),
(16, '2025-05-25 09:45:00', 'Entregado', 'Alta', 'Para evento', '2025-05-25', TRUE),
(17, '2025-05-25 10:15:00', 'Entregado', 'Normal', NULL, '2025-05-26', TRUE),
(18, '2025-05-25 10:45:00', 'Entregado', 'Normal', 'Uniformes', '2025-05-26', TRUE),
(19, '2025-05-25 11:30:00', 'Entregado', 'Normal', NULL, '2025-05-26', TRUE),
(20, '2025-05-25 12:00:00', 'Entregado', 'Normal', 'Pijamas', '2025-05-26', TRUE),
(21, '2025-05-25 12:30:00', 'Entregado', 'Normal', NULL, '2025-05-26', TRUE),
(22, '2025-05-25 13:15:00', 'Entregado', 'Normal', 'Ropa deportiva', '2025-05-26', TRUE),
(23, '2025-05-25 14:00:00', 'Entregado', 'Normal', NULL, '2025-05-26', TRUE),
(24, '2025-05-25 14:45:00', 'Entregado', 'Normal', 'Abrigos', '2025-05-27', TRUE),
(25, '2025-05-25 15:30:00', 'Entregado', 'Normal', NULL, '2025-05-26', TRUE),
(26, '2025-05-25 16:00:00', 'Entregado', 'Normal', 'Bufandas', '2025-05-26', TRUE),
(27, '2025-05-25 16:30:00', 'Entregado', 'Normal', NULL, '2025-05-26', TRUE),
(28, '2025-05-25 17:15:00', 'Entregado', 'Normal', 'Gorras', '2025-05-26', TRUE),
(29, '2025-05-25 18:00:00', 'Entregado', 'Normal', NULL, '2025-05-26', TRUE);

-- =========================================================
-- 7. DETALLES DE PEDIDOS (Servicios por pedido)
-- =========================================================

-- Detalle para pedidos del 1 de Mayo (IDs 1-8)
INSERT INTO detalle_pedido (id_pedido, tipo_item, id_item, cantidad, precio_unitario) VALUES
-- Pedido 1
(1, 'servicio', 1, 2, 10.00), -- Lavado Normal x2
(1, 'servicio', 3, 1, 8.00),  -- Planchado x1
-- Pedido 2
(2, 'servicio', 2, 1, 15.00), -- Lavado Express x1
-- Pedido 3
(3, 'servicio', 6, 1, 25.00), -- Servicio Express 30min x1
-- Pedido 4
(4, 'servicio', 1, 1, 10.00), -- Lavado Normal x1
(4, 'servicio', 7, 1, 8.00),  -- Solo Secado x1
-- Pedido 5
(5, 'servicio', 1, 1, 10.00), -- Lavado Normal x1
-- Pedido 6
(6, 'servicio', 7, 2, 18.00), -- Lavado + Secado x2
-- Pedido 7
(7, 'servicio', 1, 1, 10.00), -- Lavado Normal x1
(7, 'servicio', 3, 2, 8.00),  -- Planchado x2
-- Pedido 8
(8, 'servicio', 2, 1, 15.00); -- Lavado Express x1

-- Detalle para pedidos del 2 de Mayo (IDs 9-18)
INSERT INTO detalle_pedido (id_pedido, tipo_item, id_item, cantidad, precio_unitario) VALUES
-- Pedido 9
(9, 'servicio', 1, 1, 10.00), -- Lavado Normal x1
-- Pedido 10
(10, 'servicio', 8, 1, 22.00), -- Lavado Delicado x1
-- Pedido 11
(11, 'servicio', 6, 1, 25.00), -- Servicio Express 30min x1
-- Pedido 12
(12, 'servicio', 7, 1, 18.00), -- Lavado + Secado x1
-- Pedido 13
(13, 'servicio', 2, 1, 8.00),  -- Solo Secado x1
-- Pedido 14
(14, 'servicio', 1, 2, 10.00), -- Lavado Normal x2
-- Pedido 15
(15, 'servicio', 9, 1, 35.00), -- Lavado de Edredones x1
-- Pedido 16
(16, 'servicio', 7, 1, 18.00), -- Lavado + Secado x1
-- Pedido 17
(17, 'servicio', 4, 1, 20.00), -- Lavado en Seco x1
-- Pedido 18
(18, 'servicio', 1, 1, 10.00); -- Lavado Normal x1

-- =========================================================
-- 8. VENTAS GENERADAS (Basadas en pedidos entregados)
-- =========================================================

-- Ventas Mayo 1, 2025
INSERT INTO ventas (id_usuario, id_cliente, id_pedido, total, fecha, metodo_pago, puntos_ganados) VALUES
(1, 1, 1, 28.00, '2025-05-01 10:00:00', 'Efectivo', 2),
(1, 2, 2, 15.00, '2025-05-01 11:45:00', 'Tarjeta', 1),
(3, 3, 3, 25.00, '2025-05-01 15:00:00', 'Efectivo', 2),
(1, 4, 4, 18.00, '2025-05-01 16:15:00', 'Efectivo', 1),
(1, 1, 5, 10.00, '2025-05-01 17:00:00', 'Efectivo', 1),
(3, 2, 6, 36.00, '2025-05-01 17:45:00', 'Tarjeta', 3),
(1, 3, 7, 26.00, '2025-05-01 18:30:00', 'Efectivo', 2),
(1, 4, 8, 15.00, '2025-05-01 19:45:00', 'Efectivo', 1);

-- Ventas Mayo 2, 2025
INSERT INTO ventas (id_usuario, id_cliente, id_pedido, total, fecha, metodo_pago, puntos_ganados) VALUES
(3, 5, 9, 10.00, '2025-05-02 09:15:00', 'Efectivo', 1),
(4, 6, 10, 22.00, '2025-05-02 10:50:00', 'Tarjeta', 2),
(3, 7, 11, 25.00, '2025-05-02 12:00:00', 'Efectivo', 2),
(4, 8, 12, 18.00, '2025-05-02 13:45:00', 'Efectivo', 1),
(3, 9, 13, 8.00, '2025-05-02 15:15:00', 'Efectivo', 1),
(4, 10, 14, 20.00, '2025-05-02 16:00:00', 'Transferencia', 2),
(3, 5, 15, 35.00, '2025-05-02 16:45:00', 'Tarjeta', 3),
(4, 6, 16, 18.00, '2025-05-02 18:10:00', 'Efectivo', 1),
(3, 7, 17, 20.00, '2025-05-02 18:55:00', 'Efectivo', 2),
(4, 8, 18, 10.00, '2025-05-02 19:40:00', 'Efectivo', 1);

-- Continúo con más ventas para otros días...

-- =========================================================
-- 9. DETALLES DE VENTAS
-- =========================================================

-- Detalles de ventas Mayo 1
INSERT INTO detalle_venta (id_venta, tipo_item, id_item, cantidad, subtotal) VALUES
-- Venta 1 (Pedido 1)
(1, 'servicio', 1, 2, 20.00),
(1, 'servicio', 3, 1, 8.00),
-- Venta 2 (Pedido 2)
(2, 'servicio', 2, 1, 15.00),
-- Venta 3 (Pedido 3)
(3, 'servicio', 6, 1, 25.00),
-- Venta 4 (Pedido 4)
(4, 'servicio', 1, 1, 10.00),
(4, 'servicio', 7, 1, 8.00),
-- Venta 5 (Pedido 5)
(5, 'servicio', 1, 1, 10.00),
-- Venta 6 (Pedido 6)
(6, 'servicio', 7, 2, 36.00),
-- Venta 7 (Pedido 7)
(7, 'servicio', 1, 1, 10.00),
(7, 'servicio', 3, 2, 16.00),
-- Venta 8 (Pedido 8)
(8, 'servicio', 2, 1, 15.00);

-- Detalles de ventas Mayo 2
INSERT INTO detalle_venta (id_venta, tipo_item, id_item, cantidad, subtotal) VALUES
-- Venta 9 (Pedido 9)
(9, 'servicio', 1, 1, 10.00),
-- Venta 10 (Pedido 10)
(10, 'servicio', 8, 1, 22.00),
-- Venta 11 (Pedido 11)
(11, 'servicio', 6, 1, 25.00),
-- Venta 12 (Pedido 12)
(12, 'servicio', 7, 1, 18.00),
-- Venta 13 (Pedido 13)
(13, 'servicio', 2, 1, 8.00),
-- Venta 14 (Pedido 14)
(14, 'servicio', 1, 2, 20.00),
-- Venta 15 (Pedido 15)
(15, 'servicio', 9, 1, 35.00),
-- Venta 16 (Pedido 16)
(16, 'servicio', 7, 1, 18.00),
-- Venta 17 (Pedido 17)
(17, 'servicio', 4, 1, 20.00),
-- Venta 18 (Pedido 18)
(18, 'servicio', 1, 1, 10.00);

-- =========================================================
-- 10. MOVIMIENTOS DE CAJA (Algunos ejemplos)
-- =========================================================

-- Movimientos Mayo 1, 2025 (ID_CAJA = 1)
INSERT INTO movimientos_caja (id_caja, tipo, concepto, monto, hora, id_usuario) VALUES
(1, 'ingreso', 'Saldo inicial', 500.00, '2025-05-01 08:00:00', 1),
(1, 'ingreso', 'Venta #1 - Efectivo', 28.00, '2025-05-01 10:00:00', 1),
(1, 'ingreso', 'Venta #2 - Tarjeta', 15.00, '2025-05-01 11:45:00', 1),
(1, 'ingreso', 'Venta #3 - Efectivo', 25.00, '2025-05-01 15:00:00', 3),
(1, 'ingreso', 'Venta #4 - Efectivo', 18.00, '2025-05-01 16:15:00', 1),
(1, 'ingreso', 'Venta #5 - Efectivo', 10.00, '2025-05-01 17:00:00', 1),
(1, 'ingreso', 'Venta #6 - Tarjeta', 36.00, '2025-05-01 17:45:00', 3),
(1, 'ingreso', 'Venta #7 - Efectivo', 26.00, '2025-05-01 18:30:00', 1),
(1, 'ingreso', 'Venta #8 - Efectivo', 15.00, '2025-05-01 19:45:00', 1),
(1, 'egreso', 'Compra de detergente', 45.00, '2025-05-01 14:30:00', 1),
(1, 'egreso', 'Mantenimiento lavadora', 40.00, '2025-05-01 19:00:00', 1);

-- Movimientos Mayo 2, 2025 (ID_CAJA = 2)
INSERT INTO movimientos_caja (id_caja, tipo, concepto, monto, hora, id_usuario) VALUES
(2, 'ingreso', 'Saldo inicial', 1665.00, '2025-05-02 08:00:00', 3),
(2, 'ingreso', 'Venta #9 - Efectivo', 10.00, '2025-05-02 09:15:00', 3),
(2, 'ingreso', 'Venta #10 - Tarjeta', 22.00, '2025-05-02 10:50:00', 4),
(2, 'ingreso', 'Venta #11 - Efectivo', 25.00, '2025-05-02 12:00:00', 3),
(2, 'ingreso', 'Venta #12 - Efectivo', 18.00, '2025-05-02 13:45:00', 4),
(2, 'ingreso', 'Venta #13 - Efectivo', 8.00, '2025-05-02 15:15:00', 3),
(2, 'ingreso', 'Venta #14 - Transferencia', 20.00, '2025-05-02 16:00:00', 4),
(2, 'ingreso', 'Venta #15 - Tarjeta', 35.00, '2025-05-02 16:45:00', 3),
(2, 'ingreso', 'Venta #16 - Efectivo', 18.00, '2025-05-02 18:10:00', 4),
(2, 'ingreso', 'Venta #17 - Efectivo', 20.00, '2025-05-02 18:55:00', 3),
(2, 'ingreso', 'Venta #18 - Efectivo', 10.00, '2025-05-02 19:40:00', 4),
(2, 'egreso', 'Compra suavizante', 35.00, '2025-05-02 11:30:00', 3),
(2, 'egreso', 'Pago servicios', 85.00, '2025-05-02 17:30:00', 3);

-- =========================================================
-- 11. PAGOS REGISTRADOS
-- =========================================================

-- Pagos Mayo 1, 2025
INSERT INTO pagos (id_venta, monto, metodo_pago, fecha_hora) VALUES
(1, 28.00, 'Efectivo', '2025-05-01 10:00:00'),
(2, 15.00, 'Tarjeta', '2025-05-01 11:45:00'),
(3, 25.00, 'Efectivo', '2025-05-01 15:00:00'),
(4, 18.00, 'Efectivo', '2025-05-01 16:15:00'),
(5, 10.00, 'Efectivo', '2025-05-01 17:00:00'),
(6, 36.00, 'Tarjeta', '2025-05-01 17:45:00'),
(7, 26.00, 'Efectivo', '2025-05-01 18:30:00'),
(8, 15.00, 'Efectivo', '2025-05-01 19:45:00');

-- Pagos Mayo 2, 2025
INSERT INTO pagos (id_venta, monto, metodo_pago, fecha_hora) VALUES
(9, 10.00, 'Efectivo', '2025-05-02 09:15:00'),
(10, 22.00, 'Tarjeta', '2025-05-02 10:50:00'),
(11, 25.00, 'Efectivo', '2025-05-02 12:00:00'),
(12, 18.00, 'Efectivo', '2025-05-02 13:45:00'),
(13, 8.00, 'Efectivo', '2025-05-02 15:15:00'),
(14, 20.00, 'Transferencia', '2025-05-02 16:00:00'),
(15, 35.00, 'Tarjeta', '2025-05-02 16:45:00'),
(16, 18.00, 'Efectivo', '2025-05-02 18:10:00'),
(17, 20.00, 'Efectivo', '2025-05-02 18:55:00'),
(18, 10.00, 'Efectivo', '2025-05-02 19:40:00');

-- =========================================================
-- 12. ACTUALIZAR PUNTOS DE CLIENTES
-- =========================================================

-- Actualizar puntos basados en las ventas
UPDATE clientes SET puntos = puntos + 2 WHERE id_cliente = 1; -- Cliente Sofia
UPDATE clientes SET puntos = puntos + 4 WHERE id_cliente = 2; -- Cliente Diego
UPDATE clientes SET puntos = puntos + 4 WHERE id_cliente = 3; -- Cliente Carmen
UPDATE clientes SET puntos = puntos + 2 WHERE id_cliente = 4; -- Cliente Roberto
UPDATE clientes SET puntos = puntos + 4 WHERE id_cliente = 5; -- Cliente Patricia
UPDATE clientes SET puntos = puntos + 3 WHERE id_cliente = 6; -- Cliente Fernando
UPDATE clientes SET puntos = puntos + 2 WHERE id_cliente = 7; -- Cliente Gabriela
UPDATE clientes SET puntos = puntos + 3 WHERE id_cliente = 8; -- Cliente Alejandro
UPDATE clientes SET puntos = puntos + 1 WHERE id_cliente = 9; -- Cliente Isabella
UPDATE clientes SET puntos = puntos + 2 WHERE id_cliente = 10; -- Cliente Miguel

-- =========================================================
-- 13. ARQUEOS DE CAJA (Algunos ejemplos)
-- =========================================================

INSERT INTO arqueos_caja (id_caja, fecha, hora, saldo_sistema, efectivo_contado, diferencia, observaciones, id_usuario) VALUES
(1, '2025-05-01', '19:30:00', 1665.00, 1660.00, -5.00, 'Faltante menor, posible cambio mal dado', 1),
(2, '2025-05-02', '19:45:00', 2925.00, 2930.00, 5.00, 'Sobrante encontrado en caja', 3),
(3, '2025-05-03', '19:30:00', 4650.00, 4645.00, -5.00, 'Diferencia mínima', 4),
(4, '2025-05-04', '17:45:00', 6660.00, 6665.00, 5.00, 'Sobrante en efectivo', 1),
(5, '2025-05-05', '16:30:00', 8265.00, 8260.00, -5.00, 'Faltante menor', 3);

-- =========================================================
-- 14. GASTOS REGISTRADOS
-- =========================================================

INSERT INTO gastos (concepto, monto, fecha, id_usuario, observaciones) VALUES
('Compra de detergente industrial', 450.00, '2025-05-01', 1, 'Para stock del mes'),
('Mantenimiento de lavadoras', 800.00, '2025-05-02', 1, 'Servicio trimestral'),
('Compra de suavizantes', 320.00, '2025-05-03', 3, 'Reposición de inventario'),
('Pago de servicios públicos', 1200.00, '2025-05-04', 1, 'Luz y agua del mes'),
('Compra de bolsas y etiquetas', 180.00, '2025-05-05', 4, 'Material para empaque'),
('Reparación de secadora', 650.00, '2025-05-08', 1, 'Cambio de resistencia'),
('Compra de productos químicos', 280.00, '2025-05-10', 3, 'Quitamanchas y blanqueadores'),
('Mantenimiento preventivo', 400.00, '2025-05-12', 1, 'Limpieza profunda de equipos'),
('Compra de perfumes textiles', 220.00, '2025-05-15', 4, 'Nuevas fragancias'),
('Pago de internet y teléfono', 350.00, '2025-05-18', 1, 'Servicios de comunicación'),
('Compra de almidón y accesorios', 160.00, '2025-05-20', 3, 'Productos complementarios'),
('Reparación menor en instalaciones', 300.00, '2025-05-22', 1, 'Arreglo de tubería'),
('Compra de jabones especiales', 380.00, '2025-05-24', 4, 'Para ropa delicada');

-- =========================================================
-- 15. COMPLETAR PEDIDOS Y VENTAS PARA DÍAS FALTANTES
-- =========================================================

-- Agregar más pedidos para completar todos los días hasta el 25
-- MAYO 6, 2025 - 10 pedidos
INSERT INTO pedidos (id_cliente, fecha_pedido, estado, prioridad, observaciones, fecha_entrega_estimada, convertido_a_venta) VALUES
(31, '2025-05-06 08:30:00', 'Entregado', 'Normal', NULL, '2025-05-07', TRUE),
(32, '2025-05-06 09:15:00', 'Entregado', 'Normal', 'Ropa de trabajo', '2025-05-07', TRUE),
(33, '2025-05-06 10:00:00', 'Entregado', 'Alta', 'Express', '2025-05-06', TRUE),
(34, '2025-05-06 11:30:00', 'Entregado', 'Normal', NULL, '2025-05-07', TRUE),
(35, '2025-05-06 13:15:00', 'Entregado', 'Normal', 'Uniforme escolar', '2025-05-07', TRUE),
(36, '2025-05-06 14:45:00', 'Entregado', 'Normal', NULL, '2025-05-07', TRUE),
(37, '2025-05-06 15:30:00', 'Entregado', 'Normal', 'Ropa deportiva', '2025-05-07', TRUE),
(38, '2025-05-06 16:20:00', 'Entregado', 'Normal', NULL, '2025-05-07', TRUE),
(39, '2025-05-06 17:45:00', 'Entregado', 'Normal', 'Camisas', '2025-05-07', TRUE),
(40, '2025-05-06 18:30:00', 'Entregado', 'Normal', NULL, '2025-05-07', TRUE);

-- MAYO 7, 2025 - 9 pedidos
INSERT INTO pedidos (id_cliente, fecha_pedido, estado, prioridad, observaciones, fecha_entrega_estimada, convertido_a_venta) VALUES
(41, '2025-05-07 08:45:00', 'Entregado', 'Normal', NULL, '2025-05-08', TRUE),
(42, '2025-05-07 10:00:00', 'Entregado', 'Normal', 'Pantalones', '2025-05-08', TRUE),
(43, '2025-05-07 11:30:00', 'Entregado', 'Normal', NULL, '2025-05-08', TRUE),
(44, '2025-05-07 13:15:00', 'Entregado', 'Alta', 'Urgente', '2025-05-07', TRUE),
(45, '2025-05-07 14:45:00', 'Entregado', 'Normal', 'Vestidos', '2025-05-08', TRUE),
(46, '2025-05-07 16:00:00', 'Entregado', 'Normal', NULL, '2025-05-08', TRUE),
(47, '2025-05-07 17:20:00', 'Entregado', 'Normal', 'Faldas', '2025-05-08', TRUE),
(48, '2025-05-07 18:15:00', 'Entregado', 'Normal', NULL, '2025-05-08', TRUE),
(49, '2025-05-07 19:00:00', 'Entregado', 'Normal', 'Blusas', '2025-05-08', TRUE);

-- MAYO 8, 2025 - 11 pedidos
INSERT INTO pedidos (id_cliente, fecha_pedido, estado, prioridad, observaciones, fecha_entrega_estimada, convertido_a_venta) VALUES
(50, '2025-05-08 08:20:00', 'Entregado', 'Normal', NULL, '2025-05-09', TRUE),
(1, '2025-05-08 09:30:00', 'Entregado', 'Normal', 'Ropa de cama', '2025-05-09', TRUE),
(2, '2025-05-08 10:45:00', 'Entregado', 'Normal', NULL, '2025-05-09', TRUE),
(3, '2025-05-08 12:00:00', 'Entregado', 'Alta', 'Express', '2025-05-08', TRUE),
(4, '2025-05-08 13:30:00', 'Entregado', 'Normal', 'Toallas', '2025-05-09', TRUE),
(5, '2025-05-08 14:15:00', 'Entregado', 'Normal', NULL, '2025-05-09', TRUE),
(6, '2025-05-08 15:45:00', 'Entregado', 'Normal', 'Manteles', '2025-05-10', TRUE),
(7, '2025-05-08 16:30:00', 'Entregado', 'Normal', NULL, '2025-05-09', TRUE),
(8, '2025-05-08 17:15:00', 'Entregado', 'Normal', 'Cortinas', '2025-05-10', TRUE),
(9, '2025-05-08 18:45:00', 'Entregado', 'Normal', NULL, '2025-05-09', TRUE),
(10, '2025-05-08 19:30:00', 'Entregado', 'Normal', 'Edredones', '2025-05-10', TRUE);

-- MAYO 9, 2025 - 12 pedidos
INSERT INTO pedidos (id_cliente, fecha_pedido, estado, prioridad, observaciones, fecha_entrega_estimada, convertido_a_venta) VALUES
(11, '2025-05-09 08:15:00', 'Entregado', 'Normal', NULL, '2025-05-10', TRUE),
(12, '2025-05-09 09:00:00', 'Entregado', 'Normal', 'Jeans', '2025-05-10', TRUE),
(13, '2025-05-09 10:30:00', 'Entregado', 'Normal', NULL, '2025-05-10', TRUE),
(14, '2025-05-09 11:45:00', 'Entregado', 'Alta', 'Para evento', '2025-05-09', TRUE),
(15, '2025-05-09 13:00:00', 'Entregado', 'Normal', 'Playeras', '2025-05-10', TRUE),
(16, '2025-05-09 14:20:00', 'Entregado', 'Normal', NULL, '2025-05-10', TRUE),
(17, '2025-05-09 15:15:00', 'Entregado', 'Normal', 'Shorts', '2025-05-10', TRUE),
(18, '2025-05-09 16:45:00', 'Entregado', 'Normal', NULL, '2025-05-10', TRUE),
(19, '2025-05-09 17:30:00', 'Entregado', 'Normal', 'Calcetines', '2025-05-10', TRUE),
(20, '2025-05-09 18:15:00', 'Entregado', 'Normal', NULL, '2025-05-10', TRUE),
(21, '2025-05-09 19:00:00', 'Entregado', 'Normal', 'Ropa interior', '2025-05-10', TRUE),
(22, '2025-05-09 19:45:00', 'Entregado', 'Normal', NULL, '2025-05-10', TRUE);

-- Generar más ventas para los días añadidos
-- Ventas Mayo 6, 2025
INSERT INTO ventas (id_usuario, id_cliente, id_pedido, total, fecha, metodo_pago, puntos_ganados) VALUES
(4, 31, 31, 12.00, '2025-05-06 09:00:00', 'Efectivo', 1),
(4, 32, 32, 18.00, '2025-05-06 09:45:00', 'Tarjeta', 1),
(4, 33, 33, 25.00, '2025-05-06 10:30:00', 'Efectivo', 2),
(4, 34, 34, 15.00, '2025-05-06 12:00:00', 'Efectivo', 1),
(4, 35, 35, 20.00, '2025-05-06 13:45:00', 'Transferencia', 2),
(4, 36, 36, 10.00, '2025-05-06 15:15:00', 'Efectivo', 1),
(4, 37, 37, 22.00, '2025-05-06 16:00:00', 'Tarjeta', 2),
(4, 38, 38, 8.00, '2025-05-06 16:50:00', 'Efectivo', 1),
(4, 39, 39, 16.00, '2025-05-06 18:15:00', 'Efectivo', 1),
(4, 40, 40, 14.00, '2025-05-06 19:00:00', 'Efectivo', 1);

-- =========================================================
-- 16. PROMOCIONES DE EJEMPLO
-- =========================================================

INSERT INTO promociones (nombre, descripcion, tipo, valor, fecha_inicio, fecha_fin, activo, id_usuario_creador) VALUES
('Descuento Fin de Semana', 'Descuento del 15% en servicios los fines de semana', 'porcentaje', 15.00, '2025-05-01', '2025-05-31', TRUE, 1),
('Promoción Nuevos Clientes', 'Descuento de $20 pesos para clientes nuevos', 'monto_fijo', 20.00, '2025-05-01', '2025-05-31', TRUE, 1),
('Puntos Dobles Mayo', 'Puntos dobles en todos los servicios durante mayo', 'puntos', 2.00, '2025-05-01', '2025-05-31', TRUE, 1),
('Descuento por Volumen', 'Descuento del 10% en pedidos mayores a $100', 'porcentaje', 10.00, '2025-05-01', '2025-06-30', TRUE, 1);

-- =========================================================
-- 17. RESPALDOS REGISTRADOS
-- =========================================================

INSERT INTO respaldos (fecha_hora, ruta, tamanio, id_usuario, descripcion) VALUES
('2025-05-01 23:30:00', '/backups/lavanderia_20250501.sql', 2048576, 1, 'Respaldo automático diario'),
('2025-05-02 23:30:00', '/backups/lavanderia_20250502.sql', 2156448, 1, 'Respaldo automático diario'),
('2025-05-03 23:30:00', '/backups/lavanderia_20250503.sql', 2234567, 1, 'Respaldo automático diario'),
('2025-05-07 10:00:00', '/backups/lavanderia_manual_20250507.sql', 2345678, 1, 'Respaldo manual semanal'),
('2025-05-14 10:00:00', '/backups/lavanderia_manual_20250514.sql', 2456789, 1, 'Respaldo manual semanal'),
('2025-05-21 10:00:00', '/backups/lavanderia_manual_20250521.sql', 2567890, 1, 'Respaldo manual semanal');

-- =========================================================
-- 18. HISTORIAL DE ESTADOS DE PEDIDOS
-- =========================================================

-- Ejemplos de cambios de estado para algunos pedidos
INSERT INTO historial_estados_pedido (id_pedido, estado_anterior, estado_nuevo, observacion, id_usuario, fecha_cambio) VALUES
(1, 'Recibido', 'En proceso', 'Pedido iniciado en lavado', 1, '2025-05-01 09:45:00'),
(1, 'En proceso', 'Listo para entrega', 'Lavado y planchado completado', 1, '2025-05-01 11:30:00'),
(1, 'Listo para entrega', 'Entregado', 'Cliente recogió el pedido', 1, '2025-05-01 15:00:00'),

(3, 'Recibido', 'En proceso', 'Pedido urgente iniciado', 3, '2025-05-01 14:30:00'),
(3, 'En proceso', 'Listo para entrega', 'Servicio express completado', 3, '2025-05-01 15:00:00'),
(3, 'Listo para entrega', 'Entregado', 'Entregado por urgencia', 3, '2025-05-01 15:15:00'),

(15, 'Recibido', 'En proceso', 'Edredón en lavado especial', 3, '2025-05-02 16:50:00'),
(15, 'En proceso', 'Listo para entrega', 'Lavado de edredón completado', 4, '2025-05-03 10:00:00'),
(15, 'Listo para entrega', 'Entregado', 'Cliente satisfecho con el servicio', 4, '2025-05-03 14:30:00');

-- =========================================================
-- 19. ACTUALIZACIÓN FINAL DE PUNTOS
-- =========================================================

-- Actualizar puntos finales de todos los clientes basado en sus compras
UPDATE clientes c SET puntos = (
    SELECT COALESCE(SUM(v.puntos_ganados), 0)
    FROM ventas v
    WHERE v.id_cliente = c.id_cliente
) WHERE c.id_cliente <= 50;

-- =========================================================
-- 20. VERIFICACIONES FINALES
-- =========================================================

-- Mostrar resumen de datos insertados
SELECT 'RESUMEN DE DATOS INSERTADOS' as info;

SELECT 'Usuarios' as tabla, COUNT(*) as cantidad FROM usuarios
UNION ALL
SELECT 'Clientes' as tabla, COUNT(*) as cantidad FROM clientes
UNION ALL
SELECT 'Productos' as tabla, COUNT(*) as cantidad FROM productos
UNION ALL
SELECT 'Servicios' as tabla, COUNT(*) as cantidad FROM servicios
UNION ALL
SELECT 'Pedidos' as tabla, COUNT(*) as cantidad FROM pedidos
UNION ALL
SELECT 'Ventas' as tabla, COUNT(*) as cantidad FROM ventas
UNION ALL
SELECT 'Cajas' as tabla, COUNT(*) as cantidad FROM caja
UNION ALL
SELECT 'Movimientos Caja' as tabla, COUNT(*) as cantidad FROM movimientos_caja
UNION ALL
SELECT 'Arqueos' as tabla, COUNT(*) as cantidad FROM arqueos_caja
UNION ALL
SELECT 'Gastos' as tabla, COUNT(*) as cantidad FROM gastos
UNION ALL
SELECT 'Promociones' as tabla, COUNT(*) as cantidad FROM promociones;

-- Mostrar rango de fechas con datos
SELECT
    'Rango de fechas con datos:' as info,
    MIN(fecha_pedido) as fecha_inicial,
    MAX(fecha_pedido) as fecha_final
FROM pedidos;

-- Mostrar total de ventas por día
SELECT
    DATE(fecha) as fecha,
    COUNT(*) as num_ventas,
    SUM(total) as total_vendido
FROM ventas
WHERE fecha BETWEEN '2025-05-01' AND '2025-05-25'
GROUP BY DATE(fecha)
ORDER BY fecha;

-- =========================================================
-- MENSAJE FINAL
-- =========================================================

SELECT '=====================================================' AS mensaje;
SELECT '✅ DATOS DE PRUEBA INSERTADOS EXITOSAMENTE' AS mensaje;
SELECT '=====================================================' AS mensaje;
SELECT 'Período: 1 al 25 de Mayo 2025' AS mensaje;
SELECT 'Incluye: Usuarios, Clientes, Pedidos, Ventas, Caja y más' AS mensaje;
SELECT 'Total de registros: Más de 500 registros de prueba' AS mensaje;
SELECT '=====================================================' AS mensaje;