"""
Módulo de Caja para el Sistema de Gestión de Lavandería
Permite gestionar apertura y cierre de caja, registrar movimientos,
y generar reportes de cortes de caja.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import sys
import utileria as utl
from datetime import datetime, date, timedelta
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

        # ID del usuario actual (para registrar quién hace las operaciones)
        self.id_usuario = id_usuario

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

                cursor.execute("""
                    SELECT c.fecha, c.hora_apertura, u.nombre, 
                           COALESCE(c.total_ingresos, 0), 
                           COALESCE(c.total_egresos, 0), 
                           COALESCE(c.saldo_final, 0),
                           (SELECT m.concepto FROM movimientos_caja m 
                            WHERE m.id_caja = c.id_caja AND m.tipo = 'ingreso' 
                            ORDER BY m.hora ASC LIMIT 1) as primer_movimiento
                    FROM caja c
                    JOIN usuarios u ON c.responsable = u.id_usuario
                    WHERE c.id_caja = %s
                """, (self.id_caja_actual,))

                caja = cursor.fetchone()
                conexion.close()

                if caja:
                    fecha, hora_apertura, responsable, ingresos, egresos, saldo, primer_movimiento = caja
                    fecha_formateada = utl.formatear_fecha(fecha)
                    hora_formateada = hora_apertura.strftime("%H:%M:%S") if hora_apertura else ""

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

                    # Mostrar el origen del saldo inicial
                    if primer_movimiento:
                        origen_texto = "(Saldo del cierre anterior)" if "cierre anterior" in primer_movimiento else "(Saldo inicial)"
                        tk.Label(
                            self.frame_estado,
                            text=origen_texto,
                            font=("Helvetica", 10),
                            bg="#f5f5f5",
                            fg="#666666"
                        ).grid(row=1, column=4, sticky=tk.W, padx=15, pady=2)

            except Exception as e:
                # Si hay error, mostrar un estado simplificado
                print(f"Error al obtener detalles de caja: {e}")
                # ... código de estado simplificado ...

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
                    ticket.agregar_texto(f"Fecha: {utl.formatear_fecha(fecha)}")
                    ticket.agregar_texto(f"Hora apertura: {hora_apertura.strftime('%H:%M:%S')}")
                    ticket.agregar_texto(f"Responsable: {responsable}")
                    ticket.agregar_linea()

                    # Detalle
                    ticket.agregar_texto(f"Total ingresos: ${ingresos:.2f}")
                    ticket.agregar_texto(f"Total egresos: ${egresos:.2f}")
                    ticket.agregar_linea()

                    # Total
                    ticket.agregar_texto(f"Saldo actual: ${saldo:.2f}")

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

    def registrar_ingreso(self):
        """Registra un ingreso en la caja actual"""
        try:
            if not self.caja_abierta:
                messagebox.showinfo("Información", "Debe abrir la caja primero")
                return

            # Solicitar información del ingreso
            concepto = simpledialog.askstring(
                "Ingreso",
                "Ingrese el concepto del ingreso:"
            )

            if not concepto:
                return

            monto = simpledialog.askfloat(
                "Ingreso",
                "Ingrese el monto del ingreso:",
                minvalue=0.01
            )

            if monto is None:
                return

            # Registrar en la base de datos
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Insertar en la tabla de movimientos
            cursor.execute("""
                INSERT INTO movimientos_caja (id_caja, fecha, hora, tipo, concepto, monto, id_usuario)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                self.id_caja_actual,
                date.today().strftime("%Y-%m-%d"),
                datetime.now(),
                'ingreso',  # Debe ser 'ingreso' (minúsculas)
                concepto,
                monto,
                self.id_usuario
            ))

            # Actualizar el total de ingresos en la caja
            cursor.execute("""
                UPDATE caja 
                SET total_ingresos = total_ingresos + %s,
                    saldo_final = saldo_final + %s
                WHERE id_caja = %s
            """, (monto, monto, self.id_caja_actual))

            conexion.commit()
            conexion.close()

            # Actualizar interfaz
            self.actualizar_estado_caja()

            # Recargar movimientos si estamos en esa pestaña
            if hasattr(self, 'cargar_movimientos'):
                self.cargar_movimientos()

            messagebox.showinfo(
                "Registro Exitoso",
                f"Se ha registrado un ingreso de ${monto:.2f} por concepto de {concepto}"
            )

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el ingreso: {str(e)}")
            print(f"Error al registrar ingreso: {e}")

    def registrar_egreso(self):
        """Registra un egreso en la caja actual"""
        try:
            if not self.caja_abierta:
                messagebox.showinfo("Información", "Debe abrir la caja primero")
                return

            # Solicitar información del egreso
            concepto = simpledialog.askstring(
                "Egreso",
                "Ingrese el concepto del egreso:"
            )

            if not concepto:
                return

            monto = simpledialog.askfloat(
                "Egreso",
                "Ingrese el monto del egreso:",
                minvalue=0.01
            )

            if monto is None:
                return

            # Verificar que haya saldo suficiente
            conexion = conectar_bd()
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT total_ingresos - total_egresos AS saldo_actual
                FROM caja
                WHERE id_caja = %s
            """, (self.id_caja_actual,))

            resultado = cursor.fetchone()

            if resultado and resultado[0] < monto:
                messagebox.showerror(
                    "Saldo Insuficiente",
                    f"No hay saldo suficiente para este egreso.\nSaldo actual: ${resultado[0]:.2f}"
                )
                conexion.close()
                return

            # Registrar en la base de datos
            # Insertar en la tabla de movimientos
            cursor.execute("""
                INSERT INTO movimientos_caja (id_caja, fecha, hora, tipo, concepto, monto, id_usuario)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                self.id_caja_actual,
                date.today().strftime("%Y-%m-%d"),
                datetime.now(),
                'egreso',  # Debe ser 'egreso' (minúsculas)
                concepto,
                monto,
                self.id_usuario
            ))

            # Actualizar el total de egresos en la caja
            cursor.execute("""
                UPDATE caja 
                SET total_egresos = total_egresos + %s,
                    saldo_final = saldo_final - %s
                WHERE id_caja = %s
            """, (monto, monto, self.id_caja_actual))

            conexion.commit()
            conexion.close()

            # Actualizar interfaz
            self.actualizar_estado_caja()

            # Recargar movimientos si estamos en esa pestaña
            if hasattr(self, 'cargar_movimientos'):
                self.cargar_movimientos()

            messagebox.showinfo(
                "Registro Exitoso",
                f"Se ha registrado un egreso de ${monto:.2f} por concepto de {concepto}"
            )

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el egreso: {str(e)}")
            print(f"Error al registrar egreso: {e}")

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

    def cargar_cortes(self):
        try:
            # 1. Limpiar tabla (método más confiable)
            for item in self.tabla_cortes.get_children():
                self.tabla_cortes.delete(item)

            # 2. Obtener fecha (formato YYYY-MM-DD)
            fecha = self.fecha_cortes.get()
            print(f"DEBUG - Buscando cortes para: {fecha}")  # Verificar en consola

            # 3. Consulta SQL (sencilla y directa)
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_caja, fecha, hora_apertura, 
                       IFNULL(hora_cierre, 'Abierta'), 
                       total_ingresos, total_egresos, 
                       saldo_final, IFNULL(responsable, 'Sistema')
                FROM caja 
                WHERE fecha = %s
                ORDER BY hora_apertura DESC
            """, (fecha,))

            # 4. Insertar datos (¡Verificar que los índices coincidan!)
            for row in cursor.fetchall():
                self.tabla_cortes.insert("", "end", values=(
                    row[0],  # id_caja
                    row[1].strftime("%d/%m/%Y") if isinstance(row[1], date) else str(row[1]),  # fecha
                    str(row[2]),  # hora_apertura
                    str(row[3]),  # cierre
                    f"${row[4]:.2f}",  # ingresos
                    f"${row[5]:.2f}",  # egresos
                    f"${row[6]:.2f}",  # saldo
                    str(row[7])  # responsable
                ))

            conexion.close()

            # 5. Forzar actualización visual (¡CRÍTICO!)
            self.tabla_cortes.update_idletasks()
            print(f"DEBUG - Filas insertadas: {len(self.tabla_cortes.get_children())}")  # Debe ser 11

        except Exception as e:
            print(f"ERROR: {str(e)}")
            messagebox.showerror("Error", f"Error al cargar cortes:\n{str(e)}")

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

    # Modificar el método configurar_tab_operaciones para agregar el botón de resumen de ventas
    def configurar_tab_operaciones(self):
        """Configura la pestaña de operaciones de caja como punto de venta"""
        frame_principal = tk.Frame(self.tab_operaciones, bg="#f5f5f5")
        frame_principal.pack(fill=tk.BOTH, expand=True, pady=20)

        if not self.caja_abierta:
            # Si la caja está cerrada, mostrar solo botón de apertura
            frame_apertura = tk.Frame(frame_principal, bg="#f5f5f5")
            frame_apertura.pack(expand=True)

            btn_abrir = tk.Button(
                frame_apertura,
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
                frame_apertura,
                text="Debe abrir la caja para comenzar a operar",
                font=("Helvetica", 11),
                bg="#f5f5f5",
                fg="#666"
            )
            lbl_info.pack(pady=5)
        else:
            # Si la caja está abierta, mostrar punto de venta completo
            # Panel de operaciones principales (lado izquierdo)
            frame_izquierdo = tk.Frame(frame_principal, bg="#f0f7ff", relief=tk.GROOVE, bd=1)
            frame_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

            tk.Label(
                frame_izquierdo,
                text="VENTAS RÁPIDAS",
                font=("Helvetica", 12, "bold"),
                bg="#f0f7ff",
                fg="#303f9f"
            ).pack(pady=5)

            # Botones de operaciones rápidas
            frame_botones_rapidos = tk.Frame(frame_izquierdo, bg="#f0f7ff")
            frame_botones_rapidos.pack(fill=tk.X, pady=10, padx=10)

            btn_nueva_venta = tk.Button(
                frame_botones_rapidos,
                text="💰 Nueva Venta",
                font=("Helvetica", 12),
                bg="#4caf50",
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                command=self.nueva_venta
            )
            btn_nueva_venta.grid(row=0, column=0, padx=5, pady=5)

            btn_nuevo_pedido = tk.Button(
                frame_botones_rapidos,
                text="📋 Nuevo Pedido",
                font=("Helvetica", 12),
                bg="#2196f3",
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                command=self.nuevo_pedido
            )
            btn_nuevo_pedido.grid(row=0, column=1, padx=5, pady=5)

            btn_seguimiento = tk.Button(
                frame_botones_rapidos,
                text="📊 Seguimiento",
                font=("Helvetica", 12),
                bg="#ff9800",
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                command=self.seguimiento_pedidos
            )
            btn_seguimiento.grid(row=1, column=0, padx=5, pady=5)

            btn_clientes = tk.Button(
                frame_botones_rapidos,
                text="👥 Clientes",
                font=("Helvetica", 12),
                bg="#9c27b0",
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                command=self.gestionar_clientes
            )
            btn_clientes.grid(row=1, column=1, padx=5, pady=5)

            # Panel de control de caja (lado derecho)
            frame_derecho = tk.Frame(frame_principal, bg="#f5f5f5", relief=tk.GROOVE, bd=1)
            frame_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

            tk.Label(
                frame_derecho,
                text="CONTROL DE CAJA",
                font=("Helvetica", 12, "bold"),
                bg="#f5f5f5",
                fg="#e53935"
            ).pack(pady=5)

            # Botones de control de caja
            frame_control_caja = tk.Frame(frame_derecho, bg="#f5f5f5")
            frame_control_caja.pack(fill=tk.X, pady=10, padx=10)

            btn_ingreso = tk.Button(
                frame_control_caja,
                text="➕ Registrar Ingreso",
                font=("Helvetica", 12),
                bg="#4caf50",
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                command=self.registrar_ingreso
            )
            btn_ingreso.grid(row=0, column=0, padx=5, pady=5)

            btn_egreso = tk.Button(
                frame_control_caja,
                text="➖ Registrar Egreso",
                font=("Helvetica", 12),
                bg="#f44336",
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                command=self.registrar_egreso
            )
            btn_egreso.grid(row=1, column=0, padx=5, pady=5)

            btn_resumen = tk.Button(
                frame_control_caja,
                text="📈 Resumen del Día",
                font=("Helvetica", 12),
                bg="#607d8b",
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                command=self.resumen_dia
            )
            btn_resumen.grid(row=2, column=0, padx=5, pady=5)

            btn_cerrar = tk.Button(
                frame_control_caja,
                text="🔒 Cerrar Caja",
                font=("Helvetica", 12, "bold"),
                bg="#795548",
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                command=self.cerrar_caja
            )
            btn_cerrar.grid(row=3, column=0, padx=5, pady=10)

            # Estado actual rápido
            frame_estado_rapido = tk.Frame(frame_derecho, bg="#f0f7ff", padx=10, pady=5)
            frame_estado_rapido.pack(fill=tk.X, pady=10)

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
        """Abre el módulo de ventas embebido en esta ventana"""
        try:
            from ventas import Ventas
            # Crear una instancia de ventas dentro de la ventana actual
            Ventas(self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir ventas: {str(e)}")

    def nuevo_pedido(self):
        """Abre el módulo de pedidos"""
        try:
            from pedidos import Pedidos
            Pedidos(self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir pedidos: {str(e)}")

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

    # Modificar el método cargar_movimientos para mostrar información más detallada
    def cargar_movimientos(self):
        """Carga los movimientos de caja según los filtros seleccionados"""
        try:
            # Limpiar tabla si existe
            if hasattr(self, 'tabla_movimientos'):
                for item in self.tabla_movimientos.get_children():
                    self.tabla_movimientos.delete(item)

            # Obtener parámetros de filtro
            fecha = self.fecha_movimientos.get() if hasattr(self, 'fecha_movimientos') else date.today().strftime(
                "%Y-%m-%d")
            tipo = self.tipo_movimiento.get() if hasattr(self, 'tipo_movimiento') else "Todos"

            # Validar fecha
            try:
                datetime.strptime(fecha, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha incorrecto. Use YYYY-MM-DD")
                return

            # Conectar a la BD
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Consulta más simple
            consulta = """
                SELECT 
                    m.id_movimiento, 
                    m.hora, 
                    m.tipo, 
                    m.concepto,
                    m.monto, 
                    u.nombre,
                    CASE 
                        WHEN m.concepto LIKE 'Venta #%' THEN
                            (SELECT c.nombre 
                             FROM ventas v 
                             JOIN clientes c ON v.id_cliente = c.id_cliente 
                             WHERE m.concepto LIKE CONCAT('Venta #', v.id_venta, '%')
                             LIMIT 1)
                        ELSE NULL
                    END as cliente_nombre
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

            # Ejecutar consulta
            cursor.execute(consulta, parametros)
            movimientos = cursor.fetchall()

            # Calcular totales
            total_ing = 0
            total_egr = 0

            # Insertar datos en la tabla si existe
            if hasattr(self, 'tabla_movimientos'):
                for mov in movimientos:
                    id_mov, hora, tipo_mov, concepto, monto, usuario, cliente_nombre = mov

                    # Formatear hora
                    hora_str = hora.strftime("%H:%M:%S") if isinstance(hora, datetime) else str(hora)

                    # Agregar información del cliente si existe
                    if cliente_nombre:
                        concepto_completo = f"{concepto} - {cliente_nombre}"
                    else:
                        concepto_completo = concepto

                    # Resaltar ventas con color
                    tags = ()
                    if "Venta #" in concepto:
                        tags = ('venta',)

                    # Agregar a tabla
                    self.tabla_movimientos.insert('', tk.END, values=(
                        id_mov, hora_str, tipo_mov.capitalize(), concepto_completo, f"${monto:.2f}", usuario
                    ), tags=tags)

                    # Acumular totales
                    if tipo_mov.lower() == 'ingreso':
                        total_ing += float(monto)
                    else:
                        total_egr += float(monto)

                # Configurar tags para resaltar ventas
                self.tabla_movimientos.tag_configure('venta', background='#e8f5e9')

                # Actualizar variables de totales si existen
                if hasattr(self, 'total_ingresos'):
                    self.total_ingresos.set(f"${total_ing:.2f}")
                if hasattr(self, 'total_egresos'):
                    self.total_egresos.set(f"${total_egr:.2f}")
                if hasattr(self, 'saldo_del_dia'):
                    self.saldo_del_dia.set(f"${(total_ing - total_egr):.2f}")

            conexion.close()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los movimientos: {str(e)}")
            print(f"Error al cargar movimientos: {e}")

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
                print(f"Caja abierta encontrada: ID {self.id_caja_actual}")  # Debug
            else:
                self.id_caja_actual = None
                self.caja_abierta = False
                print("No hay caja abierta")  # Debug

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al verificar estado de caja: {str(e)}")
            self.caja_abierta = False

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
                conexion.close()

                if caja:
                    fecha, hora_apertura, responsable, ingresos, egresos, saldo = caja
                    fecha_formateada = utl.formatear_fecha(fecha)
                    hora_formateada = hora_apertura.strftime("%H:%M:%S") if hora_apertura else ""

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
        """Método para abrir la caja"""
        try:
            if not self.caja_abierta:
                # Preguntar si desea usar el saldo del último corte
                usar_saldo_anterior = messagebox.askyesno(
                    "Apertura de Caja",
                    "¿Desea iniciar con el saldo del último cierre de caja?"
                )

                monto_inicial = 0.0
                if usar_saldo_anterior:
                    # Obtener el último corte
                    try:
                        conexion = conectar_bd()
                        cursor = conexion.cursor()

                        cursor.execute("""
                            SELECT c.saldo_final 
                            FROM caja c
                            WHERE c.hora_cierre IS NOT NULL
                            ORDER BY c.fecha DESC, c.hora_cierre DESC
                            LIMIT 1
                        """)

                        ultimo_corte = cursor.fetchone()
                        conexion.close()

                        if ultimo_corte and ultimo_corte[0] is not None:
                            monto_inicial = float(ultimo_corte[0])
                            # Preguntar si desea modificar el monto
                            modificar = messagebox.askyesno(
                                "Confirmar Saldo",
                                f"Saldo del último cierre: ${monto_inicial:.2f}\n¿Desea modificar este monto?"
                            )

                            if modificar:
                                monto_inicial = simpledialog.askfloat(
                                    "Modificar Saldo",
                                    "Ingrese el monto inicial en caja:",
                                    initialvalue=monto_inicial,
                                    minvalue=0.0
                                )

                                if monto_inicial is None:
                                    messagebox.showinfo("Cancelado", "Apertura de caja cancelada")
                                    return
                        else:
                            messagebox.showinfo("Información", "No se encontró un corte anterior. Iniciando con $0.00")
                            monto_inicial = 0.0
                    except Exception as e:
                        messagebox.showerror("Error", f"Error al obtener último corte: {str(e)}")
                        monto_inicial = 0.0
                else:
                    # Pedir monto inicial manualmente
                    monto_inicial = simpledialog.askfloat(
                        "Apertura de Caja",
                        "Ingrese el monto inicial en caja:",
                        minvalue=0.0
                    )

                    if monto_inicial is None:
                        messagebox.showinfo("Cancelado", "Apertura de caja cancelada")
                        return

                conexion = conectar_bd()
                cursor = conexion.cursor()

                # Registrar apertura en la tabla de caja
                cursor.execute("""
                    INSERT INTO caja (fecha, hora_apertura, responsable, total_ingresos, total_egresos, saldo_final)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    date.today(),  # Usar objeto date en lugar de string
                    datetime.now().time(),  # Usar objeto time
                    self.id_usuario,
                    0.0,  # Total ingresos inicia en 0
                    0.0,  # Total egresos inicia en 0
                    monto_inicial  # Saldo inicial
                ))

                # Obtener el ID de la caja recién abierta
                self.id_caja_actual = cursor.lastrowid
                self.caja_abierta = True

                # Si hay monto inicial, registrarlo como ingreso
                if monto_inicial > 0:
                    cursor.execute("""
                        INSERT INTO movimientos_caja (id_caja, tipo, concepto, monto, hora, id_usuario)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        self.id_caja_actual,
                        'ingreso',
                        'Saldo inicial' if not usar_saldo_anterior else 'Saldo del cierre anterior',
                        monto_inicial,
                        datetime.now(),
                        self.id_usuario
                    ))

                    # Actualizar el total de ingresos
                    cursor.execute("""
                        UPDATE caja 
                        SET total_ingresos = %s
                        WHERE id_caja = %s
                    """, (monto_inicial, self.id_caja_actual))

                conexion.commit()
                conexion.close()

                mensaje = f"La caja se ha abierto correctamente con un monto inicial de ${monto_inicial:.2f}"
                if usar_saldo_anterior:
                    mensaje += "\n(Saldo del cierre anterior)"

                messagebox.showinfo("Apertura Exitosa", mensaje)

                # Actualizar la interfaz
                self.actualizar_estado_caja()
                self.configurar_tab_operaciones()
            else:
                messagebox.showinfo("Información", "La caja ya se encuentra abierta")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la caja: {str(e)}")
            print(f"Error al abrir caja: {e}")

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
            # En configurar_tab_operaciones()
            btn_abrir = tk.Button(
                frame_botones_principales,
                text="Abrir Caja",
                font=("Helvetica", 12, "bold"),
                bg="#4caf50",
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                command=self.abrir_caja  # NO debe tener paréntesis ni argumentos
            )
            btn_abrir.pack(padx=20, pady=10)
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
                command=self.registrar_ingreso
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

            btn_resumen_ventas = tk.Button(
                frame_botones_principales,
                text="📊 Resumen Ventas",
                font=("Helvetica", 12),
                bg="#9c27b0",
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                command=self.ver_resumen_ventas_dia
            )
            btn_resumen_ventas.grid(row=1, column=0, padx=10, pady=10)

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
            btn_cerrar.grid(row=1, column=1, columnspan=2, padx=10, pady=20)

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

    def registrar_egreso(self):
        """Registra un egreso en la caja actual"""
        try:
            if not self.caja_abierta:
                messagebox.showinfo("Información", "Debe abrir la caja primero")
                return

            # Solicitar información del egreso
            concepto = simpledialog.askstring(
                "Egreso",
                "Ingrese el concepto del egreso:"
            )

            if not concepto:
                return

            monto = simpledialog.askfloat(
                "Egreso",
                "Ingrese el monto del egreso:",
                minvalue=0.01
            )

            if monto is None:
                return

            # Verificar que haya saldo suficiente
            conexion = conectar_bd()
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT monto_inicial + total_ingresos - total_egresos AS saldo_actual
                FROM caja
                WHERE id_caja = %s
            """, (self.id_caja_actual,))

            resultado = cursor.fetchone()

            if resultado and resultado[0] < monto:
                messagebox.showerror(
                    "Saldo Insuficiente",
                    f"No hay saldo suficiente para este egreso.\nSaldo actual: ${resultado[0]:.2f}"
                )
                conexion.close()
                return

            # Registrar en la base de datos
            # Insertar en la tabla de movimientos
            cursor.execute("""
                INSERT INTO movimientos_caja (id_caja, fecha, hora, tipo, concepto, monto, id_usuario)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                self.id_caja_actual,
                date.today().strftime("%Y-%m-%d"),
                datetime.now().strftime("%H:%M:%S"),
                "Egreso",
                concepto,
                monto,
                self.id_usuario
            ))

            # Actualizar el total de egresos en la caja
            cursor.execute("""
                UPDATE caja 
                SET total_egresos = total_egresos + %s,
                    saldo_final = saldo_final - %s
                WHERE id_caja = %s
            """, (monto, monto, self.id_caja_actual))

            conexion.commit()
            conexion.close()

            # Actualizar interfaz
            self.actualizar_estado_caja()

            # Recargar movimientos
            self.cargar_movimientos()

            messagebox.showinfo(
                "Registro Exitoso",
                f"Se ha registrado un egreso de ${monto:.2f} por concepto de {concepto}"
            )

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el egreso: {str(e)}")
            print(f"Error al registrar egreso: {e}")

    def configurar_tab_cortes(self):
        # A. Frame contenedor (para tabla + scrollbar)
        frame_tabla = tk.Frame(self.tab_cortes, bg="#f0f0f0")
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        # B. Treeview - Columnas principales
        self.tabla_cortes = ttk.Treeview(
            frame_tabla,
            columns=("id", "fecha", "apertura", "cierre", "ingresos", "egresos", "saldo", "responsable"),
            show="headings",
            height=15
        )

        # C. Configurar encabezados (¡DEBEN coincidir con los 'values' al insertar!)
        encabezados = [
            ("id", "ID", 50),
            ("fecha", "Fecha", 100),
            ("apertura", "Apertura", 100),
            ("cierre", "Cierre", 100),
            ("ingresos", "Ingresos", 100),
            ("egresos", "Egresos", 100),
            ("saldo", "Saldo", 100),
            ("responsable", "Responsable", 150)
        ]

        for col_id, text, width in encabezados:
            self.tabla_cortes.heading(col_id, text=text)
            self.tabla_cortes.column(col_id, width=width, anchor="center")

        # D. Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_cortes.yview)
        self.tabla_cortes.configure(yscrollcommand=scrollbar.set)

        # E. Posicionamiento (¡ESTE ORDEN IMPORTA!)
        self.tabla_cortes.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # F. Estilo para mejorar visibilidad
        style = ttk.Style()
        style.configure("Treeview", font=('Helvetica', 10), rowheight=25)
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
    def mostrar_calendario(self):
        """Muestra una ventana para seleccionar la fecha"""
        # Crear ventana para el calendario
        ventana_cal = tk.Toplevel(self.ventana)
        ventana_cal.title("Seleccionar Fecha")
        ventana_cal.geometry("300x200")
        ventana_cal.config(bg="#f5f5f5")

        # Centrar la ventana
        utl.centrar_ventana(ventana_cal, 300, 200)
        ventana_cal.transient(self.ventana)
        ventana_cal.grab_set()

        # Frame principal
        frame = tk.Frame(ventana_cal, bg="#f5f5f5", padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Seleccionar fecha:", font=("Helvetica", 12, "bold"), bg="#f5f5f5").pack(pady=(0, 10))

        # Obtener la fecha actual
        fecha_actual = self.fecha_cortes.get()
        try:
            year, month, day = fecha_actual.split("-")
        except:
            hoy = date.today()
            year, month, day = str(hoy.year), str(hoy.month), str(hoy.day)

        # Frame para los controles de fecha
        date_frame = tk.Frame(frame, bg="#f5f5f5")
        date_frame.pack(fill=tk.X, pady=10)

        # Día
        tk.Label(date_frame, text="Día:", bg="#f5f5f5", font=("Helvetica", 11)).pack(side=tk.LEFT, padx=(0, 5))
        combo_dia = ttk.Combobox(date_frame, values=list(range(1, 32)), width=4, state="readonly")
        combo_dia.set(day)
        combo_dia.pack(side=tk.LEFT, padx=5)

        # Mes
        tk.Label(date_frame, text="Mes:", bg="#f5f5f5", font=("Helvetica", 11)).pack(side=tk.LEFT, padx=(10, 5))
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
                 "Noviembre", "Diciembre"]
        combo_mes = ttk.Combobox(date_frame, values=meses, width=12, state="readonly")
        combo_mes.set(meses[int(month) - 1])
        combo_mes.pack(side=tk.LEFT, padx=5)

        # Año
        tk.Label(date_frame, text="Año:", bg="#f5f5f5", font=("Helvetica", 11)).pack(side=tk.LEFT, padx=(10, 5))
        anios = list(range(2020, 2031))
        combo_anio = ttk.Combobox(date_frame, values=anios, width=8, state="readonly")
        combo_anio.set(year)
        combo_anio.pack(side=tk.LEFT, padx=5)

        # Frame para botones
        frame_botones = tk.Frame(frame, bg="#f5f5f5")
        frame_botones.pack(pady=20)

        def aplicar_fecha():
            try:
                dia = int(combo_dia.get())
                mes = meses.index(combo_mes.get()) + 1
                anio = int(combo_anio.get())

                # Validar la fecha
                fecha_obj = date(anio, mes, dia)
                fecha_str = fecha_obj.strftime("%Y-%m-%d")
                self.fecha_cortes.set(fecha_str)
                ventana_cal.destroy()

                # Cargar cortes automáticamente después de seleccionar la fecha
                self.cargar_cortes()

            except ValueError:
                messagebox.showerror("Error", "Fecha inválida. Por favor, selecciona una fecha válida.")

        btn_aplicar = tk.Button(
            frame_botones,
            text="Aplicar",
            bg="#3f51b5",
            fg="white",
            width=10,
            command=aplicar_fecha
        )
        btn_aplicar.pack(side=tk.LEFT, padx=5)

        btn_hoy = tk.Button(
            frame_botones,
            text="Hoy",
            bg="#4caf50",
            fg="white",
            width=10,
            command=lambda: (aplicar_fecha_hoy())
        )
        btn_hoy.pack(side=tk.LEFT, padx=5)

        def aplicar_fecha_hoy():
            hoy = date.today()
            combo_dia.set(hoy.day)
            combo_mes.set(meses[hoy.month - 1])
            combo_anio.set(hoy.year)
            aplicar_fecha()

        btn_cancelar = tk.Button(
            frame_botones,
            text="Cancelar",
            bg="#e53935",
            fg="white",
            width=10,
            command=ventana_cal.destroy
        )
        btn_cancelar.pack(side=tk.LEFT, padx=5)

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

            # Mostrar detalles del corte (similar a ver_ultimo_corte pero con el ID específico)
            self.mostrar_detalle_corte(id_corte)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mostrar el detalle del corte: {str(e)}")
            print(f"Error al mostrar detalle del corte: {e}")

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


    # Agregar este nuevo método para otros ingresos simples
    def otro_ingreso(self):
        """Registra un ingreso simple en la caja"""
        try:
            if not self.caja_abierta:
                messagebox.showinfo("Información", "Debe abrir la caja primero")
                return

            # Solicitar información del ingreso
            concepto = simpledialog.askstring(
                "Otro Ingreso",
                "Ingrese el concepto del ingreso:"
            )

            if not concepto:
                return

            monto = simpledialog.askfloat(
                "Otro Ingreso",
                "Ingrese el monto del ingreso:",
                minvalue=0.01
            )

            if monto is None:
                return

            # Registrar en la base de datos
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Insertar en la tabla de movimientos
            cursor.execute("""
                INSERT INTO movimientos_caja (id_caja, tipo, concepto, monto, hora, id_usuario)
                VALUES (%s, 'ingreso', %s, %s, %s, %s)
            """, (
                self.id_caja_actual,
                concepto,
                monto,
                datetime.now(),
                self.id_usuario
            ))

            # Actualizar el total de ingresos en la caja
            cursor.execute("""
                UPDATE caja 
                SET total_ingresos = total_ingresos + %s,
                    saldo_final = saldo_final + %s
                WHERE id_caja = %s
            """, (monto, monto, self.id_caja_actual))

            conexion.commit()
            conexion.close()

            # Actualizar interfaz
            self.actualizar_estado_caja()

            # Recargar movimientos si estamos en esa pestaña
            if hasattr(self, 'cargar_movimientos'):
                self.cargar_movimientos()

            messagebox.showinfo(
                "Registro Exitoso",
                f"Se ha registrado un ingreso de ${monto:.2f} por concepto de {concepto}"
            )

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el ingreso: {str(e)}")
            print(f"Error al registrar ingreso: {e}")

    def actualizar_vista_tabla(self):
        """Forza la actualización visual de la tabla"""
        if hasattr(self, 'tabla_cortes'):
            self.tabla_cortes.update_idletasks()
            self.ventana.update()
    def configurar_tab_movimientos(self):
        """Configura la pestaña de movimientos de caja"""
        # Frame para filtros
        frame_filtros = tk.Frame(self.tab_movimientos, bg="#f5f5f5")
        frame_filtros.pack(fill=tk.X, pady=10)

        # Filtro por fecha
        tk.Label(
            frame_filtros,
            text="Fecha:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).grid(row=0, column=0, padx=5, pady=5)

        self.fecha_movimientos = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))

        entry_fecha = tk.Entry(
            frame_filtros,
            textvariable=self.fecha_movimientos,
            font=("Helvetica", 11),
            width=12
        )
        entry_fecha.grid(row=0, column=1, padx=5, pady=5)

        # Botón para seleccionar fecha con un calendario
        btn_fecha = tk.Button(
            frame_filtros,
            text="📅",
            font=("Helvetica", 11),
            bg="#3f51b5",
            fg="white",
            cursor="hand2",
            command=self.mostrar_calendario  # Usar el método directamente
        )
        btn_fecha.grid(row=0, column=2, padx=2, pady=5)

        # Resto del código...

        # Filtro por tipo
        tk.Label(
            frame_filtros,
            text="Tipo:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).grid(row=0, column=3, padx=5, pady=5)

        self.tipo_movimiento = tk.StringVar(value="Todos")
        combo_tipo = ttk.Combobox(
            frame_filtros,
            textvariable=self.tipo_movimiento,
            values=["Todos", "Ingreso", "Egreso"],
            width=10,
            state="readonly"
        )
        combo_tipo.grid(row=0, column=4, padx=5, pady=5)

        # Botón de búsqueda
        btn_buscar = tk.Button(
            frame_filtros,
            text="Buscar",
            font=("Helvetica", 11),
            bg="#3f51b5",
            fg="white",
            width=8,
            cursor="hand2",
            command=self.cargar_movimientos
        )
        btn_buscar.grid(row=0, column=5, padx=15, pady=5)

        # Tabla de movimientos
        frame_tabla = tk.Frame(self.tab_movimientos, bg="#f5f5f5")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)

        # Columnas de la tabla
        columnas = ('id', 'hora', 'tipo', 'concepto', 'monto', 'usuario')

        self.tabla_movimientos = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=15)

        # Aplicar estilo a la tabla
        utl.aplicar_estilo_tabla(self.tabla_movimientos)

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
        self.tabla_movimientos.column('tipo', width=100, anchor=tk.CENTER)
        self.tabla_movimientos.column('concepto', width=300)
        self.tabla_movimientos.column('monto', width=100, anchor=tk.E)
        self.tabla_movimientos.column('usuario', width=150)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_movimientos.yview)
        self.tabla_movimientos.configure(yscrollcommand=scrollbar.set)

        # Empaquetar tabla y scrollbar
        self.tabla_movimientos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame para resumen
        frame_resumen = tk.Frame(self.tab_movimientos, bg="#f5f5f5", relief=tk.GROOVE, bd=1)
        frame_resumen.pack(fill=tk.X, pady=10, padx=5)

        # Variables para los totales
        self.total_ingresos = tk.StringVar(value="$0.00")
        self.total_egresos = tk.StringVar(value="$0.00")
        self.saldo_del_dia = tk.StringVar(value="$0.00")

        # Mostrar resumen
        tk.Label(
            frame_resumen,
            text="Total Ingresos:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        tk.Label(
            frame_resumen,
            textvariable=self.total_ingresos,
            font=("Helvetica", 11, "bold"),
            bg="#f5f5f5",
            fg="#388e3c"
        ).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(
            frame_resumen,
            text="Total Egresos:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).grid(row=0, column=2, padx=20, pady=5, sticky=tk.W)

        tk.Label(
            frame_resumen,
            textvariable=self.total_egresos,
            font=("Helvetica", 11, "bold"),
            bg="#f5f5f5",
            fg="#d32f2f"
        ).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        tk.Label(
            frame_resumen,
            text="Saldo del Día:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).grid(row=0, column=4, padx=20, pady=5, sticky=tk.W)

        tk.Label(
            frame_resumen,
            textvariable=self.saldo_del_dia,
            font=("Helvetica", 11, "bold"),
            bg="#f5f5f5"
        ).grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)

        # Botón para imprimir movimientos
        btn_imprimir = tk.Button(
            frame_resumen,
            text="Imprimir Movimientos",
            font=("Helvetica", 11),
            bg="#3f51b5",
            fg="white",
            cursor="hand2",
            command=self.imprimir_movimientos
        )
        btn_imprimir.grid(row=0, column=6, padx=20, pady=5)

        # Cargar movimientos iniciales
        self.cargar_movimientos()

    def configurar_tab_cortes(self):
        """Configura la pestaña de cortes de caja"""
        # Frame para filtros
        frame_filtros = tk.Frame(self.tab_cortes, bg="#f5f5f5")
        frame_filtros.pack(fill=tk.X, pady=10)

        # Filtro por fecha
        tk.Label(
            frame_filtros,
            text="Fecha:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).grid(row=0, column=0, padx=5, pady=5)

        self.fecha_cortes = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))

        entry_fecha_cortes = tk.Entry(
            frame_filtros,
            textvariable=self.fecha_cortes,
            font=("Helvetica", 11),
            width=12
        )
        entry_fecha_cortes.grid(row=0, column=1, padx=5, pady=5)

        # Botón para seleccionar fecha con un calendario (simplificado)
        btn_fecha_cortes = tk.Button(
            frame_filtros,
            text="📅",
            font=("Helvetica", 11),
            bg="#3f51b5",
            fg="white",
            cursor="hand2",
            command=self.mostrar_calendario
        )
        btn_fecha_cortes.grid(row=0, column=2, padx=2, pady=5)

        # Botón de búsqueda
        btn_buscar_cortes = tk.Button(
            frame_filtros,
            text="Buscar",
            font=("Helvetica", 11),
            bg="#3f51b5",
            fg="white",
            width=8,
            cursor="hand2",
            command=self.cargar_cortes
        )
        btn_buscar_cortes.grid(row=0, column=3, padx=15, pady=5)

        # Tabla de cortes
        frame_tabla = tk.Frame(self.tab_cortes, bg="#f5f5f5")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)

        # Columnas de la tabla
        columnas = ('id', 'fecha', 'apertura', 'cierre', 'ingresos', 'egresos', 'saldo', 'responsable')

        self.tabla_cortes = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=15)

        # Aplicar estilo a la tabla
        utl.aplicar_estilo_tabla(self.tabla_cortes)

        # Configurar encabezados
        self.tabla_cortes.heading('id', text='ID')
        self.tabla_cortes.heading('fecha', text='Fecha')
        self.tabla_cortes.heading('apertura', text='Apertura')
        self.tabla_cortes.heading('cierre', text='Cierre')
        self.tabla_cortes.heading('ingresos', text='Ingresos')
        self.tabla_cortes.heading('egresos', text='Egresos')
        self.tabla_cortes.heading('saldo', text='Saldo Final')
        self.tabla_cortes.heading('responsable', text='Responsable')

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
                print(f"Caja abierta encontrada: ID {self.id_caja_actual}")  # Debug
            else:
                self.id_caja_actual = None
                self.caja_abierta = False
                print("No hay caja abierta")  # Debug

            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al verificar estado de caja: {str(e)}")
            self.caja_abierta = False

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
                hora_ap = hora_apertura.strftime("%H:%M:%S") if hora_apertura else ""
                hora_ci = hora_cierre.strftime("%H:%M:%S") if hora_cierre else ""

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

