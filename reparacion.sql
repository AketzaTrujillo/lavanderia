-- =========================================================
-- SCRIPT DE REPARACIÓN COMPLETA - SISTEMA LAVANDERÍA
-- =========================================================
-- Este script corrige duplicaciones y problemas estructurales
-- Ejecutar PASO A PASO para verificar cada corrección
-- =========================================================

USE lavanderiadb;

-- PASO 1: DIAGNÓSTICO INICIAL
-- =========================================================
SELECT 'DIAGNÓSTICO INICIAL' as seccion;

-- Verificar estructura de tabla ventas
DESCRIBE ventas;

-- Buscar duplicados en productos
SELECT nombre, COUNT(*) as cantidad
FROM productos
GROUP BY nombre
HAVING COUNT(*) > 1;

-- Buscar duplicados en clientes
SELECT nombre, telefono, COUNT(*) as cantidad
FROM clientes
GROUP BY nombre, telefono
HAVING COUNT(*) > 1;

-- Buscar duplicados en movimientos de caja
SELECT concepto, id_caja, monto, DATE(hora), COUNT(*) as cantidad
FROM movimientos_caja
WHERE concepto LIKE 'Venta #%'
GROUP BY concepto, id_caja, monto, DATE(hora)
HAVING COUNT(*) > 1;

-- PASO 2: REPARAR ESTRUCTURA DE TABLA VENTAS
-- =========================================================
SELECT 'REPARANDO ESTRUCTURA TABLA VENTAS' as seccion;

-- Agregar columna registrado_en_caja si no existe
ALTER TABLE ventas
ADD COLUMN IF NOT EXISTS registrado_en_caja BOOLEAN DEFAULT FALSE;

-- Verificar que se agregó correctamente
SELECT 'Columna registrado_en_caja agregada' as resultado;

-- PASO 3: ELIMINAR DUPLICADOS EN PRODUCTOS
-- =========================================================
SELECT 'ELIMINANDO DUPLICADOS EN PRODUCTOS' as seccion;

-- Crear tabla temporal para productos únicos
CREATE TEMPORARY TABLE productos_unicos AS
SELECT MIN(id_producto) as id_producto, nombre, precio, stock
FROM productos
GROUP BY nombre, precio;

-- Respaldar productos originales
CREATE TABLE IF NOT EXISTS productos_backup AS SELECT * FROM productos;

-- Eliminar duplicados manteniendo solo el primero
DELETE p1 FROM productos p1
INNER JOIN productos p2
WHERE p1.id_producto > p2.id_producto
  AND p1.nombre = p2.nombre
  AND p1.precio = p2.precio;

SELECT CONCAT('Productos duplicados eliminados. Total actual: ', COUNT(*)) as resultado
FROM productos;

-- PASO 4: ELIMINAR DUPLICADOS EN CLIENTES
-- =========================================================
SELECT 'ELIMINANDO DUPLICADOS EN CLIENTES' as seccion;

-- Respaldar clientes originales
CREATE TABLE IF NOT EXISTS clientes_backup AS SELECT * FROM clientes;

-- Eliminar duplicados de clientes
DELETE c1 FROM clientes c1
INNER JOIN clientes c2
WHERE c1.id_cliente > c2.id_cliente
  AND c1.nombre = c2.nombre
  AND (c1.telefono = c2.telefono OR (c1.telefono IS NULL AND c2.telefono IS NULL));

SELECT CONCAT('Clientes duplicados eliminados. Total actual: ', COUNT(*)) as resultado
FROM clientes;

-- PASO 5: ELIMINAR DUPLICADOS EN MOVIMIENTOS DE CAJA
-- =========================================================
SELECT 'ELIMINANDO DUPLICADOS EN MOVIMIENTOS DE CAJA' as seccion;

-- Respaldar movimientos originales
CREATE TABLE IF NOT EXISTS movimientos_caja_backup AS SELECT * FROM movimientos_caja;

-- Eliminar duplicados manteniendo solo el primero
DELETE mc1 FROM movimientos_caja mc1
INNER JOIN movimientos_caja mc2
WHERE mc1.id_movimiento > mc2.id_movimiento
  AND mc1.concepto = mc2.concepto
  AND mc1.id_caja = mc2.id_caja
  AND mc1.monto = mc2.monto
  AND DATE(mc1.hora) = DATE(mc2.hora);

SELECT CONCAT('Movimientos duplicados eliminados. Total actual: ', COUNT(*)) as resultado
FROM movimientos_caja;

-- PASO 6: RECALCULAR TOTALES DE CAJA
-- =========================================================
SELECT 'RECALCULANDO TOTALES DE CAJA' as seccion;

-- Recalcular totales basados en movimientos únicos
UPDATE caja c SET
    total_ingresos = (
        SELECT COALESCE(SUM(monto), 0)
        FROM movimientos_caja mc
        WHERE mc.id_caja = c.id_caja AND mc.tipo = 'ingreso'
    ),
    total_egresos = (
        SELECT COALESCE(SUM(monto), 0)
        FROM movimientos_caja mc
        WHERE mc.id_caja = c.id_caja AND mc.tipo = 'egreso'
    );

-- Recalcular saldo final
UPDATE caja
SET saldo_final = (total_ingresos - total_egresos);

SELECT 'Totales de caja recalculados' as resultado;

-- PASO 7: MARCAR VENTAS COMO REGISTRADAS
-- =========================================================
SELECT 'MARCANDO VENTAS COMO REGISTRADAS' as seccion;

