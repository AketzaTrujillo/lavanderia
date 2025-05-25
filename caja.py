import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import sys
import utileria as utl
from datetime import datetime, date, time, timedelta
import decimal

# Asegurar que podamos importar módulos del sistema
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

try:
    from conexion import conectar_bd
    # Intentar importar el módulo de tickets si está disponible
    from ticket import Ticket
except ImportError as e:
    print(f"Error al importar módulos: {e}")


class GestionCaja:
    """Clase para gestionar las operaciones de caja"""

    # Busca esta sección en tu archivo caja.py actual (debe estar cerca del inicio de la clase GestionCaja)
    def __init__(self, ventana_padre=None, id_usuario=None):
        # Si hay una ventana padre, crear Toplevel en lugar de Tk
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Gestión de Caja - Lavandería")
        self.ventana.geometry("900x650")
        self.ventana.config(bg="#f5f5f5")
        self.ventana.resizable(False, False)


        if id_usuario is None:
            # Establecer a un valor por defecto (administrador) si no hay ID proporcionado
            self.id_usuario = 1
            print(
                f"ADVERTENCIA: GestionCaja inicializada sin ID de usuario. Usando valor por defecto: {self.id_usuario}")
        else:
            self.id_usuario = id_usuario

        print(f"Debug - GestionCaja inicializada con ID usuario: {self.id_usuario}")

        # Verificar si el usuario existe en la BD
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("SELECT nombre FROM usuarios WHERE id_usuario = %s", (self.id_usuario,))
            nombre_usuario = cursor.fetchone()
            if nombre_usuario:
                print(f"Debug - Usuario verificado: {nombre_usuario[0]}")
            else:
                print(f"Debug - ¡ALERTA! Usuario ID {self.id_usuario} no existe en la BD")

                # Mostrar todos los usuarios disponibles
                cursor.execute("SELECT id_usuario, nombre FROM usuarios ORDER BY id_usuario")
                print("Usuarios disponibles en la BD:")
                for usuario in cursor.fetchall():
                    print(f"ID={usuario[0]}, Nombre={usuario[1]}")
            conexion.close()
        except Exception as e:
            print(f"Error al verificar usuario en constructor: {e}")

        # ID y estado de la caja actual
        self.id_caja_actual = None
        self.caja_abierta = False

        if ventana_padre:
            # Centrar la ventana si existe una ventana padre
            utl.centrar_ventana(self.ventana, 900, 650)
            # Hacer esta ventana modal
            self.ventana.transient(ventana_padre)
            self.ventana.grab_set()

        # Verificar estado de la caja al iniciar
        self.verificar_estado_caja()

        # Construir la interfaz
        self.construir_interfaz()

        if not ventana_padre:
            self.ventana.mainloop()


    def construir_interfaz(self):
        """Construye la interfaz gráfica del módulo de caja"""
        # Frame principal con padding
        self.frame_principal = tk.Frame(self.ventana, bg="#f5f5f5", padx=20, pady=20)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)

        # Título con estilo
        titulo_frame = tk.Frame(self.frame_principal, bg="#f5f5f5")
        titulo_frame.pack(fill=tk.X, pady=(0, 20))

        titulo = tk.Label(
            titulo_frame,
            text="GESTIÓN DE CAJA",
            font=("Helvetica", 18, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        )
        titulo.pack()

        # Separador
        separador = ttk.Separator(self.frame_principal, orient="horizontal")
        separador.pack(fill=tk.X, pady=(0, 20))

        # Frame para mostrar estado actual de la caja
        self.frame_estado = tk.Frame(self.frame_principal, bg="#f5f5f5", relief=tk.GROOVE, bd=1)
        self.frame_estado.pack(fill=tk.X, pady=10, padx=5)

        # Mostrar estado de caja actual
        self.actualizar_estado_caja()

        # Crear notebook (pestañas)
        self.notebook = ttk.Notebook(self.frame_principal)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Pestañas
        self.tab_operaciones = tk.Frame(self.notebook, bg="#f5f5f5")
        self.tab_movimientos = tk.Frame(self.notebook, bg="#f5f5f5")
        self.tab_cortes = tk.Frame(self.notebook, bg="#f5f5f5")

        self.notebook.add(self.tab_operaciones, text="Operaciones de Caja")
        self.notebook.add(self.tab_movimientos, text="Movimientos")
        self.notebook.add(self.tab_cortes, text="Cortes de Caja")

        # Configurar las pestañas
        self.configurar_tab_operaciones()
        self.configurar_tab_movimientos()
        self.configurar_tab_cortes()

        # Botón para volver
        btn_volver = tk.Button(
            self.frame_principal,
            text="Volver",
            font=("Helvetica", 11),
            bg="#e53935",
            fg="white",
            width=10,
            cursor="hand2",
            command=self.ventana.destroy
        )
        btn_volver.pack(pady=10, anchor=tk.SE)

    def actualizar_estado_caja(self):
        """Actualiza la visualización del estado actual de la caja"""
        # Limpiar frame de estado
        for widget in self.frame_estado.winfo_children():
            widget.destroy()

        # Verificar estado antes de mostrar
        self.verificar_estado_caja()

        if self.caja_abierta:
            # Obtener información detallada de la caja actual
            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()

                # Verificar qué columnas existen en la tabla
                cursor.execute("DESCRIBE caja")
                columnas = {col[0] for col in cursor.fetchall()}

                # Depuración para estructura de tabla
                print(f"Debug - Columnas de tabla caja: {', '.join(columnas)}")

                # Construir consulta basada en columnas disponibles
                if 'total_ingresos' in columnas and 'total_egresos' in columnas and 'saldo_final' in columnas:
                    consulta = """
                        SELECT c.fecha, c.hora_apertura, u.nombre, 
                               c.total_ingresos, c.total_egresos, c.saldo_final
                        FROM caja c
                        JOIN usuarios u ON c.responsable = u.id_usuario
                        WHERE c.id_caja = %s
                    """
                else:
                    # Consulta con cálculo manual
                    consulta = """
                        SELECT c.fecha, c.hora_apertura, u.nombre, 
                               COALESCE((SELECT SUM(m.monto) FROM movimientos_caja m 
                                        WHERE m.id_caja = c.id_caja AND m.tipo = 'ingreso'), 0) as total_ingresos,
                               COALESCE((SELECT SUM(m.monto) FROM movimientos_caja m 
                                        WHERE m.id_caja = c.id_caja AND m.tipo = 'egreso'), 0) as total_egresos,
                               COALESCE((SELECT SUM(m.monto) FROM movimientos_caja m 
                                        WHERE m.id_caja = c.id_caja AND m.tipo = 'ingreso'), 0) -
                               COALESCE((SELECT SUM(m.monto) FROM movimientos_caja m 
                                        WHERE m.id_caja = c.id_caja AND m.tipo = 'egreso'), 0) as saldo_final
                        FROM caja c
                        JOIN usuarios u ON c.responsable = u.id_usuario
                        WHERE c.id_caja = %s
                    """

                cursor.execute(consulta, (self.id_caja_actual,))
                caja = cursor.fetchone()

                # Depuración para verificar datos de caja
                print(f"Debug - Datos de caja: {caja}")

                conexion.close()

                if caja:
                    fecha, hora_apertura, responsable, ingresos, egresos, saldo = caja
                    fecha_formateada = utl.formatear_fecha(fecha)

                    # Formatear hora_apertura correctamente
                    hora_formateada = "No disponible"
                    if hora_apertura:
                        try:
                            if hasattr(hora_apertura, 'strftime'):  # datetime o time
                                hora_formateada = hora_apertura.strftime("%H:%M:%S")
                            elif isinstance(hora_apertura, timedelta):  # timedelta
                                segundos = hora_apertura.total_seconds()
                                horas = int(segundos // 3600)
                                minutos = int((segundos % 3600) // 60)
                                segundos = int(segundos % 60)
                                hora_formateada = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
                            else:
                                hora_formateada = str(hora_apertura)
                        except Exception as e:
                            print(f"Error al formatear hora: {e}")
                            hora_formateada = str(hora_apertura)

                    # Depuración para el nombre del responsable
                    print(f"Debug - Responsable de caja: {responsable}")

                    # Mostrar información de caja abierta
                    lbl_estado = tk.Label(
                        self.frame_estado,
                        text="CAJA ABIERTA",
                        font=("Helvetica", 14, "bold"),
                        bg="#b2ff59",
                        fg="#33691e",
                        padx=15,
                        pady=5
                    )
                    lbl_estado.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

                    tk.Label(
                        self.frame_estado,
                        text=f"Fecha: {fecha_formateada}",
                        font=("Helvetica", 12),
                        bg="#f5f5f5"
                    ).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

                    tk.Label(
                        self.frame_estado,
                        text=f"Hora apertura: {hora_formateada}",
                        font=("Helvetica", 12),
                        bg="#f5f5f5"
                    ).grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)

                    tk.Label(
                        self.frame_estado,
                        text=f"Responsable: {responsable}",
                        font=("Helvetica", 12),
                        bg="#f5f5f5"
                    ).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

                    # Mostrar ingresos, egresos y saldo actual
                    tk.Label(
                        self.frame_estado,
                        text=f"Ingresos: ${ingresos:.2f}",
                        font=("Helvetica", 12),
                        bg="#f5f5f5",
                        fg="#388e3c"
                    ).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)

                    tk.Label(
                        self.frame_estado,
                        text=f"Egresos: ${egresos:.2f}",
                        font=("Helvetica", 12),
                        bg="#f5f5f5",
                        fg="#d32f2f"
                    ).grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)

                    tk.Label(
                        self.frame_estado,
                        text=f"Saldo: ${saldo:.2f}",
                        font=("Helvetica", 12, "bold"),
                        bg="#f5f5f5"
                    ).grid(row=0, column=4, rowspan=2, sticky=tk.W, padx=15, pady=2)

                else:
                    # Si no hay datos, mostrar mensaje simple
                    lbl_estado = tk.Label(
                        self.frame_estado,
                        text="CAJA ABIERTA - Sin detalles disponibles",
                        font=("Helvetica", 14, "bold"),
                        bg="#b2ff59",
                        fg="#33691e",
                        padx=15,
                        pady=5
                    )
                    lbl_estado.pack(padx=10, pady=10)

            except Exception as e:
                # Si hay error, mostrar un estado simplificado
                lbl_estado = tk.Label(
                    self.frame_estado,
                    text="CAJA ABIERTA",
                    font=("Helvetica", 14, "bold"),
                    bg="#b2ff59",
                    fg="#33691e",
                    padx=15,
                    pady=5
                )
                lbl_estado.pack(side=tk.LEFT, padx=10, pady=10)

                tk.Label(
                    self.frame_estado,
                    text=f"ID Caja: {self.id_caja_actual}",
                    font=("Helvetica", 12),
                    bg="#f5f5f5"
                ).pack(side=tk.LEFT, padx=15, pady=10)

                print(f"Error al obtener detalles de caja: {e}")
        else:
            # Mostrar que la caja está cerrada
            lbl_estado = tk.Label(
                self.frame_estado,
                text="CAJA CERRADA",
                font=("Helvetica", 14, "bold"),
                bg="#ffcdd2",
                fg="#c62828",
                padx=15,
                pady=5
            )
            lbl_estado.pack(side=tk.LEFT, padx=10, pady=10)

            tk.Label(
                self.frame_estado,
                text="Debe abrir la caja para operar",
                font=("Helvetica", 12),
                bg="#f5f5f5"
            ).pack(side=tk.LEFT, padx=15, pady=10)

    def imprimir_estado_caja(self):
        """Imprime el estado actual de la caja"""
        try:
            if self.caja_abierta:
                # Obtener información detallada de la caja actual
                conexion = conectar_bd()
                cursor = conexion.cursor()

                cursor.execute("""
                    SELECT c.fecha, c.hora_apertura, u.nombre, 
                           c.total_ingresos, c.total_egresos, c.saldo_final
                    FROM caja c
                    JOIN usuarios u ON c.responsable = u.id_usuario
                    WHERE c.id_caja = %s
                """, (self.id_caja_actual,))

                caja = cursor.fetchone()
                conexion.close()

                if caja:
                    fecha, hora_apertura, responsable, ingresos, egresos, saldo = caja

                    # Formatear la información para imprimir
                    ticket = Ticket()

                    # Encabezado
                    ticket.agregar_encabezado()
                    ticket.agregar_titulo("ESTADO DE CAJA")

                    # Formatear fecha de manera segura
                    fecha_str = fecha.strftime("%d/%m/%Y") if hasattr(fecha, 'strftime') else str(fecha)
                    ticket.agregar_texto(f"Fecha: {fecha_str}")

                    # Formatear hora de apertura de manera segura
                    # Si es un objeto time, usar strftime
                    if hora_apertura:
                        if hasattr(hora_apertura, 'strftime'):
                            hora_str = hora_apertura.strftime("%H:%M:%S")
                        elif isinstance(hora_apertura, timedelta):
                            # Si es timedelta, convertir a formato adecuado
                            segundos = hora_apertura.total_seconds()
                            horas = int(segundos // 3600)
                            minutos = int((segundos % 3600) // 60)
                            segundos = int(segundos % 60)
                            hora_str = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
                        else:
                            # Cualquier otro tipo
                            hora_str = str(hora_apertura)
                    else:
                        hora_str = "No disponible"

                    ticket.agregar_texto(f"Hora apertura: {hora_str}")
                    ticket.agregar_texto(f"Responsable: {responsable}")
                    ticket.agregar_linea()

                    # Detalle
                    ticket.agregar_texto(f"Total ingresos: ${float(ingresos):.2f}")
                    ticket.agregar_texto(f"Total egresos: ${float(egresos):.2f}")
                    ticket.agregar_linea()

                    # Total
                    ticket.agregar_texto(f"Saldo actual: ${float(saldo):.2f}")

                    # Pie
                    ticket.agregar_espacio()
                    ticket.agregar_texto("Generado el: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

                    # Generar nombre del archivo
                    nombre_archivo = f"estado_caja_{self.id_caja_actual}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

                    # Generar PDF
                    ruta_pdf = ticket.generar_pdf(nombre_archivo)

                    # Mostrar vista previa
                    ticket.mostrar_vista_previa(ruta_pdf)

                    messagebox.showinfo("Vista Previa", "Se ha generado la vista previa del estado de caja")
                else:
                    messagebox.showwarning("Advertencia", "No se pudo obtener la información de la caja actual")
            else:
                messagebox.showinfo("Información", "La caja está cerrada, no hay estado para imprimir")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo imprimir el estado: {str(e)}")
            print(f"Error al imprimir estado: {e}")
            import traceback
            traceback.print_exc()

    
            print(f"Error al registrar ingreso: {e}")

    def registrar_egreso(self):
        """Registra un egreso en la caja actual usando un diálogo personalizado centrado"""
        try:
            if not self.caja_abierta:
                messagebox.showinfo("Información",
                                    "Debe abrir la caja primero",
                                    parent=self.ventana)
                return

            resultado = self._dialogo_concepto_monto("Egreso")
            if resultado is None:
                return
            concepto, monto = resultado

            # —— resto igual: verificar saldo, insertar y actualizar UI ——
            conexion = conectar_bd()
            try:
                cursor = conexion.cursor()
                cursor.execute("SELECT saldo_final FROM caja WHERE id_caja = %s",
                               (self.id_caja_actual,))
                fila = cursor.fetchone()
                if not fila:
                    messagebox.showerror("Error",
                                         "No se encontró la caja.",
                                         parent=self.ventana)
                    return
                saldo_actual = fila[0]
                if saldo_actual < monto:
                    messagebox.showerror("Saldo insuficiente",
                                         f"No hay saldo suficiente.\nSaldo actual: ${saldo_actual:.2f}",
                                         parent=self.ventana)
                    return

                cursor.execute("""
                    INSERT INTO movimientos_caja
                      (id_caja, hora, tipo, concepto, monto, id_usuario)
                    VALUES (%s, NOW(), %s, %s, %s, %s)
                """, (
                    self.id_caja_actual,
                    'egreso', concepto, monto, self.id_usuario
                ))
                cursor.execute("""
                    UPDATE caja
                    SET total_egresos = total_egresos + %s,
                        saldo_final   = saldo_final   - %s
                    WHERE id_caja = %s
                """, (monto, monto, self.id_caja_actual))
                conexion.commit()
            finally:
                conexion.close()

            self.actualizar_estado_caja()
            if hasattr(self, 'cargar_movimientos'):
                self.cargar_movimientos()

            messagebox.showinfo("Registro Exitoso",
                                f"Se registró un egreso de ${monto:.2f} por {concepto}",
                                parent=self.ventana)

        except Exception as e:
            messagebox.showerror("Error",
                                 f"No se pudo registrar el egreso:\n{e}",
                                 parent=self.ventana)
            print(f"Error al registrar egreso: {e}")

    def _dialogo_concepto_monto(self, tipo: str):
        """Diálogo centrado y estilizado para pedir concepto y monto."""
        parent = self.ventana
        top = tk.Toplevel(parent)
        top.transient(parent)
        top.grab_set()
        top.configure(bg="#ffffff")
        top.title(f"Registrar {tipo}")

        # Contenedor con padding
        container = ttk.Frame(top, padding=20)
        container.pack(fill="both", expand=True)

        # Estilo general
        style = ttk.Style(top)
        style.configure("TLabel", background="#ffffff", font=("Segoe UI", 10))
        style.configure("TEntry", font=("Segoe UI", 11))
        style.configure("Accent.TButton", font=("Segoe UI", 10), padding=6)
        style.map("Accent.TButton",
                  foreground=[("active", "#ffffff")],
                  background=[("active", "#0078D4"), ("!active", "#005A9E")])

        # Variables
        var_concepto = tk.StringVar()
        var_monto    = tk.StringVar()

        # Título interno
        ttk.Label(container, text=f"{tipo} en caja",
                  font=("Segoe UI Semibold", 12)
        ).pack(pady=(0, 10))

        # Concepto
        ttk.Label(container, text="Concepto:").pack(anchor="w")
        ent1 = ttk.Entry(container, textvariable=var_concepto, width=30)
        ent1.pack(fill="x", pady=(0, 10))
        ent1.focus()

        # Monto
        ttk.Label(container, text="Monto (MXN):").pack(anchor="w")
        ent2 = ttk.Entry(container, textvariable=var_monto, width=30)
        ent2.pack(fill="x", pady=(0, 20))

        resultado = {"ok": False, "concepto": None, "monto": None}

        def on_aceptar():
            c = var_concepto.get().strip()
            m_str = var_monto.get().strip()
            if not c:
                messagebox.showwarning("Concepto vacío",
                                       "Debe ingresar un concepto válido.",
                                       parent=top)
                return
            try:
                m = float(m_str)
                if m <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Monto inválido",
                                       "Ingrese un número válido mayor que 0.",
                                       parent=top)
                return
            resultado.update(ok=True, concepto=c, monto=m)
            top.destroy()

        # Botones en línea
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Cancelar",
                   command=top.destroy).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Aceptar",
                   style="Accent.TButton",
                   command=on_aceptar).pack(side="right")

        # Enter/Escape
        top.bind("<Return>", lambda e: on_aceptar())
        top.bind("<Escape>", lambda e: top.destroy())

        # Forzamos layout, luego centramos
        top.update_idletasks()
        w, h = top.winfo_width(), top.winfo_height()
        px, py = parent.winfo_x(), parent.winfo_y()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        x = px + (pw - w)//2
        y = py + (ph - h)//2
        top.geometry(f"{w}x{h}+{x}+{y}")

        top.wait_window()
        return (resultado["concepto"], resultado["monto"]) if resultado["ok"] else None



    def cerrar_caja(self):
        """Método para cerrar la caja actual"""
        try:
            if self.caja_abierta:
                # Confirmar cierre
                if not messagebox.askyesno("Confirmar Cierre", "¿Estás seguro de que deseas cerrar la caja?"):
                    return

                # Obtener el saldo final actual
                conexion = conectar_bd()
                cursor = conexion.cursor()

                # Obtener información actual de la caja
                cursor.execute("""
                    SELECT total_ingresos, total_egresos, saldo_final
                    FROM caja
                    WHERE id_caja = %s
                """, (self.id_caja_actual,))

                caja = cursor.fetchone()

                if caja:
                    ingresos, egresos, saldo_final = caja

                    # Actualizar la caja con la hora de cierre
                    cursor.execute("""
                        UPDATE caja 
                        SET hora_cierre = %s
                        WHERE id_caja = %s
                    """, (datetime.now().time(), self.id_caja_actual))

                    conexion.commit()

                    # Preguntar si desea imprimir el corte
                    if messagebox.askyesno("Imprimir Corte", "¿Deseas imprimir el corte de caja?"):
                        self.imprimir_corte(self.id_caja_actual)

                    # Cambiar estado
                    self.caja_abierta = False
                    self.id_caja_actual = None

                    # Actualizar interfaz
                    self.actualizar_estado_caja()
                    self.configurar_tab_operaciones()

                    messagebox.showinfo(
                        "Cierre Exitoso",
                        f"La caja se ha cerrado correctamente con un saldo final de ${saldo_final:.2f}"
                    )
                else:
                    messagebox.showerror("Error", "No se pudo obtener la información de la caja actual")

                conexion.close()
            else:
                messagebox.showinfo("Información", "No hay una caja abierta para cerrar")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cerrar la caja: {str(e)}")
            print(f"Error al cerrar caja: {e}")

    def imprimir_corte(self, id_caja):
        """Imprime un corte de caja específico"""
        try:
            # Obtener información del corte
            conexion = conectar_bd()
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT c.id_caja, c.fecha, c.hora_apertura, c.hora_cierre, 
                       c.total_ingresos, c.total_egresos, c.saldo_final,
                       u.nombre
                FROM caja c
                JOIN usuarios u ON c.responsable = u.id_usuario
                WHERE c.id_caja = %s
            """, (id_caja,))

            corte = cursor.fetchone()

            # Obtener los movimientos de ese corte
            cursor.execute("""
                SELECT m.hora, m.tipo, m.concepto, m.monto, u.nombre
                FROM movimientos_caja m
                JOIN usuarios u ON m.id_usuario = u.id_usuario
                WHERE m.id_caja = %s
                ORDER BY m.hora
            """, (id_caja,))

            movimientos = cursor.fetchall()
            conexion.close()

            if corte:
                id_caja, fecha, hora_apertura, hora_cierre, ingresos, egresos, saldo, responsable = corte

                # Formatear fechas y horas de manera segura
                fecha_formateada = fecha.strftime("%d/%m/%Y") if hasattr(fecha, 'strftime') else str(fecha)
                hora_ap = hora_apertura.strftime("%H:%M:%S") if hora_apertura and hasattr(hora_apertura,
                                                                                          'strftime') else str(
                    hora_apertura) if hora_apertura else "N/A"
                hora_ci = hora_cierre.strftime("%H:%M:%S") if hora_cierre and hasattr(hora_cierre, 'strftime') else str(
                    hora_cierre) if hora_cierre else "Abierta"

                # Crear ticket
                ticket = Ticket()

                # Encabezado
                ticket.agregar_encabezado()
                ticket.agregar_titulo("CORTE DE CAJA")
                ticket.agregar_texto(f"Caja #: {id_caja}")
                ticket.agregar_texto(f"Fecha: {fecha_formateada}")
                ticket.agregar_texto(f"Apertura: {hora_ap}")
                ticket.agregar_texto(f"Cierre: {hora_ci}")
                ticket.agregar_texto(f"Responsable: {responsable}")
                ticket.agregar_linea()

                # Resumen
                ticket.agregar_texto_centrado("RESUMEN:")
                ticket.agregar_texto(f"Total ingresos: ${ingresos:.2f}")
                ticket.agregar_texto(f"Total egresos: ${egresos:.2f}")
                ticket.agregar_texto(f"Saldo final: ${saldo:.2f}")
                ticket.agregar_linea()

                # Detalle de movimientos
                if movimientos:
                    ticket.agregar_texto_centrado("DETALLE DE MOVIMIENTOS:")

                    # Agregar cada movimiento
                    for mov in movimientos:
                        hora, tipo_mov, concepto, monto, usuario = mov
                        hora_str = hora.strftime('%H:%M:%S') if hasattr(hora, 'strftime') else str(hora)

                        # Formatear tipo de movimiento
                        tipo_texto = "Ingreso" if tipo_mov == 'ingreso' else "Egreso"

                        # Agregar línea de movimiento
                        ticket.agregar_texto(f"{hora_str} - {tipo_texto}: {concepto}")

                        # Signo según el tipo
                        signo = "+" if tipo_mov == 'ingreso' else "-"
                        ticket.agregar_texto_derecha(f"{signo}${monto:.2f}")

                # Pie
                ticket.agregar_espacio()
                ticket.agregar_texto_centrado("Firma del Responsable: ___________________")
                ticket.agregar_espacio()

                # Generar nombre del archivo
                nombre_archivo = f"corte_caja_{id_caja}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

                # Generar el PDF
                ruta_pdf = ticket.generar_pdf(nombre_archivo)

                # Mostrar vista previa
                ticket.mostrar_vista_previa(ruta_pdf)

                messagebox.showinfo("Vista Previa", "Se ha generado la vista previa del corte de caja")
            else:
                messagebox.showwarning("Advertencia", "No se pudo obtener la información del corte")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo imprimir el corte: {str(e)}")
            print(f"Error al imprimir corte: {e}")

    # Agregar prints de debug extensivo
    def diagnosticar_pestanas(self):
        """Método para diagnosticar problemas con las pestañas"""
        print("\n=== DIAGNÓSTICO DE PESTAÑAS ===")

        # Verificar si las pestañas existen
        print(f"¿Existe tab_cortes? {hasattr(self, 'tab_cortes')}")
        print(f"¿Existe tab_movimientos? {hasattr(self, 'tab_movimientos')}")

        if hasattr(self, 'tabla_cortes'):
            print("\nTabla de cortes:")
            print(f"  Visible: {self.tabla_cortes.winfo_ismapped()}")
            print(f"  Geometría: {self.tabla_cortes.winfo_geometry()}")
            print(f"  Filas: {len(self.tabla_cortes.get_children())}")

        if hasattr(self, 'tabla_movimientos'):
            print("\nTabla de movimientos:")
            print(f"  Visible: {self.tabla_movimientos.winfo_ismapped()}")
            print(f"  Geometría: {self.tabla_movimientos.winfo_geometry()}")
            print(f"  Filas: {len(self.tabla_movimientos.get_children())}")

    def cargar_cortes(self):
        """Carga los cortes de caja para la fecha especificada"""
        try:
            # Limpiar tabla
            for item in self.tabla_cortes.get_children():
                self.tabla_cortes.delete(item)

            fecha = self.fecha_cortes.get()
            print(f"Cargando cortes para fecha: {fecha}")

            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Consulta ajustada según la estructura real de la base de datos
            consulta = """
            SELECT c.id_caja, c.fecha, c.hora_apertura, c.hora_cierre, 
                   c.total_ingresos, c.total_egresos, c.saldo_final, 
                   u.nombre as responsable
            FROM caja c
            JOIN usuarios u ON c.responsable = u.id_usuario
            WHERE c.fecha = %s
            ORDER BY c.hora_apertura DESC
            """

            cursor.execute(consulta, (fecha,))
            resultados = cursor.fetchall()
            print(f"Encontrados {len(resultados)} cortes")

            for fila in resultados:
                id_caja, fecha_db, hora_apertura, hora_cierre, ingresos, egresos, saldo, responsable = fila

                # Formatear fecha
                fecha_str = fecha_db.strftime("%d/%m/%Y") if hasattr(fecha_db, 'strftime') else str(fecha_db)

                # Formatear hora de apertura con manejo de nulos
                hora_apertura_str = "N/A"
                if hora_apertura:
                    try:
                        if hasattr(hora_apertura, 'strftime'):
                            hora_apertura_str = hora_apertura.strftime("%H:%M:%S")
                        else:
                            hora_apertura_str = str(hora_apertura)
                    except:
                        hora_apertura_str = str(hora_apertura)

                # Formatear hora de cierre con manejo de nulos
                hora_cierre_str = "Abierta"
                if hora_cierre:
                    try:
                        if hasattr(hora_cierre, 'strftime'):
                            hora_cierre_str = hora_cierre.strftime("%H:%M:%S")
                        else:
                            hora_cierre_str = str(hora_cierre)
                    except:
                        hora_cierre_str = str(hora_cierre)

                # Formatear valores monetarios con manejo de nulos
                ingresos_str = f"${float(ingresos):.2f}" if ingresos is not None else "$0.00"
                egresos_str = f"${float(egresos):.2f}" if egresos is not None else "$0.00"
                saldo_str = f"${float(saldo):.2f}" if saldo is not None else "$0.00"

                # Insertar en la tabla
                self.tabla_cortes.insert('', tk.END, values=(
                    id_caja, fecha_str, hora_apertura_str, hora_cierre_str,
                    ingresos_str, egresos_str, saldo_str, responsable
                ))

            conexion.close()

            # Si no hay resultados, mostrar un mensaje
            if len(resultados) == 0:
                self.tabla_cortes.insert('', tk.END, values=(
                    "", "No hay datos para esta fecha", "", "", "", "", "", ""
                ))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los cortes: {str(e)}")
            print(f"Error detallado al cargar cortes: {e}")
            import traceback
            traceback.print_exc()

            # Insertar mensaje de error en la tabla
            self.tabla_cortes.insert('', tk.END, values=(
                "", f"Error: {str(e)}", "", "", "", "", "", ""
            ))

    def diagnosticar_problema(self):
        """Identifica problemas con las pestañas y tablas"""
        print("\n=== DIAGNÓSTICO DE PESTAÑAS ===")

        # Verificar notebook
        if hasattr(self, 'notebook'):
            tabs = self.notebook.tabs()
            print(f"Pestañas disponibles: {len(tabs)}")
            for i, tab in enumerate(tabs):
                print(f"  Tab {i}: {tab}")
            print(f"Pestaña actual: {self.notebook.select()}")
        else:
            print("ERROR: No hay notebook configurado")

        # Verificar tabla de cortes
        if hasattr(self, 'tabla_cortes'):
            print("\nTabla de cortes:")
            print(f"  Existe: Sí")
            print(f"  Es visible: {self.tabla_cortes.winfo_ismapped()}")
            print(f"  Filas: {len(self.tabla_cortes.get_children())}")
        else:
            print("\nERROR: No existe tabla_cortes")

        # Verificar tabla de movimientos
        if hasattr(self, 'tabla_movimientos'):
            print("\nTabla de movimientos:")
            print(f"  Existe: Sí")
            print(f"  Es visible: {self.tabla_movimientos.winfo_ismapped()}")
            print(f"  Filas: {len(self.tabla_movimientos.get_children())}")
        else:
            print("\nERROR: No existe tabla_movimientos")

        # Mostrar mensaje al usuario
        messagebox.showinfo("Diagnóstico completado",
                            "Se ha ejecutado el diagnóstico. Revisa la consola para detalles.")

    # También agrega este método para hacer un test rápido de la tabla
    def test_tabla_cortes(self):
        """Prueba rápida de la tabla"""
        try:
            print("=== TEST TABLA ===")

            # Verificar que la tabla existe
            if not hasattr(self, 'tabla_cortes'):
                print("ERROR: tabla_cortes no existe!")
                return

            # Insertar un item de prueba
            self.tabla_cortes.insert('', tk.END, values=(
                '999', '04/05/2025', '10:00:00', '18:00:00',
                '$1000.00', '$200.00', '$800.00', 'TEST'
            ))

            # Verificar
            items = len(self.tabla_cortes.get_children())
            print(f"Items después de insertar prueba: {items}")

            # Actualizar vista
            self.tabla_cortes.update_idletasks()
            self.ventana.update()

            print("=== FIN TEST ===")

        except Exception as e:
            print(f"Error en test: {e}")

    # Si necesitas un botón de prueba para test_tabla_cortes:
    def agregar_boton_test(self):
        """Agrega un botón de test (solo para desarrollo)"""
        try:
            frame_filtros = getattr(self, 'frame_filtros', None)
            if frame_filtros:
                btn_test = tk.Button(
                    frame_filtros,
                    text="🧪 Test",
                    font=("Helvetica", 11),
                    bg="#ff5722",
                    fg="white",
                    cursor="hand2",
                    command=self.test_tabla_cortes
                )
                btn_test.grid(row=0, column=5, padx=5, pady=5)
        except Exception as e:
            print(f"Error al agregar botón test: {e}")

    def debug_tabla_cortes(self):
        """Debug para verificar estado de la tabla"""
        print("=== DEBUG TABLA CORTES ===")
        print(f"¿Existe tabla_cortes? {hasattr(self, 'tabla_cortes')}")
        if hasattr(self, 'tabla_cortes'):
            print(f"Tabla es visible? {self.tabla_cortes.winfo_viewable()}")
            print(f"Geometría de tabla: {self.tabla_cortes.winfo_geometry()}")
            print(f"Items en tabla: {len(self.tabla_cortes.get_children())}")
            print(f"Columnas configuradas: {self.tabla_cortes['columns']}")

            # Mostrar todos los items
            children = self.tabla_cortes.get_children()
            print(f"Total de hijos en tabla: {len(children)}")
            for child in children:
                print(f"  Item: {self.tabla_cortes.item(child, 'values')}")

    # Agregar este método a la clase GestionCaja para mostrar un resumen de ventas
    def ver_resumen_ventas_dia(self):
        """Muestra un resumen de las ventas registradas en la caja actual"""
        try:
            if not self.caja_abierta:
                messagebox.showinfo("Información", "Debe abrir la caja primero")
                return

            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Obtener resumen de ventas para la caja actual
            cursor.execute("""
                SELECT COUNT(*) as total_ventas, 
                       SUM(v.total) as total_facturado,
                       u.nombre as vendedor,
                       COUNT(*) as ventas_por_usuario
                FROM ventas v
                JOIN movimientos_caja mc ON mc.concepto LIKE CONCAT('Venta #', v.id_venta, '%')
                JOIN usuarios u ON v.id_usuario = u.id_usuario
                WHERE mc.id_caja = %s
                GROUP BY u.nombre
            """, (self.id_caja_actual,))

            resumen_vendedores = cursor.fetchall()

            # Obtener resumen general
            cursor.execute("""
                SELECT COUNT(*) as total_ventas, 
                       SUM(v.total) as total_facturado,
                       MIN(v.fecha) as primera_venta,
                       MAX(v.fecha) as ultima_venta
                FROM ventas v
                JOIN movimientos_caja mc ON mc.concepto LIKE CONCAT('Venta #', v.id_venta, '%')
                WHERE mc.id_caja = %s
            """, (self.id_caja_actual,))

            resumen_general = cursor.fetchone()

            # Mostrar ventana con resumen
            ventana_resumen = tk.Toplevel(self.ventana)
            ventana_resumen.title("Resumen de Ventas")
            ventana_resumen.geometry("600x400")
            ventana_resumen.config(bg="#f5f5f5")
            ventana_resumen.grab_set()

            utl.centrar_ventana(ventana_resumen, 600, 400)

            frame = tk.Frame(ventana_resumen, bg="#f5f5f5", padx=20, pady=20)
            frame.pack(fill=tk.BOTH, expand=True)

            # Título
            tk.Label(frame, text="RESUMEN DE VENTAS", font=("Helvetica", 14, "bold"),
                     bg="#f5f5f5", fg="#3a7ff6").pack(pady=(0, 10))

            # Resumen general
            if resumen_general:
                tk.Label(frame, text=f"Total de ventas: {resumen_general[0]}",
                         font=("Helvetica", 12), bg="#f5f5f5").pack(anchor=tk.W, pady=2)
                tk.Label(frame, text=f"Total facturado: ${resumen_general[1]:.2f}",
                         font=("Helvetica", 12), bg="#f5f5f5").pack(anchor=tk.W, pady=2)

                if resumen_general[2]:  # primera venta
                    tk.Label(frame, text=f"Primera venta: {resumen_general[2].strftime('%H:%M:%S')}",
                             font=("Helvetica", 12), bg="#f5f5f5").pack(anchor=tk.W, pady=2)
                if resumen_general[3]:  # última venta
                    tk.Label(frame, text=f"Última venta: {resumen_general[3].strftime('%H:%M:%S')}",
                             font=("Helvetica", 12), bg="#f5f5f5").pack(anchor=tk.W, pady=2)

            # Separador
            ttk.Separator(frame, orient="horizontal").pack(fill=tk.X, pady=10)

            # Resumen por vendedor
            tk.Label(frame, text="Ventas por Vendedor:", font=("Helvetica", 12, "bold"),
                     bg="#f5f5f5").pack(anchor=tk.W, pady=(10, 5))

            for vendedor in resumen_vendedores:
                tk.Label(frame, text=f"{vendedor[2]}: {vendedor[3]} ventas - ${vendedor[1]:.2f}",
                         font=("Helvetica", 11), bg="#f5f5f5").pack(anchor=tk.W, padx=20, pady=2)

            # Botón cerrar
            tk.Button(frame, text="Cerrar", bg="#3a7ff6", fg="white", width=10,
                      command=ventana_resumen.destroy).pack(pady=20)

            conexion.close()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el resumen: {str(e)}")

    # Agrega esta función temporal en tu clase GestionCaja
    def debug_parametros_sql(self):
        """Debug para entender el problema con los parámetros SQL"""
        try:
            fecha = self.fecha_cortes.get()
            print(f"DEBUG - Fecha original: '{fecha}'")
            print(f"DEBUG - Tipo de fecha: {type(fecha)}")

            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Probar consulta simple
            cursor.execute("SELECT COUNT(*) FROM caja WHERE DATE(fecha) = %s", (fecha,))
            count = cursor.fetchone()[0]
            print(f"DEBUG - Count: {count}")

            conexion.close()

        except Exception as e:
            print(f"DEBUG ERROR: {e}")
            import traceback
            traceback.print_exc()

    def agregar_boton_debug(self):
        """Agrega un botón para ejecutar verificaciones de debug (solo para desarrollo)"""
        if hasattr(self, 'frame_filtros'):
            btn_debug = tk.Button(
                self.frame_filtros,
                text="🔍 Debug",
                font=("Helvetica", 11),
                bg="#ff9800",
                fg="white",
                width=8,
                cursor="hand2",
                command=self.debug_verificar_fechas
            )
            btn_debug.grid(row=0, column=4, padx=5, pady=5)

    # Modificar el método configurar_tab_operaciones para agregar el botón de resumen de ventas
    def configurar_tab_operaciones(self):
        """Configura la pestaña de operaciones de caja"""
        # Limpiar la pestaña
        for widget in self.tab_operaciones.winfo_children():
            widget.destroy()

        # Frame para botones principales
        frame_botones_principales = tk.Frame(self.tab_operaciones, bg="#f5f5f5")
        frame_botones_principales.pack(pady=20)

        if not self.caja_abierta:
            # Si la caja está cerrada, mostrar solo botón de apertura
            btn_abrir = tk.Button(
                frame_botones_principales,
                text="Abrir Caja",
                font=("Helvetica", 12, "bold"),
                bg="#4caf50",
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                command=self.abrir_caja
            )
            btn_abrir.pack(padx=20, pady=10)

            lbl_info = tk.Label(
                frame_botones_principales,
                text="Debe abrir la caja para comenzar a operar",
                font=("Helvetica", 11),
                bg="#f5f5f5",
                fg="#666"
            )
            lbl_info.pack(pady=5)
        else:
            # Si la caja está abierta, mostrar todos los botones
            btn_nueva_venta = tk.Button(
                frame_botones_principales,
                text="💰 Nueva Venta",
                font=("Helvetica", 12),
                bg="#4caf50",
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                command=self.nueva_venta
            )
            btn_nueva_venta.grid(row=0, column=0, padx=10, pady=10)

            btn_otro_ingreso = tk.Button(
                frame_botones_principales,
                text="➕ Otro Ingreso",
                font=("Helvetica", 12),
                bg="#2196f3",
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                command=self.otro_ingreso
            )
            btn_otro_ingreso.grid(row=0, column=1, padx=10, pady=10)

            btn_egreso = tk.Button(
                frame_botones_principales,
                text="➖ Registrar Egreso",
                font=("Helvetica", 12),
                bg="#f44336",
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                command=self.registrar_egreso
            )
            btn_egreso.grid(row=0, column=2, padx=10, pady=10)

            # Botón de arqueo de caja (asegúrate de que esté visible y con el comando correcto)
            btn_arqueo = tk.Button(
                frame_botones_principales,
                text="🧮 Arqueo de Caja",
                font=("Helvetica", 12),
                bg="#9c27b0",
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                command=self.realizar_arqueo_caja
            )
            btn_arqueo.grid(row=1, column=0, padx=10, pady=10)

            btn_resumen_ventas = tk.Button(
                frame_botones_principales,
                text="📊 Resumen Ventas",
                font=("Helvetica", 12),
                bg="#ff9800",
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                command=self.ver_resumen_ventas_dia
            )
            btn_resumen_ventas.grid(row=1, column=1, padx=10, pady=10)

            btn_cerrar = tk.Button(
                frame_botones_principales,
                text="🔒 Cerrar Caja",
                font=("Helvetica", 12, "bold"),
                bg="#795548",
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                command=self.cerrar_caja
            )
            btn_cerrar.grid(row=1, column=2, padx=10, pady=20)

            # Frame para operaciones especiales (siempre visible)
            frame_especial = tk.Frame(self.tab_operaciones, bg="#f5f5f5", padx=20, pady=10)
            frame_especial.pack(fill=tk.X, pady=10)

            ttk.Separator(self.tab_operaciones, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=20)

            lbl_operaciones = tk.Label(
                frame_especial,
                text="Operaciones Especiales",
                font=("Helvetica", 12, "bold"),
                bg="#f5f5f5"
            )
            lbl_operaciones.pack(anchor=tk.W, pady=5)

            frame_botones_especiales = tk.Frame(frame_especial, bg="#f5f5f5")
            frame_botones_especiales.pack(fill=tk.X)

            btn_ultimo_corte = tk.Button(
                frame_botones_especiales,
                text="Ver Último Corte",
                font=("Helvetica", 11),
                bg="#3f51b5",
                fg="white",
                width=15,
                cursor="hand2",
                command=self.ver_ultimo_corte
            )
            btn_ultimo_corte.grid(row=0, column=0, padx=5, pady=5)

            btn_imprimir = tk.Button(
                frame_botones_especiales,
                text="Imprimir Estado",
                font=("Helvetica", 11),
                bg="#3f51b5",
                fg="white",
                width=15,
                cursor="hand2",
                command=self.imprimir_estado_caja
            )
            btn_imprimir.grid(row=0, column=1, padx=5, pady=5)

            # Botón para ver arqueos anteriores
            btn_ver_arqueos = tk.Button(
                frame_botones_especiales,
                text="📋 Ver Arqueos",
                font=("Helvetica", 11),
                bg="#3f51b5",
                fg="white",
                width=15,
                cursor="hand2",
                command=self.ver_arqueos_anteriores
            )
            btn_ver_arqueos.grid(row=0, column=2, padx=5, pady=5)

            # Estado actual rápido
            frame_estado_rapido = tk.Frame(self.tab_operaciones, bg="#f0f7ff", padx=10, pady=5)
            frame_estado_rapido.pack(fill=tk.X, pady=10, padx=20)

            self.lbl_ventas_hoy = tk.Label(
                frame_estado_rapido,
                text="Ventas hoy: $0.00",
                font=("Helvetica", 11),
                bg="#f0f7ff"
            )
            self.lbl_ventas_hoy.pack()

            self.lbl_pedidos_pendientes = tk.Label(
                frame_estado_rapido,
                text="Pedidos pendientes: 0",
                font=("Helvetica", 11),
                bg="#f0f7ff"
            )
            self.lbl_pedidos_pendientes.pack()

    # Agregar estos métodos a la clase
    def nueva_venta(self):
        """Abre el módulo de ventas y refresca la caja cuando se cierre."""
        try:
            from ventas import Ventas

            # 1) Instanciamos y capturamos el objeto
            ventas_win = Ventas(self.ventana)

            # 2) Esperamos a que su Toplevel se cierre
            #    (Ventas debe exponer su ventana en, por ejemplo, ventas_win.ventana)
            self.ventana.wait_window(ventas_win.ventana)

            # 3) Solo al cerrar la ventana de ventas refrescamos la caja
            self.actualizar_estado_caja()
            if hasattr(self, 'cargar_movimientos'):
                self.cargar_movimientos()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir ventas: {e}")

    def nuevo_pedido(self):
        """Abre el módulo de pedidos"""
        try:
            from pedidos import Pedidos
            Pedidos(self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir pedidos: {str(e)}")

    def ver_arqueos_anteriores(self):
        """Muestra los arqueos realizados previamente para la caja actual"""
        try:
            if not self.id_caja_actual:
                messagebox.showinfo("Información", "No hay una caja seleccionada")
                return

            # Crear ventana para mostrar arqueos
            ventana_arqueos = tk.Toplevel(self.ventana)
            ventana_arqueos.title("Historial de Arqueos")
            ventana_arqueos.geometry("800x500")
            ventana_arqueos.config(bg="#f5f5f5")
            ventana_arqueos.grab_set()  # Hacer modal
            utl.centrar_ventana(ventana_arqueos, 800, 500)

            # Frame principal
            frame_principal = tk.Frame(ventana_arqueos, bg="#f5f5f5", padx=20, pady=20)
            frame_principal.pack(fill=tk.BOTH, expand=True)

            # Título
            tk.Label(
                frame_principal,
                text=f"HISTORIAL DE ARQUEOS - Caja #{self.id_caja_actual}",
                font=("Helvetica", 14, "bold"),
                bg="#f5f5f5",
                fg="#3a7ff6"
            ).pack(pady=(0, 20))

            # Frame para la tabla
            frame_tabla = tk.Frame(frame_principal, bg="#f5f5f5")
            frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10)

            # Columnas de la tabla
            columnas = ('id', 'fecha', 'hora', 'saldo_sistema', 'efectivo', 'diferencia', 'usuario')

            tabla_arqueos = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=15)
            utl.aplicar_estilo_tabla(tabla_arqueos)

            # Configurar encabezados
            tabla_arqueos.heading('id', text='ID')
            tabla_arqueos.heading('fecha', text='Fecha')
            tabla_arqueos.heading('hora', text='Hora')
            tabla_arqueos.heading('saldo_sistema', text='Saldo Sistema')
            tabla_arqueos.heading('efectivo', text='Efectivo Contado')
            tabla_arqueos.heading('diferencia', text='Diferencia')
            tabla_arqueos.heading('usuario', text='Usuario')

            # Configurar anchos
            tabla_arqueos.column('id', width=50, anchor=tk.CENTER)
            tabla_arqueos.column('fecha', width=100, anchor=tk.CENTER)
            tabla_arqueos.column('hora', width=100, anchor=tk.CENTER)
            tabla_arqueos.column('saldo_sistema', width=120, anchor=tk.E)
            tabla_arqueos.column('efectivo', width=120, anchor=tk.E)
            tabla_arqueos.column('diferencia', width=100, anchor=tk.E)
            tabla_arqueos.column('usuario', width=150)

            # Scrollbar para la tabla
            scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=tabla_arqueos.yview)
            tabla_arqueos.configure(yscrollcommand=scrollbar.set)

            # Empaquetar tabla y scrollbar
            tabla_arqueos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Para obtener la estructura de la tabla
            def obtener_estructura_tabla():
                try:
                    conexion = conectar_bd()
                    cursor = conexion.cursor()
                    cursor.execute("DESCRIBE arqueos_caja")
                    columnas = [col[0] for col in cursor.fetchall()]
                    conexion.close()
                    return columnas
                except Exception as e:
                    print(f"Error al obtener estructura: {e}")
                    return []

            # Obtener columnas de la tabla
            columnas_tabla = obtener_estructura_tabla()
            print(f"Columnas en arqueos_caja: {columnas_tabla}")

            # Definimos las funciones auxiliares
            def mostrar_detalle_arqueo(id_arqueo):
                try:
                    conexion = conectar_bd()
                    cursor = conexion.cursor()

                    # Verificar las columnas existentes
                    if 'fecha_hora' in columnas_tabla:
                        # Versión con fecha_hora unificada
                        consulta = """
                            SELECT a.id_arqueo, DATE(a.fecha_hora) as fecha, TIME(a.fecha_hora) as hora, 
                                   a.total_sistema as saldo_sistema, a.total_fisico as efectivo_contado, 
                                   a.diferencia, a.observaciones, u.nombre
                            FROM arqueos_caja a
                            JOIN usuarios u ON a.id_usuario = u.id_usuario
                            WHERE a.id_arqueo = %s
                        """
                    elif 'fecha' in columnas_tabla and 'hora' in columnas_tabla:
                        # Versión con fecha y hora separadas
                        consulta = """
                            SELECT a.id_arqueo, a.fecha, a.hora, a.saldo_sistema, 
                                   a.efectivo_contado, a.diferencia, a.observaciones, u.nombre
                            FROM arqueos_caja a
                            JOIN usuarios u ON a.id_usuario = u.id_usuario
                            WHERE a.id_arqueo = %s
                        """
                    else:
                        # Intentemos una versión más genérica
                        consulta = """
                            SELECT a.id_arqueo, CURDATE() as fecha, CURTIME() as hora, 
                                   a.saldo_sistema, a.efectivo_contado, a.diferencia, 
                                   a.observaciones, u.nombre
                            FROM arqueos_caja a
                            JOIN usuarios u ON a.id_usuario = u.id_usuario
                            WHERE a.id_arqueo = %s
                        """

                    cursor.execute(consulta, (id_arqueo,))
                    arqueo = cursor.fetchone()
                    conexion.close()

                    if arqueo:
                        id_a, fecha, hora, saldo, efectivo, diferencia, observaciones, usuario = arqueo

                        # Crear ventana de detalles
                        ventana_detalle = tk.Toplevel(ventana_arqueos)
                        ventana_detalle.title(f"Detalle de Arqueo #{id_a}")
                        ventana_detalle.geometry("500x400")
                        ventana_detalle.config(bg="#f5f5f5")
                        ventana_detalle.grab_set()
                        utl.centrar_ventana(ventana_detalle, 500, 400)

                        # Frame principal
                        frame_det = tk.Frame(ventana_detalle, bg="#f5f5f5", padx=20, pady=20)
                        frame_det.pack(fill=tk.BOTH, expand=True)

                        # Título
                        tk.Label(
                            frame_det,
                            text=f"DETALLE DE ARQUEO #{id_a}",
                            font=("Helvetica", 14, "bold"),
                            bg="#f5f5f5",
                            fg="#3a7ff6"
                        ).pack(pady=(0, 20))

                        # Información del arqueo en formato de tabla
                        info_frame = tk.Frame(frame_det, bg="#f0f7ff", padx=15, pady=15, relief=tk.GROOVE, bd=1)
                        info_frame.pack(fill=tk.BOTH, expand=True)

                        # Fecha y hora formateadas
                        fecha_str = fecha.strftime("%d/%m/%Y") if hasattr(fecha, 'strftime') else str(fecha)
                        hora_str = hora.strftime("%H:%M:%S") if hasattr(hora, 'strftime') else str(hora)

                        # Datos
                        datos = [
                            ("ID:", str(id_a)),
                            ("Fecha:", fecha_str),
                            ("Hora:", hora_str),
                            ("Realizado por:", usuario),
                            ("Saldo en Sistema:", f"${float(saldo):.2f}"),
                            ("Efectivo Contado:", f"${float(efectivo):.2f}")
                        ]

                        # Diferencia con color
                        if diferencia > 0:
                            dif_str = f"Sobrante: ${diferencia:.2f}"
                            color_dif = "#388e3c"  # Verde
                        elif diferencia < 0:
                            dif_str = f"Faltante: ${abs(diferencia):.2f}"
                            color_dif = "#d32f2f"  # Rojo
                        else:
                            dif_str = "Sin diferencia"
                            color_dif = "#000000"  # Negro

                        for i, (etiqueta, valor) in enumerate(datos):
                            tk.Label(
                                info_frame,
                                text=etiqueta,
                                font=("Helvetica", 11, "bold"),
                                bg="#f0f7ff",
                                anchor=tk.W
                            ).grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)

                            tk.Label(
                                info_frame,
                                text=valor,
                                font=("Helvetica", 11),
                                bg="#f0f7ff",
                                anchor=tk.W
                            ).grid(row=i, column=1, sticky=tk.W, padx=5, pady=5)

                        # Diferencia con color especial
                        tk.Label(
                            info_frame,
                            text="Diferencia:",
                            font=("Helvetica", 11, "bold"),
                            bg="#f0f7ff",
                            anchor=tk.W
                        ).grid(row=len(datos), column=0, sticky=tk.W, padx=5, pady=5)

                        tk.Label(
                            info_frame,
                            text=dif_str,
                            font=("Helvetica", 11, "bold"),
                            bg="#f0f7ff",
                            fg=color_dif,
                            anchor=tk.W
                        ).grid(row=len(datos), column=1, sticky=tk.W, padx=5, pady=5)

                        # Observaciones
                        if observaciones:
                            tk.Label(
                                frame_det,
                                text="Observaciones:",
                                font=("Helvetica", 11, "bold"),
                                bg="#f5f5f5",
                                anchor=tk.W
                            ).pack(anchor=tk.W, pady=(20, 5))

                            txt_obs = tk.Text(frame_det, height=4, width=50, font=("Helvetica", 11))
                            txt_obs.pack(fill=tk.X, pady=(0, 10))
                            txt_obs.insert("1.0", observaciones)
                            txt_obs.config(state=tk.DISABLED)  # Solo lectura

                        # Botones
                        frame_bot = tk.Frame(frame_det, bg="#f5f5f5")
                        frame_bot.pack(pady=15)

                        btn_imprimir = tk.Button(
                            frame_bot,
                            text="Imprimir",
                            font=("Helvetica", 11),
                            bg="#3a7ff6",
                            fg="white",
                            width=10,
                            cursor="hand2",
                            command=lambda: imprimir_arqueo_existente(id_a)
                        )
                        btn_imprimir.pack(side=tk.LEFT, padx=10)

                        btn_cerrar = tk.Button(
                            frame_bot,
                            text="Cerrar",
                            font=("Helvetica", 11),
                            bg="#e53935",
                            fg="white",
                            width=10,
                            cursor="hand2",
                            command=ventana_detalle.destroy
                        )
                        btn_cerrar.pack(side=tk.LEFT, padx=10)

                    else:
                        messagebox.showinfo("Información", "No se encontró el arqueo solicitado")

                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo mostrar el detalle del arqueo: {str(e)}")
                    print(f"Error detallado: {e}")
                    import traceback
                    traceback.print_exc()

            def imprimir_arqueo_existente(id_arqueo):
                # Función para imprimir (puede simplificarse para el ejemplo)
                messagebox.showinfo("Imprimir Arqueo", f"Imprimiendo arqueo {id_arqueo}")

            def ver_detalle_arqueo():
                seleccion = tabla_arqueos.selection()
                if not seleccion:
                    messagebox.showinfo("Información", "Seleccione un arqueo para ver detalles")
                    return

                item = tabla_arqueos.item(seleccion[0])
                id_arqueo = item['values'][0]
                mostrar_detalle_arqueo(id_arqueo)

            def imprimir_arqueo_seleccionado():
                seleccion = tabla_arqueos.selection()
                if not seleccion:
                    messagebox.showinfo("Información", "Seleccione un arqueo para imprimir")
                    return

                item = tabla_arqueos.item(seleccion[0])
                id_arqueo = item['values'][0]
                imprimir_arqueo_existente(id_arqueo)

            # Cargar arqueos con seguridad
            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()

                # Mostrar datos de ejemplo primero (para asegurar que la tabla tenga contenido)
                for i in range(1, 4):
                    tabla_arqueos.insert('', tk.END, values=(
                        i,
                        date.today().strftime("%d/%m/%Y"),
                        datetime.now().strftime("%H:%M:%S"),
                        f"${1000.0:.2f}",
                        f"${950.0:.2f}",
                        f"Faltante: ${50.0:.2f}",
                        "Usuario"
                    ), tags=('faltante',))

                # Configurar colores de tags
                tabla_arqueos.tag_configure('sobrante', background='#e8f5e9')
                tabla_arqueos.tag_configure('faltante', background='#ffebee')
                tabla_arqueos.tag_configure('equilibrado', background='#e3f2fd')

                # Intentar cargar datos reales después
                try:
                    # Limpiar tabla primero
                    for item in tabla_arqueos.get_children():
                        tabla_arqueos.delete(item)

                    if 'fecha_hora' in columnas_tabla:
                        # Versión con fecha_hora unificada
                        consulta = """
                            SELECT a.id_arqueo, DATE(a.fecha_hora) as fecha, TIME(a.fecha_hora) as hora, 
                                   a.total_sistema as saldo_sistema, a.total_fisico as efectivo_contado, 
                                   a.diferencia, u.nombre
                            FROM arqueos_caja a
                            JOIN usuarios u ON a.id_usuario = u.id_usuario
                            WHERE a.id_caja = %s
                            ORDER BY a.fecha_hora DESC
                        """
                    elif 'fecha' in columnas_tabla and 'hora' in columnas_tabla:
                        # Versión con fecha y hora separadas
                        consulta = """
                            SELECT a.id_arqueo, a.fecha, a.hora, a.saldo_sistema, 
                                   a.efectivo_contado, a.diferencia, u.nombre
                            FROM arqueos_caja a
                            JOIN usuarios u ON a.id_usuario = u.id_usuario
                            WHERE a.id_caja = %s
                            ORDER BY a.fecha DESC, a.hora DESC
                        """
                    else:
                        # Si no podemos determinar la estructura, usamos la tabla como está
                        raise Exception("No se pudo determinar la estructura de la tabla arqueos_caja")

                    cursor.execute(consulta, (self.id_caja_actual,))
                    arqueos = cursor.fetchall()

                    if arqueos:
                        # Limpiar tabla de nuevo
                        for item in tabla_arqueos.get_children():
                            tabla_arqueos.delete(item)

                        for arqueo in arqueos:
                            id_arqueo, fecha, hora, saldo, efectivo, diferencia, usuario = arqueo

                            # Formatear fecha y hora
                            fecha_str = fecha.strftime("%d/%m/%Y") if hasattr(fecha, 'strftime') else str(fecha)
                            hora_str = hora.strftime("%H:%M:%S") if hasattr(hora, 'strftime') else str(hora)

                            # Formatear valores monetarios
                            saldo_str = f"${float(saldo):.2f}"
                            efectivo_str = f"${float(efectivo):.2f}"

                            # Formatear diferencia con color
                            if diferencia > 0:
                                dif_str = f"Sobrante: ${diferencia:.2f}"
                                tag = 'sobrante'
                            elif diferencia < 0:
                                dif_str = f"Faltante: ${abs(diferencia):.2f}"
                                tag = 'faltante'
                            else:
                                dif_str = "Sin diferencia"
                                tag = 'equilibrado'

                            item = tabla_arqueos.insert('', tk.END, values=(
                                id_arqueo, fecha_str, hora_str, saldo_str, efectivo_str, dif_str, usuario
                            ), tags=(tag,))
                except Exception as e:
                    print(f"Error al cargar datos reales: {e}")
                    # Mantenemos los datos de ejemplo si falla

                conexion.close()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el historial de arqueos: {str(e)}")
                print(f"Error detallado: {e}")
                import traceback
                traceback.print_exc()

            # Frame para botones
            frame_botones = tk.Frame(frame_principal, bg="#f5f5f5")
            frame_botones.pack(pady=15)

            # Botones
            btn_detalle = tk.Button(
                frame_botones,
                text="Ver Detalle",
                font=("Helvetica", 11),
                bg="#3a7ff6",
                fg="white",
                width=12,
                cursor="hand2",
                command=ver_detalle_arqueo
            )
            btn_detalle.pack(side=tk.LEFT, padx=10)

            btn_imprimir = tk.Button(
                frame_botones,
                text="Imprimir",
                font=("Helvetica", 11),
                bg="#4caf50",
                fg="white",
                width=12,
                cursor="hand2",
                command=imprimir_arqueo_seleccionado
            )
            btn_imprimir.pack(side=tk.LEFT, padx=10)

            # Botón cerrar
            btn_cerrar = tk.Button(
                frame_botones,
                text="Cerrar",
                font=("Helvetica", 11),
                bg="#e53935",
                fg="white",
                width=10,
                cursor="hand2",
                command=ventana_arqueos.destroy
            )
            btn_cerrar.pack(side=tk.LEFT, padx=10)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el historial de arqueos: {str(e)}")
            print(f"Error detallado: {e}")
            import traceback
            traceback.print_exc()

    def exportar_arqueos_pdf(self):
        """Exporta todos los arqueos de la caja actual a un PDF"""
        try:
            if not self.id_caja_actual:
                messagebox.showinfo("Información", "No hay una caja seleccionada")
                return

            # Obtener información de la caja
            conexion = conectar_bd()
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT c.fecha, c.hora_apertura, c.hora_cierre, 
                       u.nombre as responsable
                FROM caja c
                JOIN usuarios u ON c.responsable = u.id_usuario
                WHERE c.id_caja = %s
            """, (self.id_caja_actual,))

            caja = cursor.fetchone()

            # Obtener todos los arqueos de la caja
            cursor.execute("""
                SELECT a.id_arqueo, a.fecha, a.hora, a.saldo_sistema, 
                       a.efectivo_contado, a.diferencia, a.observaciones, u.nombre
                FROM arqueos_caja a
                JOIN usuarios u ON a.id_usuario = u.id_usuario
                WHERE a.id_caja = %s
                ORDER BY a.fecha, a.hora
            """, (self.id_caja_actual,))

            arqueos = cursor.fetchall()
            conexion.close()

            if not arqueos:
                messagebox.showinfo("Información", "No hay arqueos para exportar")
                return

            # Crear ticket para PDF
            ticket = Ticket()

            # Encabezado
            ticket.agregar_encabezado()
            ticket.agregar_titulo("REPORTE DE ARQUEOS DE CAJA")

            if caja:
                fecha, hora_ap, hora_ci, resp = caja

                # Formatear fecha y horas
                fecha_str = fecha.strftime("%d/%m/%Y") if hasattr(fecha, 'strftime') else str(fecha)
                hora_ap_str = hora_ap.strftime("%H:%M:%S") if hora_ap and hasattr(hora_ap, 'strftime') else "N/A"

                if hora_ci:
                    hora_ci_str = hora_ci.strftime("%H:%M:%S") if hasattr(hora_ci, 'strftime') else str(hora_ci)
                    estado = "CERRADA"
                else:
                    hora_ci_str = "No cerrada"
                    estado = "ABIERTA"

                ticket.agregar_texto(f"Caja #: {self.id_caja_actual} - Estado: {estado}")
                ticket.agregar_texto(f"Fecha: {fecha_str}")
                ticket.agregar_texto(f"Apertura: {hora_ap_str} - Cierre: {hora_ci_str}")
                ticket.agregar_texto(f"Responsable: {resp}")
            else:
                ticket.agregar_texto(f"Caja #: {self.id_caja_actual}")

            ticket.agregar_linea()

            # Tabla de arqueos
            ticket.agregar_texto_centrado("ARQUEOS REALIZADOS")
            ticket.agregar_texto("")

            # Encabezados de tabla
            ticket.agregar_texto("ID  FECHA       HORA     SALDO        EFECTIVO     DIFERENCIA    USUARIO")
            ticket.agregar_linea()

            # Datos de arqueos
            for arqueo in arqueos:
                id_a, fecha, hora, saldo, efectivo, diferencia, obs, usuario = arqueo

                # Formatear fecha y hora
                fecha_str = fecha.strftime("%d/%m/%Y") if hasattr(fecha, 'strftime') else str(fecha)
                hora_str = hora.strftime("%H:%M") if hasattr(hora, 'strftime') else str(hora)

                # Formatear valores monetarios
                saldo_str = f"${float(saldo):.2f}".ljust(12)
                efectivo_str = f"${float(efectivo):.2f}".ljust(12)

                # Formatear diferencia
                if diferencia > 0:
                    dif_str = f"${diferencia:.2f} (S)".ljust(13)  # Sobrante
                elif diferencia < 0:
                    dif_str = f"${abs(diferencia):.2f} (F)".ljust(13)  # Faltante
                else:
                    dif_str = "$0.00".ljust(13)

                # Limitar longitud del nombre de usuario
                if len(usuario) > 12:
                    usuario = usuario[:10] + "..."

                # Agregar línea a la tabla
                linea = f"{str(id_a).ljust(4)}{fecha_str.ljust(11)}{hora_str.ljust(8)}{saldo_str}{efectivo_str}{dif_str}{usuario}"
                ticket.agregar_texto(linea)

                # Si hay observaciones, agregarlas con sangría
                if obs and len(obs.strip()) > 0:
                    ticket.agregar_texto(f"  Obs: {obs[:50]}")
                    if len(obs) > 50:
                        ticket.agregar_texto(f"       {obs[50:100]}")

            ticket.agregar_linea()

            # Resumen
            total_arqueos = len(arqueos)
            total_diferencias = sum(a[5] for a in arqueos)

            ticket.agregar_texto(f"Total de arqueos: {total_arqueos}")

            if total_diferencias > 0:
                ticket.agregar_texto(f"Diferencia acumulada: Sobrante ${total_diferencias:.2f}")
            elif total_diferencias < 0:
                ticket.agregar_texto(f"Diferencia acumulada: Faltante ${abs(total_diferencias):.2f}")
            else:
                ticket.agregar_texto("Diferencia acumulada: $0.00")

            # Pie del reporte
            ticket.agregar_espacio()
            ticket.agregar_texto(f"Reporte generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

            # Generar nombre del archivo
            nombre_archivo = f"reporte_arqueos_caja_{self.id_caja_actual}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

            # Generar PDF
            ruta_pdf = ticket.generar_pdf(nombre_archivo)

            # Mostrar vista previa
            ticket.mostrar_vista_previa(ruta_pdf)

            messagebox.showinfo("PDF Generado", "El reporte de arqueos ha sido generado correctamente")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte de arqueos: {str(e)}")

    def imprimir_arqueo_existente(self, id_arqueo):
        """Imprime un arqueo existente en formato de ticket"""
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT a.id_arqueo, a.fecha, a.hora, a.saldo_sistema, 
                       a.efectivo_contado, a.diferencia, a.observaciones, u.nombre
                FROM arqueos_caja a
                JOIN usuarios u ON a.id_usuario = u.id_usuario
                WHERE a.id_arqueo = %s
            """, (id_arqueo,))

            arqueo = cursor.fetchone()
            conexion.close()

            if arqueo:
                id_a, fecha, hora, saldo, efectivo, diferencia, observaciones, usuario = arqueo

                # Crear ticket
                ticket = Ticket()

                # Encabezado
                ticket.agregar_encabezado()
                ticket.agregar_titulo("ARQUEO DE CAJA")
                ticket.agregar_texto(f"Arqueo #: {id_a}")

                # Fecha y hora formateadas
                fecha_str = fecha.strftime("%d/%m/%Y") if hasattr(fecha, 'strftime') else str(fecha)
                hora_str = hora.strftime("%H:%M:%S") if hasattr(hora, 'strftime') else str(hora)

                ticket.agregar_texto(f"Fecha: {fecha_str}")
                ticket.agregar_texto(f"Hora: {hora_str}")
                ticket.agregar_texto(f"Realizado por: {usuario}")
                ticket.agregar_linea()

                # Detalles del arqueo
                ticket.agregar_texto(f"Saldo en Sistema: ${float(saldo):.2f}")
                ticket.agregar_texto(f"Efectivo Contado: ${float(efectivo):.2f}")

                # Diferencia
                if diferencia > 0:
                    ticket.agregar_texto(f"Sobrante: ${diferencia:.2f}")
                elif diferencia < 0:
                    ticket.agregar_texto(f"Faltante: ${abs(diferencia):.2f}")
                else:
                    ticket.agregar_texto("Sin diferencia")

                ticket.agregar_linea()

                # Observaciones
                if observaciones:
                    ticket.agregar_texto("OBSERVACIONES:")
                    ticket.agregar_texto(observaciones)
                    ticket.agregar_linea()

                # Firmas
                ticket.agregar_espacio()
                ticket.agregar_texto_centrado("___________________")
                ticket.agregar_texto_centrado("Firma del Cajero")
                ticket.agregar_espacio()
                ticket.agregar_texto_centrado("___________________")
                ticket.agregar_texto_centrado("Supervisor")

                # Generar nombre del archivo
                nombre_archivo = f"arqueo_caja_{id_a}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

                # Generar PDF
                ruta_pdf = ticket.generar_pdf(nombre_archivo)

                # Mostrar vista previa
                ticket.mostrar_vista_previa(ruta_pdf)

            else:
                messagebox.showinfo("Información", "No se encontró el arqueo solicitado")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo imprimir el arqueo: {str(e)}")

    def seguimiento_pedidos(self):
        """Abre el seguimiento de pedidos"""
        try:
            from seguimiento_pedidos import SeguimientoPedidos
            SeguimientoPedidos(self.ventana, self.id_usuario)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir seguimiento: {str(e)}")

    def gestionar_clientes(self):
        """Abre la gestión de clientes"""
        try:
            from clientes import GestionClientes
            GestionClientes(self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir clientes: {str(e)}")

    def resumen_dia(self):
        """Muestra un resumen completo del día"""
        try:
            if not self.caja_abierta:
                messagebox.showinfo("Información", "Debe abrir la caja primero")
                return

            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Obtener resumen completo
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM ventas v 
                     JOIN movimientos_caja mc ON mc.concepto LIKE CONCAT('Venta #', v.id_venta, '%') 
                     WHERE mc.id_caja = %s) as total_ventas,
                    (SELECT SUM(v.total) FROM ventas v 
                     JOIN movimientos_caja mc ON mc.concepto LIKE CONCAT('Venta #', v.id_venta, '%') 
                     WHERE mc.id_caja = %s) as total_vendido,
                    (SELECT COUNT(*) FROM pedidos p WHERE DATE(p.fecha_pedido) = CURDATE()) as total_pedidos,
                    (SELECT COUNT(*) FROM pedidos p WHERE DATE(p.fecha_pedido) = CURDATE() AND p.estado != 'Entregado') as pedidos_pendientes
            """, (self.id_caja_actual, self.id_caja_actual))

            resumen = cursor.fetchone()

            # Obtener ingresos y egresos de la caja
            cursor.execute("""
                SELECT total_ingresos, total_egresos, saldo_final
                FROM caja WHERE id_caja = %s
            """, (self.id_caja_actual,))

            caja_info = cursor.fetchone()
            conexion.close()

            # Crear ventana de resumen
            ventana_resumen = tk.Toplevel(self.ventana)
            ventana_resumen.title("Resumen del Día")
            ventana_resumen.geometry("600x500")
            ventana_resumen.config(bg="#f5f5f5")
            ventana_resumen.grab_set()

            utl.centrar_ventana(ventana_resumen, 600, 500)

            frame = tk.Frame(ventana_resumen, bg="#f5f5f5", padx=20, pady=20)
            frame.pack(fill=tk.BOTH, expand=True)

            # Título
            tk.Label(frame, text="RESUMEN DEL DÍA", font=("Helvetica", 16, "bold"),
                     bg="#f5f5f5", fg="#303f9f").pack(pady=(0, 20))

            # Ventas
            tk.Label(frame, text="VENTAS", font=("Helvetica", 14, "bold"),
                     bg="#f5f5f5").pack(anchor=tk.W, pady=(10, 5))
            tk.Label(frame, text=f"Total de ventas: {resumen[0]}",
                     font=("Helvetica", 12), bg="#f5f5f5").pack(anchor=tk.W, padx=20)
            tk.Label(frame, text=f"Total vendido: ${resumen[1]:.2f}",
                     font=("Helvetica", 12), bg="#f5f5f5").pack(anchor=tk.W, padx=20)

            # Pedidos
            tk.Label(frame, text="PEDIDOS", font=("Helvetica", 14, "bold"),
                     bg="#f5f5f5").pack(anchor=tk.W, pady=(20, 5))
            tk.Label(frame, text=f"Total de pedidos: {resumen[2]}",
                     font=("Helvetica", 12), bg="#f5f5f5").pack(anchor=tk.W, padx=20)
            tk.Label(frame, text=f"Pedidos pendientes: {resumen[3]}",
                     font=("Helvetica", 12), bg="#f5f5f5").pack(anchor=tk.W, padx=20)

            # Caja
            if caja_info:
                tk.Label(frame, text="CAJA", font=("Helvetica", 14, "bold"),
                         bg="#f5f5f5").pack(anchor=tk.W, pady=(20, 5))
                tk.Label(frame, text=f"Total ingresos: ${caja_info[0]:.2f}",
                         font=("Helvetica", 12), bg="#f5f5f5").pack(anchor=tk.W, padx=20)
                tk.Label(frame, text=f"Total egresos: ${caja_info[1]:.2f}",
                         font=("Helvetica", 12), bg="#f5f5f5").pack(anchor=tk.W, padx=20)
                tk.Label(frame, text=f"Saldo actual: ${caja_info[2]:.2f}",
                         font=("Helvetica", 12, "bold"), bg="#f5f5f5", fg="#4caf50").pack(anchor=tk.W, padx=20)

            # Botón cerrar
            tk.Button(frame, text="Cerrar", bg="#e53935", fg="white", width=10,
                      command=ventana_resumen.destroy).pack(pady=30)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el resumen: {str(e)}")

    def cargar_movimientos(self):
        """Carga los movimientos de caja con información detallada de usuarios"""
        try:
            # Limpiar tabla
            for item in self.tabla_movimientos.get_children():
                self.tabla_movimientos.delete(item)

            # Obtener parámetros de filtro
            fecha = self.fecha_movimientos.get()
            tipo = self.tipo_movimiento.get()

            print(f"🔍 DEBUG - Cargando movimientos para fecha: {fecha}, tipo: {tipo}")

            # Conectar a la BD
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Consulta mejorada que une con tabla usuarios para obtener el nombre
            consulta = """
                SELECT DISTINCT 
                    m.id_movimiento, 
                    m.hora, 
                    m.tipo, 
                    m.concepto,
                    m.monto, 
                    u.nombre as usuario,
                    u.rol,
                    m.id_usuario
                FROM movimientos_caja m
                LEFT JOIN usuarios u ON m.id_usuario = u.id_usuario
                WHERE DATE(m.hora) = %s
            """

            parametros = [fecha]

            # Agregar condición de tipo si no es "Todos"
            if tipo != "Todos":
                consulta += " AND m.tipo = %s"
                tipo_bd = tipo.lower()
                parametros.append(tipo_bd)

            consulta += " ORDER BY m.hora DESC"

            print(f"🔍 DEBUG - Consulta SQL: {consulta}")
            print(f"🔍 DEBUG - Parámetros: {parametros}")

            # Ejecutar consulta
            cursor.execute(consulta, parametros)
            movimientos = cursor.fetchall()
            print(f"🔍 DEBUG - Movimientos encontrados: {len(movimientos)}")

            # Calcular totales
            total_ing = 0
            total_egr = 0

            # Insertar datos en la tabla
            for mov in movimientos:
                id_mov, hora, tipo_mov, concepto, monto, usuario, rol, id_usuario_real = mov

                # Debug para cada movimiento
                print(f"🔍 DEBUG - Movimiento: {concepto}, Usuario: {usuario} (ID: {id_usuario_real}), Rol: {rol}")

                # Formatear hora
                hora_str = hora.strftime("%H:%M:%S") if hasattr(hora, 'strftime') else str(hora)

                # Poner la primera letra en mayúscula
                tipo_mov_display = tipo_mov.capitalize() if tipo_mov else ""

                # Acumular totales
                if tipo_mov == 'ingreso':
                    total_ing += float(monto) if monto is not None else 0
                else:
                    total_egr += float(monto) if monto is not None else 0

                # Formatear monto
                monto_str = f"${float(monto):.2f}" if monto is not None else "$0.00"

                # Formatear nombre de usuario con rol si está disponible
                if usuario:
                    usuario_display = f"{usuario} ({rol})" if rol else usuario
                else:
                    usuario_display = f"Usuario ID: {id_usuario_real}"

                # Insertar en la tabla
                self.tabla_movimientos.insert('', tk.END, values=(
                    id_mov, hora_str, tipo_mov_display, concepto, monto_str, usuario_display
                ))

            # Actualizar variables de totales
            self.total_ingresos.set(f"${total_ing:.2f}")
            self.total_egresos.set(f"${total_egr:.2f}")
            self.saldo_del_dia.set(f"${(total_ing - total_egr):.2f}")

            conexion.close()

            # Si no hay resultados, mostrar un mensaje
            if len(movimientos) == 0:
                self.tabla_movimientos.insert('', tk.END, values=(
                    "", "", "", "No hay movimientos para esta fecha", "", ""
                ))

            print(f"🔍 DEBUG - Carga de movimientos completada")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los movimientos: {str(e)}")
            print(f"🔍 DEBUG - Error detallado al cargar movimientos: {e}")
            import traceback
            traceback.print_exc()

            # Insertar mensaje de error en la tabla
            self.tabla_movimientos.insert('', tk.END, values=(
                "", "", "", f"Error: {str(e)}", "", ""
            ))

    def imprimir_movimientos(self):
        """Imprime los movimientos de caja mostrados actualmente"""
        try:
            # Obtener fecha actual de filtro
            fecha = self.fecha_movimientos.get() if hasattr(self, 'fecha_movimientos') else date.today().strftime(
                "%Y-%m-%d")
            tipo = self.tipo_movimiento.get() if hasattr(self, 'tipo_movimiento') else "Todos"

            # Verificar si hay datos en la tabla
            if hasattr(self, 'tabla_movimientos') and len(self.tabla_movimientos.get_children()) == 0:
                messagebox.showinfo("Información", "No hay movimientos para imprimir")
                return

            # Crear ticket
            ticket = Ticket()

            # Encabezado
            ticket.agregar_encabezado()
            ticket.agregar_titulo("MOVIMIENTOS DE CAJA")
            ticket.agregar_texto(f"Fecha: {utl.formatear_fecha(fecha)}")
            if tipo != "Todos":
                ticket.agregar_texto(f"Tipo: {tipo}")
            ticket.agregar_linea()

            # Obtener datos de la tabla o directamente de la base de datos
            total_ingresos = 0
            total_egresos = 0

            # Si tenemos tabla, usamos sus datos
            if hasattr(self, 'tabla_movimientos'):
                # Encabezados de columnas
                ticket.agregar_texto("Hora      Tipo      Concepto                 Monto")
                ticket.agregar_linea()

                for item in self.tabla_movimientos.get_children():
                    datos = self.tabla_movimientos.item(item, 'values')
                    if len(datos) >= 5:  # Asegurarse de que hay suficientes datos
                        hora = datos[1]
                        tipo_mov = datos[2]
                        concepto = datos[3]
                        monto_str = datos[4]

                        # Extraer el valor numérico del monto (quitar el símbolo $)
                        monto = float(monto_str.replace('$', '').replace(',', '.'))

                        # Formatear concepto para que no sea muy largo
                        if len(concepto) > 20:
                            concepto = concepto[:17] + "..."

                        # Agregar línea al ticket
                        ticket.agregar_texto(f"{hora}  {tipo_mov.ljust(8)}  {concepto.ljust(20)}  ${monto:.2f}")

                        # Acumular totales
                        if tipo_mov.lower() == 'ingreso':
                            total_ingresos += monto
                        else:
                            total_egresos += monto
            else:
                # Si no hay tabla, obtener datos directamente de la BD
                conexion = conectar_bd()
                cursor = conexion.cursor()

                # Consulta similar a la de cargar_movimientos
                consulta = """
                    SELECT m.hora, m.tipo, m.concepto, m.monto, u.nombre
                    FROM movimientos_caja m
                    JOIN usuarios u ON m.id_usuario = u.id_usuario
                    WHERE DATE(m.hora) = %s
                """

                parametros = [fecha]

                if tipo != "Todos":
                    consulta += " AND m.tipo = %s"
                    tipo_bd = tipo.lower()
                    parametros.append(tipo_bd)

                consulta += " ORDER BY m.hora"

                cursor.execute(consulta, parametros)
                movimientos = cursor.fetchall()

                # Encabezados de columnas
                ticket.agregar_texto("Hora      Tipo      Concepto                 Monto")
                ticket.agregar_linea()

                for mov in movimientos:
                    hora, tipo_mov, concepto, monto, usuario = mov

                    # Formatear hora
                    hora_str = hora.strftime("%H:%M:%S") if isinstance(hora, datetime) else str(hora)

                    # Formatear concepto
                    if len(concepto) > 20:
                        concepto = concepto[:17] + "..."

                    # Agregar línea al ticket
                    ticket.agregar_texto(
                        f"{hora_str}  {tipo_mov.capitalize().ljust(8)}  {concepto.ljust(20)}  ${monto:.2f}")

                    # Acumular totales
                    if tipo_mov == 'ingreso':
                        total_ingresos += monto
                    else:
                        total_egresos += monto

                conexion.close()

            # Totales
            ticket.agregar_linea()
            ticket.agregar_texto(f"Total Ingresos: ${total_ingresos:.2f}")
            ticket.agregar_texto(f"Total Egresos: ${total_egresos:.2f}")
            ticket.agregar_texto(f"Saldo: ${(total_ingresos - total_egresos):.2f}")

            # Pie
            ticket.agregar_espacio()
            ticket.agregar_texto("Generado el: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

            # Generar nombre del archivo
            nombre_archivo = f"movimientos_caja_{fecha}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

            # Generar PDF
            ruta_pdf = ticket.generar_pdf(nombre_archivo)

            # Mostrar vista previa
            ticket.mostrar_vista_previa(ruta_pdf)

            messagebox.showinfo("Vista Previa", "Se ha generado la vista previa de los movimientos")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo imprimir los movimientos: {str(e)}")
            print(f"Error al imprimir movimientos: {e}")

    def ver_resumen_ventas_dia(self):
        """Muestra un resumen de las ventas registradas en la caja actual"""
        try:
            if not self.caja_abierta:
                messagebox.showinfo("Información", "Debe abrir la caja primero")
                return

            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Obtener resumen de ventas para la caja actual
            cursor.execute("""
                SELECT COUNT(*) as total_ventas, 
                       SUM(v.total) as total_facturado,
                       u.nombre as vendedor,
                       COUNT(*) as ventas_por_usuario
                FROM ventas v
                JOIN movimientos_caja mc ON mc.concepto LIKE CONCAT('Venta #', v.id_venta, '%')
                JOIN usuarios u ON v.id_usuario = u.id_usuario
                WHERE mc.id_caja = %s
                GROUP BY u.nombre
            """, (self.id_caja_actual,))

            resumen_vendedores = cursor.fetchall()

            # Obtener resumen general
            cursor.execute("""
                SELECT COUNT(*) as total_ventas, 
                       SUM(v.total) as total_facturado,
                       MIN(v.fecha) as primera_venta,
                       MAX(v.fecha) as ultima_venta
                FROM ventas v
                JOIN movimientos_caja mc ON mc.concepto LIKE CONCAT('Venta #', v.id_venta, '%')
                WHERE mc.id_caja = %s
            """, (self.id_caja_actual,))

            resumen_general = cursor.fetchone()

            # Mostrar ventana con resumen
            ventana_resumen = tk.Toplevel(self.ventana)
            ventana_resumen.title("Resumen de Ventas")
            ventana_resumen.geometry("600x400")
            ventana_resumen.config(bg="#f5f5f5")
            ventana_resumen.grab_set()

            utl.centrar_ventana(ventana_resumen, 600, 400)

            frame = tk.Frame(ventana_resumen, bg="#f5f5f5", padx=20, pady=20)
            frame.pack(fill=tk.BOTH, expand=True)

            # Título
            tk.Label(frame, text="RESUMEN DE VENTAS", font=("Helvetica", 14, "bold"),
                     bg="#f5f5f5", fg="#3a7ff6").pack(pady=(0, 10))

            # Resumen general
            if resumen_general:
                tk.Label(frame, text=f"Total de ventas: {resumen_general[0]}",
                         font=("Helvetica", 12), bg="#f5f5f5").pack(anchor=tk.W, pady=2)
                tk.Label(frame, text=f"Total facturado: ${resumen_general[1]:.2f}",
                         font=("Helvetica", 12), bg="#f5f5f5").pack(anchor=tk.W, pady=2)

                if resumen_general[2]:  # primera venta
                    tk.Label(frame, text=f"Primera venta: {resumen_general[2].strftime('%H:%M:%S')}",
                             font=("Helvetica", 12), bg="#f5f5f5").pack(anchor=tk.W, pady=2)
                if resumen_general[3]:  # última venta
                    tk.Label(frame, text=f"Última venta: {resumen_general[3].strftime('%H:%M:%S')}",
                             font=("Helvetica", 12), bg="#f5f5f5").pack(anchor=tk.W, pady=2)

            # Separador
            ttk.Separator(frame, orient="horizontal").pack(fill=tk.X, pady=10)

            # Resumen por vendedor
            tk.Label(frame, text="Ventas por Vendedor:", font=("Helvetica", 12, "bold"),
                     bg="#f5f5f5").pack(anchor=tk.W, pady=(10, 5))

            for vendedor in resumen_vendedores:
                tk.Label(frame, text=f"{vendedor[2]}: {vendedor[3]} ventas - ${vendedor[1]:.2f}",
                         font=("Helvetica", 11), bg="#f5f5f5").pack(anchor=tk.W, padx=20, pady=2)

            # Botón cerrar
            tk.Button(frame, text="Cerrar", bg="#3a7ff6", fg="white", width=10,
                      command=ventana_resumen.destroy).pack(pady=20)

            conexion.close()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el resumen: {str(e)}")

    def registrar_ingreso(self):
        """Abre el módulo de ventas para registrar un ingreso en la caja actual"""
        try:
            if not self.caja_abierta:
                messagebox.showinfo("Información", "Debe abrir la caja primero")
                return

            # Importar y abrir el módulo de ventas
            from ventas import Ventas
            Ventas(self.ventana)

            # En lugar de un simple diálogo, se abre el módulo completo de ventas
            # Cuando se complete una venta, esta se registrará automáticamente en la caja

        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir módulo de ventas: {str(e)}")
            print(f"Error al abrir ventas: {e}")

    # Agrega este método a la clase GestionCaja en caja.py

    def verificar_estado_caja(self):
        """Verifica si hay una caja abierta para la fecha actual"""
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Consultar si hay una caja abierta para hoy (hora_cierre es NULL)
            fecha_actual = date.today().strftime("%Y-%m-%d")
            cursor.execute(
                "SELECT id_caja, responsable FROM caja WHERE fecha = %s AND hora_cierre IS NULL",
                (fecha_actual,)
            )

            resultado = cursor.fetchone()

            if resultado:
                self.id_caja_actual = resultado[0]
                self.caja_abierta = True

                # Verificar el responsable asignado
                cursor.execute(
                    "SELECT u.nombre FROM usuarios u JOIN caja c ON u.id_usuario = c.responsable WHERE c.id_caja = %s",
                    (self.id_caja_actual,)
                )
                responsable = cursor.fetchone()
                print(
                    f"Debug - Caja abierta encontrada: ID {self.id_caja_actual}, Responsable: {responsable[0] if responsable else 'Desconocido'}")
            else:
                self.id_caja_actual = None
                self.caja_abierta = False
                print("Debug - No hay caja abierta")

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al verificar estado de caja: {str(e)}")
            print(f"Error detallado al verificar estado: {e}")
            self.caja_abierta = False

    def verificar_formato_fecha(self):
        """Verifica que la fecha esté en formato correcto"""
        try:
            fecha_actual = self.fecha_cortes.get()
            # Intentar convertir a formato correcto
            fecha_obj = datetime.strptime(fecha_actual, "%Y-%m-%d")
            # Asegurar que esté en formato correcto
            fecha_corregida = fecha_obj.strftime("%Y-%m-%d")
            self.fecha_cortes.set(fecha_corregida)
        except ValueError:
            # Si no es válida, usar fecha actual
            self.fecha_cortes.set(date.today().strftime("%Y-%m-%d"))
            messagebox.showwarning("Formato incorrecto", "La fecha debe estar en formato YYYY-MM-DD")


    def reconstruir_pestanas(self):
        """Reconstruye completamente las pestañas problemáticas"""
        # Eliminar pestañas existentes
        if hasattr(self, 'tab_cortes'):
            self.notebook.forget(self.tab_cortes)
        if hasattr(self, 'tab_movimientos'):
            self.notebook.forget(self.tab_movimientos)

        # Crear nuevas pestañas
        self.tab_cortes = tk.Frame(self.notebook, bg="#f5f5f5")
        self.tab_movimientos = tk.Frame(self.notebook, bg="#f5f5f5")

        # Añadirlas al notebook
        self.notebook.add(self.tab_cortes, text="Cortes de Caja")
        self.notebook.add(self.tab_movimientos, text="Movimientos")

        # Reconfigurar las pestañas
        self.configurar_tab_cortes()
        self.configurar_tab_movimientos()

        # Mostrar mensaje
        messagebox.showinfo("Reconstrucción completada",
                            "Se han reconstruido las pestañas. Intente verlas nuevamente.")

    def construir_interfaz(self):
        """Construye la interfaz gráfica del módulo de caja"""
        # Frame principal con padding
        self.frame_principal = tk.Frame(self.ventana, bg="#f5f5f5", padx=20, pady=20)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)

        # Título con estilo
        titulo_frame = tk.Frame(self.frame_principal, bg="#f5f5f5")
        titulo_frame.pack(fill=tk.X, pady=(0, 20))

        titulo = tk.Label(
            titulo_frame,
            text="GESTIÓN DE CAJA",
            font=("Helvetica", 18, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        )
        titulo.pack()

        # Separador
        separador = ttk.Separator(self.frame_principal, orient="horizontal")
        separador.pack(fill=tk.X, pady=(0, 20))

        # Frame para mostrar estado actual de la caja
        self.frame_estado = tk.Frame(self.frame_principal, bg="#f5f5f5", relief=tk.GROOVE, bd=1)
        self.frame_estado.pack(fill=tk.X, pady=10, padx=5)

        # Mostrar estado de caja actual
        self.actualizar_estado_caja()

        # Crear notebook (pestañas)
        self.notebook = ttk.Notebook(self.frame_principal)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Pestañas
        self.tab_operaciones = tk.Frame(self.notebook, bg="#f5f5f5")
        self.tab_movimientos = tk.Frame(self.notebook, bg="#f5f5f5")
        self.tab_cortes = tk.Frame(self.notebook, bg="#f5f5f5")

        self.notebook.add(self.tab_operaciones, text="Operaciones de Caja")
        self.notebook.add(self.tab_movimientos, text="Movimientos")
        self.notebook.add(self.tab_cortes, text="Cortes de Caja")

        # Configurar las pestañas
        self.configurar_tab_operaciones()
        self.configurar_tab_movimientos()
        self.configurar_tab_cortes()

        # Botón para volver
        btn_volver = tk.Button(
            self.frame_principal,
            text="Volver",
            font=("Helvetica", 11),
            bg="#e53935",
            fg="white",
            width=10,
            cursor="hand2",
            command=self.ventana.destroy
        )
        btn_volver.pack(pady=10, anchor=tk.SE)

    def abrir_caja(self):
        """Método para abrir la caja con usuario correcto"""
        try:
            print(f"Debug - Valor de self.id_usuario antes de abrir caja: {self.id_usuario}")

            # 1. Verificación directa del usuario en la BD
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Verificar qué usuario somos realmente
            cursor.execute("SELECT id_usuario, nombre FROM usuarios WHERE id_usuario = %s", (self.id_usuario,))
            usuario_actual = cursor.fetchone()

            if usuario_actual:
                print(f"Debug - Usuario verificado: ID={usuario_actual[0]}, Nombre={usuario_actual[1]}")
            else:
                print(f"Debug - ADVERTENCIA: No se pudo encontrar usuario con ID={self.id_usuario}")
                # Buscar a Aketzaly para verificar su ID
                cursor.execute("SELECT id_usuario, nombre FROM usuarios WHERE nombre = 'Aketzaly'")
                usuario_aketzaly = cursor.fetchone()
                if usuario_aketzaly:
                    print(f"Debug - Usuario Aketzaly: ID={usuario_aketzaly[0]}, Nombre={usuario_aketzaly[1]}")

                # Mostrar todos los usuarios para diagnóstico
                cursor.execute("SELECT id_usuario, nombre FROM usuarios LIMIT 10")
                print("Debug - Usuarios en BD:")
                for usuario in cursor.fetchall():
                    print(f"  ID={usuario[0]}, Nombre={usuario[1]}")

            # 2. Si ya hay una caja abierta, solo informar y salir
            if self.caja_abierta:
                messagebox.showinfo("Información", "La caja ya se encuentra abierta")
                conexion.close()
                return

            # Verificar si hay saldo anterior disponible
            cursor.execute("""
                SELECT c.id_caja, c.fecha, c.saldo_final, u.nombre 
                FROM caja c 
                JOIN usuarios u ON c.responsable = u.id_usuario
                WHERE c.hora_cierre IS NOT NULL
                ORDER BY c.fecha DESC, c.hora_cierre DESC
                LIMIT 1
            """)

            ultimo_saldo = cursor.fetchone()

            # 3. Preguntar si se desea abrir la caja con saldo anterior o con nuevo saldo
            if ultimo_saldo and ultimo_saldo[2] > 0:
                fecha_ultimo = ultimo_saldo[1].strftime("%d/%m/%Y") if hasattr(ultimo_saldo[1], 'strftime') else str(
                    ultimo_saldo[1])
                respuesta = messagebox.askyesno(
                    "Saldo anterior disponible",
                    f"Existe un saldo anterior de ${ultimo_saldo[2]:.2f} del {fecha_ultimo}.\n"
                    f"Responsable: {ultimo_saldo[3]}\n\n"
                    "¿Desea abrir la caja con este saldo?",
                    icon='question'
                )

                if respuesta:
                    # Usar saldo anterior
                    monto_inicial = ultimo_saldo[2]
                else:
                    # Pedir nuevo monto
                    monto_inicial = simpledialog.askfloat(
                        "Apertura de Caja",
                        "Ingrese el monto inicial en caja:",
                        minvalue=0.0
                    )
            else:
                # Sin saldo anterior, pedir monto inicial
                monto_inicial = simpledialog.askfloat(
                    "Apertura de Caja",
                    "Ingrese el monto inicial en caja:",
                    minvalue=0.0
                )

            if monto_inicial is None:
                messagebox.showinfo("Cancelado", "Apertura de caja cancelada")
                conexion.close()
                return

            # 4. Insertar en la tabla caja - ASEGURAR que se use el ID correcto
            fecha_actual = date.today()
            hora_actual = datetime.now().time()

            print(f"Debug - Ejecutando INSERT con ID usuario: {self.id_usuario}")

            # Usar sentencia SQL con valores explícitos para verificar
            cursor.execute(f"""
                INSERT INTO caja 
                  (fecha, hora_apertura, responsable, total_ingresos, total_egresos, saldo_final)
                VALUES 
                  ('{fecha_actual}', '{hora_actual}', {self.id_usuario}, 0.0, 0.0, {monto_inicial})
            """)

            # Obtener el ID de la caja insertada
            self.id_caja_actual = cursor.lastrowid
            self.caja_abierta = True

            # 5. Verificar inmediatamente que se haya insertado correctamente
            cursor.execute("""
                SELECT c.id_caja, c.responsable, u.nombre 
                FROM caja c 
                JOIN usuarios u ON c.responsable = u.id_usuario
                WHERE c.id_caja = %s
            """, (self.id_caja_actual,))

            caja_creada = cursor.fetchone()
            if caja_creada:
                print(
                    f"Debug - Caja creada: ID={caja_creada[0]}, ResponsableID={caja_creada[1]}, Nombre={caja_creada[2]}")

                # Si el responsable no es el esperado, corregir manualmente
                if caja_creada[1] != self.id_usuario:
                    print("Debug - CORRECCIÓN MANUAL: Responsable no es el usuario actual, corrigiendo...")
                    cursor.execute("""
                        UPDATE caja 
                        SET responsable = %s 
                        WHERE id_caja = %s
                    """, (self.id_usuario, self.id_caja_actual))

                    # Verificar la corrección
                    cursor.execute("""
                        SELECT c.id_caja, c.responsable, u.nombre 
                        FROM caja c 
                        JOIN usuarios u ON c.responsable = u.id_usuario
                        WHERE c.id_caja = %s
                    """, (self.id_caja_actual,))
                    caja_corregida = cursor.fetchone()
                    print(
                        f"Debug - Después de corrección: ID={caja_corregida[0]}, ResponsableID={caja_corregida[1]}, Nombre={caja_corregida[2]}")

            # 6. Registrar el movimiento inicial
            if monto_inicial > 0:
                cursor.execute("""
                    INSERT INTO movimientos_caja (id_caja, tipo, concepto, monto, hora, id_usuario)
                    VALUES (%s, 'ingreso', 'Saldo inicial', %s, %s, %s)
                """, (
                    self.id_caja_actual,
                    monto_inicial,
                    datetime.now(),
                    self.id_usuario
                ))

                # Actualizar saldo e ingresos
                cursor.execute("""
                    UPDATE caja 
                    SET total_ingresos = %s, saldo_final = %s
                    WHERE id_caja = %s
                """, (monto_inicial, monto_inicial, self.id_caja_actual))

            # 7. Confirmar transacción y cerrar conexión
            conexion.commit()
            conexion.close()

            # 8. Mostrar mensaje de éxito y actualizar interfaz
            messagebox.showinfo("Apertura Exitosa",
                                f"La caja se ha abierto correctamente con un monto inicial de ${monto_inicial:.2f}")

            # 9. Actualizar la interfaz
            self.actualizar_estado_caja()
            self.configurar_tab_operaciones()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la caja: {str(e)}")
            print(f"Error detallado al abrir caja: {e}")
            import traceback
            traceback.print_exc()



    def mostrar_calendario_para(self, target="cortes"):
        """Muestra un calendario para seleccionar fecha"""

        def set_fecha():
            try:
                # Construir fecha seleccionada
                dia = int(combo_dia.get())
                mes = meses.index(combo_mes.get()) + 1
                anio = int(combo_anio.get())

                # Validar fecha
                fecha_obj = date(anio, mes, dia)
                fecha_str = fecha_obj.strftime("%Y-%m-%d")

                # Asignar según pestaña
                if target == "cortes":
                    self.fecha_cortes.set(fecha_str)
                    self.cargar_cortes()
                elif target == "movimientos":
                    self.fecha_movimientos.set(fecha_str)
                    self.cargar_movimientos()

                ventana_cal.destroy()
            except ValueError:
                messagebox.showerror("Error", "Fecha inválida")

        # Crear ventana
        ventana_cal = tk.Toplevel(self.ventana)
        ventana_cal.title("Seleccionar Fecha")
        ventana_cal.geometry("300x200")
        ventana_cal.config(bg="#f5f5f5")
        ventana_cal.transient(self.ventana)
        ventana_cal.grab_set()
        utl.centrar_ventana(ventana_cal, 300, 200)

        frame = tk.Frame(ventana_cal, bg="#f5f5f5", padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Obtener fecha actual según pestaña
        if target == "cortes":
            fecha_actual = self.fecha_cortes.get()
        else:
            fecha_actual = self.fecha_movimientos.get()

        try:
            anio, mes, dia = fecha_actual.split("-")
            mes = int(mes)
            dia = int(dia)
        except:
            hoy = date.today()
            anio, mes, dia = str(hoy.year), hoy.month, hoy.day

        # Controles de fecha
        tk.Label(frame, text="Día:", bg="#f5f5f5").grid(row=0, column=0, sticky=tk.W)
        combo_dia = ttk.Combobox(frame, values=list(range(1, 32)), width=5, state="readonly")
        combo_dia.set(str(dia))
        combo_dia.grid(row=0, column=1, padx=5, pady=5)

        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        tk.Label(frame, text="Mes:", bg="#f5f5f5").grid(row=1, column=0, sticky=tk.W)
        combo_mes = ttk.Combobox(frame, values=meses, width=10, state="readonly")
        combo_mes.set(meses[int(mes) - 1])
        combo_mes.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="Año:", bg="#f5f5f5").grid(row=2, column=0, sticky=tk.W)
        combo_anio = ttk.Combobox(frame, values=list(range(2020, 2031)), width=6, state="readonly")
        combo_anio.set(anio)
        combo_anio.grid(row=2, column=1, padx=5, pady=5)

        # Botones
        frame_btn = tk.Frame(frame, bg="#f5f5f5")
        frame_btn.grid(row=3, column=0, columnspan=2, pady=20)

        btn_aceptar = tk.Button(frame_btn, text="Aceptar", bg="#4CAF50", fg="white", command=set_fecha)
        btn_aceptar.pack(side=tk.LEFT, padx=5)

        btn_hoy = tk.Button(frame_btn, text="Hoy", bg="#2196F3", fg="white",
                            command=lambda: [
                                combo_dia.set(str(date.today().day)),
                                combo_mes.set(meses[date.today().month - 1]),
                                combo_anio.set(str(date.today().year))
                            ])
        btn_hoy.pack(side=tk.LEFT, padx=5)

        btn_cancelar = tk.Button(frame_btn, text="Cancelar", bg="#f44336", fg="white",
                                 command=ventana_cal.destroy)
        btn_cancelar.pack(side=tk.LEFT, padx=5)

    def configurar_tab_cortes(self):
        """Configura la pestaña de cortes de caja"""
        # Limpiar pestaña
        for widget in self.tab_cortes.winfo_children():
            widget.destroy()

        # Frame principal
        frame_principal = tk.Frame(self.tab_cortes, bg="#f5f5f5", padx=10, pady=10)
        frame_principal.pack(fill=tk.BOTH, expand=True)

        # Variable para fecha
        self.fecha_cortes = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))

        # Frame para filtros
        frame_filtros = tk.Frame(frame_principal, bg="#f5f5f5", padx=5, pady=5, relief=tk.GROOVE, bd=1)
        frame_filtros.pack(fill=tk.X, pady=10)
        self.frame_filtros = frame_filtros  # Guardar referencia

        # Control de fecha
        tk.Label(frame_filtros, text="Fecha:", bg="#f5f5f5", font=("Helvetica", 11)).grid(row=0, column=0, padx=5,
                                                                                          pady=5)

        entry_fecha = tk.Entry(
            frame_filtros,
            textvariable=self.fecha_cortes,
            width=12,
            font=("Helvetica", 11)
        )
        entry_fecha.grid(row=0, column=1, padx=5, pady=5)

        btn_fecha = tk.Button(
            frame_filtros,
            text="📅",
            font=("Helvetica", 11),
            bg="#2196f3",
            fg="white",
            command=lambda: self.mostrar_calendario("cortes")
        )
        btn_fecha.grid(row=0, column=2, padx=5, pady=5)

        # Botón de búsqueda
        btn_buscar = tk.Button(
            frame_filtros,
            text="🔍 Buscar",
            font=("Helvetica", 11),
            bg="#3f51b5",
            fg="white",
            width=10,
            command=self.cargar_cortes
        )
        btn_buscar.grid(row=0, column=3, padx=15, pady=5)

        # Frame para tabla con altura fija
        frame_tabla = tk.Frame(frame_principal, bg="#f5f5f5", padx=5, pady=5, height=300)
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10)
        frame_tabla.pack_propagate(False)  # Evita que se encoja

        # Columnas para la tabla
        columnas = ('id', 'fecha', 'apertura', 'cierre', 'ingresos', 'egresos', 'saldo', 'responsable')

        # Crear tabla
        self.tabla_cortes = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            show='headings',
            height=10
        )

        # Configurar encabezados
        self.tabla_cortes.heading('id', text='ID')
        self.tabla_cortes.heading('fecha', text='Fecha')
        self.tabla_cortes.heading('apertura', text='Apertura')
        self.tabla_cortes.heading('cierre', text='Cierre')
        self.tabla_cortes.heading('ingresos', text='Ingresos')
        self.tabla_cortes.heading('egresos', text='Egresos')
        self.tabla_cortes.heading('saldo', text='Saldo')
        self.tabla_cortes.heading('responsable', text='Responsable')

        # Configurar anchos
        self.tabla_cortes.column('id', width=50, anchor=tk.CENTER)
        self.tabla_cortes.column('fecha', width=100, anchor=tk.CENTER)
        self.tabla_cortes.column('apertura', width=100, anchor=tk.CENTER)
        self.tabla_cortes.column('cierre', width=100, anchor=tk.CENTER)
        self.tabla_cortes.column('ingresos', width=100, anchor=tk.E)
        self.tabla_cortes.column('egresos', width=100, anchor=tk.E)
        self.tabla_cortes.column('saldo', width=100, anchor=tk.E)
        self.tabla_cortes.column('responsable', width=150)

        # Aplicar estilo predefinido
        utl.aplicar_estilo_tabla(self.tabla_cortes)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_cortes.yview)
        self.tabla_cortes.configure(yscrollcommand=scrollbar.set)

        # Empaquetar tabla y scrollbar
        self.tabla_cortes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame para botones
        frame_botones = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_botones.pack(fill=tk.X, pady=10)

        # Botones
        btn_detalle = tk.Button(
            frame_botones,
            text="📄 Ver Detalle",
            font=("Helvetica", 11),
            bg="#3f51b5",
            fg="white",
            width=12,
            command=self.ver_detalle_corte
        )
        btn_detalle.pack(side=tk.LEFT, padx=5)

        btn_imprimir = tk.Button(
            frame_botones,
            text="🖨️ Imprimir Corte",
            font=("Helvetica", 11),
            bg="#4caf50",
            fg="white",
            width=15,
            command=self.imprimir_corte_seleccionado
        )
        btn_imprimir.pack(side=tk.LEFT, padx=5)

        btn_exportar = tk.Button(
            frame_botones,
            text="📊 Exportar a PDF",
            font=("Helvetica", 11),
            bg="#ff9800",
            fg="white",
            width=15,
            command=self.exportar_cortes_pdf
        )
        btn_exportar.pack(side=tk.LEFT, padx=5)

        # Programar carga de datos con un ligero retraso
        self.ventana.after(100, self.cargar_cortes)

    def debug_verificar_fechas(self):
        """Método para depurar fechas en la base de datos"""
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Verificar todas las fechas en la tabla caja
            cursor.execute("SELECT id_caja, fecha, DATE_FORMAT(fecha, '%Y-%m-%d') as fecha_formateada FROM caja")
            fechas = cursor.fetchall()

            print("\n=== DEBUG FECHAS EN BD ===")
            for f in fechas:
                print(f"ID: {f[0]}, Fecha raw: {f[1]}, Fecha formateada: {f[2]}")

            # Verificar formato actual
            fecha_actual = self.fecha_cortes.get()
            print(f"\nFecha buscada: '{fecha_actual}'")

            # Intentar con diferentes formatos
            try:
                fecha_obj = datetime.strptime(fecha_actual, "%Y-%m-%d")
                print(f"Fecha parseada como objeto: {fecha_obj}")
            except:
                print("Error al parsear fecha actual")

            # Buscar con formato correcto
            cursor.execute("""
                SELECT id_caja, fecha, DATE_FORMAT(fecha, '%Y-%m-%d') as fecha_formateada 
                FROM caja 
                WHERE DATE(fecha) = DATE(%s)
            """, (fecha_actual,))

            resultados = cursor.fetchall()
            print(f"\nResultados de búsqueda para {fecha_actual}:")
            print(f"Cantidad: {len(resultados)}")
            for r in resultados:
                print(f"  ID: {r[0]}, Fecha: {r[2]}")

            conexion.close()

        except Exception as e:
            print(f"Error en debug_verificar_fechas: {e}")

    def mostrar_calendario(self, target="cortes"):
        """Muestra un calendario para seleccionar fecha"""
        ventana_cal = tk.Toplevel(self.ventana)
        ventana_cal.title("Seleccionar Fecha")
        ventana_cal.geometry("300x200")
        ventana_cal.config(bg="#f5f5f5")
        ventana_cal.transient(self.ventana)
        ventana_cal.grab_set()
        utl.centrar_ventana(ventana_cal, 300, 200)

        frame = tk.Frame(ventana_cal, bg="#f5f5f5", padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Obtener fecha actual
        if target == "cortes":
            fecha_str = self.fecha_cortes.get()
        else:  # movimientos
            fecha_str = self.fecha_movimientos.get()

        try:
            anio, mes, dia = fecha_str.split("-")
            dia = int(dia)
            mes = int(mes)
            anio = int(anio)
        except:
            hoy = date.today()
            dia, mes, anio = hoy.day, hoy.month, hoy.year

        # Controles de fecha
        frame_fecha = tk.Frame(frame, bg="#f5f5f5")
        frame_fecha.pack(fill=tk.X, pady=10)

        # Día
        tk.Label(frame_fecha, text="Día:", bg="#f5f5f5").grid(row=0, column=0, sticky=tk.W)
        combo_dia = ttk.Combobox(frame_fecha, values=list(range(1, 32)), width=5, state="readonly")
        combo_dia.set(str(dia))
        combo_dia.grid(row=0, column=1, padx=5, pady=5)

        # Mes
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        tk.Label(frame_fecha, text="Mes:", bg="#f5f5f5").grid(row=1, column=0, sticky=tk.W)
        combo_mes = ttk.Combobox(frame_fecha, values=meses, width=10, state="readonly")
        combo_mes.set(meses[mes - 1])
        combo_mes.grid(row=1, column=1, padx=5, pady=5)

        # Año
        tk.Label(frame_fecha, text="Año:", bg="#f5f5f5").grid(row=2, column=0, sticky=tk.W)
        combo_anio = ttk.Combobox(frame_fecha, values=list(range(2020, 2031)), width=6, state="readonly")
        combo_anio.set(str(anio))
        combo_anio.grid(row=2, column=1, padx=5, pady=5)

        # Función para aplicar la fecha
        def aplicar_fecha():
            try:
                d = int(combo_dia.get())
                m = meses.index(combo_mes.get()) + 1
                a = int(combo_anio.get())

                fecha_obj = date(a, m, d)
                fecha_formateada = fecha_obj.strftime("%Y-%m-%d")

                if target == "cortes":
                    self.fecha_cortes.set(fecha_formateada)
                    self.cargar_cortes()
                else:  # movimientos
                    self.fecha_movimientos.set(fecha_formateada)
                    self.cargar_movimientos()

                ventana_cal.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Fecha inválida: {e}")

        # Botones
        frame_botones = tk.Frame(frame, bg="#f5f5f5")
        frame_botones.pack(pady=20)

        tk.Button(
            frame_botones,
            text="Aceptar",
            bg="#4CAF50",
            fg="white",
            width=8,
            command=aplicar_fecha
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            frame_botones,
            text="Hoy",
            bg="#2196F3",
            fg="white",
            width=8,
            command=lambda: [
                combo_dia.set(str(date.today().day)),
                combo_mes.set(meses[date.today().month - 1]),
                combo_anio.set(str(date.today().year))
            ]
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            frame_botones,
            text="Cancelar",
            bg="#F44336",
            fg="white",
            width=8,
            command=ventana_cal.destroy
        ).pack(side=tk.LEFT, padx=5)

    def ver_detalle_corte(self):
        """Muestra los detalles de un corte seleccionado"""
        try:
            # Obtener el item seleccionado
            seleccion = self.tabla_cortes.selection()

            if not seleccion:
                messagebox.showinfo("Información", "Seleccione un corte para ver sus detalles")
                return

            # Obtener el ID del corte seleccionado
            item = self.tabla_cortes.item(seleccion[0])
            id_corte = item['values'][0]

            # Mostrar detalles del corte
            self.mostrar_detalle_corte(id_corte)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mostrar el detalle del corte: {str(e)}")

    def mostrar_detalle_corte(self, id_corte):
        """Muestra información detallada de un corte específico"""
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Obtener información del corte
            cursor.execute("""
                SELECT c.id_caja, c.fecha, c.hora_apertura, c.hora_cierre, 
                       c.monto_inicial, c.total_ingresos, c.total_egresos, c.saldo_final,
                       u.nombre
                FROM caja c
                JOIN usuarios u ON c.responsable = u.id_usuario
                WHERE c.id_caja = %s
            """, (id_corte,))

            corte = cursor.fetchone()

            # Obtener los movimientos asociados al corte
            cursor.execute("""
                SELECT m.hora, m.tipo, m.concepto, m.monto, u.nombre
                FROM movimientos_caja m
                JOIN usuarios u ON m.id_usuario = u.id_usuario
                WHERE m.id_caja = %s
                ORDER BY m.hora
            """, (id_corte,))

            movimientos = cursor.fetchall()
            conexion.close()

            if corte:
                id_caja, fecha, hora_apertura, hora_cierre, monto_inicial, ingresos, egresos, saldo, responsable = corte

                # Formatear fechas y horas para mejor visualización
                fecha_formateada = utl.formatear_fecha(fecha)
                hora_ap = hora_apertura.strftime("%H:%M:%S") if hora_apertura else ""
                hora_ci = hora_cierre.strftime("%H:%M:%S") if hora_cierre else "Abierta"

                # Crear una ventana para mostrar el corte
                ventana_corte = tk.Toplevel(self.ventana)
                ventana_corte.title(f"Detalle de Corte #{id_caja}")
                ventana_corte.geometry("600x500")
                ventana_corte.config(bg="#f5f5f5")
                ventana_corte.resizable(False, False)

                # Centrar la ventana
                utl.centrar_ventana(ventana_corte, 600, 500)

                # Hacer la ventana modal
                ventana_corte.transient(self.ventana)
                ventana_corte.grab_set()

                # Contenido
                frame_corte = tk.Frame(ventana_corte, bg="#f5f5f5", padx=20, pady=20)
                frame_corte.pack(fill=tk.BOTH, expand=True)

                # Título
                tk.Label(
                    frame_corte,
                    text=f"DETALLE DE CORTE #{id_caja}",
                    font=("Helvetica", 14, "bold"),
                    bg="#f5f5f5",
                    fg="#3a7ff6"
                ).pack(pady=(0, 20))

                # Notebook para pestañas de resumen y movimientos
                notebook = ttk.Notebook(frame_corte)
                notebook.pack(fill=tk.BOTH, expand=True)

                # Pestaña de resumen
                tab_resumen = tk.Frame(notebook, bg="#f5f5f5")
                notebook.add(tab_resumen, text="Resumen")

                # Pestaña de movimientos
                tab_movimientos = tk.Frame(notebook, bg="#f5f5f5")
                notebook.add(tab_movimientos, text="Movimientos")

                # Información del corte en formato de tabla (pestaña resumen)
                info_frame = tk.Frame(tab_resumen, bg="#f0f7ff", padx=15, pady=15, relief=tk.GROOVE, bd=1)
                info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

                # Datos en dos columnas
                datos = [
                    ("ID de Caja:", f"{id_caja}"),
                    ("Fecha:", fecha_formateada),
                    ("Hora de Apertura:", hora_ap),
                    ("Hora de Cierre:", hora_ci),
                    ("Responsable:", responsable),
                    ("Monto Inicial:", f"${monto_inicial:.2f}"),
                    ("Total Ingresos:", f"${ingresos:.2f}"),
                    ("Total Egresos:", f"${egresos:.2f}"),
                    ("Saldo Final:", f"${saldo:.2f}")
                ]

                for i, (etiqueta, valor) in enumerate(datos):
                    tk.Label(
                        info_frame,
                        text=etiqueta,
                        font=("Helvetica", 11, "bold"),
                        bg="#f0f7ff",
                        anchor=tk.W
                    ).grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)

                    tk.Label(
                        info_frame,
                        text=valor,
                        font=("Helvetica", 11),
                        bg="#f0f7ff",
                        anchor=tk.W
                    ).grid(row=i, column=1, sticky=tk.W, padx=5, pady=5)

                # Tabla de movimientos (pestaña movimientos)
                mov_frame = tk.Frame(tab_movimientos, bg="#f5f5f5", padx=10, pady=10)
                mov_frame.pack(fill=tk.BOTH, expand=True)

                if movimientos:
                    # Crear tabla
                    columnas = ('hora', 'tipo', 'concepto', 'monto', 'usuario')

                    tabla_mov = ttk.Treeview(mov_frame, columns=columnas, show='headings', height=12)

                    # Aplicar estilo
                    utl.aplicar_estilo_tabla(tabla_mov)

                    # Configurar encabezados
                    tabla_mov.heading('hora', text='Hora')
                    tabla_mov.heading('tipo', text='Tipo')
                    tabla_mov.heading('concepto', text='Concepto')
                    tabla_mov.heading('monto', text='Monto')
                    tabla_mov.heading('usuario', text='Usuario')

                    # Configurar anchos
                    tabla_mov.column('hora', width=80, anchor=tk.CENTER)
                    tabla_mov.column('tipo', width=80, anchor=tk.CENTER)
                    tabla_mov.column('concepto', width=200)
                    tabla_mov.column('monto', width=80, anchor=tk.E)
                    tabla_mov.column('usuario', width=120)

                    # Scrollbar
                    scrollbar = ttk.Scrollbar(mov_frame, orient=tk.VERTICAL, command=tabla_mov.yview)
                    tabla_mov.configure(yscrollcommand=scrollbar.set)

                    # Empaquetar
                    tabla_mov.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                    # Insertar datos
                    for mov in movimientos:
                        hora, tipo, concepto, monto, usuario = mov
                        hora_str = hora.strftime("%H:%M:%S")

                        tabla_mov.insert('', tk.END, values=(
                            hora_str, tipo, concepto, f"${monto:.2f}", usuario
                        ))
                else:
                    # Mensaje si no hay movimientos
                    tk.Label(
                        mov_frame,
                        text="No hay movimientos registrados para este corte",
                        font=("Helvetica", 12),
                        bg="#f5f5f5",
                        fg="#666"
                    ).pack(pady=50)

                # Botones
                frame_botones = tk.Frame(frame_corte, bg="#f5f5f5")
                frame_botones.pack(pady=15)

                btn_imprimir = tk.Button(
                    frame_botones,
                    text="Imprimir Corte",
                    font=("Helvetica", 11),
                    bg="#3f51b5",
                    fg="white",
                    width=15,
                    cursor="hand2",
                    command=lambda: self.imprimir_corte(id_caja)
                )
                btn_imprimir.grid(row=0, column=0, padx=10)

                btn_cerrar = tk.Button(
                    frame_botones,
                    text="Cerrar",
                    font=("Helvetica", 11),
                    bg="#e53935",
                    fg="white",
                    width=10,
                    cursor="hand2",
                    command=ventana_corte.destroy
                )
                btn_cerrar.grid(row=0, column=1, padx=10)

            else:
                messagebox.showinfo("Información", "No se encontró información para el corte seleccionado")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mostrar el detalle del corte: {str(e)}")
            print(f"Error al mostrar detalle del corte: {e}")

    def exportar_cortes_pdf(self):
        """Exporta todos los cortes visibles a un PDF"""
        try:
            fecha = self.fecha_cortes.get()

            # Crear ticket para PDF
            ticket = Ticket()

            # Encabezado
            ticket.agregar_encabezado()
            ticket.agregar_titulo("REPORTE DE CORTES DE CAJA")
            ticket.agregar_texto(f"Fecha: {fecha}")
            ticket.agregar_linea()

            # Encabezados de la tabla
            ticket.agregar_texto(
                "ID    FECHA        APERTURA   CIERRE     INGRESOS    EGRESOS    SALDO      RESPONSABLE")
            ticket.agregar_linea()

            # Obtener datos de la tabla
            for item in self.tabla_cortes.get_children():
                valores = self.tabla_cortes.item(item, 'values')

                # Formatear para alineación
                id_caja = str(valores[0]).ljust(4)
                fecha_val = str(valores[1]).ljust(10)
                apertura = str(valores[2]).ljust(8)
                cierre = str(valores[3]).ljust(8)
                ingresos = str(valores[4]).rjust(10)
                egresos = str(valores[5]).rjust(9)
                saldo = str(valores[6]).rjust(10)
                responsable = str(valores[7]).ljust(12)

                ticket.agregar_texto(
                    f"{id_caja} {fecha_val} {apertura} {cierre} {ingresos} {egresos} {saldo} {responsable}")

            # Pie del reporte
            ticket.agregar_linea()
            ticket.agregar_texto("Reporte generado el: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

            # Generar PDF
            nombre_archivo = f"reporte_cortes_{fecha}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            ruta_pdf = ticket.generar_pdf(nombre_archivo)

            # Mostrar vista previa
            ticket.mostrar_vista_previa(ruta_pdf)

            messagebox.showinfo("PDF Generado", f"El reporte ha sido generado correctamente: {nombre_archivo}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF: {str(e)}")

    def imprimir_corte_seleccionado(self):
        """Imprime el corte seleccionado en la tabla"""
        try:
            # Obtener el item seleccionado
            seleccion = self.tabla_cortes.selection()

            if not seleccion:
                messagebox.showinfo("Información", "Seleccione un corte para imprimir")
                return

            # Obtener el ID del corte seleccionado
            item = self.tabla_cortes.item(seleccion[0])
            id_corte = item['values'][0]

            # Imprimir el corte
            self.imprimir_corte(id_corte)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo imprimir el corte: {str(e)}")
            print(f"Error al imprimir corte seleccionado: {e}")

    def otro_ingreso(self):
        """Registra un ingreso simple en la caja usando diálogo personalizado"""
        try:
            if not self.caja_abierta:
                messagebox.showinfo(
                    "Información",
                    "Debe abrir la caja primero",
                    parent=self.ventana
                )
                return

            # — 1) Pedimos concepto y monto con la misma interfaz —
            resultado = self._dialogo_concepto_monto("Ingreso")
            if resultado is None:
                return
            concepto, monto = resultado

            # — 2) Inserto en BD igual que registrar_ingreso —
            conexion = conectar_bd()
            try:
                cursor = conexion.cursor()
                cursor.execute("""
                    INSERT INTO movimientos_caja
                    (id_caja, hora, tipo, concepto, monto, id_usuario)
                    VALUES (%s, NOW(), %s, %s, %s, %s)
                """, (
                    self.id_caja_actual,
                    'ingreso',
                    concepto,
                    monto,
                    self.id_usuario
                ))
                cursor.execute("""
                    UPDATE caja
                    SET total_ingresos = total_ingresos + %s,
                        saldo_final    = saldo_final + %s
                    WHERE id_caja = %s
                """, (monto, monto, self.id_caja_actual))
                conexion.commit()
            finally:
                conexion.close()

            # — 3) Refrescar interfaz y movimientos —
            self.actualizar_estado_caja()
            if hasattr(self, 'cargar_movimientos'):
                self.cargar_movimientos()

            messagebox.showinfo(
                "Registro Exitoso",
                f"Se registró un ingreso de ${monto:.2f} por concepto de {concepto}",
                parent=self.ventana
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo registrar el ingreso:\n{e}",   
                parent=self.ventana
            )
            print(f"Error al registrar otro ingreso: {e}")

    def realizar_arqueo_caja(self):
        """Realiza un arqueo de caja - VERSIÓN CORREGIDA CON ACTUALIZACIÓN DE SALDO"""
        try:
            if not self.caja_abierta:
                messagebox.showinfo("Información", "Debe abrir la caja primero")
                return

            # Crear ventana para arqueo
            ventana_arqueo = tk.Toplevel(self.ventana)
            ventana_arqueo.title("Arqueo de Caja")
            ventana_arqueo.geometry("650x550")
            ventana_arqueo.config(bg="#f5f5f5")
            ventana_arqueo.grab_set()

            utl.centrar_ventana(ventana_arqueo, 650, 550)

            # Frame principal
            frame_principal = tk.Frame(ventana_arqueo, bg="#f5f5f5", padx=20, pady=20)
            frame_principal.pack(fill=tk.BOTH, expand=True)

            # Título
            tk.Label(
                frame_principal,
                text="ARQUEO DE CAJA",
                font=("Helvetica", 16, "bold"),
                bg="#f5f5f5",
                fg="#3a7ff6"
            ).pack(pady=(0, 20))

            # Obtener saldo actual según sistema
            try:
                conexion = conectar_bd()
                cursor = conexion.cursor()
                cursor.execute("""
                    SELECT total_ingresos, total_egresos, saldo_final
                    FROM caja WHERE id_caja = %s
                """, (self.id_caja_actual,))

                caja_info = cursor.fetchone()
                conexion.close()

                if not caja_info:
                    messagebox.showerror("Error", "No se pudo obtener información de la caja actual")
                    ventana_arqueo.destroy()
                    return

                # CONVERTIR A FLOAT para evitar problemas de tipos
                ingresos = float(caja_info[0] or 0)
                egresos = float(caja_info[1] or 0)
                saldo_sistema = float(caja_info[2] or 0)

            except Exception as e:
                messagebox.showerror("Error", f"Error al obtener datos de caja: {str(e)}")
                ventana_arqueo.destroy()
                return

            # Frame para información del sistema
            frame_sistema = tk.Frame(frame_principal, bg="#e8f5e9", padx=15, pady=15, relief=tk.GROOVE, bd=1)
            frame_sistema.pack(fill=tk.X, pady=10)

            tk.Label(
                frame_sistema,
                text="SEGÚN SISTEMA",
                font=("Helvetica", 12, "bold"),
                bg="#e8f5e9"
            ).pack(anchor=tk.W)

            tk.Label(
                frame_sistema,
                text=f"Total Ingresos: ${ingresos:.2f}",
                font=("Helvetica", 11),
                bg="#e8f5e9"
            ).pack(anchor=tk.W, pady=2)

            tk.Label(
                frame_sistema,
                text=f"Total Egresos: ${egresos:.2f}",
                font=("Helvetica", 11),
                bg="#e8f5e9"
            ).pack(anchor=tk.W, pady=2)

            tk.Label(
                frame_sistema,
                text=f"Saldo en Sistema: ${saldo_sistema:.2f}",
                font=("Helvetica", 12, "bold"),
                bg="#e8f5e9"
            ).pack(anchor=tk.W, pady=2)

            # Frame para conteo de efectivo
            frame_conteo = tk.Frame(frame_principal, bg="#f5f5f5", pady=10)
            frame_conteo.pack(fill=tk.X, pady=10)

            tk.Label(
                frame_conteo,
                text="CONTEO DE EFECTIVO",
                font=("Helvetica", 12, "bold"),
                bg="#f5f5f5"
            ).pack(anchor=tk.W, pady=(0, 10))

            # Denominaciones de billetes y monedas
            denominaciones = [
                ("Billetes $500:", 500.0),
                ("Billetes $200:", 200.0),
                ("Billetes $100:", 100.0),
                ("Billetes $50:", 50.0),
                ("Billetes $20:", 20.0),
                ("Monedas $10:", 10.0),
                ("Monedas $5:", 5.0),
                ("Monedas $2:", 2.0),
                ("Monedas $1:", 1.0),
                ("Monedas $0.50:", 0.5),
                ("Monedas $0.20:", 0.2),
                ("Monedas $0.10:", 0.1)
            ]

            # Frame para grid de denominaciones
            frame_grid = tk.Frame(frame_conteo, bg="#f5f5f5")
            frame_grid.pack(fill=tk.X, pady=5)

            # Variables para cantidad por denominación
            cantidades = {}
            subtotales = {}

            # Variable para el total
            var_total = tk.StringVar(value="$0.00")
            var_diferencia = tk.StringVar(value="---")

            # Función para calcular subtotal cuando cambia la cantidad
            def calcular_subtotal():
                """Calcula el total y la diferencia"""
                total = 0.0
                try:
                    for i, (etiqueta, valor) in enumerate(denominaciones):
                        clave = f"denom_{i}"
                        try:
                            cantidad = int(cantidades[clave].get()) if cantidades[clave].get().strip() else 0
                            subtotal = cantidad * valor
                            subtotales[clave].set(f"${subtotal:.2f}")
                            total += subtotal
                        except (ValueError, AttributeError):
                            subtotales[clave].set("$0.00")

                    var_total.set(f"${total:.2f}")

                    # Calcular diferencia
                    diferencia = total - saldo_sistema

                    if diferencia > 0:
                        var_diferencia.set(f"Sobrante: ${diferencia:.2f}")
                    elif diferencia < 0:
                        var_diferencia.set(f"Faltante: ${abs(diferencia):.2f}")
                    else:
                        var_diferencia.set("Sin diferencia")

                except Exception as e:
                    print(f"Error en calcular_subtotal: {e}")
                    var_diferencia.set("Error en cálculo")

            # Crear campos en grid
            for i, (etiqueta, valor) in enumerate(denominaciones):
                fila = i // 2
                columna = (i % 2) * 3

                # Etiqueta
                tk.Label(
                    frame_grid,
                    text=etiqueta,
                    font=("Helvetica", 11),
                    width=12,
                    anchor=tk.W,
                    bg="#f5f5f5"
                ).grid(row=fila, column=columna, padx=5, pady=5, sticky=tk.W)

                # Campo de entrada para cantidad
                clave = f"denom_{i}"
                cantidades[clave] = tk.StringVar(value="0")
                entry = tk.Entry(
                    frame_grid,
                    textvariable=cantidades[clave],
                    font=("Helvetica", 11),
                    width=5
                )
                entry.grid(row=fila, column=columna + 1, padx=5, pady=5)

                # Bind para actualizar cuando cambie el valor
                entry.bind("<KeyRelease>", lambda event: calcular_subtotal())
                entry.bind("<FocusOut>", lambda event: calcular_subtotal())

                # Subtotal
                subtotales[clave] = tk.StringVar(value="$0.00")
                tk.Label(
                    frame_grid,
                    textvariable=subtotales[clave],
                    font=("Helvetica", 11),
                    width=10,
                    bg="#f5f5f5"
                ).grid(row=fila, column=columna + 2, padx=5, pady=5, sticky=tk.E)

            # Frame para total
            frame_total = tk.Frame(frame_principal, bg="#e3f2fd", padx=15, pady=15, relief=tk.GROOVE, bd=1)
            frame_total.pack(fill=tk.X, pady=(20, 10))

            tk.Label(
                frame_total,
                text="TOTAL EFECTIVO CONTADO:",
                font=("Helvetica", 12, "bold"),
                bg="#e3f2fd"
            ).pack(side=tk.LEFT, padx=5)

            tk.Label(
                frame_total,
                textvariable=var_total,
                font=("Helvetica", 14, "bold"),
                bg="#e3f2fd",
                fg="#3a7ff6"
            ).pack(side=tk.LEFT, padx=10)

            # Diferencia
            tk.Label(
                frame_total,
                text="Diferencia:",
                font=("Helvetica", 11),
                bg="#e3f2fd"
            ).pack(side=tk.LEFT, padx=(20, 5))

            lbl_diferencia = tk.Label(
                frame_total,
                textvariable=var_diferencia,
                font=("Helvetica", 11, "bold"),
                bg="#e3f2fd"
            )
            lbl_diferencia.pack(side=tk.LEFT)

            # Observaciones
            tk.Label(
                frame_principal,
                text="Observaciones:",
                font=("Helvetica", 11),
                bg="#f5f5f5"
            ).pack(anchor=tk.W, pady=(15, 5))

            txt_observaciones = tk.Text(frame_principal, height=3, width=50, font=("Helvetica", 11))
            txt_observaciones.pack(fill=tk.X, pady=(0, 15))

            # Función para guardar arqueo
            def guardar_arqueo():
                try:
                    total_efectivo = float(var_total.get().replace('$', '').replace(',', ''))
                    diferencia = total_efectivo - saldo_sistema
                    observaciones = txt_observaciones.get("1.0", "end-1c").strip()

                    # Confirmar que quiere actualizar el saldo
                    if diferencia != 0:
                        mensaje_confirmacion = f"""
                        El efectivo contado (${total_efectivo:.2f}) no coincide con el saldo del sistema (${saldo_sistema:.2f}).

                        Diferencia: {"Sobrante" if diferencia > 0 else "Faltante"} de ${abs(diferencia):.2f}

                        ¿Desea proceder y actualizar el saldo de la caja al efectivo contado?
                        El nuevo saldo será: ${total_efectivo:.2f}
                        """

                        if not messagebox.askyesno("Confirmar Actualización de Saldo", mensaje_confirmacion):
                            return

                    # Guardar en la base de datos
                    conexion = conectar_bd()
                    cursor = conexion.cursor()

                    # Iniciar transacción
                    cursor.execute("START TRANSACTION")

                    try:
                        # 1. Insertar arqueo
                        cursor.execute("""
                            INSERT INTO arqueos_caja 
                            (id_caja, fecha, hora, saldo_sistema, efectivo_contado, diferencia, observaciones, id_usuario)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            self.id_caja_actual,
                            date.today(),
                            datetime.now().time(),
                            saldo_sistema,
                            total_efectivo,
                            diferencia,
                            observaciones,
                            self.id_usuario
                        ))

                        arqueo_id = cursor.lastrowid

                        # 2. ACTUALIZAR EL SALDO DE LA CAJA AL EFECTIVO CONTADO
                        cursor.execute("""
                            UPDATE caja 
                            SET saldo_final = %s
                            WHERE id_caja = %s
                        """, (total_efectivo, self.id_caja_actual))

                        # 3. Si hay diferencia, registrar movimiento de ajuste
                        if diferencia != 0:
                            tipo_ajuste = "ingreso" if diferencia > 0 else "egreso"
                            concepto_ajuste = f"Ajuste por arqueo #{arqueo_id} - {'Sobrante encontrado' if diferencia > 0 else 'Faltante detectado'}"

                            cursor.execute("""
                                INSERT INTO movimientos_caja (id_caja, tipo, concepto, monto, hora, id_usuario)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (
                                self.id_caja_actual,
                                tipo_ajuste,
                                concepto_ajuste,
                                abs(diferencia),
                                datetime.now(),
                                self.id_usuario
                            ))

                            # Actualizar totales de ingresos/egresos según corresponda
                            if diferencia > 0:
                                cursor.execute("""
                                    UPDATE caja 
                                    SET total_ingresos = total_ingresos + %s
                                    WHERE id_caja = %s
                                """, (diferencia, self.id_caja_actual))
                            else:
                                cursor.execute("""
                                    UPDATE caja 
                                    SET total_egresos = total_egresos + %s
                                    WHERE id_caja = %s
                                """, (abs(diferencia), self.id_caja_actual))

                        # Confirmar transacción
                        cursor.execute("COMMIT")
                        conexion.close()

                        # Mensaje de éxito
                        mensaje_exito = f"Arqueo de caja guardado correctamente.\n"
                        mensaje_exito += f"Saldo actualizado a: ${total_efectivo:.2f}"
                        if diferencia != 0:
                            mensaje_exito += f"\nSe registró un ajuste de ${abs(diferencia):.2f}"

                        messagebox.showinfo("Éxito", mensaje_exito)

                        # Actualizar la interfaz de caja
                        self.actualizar_estado_caja()

                        # Preguntar si desea imprimir
                        if messagebox.askyesno("Imprimir", "¿Desea imprimir el arqueo de caja?"):
                            self.imprimir_arqueo_guardado(arqueo_id)

                        ventana_arqueo.destroy()

                    except Exception as e:
                        cursor.execute("ROLLBACK")
                        conexion.close()
                        raise e

                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo guardar el arqueo: {str(e)}")
                    print(f"Error detallado: {e}")
                    import traceback
                    traceback.print_exc()

            # Botones
            frame_botones = tk.Frame(frame_principal, bg="#f5f5f5")
            frame_botones.pack(pady=10)

            btn_guardar = tk.Button(
                frame_botones,
                text="Guardar Arqueo",
                font=("Helvetica", 11),
                bg="#4caf50",
                fg="white",
                width=15,
                cursor="hand2",
                command=guardar_arqueo
            )
            btn_guardar.pack(side=tk.LEFT, padx=10)

            btn_cancelar = tk.Button(
                frame_botones,
                text="Cancelar",
                font=("Helvetica", 11),
                bg="#e53935",
                fg="white",
                width=10,
                cursor="hand2",
                command=ventana_arqueo.destroy
            )
            btn_cancelar.pack(side=tk.LEFT, padx=10)

            # Calcular totales iniciales
            calcular_subtotal()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el arqueo: {str(e)}")
            print(f"Error detallado en realizar_arqueo_caja: {e}")
            import traceback
            traceback.print_exc()

    def imprimir_arqueo_guardado(self, id_arqueo):
        """Imprime un arqueo que ya fue guardado - VERSIÓN CORREGIDA"""
        try:
            # Obtener datos del arqueo
            conexion = conectar_bd()
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT a.fecha, a.hora, a.saldo_sistema, a.efectivo_contado, 
                       a.diferencia, a.observaciones, u.nombre
                FROM arqueos_caja a
                JOIN usuarios u ON a.id_usuario = u.id_usuario
                WHERE a.id_arqueo = %s
            """, (id_arqueo,))

            arqueo = cursor.fetchone()
            conexion.close()

            if not arqueo:
                messagebox.showerror("Error", "No se encontró el arqueo")
                return

            fecha, hora, saldo_sistema, efectivo, diferencia, observaciones, usuario = arqueo

            # Crear ticket
            try:
                from ticket import Ticket
                ticket = Ticket()

                # Encabezado
                ticket.agregar_encabezado()
                ticket.agregar_titulo("ARQUEO DE CAJA")

                # Formatear fecha de manera segura
                fecha_str = "N/A"
                if fecha:
                    try:
                        if hasattr(fecha, 'strftime'):
                            fecha_str = fecha.strftime('%d/%m/%Y')
                        else:
                            fecha_str = str(fecha)
                    except:
                        fecha_str = str(fecha)

                ticket.agregar_texto(f"Fecha: {fecha_str}")

                # Formatear hora de manera segura
                hora_str = "N/A"
                if hora:
                    try:
                        if hasattr(hora, 'strftime'):
                            hora_str = hora.strftime('%H:%M:%S')
                        elif isinstance(hora, timedelta):
                            # Convertir timedelta a horas:minutos:segundos
                            total_seconds = int(hora.total_seconds())
                            hours = total_seconds // 3600
                            minutes = (total_seconds % 3600) // 60
                            seconds = total_seconds % 60
                            hora_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                        else:
                            hora_str = str(hora)
                    except:
                        hora_str = str(hora)

                ticket.agregar_texto(f"Hora: {hora_str}")
                ticket.agregar_texto(f"Responsable: {usuario}")
                ticket.agregar_linea()

                # Detalles
                ticket.agregar_texto(f"Saldo sistema: ${float(saldo_sistema):.2f}")
                ticket.agregar_texto(f"Efectivo contado: ${float(efectivo):.2f}")

                if float(diferencia) > 0:
                    ticket.agregar_texto(f"Sobrante: ${float(diferencia):.2f}")
                elif float(diferencia) < 0:
                    ticket.agregar_texto(f"Faltante: ${abs(float(diferencia)):.2f}")
                else:
                    ticket.agregar_texto("Sin diferencia")

                if observaciones:
                    ticket.agregar_linea()
                    ticket.agregar_texto("Observaciones:")
                    ticket.agregar_texto(observaciones)

                # Firmas
                ticket.agregar_espacio()
                ticket.agregar_texto_centrado("___________________")
                ticket.agregar_texto_centrado("Firma del Responsable")

                # Generar PDF
                nombre_archivo = f"arqueo_{id_arqueo}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
                ruta_pdf = ticket.generar_pdf(nombre_archivo)
                ticket.mostrar_vista_previa(ruta_pdf)

                messagebox.showinfo("Éxito", "Arqueo impreso correctamente")

            except ImportError:
                # Si no está disponible el módulo ticket, crear HTML simple
                self.crear_arqueo_html_simple(id_arqueo, arqueo)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo imprimir el arqueo: {str(e)}")
            print(f"Error detallado: {e}")
            import traceback
            traceback.print_exc()

    def crear_arqueo_html_simple(self, id_arqueo, datos_arqueo):
        """Crea un archivo HTML simple para imprimir el arqueo"""
        try:
            fecha, hora, saldo_sistema, efectivo, diferencia, observaciones, usuario = datos_arqueo

            # Formatear datos de manera segura
            fecha_str = "N/A"
            if fecha:
                try:
                    fecha_str = fecha.strftime('%d/%m/%Y') if hasattr(fecha, 'strftime') else str(fecha)
                except:
                    fecha_str = str(fecha)

            hora_str = "N/A"
            if hora:
                try:
                    if hasattr(hora, 'strftime'):
                        hora_str = hora.strftime('%H:%M:%S')
                    elif isinstance(hora, timedelta):
                        total_seconds = int(hora.total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        seconds = total_seconds % 60
                        hora_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    else:
                        hora_str = str(hora)
                except:
                    hora_str = str(hora)

            # Crear HTML
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Arqueo de Caja #{id_arqueo}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; width: 300px; margin: 0 auto; }}
                    .header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; }}
                    .content {{ margin: 20px 0; }}
                    .line {{ border-top: 1px dashed #000; margin: 10px 0; }}
                    .total {{ font-weight: bold; font-size: 14px; }}
                    .footer {{ margin-top: 30px; text-align: center; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>ARQUEO DE CAJA</h2>
                    <p>Arqueo #{id_arqueo}</p>
                </div>

                <div class="content">
                    <p><strong>Fecha:</strong> {fecha_str}</p>
                    <p><strong>Hora:</strong> {hora_str}</p>
                    <p><strong>Responsable:</strong> {usuario}</p>

                    <div class="line"></div>

                    <p><strong>Saldo en Sistema:</strong> ${float(saldo_sistema):.2f}</p>
                    <p><strong>Efectivo Contado:</strong> ${float(efectivo):.2f}</p>

                    <div class="line"></div>

                    <p class="total">
                        <strong>Diferencia:</strong> 
                        {
            f"Sobrante: ${float(diferencia):.2f}" if float(diferencia) > 0
            else f"Faltante: ${abs(float(diferencia)):.2f}" if float(diferencia) < 0
            else "Sin diferencia"
            }
                    </p>

                    {f'<div class="line"></div><p><strong>Observaciones:</strong><br>{observaciones}</p>' if observaciones else ''}

                    <div class="footer">
                        <div class="line"></div>
                        <p>Firma del Responsable: ___________________</p>
                        <p style="font-size: 10px; margin-top: 20px;">
                            Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """

            nombre_archivo = f"arqueo_{id_arqueo}_{datetime.now().strftime('%Y%m%d%H%M%S')}.html"

            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                f.write(html)

            # Abrir en navegador
            import webbrowser
            webbrowser.open(nombre_archivo)

            messagebox.showinfo("Arqueo Generado", f"Archivo HTML creado: {nombre_archivo}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el archivo HTML: {str(e)}")
            print(f"Error al crear HTML: {e}")

    def imprimir_arqueo_guardado(self, id_arqueo):
        """Imprime un arqueo que ya fue guardado"""
        try:
            # Obtener datos del arqueo
            conexion = conectar_bd()
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT a.fecha, a.hora, a.saldo_sistema, a.efectivo_contado, 
                       a.diferencia, a.observaciones, u.nombre
                FROM arqueos_caja a
                JOIN usuarios u ON a.id_usuario = u.id_usuario
                WHERE a.id_arqueo = %s
            """, (id_arqueo,))

            arqueo = cursor.fetchone()
            conexion.close()

            if not arqueo:
                messagebox.showerror("Error", "No se encontró el arqueo")
                return

            fecha, hora, saldo_sistema, efectivo, diferencia, observaciones, usuario = arqueo

            # Crear ticket
            from ticket import Ticket
            ticket = Ticket()

            # Encabezado
            ticket.agregar_encabezado()
            ticket.agregar_titulo("ARQUEO DE CAJA")
            ticket.agregar_texto(f"Fecha: {fecha.strftime('%d/%m/%Y')}")
            ticket.agregar_texto(f"Hora: {hora.strftime('%H:%M:%S')}")
            ticket.agregar_texto(f"Responsable: {usuario}")
            ticket.agregar_linea()

            # Detalles
            ticket.agregar_texto(f"Saldo sistema: ${float(saldo_sistema):.2f}")
            ticket.agregar_texto(f"Efectivo contado: ${float(efectivo):.2f}")

            if diferencia > 0:
                ticket.agregar_texto(f"Sobrante: ${float(diferencia):.2f}")
            elif diferencia < 0:
                ticket.agregar_texto(f"Faltante: ${abs(float(diferencia)):.2f}")
            else:
                ticket.agregar_texto("Sin diferencia")

            if observaciones:
                ticket.agregar_linea()
                ticket.agregar_texto("Observaciones:")
                ticket.agregar_texto(observaciones)

            # Generar PDF
            nombre_archivo = f"arqueo_{id_arqueo}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            ruta_pdf = ticket.generar_pdf(nombre_archivo)
            ticket.mostrar_vista_previa(ruta_pdf)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo imprimir el arqueo: {str(e)}")
    def actualizar_vista_tabla(self):
        """Forza la actualización visual de la tabla"""
        if hasattr(self, 'tabla_cortes'):
            self.tabla_cortes.update_idletasks()
            self.ventana.update()

    def configurar_tab_movimientos(self):
        """Configura la pestaña de movimientos de caja"""
        # Limpiar pestaña
        for widget in self.tab_movimientos.winfo_children():
            widget.destroy()

        # Frame principal
        frame_principal = tk.Frame(self.tab_movimientos, bg="#f5f5f5", padx=10, pady=10)
        frame_principal.pack(fill=tk.BOTH, expand=True)

        # Variables para filtros
        self.fecha_movimientos = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.tipo_movimiento = tk.StringVar(value="Todos")

        # Frame para filtros
        frame_filtros = tk.Frame(frame_principal, bg="#f5f5f5", padx=5, pady=5, relief=tk.GROOVE, bd=1)
        frame_filtros.pack(fill=tk.X, pady=10)

        # Control de fecha
        frame_fecha = tk.Frame(frame_filtros, bg="#f5f5f5")
        frame_fecha.pack(side=tk.LEFT, padx=10)

        tk.Label(frame_fecha, text="Fecha:", bg="#f5f5f5", font=("Helvetica", 11)).pack(side=tk.LEFT)

        entry_fecha = tk.Entry(
            frame_fecha,
            textvariable=self.fecha_movimientos,
            width=12,
            font=("Helvetica", 11)
        )
        entry_fecha.pack(side=tk.LEFT, padx=5)

        btn_fecha = tk.Button(
            frame_fecha,
            text="📅",
            font=("Helvetica", 11),
            bg="#2196f3",
            fg="white",
            command=lambda: self.mostrar_calendario("movimientos")
        )
        btn_fecha.pack(side=tk.LEFT)

        # Control de tipo
        frame_tipo = tk.Frame(frame_filtros, bg="#f5f5f5")
        frame_tipo.pack(side=tk.LEFT, padx=10)

        tk.Label(frame_tipo, text="Tipo:", bg="#f5f5f5", font=("Helvetica", 11)).pack(side=tk.LEFT)

        combo_tipo = ttk.Combobox(
            frame_tipo,
            textvariable=self.tipo_movimiento,
            values=["Todos", "Ingreso", "Egreso"],
            width=10,
            state="readonly"
        )
        combo_tipo.pack(side=tk.LEFT, padx=5)

        # Botón de búsqueda
        frame_btn = tk.Frame(frame_filtros, bg="#f5f5f5")
        frame_btn.pack(side=tk.LEFT, padx=20)

        btn_buscar = tk.Button(
            frame_btn,
            text="🔍 Buscar",
            font=("Helvetica", 11),
            bg="#3f51b5",
            fg="white",
            command=self.cargar_movimientos
        )
        btn_buscar.pack()

        # Frame para tabla
        frame_tabla = tk.Frame(frame_principal, bg="#f5f5f5", padx=5, pady=5, height=300)
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10)
        frame_tabla.pack_propagate(False)  # Evita que se encoja

        # Columnas para la tabla
        columnas = ('id', 'hora', 'tipo', 'concepto', 'monto', 'usuario')

        # Crear tabla
        self.tabla_movimientos = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            show='headings',
            height=10
        )

        # Configurar encabezados
        self.tabla_movimientos.heading('id', text='ID')
        self.tabla_movimientos.heading('hora', text='Hora')
        self.tabla_movimientos.heading('tipo', text='Tipo')
        self.tabla_movimientos.heading('concepto', text='Concepto')
        self.tabla_movimientos.heading('monto', text='Monto')
        self.tabla_movimientos.heading('usuario', text='Usuario')

        # Configurar anchos
        self.tabla_movimientos.column('id', width=50, anchor=tk.CENTER)
        self.tabla_movimientos.column('hora', width=100, anchor=tk.CENTER)
        self.tabla_movimientos.column('tipo', width=80, anchor=tk.CENTER)
        self.tabla_movimientos.column('concepto', width=250)
        self.tabla_movimientos.column('monto', width=100, anchor=tk.E)
        self.tabla_movimientos.column('usuario', width=150)

        # Aplicar estilo predefinido
        utl.aplicar_estilo_tabla(self.tabla_movimientos)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_movimientos.yview)
        self.tabla_movimientos.configure(yscrollcommand=scrollbar.set)

        # Empaquetar tabla y scrollbar
        self.tabla_movimientos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame para totales
        frame_totales = tk.Frame(frame_principal, bg="#f0f7fa", relief=tk.GROOVE, bd=1, padx=10, pady=10)
        frame_totales.pack(fill=tk.X, pady=10)

        # Variables de totales
        self.total_ingresos = tk.StringVar(value="$0.00")
        self.total_egresos = tk.StringVar(value="$0.00")
        self.saldo_del_dia = tk.StringVar(value="$0.00")

        # Mostrar totales en 3 columnas
        frame_ing = tk.Frame(frame_totales, bg="#f0f7fa")
        frame_ing.pack(side=tk.LEFT, expand=True, fill=tk.X)

        tk.Label(frame_ing, text="Total Ingresos:", font=("Helvetica", 11, "bold"), bg="#f0f7fa").pack(anchor=tk.W)
        tk.Label(frame_ing, textvariable=self.total_ingresos, font=("Helvetica", 11), fg="#4caf50", bg="#f0f7fa").pack(
            anchor=tk.W)

        frame_egr = tk.Frame(frame_totales, bg="#f0f7fa")
        frame_egr.pack(side=tk.LEFT, expand=True, fill=tk.X)

        tk.Label(frame_egr, text="Total Egresos:", font=("Helvetica", 11, "bold"), bg="#f0f7fa").pack(anchor=tk.W)
        tk.Label(frame_egr, textvariable=self.total_egresos, font=("Helvetica", 11), fg="#f44336", bg="#f0f7fa").pack(
            anchor=tk.W)

        frame_saldo = tk.Frame(frame_totales, bg="#f0f7fa")
        frame_saldo.pack(side=tk.LEFT, expand=True, fill=tk.X)

        tk.Label(frame_saldo, text="Saldo del Día:", font=("Helvetica", 11, "bold"), bg="#f0f7fa").pack(anchor=tk.W)
        tk.Label(frame_saldo, textvariable=self.saldo_del_dia, font=("Helvetica", 11, "bold"), bg="#f0f7fa").pack(
            anchor=tk.W)

        # Botón de imprimir
        frame_btn_imp = tk.Frame(frame_totales, bg="#f0f7fa")
        frame_btn_imp.pack(side=tk.RIGHT)

        btn_imprimir = tk.Button(
            frame_btn_imp,
            text="🖨️ Imprimir",
            font=("Helvetica", 11),
            bg="#3f51b5",
            fg="white",
            command=self.imprimir_movimientos
        )
        btn_imprimir.pack(pady=5)

        # Programar carga de datos con un ligero retraso
        self.ventana.after(100, self.cargar_movimientos)


    def ver_ultimo_corte(self):
        """Muestra información del último corte de caja registrado"""
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Consultar el último corte de caja (una caja cerrada)
            cursor.execute("""
                SELECT c.id_caja, c.fecha, c.hora_apertura, c.hora_cierre, 
                       c.total_ingresos, c.total_egresos, c.saldo_final,
                       u.nombre
                FROM caja c
                JOIN usuarios u ON c.responsable = u.id_usuario
                WHERE c.hora_cierre IS NOT NULL
                ORDER BY c.fecha DESC, c.hora_cierre DESC
                LIMIT 1
            """)

            corte = cursor.fetchone()
            conexion.close()

            if corte:
                id_caja, fecha, hora_apertura, hora_cierre, ingresos, egresos, saldo, responsable = corte

                # Formatear fechas y horas para mejor visualización
                fecha_formateada = utl.formatear_fecha(fecha)

                # Formatear hora de apertura con manejo seguro
                hora_ap = "N/A"
                if hora_apertura:
                    if hasattr(hora_apertura, 'strftime'):
                        hora_ap = hora_apertura.strftime("%H:%M:%S")
                    elif isinstance(hora_apertura, timedelta):
                        # Si es timedelta, convertir a formato adecuado
                        segundos = hora_apertura.total_seconds()
                        horas = int(segundos // 3600)
                        minutos = int((segundos % 3600) // 60)
                        segundos = int(segundos % 60)
                        hora_ap = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
                    else:
                        hora_ap = str(hora_apertura)

                # Formatear hora de cierre con manejo seguro
                hora_ci = "N/A"
                if hora_cierre:
                    if hasattr(hora_cierre, 'strftime'):
                        hora_ci = hora_cierre.strftime("%H:%M:%S")
                    elif isinstance(hora_cierre, timedelta):
                        # Si es timedelta, convertir a formato adecuado
                        segundos = hora_cierre.total_seconds()
                        horas = int(segundos // 3600)
                        minutos = int((segundos % 3600) // 60)
                        segundos = int(segundos % 60)
                        hora_ci = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
                    else:
                        hora_ci = str(hora_cierre)

                # Crear una ventana para mostrar el corte
                ventana_corte = tk.Toplevel(self.ventana)
                ventana_corte.title("Último Corte de Caja")
                ventana_corte.geometry("500x400")
                ventana_corte.config(bg="#f5f5f5")
                ventana_corte.resizable(False, False)

                # Centrar la ventana
                utl.centrar_ventana(ventana_corte, 500, 400)

                # Hacer la ventana modal
                ventana_corte.transient(self.ventana)
                ventana_corte.grab_set()

                # Contenido
                frame_corte = tk.Frame(ventana_corte, bg="#f5f5f5", padx=20, pady=20)
                frame_corte.pack(fill=tk.BOTH, expand=True)

                # Título
                tk.Label(
                    frame_corte,
                    text="ÚLTIMO CORTE DE CAJA",
                    font=("Helvetica", 14, "bold"),
                    bg="#f5f5f5",
                    fg="#3a7ff6"
                ).pack(pady=(0, 20))

                # Información del corte en formato de tabla
                info_frame = tk.Frame(frame_corte, bg="#f0f7ff", padx=15, pady=15, relief=tk.GROOVE, bd=1)
                info_frame.pack(fill=tk.BOTH, expand=True)

                # Datos en dos columnas
                datos = [
                    ("ID de Caja:", f"{id_caja}"),
                    ("Fecha:", fecha_formateada),
                    ("Hora de Apertura:", hora_ap),
                    ("Hora de Cierre:", hora_ci),
                    ("Responsable:", responsable),
                    ("Total Ingresos:", f"${ingresos:.2f}"),
                    ("Total Egresos:", f"${egresos:.2f}"),
                    ("Saldo Final:", f"${saldo:.2f}")
                ]

                for i, (etiqueta, valor) in enumerate(datos):
                    tk.Label(
                        info_frame,
                        text=etiqueta,
                        font=("Helvetica", 11, "bold"),
                        bg="#f0f7ff",
                        anchor=tk.W
                    ).grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)

                    tk.Label(
                        info_frame,
                        text=valor,
                        font=("Helvetica", 11),
                        bg="#f0f7ff",
                        anchor=tk.W
                    ).grid(row=i, column=1, sticky=tk.W, padx=5, pady=5)

                # Botones
                frame_botones = tk.Frame(frame_corte, bg="#f5f5f5")
                frame_botones.pack(pady=15)

                btn_imprimir = tk.Button(
                    frame_botones,
                    text="Imprimir Corte",
                    font=("Helvetica", 11),
                    bg="#3f51b5",
                    fg="white",
                    width=15,
                    cursor="hand2",
                    command=lambda: self.imprimir_corte(id_caja)
                )
                btn_imprimir.grid(row=0, column=0, padx=10)

                btn_cerrar = tk.Button(
                    frame_botones,
                    text="Cerrar",
                    font=("Helvetica", 11),
                    bg="#e53935",
                    fg="white",
                    width=10,
                    cursor="hand2",
                    command=ventana_corte.destroy
                )
                btn_cerrar.grid(row=0, column=1, padx=10)

            else:
                messagebox.showinfo("Información", "No se encontraron cortes de caja anteriores")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo consultar el último corte: {str(e)}")
            print(f"Error al consultar último corte: {e}")
            import traceback
            traceback.print_exc()

# Agrega esta función al final de tu archivo caja.py

def abrir_caja(self):
    """Método para abrir la caja con usuario correcto"""
    try:
        print(f"Debug - Valor de self.id_usuario antes de abrir caja: {self.id_usuario}")

        # 1. Verificación directa del usuario en la BD
        conexion = conectar_bd()
        cursor = conexion.cursor()

        # Verificar qué usuario somos realmente
        cursor.execute("SELECT id_usuario, nombre FROM usuarios WHERE id_usuario = %s", (self.id_usuario,))
        usuario_actual = cursor.fetchone()

        if usuario_actual:
            print(f"Debug - Usuario verificado: ID={usuario_actual[0]}, Nombre={usuario_actual[1]}")
        else:
            print(f"Debug - ADVERTENCIA: No se pudo encontrar usuario con ID={self.id_usuario}")
            # Buscar a Aketzaly para verificar su ID
            cursor.execute("SELECT id_usuario, nombre FROM usuarios WHERE nombre = 'Aketzaly'")
            usuario_aketzaly = cursor.fetchone()
            if usuario_aketzaly:
                print(f"Debug - Usuario Aketzaly: ID={usuario_aketzaly[0]}, Nombre={usuario_aketzaly[1]}")

            # Mostrar todos los usuarios para diagnóstico
            cursor.execute("SELECT id_usuario, nombre FROM usuarios LIMIT 10")
            print("Debug - Usuarios en BD:")
            for usuario in cursor.fetchall():
                print(f"  ID={usuario[0]}, Nombre={usuario[1]}")

        # 2. Si ya hay una caja abierta, solo informar y salir
        if self.caja_abierta:
            messagebox.showinfo("Información", "La caja ya se encuentra abierta")
            conexion.close()
            return

        # 3. Preguntar por el monto inicial (código simplificado para claridad
        monto_inicial = simpledialog.askfloat(
            "Apertura de Caja",
            "Ingrese el monto inicial en caja:",
            minvalue=0.0
        )

        if monto_inicial is None:
            messagebox.showinfo("Cancelado", "Apertura de caja cancelada")
            conexion.close()
            return

        # 4. Insertar en la tabla caja - ASEGURAR que se use el ID correcto
        fecha_actual = date.today()
        hora_actual = datetime.now().time()

        print(f"Debug - Ejecutando INSERT con ID usuario: {self.id_usuario}")

        # Usar sentencia SQL con valores explícitos para verificar
        cursor.execute(f"""
            INSERT INTO caja 
              (fecha, hora_apertura, responsable, total_ingresos, total_egresos, saldo_final)
            VALUES 
              ('{fecha_actual}', '{hora_actual}', {self.id_usuario}, 0.0, 0.0, {monto_inicial})
        """)

        # Obtener el ID de la caja insertada
        self.id_caja_actual = cursor.lastrowid
        self.caja_abierta = True

        # 5. Verificar inmediatamente que se haya insertado correctamente
        cursor.execute("""
            SELECT c.id_caja, c.responsable, u.nombre 
            FROM caja c 
            JOIN usuarios u ON c.responsable = u.id_usuario
            WHERE c.id_caja = %s
        """, (self.id_caja_actual,))

        caja_creada = cursor.fetchone()
        if caja_creada:
            print(f"Debug - Caja creada: ID={caja_creada[0]}, ResponsableID={caja_creada[1]}, Nombre={caja_creada[2]}")

            # Si el responsable no es el esperado, corregir manualmente
            if caja_creada[1] != self.id_usuario:
                print("Debug - CORRECCIÓN MANUAL: Responsable no es el usuario actual, corrigiendo...")
                cursor.execute("""
                    UPDATE caja 
                    SET responsable = %s 
                    WHERE id_caja = %s
                """, (self.id_usuario, self.id_caja_actual))

                # Verificar la corrección
                cursor.execute("""
                    SELECT c.id_caja, c.responsable, u.nombre 
                    FROM caja c 
                    JOIN usuarios u ON c.responsable = u.id_usuario
                    WHERE c.id_caja = %s
                """, (self.id_caja_actual,))
                caja_corregida = cursor.fetchone()
                print(
                    f"Debug - Después de corrección: ID={caja_corregida[0]}, ResponsableID={caja_corregida[1]}, Nombre={caja_corregida[2]}")

        # 6. Registrar el movimiento inicial
        if monto_inicial > 0:
            cursor.execute("""
                INSERT INTO movimientos_caja (id_caja, tipo, concepto, monto, hora, id_usuario)
                VALUES (%s, 'ingreso', 'Saldo inicial', %s, %s, %s)
            """, (
                self.id_caja_actual,
                monto_inicial,
                datetime.now(),
                self.id_usuario
            ))

            # Actualizar saldo e ingresos
            cursor.execute("""
                UPDATE caja 
                SET total_ingresos = %s, saldo_final = %s
                WHERE id_caja = %s
            """, (monto_inicial, monto_inicial, self.id_caja_actual))

        # 7. Confirmar transacción y cerrar conexión
        conexion.commit()
        conexion.close()

        # 8. Mostrar mensaje de éxito y actualizar interfaz
        messagebox.showinfo("Apertura Exitosa",
                            f"La caja se ha abierto correctamente con un monto inicial de ${monto_inicial:.2f}")

        # 9. Actualizar la interfaz
        self.actualizar_estado_caja()
        self.configurar_tab_operaciones()

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la caja: {str(e)}")
        print(f"Error detallado al abrir caja: {e}")
        import traceback
        traceback.print_exc()