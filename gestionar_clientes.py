"""
Módulo de Gestión de Clientes para el Sistema de Lavandería
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import utileria as utl
from datetime import datetime

# Asegurar que podamos importar módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Importar módulos del sistema
from conexion import conectar_bd


class GestionClientes:
    """Clase para gestionar los clientes del sistema"""

    def __init__(self, ventana_padre=None):
        # Si hay una ventana padre, crear Toplevel en lugar de Tk
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Gestión de Clientes - Lavandería")
        self.ventana.geometry("900x600")
        self.ventana.config(bg="#f5f5f5")
        self.ventana.resizable(False, False)

        if ventana_padre:
            # Centrar la ventana si existe una ventana padre
            utl.centrar_ventana(self.ventana, 900, 600)
            # Hacer esta ventana modal
            self.ventana.transient(ventana_padre)
            self.ventana.grab_set()

        # Establecer ícono si existe
        try:
            if os.path.exists("Img/lavadora.ico"):
                self.ventana.iconbitmap("Img/lavadora.ico")
        except Exception:
            pass  # Si no se puede cargar el ícono, continuar sin él

        self.construir_interfaz()

        if not ventana_padre:
            self.ventana.mainloop()

    def construir_interfaz(self):
        """Construye la interfaz gráfica del módulo"""
        # Frame principal con padding
        self.frame_principal = tk.Frame(self.ventana, bg="#f5f5f5", padx=20, pady=20)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)

        # Título con estilo
        titulo_frame = tk.Frame(self.frame_principal, bg="#f5f5f5")
        titulo_frame.pack(fill=tk.X, pady=(0, 20))

        titulo = tk.Label(
            titulo_frame,
            text="GESTIÓN DE CLIENTES",
            font=("Helvetica", 18, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        )
        titulo.pack()

        # Separador
        separador = ttk.Separator(self.frame_principal, orient="horizontal")
        separador.pack(fill=tk.X, pady=(0, 20))

        # Frame para botones de acción
        frame_botones = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_botones.pack(pady=10)

        # Botones de acción con íconos
        botones = [
            ("Nuevo Cliente", self.nuevo_cliente, "➕"),
            ("Editar Cliente", self.editar_cliente, "✏️"),
            ("Ver Historial", self.ver_historial, "📋"),
            ("Gestionar Puntos", self.gestionar_puntos, "🎁"),
            ("Pago de Crédito", self.abrir_ventana_pago_credito, "🎁")
            ("Eliminar Cliente", self.eliminar_cliente, "🗑️")
        ]

        for texto, comando, icono in botones:
            b = tk.Button(
                frame_botones,
                text=f"{icono} {texto}",
                font=("Helvetica", 11),
                bg="#3a7ff6",
                fg="white",
                width=16,
                height=2,
                cursor="hand2",
                command=comando
            )
            b.pack(side=tk.LEFT, padx=5)

            # Efecto hover
            b.bind("<Enter>", lambda e, b=b: b.config(bg="#1a5fce"))
            b.bind("<Leave>", lambda e, b=b: b.config(bg="#3a7ff6"))

        # Frame para el buscador
        frame_busqueda = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_busqueda.pack(fill=tk.X, pady=15)

        tk.Label(
            frame_busqueda,
            text="Buscar cliente:",
            font=("Helvetica", 12),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        self.entry_buscar = tk.Entry(frame_busqueda, width=30, font=("Helvetica", 12))
        self.entry_buscar.pack(side=tk.LEFT, padx=5)

        # Vincular tecla Enter al buscador
        self.entry_buscar.bind("<Return>", lambda event: self.buscar_clientes())

        btn_buscar = tk.Button(
            frame_busqueda,
            text="🔍 Buscar",
            font=("Helvetica", 10),
            bg="#3a7ff6",
            fg="white",
            padx=10,
            cursor="hand2",
            command=self.buscar_clientes
        )
        btn_buscar.pack(side=tk.LEFT, padx=5)

        # Efecto hover
        btn_buscar.bind("<Enter>", lambda e: btn_buscar.config(bg="#1a5fce"))
        btn_buscar.bind("<Leave>", lambda e: btn_buscar.config(bg="#3a7ff6"))

        # Frame para la tabla de clientes
        frame_tabla = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10)

        # Tabla de clientes (TreeView)
        columnas = ('id', 'nombre', 'telefono', 'correo', 'puntos', 'fecha_registro')

        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=15)

        # Aplicar estilo a la tabla
        utl.aplicar_estilo_tabla(self.tabla)

        # Configurar encabezados de columnas
        self.tabla.heading('id', text='ID')
        self.tabla.heading('nombre', text='Nombre')
        self.tabla.heading('telefono', text='Teléfono')
        self.tabla.heading('correo', text='Correo')
        self.tabla.heading('puntos', text='Puntos')
        self.tabla.heading('fecha_registro', text='Fecha Registro')

        # Configurar anchos de columnas
        self.tabla.column('id', width=50, anchor=tk.CENTER)
        self.tabla.column('nombre', width=200)
        self.tabla.column('telefono', width=100, anchor=tk.CENTER)
        self.tabla.column('correo', width=150)
        self.tabla.column('puntos', width=80, anchor=tk.CENTER)
        self.tabla.column('fecha_registro', width=150, anchor=tk.CENTER)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        # Empaquetar tabla y scrollbar
        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Barra de estado y botones inferiores
        frame_estado = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_estado.pack(fill=tk.X, pady=10)

        # Botón para refrescar la tabla
        btn_refrescar = tk.Button(
            frame_estado,
            text="🔄 Refrescar",
            font=("Helvetica", 10),
            bg="#3a7ff6",
            fg="white",
            padx=10,
            cursor="hand2",
            command=self.cargar_clientes
        )
        btn_refrescar.pack(side=tk.LEFT, padx=5)

        # Efecto hover
        btn_refrescar.bind("<Enter>", lambda e: btn_refrescar.config(bg="#1a5fce"))
        btn_refrescar.bind("<Leave>", lambda e: btn_refrescar.config(bg="#3a7ff6"))

        # Separador flexible para distribuir espacio
        tk.Frame(frame_estado, bg="#f5f5f5").pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Botón para volver
        btn_volver = tk.Button(
            frame_estado,
            text="↩ Volver",
            font=("Helvetica", 10),
            bg="#e53935",
            fg="white",
            padx=10,
            cursor="hand2",
            command=self.ventana.destroy
        )
        btn_volver.pack(side=tk.RIGHT, padx=5)

        # Efecto hover
        btn_volver.bind("<Enter>", lambda e: btn_volver.config(bg="#c62828"))
        btn_volver.bind("<Leave>", lambda e: btn_volver.config(bg="#e53935"))

        # Cargar clientes iniciales
        self.cargar_clientes()

    def cargar_clientes(self):
        """Carga todos los clientes en la tabla"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT id_cliente, nombre, telefono, correo, puntos, fecha_registro FROM clientes ORDER BY nombre")

            for cliente in cursor.fetchall():
                self.tabla.insert('', tk.END, values=cliente)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los clientes: {str(e)}")

    def buscar_clientes(self):
        """Busca clientes según el texto ingresado"""
        texto_busqueda = self.entry_buscar.get().strip()

        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        if not texto_busqueda:
            self.cargar_clientes()
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Búsqueda por nombre, teléfono o correo
            consulta = """
            SELECT id_cliente, nombre, telefono, correo, puntos, fecha_registro 
            FROM clientes 
            WHERE nombre LIKE %s OR telefono LIKE %s OR correo LIKE %s
            ORDER BY nombre
            """

            cursor.execute(consulta, (f"%{texto_busqueda}%", f"%{texto_busqueda}%", f"%{texto_busqueda}%"))

            for cliente in cursor.fetchall():
                self.tabla.insert('', tk.END, values=cliente)

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar clientes: {str(e)}")

    def nuevo_cliente(self):
        """Abre ventana para crear un nuevo cliente"""
        # Crear una nueva ventana para añadir cliente
        ventana_nuevo = tk.Toplevel(self.ventana)
        ventana_nuevo.title("Nuevo Cliente")
        ventana_nuevo.geometry("500x400")
        ventana_nuevo.config(bg="#f5f5f5")
        ventana_nuevo.grab_set()  # Hacer modal

        # Centrar ventana
        utl.centrar_ventana(ventana_nuevo, 500, 400)

        # Establecer ícono si existe
        try:
            if os.path.exists("Img/lavadora.ico"):
                ventana_nuevo.iconbitmap("Img/lavadora.ico")
        except Exception:
            pass

        # Título
        tk.Label(
            ventana_nuevo,
            text="REGISTRO DE NUEVO CLIENTE",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        ).pack(pady=(20, 10))

        # Separador
        ttk.Separator(ventana_nuevo, orient="horizontal").pack(fill=tk.X, padx=20)

        # Frame para el formulario
        frame_form = tk.Frame(ventana_nuevo, bg="#f5f5f5")
        frame_form.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Etiquetas y campos
        tk.Label(frame_form, text="Nombre:", font=("Helvetica", 12), bg="#f5f5f5").grid(row=0, column=0, sticky=tk.W, pady=10)
        entry_nombre = tk.Entry(frame_form, font=("Helvetica", 12), width=30)
        entry_nombre.grid(row=0, column=1, sticky=tk.W + tk.E, pady=10, padx=10)

        tk.Label(frame_form, text="Teléfono:", font=("Helvetica", 12), bg="#f5f5f5").grid(row=1, column=0, sticky=tk.W, pady=10)
        entry_telefono = tk.Entry(frame_form, font=("Helvetica", 12), width=30)
        entry_telefono.grid(row=1, column=1, sticky=tk.W + tk.E, pady=10, padx=10)

        tk.Label(frame_form, text="Correo:", font=("Helvetica", 12), bg="#f5f5f5").grid(row=2, column=0, sticky=tk.W, pady=10)
        entry_correo = tk.Entry(frame_form, font=("Helvetica", 12), width=30)
        entry_correo.grid(row=2, column=1, sticky=tk.W + tk.E, pady=10, padx=10)

        # Botones
        frame_botones = tk.Frame(ventana_nuevo, bg="#f5f5f5")
        frame_botones.pack(pady=20)

        def guardar_cliente():
            # Validar campos
            nombre = entry_nombre.get().strip()
            telefono = entry_telefono.get().strip()
            correo = entry_correo.get().strip()

            if not nombre:
                messagebox.showwarning("Campo incompleto", "El nombre del cliente es obligatorio")
                return

            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()

                # Insertar nuevo cliente con 0 puntos iniciales
                consulta = "INSERT INTO clientes (nombre, telefono, correo, puntos) VALUES (%s, %s, %s, 0)"
                cursor.execute(consulta, (nombre, telefono, correo))

                conexion.commit()
                conexion.close()

                messagebox.showinfo("Éxito", "Cliente registrado correctamente")
                ventana_nuevo.destroy()
                self.cargar_clientes()  # Refrescar tabla
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo registrar el cliente: {str(e)}")

        btn_guardar = tk.Button(
            frame_botones,
            text="💾 Guardar",
            font=("Helvetica", 11),
            bg="#3a7ff6",
            fg="white",
            width=10,
            cursor="hand2",
            command=guardar_cliente
        )
        btn_guardar.pack(side=tk.LEFT, padx=5)

        # Efecto hover
        btn_guardar.bind("<Enter>", lambda e: btn_guardar.config(bg="#1a5fce"))
        btn_guardar.bind("<Leave>", lambda e: btn_guardar.config(bg="#3a7ff6"))

        btn_cancelar = tk.Button(
            frame_botones,
            text="❌ Cancelar",
            font=("Helvetica", 11),
            bg="#e53935",
            fg="white",
            width=10,
            cursor="hand2",
            command=ventana_nuevo.destroy
        )
        btn_cancelar.pack(side=tk.LEFT, padx=5)

        # Efecto hover
        btn_cancelar.bind("<Enter>", lambda e: btn_cancelar.config(bg="#c62828"))
        btn_cancelar.bind("<Leave>", lambda e: btn_cancelar.config(bg="#e53935"))

    def editar_cliente(self):
        """Abre ventana para editar un cliente seleccionado"""
        # Obtener el cliente seleccionado
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un cliente para editar")
            return

        # Obtener datos del cliente seleccionado
        valores = self.tabla.item(seleccion[0], 'values')
        id_cliente = valores[0]
        nombre_actual = valores[1]
        telefono_actual = valores[2]
        correo_actual = valores[3]

        # Crear ventana de edición
        ventana_editar = tk.Toplevel(self.ventana)
        ventana_editar.title("Editar Cliente")
        ventana_editar.geometry("400x300")
        ventana_editar.config(bg="#f5f5f5")
        ventana_editar.grab_set()  # Hacer modal

        # Frame para el formulario
        frame_form = tk.Frame(ventana_editar, bg="#f5f5f5")
        frame_form.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Etiquetas y campos
        lbl_nombre = tk.Label(frame_form, text="Nombre:", font=("Helvetica", 12), bg="#f5f5f5")
        lbl_nombre.grid(row=0, column=0, sticky=tk.W, pady=5)

        entry_nombre = tk.Entry(frame_form, font=("Helvetica", 12))
        entry_nombre.grid(row=0, column=1, sticky=tk.W + tk.E, pady=5, padx=5)
        entry_nombre.insert(0, nombre_actual)

        lbl_telefono = tk.Label(frame_form, text="Teléfono:", font=("Helvetica", 12), bg="#f5f5f5")
        lbl_telefono.grid(row=1, column=0, sticky=tk.W, pady=5)

        entry_telefono = tk.Entry(frame_form, font=("Helvetica", 12))
        entry_telefono.grid(row=1, column=1, sticky=tk.W + tk.E, pady=5, padx=5)
        entry_telefono.insert(0, telefono_actual if telefono_actual else "")

        lbl_correo = tk.Label(frame_form, text="Correo:", font=("Helvetica", 12), bg="#f5f5f5")
        lbl_correo.grid(row=2, column=0, sticky=tk.W, pady=5)

        entry_correo = tk.Entry(frame_form, font=("Helvetica", 12))
        entry_correo.grid(row=2, column=1, sticky=tk.W + tk.E, pady=5, padx=5)
        entry_correo.insert(0, correo_actual if correo_actual else "")

        # Botones
        frame_botones = tk.Frame(ventana_editar, bg="#f5f5f5")
        frame_botones.pack(pady=10)

        def actualizar_cliente():
            # Validar campos
            nuevo_nombre = entry_nombre.get().strip()
            nuevo_telefono = entry_telefono.get().strip()
            nuevo_correo = entry_correo.get().strip()

            if not nuevo_nombre:
                messagebox.showwarning("Campo incompleto", "El nombre del cliente es obligatorio")
                return

            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()

                # Actualizar cliente
                consulta = """
                UPDATE clientes SET nombre = %s, telefono = %s, correo = %s
                WHERE id_cliente = %s
                """
                cursor.execute(consulta, (nuevo_nombre, nuevo_telefono, nuevo_correo, id_cliente))

                conexion.commit()
                conexion.close()

                messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
                ventana_editar.destroy()
                self.cargar_clientes()  # Refrescar tabla
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el cliente: {str(e)}")

        btn_actualizar = tk.Button(
            frame_botones,
            text="Actualizar",
            font=("Helvetica", 12),
            bg="#3a7ff6",
            fg="white",
            command=actualizar_cliente
        )
        btn_actualizar.pack(side=tk.LEFT, padx=5)

        btn_cancelar = tk.Button(
            frame_botones,
            text="Cancelar",
            font=("Helvetica", 12),
            bg="#e53935",
            fg="white",
            command=ventana_editar.destroy
        )
        btn_cancelar.pack(side=tk.LEFT, padx=5)

    def ver_historial(self):
        """Abre la ventana de historial del cliente seleccionado"""
        # Obtener el cliente seleccionado
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un cliente para ver su historial")
            return

        # Obtener datos del cliente seleccionado
        valores = self.tabla.item(seleccion[0], 'values')
        id_cliente = valores[0]

        # Importar el módulo de historial de cliente aquí para evitar importaciones circulares
        try:
            # Intentar importar el módulo de historial
            from historial_cliente import HistorialCliente
            # Abrir ventana de historial
            HistorialCliente(id_cliente, self.ventana)
        except ImportError:
            messagebox.showerror("Error", "No se pudo importar el módulo de historial de clientes")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el historial: {str(e)}")

    def gestionar_puntos(self):
        """Abre ventana para gestionar los puntos de un cliente"""
        # Obtener el cliente seleccionado
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un cliente para gestionar sus puntos")
            return

        # Obtener datos del cliente seleccionado
        valores = self.tabla.item(seleccion[0], 'values')
        id_cliente = valores[0]
        nombre_cliente = valores[1]
        puntos_actuales = int(valores[4])

        # Crear ventana para gestionar puntos
        ventana_puntos = tk.Toplevel(self.ventana)
        ventana_puntos.title(f"Gestionar Puntos - {nombre_cliente}")
        ventana_puntos.geometry("400x340")
        ventana_puntos.config(bg="#f5f5f5")
        ventana_puntos.grab_set()  # Hacer modal

        # Centrar ventana
        utl.centrar_ventana(ventana_puntos, 400, 340)

        # Establecer ícono si existe
        try:
            if os.path.exists("Img/lavadora.ico"):
                ventana_puntos.iconbitmap("Img/lavadora.ico")
        except Exception:
            pass

        # Título
        tk.Label(
            ventana_puntos,
            text="GESTIÓN DE PUNTOS",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        ).pack(pady=(20, 10))

        # Separador
        ttk.Separator(ventana_puntos, orient="horizontal").pack(fill=tk.X, padx=20)

        # Frame para el contenido
        frame_contenido = tk.Frame(ventana_puntos, bg="#f5f5f5")
        frame_contenido.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Información del cliente
        tk.Label(
            frame_contenido,
            text=f"Cliente: {nombre_cliente}",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5"
        ).pack(anchor=tk.W, pady=5)

        tk.Label(
            frame_contenido,
            text=f"Puntos actuales: {puntos_actuales}",
            font=("Helvetica", 12),
            bg="#f5f5f5"
        ).pack(anchor=tk.W, pady=5)

        # Separador
        ttk.Separator(frame_contenido, orient='horizontal').pack(fill=tk.X, pady=10)

        # Frame para ajustar puntos
        frame_ajuste = tk.Frame(frame_contenido, bg="#f5f5f5")
        frame_ajuste.pack(fill=tk.X, pady=10)

        # Opciones para sumar o restar puntos
        operacion = tk.StringVar(value="sumar")

        tk.Radiobutton(
            frame_ajuste,
            text="Sumar puntos",
            variable=operacion,
            value="sumar",
            bg="#f5f5f5",
            font=("Helvetica", 11)
        ).pack(anchor=tk.W)

        tk.Radiobutton(
            frame_ajuste,
            text="Restar puntos",
            variable=operacion,
            value="restar",
            bg="#f5f5f5",
            font=("Helvetica", 11)
        ).pack(anchor=tk.W)

        # Frame para la cantidad
        frame_cantidad = tk.Frame(frame_contenido, bg="#f5f5f5")
        frame_cantidad.pack(fill=tk.X, pady=10)

        tk.Label(
            frame_cantidad,
            text="Cantidad:",
            font=("Helvetica", 12),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        entry_cantidad = tk.Entry(frame_cantidad, font=("Helvetica", 12), width=10)
        entry_cantidad.pack(side=tk.LEFT, padx=5)

        # Motivo del ajuste
        frame_motivo = tk.Frame(frame_contenido, bg="#f5f5f5")
        frame_motivo.pack(fill=tk.X, pady=10)

        tk.Label(
            frame_motivo,
            text="Motivo:",
            font=("Helvetica", 12),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        entry_motivo = tk.Entry(frame_motivo, font=("Helvetica", 12), width=25)
        entry_motivo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Botones
        frame_botones = tk.Frame(ventana_puntos, bg="#f5f5f5")
        frame_botones.pack(pady=20)

        def aplicar_ajuste_puntos():
            try:
                cantidad = int(entry_cantidad.get().strip())
                if cantidad <= 0:
                    messagebox.showwarning("Valor inválido", "La cantidad debe ser un número positivo")
                    return

                motivo = entry_motivo.get().strip()
                if not motivo:
                    messagebox.showwarning("Campo requerido", "Por favor ingresa un motivo para el ajuste")
                    return

                # Calcular nuevos puntos
                if operacion.get() == "sumar":
                    nuevos_puntos = puntos_actuales + cantidad
                    mensaje_cambio = f"Se agregaron {cantidad} puntos."
                else:  # restar
                    nuevos_puntos = puntos_actuales - cantidad
                    if nuevos_puntos < 0:
                        messagebox.showwarning(
                            "Puntos insuficientes",
                            f"El cliente solo tiene {puntos_actuales} puntos disponibles"
                        )
                        return
                    mensaje_cambio = f"Se descontaron {cantidad} puntos."

                conexion = conectar_bd()
                cursor = conexion.cursor()

                # Actualizar puntos del cliente
                cursor.execute(
                    "UPDATE clientes SET puntos = %s WHERE id_cliente = %s",
                    (nuevos_puntos, id_cliente)
                )

                conexion.commit()
                conexion.close()

                messagebox.showinfo("Éxito", f"{mensaje_cambio} Nuevos puntos: {nuevos_puntos}")
                ventana_puntos.destroy()
                self.cargar_clientes()  # Refrescar tabla

            except ValueError:
                messagebox.showwarning("Valor inválido", "Por favor ingresa un número entero")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo ajustar los puntos: {str(e)}")

        btn_aplicar = tk.Button(
            frame_botones,
            text="✓ Aplicar",
            font=("Helvetica", 11),
            bg="#3a7ff6",
            fg="white",
            width=10,
            cursor="hand2",
            command=aplicar_ajuste_puntos
        )
        btn_aplicar.pack(side=tk.LEFT, padx=5)

        # Efecto hover
        btn_aplicar.bind("<Enter>", lambda e: btn_aplicar.config(bg="#1a5fce"))
        btn_aplicar.bind("<Leave>", lambda e: btn_aplicar.config(bg="#3a7ff6"))

        btn_cancelar = tk.Button(
            frame_botones,
            text="❌ Cancelar",
            font=("Helvetica", 11),
            bg="#e53935",
            fg="white",
            width=10,
            cursor="hand2",
            command=ventana_puntos.destroy
        )
        btn_cancelar.pack(side=tk.LEFT, padx=5)

        # Efecto hover
        btn_cancelar.bind("<Enter>", lambda e: btn_cancelar.config(bg="#c62828"))
        btn_cancelar.bind("<Leave>", lambda e: btn_cancelar.config(bg="#e53935"))

    def abrir_ventana_pago_credito(self):
        ventana_pago = tk.Toplevel(self.ventana)
        ventana_pago.title("Registrar Pago de Crédito")
        ventana_pago.geometry("400x300")
        ventana_pago.config(bg="#f9f9f9")
        ventana_pago.transient(self.ventana)
        ventana_pago.grab_set()

        tk.Label(ventana_pago, text="Selecciona un cliente:", font=("Helvetica", 12), bg="#f9f9f9").pack(pady=10)

        combo_clientes = ttk.Combobox(ventana_pago, state="readonly", width=35)
        combo_clientes.pack(pady=5)

        # Cargar clientes con crédito
        import conexion
        con = conexion.get_connection()
        cursor = con.cursor()
        cursor.execute("SELECT id, nombre, saldo_credito, deuda_credito, credito_original FROM clientes WHERE deuda_credito > 0")
        clientes_credito = cursor.fetchall()
        con.close()

        clientes_dict = {}
        for c in clientes_credito:
            display = f"{c[1]} (Deuda: ${c[3]:.2f})"
            combo_clientes["values"] = (*combo_clientes["values"], display)
            clientes_dict[display] = {
                'id': c[0], 'nombre': c[1],
                'saldo': c[2], 'deuda': c[3], 'credito_original': c[4]
            }

        lbl_monto = tk.Label(ventana_pago, text="Monto a pagar:", font=("Helvetica", 11), bg="#f9f9f9")
        lbl_monto.pack(pady=(20, 5))
        entry_monto = tk.Entry(ventana_pago, font=("Helvetica", 11))
        entry_monto.pack()

        def registrar_pago():
            seleccionado = combo_clientes.get()
            datos = clientes_dict.get(seleccionado)
            if not datos:
                messagebox.showwarning("Advertencia", "Debes seleccionar un cliente.")
                return

            try:
                pago = float(entry_monto.get())
            except ValueError:
                messagebox.showerror("Error", "Ingresa un número válido.")
                return

            if pago <= 0:
                messagebox.showerror("Error", "El monto debe ser mayor a cero.")
                return
            if pago > datos['deuda']:
                messagebox.showwarning("Advertencia", "El monto excede la deuda actual.")
                return

            nueva_deuda = datos['deuda'] - pago
            nuevo_saldo = datos['saldo'] + pago if nueva_deuda == 0 else datos['saldo']

            try:
                con = conexion.get_connection()
                cursor = con.cursor()
                cursor.execute(
                    "UPDATE clientes SET saldo_credito = %s, deuda_credito = %s WHERE id = %s",
                    (nuevo_saldo if nueva_deuda == 0 else datos['saldo'], nueva_deuda, datos['id'])
                )
                con.commit()
                con.close()
                messagebox.showinfo("Éxito", "Pago registrado correctamente.")
                ventana_pago.destroy()
                self.cargar_datos()  # Recargar tabla si tienes esa función
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar la deuda: {str(e)}")

        tk.Button(
            ventana_pago, text="Registrar Pago", bg="#388E3C", fg="white",
            font=("Helvetica", 11), command=registrar_pago
        ).pack(pady=20)
    
    def eliminar_cliente(self):
        """Elimina un cliente seleccionado"""
        # Obtener el cliente seleccionado
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un cliente para eliminar")
            return

        # Obtener datos del cliente seleccionado
        valores = self.tabla.item(seleccion[0], 'values')
        id_cliente = valores[0]
        nombre_cliente = valores[1]

        # Confirmar eliminación
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de eliminar al cliente '{nombre_cliente}'?\n\nEsta acción no se puede deshacer."
        )

        if not confirmacion:
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Verificar si el cliente tiene pedidos o ventas asociadas
            cursor.execute("""
                SELECT COUNT(*) FROM pedidos WHERE id_cliente = %s
                UNION ALL
                SELECT COUNT(*) FROM ventas WHERE id_cliente = %s
            """, (id_cliente, id_cliente))

            resultados = cursor.fetchall()

            if resultados[0][0] > 0 or (len(resultados) > 1 and resultados[1][0] > 0):
                messagebox.showwarning(
                    "No se puede eliminar",
                    "Este cliente tiene pedidos o ventas asociadas y no puede eliminarse."
                )
                conexion.close()
                return

            # Eliminar cliente
            cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))

            conexion.commit()
            conexion.close()

            messagebox.showinfo("Éxito", f"Cliente '{nombre_cliente}' eliminado correctamente")
            self.cargar_clientes()  # Refrescar tabla
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el cliente: {str(e)}")

# Para probar de forma independiente
if __name__ == "__main__":
    GestionClientes()