import mysql.connector

def conectar_bd():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="tired2019",
        database="lavanderiadb",
        auth_plugin = 'mysql_native_password'
    )
