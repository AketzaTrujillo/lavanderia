import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog
from tkinter.font import BOLD
import utileria as utl
from admin_view import MasterPanel
from cajero_view import CajeroPanel
from conexion import conectar_bd  
import random
from email_sender import enviar_codigo

class App: 
    

    def verificar(self):
        correo = self.usuario.get().strip()
        password = self.password.get().strip()

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("SELECT nombre, rol FROM usuarios WHERE correo = %s AND contraseña = %s", (correo, password))
            resultado = cursor.fetchone()
            print("Correo ingresado:", correo)
            print("Contraseña ingresada:", password)
            print("Resultado en BD:", resultado)
            conexion.close()

            if resultado:
                nombre_usuario, rol = resultado
                messagebox.showinfo("Bienvenido", f"Hola {nombre_usuario}, rol: {rol}")
                self.ventana.destroy()

                if rol == "admin":
                    MasterPanel()  # tu panel de administrador
                elif rol == "cajero":
                    CajeroPanel()  # el panel que debes crear
                else:
                    messagebox.showwarning("Rol desconocido", f"Rol no reconocido: {rol}")
            else:
                messagebox.showerror("Error", "Correo o contraseña incorrectos.")

        except Exception as e:
            messagebox.showerror("Error de conexión", str(e))


    def recuperar_contrasena(self):
        correo = self.usuario.get().strip()

        if not correo:
            messagebox.showwarning("Campo vacío", "Por favor ingresa tu correo.")
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("SELECT rol FROM usuarios WHERE correo = %s", (correo,))
            resultado = cursor.fetchone()

            if not resultado:
                messagebox.showerror("Error", "Correo no encontrado.")
                return

            rol = resultado[0]
            if rol != "admin":
                messagebox.showwarning("No autorizado", "Solo los administradores pueden recuperar su contraseña.")
                return

            codigo = str(random.randint(100000, 999999))
            enviado = enviar_codigo(correo, codigo)

            if not enviado:
                messagebox.showerror("Error", "No se pudo enviar el correo. Verifica la configuración.")
                return

            ingresado = simpledialog.askstring("Verificación", f"Se envió un código a {correo}.\nIngresa el código:")

            if ingresado == codigo:
                nueva_contra = simpledialog.askstring("Nueva contraseña", "Ingresa tu nueva contraseña:", show='*')
                if nueva_contra:
                    cursor.execute("UPDATE usuarios SET contraseña = %s WHERE correo = %s", (nueva_contra, correo))
                    conexion.commit()
                    messagebox.showinfo("Éxito", "Contraseña actualizada.")
            else:
                messagebox.showerror("Código incorrecto", "El código ingresado no es válido.")

            conexion.close()

        except Exception as e:
            messagebox.showerror("Error", str(e))
         
                      
    def __init__(self):        
        self.ventana = tk.Tk()                             
        self.ventana.title('Inicio de sesión')
        self.ventana.geometry('800x500')
        self.ventana.config(bg='#fcfcfc')
        self.ventana.resizable(width=0, height=0)    
        utl.centrar_ventana(self.ventana,800,500)
        
        logo =utl.leer_imagen("Img/lavadora.jpg", (200, 200))
        # frame_logo
        frame_logo = tk.Frame(self.ventana, bd=0, width=300, relief=tk.SOLID, padx=10, pady=10,bg='#3a7ff6')
        frame_logo.pack(side="left",expand=tk.YES,fill=tk.BOTH)
        label = tk.Label( frame_logo, image=logo,bg='#3a7ff6' )
        label.place(x=0,y=0,relwidth=1, relheight=1)
        
        #frame_form
        frame_form = tk.Frame(self.ventana, bd=0, relief=tk.SOLID, bg='#fcfcfc')
        frame_form.pack(side="right",expand=tk.YES,fill=tk.BOTH)
        #frame_form
        
        #frame_form_top
        frame_form_top = tk.Frame(frame_form,height = 50, bd=0, relief=tk.SOLID,bg='black')
        frame_form_top.pack(side="top",fill=tk.X)
        title = tk.Label(frame_form_top, text="Inicio de sesion",font=('Times', 30), fg="#666a88",bg='#fcfcfc',pady=50)
        title.pack(expand=tk.YES,fill=tk.BOTH)
        #end frame_form_top

        #frame_form_fill
        frame_form_fill = tk.Frame(frame_form,height = 50,  bd=0, relief=tk.SOLID,bg='#fcfcfc')
        frame_form_fill.pack(side="bottom",expand=tk.YES,fill=tk.BOTH)

        etiqueta_usuario = tk.Label(frame_form_fill, text="Usuario", font=('Times', 14) ,fg="#666a88",bg='#fcfcfc', anchor="w")
        etiqueta_usuario.pack(fill=tk.X, padx=20,pady=5)
        self.usuario = ttk.Entry(frame_form_fill, font=('Times', 14))
        self.usuario.pack(fill=tk.X, padx=20,pady=10)

        etiqueta_password = tk.Label(frame_form_fill, text="Contraseña", font=('Times', 14),fg="#666a88",bg='#fcfcfc' , anchor="w")
        etiqueta_password.pack(fill=tk.X, padx=20,pady=5)
        self.password = ttk.Entry(frame_form_fill, font=('Times', 14))
        self.password.pack(fill=tk.X, padx=20,pady=10)
        self.password.config(show="*")

        inicio = tk.Button(frame_form_fill,text="Iniciar sesion",font=('Times', 15,BOLD),bg='#3a7ff6', bd=0,fg="#fff",command=self.verificar)
        inicio.pack(fill=tk.X, padx=20,pady=20)        
        inicio.bind("<Return>", (lambda event: self.verificar()))
        #end frame_form_fill

        recuperar = tk.Button(
        frame_form_fill,
        text="¿Olvidaste tu contraseña?",
        font=('Times', 11),
        bg='#fcfcfc',
        fg="#3a7ff6",
        bd=0,
        command=self.recuperar_contrasena
        )
        recuperar.pack(pady=(0, 10))


        self.ventana.mainloop()
        
if __name__ == "__main__":
   App()