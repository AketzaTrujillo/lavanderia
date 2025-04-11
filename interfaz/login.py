import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import messagebox
from db.conexion import obtener_conexion

def verificar_login():
    usuario = entrada_usuario.get()
    contraseña = entrada_contraseña.get()

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        query = "SELECT rol FROM usuarios WHERE correo = %s AND contraseña = %s"
        cursor.execute(query, (usuario, contraseña))
        resultado = cursor.fetchone()

        if resultado:
            rol = resultado[0]
            messagebox.showinfo("Acceso correcto", f"Bienvenido, {rol}")
            ventana.destroy()  # Cerrar ventana de login
            # Aquí podrías abrir el menú principal después
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

        cursor.close()
        conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

# Crear ventana
ventana = tk.Tk()
ventana.title("Inicio de sesión - Lavandería")
ventana.geometry("300x200")
ventana.resizable(False, False)

# Widgets
tk.Label(ventana, text="Correo:").pack(pady=5)
entrada_usuario = tk.Entry(ventana, width=30)
entrada_usuario.pack()

tk.Label(ventana, text="Contraseña:").pack(pady=5)
entrada_contraseña = tk.Entry(ventana, show="*", width=30)
entrada_contraseña.pack()

tk.Button(ventana, text="Iniciar sesión", command=verificar_login).pack(pady=15)

ventana.mainloop()