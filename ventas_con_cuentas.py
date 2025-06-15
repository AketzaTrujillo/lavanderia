"""
Sistema de ventas con cuentas abiertas - Versión simplificada SIN ERRORES
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import mysql.connector
import json

def abrir_ventas_con_cuentas_abiertas(parent_window, usuario_actual):
    """Función principal para abrir ventas con cuentas"""
    try:
        # Crear ventana principal
        ventana = tk.Toplevel(parent_window)
        ventana.title("💰 Sistema de Ventas con Cuentas Abiertas")
        ventana.geometry("1000x700")
        ventana.configure(bg="#f0f4f8")

        # Frame principal
        frame_principal = tk.Frame(ventana, bg="#f0f4f8")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        titulo = tk.Label(frame_principal, text="💰 Sistema de Ventas con Cuentas Abiertas",
                         font=("Arial", 16, "bold"), bg="#f0f4f8", fg="#1f2937")
        titulo.pack(pady=(0, 30))

        # Frame de opciones
        opciones_frame = tk.LabelFrame(frame_principal, text="🎯 Opciones de Venta",
                                      bg="#ffffff", fg="#1f2937", font=("Arial", 12, "bold"))
        opciones_frame.pack(fill=tk.X, pady=(0, 30))

        opciones_inner = tk.Frame(opciones_frame, bg="#ffffff")
        opciones_inner.pack(padx=20, pady=20)

        # Botones de acción principales
        tk.Button(opciones_inner, text="🧾 Crear Nueva Cuenta Abierta",
                 command=lambda: crear_nueva_cuenta(usuario_actual),
                 bg="#2563eb", fg="white", font=("Arial", 12, "bold"),
                 padx=30, pady=15, width=25).pack(pady=(0, 10))

        tk.Button(opciones_inner, text="➕ Agregar a Cuenta Existente",
                 command=lambda: agregar_a_cuenta_existente(usuario_actual),
                 bg="#059669", fg="white", font=("Arial", 12, "bold"),
                 padx=30, pady=15, width=25).pack(pady=(0, 10))

        tk.Button(opciones_inner, text="💰 Venta Directa (Sistema Normal)",
                 command=lambda: venta_directa(),
                 bg="#d97706", fg="white", font=("Arial", 12, "bold"),
                 padx=30, pady=15, width=25).pack(pady=(0, 10))

        tk.Button(opciones_inner, text="📋 Ver Cuentas Activas",
                 command=lambda: ver_cuentas_activas(),
                 bg="#7c3aed", fg="white", font=("Arial", 12, "bold"),
                 padx=30, pady=15, width=25).pack()

        # Información explicativa
        info_frame = tk.LabelFrame(frame_principal, text="ℹ️ ¿Cómo Funciona?",
                                  bg="#ffffff", fg="#1f2937", font=("Arial", 12, "bold"))
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        info_text = """
        🎯 NUEVO SISTEMA DE CUENTAS ABIERTAS:
        
        ✅ Para clientes que van agregando servicios progresivamente
        ✅ Múltiples clientes pueden tener cuentas simultáneamente  
        ✅ Se paga al final cuando el cliente termina
        ✅ Integración automática con tu sistema de caja
        
        🔄 FLUJO TÍPICO:
        1. Cliente llega → Crear Nueva Cuenta Abierta
        2. Cliente pide más cosas → Agregar a Cuenta Existente  
        3. Cliente termina → Ir a "Cuentas Abiertas" y cerrar cuenta
        4. Sistema genera venta automáticamente
        
        💡 CASOS PERFECTOS:
        • "Quiero lavado... tal vez después pida planchado"
        • Familias que van trayendo ropa en diferentes momentos
        • Múltiples mesas/clientes al mismo tiempo
        """

        info_label = tk.Label(info_frame, text=info_text,
                             font=("Arial", 10), bg="#ffffff", fg="#374151",
                             justify=tk.LEFT, wraplength=900)
        info_label.pack(padx=20, pady=20)

        # Botón cerrar
        tk.Button(frame_principal, text="❌ Cerrar",
                 command=ventana.destroy,
                 bg="#dc2626", fg="white", font=("Arial", 10, "bold"),
                 padx=20, pady=8).pack(pady=20)

        def crear_nueva_cuenta(usuario_actual):
            """Crea una nueva cuenta abierta"""
            try:
                # Solicitar datos
                numero_cuenta = simpledialog.askstring("Nueva Cuenta",
                                                       "Número/Nombre de la cuenta:\n(Ejemplo: Mesa 1, Cliente A)")
                if not numero_cuenta:
                    return

                nombre_cliente = simpledialog.askstring("Cliente", "Nombre del cliente:")
                if not nombre_cliente:
                    return

                # Conectar a BD
                with open('config.json', 'r') as f:
                    config = json.load(f)
                    db_config = config['database']

                conexion = mysql.connector.connect(**db_config)
                cursor = conexion.cursor()

                # Verificar tablas
                cursor.execute("SHOW TABLES LIKE 'cuentas_abiertas'")
                if not cursor.fetchone():
                    messagebox.showerror("Error",
                                       "Tablas no encontradas. Ejecuta primero el script SQL:\n\n"
                                       "CREATE TABLE cuentas_abiertas (...)")
                    conexion.close()
                    return

                # Crear cuenta
                cursor.execute("""
                    INSERT INTO cuentas_abiertas (numero_cuenta, nombre_cliente, total, id_usuario_apertura)
                    VALUES (%s, %s, %s, %s)
                """, (numero_cuenta, nombre_cliente, 0.00, usuario_actual['id_usuario']))

                conexion.commit()
                conexion.close()

                messagebox.showinfo("✅ Cuenta Creada",
                                   f"Nueva cuenta creada exitosamente:\n\n"
                                   f"📋 Cuenta: {numero_cuenta}\n"
                                   f"👤 Cliente: {nombre_cliente}\n"
                                   f"💰 Total inicial: $0.00\n\n"
                                   f"Ahora puedes agregar productos/servicios a esta cuenta.")

            except mysql.connector.Error as e:
                if e.errno == 1062:  # Duplicate entry
                    messagebox.showerror("Error", f"Ya existe una cuenta con el número '{numero_cuenta}'")
                else:
                    messagebox.showerror("Error BD", f"Error de base de datos:\n{str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"Error general:\n{str(e)}")

        def agregar_a_cuenta_existente(usuario_actual):
            """Agrega items a una cuenta existente"""
            try:
                # Conectar y obtener cuentas
                with open('config.json', 'r') as f:
                    config = json.load(f)
                    db_config = config['database']

                conexion = mysql.connector.connect(**db_config)
                cursor = conexion.cursor()

                cursor.execute("""
                    SELECT numero_cuenta, nombre_cliente, total
                    FROM cuentas_abiertas 
                    WHERE estado = 'abierta'
                    ORDER BY fecha_apertura ASC
                """)

                cuentas = cursor.fetchall()

                if not cuentas:
                    messagebox.showinfo("Sin Cuentas", "No hay cuentas abiertas.\nCrea una nueva cuenta primero.")
                    conexion.close()
                    return

                # Mostrar cuentas disponibles
                lista_cuentas = "\n".join([f"• {c[0]} - {c[1]} (${c[2]:.2f})" for c in cuentas])

                cuenta_elegida = simpledialog.askstring("Seleccionar Cuenta",
                                                       f"Cuentas disponibles:\n\n{lista_cuentas}\n\n"
                                                       f"Escribe el número de cuenta:")
                if not cuenta_elegida:
                    conexion.close()
                    return

                # Verificar que la cuenta existe
                cuenta_encontrada = None
                for cuenta in cuentas:
                    if cuenta[0] == cuenta_elegida:
                        cuenta_encontrada = cuenta
                        break

                if not cuenta_encontrada:
                    messagebox.showerror("Error", f"Cuenta '{cuenta_elegida}' no encontrada")
                    conexion.close()
                    return

                # Simular agregar item
                item_nombre = simpledialog.askstring("Agregar Item", "Nombre del producto/servicio:")
                if not item_nombre:
                    conexion.close()
                    return

                item_precio = simpledialog.askfloat("Precio", f"Precio de '{item_nombre}':", initialvalue=10.00)
                if not item_precio:
                    conexion.close()
                    return

                # Actualizar cuenta
                cursor.execute("""
                    UPDATE cuentas_abiertas 
                    SET total = total + %s
                    WHERE numero_cuenta = %s AND estado = 'abierta'
                """, (item_precio, cuenta_elegida))

                conexion.commit()
                conexion.close()

                nuevo_total = cuenta_encontrada[2] + item_precio

                messagebox.showinfo("✅ Item Agregado",
                                   f"Item agregado exitosamente:\n\n"
                                   f"📋 Cuenta: {cuenta_elegida}\n"
                                   f"📦 Item: {item_nombre}\n"
                                   f"💰 Precio: ${item_precio:.2f}\n"
                                   f"💰 Total cuenta: ${nuevo_total:.2f}")

            except Exception as e:
                messagebox.showerror("Error", f"Error al agregar item:\n{str(e)}")

        def venta_directa():
            """Venta directa tradicional"""
            messagebox.showinfo("Venta Directa",
                               "Para ventas directas tradicionales,\n"
                               "usa el botón 'Registrar Ventas' del menú principal.\n\n"
                               "Las cuentas abiertas son para clientes que\n"
                               "van agregando productos progresivamente.")

        def ver_cuentas_activas():
            """Muestra las cuentas activas"""
            try:
                with open('config.json', 'r') as f:
                    config = json.load(f)
                    db_config = config['database']

                conexion = mysql.connector.connect(**db_config)
                cursor = conexion.cursor()

                cursor.execute("""
                    SELECT numero_cuenta, nombre_cliente, total, fecha_apertura
                    FROM cuentas_abiertas 
                    WHERE estado = 'abierta'
                    ORDER BY fecha_apertura ASC
                """)

                cuentas = cursor.fetchall()
                conexion.close()

                if not cuentas:
                    messagebox.showinfo("Sin Cuentas", "No hay cuentas abiertas actualmente.")
                    return

                lista_texto = "📋 CUENTAS ABIERTAS ACTIVAS:\n\n"
                for cuenta in cuentas:
                    numero, cliente, total, fecha = cuenta
                    lista_texto += f"• {numero} - {cliente}\n  💰 ${total:.2f} | 📅 {fecha}\n\n"

                lista_texto += f"Total de cuentas activas: {len(cuentas)}\n\n"
                lista_texto += "💡 Para cerrar cuentas, usa el botón 'Cuentas Abiertas' del menú principal."

                messagebox.showinfo("Cuentas Activas", lista_texto)

            except Exception as e:
                messagebox.showerror("Error", f"Error al obtener cuentas:\n{str(e)}")

    except Exception as e:
        messagebox.showerror("Error", f"Error al abrir ventas con cuentas: {str(e)}")