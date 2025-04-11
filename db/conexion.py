import mysql.connector
import json

with open("config.json") as archivo:
    config = json.load(archivo)

def obtener_conexion():
    return mysql.connector.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        database=config["database"]
    )