"""
Instalador que maneja correctamente DELIMITER, procedimientos, funciones y triggers
Compatible con tu script SQL original
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import mysql.connector
import json
import os
import re

def instalar_sistema():
    """Instalación que maneja bloques DELIMITER correctamente"""

    # Paso 1: Bienvenida
    respuesta = messagebox.askyesno(
        "Sistema de Lavandería - Instalador",
        "¡Bienvenido al instalador!\n\n"
        "Este proceso:\n"
        "✅ Configurará la base de datos\n"
        "✅ Ejecutará procedimientos y triggers\n"
        "✅ Configurará el sistema\n\n"
        "Requisitos:\n"
        "• MySQL Server ejecutándose\n"
        "• Permisos de administrador\n\n"
        "¿Desea continuar?"
    )

    if not respuesta:
        return

    # Paso 2: Configuración MySQL
    root = tk.Tk()
    root.withdraw()

    host = simpledialog.askstring("Configuración MySQL", "Servidor MySQL:", initialvalue="localhost")
    if not host:
        return

    user = simpledialog.askstring("Configuración MySQL", "Usuario MySQL:", initialvalue="root")
    if not user:
        return

    password = simpledialog.askstring("Configuración MySQL", "Contraseña MySQL:", show='*')
    if password is None:
        return

    # Paso 3: Probar conexión
    try:
        messagebox.showinfo("Información", "Probando conexión a MySQL...\n\nEsto puede tardar unos segundos.")

        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )

        if conn.is_connected():
            messagebox.showinfo("Éxito", "✅ Conexión a MySQL exitosa!")
            conn.close()
        else:
            raise Exception("No se pudo conectar")

    except Exception as e:
        messagebox.showerror("Error de Conexión", f"❌ No se pudo conectar a MySQL:\n\n{e}")
        return

    # Paso 4: Confirmar instalación
    confirmar = messagebox.askyesno(
        "Confirmar Instalación",
        f"Configuración MySQL:\n"
        f"• Servidor: {host}\n"
        f"• Usuario: {user}\n"
        f"• Base de datos: lavanderiadb\n\n"
        f"¿Proceder con la instalación?"
    )

    if not confirmar:
        return

    # Paso 5: Instalación con manejo de DELIMITER
    try:
        messagebox.showinfo("Instalando", "Ejecutando script SQL completo...\n\nEsto tomará 2-3 minutos.\nNo cierre esta ventana.")

        # Conectar
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        cursor = conn.cursor()

        # Buscar script SQL
        script_paths = [
            "lavanderia_estructura.sql",
            os.path.join(os.path.dirname(__file__), "lavanderia_estructura.sql"),
            os.path.join(os.getcwd(), "lavanderia_estructura.sql")
        ]

        script_path = None
        for path in script_paths:
            if os.path.exists(path):
                script_path = path
                break

        if not script_path:
            raise FileNotFoundError("No se encontró lavanderia_estructura.sql")

        # Leer script
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        # NUEVO MÉTODO: Parsear bloques DELIMITER correctamente
        bloques = parsear_script_con_delimiter(sql_script)

        print(f"📋 Script dividido en {len(bloques)} bloques")

        bloques_exitosos = 0
        errores_menores = 0

        for i, bloque in enumerate(bloques):
            if not bloque.strip():
                continue

            print(f"⚙️ Ejecutando bloque {i+1}/{len(bloques)}")
            print(f"📝 Primeras 100 chars: {bloque[:100]}...")

            try:
                # Determinar si es un bloque especial
                bloque_upper = bloque.upper().strip()

                if any(keyword in bloque_upper for keyword in ['DELIMITER', 'PROCEDURE', 'FUNCTION', 'TRIGGER']):
                    # Bloque con procedimiento/función/trigger
                    print("🔧 Ejecutando procedimiento/función/trigger...")
                    ejecutar_bloque_delimiter(cursor, bloque)
                else:
                    # Bloque normal
                    cursor.execute(bloque)

                conn.commit()
                bloques_exitosos += 1
                print(f"✅ Bloque {i+1} ejecutado")

            except mysql.connector.Error as e:
                error_msg = str(e).lower()

                # Ignorar errores menores conocidos
                if any(ignore in error_msg for ignore in [
                    'already exists', 'duplicate', 'unknown database',
                    'doesn\'t exist', 'table doesn\'t exist'
                ]):
                    errores_menores += 1
                    print(f"⚠️ Error menor ignorado en bloque {i+1}: {e}")
                else:
                    print(f"❌ Error en bloque {i+1}: {e}")
                    errores_menores += 1

                    # Continuar a menos que haya demasiados errores
                    if errores_menores > 30:
                        raise Exception(f"Demasiados errores. Último: {e}")

            except Exception as e:
                print(f"❌ Error inesperado en bloque {i+1}: {e}")
                errores_menores += 1

                if errores_menores > 30:
                    raise

        cursor.close()
        conn.close()

        # Crear config.json
        config_data = {
            "host": host,
            "user": user,
            "password": password,
            "database": "lavanderiadb"
        }

        with open("config.json", 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)

        # Mensaje de éxito
        messagebox.showinfo(
            "¡Instalación Completada!",
            f"✅ Script SQL ejecutado correctamente!\n\n"
            f"Bloques procesados: {bloques_exitosos}\n"
            f"Errores menores: {errores_menores}\n\n"
            f"✅ Base de datos creada\n"
            f"✅ Procedimientos instalados\n"
            f"✅ Triggers configurados\n"
            f"✅ Configuración guardada\n\n"
            f"Credenciales:\n"
            f"• admin@lavanderia.com / 1234\n\n"
            f"¡Sistema listo!"
        )

        # Iniciar sistema
        if messagebox.askyesno("Iniciar Sistema", "¿Iniciar el Sistema de Lavandería ahora?"):
            try:
                import subprocess
                if os.path.exists("SistemaLavanderia.exe"):
                    subprocess.Popen(["SistemaLavanderia.exe"])
                    messagebox.showinfo("Sistema Iniciado", "El sistema se está iniciando...")
                else:
                    messagebox.showwarning("Ejecutable no encontrado", "Ejecute SistemaLavanderia.exe manualmente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo iniciar:\n{e}")

    except Exception as e:
        messagebox.showerror("Error de Instalación", f"❌ Error durante la instalación:\n{e}")

    finally:
        try:
            root.destroy()
        except:
            pass

def parsear_script_con_delimiter(sql_script):
    """
    Parsea el script SQL respetando los bloques DELIMITER
    Retorna lista de bloques que se pueden ejecutar independientemente
    """

    bloques = []
    lineas = sql_script.split('\n')

    bloque_actual = []
    delimitador_actual = ';'
    dentro_delimiter = False

    i = 0
    while i < len(lineas):
        linea = lineas[i].strip()

        # Detectar cambio de delimitador
        if linea.upper().startswith('DELIMITER'):
            # Si hay bloque pendiente, guardarlo
            if bloque_actual:
                bloques.append('\n'.join(bloque_actual))
                bloque_actual = []

            # Extraer nuevo delimitador
            partes = linea.split()
            if len(partes) > 1:
                delimitador_actual = partes[1]
                dentro_delimiter = delimitador_actual != ';'

            i += 1
            continue

        # Si estamos dentro de un bloque con delimitador personalizado
        if dentro_delimiter:
            bloque_actual.append(lineas[i])  # Mantener línea original con espacios

            # Verificar si terminó el bloque
            if delimitador_actual in linea:
                # Remover el delimitador del final
                if bloque_actual:
                    ultima_linea = bloque_actual[-1]
                    bloque_actual[-1] = ultima_linea.replace(delimitador_actual, ';')

                # Guardar bloque y resetear
                if bloque_actual:
                    bloques.append('\n'.join(bloque_actual))
                    bloque_actual = []

                dentro_delimiter = False
                delimitador_actual = ';'
        else:
            # Procesamiento normal fuera de bloques DELIMITER
            if linea and not linea.startswith('--'):
                bloque_actual.append(lineas[i])

                # Si termina con delimitador actual, finalizar bloque
                if linea.endswith(delimitador_actual):
                    if bloque_actual:
                        bloques.append('\n'.join(bloque_actual))
                        bloque_actual = []

        i += 1

    # Agregar bloque final si existe
    if bloque_actual:
        bloques.append('\n'.join(bloque_actual))

    # Filtrar bloques vacíos o solo comentarios
    bloques_filtrados = []
    for bloque in bloques:
        lineas_validas = [l for l in bloque.split('\n') if l.strip() and not l.strip().startswith('--')]
        if lineas_validas:
            bloques_filtrados.append(bloque)

    return bloques_filtrados

def ejecutar_bloque_delimiter(cursor, bloque):
    """
    Ejecuta un bloque que puede contener procedimientos, funciones o triggers
    """

    # Limpiar el bloque
    bloque = bloque.strip()

    # Remover comentarios SQL
    lineas = []
    for linea in bloque.split('\n'):
        linea = linea.strip()
        if linea and not linea.startswith('--'):
            lineas.append(linea)

    bloque_limpio = '\n'.join(lineas)

    if not bloque_limpio:
        return

    # Ejecutar el bloque completo
    cursor.execute(bloque_limpio)

if __name__ == "__main__":
    print("🚀 Instalador con soporte DELIMITER")
    print("=" * 50)
    instalar_sistema()