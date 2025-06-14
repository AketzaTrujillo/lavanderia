#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Migración - Sistema de Permisos por Usuario (FINAL)
=============================================================

Este script configura el sistema de permisos personalizado para cada cajero.
Debe ejecutarse UNA SOLA VEZ después de implementar los archivos del sistema.

Versión adaptada a la estructura existente de la base de datos.

Autor: Sistema Lavandería v2.0
Fecha: 2025
"""

import os
import sys
from datetime import datetime

# Asegurar que podemos importar módulos del sistema
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

try:
    from conexion import conectar_bd
except ImportError as e:
    print(f"❌ Error: No se pudo importar el módulo de conexión: {e}")
    print("Asegúrese de que el archivo 'conexion.py' esté en el mismo directorio.")
    sys.exit(1)


class MigracionPermisos:
    """Clase para gestionar la migración del sistema de permisos"""

    def __init__(self):
        self.conexion = None
        self.cursor = None

    def conectar(self):
        """Establecer conexión con la base de datos"""
        try:
            self.conexion = conectar_bd()
            self.cursor = self.conexion.cursor()
            print("✅ Conexión a la base de datos establecida")
            return True
        except Exception as e:
            print(f"❌ Error al conectar con la base de datos: {e}")
            return False

    def verificar_estructura_usuarios(self):
        """Verificar la estructura de la tabla usuarios"""
        try:
            self.cursor.execute("DESCRIBE usuarios")
            columnas = self.cursor.fetchall()

            print("📋 Estructura de tabla usuarios:")
            columnas_disponibles = []
            for col in columnas:
                columnas_disponibles.append(col[0])
                print(f"   • {col[0]} ({col[1]})")

            # Verificar columnas esenciales
            if 'id_usuario' not in columnas_disponibles:
                print("❌ Error: Columna 'id_usuario' no encontrada")
                return False, None
            if 'rol' not in columnas_disponibles:
                print("❌ Error: Columna 'rol' no encontrada")
                return False, None

            return True, columnas_disponibles

        except Exception as e:
            print(f"❌ Error al verificar estructura de usuarios: {e}")
            return False, None

    def verificar_tabla_usuarios(self):
        """Verificar que la tabla usuarios existe y obtener cajeros"""
        try:
            self.cursor.execute("SHOW TABLES LIKE 'usuarios'")
            if self.cursor.fetchone():
                print("✅ Tabla 'usuarios' encontrada")

                # Verificar estructura
                estructura_ok, columnas = self.verificar_estructura_usuarios()
                if not estructura_ok:
                    return False

                # Verificar cajeros existentes
                self.cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'cajero'")
                count = self.cursor.fetchone()[0]
                print(f"📊 Cajeros encontrados en el sistema: {count}")

                if count == 0:
                    print("⚠️  No hay cajeros en el sistema actualmente.")
                    print("   El sistema de permisos se configurará para futuros cajeros.")

                return True
            else:
                print("❌ Error: Tabla 'usuarios' no encontrada")
                print("   El sistema de permisos requiere que la tabla usuarios exista.")
                return False

        except Exception as e:
            print(f"❌ Error al verificar tabla usuarios: {e}")
            return False

    def crear_tabla_permisos(self):
        """Crear tabla permisos_usuarios"""
        try:
            print("\n🔄 Creando tabla permisos_usuarios...")

            sql_crear_tabla = """
                CREATE TABLE IF NOT EXISTS permisos_usuarios (
                    id_permiso INT AUTO_INCREMENT PRIMARY KEY,
                    id_usuario INT NOT NULL,
                    modulo VARCHAR(50) NOT NULL,
                    permitido BOOLEAN DEFAULT FALSE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
                    UNIQUE KEY unique_user_module (id_usuario, modulo),
                    INDEX idx_usuario (id_usuario),
                    INDEX idx_modulo (modulo)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """

            self.cursor.execute(sql_crear_tabla)
            print("✅ Tabla permisos_usuarios creada correctamente")
            return True

        except Exception as e:
            print(f"❌ Error al crear tabla permisos_usuarios: {e}")
            return False

    def asignar_permisos_basicos(self):
        """Asignar permisos básicos a cajeros existentes"""
        try:
            print("\n🔄 Asignando permisos básicos a cajeros...")

            # Primero, obtener la estructura de la tabla usuarios para saber qué columnas usar
            self.cursor.execute("DESCRIBE usuarios")
            columnas_usuarios = [col[0] for col in self.cursor.fetchall()]

            # Determinar qué columnas están disponibles
            nombre_col = 'nombre' if 'nombre' in columnas_usuarios else 'usuario'
            email_col = 'correo' if 'correo' in columnas_usuarios else (
                'email' if 'email' in columnas_usuarios else None)

            # Construir query dinámicamente
            if email_col:
                query = f"SELECT id_usuario, {nombre_col}, {email_col} FROM usuarios WHERE rol = 'cajero' ORDER BY {nombre_col}"
            else:
                query = f"SELECT id_usuario, {nombre_col} FROM usuarios WHERE rol = 'cajero' ORDER BY {nombre_col}"

            self.cursor.execute(query)
            cajeros = self.cursor.fetchall()

            if not cajeros:
                print("⚠️  No se encontraron cajeros para asignar permisos")
                print("   Cuando se agreguen cajeros, deberán configurarse sus permisos desde el panel admin.")
                return True

            # Permisos básicos que se asignarán por defecto
            permisos_basicos = [
                'registrar_pedido',
                'gestionar_clientes',
                'registrar_venta',
                'seguimiento_pedidos'
            ]

            # Permisos adicionales que estarán disponibles pero no asignados por defecto
            permisos_adicionales = [
                'gestionar_caja',
                'ver_reportes',
                'gestionar_inventario',
                'aplicar_descuentos'
            ]

            contador_permisos = 0

            for cajero in cajeros:
                if email_col:
                    id_usuario, nombre, email = cajero
                    print(f"   👤 Configurando permisos para: {nombre} ({email})")
                else:
                    id_usuario, nombre = cajero
                    print(f"   👤 Configurando permisos para: {nombre}")

                # Asignar permisos básicos (habilitados)
                for modulo in permisos_basicos:
                    self.cursor.execute("""
                        INSERT IGNORE INTO permisos_usuarios (id_usuario, modulo, permitido) 
                        VALUES (%s, %s, %s)
                    """, (id_usuario, modulo, True))
                    contador_permisos += 1

                # Crear registros para permisos adicionales (deshabilitados)
                for modulo in permisos_adicionales:
                    self.cursor.execute("""
                        INSERT IGNORE INTO permisos_usuarios (id_usuario, modulo, permitido) 
                        VALUES (%s, %s, %s)
                    """, (id_usuario, modulo, False))

            print(f"✅ Permisos configurados para {len(cajeros)} cajeros")
            print(f"📋 Total de registros de permisos creados: {contador_permisos}")
            return True

        except Exception as e:
            print(f"❌ Error al asignar permisos básicos: {e}")
            return False

    def verificar_migracion(self):
        """Verificar que la migración se completó correctamente"""
        try:
            print("\n🔍 Verificando migración...")

            # Verificar que la tabla existe
            self.cursor.execute("SHOW TABLES LIKE 'permisos_usuarios'")
            if not self.cursor.fetchone():
                print("❌ Error: Tabla permisos_usuarios no fue creada")
                return False

            # Verificar estructura de la tabla
            self.cursor.execute("DESCRIBE permisos_usuarios")
            columnas = [col[0] for col in self.cursor.fetchall()]
            columnas_esperadas = ['id_permiso', 'id_usuario', 'modulo', 'permitido',
                                  'fecha_creacion', 'fecha_modificacion']

            for col in columnas_esperadas:
                if col not in columnas:
                    print(f"❌ Error: Columna '{col}' no encontrada en la tabla")
                    return False

            # Verificar datos
            self.cursor.execute("SELECT COUNT(*) FROM permisos_usuarios")
            total_permisos = self.cursor.fetchone()[0]

            # Query corregida con aliases específicos
            self.cursor.execute("""
                SELECT COUNT(DISTINCT p.id_usuario) 
                FROM permisos_usuarios p 
                INNER JOIN usuarios u ON p.id_usuario = u.id_usuario 
                WHERE u.rol = 'cajero'
            """)
            cajeros_con_permisos = self.cursor.fetchone()[0]

            print(f"✅ Estructura de tabla verificada")
            print(f"📊 Total registros de permisos: {total_permisos}")
            print(f"👥 Cajeros con permisos configurados: {cajeros_con_permisos}")

            return True

        except Exception as e:
            print(f"❌ Error en verificación: {e}")
            return False

    def mostrar_resumen(self):
        """Mostrar resumen de permisos configurados"""
        try:
            print("\n📋 RESUMEN DE CONFIGURACIÓN")
            print("=" * 50)

            # Obtener estructura de usuarios para query dinámico
            self.cursor.execute("DESCRIBE usuarios")
            columnas_usuarios = [col[0] for col in self.cursor.fetchall()]

            nombre_col = 'nombre' if 'nombre' in columnas_usuarios else 'usuario'
            email_col = 'correo' if 'correo' in columnas_usuarios else (
                'email' if 'email' in columnas_usuarios else None)

            # Query dinámico según estructura
            if email_col:
                query = f"""
                    SELECT u.{nombre_col}, u.{email_col}, 
                           SUM(CASE WHEN p.permitido = 1 THEN 1 ELSE 0 END) as permisos_activos,
                           COUNT(p.modulo) as total_permisos
                    FROM usuarios u
                    LEFT JOIN permisos_usuarios p ON u.id_usuario = p.id_usuario
                    WHERE u.rol = 'cajero'
                    GROUP BY u.id_usuario, u.{nombre_col}, u.{email_col}
                    ORDER BY u.{nombre_col}
                """
            else:
                query = f"""
                    SELECT u.{nombre_col}, 
                           SUM(CASE WHEN p.permitido = 1 THEN 1 ELSE 0 END) as permisos_activos,
                           COUNT(p.modulo) as total_permisos
                    FROM usuarios u
                    LEFT JOIN permisos_usuarios p ON u.id_usuario = p.id_usuario
                    WHERE u.rol = 'cajero'
                    GROUP BY u.id_usuario, u.{nombre_col}
                    ORDER BY u.{nombre_col}
                """

            self.cursor.execute(query)
            cajeros = self.cursor.fetchall()

            if not cajeros:
                print("⚠️  No hay cajeros en el sistema actualmente.")
                print("   Cuando se agreguen cajeros, aparecerán aquí sus permisos.")
            else:
                for cajero in cajeros:
                    if email_col:
                        nombre, email, activos, total = cajero
                        print(f"👤 {nombre} ({email})")
                    else:
                        nombre, activos, total = cajero
                        print(f"👤 {nombre}")
                    print(f"   ✅ Permisos activos: {activos or 0}")
                    print(f"   📋 Total configurados: {total or 0}")
                    print()

        except Exception as e:
            print(f"Error al mostrar resumen: {e}")

    def cerrar_conexion(self):
        """Cerrar conexión con la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.conexion:
            self.conexion.close()
        print("🔌 Conexión cerrada")

    def ejecutar_migracion_completa(self):
        """Ejecutar el proceso completo de migración"""
        print("🚀 INICIANDO MIGRACIÓN DEL SISTEMA DE PERMISOS")
        print("=" * 60)
        print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print()

        # Paso 1: Conectar
        if not self.conectar():
            return False

        try:
            # Paso 2: Verificar prerequisitos
            if not self.verificar_tabla_usuarios():
                return False

            # Paso 3: Crear tabla de permisos
            if not self.crear_tabla_permisos():
                return False

            # Paso 4: Asignar permisos básicos
            if not self.asignar_permisos_basicos():
                return False

            # Paso 5: Confirmar cambios
            self.conexion.commit()
            print("\n💾 Cambios guardados en la base de datos")

            # Paso 6: Verificar migración
            if not self.verificar_migracion():
                return False

            # Paso 7: Mostrar resumen
            self.mostrar_resumen()

            print("\n🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 60)
            print("\n📝 PRÓXIMOS PASOS:")
            print("1. ✅ Reiniciar la aplicación principal")
            print("2. ✅ Los administradores pueden gestionar permisos desde su panel")
            print("3. ✅ Los cajeros verán solo las funciones autorizadas")
            print("4. ✅ Sistema de permisos totalmente operativo")
            print("\n💡 NOTAS:")
            print("   • Esta migración solo debe ejecutarse UNA VEZ")
            print("   • Si no hay cajeros, se configurarán cuando se agreguen")
            print("   • Los permisos se gestionan desde el panel de administrador")
            print("   • Para probar, cree un usuario cajero desde el panel de administrador")

            return True

        except Exception as e:
            print(f"\n❌ ERROR DURANTE LA MIGRACIÓN: {e}")
            print("🔄 Revertiendo cambios...")
            self.conexion.rollback()
            return False

        finally:
            self.cerrar_conexion()


def main():
    """Función principal"""
    print("🧼 SISTEMA DE LAVANDERÍA - MIGRACIÓN DE PERMISOS")
    print("=" * 60)

    # Verificar que el usuario está seguro
    respuesta = input("\n⚠️  IMPORTANTE: Esta migración modifica la base de datos.\n"
                      "¿Está seguro de que desea continuar? (s/N): ").lower().strip()

    if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Migración cancelada por el usuario")
        return

    # Verificar si ya se ejecutó la migración
    try:
        from conexion import conectar_bd
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute("SHOW TABLES LIKE 'permisos_usuarios'")
        if cursor.fetchone():
            respuesta_sobrescribir = input("\n⚠️  La tabla 'permisos_usuarios' ya existe.\n"
                                           "¿Desea continuar y actualizar la configuración? (s/N): ").lower().strip()
            if respuesta_sobrescribir not in ['s', 'si', 'sí', 'y', 'yes']:
                print("❌ Migración cancelada")
                cursor.close()
                conexion.close()
                return
        cursor.close()
        conexion.close()
    except Exception as e:
        print(f"⚠️  No se pudo verificar el estado de la base de datos: {e}")

    # Ejecutar migración
    migracion = MigracionPermisos()
    exito = migracion.ejecutar_migracion_completa()

    if exito:
        print("\n✨ ¡Migración finalizada con éxito!")
        print("\n📋 INSTRUCCIONES PARA PROBAR EL SISTEMA:")
        print("1. Abra la aplicación principal")
        print("2. Inicie sesión como administrador")
        print("3. Vaya a 'Gestionar Usuarios' y cree un usuario cajero")
        print("4. Luego vaya a 'Gestionar Permisos' para configurar sus permisos")
        print("5. Inicie sesión como cajero para ver el sistema de permisos funcionando")
        input("\nPresione Enter para continuar...")
    else:
        print("\n💥 La migración falló. Revise los errores mostrados.")
        input("\nPresione Enter para salir...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Migración interrumpida por el usuario")
        print("🔄 Asegúrese de ejecutar la migración completamente antes de usar el sistema")
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        print("🔄 Contacte al administrador del sistema")