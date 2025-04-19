"""
Sistema de inicio de sesión para la aplicación de Lavandería
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter.font import BOLD
import os
import sys
import random
import utileria as utl

# Asegurar que podamos importar los módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Importar módulos del sistema
try:
    from conexion import conectar_bd
    from email_sender import enviar_codigo
except ImportError as e:
    print(f"Error al importar módulos: {e}")


class App:
    """Clase principal para la pantalla de inicio de sesión"""

    def __init__(self):
        # Configuración de la ventana principal
        self.ventana = tk.Tk()
        self.ventana.title('Sistema de Lavandería - Inicio de sesión')
        self.ventana.geometry('800x500')
        self.ventana.config(bg='#fcfcfc')
        self.ventana.resizable(width=0, height=0)

        # Centrar ventana
        utl.centrar_ventana(self.ventana, 800, 500)

        # Establecer ícono si existe
        try:
            if os.path.exists("Img/lavadora.ico"):
                self.ventana.iconbitmap("Img/lavadora.ico")
        except Exception:
            pass  # Si no se puede cargar el ícono, continuar sin él

        # Cargar imagen del logo
        try:
            self.logo = utl.leer_imagen("Img/lavadora.jpg", (200, 200))
        except Exception:
            # Si no se puede cargar la imagen, crear un canvas con colores
            self.logo = None

        # Construir interfaz gráfica
        self.construir_interfaz()

        # Iniciar bucle principal
        self.ventana.mainloop()

    def construir_interfaz(self):
        """Construye la interfaz gráfica del login"""
        # Panel izquierdo (logo)
        frame_logo = tk.Frame(
            self.ventana,
            bd=0,
            width=300,
            relief=tk.SOLID,
            padx=10,
            pady=10,
            bg='#3a7ff6'
        )
        frame_logo.pack(side="left", expand=tk.YES, fill=tk.BOTH)

        # Si hay logo, mostrarlo
        if self.logo:
            label_logo = tk.Label(frame_logo, image=self.logo, bg='#3a7ff6')
            label_logo.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            # Si no hay logo, mostrar un título
            label_titulo = tk.Label(
                frame_logo,
                text="SISTEMA DE\nLAVANDERÍA",
                font=('Helvetica', 20, 'bold'),
                bg='#3a7ff6',
                fg='white'
            )
            label_titulo.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Panel derecho (formulario)
        frame_form = tk.Frame(
            self.ventana,
            bd=0,
            relief=tk.SOLID,
            bg='#fcfcfc'
        )
        frame_form.pack(side="right", expand=tk.YES, fill=tk.BOTH)

        # Título del formulario
        frame_form_top = tk.Frame(
            frame_form,
            height=50,
            bd=0,
            relief=tk.SOLID,
            bg='#fcfcfc'
        )
        frame_form_top.pack(side="top", fill=tk.X)

        title = tk.Label(
            frame_form_top,
            text="Inicio de sesión",
            font=('Times', 30),
            fg="#666a88",
            bg='#fcfcfc',
            pady=50
        )
        title.pack(expand=tk.YES, fill=tk.BOTH)

        # Contenido del formulario
        frame_form_fill = tk.Frame(
            frame_form,
            height=50,
            bd=0,
            relief=tk.SOLID,
            bg='#fcfcfc'
        )
        frame_form_fill.pack(side="bottom", expand=tk.YES, fill=tk.BOTH)

        # Etiqueta y campo de usuario
        etiqueta_usuario = tk.Label(
            frame_form_fill,
            text="Usuario (Correo)",
            font=('Times', 14),
            fg="#666a88",
            bg='#fcfcfc',
            anchor="w"
        )
        etiqueta_usuario.pack(fill=tk.X, padx=20, pady=5)

        self.usuario = ttk.Entry(frame_form_fill, font=('Times', 14))
        self.usuario.pack(fill=tk.X, padx=20, pady=10)

        # Etiqueta y campo de contraseña
        etiqueta_password = tk.Label(
            frame_form_fill,
            text="Contraseña",
            font=('Times', 14),
            fg="#666a88",
            bg='#fcfcfc',
            anchor="w"
        )
        etiqueta_password.pack(fill=tk.X, padx=20, pady=5)

        self.password = ttk.Entry(frame_form_fill, font=('Times', 14), show="*")
        self.password.pack(fill=tk.X, padx=20, pady=10)

        # Botón de inicio de sesión
        inicio = tk.Button(
            frame_form_fill,
            text="Iniciar sesión",
            font=('Times', 15, BOLD),
            bg='#3a7ff6',
            bd=0,
            fg="#fff",
            command=self.verificar
        )
        inicio.pack(fill=tk.X, padx=20, pady=20)
        inicio.bind("<Return>", lambda event: self.verificar())

        # Botón de recuperación de contraseña
        recuperar = tk.Button(
            frame_form_fill,
            text="¿Olvidaste tu contraseña?",
            font=('Times', 11),
            bg='#fcfcfc',
            fg="#3a7ff6",
            bd=0,
            cursor="hand2",
            command=self.recuperar_contrasena
        )
        recuperar.pack(pady=(0, 10))

    def verificar(self):
        """Verifica las credenciales del usuario"""
        correo = self.usuario.get().strip()
        password = self.password.get().strip()

        # Validación básica
        if not correo or not password:
            messagebox.showwarning(
                "Campos incompletos",
                "Por favor, complete todos los campos."
            )
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT nombre, rol FROM usuarios WHERE correo = %s AND contraseña = %s",
                (correo, password)
            )
            resultado = cursor.fetchone()
            conexion.close()

            if resultado:
                nombre_usuario, rol = resultado
                messagebox.showinfo("Bienvenido", f"Hola {nombre_usuario}, rol: {rol}")
                self.ventana.destroy()

                # Abrir panel según rol
                if rol == "admin":
                    from admin_view import MasterPanel
                    MasterPanel()
                elif rol == "cajero":
                    from cajero_view import CajeroPanel
                    CajeroPanel()
                else:
                    messagebox.showwarning("Rol desconocido", f"Rol no reconocido: {rol}")
            else:
                messagebox.showerror(
                    "Error de autenticación",
                    "Correo o contraseña incorrectos.\nPor favor, verifique sus credenciales."
                )
                # Limpiar campo de contraseña
                self.password.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror(
                "Error de conexión",
                f"No se pudo conectar con la base de datos.\nError: {str(e)}"
            )

    def recuperar_contrasena(self):
        """Proceso para recuperar contraseña olvidada"""
        correo = self.usuario.get().strip()

        if not correo:
            messagebox.showwarning(
                "Campo vacío",
                "Por favor ingresa tu correo electrónico en el campo de usuario."
            )
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("SELECT rol FROM usuarios WHERE correo = %s", (correo,))
            resultado = cursor.fetchone()

            if not resultado:
                messagebox.showerror(
                    "Correo no encontrado",
                    "El correo ingresado no está registrado en el sistema."
                )
                return

            rol = resultado[0]

            # Validar que sea administrador para recuperar
            if rol != "admin":
                messagebox.showwarning(
                    "No autorizado",
                    "Solo los administradores pueden recuperar su contraseña por este medio.\n"
                    "Por favor, contacta al administrador del sistema."
                )
                return

            # Generar código y enviarlo
            codigo = str(random.randint(100000, 999999))
            enviado = False

            try:
                enviado = enviar_codigo(correo, codigo)
            except Exception as e:
                messagebox.showerror(
                    "Error de envío",
                    f"No se pudo enviar el correo de recuperación.\nError: {str(e)}"
                )
                return

            if not enviado:
                messagebox.showerror(
                    "Error de envío",
                    "No se pudo enviar el código. Verifica la configuración del servidor de correo."
                )
                return

            # Solicitar código al usuario
            ingresado = simpledialog.askstring(
                "Verificación",
                f"Se envió un código a {correo}.\nIngresa el código:",
                parent=self.ventana
            )

            # Verificar código
            if ingresado and ingresado == codigo:
                # Solicitar nueva contraseña
                nueva_contra = simpledialog.askstring(
                    "Nueva contraseña",
                    "Ingresa tu nueva contraseña:",
                    show='*',
                    parent=self.ventana
                )

                if nueva_contra:
                    cursor.execute(
                        "UPDATE usuarios SET contraseña = %s WHERE correo = %s",
                        (nueva_contra, correo)
                    )
                    conexion.commit()
                    messagebox.showinfo(
                        "Éxito",
                        "Contraseña actualizada correctamente."
                    )
            else:
                messagebox.showerror(
                    "Código incorrecto",
                    "El código ingresado no es válido o ha sido cancelado."
                )

            conexion.close()

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Ha ocurrido un error durante el proceso de recuperación.\nError: {str(e)}"
            )