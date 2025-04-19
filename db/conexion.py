"""
Módulo de conexión a base de datos para el Sistema de Gestión de Lavandería
Proporciona funciones para conectar con la base de datos MySQL
"""

import os
import json
import mysql.connector
from mysql.connector import Error

# Ruta del archivo de configuración
CONFIG_FILE = "config.json"


def cargar_configuracion():
    """
    Carga la configuración de la base de datos desde el archivo config.json

    Returns:
        dict: Configuración de la base de datos
    """
    # Valores predeterminados
    config_default = {
        "host": "localhost",
        "user": "root",
        "password": "1234",
        "database": "lavanderiadb"
    }

    # Intentar cargar desde archivo
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as archivo:
                return json.load(archivo)
        else:
            # Si no existe el archivo, crearlo con valores predeterminados
            with open(CONFIG_FILE, 'w') as archivo:
                json.dump(config_default, archivo, indent=4)
            return config_default
    except Exception as e:
        print(f"Error al cargar configuración: {e}")
        return config_default


def conectar_bd():
    """
    Establece una conexión con la base de datos MySQL

    Returns:
        mysql.connector.connection.MySQLConnection: Objeto de conexión

    Raises:
        Error: Si no se puede establecer la conexión
    """
    try:
        # Cargar configuración
        config = cargar_configuracion()

        # Conectar a la base de datos
        conexion = mysql.connector.connect(
            host=config["host"],
            user=config["user"],
            password=config["password"],
            database=config["database"],
            auth_plugin='mysql_native_password'
        )

        return conexion
    except Error as e:
        raise Error(f"Error al conectar a la base de datos: {e}")


def ejecutar_consulta(consulta, parametros=None, obtener_resultado=True):
    """
    Ejecuta una consulta SQL en la base de datos

    Args:
        consulta (str): Consulta SQL a ejecutar
        parametros (tuple, opcional): Parámetros para la consulta. Por defecto None.
        obtener_resultado (bool, opcional): Indica si debe devolver resultados. Por defecto True.

    Returns:
        list or bool: Resultados de la consulta si obtener_resultado es True,
                     o True/False si la operación tuvo éxito

    Raises:
        Exception: Si ocurre un error al ejecutar la consulta
    """
    conexion = None
    cursor = None
    resultado = None

    try:
        # Establecer conexión
        conexion = conectar_bd()
        cursor = conexion.cursor()

        # Ejecutar consulta
        if parametros:
            cursor.execute(consulta, parametros)
        else:
            cursor.execute(consulta)

        # Obtener resultados si es necesario
        if obtener_resultado:
            resultado = cursor.fetchall()
        else:
            conexion.commit()
            resultado = True

        return resultado
    except Exception as e:
        # En caso de error, hacer rollback
        if conexion:
            try:
                conexion.rollback()
            except:
                pass
        raise Exception(f"Error al ejecutar la consulta: {e}")
    finally:
        # Cerrar cursor y conexión
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


# Para probar la conexión de forma independiente
if __name__ == "__main__":
    try:
        conn = conectar_bd()
        print("Conexión establecida correctamente.")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")