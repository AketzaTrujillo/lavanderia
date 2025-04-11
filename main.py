from db.conexion import obtener_conexion

conexion = obtener_conexion()

if conexion.is_connected():
    print("✅ Conexión exitosa a la base de datos")
else:
    print("❌ No se pudo conectar")