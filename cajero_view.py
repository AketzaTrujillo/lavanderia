import tkinter as tk
from tkinter import messagebox

class CajeroPanel:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Panel de Cajero - Lavandería")
        self.ventana.geometry("600x400")
        self.ventana.config(bg="#e0f7fa")
        self.ventana.resizable(False, False)

        self.construir_interfaz()

        self.ventana.mainloop()

    def construir_interfaz(self):
        etiqueta_bienvenida = tk.Label(
            self.ventana,
            text="Bienvenido, Cajero",
            font=("Helvetica", 18, "bold"),
            bg="#e0f7fa",
            fg="#00796b"
        )
        etiqueta_bienvenida.pack(pady=20)

        boton_registrar_venta = tk.Button(
            self.ventana,
            text="Registrar Pedido",
            font=("Helvetica", 14),
            bg="#00796b",
            fg="white",
            width=20,
            command=self.registrar_pedido
        )
        boton_registrar_venta.pack(pady=10)

        boton_salir = tk.Button(
            self.ventana,
            text="Cerrar sesión",
            font=("Helvetica", 14),
            bg="#c62828",
            fg="white",
            width=20,
            command=self.salir
        )
        boton_salir.pack(pady=10)

    def registrar_pedido(self):
        messagebox.showinfo("Función", "Aquí irá la lógica para registrar pedidos.")

    def salir(self):
        self.ventana.destroy()
