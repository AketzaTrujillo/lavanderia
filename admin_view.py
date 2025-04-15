import tkinter as tk
from tkinter import messagebox
from gestionar_usuarios import GestionUsuarios
from gestionar_productos import GestionProductos
from gestionar_clientes import GestionClientes

class MasterPanel:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Panel de Administrador - Lavandería")
        self.ventana.geometry("700x500")
        self.ventana.config(bg="#f0f4c3")
        self.ventana.resizable(False, False)

        self.construir_interfaz()

        self.ventana.mainloop()

    def construir_interfaz(self):
        titulo = tk.Label(
            self.ventana,
            text="Bienvenido, Administrador",
            font=("Helvetica", 20, "bold"),
            bg="#f0f4c3",
            fg="#33691e"
        )
        titulo.pack(pady=20)

        # Botones del panel
        botones = [
            ("Gestionar Usuarios", self.gestionar_usuarios),
            ("Gestionar Productos", self.gestionar_productos),
            ("Gestionar Clientes", self.gestionar_clientes),
            ("Ver Pedidos", self.ver_pedidos),
            ("Ver Ventas", self.ver_ventas),
            ("Cerrar Sesión", self.salir)
        ]

        for texto, comando in botones:
            b = tk.Button(
                self.ventana,
                text=texto,
                font=("Helvetica", 14),
                bg="#558b2f",
                fg="white",
                width=30,
                pady=5,
                command=comando
            )
            b.pack(pady=8)

    # Funciones actualizadas
    def gestionar_usuarios(self):
        GestionUsuarios(self.ventana)  # Pasar la ventana actual como padre

    def gestionar_productos(self):
        GestionProductos(self.ventana)  # Pasar la ventana actual como padre

    def gestionar_clientes(self):
        GestionClientes(self.ventana)  # Pasar la ventana actual como padre

    def ver_pedidos(self):
        messagebox.showinfo("Pedidos", "Aquí irá la vista de pedidos.")

    def ver_ventas(self):
        messagebox.showinfo("Ventas", "Aquí irá la vista de ventas.")

    def salir(self):
        self.ventana.destroy()