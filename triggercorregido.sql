-- SOLUCIÓN: Modificar el trigger para usar el RESPONSABLE DE LA CAJA
-- Así será consistente con cómo se muestra en la interfaz

USE lavanderiadb;

-- Eliminar trigger actual
DROP TRIGGER IF EXISTS trigger_venta_a_caja;

-- Crear trigger que usa el RESPONSABLE DE LA CAJA (igual que en la interfaz)
DELIMITER //
CREATE TRIGGER trigger_venta_a_caja
AFTER INSERT ON ventas
FOR EACH ROW
BEGIN
    DECLARE v_id_caja INT;
    DECLARE v_responsable_caja INT;  -- Este será el ID del responsable real de la caja

    -- Buscar caja abierta Y su responsable (igual que en la interfaz)
    SELECT id_caja, responsable INTO v_id_caja, v_responsable_caja
    FROM caja
    WHERE fecha = DATE(NEW.fecha) AND hora_cierre IS NULL
    LIMIT 1;

    -- Si hay caja abierta, registrar el movimiento
    IF v_id_caja IS NOT NULL AND v_responsable_caja IS NOT NULL THEN
        -- Insertar movimiento usando el RESPONSABLE DE LA CAJA
        -- (NO el usuario de la venta, sino el responsable actual de la caja)
        INSERT IGNORE INTO movimientos_caja (id_caja, tipo, concepto, monto, hora, id_usuario)
        VALUES (
            v_id_caja,
            'ingreso',
            CONCAT('Venta #', NEW.id_venta, ' - ', COALESCE(NEW.metodo_pago, 'N/A')),
            NEW.total,
            NEW.fecha,
            v_responsable_caja  -- ← USAR EL RESPONSABLE DE LA CAJA, no el usuario de la venta
        );

        -- Actualizar totales de caja
        IF NEW.metodo_pago = 'Efectivo' THEN
            UPDATE caja
            SET total_ingresos = total_ingresos + NEW.total,
                saldo_final = saldo_final + NEW.total
            WHERE id_caja = v_id_caja;
        ELSE
            UPDATE caja
            SET total_ingresos = total_ingresos + NEW.total
            WHERE id_caja = v_id_caja;
        END IF;
    END IF;
END //
DELIMITER ;

-- Verificar que se creó correctamente
SELECT 'Trigger actualizado - ahora usa responsable de caja' as resultado;

-- OPCIONAL: Actualizar movimientos existentes para que usen el responsable de caja
UPDATE movimientos_caja mc
JOIN caja c ON mc.id_caja = c.id_caja
SET mc.id_usuario = c.responsable
WHERE mc.concepto LIKE 'Venta #%'
  AND mc.id_usuario != c.responsable;

SELECT 'Movimientos existentes actualizados' as resultado;