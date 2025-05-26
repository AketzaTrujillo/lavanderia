"""
Sistema de inicio de sesión para la aplicación de Lavandería
MEJORADO: Funcionalidad Enter y ventana maximizada
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

        # CONFIGURAR VENTANA MAXIMIZADA (con bordes)
        self.ventana.state('zoomed')  # Windows - maximizada con bordes
        # Para Linux también intentar:
        try:
            self.ventana.attributes('-zoomed', True)  # Linux
        except:
            pass

        self.ventana.config(bg='#fcfcfc')
        self.ventana.resizable(width=1, height=1)  # Permitir redimensionar

        # Establecer ícono si existe
        try:
            if os.path.exists("Img/lavadora.ico"):
                self.ventana.iconbitmap("Img/lavadora.ico")
        except Exception:
            pass  # Si no se puede cargar el ícono, continuar sin él

        # Cargar imagen del logo
        try:
            self.logo = utl.leer_imagen("Img/logo_lavanderia.png", (800, 200))
        except Exception:
            # Si no se puede cargar la imagen, crear un canvas con colores
            self.logo = None

        # CONFIGURAR TECLAS ESPECIALES
        self.configurar_teclas()

        # Construir interfaz gráfica
        self.construir_interfaz()

        # CONFIGURAR FOCUS INICIAL EN USUARIO
        self.ventana.after(100, self.configurar_focus_inicial)

        # Iniciar bucle principal
        self.ventana.mainloop()

    def configurar_teclas(self):
        """Configura las teclas especiales del sistema"""

        # F11 para alternar maximizado
        self.ventana.bind('<F11>', self.toggle_maximizado)

        # Alt+F4 para cerrar (Windows)
        self.ventana.bind('<Alt-F4>', self.cerrar_aplicacion)

    def minimizar_ventana(self, event=None):
        """Minimiza la ventana"""
        self.ventana.iconify()

    def toggle_maximizado(self, event=None):
        """Alterna entre ventana maximizada y normal"""
        try:
            if self.ventana.state() == 'zoomed':
                self.ventana.state('normal')
                self.ventana.geometry('800x500')
                utl.centrar_ventana(self.ventana, 800, 500)
            else:
                self.ventana.state('zoomed')
        except:
            pass

    def cerrar_aplicacion(self, event=None):
        """Cierra la aplicación de forma segura"""
        if messagebox.askyesno("Salir", "¿Está seguro de que desea salir del sistema?"):
            self.ventana.quit()
            self.ventana.destroy()

    def configurar_focus_inicial(self):
        """Configura el foco inicial en el campo de usuario"""
        self.usuario.focus_set()

    def mover_a_password(self, event=None):
        """Mueve el foco al campo de contraseña cuando se presiona Enter en usuario"""
        self.password.focus_set()

    def verificar_con_enter(self, event=None):
        """Ejecuta la verificación cuando se presiona Enter en el campo de contraseña"""
        self.verificar()

    def construir_interfaz(self):
        """Construye la interfaz gráfica del login con colores invertidos"""

        # Panel izquierdo (blanco, con logo)
        frame_logo = tk.Frame(
            self.ventana,
            bd=0,
            width=300,
            relief=tk.SOLID,
            padx=10,
            pady=10,
            bg='#ffffff'  # ← fondo blanco ahora
        )
        frame_logo.pack(side="left", expand=tk.YES, fill=tk.BOTH)

        # Mostrar logo (y mantener referencia para que no se borre)
        if self.logo:
            self.label_logo = tk.Label(frame_logo, image=self.logo, bg='#ffffff')
            self.label_logo.image = self.logo  # <- ¡mantener referencia!
            self.label_logo.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        else:
            label_titulo = tk.Label(
                frame_logo,
                text="SISTEMA DE\nLAVANDERÍA",
                font=('Helvetica', 20, 'bold'),
                bg='#ffffff',
                fg='#3a7ff6'
            )
            label_titulo.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Panel derecho (formulario - azul)
        frame_form = tk.Frame(
            self.ventana,
            bd=0,
            relief=tk.SOLID,
            bg='#3a7ff6'  # ← azul
        )
        frame_form.pack(side="right", expand=tk.YES, fill=tk.BOTH)

        # Título del formulario
        frame_form_top = tk.Frame(
            frame_form,
            height=50,
            bd=0,
            relief=tk.SOLID,
            bg='#3a7ff6'
        )
        frame_form_top.pack(side="top", fill=tk.X)

        title = tk.Label(
            frame_form_top,
            text="Inicio de sesión",
            font=('Times', 30),
            fg="#ffffff",  # ← texto blanco
            bg='#3a7ff6',
            pady=50
        )
        title.pack(expand=tk.YES, fill=tk.BOTH)

        # Contenido del formulario
        frame_form_fill = tk.Frame(
            frame_form,
            height=50,
            bd=0,
            relief=tk.SOLID,
            bg='#3a7ff6'
        )
        frame_form_fill.pack(side="bottom", expand=tk.YES, fill=tk.BOTH)

        # Etiqueta y campo de usuario
        etiqueta_usuario = tk.Label(
            frame_form_fill,
            text="Usuario (Correo)",
            font=('Times', 14),
            fg="#ffffff",
            bg='#3a7ff6',
            anchor="w"
        )
        etiqueta_usuario.pack(fill=tk.X, padx=20, pady=5)

        self.usuario = ttk.Entry(frame_form_fill, font=('Times', 14))
        self.usuario.pack(fill=tk.X, padx=20, pady=10)

        # VINCULAR ENTER EN CAMPO USUARIO
        self.usuario.bind('<Return>', self.mover_a_password)

        # Etiqueta y campo de contraseña
        etiqueta_password = tk.Label(
            frame_form_fill,
            text="Contraseña",
            font=('Times', 14),
            fg="#ffffff",
            bg='#3a7ff6',
            anchor="w"
        )
        etiqueta_password.pack(fill=tk.X, padx=20, pady=5)

        self.password = ttk.Entry(frame_form_fill, font=('Times', 14), show="*")
        self.password.pack(fill=tk.X, padx=20, pady=10)

        # VINCULAR ENTER EN CAMPO PASSWORD PARA INICIAR SESIÓN
        self.password.bind('<Return>', self.verificar_con_enter)

        # Botón de inicio de sesión
        inicio = tk.Button(
            frame_form_fill,
            text="Iniciar sesión",
            font=('Times', 15, BOLD),
            bg='#ffffff',
            fg="#3a7ff6",
            bd=0,
            command=self.verificar
        )
        inicio.pack(fill=tk.X, padx=20, pady=20)

        # VINCULAR ENTER TAMBIÉN AL BOTÓN
        inicio.bind("<Return>", lambda event: self.verificar())

        # Botón de recuperación de contraseña
        recuperar = tk.Button(
            frame_form_fill,
            text="¿Olvidaste tu contraseña?",
            font=('Times', 11),
            bg='#3a7ff6',
            fg="#ffffff",
            bd=0,
            cursor="hand2",
            command=self.recuperar_contrasena
        )
        recuperar.pack(pady=(0, 10))

        # Instrucciones en la parte inferior
        instrucciones = tk.Label(
            frame_form_fill,
            text="Presiona ENTER para iniciar sesión",
            font=('Times', 9),
            bg='#3a7ff6',
            fg="#a0c4ff",
            wraplength=400
        )
        instrucciones.pack(pady=(20, 10))

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
            # Regresar foco al campo vacío
            if not correo:
                self.usuario.focus_set()
            else:
                self.password.focus_set()
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT id_usuario, nombre, rol FROM usuarios WHERE correo = %s AND contraseña = %s",
                (correo, password)
            )
            resultado = cursor.fetchone()
            conexion.close()

            if resultado:
                id_usuario, nombre_usuario, rol = resultado
                messagebox.showinfo("Bienvenido", f"Hola {nombre_usuario}, rol: {rol}")
                self.ventana.destroy()

                # Abrir panel según rol con el ID de usuario
                if rol == "admin":
                    from admin_view import MasterPanel
                    MasterPanel(id_usuario=id_usuario)
                elif rol == "cajero":
                    from cajero_view import CajeroPanel
                    CajeroPanel(id_usuario=id_usuario)
                else:
                    messagebox.showwarning("Rol desconocido", f"Rol no reconocido: {rol}")
            else:
                messagebox.showerror(
                    "Error de autenticación",
                    "Correo o contraseña incorrectos.\nPor favor, verifique sus credenciales."
                )
                # Limpiar campo de contraseña y regresar foco a usuario
                self.password.delete(0, tk.END)
                self.usuario.focus_set()
                # Seleccionar todo el texto del usuario para facilitar corrección
                self.usuario.select_range(0, tk.END)

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
            self.usuario.focus_set()
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
                    # Colocar la nueva contraseña en el campo
                    self.password.delete(0, tk.END)
                    self.password.insert(0, nueva_contra)
                    self.password.focus_set()
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