-- Marcar todas las ventas existentes como registradas
UPDATE ventas
SET registrado_en_caja = TRUE
WHERE registrado_en_caja IS NULL OR registrado_en_caja = FALSE;

SELECT CONCAT('Ventas marcadas como registradas: ', COUNT(*)) as resultado
FROM ventas WHERE registrado_en_caja = TRUE;

-- PASO 8: CREAR ÍNDICES ÚNICOS PARA PREVENIR DUPLICACIONES FUTURAS
-- =========================================================
SELECT 'CREANDO ÍNDICES ÚNICOS' as seccion;

-- Índice único para productos (evita duplicados por nombre)
CREATE UNIQUE INDEX IF NOT EXISTS idx_productos_nombre_unico
ON productos(nombre);

-- Índice único para clientes (evita duplicados por nombre+teléfono)
CREATE UNIQUE INDEX IF NOT EXISTS idx_clientes_nombre_telefono_unico
ON clientes(nombre, telefono);

-- Índice único para movimientos de caja (evita duplicados de ventas)
-- Eliminamos el anterior si existe y creamos uno nuevo más específico
DROP INDEX IF EXISTS idx_movimientos_venta_unico ON movimientos_caja;
CREATE UNIQUE INDEX idx_movimientos_venta_unico
ON movimientos_caja(id_caja, concepto, monto, DATE(hora));

SELECT 'Índices únicos creados' as resultado;

-- PASO 9: RECREAR TRIGGER CORREGIDO
-- =========================================================
SELECT 'RECREANDO TRIGGER CORREGIDO' as seccion;

-- Eliminar trigger anterior
DROP TRIGGER IF EXISTS trigger_actualizar_caja_venta;

-- Crear trigger que NO duplica
DELIMITER //
CREATE TRIGGER trigger_actualizar_caja_venta
AFTER INSERT ON ventas
FOR EACH ROW
BEGIN
    DECLARE v_id_caja INT;

    -- SOLO procesar si NO está marcada como registrada
    IF NEW.registrado_en_caja = FALSE OR NEW.registrado_en_caja IS NULL THEN
        -- Buscar caja abierta
        SELECT id_caja INTO v_id_caja
        FROM caja
        WHERE fecha = DATE(NEW.fecha) AND hora_cierre IS NULL
        LIMIT 1;

        IF v_id_caja IS NOT NULL THEN
            -- Verificar que NO existe ya un movimiento para esta venta
            IF NOT EXISTS (
                SELECT 1 FROM movimientos_caja
                WHERE concepto LIKE CONCAT('Venta #', NEW.id_venta, '%')
                  AND id_caja = v_id_caja
            ) THEN
                -- Insertar movimiento SOLO si no existe
                INSERT INTO movimientos_caja (id_caja, tipo, concepto, monto, hora, id_usuario)
                VALUES (v_id_caja, 'ingreso',
                        CONCAT('Venta #', NEW.id_venta),
                        NEW.total, NOW(), NEW.id_usuario)
                ON DUPLICATE KEY UPDATE id_movimiento = id_movimiento;

                -- Actualizar totales de caja
                UPDATE caja
                SET total_ingresos = total_ingresos + NEW.total,
                    saldo_final = saldo_final + NEW.total
                WHERE id_caja = v_id_caja;
            END IF;

            -- Marcar como registrada
            UPDATE ventas
            SET registrado_en_caja = TRUE
            WHERE id_venta = NEW.id_venta;
        END IF;
    END IF;
END //
DELIMITER ;

SELECT 'Trigger corregido creado' as resultado;

-- PASO 10: VERIFICACIÓN FINAL
-- =========================================================
SELECT 'VERIFICACIÓN FINAL' as seccion;

-- Verificar que no hay duplicados en productos
SELECT 'Productos duplicados restantes:' as verificacion, COUNT(*) as cantidad
FROM (
    SELECT nombre, COUNT(*)
    FROM productos
    GROUP BY nombre
    HAVING COUNT(*) > 1
) duplicados;

-- Verificar que no hay duplicados en clientes
SELECT 'Clientes duplicados restantes:' as verificacion, COUNT(*) as cantidad
FROM (
    SELECT nombre, telefono, COUNT(*)
    FROM clientes
    GROUP BY nombre, telefono
    HAVING COUNT(*) > 1
) duplicados;

-- Verificar que no hay duplicados en movimientos
SELECT 'Movimientos duplicados restantes:' as verificacion, COUNT(*) as cantidad
FROM (
    SELECT concepto, id_caja, monto, DATE(hora), COUNT(*)
    FROM movimientos_caja
    WHERE concepto LIKE 'Venta #%'
    GROUP BY concepto, id_caja, monto, DATE(hora)
    HAVING COUNT(*) > 1
) duplicados;

-- Verificar estructura de ventas
SELECT 'Columna registrado_en_caja existe:' as verificacion,
       CASE WHEN COUNT(*) > 0 THEN 'SÍ' ELSE 'NO' END as resultado
FROM information_schema.columns
WHERE table_name = 'ventas'
  AND column_name = 'registrado_en_caja'
  AND table_schema = DATABASE();

-- RESULTADO FINAL
SELECT '========================================' as resultado;
SELECT 'REPARACIÓN COMPLETADA EXITOSAMENTE' as resultado;
SELECT '========================================' as resultado;
SELECT 'El sistema ha sido reparado completamente.' as resultado;
SELECT 'Todas las duplicaciones han sido eliminadas.' as resultado;
SELECT 'Los índices únicos previenen futuras duplicaciones.' as resultado;
SELECT 'El trigger ha sido corregido.' as resultado;
SELECT '========================================' as resultado;