# Agrega esta función al final de tu archivo caja.py

def abrir_caja(self):
    """Método para abrir la caja"""
    try:
        if not self.caja_abierta:
            # Solicitar monto inicial
            monto_inicial = simpledialog.askfloat(
                "Apertura de Caja",
                "Ingrese el monto inicial en caja:",
                minvalue=0.0
            )

            if monto_inicial is not None:
                conexion = conectar_bd()
                cursor = conexion.cursor()

                # Registrar apertura en la tabla de caja - sin usar monto_inicial en caja
                cursor.execute("""
                    INSERT INTO caja (fecha, hora_apertura, responsable, total_ingresos, total_egresos, saldo_final)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    date.today().strftime("%Y-%m-%d"),
                    datetime.now().strftime("%H:%M:%S"),
                    self.id_usuario,
                    0.0,  # Total ingresos inicia en 0
                    0.0,  # Total egresos inicia en 0
                    monto_inicial  # Saldo inicial igual al monto inicial
                ))

                # Obtener el ID de la caja recién abierta
                self.id_caja_actual = cursor.lastrowid
                self.caja_abierta = True  # Establecer el estado ANTES de cualquier otra operación

                # Registrar el monto inicial como un ingreso inicial
                cursor.execute("""
                    INSERT INTO movimientos_caja (id_caja, tipo, concepto, monto, hora, id_usuario)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    self.id_caja_actual,
                    'ingreso',  # Tipo debe ser 'ingreso' o 'egreso' (minúsculas)
                    'Saldo inicial',
                    monto_inicial,
                    datetime.now(),
                    self.id_usuario
                ))

                # Actualizar el total de ingresos y saldo final
                cursor.execute("""
                    UPDATE caja 
                    SET total_ingresos = %s, saldo_final = %s
                    WHERE id_caja = %s
                """, (monto_inicial, monto_inicial, self.id_caja_actual))

                conexion.commit()
                conexion.close()

                messagebox.showinfo(
                    "Apertura Exitosa",
                    f"La caja se ha abierto correctamente con un monto inicial de ${monto_inicial:.2f}"
                )

                # Actualizar la interfaz
                self.actualizar_estado_caja()
                self.configurar_tab_operaciones()
            else:
                messagebox.showinfo("Cancelado", "Apertura de caja cancelada")
        else:
            messagebox.showinfo("Información", "La caja ya se encuentra abierta")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la caja: {str(e)}")
        print(f"Error detallado al abrir caja: {e}")