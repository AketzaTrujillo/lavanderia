import tkinter as tk
from tkinter import ttk, messagebox
import os, sys
import utileria as utl
from conexion import conectar_bd

class PuntosLealtadVentana:
    def __init__(self, ventana_padre=None, id_usuario=None):
        self.ventana = tk.Toplevel(ventana_padre) if ventana_padre else tk.Tk()
        self.ventana.title("Gestión de Puntos de Lealtad")
        self.ventana.geometry("800x550")
        self.ventana.config(bg="#f5f7fa")
        self.ventana.resizable(False, False)
        if ventana_padre:
            utl.centrar_ventana(self.ventana, 800, 550)
            self.ventana.transient(ventana_padre)
            self.ventana.grab_set()

        # Título
        tk.Label(self.ventana, text="PUNTOS DE LEALTAD", font=("Helvetica", 18, "bold"),
                 bg="#f5f7fa", fg="#1976D2").pack(pady=(18, 5))

        # Frame equivalencia
        frame_eq = tk.Frame(self.ventana, bg="#f5f7fa")
        frame_eq.pack(pady=5)
        tk.Label(frame_eq, text="Equivalencia: 1 punto = $", font=("Helvetica", 12), bg="#f5f7fa").pack(side=tk.LEFT)
        self.equiv_var = tk.StringVar()
        self.cargar_equivalencia()
        entry_eq = tk.Entry(frame_eq, textvariable=self.equiv_var, width=8, font=("Helvetica", 12))
        entry_eq.pack(side=tk.LEFT, padx=5)
        btn_eq = tk.Button(frame_eq, text="Guardar", font=("Helvetica", 10, "bold"),
                           bg="#059669", fg="white", relief="flat", cursor="hand2",
                           command=self.guardar_equivalencia)
        btn_eq.pack(side=tk.LEFT, padx=5)

        # Frame búsqueda
        frame_busq = tk.Frame(self.ventana, bg="#f5f7fa")
        frame_busq.pack(pady=10)
        tk.Label(frame_busq, text="Buscar cliente:", font=("Helvetica", 11), bg="#f5f7fa").pack(side=tk.LEFT, padx=5)
        self.entry_buscar = tk.Entry(frame_busq, width=30, font=("Helvetica", 11))
        self.entry_buscar.pack(side=tk.LEFT, padx=5)
        btn_buscar = tk.Button(frame_busq, text="Buscar", font=("Helvetica", 10),
                               bg="#1976D2", fg="white", command=self.buscar_clientes)
        btn_buscar.pack(side=tk.LEFT, padx=5)
        self.entry_buscar.bind("<Return>", lambda e: self.buscar_clientes())

        # Tabla de clientes
        frame_tabla = tk.Frame(self.ventana, bg="#f5f7fa")
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        columnas = ('id', 'nombre', 'telefono', 'correo', 'puntos')
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=15)
        for col, ancho in zip(columnas, [50, 200, 100, 180, 80]):
            self.tabla.heading(col, text=col.capitalize())
            self.tabla.column(col, width=ancho, anchor=tk.CENTER if col in ('id', 'telefono', 'puntos') else tk.W)
        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Botón para ajustar puntos
        frame_accion = tk.Frame(self.ventana, bg="#f5f7fa")
        frame_accion.pack(pady=10)
        btn_ajustar = tk.Button(frame_accion, text="Ajustar puntos del cliente seleccionado",
                                font=("Helvetica", 11, "bold"), bg="#f59e42", fg="white",
                                command=self.abrir_ajuste_puntos)
        btn_ajustar.pack()

        # Botón cerrar
        btn_cerrar = tk.Button(self.ventana, text="Cerrar", font=("Helvetica", 11),
                               bg="#e53935", fg="white", width=12, cursor="hand2",
                               command=self.ventana.destroy)
        btn_cerrar.pack(pady=10)

        self.cargar_clientes()

        if not ventana_padre:
            self.ventana.mainloop()

    def cargar_equivalencia(self):
        """Carga la equivalencia actual de puntos desde la base de datos o archivo."""
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("SELECT valor_punto_en_dinero FROM configuracion LIMIT 1")
            row = cursor.fetchone()
            if row:
                self.equiv_var.set(str(row[0]))
            else:
                self.equiv_var.set("10")
            conexion.close()
        except Exception:
            self.equiv_var.set("10")

    def guardar_equivalencia(self):
        """Guarda la equivalencia de puntos en la base de datos."""
        try:
            valor = float(self.equiv_var.get())
            if valor <= 0:
                raise ValueError
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("UPDATE configuracion SET valor_punto_en_dinero = %s", (valor,))
            conexion.commit()
            conexion.close()
            messagebox.showinfo("Éxito", "Equivalencia de puntos actualizada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Ingresa un valor numérico válido y mayor a 0.\n{e}")

    def cargar_clientes(self):
        """Carga todos los clientes en la tabla"""
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("SELECT id_cliente, nombre, telefono, correo, puntos FROM clientes ORDER BY nombre")
            for cliente in cursor.fetchall():
                self.tabla.insert('', tk.END, values=cliente)
            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los clientes: {str(e)}")

    def buscar_clientes(self):
        """Busca clientes según el texto ingresado"""
        texto = self.entry_buscar.get().strip()
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        if not texto:
            self.cargar_clientes()
            return
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            consulta = """
            SELECT id_cliente, nombre, telefono, correo, puntos
            FROM clientes
            WHERE nombre LIKE %s OR telefono LIKE %s OR correo LIKE %s
            ORDER BY nombre
            """
            cursor.execute(consulta, (f"%{texto}%", f"%{texto}%", f"%{texto}%"))
            for cliente in cursor.fetchall():
                self.tabla.insert('', tk.END, values=cliente)
            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar clientes: {str(e)}")

    def abrir_ajuste_puntos(self):
        """Abre ventana para ajustar puntos del cliente seleccionado"""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Selecciona un cliente", "Selecciona un cliente para ajustar sus puntos.")
            return
        valores = self.tabla.item(seleccion[0], 'values')
        id_cliente, nombre, telefono, correo, puntos = valores

        ventana_ajuste = tk.Toplevel(self.ventana)
        ventana_ajuste.title(f"Ajustar puntos - {nombre}")
        ventana_ajuste.geometry("350x250")
        ventana_ajuste.config(bg="#f5f7fa")
        ventana_ajuste.grab_set()
        utl.centrar_ventana(ventana_ajuste, 350, 250)

        tk.Label(ventana_ajuste, text=f"Cliente: {nombre}", font=("Helvetica", 12, "bold"),
                 bg="#f5f7fa").pack(pady=(18, 5))
        tk.Label(ventana_ajuste, text=f"Puntos actuales: {puntos}", font=("Helvetica", 12),
                 bg="#f5f7fa").pack(pady=5)

        frame_op = tk.Frame(ventana_ajuste, bg="#f5f7fa")
        frame_op.pack(pady=10)
        operacion = tk.StringVar(value="sumar")
        tk.Radiobutton(frame_op, text="Sumar", variable=operacion, value="sumar",
                       bg="#f5f7fa", font=("Helvetica", 11)).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(frame_op, text="Restar", variable=operacion, value="restar",
                       bg="#f5f7fa", font=("Helvetica", 11)).pack(side=tk.LEFT, padx=10)

        frame_cant = tk.Frame(ventana_ajuste, bg="#f5f7fa")
        frame_cant.pack(pady=5)
        tk.Label(frame_cant, text="Cantidad:", font=("Helvetica", 12), bg="#f5f7fa").pack(side=tk.LEFT, padx=5)
        entry_cant = tk.Entry(frame_cant, font=("Helvetica", 12), width=10)
        entry_cant.pack(side=tk.LEFT, padx=5)

        frame_motivo = tk.Frame(ventana_ajuste, bg="#f5f7fa")
        frame_motivo.pack(pady=5)
        tk.Label(frame_motivo, text="Motivo:", font=("Helvetica", 12), bg="#f5f7fa").pack(side=tk.LEFT, padx=5)
        entry_motivo = tk.Entry(frame_motivo, font=("Helvetica", 12), width=18)
        entry_motivo.pack(side=tk.LEFT, padx=5)

        def aplicar_ajuste():
            try:
                cantidad = int(entry_cant.get().strip())
                if cantidad <= 0:
                    messagebox.showwarning("Valor inválido", "La cantidad debe ser positiva.")
                    return
                motivo = entry_motivo.get().strip()
                if not motivo:
                    messagebox.showwarning("Campo requerido", "Ingresa un motivo para el ajuste.")
                    return
                puntos_actuales = int(puntos)
                if operacion.get() == "sumar":
                    nuevos_puntos = puntos_actuales + cantidad
                else:
                    nuevos_puntos = puntos_actuales - cantidad
                    if nuevos_puntos < 0:
                        messagebox.showwarning("Puntos insuficientes", "No puedes dejar puntos negativos.")
                        return
                conexion = conectar_bd()
                cursor = conexion.cursor()
                cursor.execute("UPDATE clientes SET puntos = %s WHERE id_cliente = %s", (nuevos_puntos, id_cliente))
                # (Opcional: guardar el ajuste en una tabla de historial de puntos)
                conexion.commit()
                conexion.close()
                messagebox.showinfo("Éxito", f"Puntos actualizados. Nuevo saldo: {nuevos_puntos}")
                ventana_ajuste.destroy()
                self.cargar_clientes()
            except ValueError:
                messagebox.showwarning("Valor inválido", "Ingresa un número entero.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo ajustar los puntos: {str(e)}")

        btn_aplicar = tk.Button(ventana_ajuste, text="✓ Aplicar", font=("Helvetica", 11),
                               bg="#059669", fg="white", width=10, cursor="hand2",
                               command=aplicar_ajuste)
        btn_aplicar.pack(pady=10)

        btn_cancelar = tk.Button(ventana_ajuste, text="Cancelar", font=("Helvetica", 11),
                                 bg="#e53935", fg="white", width=10, cursor="hand2",
                                 command=ventana_ajuste.destroy)
        btn_cancelar.pack()

# Para probar de forma independiente
#if __name__ == "__main__":
#    PuntosLealtadVentana()