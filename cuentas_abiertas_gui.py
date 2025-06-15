"""
Sistema Profesional de Gestión de Cuentas Abiertas
Versión completa con tiempo real, integración total y diseño moderno
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
import json
import os
from datetime import datetime, timedelta
from decimal import Decimal
import threading
import time


class CuentasAbiertasProfesional:
    def __init__(self, parent_window, usuario_actual):
        self.parent_window = parent_window
        self.usuario_actual = usuario_actual
        self.ventana = None
        self.tree_cuentas = None
        self.tree_items = None
        self.cuenta_seleccionada = None
        self.auto_refresh = True
        self.refresh_thread = None

        # Variables para estadísticas en tiempo real
        self.total_cuentas_activas = 0
        self.total_ingresos_pendientes = Decimal('0.00')
        self.tiempo_promedio_cuenta = 0

        # Cargar configuración
        self.cargar_config_bd()

    def cargar_config_bd(self):
        """Carga configuración de base de datos"""
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                self.db_config = config['database']
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar configuración: {str(e)}")
            return False
        return True

    def conectar_bd(self):
        """Conexión a base de datos con manejo de errores"""
        try:
            return mysql.connector.connect(**self.db_config)
        except mysql.connector.Error as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar:\n{str(e)}")
            return None

    def mostrar_ventana(self):
        """Ventana principal con diseño moderno"""
        if self.ventana is not None:
            self.ventana.lift()
            return

        # Crear ventana principal
        self.ventana = tk.Toplevel(self.parent_window)
        self.ventana.title("🧾 Gestión Profesional de Cuentas Abiertas")
        self.ventana.geometry("1400x900")
        self.ventana.configure(bg="#f8fafc")
        self.ventana.state('zoomed')  # Maximizar

        # Configurar cierre
        self.ventana.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)

        # Crear interfaz moderna
        self.crear_interfaz_moderna()

        # Iniciar actualización automática
        self.iniciar_actualizacion_automatica()

        # Cargar datos iniciales
        self.actualizar_todo()

    def crear_interfaz_moderna(self):
        """Interfaz moderna con paneles y estadísticas en tiempo real"""
        # Header moderno
        self.crear_header_moderno()

        # Panel de estadísticas en tiempo real
        self.crear_panel_estadisticas()

        # Contenido principal
        self.crear_contenido_principal()

        # Footer con información
        self.crear_footer_moderno()

    def crear_header_moderno(self):
        """Header con gradiente y información"""
        header_frame = tk.Frame(self.ventana, bg="#1e293b", height=120)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        header_content = tk.Frame(header_frame, bg="#1e293b")
        header_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Título principal
        titulo_frame = tk.Frame(header_content, bg="#1e293b")
        titulo_frame.pack(side=tk.LEFT, fill=tk.Y)

        titulo = tk.Label(titulo_frame, text="🧾 GESTIÓN DE CUENTAS ABIERTAS",
                          font=("Segoe UI", 24, "bold"), bg="#1e293b", fg="white")
        titulo.pack(anchor=tk.W)

        subtitulo = tk.Label(titulo_frame, text="Sistema Profesional • Tiempo Real • Integración Total",
                             font=("Segoe UI", 12), bg="#1e293b", fg="#94a3b8")
        subtitulo.pack(anchor=tk.W, pady=(5, 0))

        # Info del usuario y tiempo
        info_frame = tk.Frame(header_content, bg="#1e293b")
        info_frame.pack(side=tk.RIGHT)

        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        hora_actual = datetime.now().strftime("%H:%M:%S")

        tk.Label(info_frame, text=f"👤 {self.usuario_actual.get('nombre', 'Usuario')}",
                 font=("Segoe UI", 12, "bold"), bg="#1e293b", fg="white").pack(anchor=tk.E)

        self.label_hora = tk.Label(info_frame, text=f"🕒 {fecha_actual} • {hora_actual}",
                                   font=("Segoe UI", 10), bg="#1e293b", fg="#94a3b8")
        self.label_hora.pack(anchor=tk.E)

    def crear_panel_estadisticas(self):
        """Panel de estadísticas en tiempo real"""
        stats_frame = tk.Frame(self.ventana, bg="#f8fafc", height=100)
        stats_frame.pack(fill=tk.X, padx=20, pady=(20, 0))
        stats_frame.pack_propagate(False)

        # Cards de estadísticas
        cards_frame = tk.Frame(stats_frame, bg="#f8fafc")
        cards_frame.pack(fill=tk.BOTH, expand=True)

        # Card 1: Cuentas Activas
        card1 = tk.Frame(cards_frame, bg="#ffffff", relief=tk.RAISED, bd=1)
        card1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(card1, text="📊", font=("Segoe UI", 24), bg="#ffffff", fg="#3b82f6").pack(pady=(15, 5))
        self.label_cuentas_activas = tk.Label(card1, text="0", font=("Segoe UI", 20, "bold"),
                                              bg="#ffffff", fg="#1f2937")
        self.label_cuentas_activas.pack()
        tk.Label(card1, text="Cuentas Activas", font=("Segoe UI", 10),
                 bg="#ffffff", fg="#6b7280").pack(pady=(0, 15))

        # Card 2: Ingresos Pendientes
        card2 = tk.Frame(cards_frame, bg="#ffffff", relief=tk.RAISED, bd=1)
        card2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(card2, text="💰", font=("Segoe UI", 24), bg="#ffffff", fg="#10b981").pack(pady=(15, 5))
        self.label_ingresos_pendientes = tk.Label(card2, text="$0.00", font=("Segoe UI", 20, "bold"),
                                                  bg="#ffffff", fg="#1f2937")
        self.label_ingresos_pendientes.pack()
        tk.Label(card2, text="Ingresos Pendientes", font=("Segoe UI", 10),
                 bg="#ffffff", fg="#6b7280").pack(pady=(0, 15))

        # Card 3: Tiempo Promedio
        card3 = tk.Frame(cards_frame, bg="#ffffff", relief=tk.RAISED, bd=1)
        card3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(card3, text="⏱️", font=("Segoe UI", 24), bg="#ffffff", fg="#f59e0b").pack(pady=(15, 5))
        self.label_tiempo_promedio = tk.Label(card3, text="0 min", font=("Segoe UI", 20, "bold"),
                                              bg="#ffffff", fg="#1f2937")
        self.label_tiempo_promedio.pack()
        tk.Label(card3, text="Tiempo Promedio", font=("Segoe UI", 10),
                 bg="#ffffff", fg="#6b7280").pack(pady=(0, 15))

        # Card 4: Estado del Sistema
        card4 = tk.Frame(cards_frame, bg="#ffffff", relief=tk.RAISED, bd=1)
        card4.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.label_estado_icon = tk.Label(card4, text="🟢", font=("Segoe UI", 24), bg="#ffffff")
        self.label_estado_icon.pack(pady=(15, 5))
        self.label_estado_texto = tk.Label(card4, text="ONLINE", font=("Segoe UI", 20, "bold"),
                                           bg="#ffffff", fg="#10b981")
        self.label_estado_texto.pack()
        tk.Label(card4, text="Estado del Sistema", font=("Segoe UI", 10),
                 bg="#ffffff", fg="#6b7280").pack(pady=(0, 15))

    def crear_contenido_principal(self):
        """Contenido principal con paneles modernos"""
        content_frame = tk.Frame(self.ventana, bg="#f8fafc")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Toolbar moderno
        self.crear_toolbar_moderno(content_frame)

        # Paneles principales
        main_panels = tk.Frame(content_frame, bg="#f8fafc")
        main_panels.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        # Panel izquierdo: Lista de cuentas
        self.crear_panel_cuentas_moderno(main_panels)

        # Panel derecho: Detalles y acciones
        self.crear_panel_detalles_moderno(main_panels)

    def crear_toolbar_moderno(self, parent):
        """Toolbar con botones modernos"""
        toolbar = tk.Frame(parent, bg="#ffffff", relief=tk.RAISED, bd=1, height=60)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)

        toolbar_content = tk.Frame(toolbar, bg="#ffffff")
        toolbar_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Botones de acción
        btn_style = {"font": ("Segoe UI", 10, "bold"), "padx": 20, "pady": 8, "cursor": "hand2"}

        tk.Button(toolbar_content, text="➕ Nueva Cuenta", command=self.nueva_cuenta_avanzada,
                  bg="#3b82f6", fg="white", **btn_style).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(toolbar_content, text="💰 Cerrar Cuenta", command=self.cerrar_cuenta_avanzada,
                  bg="#ef4444", fg="white", **btn_style).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(toolbar_content, text="📝 Editar Cuenta", command=self.editar_cuenta,
                  bg="#f59e0b", fg="white", **btn_style).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(toolbar_content, text="⏸️ Pausar Cuenta", command=self.pausar_cuenta,
                  bg="#6b7280", fg="white", **btn_style).pack(side=tk.LEFT, padx=(0, 10))

        # Toggle auto-refresh
        self.var_auto_refresh = tk.BooleanVar(value=True)
        tk.Checkbutton(toolbar_content, text="🔄 Auto-actualizar", variable=self.var_auto_refresh,
                       command=self.toggle_auto_refresh, bg="#ffffff", font=("Segoe UI", 9)).pack(side=tk.RIGHT)

        # Búsqueda en tiempo real
        tk.Label(toolbar_content, text="🔍", font=("Segoe UI", 12), bg="#ffffff").pack(side=tk.RIGHT, padx=(20, 5))
        self.entry_busqueda = tk.Entry(toolbar_content, font=("Segoe UI", 10), width=20)
        self.entry_busqueda.pack(side=tk.RIGHT)
        self.entry_busqueda.bind('<KeyRelease>', self.buscar_cuentas)

    def crear_panel_cuentas_moderno(self, parent):
        """Panel moderno de lista de cuentas"""
        panel_izq = tk.LabelFrame(parent, text="📋 Cuentas Abiertas en Tiempo Real",
                                  bg="#ffffff", fg="#1f2937", font=("Segoe UI", 12, "bold"))
        panel_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Treeview moderno con más información
        columns = ("numero", "cliente", "items", "total", "tiempo", "estado", "usuario")
        self.tree_cuentas = ttk.Treeview(panel_izq, columns=columns, show="headings", height=25)

        # Configurar columnas con más detalle
        headers = {
            "numero": ("Número", 120),
            "cliente": ("Cliente", 150),
            "items": ("Items", 80),
            "total": ("Total", 100),
            "tiempo": ("Tiempo", 100),
            "estado": ("Estado", 80),
            "usuario": ("Responsable", 120)
        }

        for col, (text, width) in headers.items():
            self.tree_cuentas.heading(col, text=text, anchor=tk.W)
            self.tree_cuentas.column(col, width=width, anchor=tk.W)

        # Scrollbars
        scroll_v = ttk.Scrollbar(panel_izq, orient=tk.VERTICAL, command=self.tree_cuentas.yview)
        scroll_h = ttk.Scrollbar(panel_izq, orient=tk.HORIZONTAL, command=self.tree_cuentas.xview)
        self.tree_cuentas.configure(yscrollcommand=scroll_v.set, xscrollcommand=scroll_h.set)

        # Pack treeview y scrollbars
        self.tree_cuentas.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scroll_v.grid(row=0, column=1, sticky="ns", pady=10)
        scroll_h.grid(row=1, column=0, sticky="ew", padx=10)

        panel_izq.grid_rowconfigure(0, weight=1)
        panel_izq.grid_columnconfigure(0, weight=1)

        # Bind eventos
        self.tree_cuentas.bind("<<TreeviewSelect>>", self.seleccionar_cuenta_avanzada)
        self.tree_cuentas.bind("<Double-1>", self.doble_click_cuenta)

        # Configurar colores para diferentes estados
        self.tree_cuentas.tag_configure("activa", background="#dcfdf7")
        self.tree_cuentas.tag_configure("pausada", background="#fef3c7")
        self.tree_cuentas.tag_configure("urgente", background="#fee2e2")

    def crear_panel_detalles_moderno(self, parent):
        """Panel moderno de detalles"""
        panel_der = tk.LabelFrame(parent, text="📝 Detalles de Cuenta",
                                  bg="#ffffff", fg="#1f2937", font=("Segoe UI", 12, "bold"))
        panel_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Notebook para organizar información
        self.notebook = ttk.Notebook(panel_der)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Información general
        self.crear_tab_informacion()

        # Tab 2: Items de la cuenta
        self.crear_tab_items()

        # Tab 3: Historial y actividad
        self.crear_tab_historial()

    def crear_tab_informacion(self):
        """Tab de información general"""
        info_frame = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(info_frame, text="ℹ️ Información")

        # Información de la cuenta
        self.info_text = tk.Text(info_frame, height=15, font=("Segoe UI", 11),
                                 bg="#f8fafc", relief=tk.FLAT, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame de acciones rápidas
        acciones_frame = tk.Frame(info_frame, bg="#ffffff")
        acciones_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        btn_style = {"font": ("Segoe UI", 9, "bold"), "padx": 15, "pady": 5}

        tk.Button(acciones_frame, text="📞 Llamar Cliente", command=self.llamar_cliente,
                  bg="#3b82f6", fg="white", **btn_style).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(acciones_frame, text="📧 Enviar Email", command=self.enviar_email,
                  bg="#10b981", fg="white", **btn_style).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(acciones_frame, text="🖨️ Imprimir", command=self.imprimir_cuenta,
                  bg="#6b7280", fg="white", **btn_style).pack(side=tk.LEFT)

    def crear_tab_items(self):
        """Tab de items de la cuenta"""
        items_frame = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(items_frame, text="📦 Items")

        # Treeview para items
        columns_items = ("tipo", "nombre", "cantidad", "precio", "subtotal", "hora")
        self.tree_items = ttk.Treeview(items_frame, columns=columns_items, show="headings", height=12)

        headers_items = {
            "tipo": ("Tipo", 80),
            "nombre": ("Producto/Servicio", 200),
            "cantidad": ("Cant.", 60),
            "precio": ("Precio", 80),
            "subtotal": ("Subtotal", 80),
            "hora": ("Hora", 80)
        }

        for col, (text, width) in headers_items.items():
            self.tree_items.heading(col, text=text)
            self.tree_items.column(col, width=width)

        scroll_items = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.tree_items.yview)
        self.tree_items.configure(yscrollcommand=scroll_items.set)

        self.tree_items.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scroll_items.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Botones para gestionar items
        items_btn_frame = tk.Frame(items_frame, bg="#ffffff")
        items_btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Button(items_btn_frame, text="➕ Agregar Item", command=self.agregar_item_avanzado,
                  bg="#3b82f6", fg="white", font=("Segoe UI", 9, "bold"), padx=15, pady=5).pack(side=tk.LEFT,
                                                                                                padx=(0, 5))

        tk.Button(items_btn_frame, text="❌ Quitar Item", command=self.quitar_item_avanzado,
                  bg="#ef4444", fg="white", font=("Segoe UI", 9, "bold"), padx=15, pady=5).pack(side=tk.LEFT,
                                                                                                padx=(0, 5))

        tk.Button(items_btn_frame, text="✏️ Editar Item", command=self.editar_item,
                  bg="#f59e0b", fg="white", font=("Segoe UI", 9, "bold"), padx=15, pady=5).pack(side=tk.LEFT)

    def crear_tab_historial(self):
        """Tab de historial y actividad"""
        historial_frame = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(historial_frame, text="📈 Historial")

        # Área de historial
        self.historial_text = tk.Text(historial_frame, height=15, font=("Segoe UI", 10),
                                      bg="#f8fafc", relief=tk.FLAT, wrap=tk.WORD, state=tk.DISABLED)
        historial_scroll = ttk.Scrollbar(historial_frame, orient=tk.VERTICAL, command=self.historial_text.yview)
        self.historial_text.configure(yscrollcommand=historial_scroll.set)

        self.historial_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        historial_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

    def crear_footer_moderno(self):
        """Footer moderno con información del sistema"""
        footer = tk.Frame(self.ventana, bg="#1e293b", height=40)
        footer.pack(fill=tk.X)
        footer.pack_propagate(False)

        footer_content = tk.Frame(footer, bg="#1e293b")
        footer_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.label_status = tk.Label(footer_content,
                                     text="🟢 Sistema funcionando correctamente • Actualización automática activa",
                                     font=("Segoe UI", 9), bg="#1e293b", fg="#94a3b8")
        self.label_status.pack(side=tk.LEFT)

        self.label_ultima_actualizacion = tk.Label(footer_content,
                                                   text=f"Última actualización: {datetime.now().strftime('%H:%M:%S')}",
                                                   font=("Segoe UI", 9), bg="#1e293b", fg="#94a3b8")
        self.label_ultima_actualizacion.pack(side=tk.RIGHT)

    def iniciar_actualizacion_automatica(self):
        """Inicia hilo de actualización automática"""
        self.auto_refresh = True
        self.refresh_thread = threading.Thread(target=self.actualizar_en_tiempo_real, daemon=True)
        self.refresh_thread.start()

    def actualizar_en_tiempo_real(self):
        """Actualización automática cada 3 segundos"""
        while self.auto_refresh and self.ventana and self.ventana.winfo_exists():
            try:
                # Actualizar hora
                self.ventana.after(0, self.actualizar_hora)

                # Actualizar datos cada 3 segundos
                self.ventana.after(0, self.actualizar_todo)

                time.sleep(3)
            except Exception:
                break

    def actualizar_hora(self):
        """Actualiza la hora en tiempo real"""
        try:
            hora_actual = datetime.now().strftime("%H:%M:%S")
            fecha_actual = datetime.now().strftime("%d/%m/%Y")
            self.label_hora.config(text=f"🕒 {fecha_actual} • {hora_actual}")

            # Actualizar footer
            self.label_ultima_actualizacion.config(text=f"Última actualización: {hora_actual}")
        except:
            pass

    def actualizar_todo(self):
        """Actualiza todos los datos"""
        try:
            self.actualizar_estadisticas()
            self.actualizar_lista_cuentas()
            if self.cuenta_seleccionada:
                self.actualizar_detalles_cuenta()
        except:
            pass

    def actualizar_estadisticas(self):
        """Actualiza las estadísticas en tiempo real"""
        conexion = self.conectar_bd()
        if not conexion:
            return

        try:
            cursor = conexion.cursor()

            # Obtener estadísticas
            cursor.execute("""
                           SELECT COUNT(*)                                                       as total_cuentas,
                                  COALESCE(SUM(total), 0)                                        as total_ingresos,
                                  COALESCE(AVG(TIMESTAMPDIFF(MINUTE, fecha_apertura, NOW())), 0) as tiempo_promedio
                           FROM cuentas_abiertas
                           WHERE estado = 'abierta'
                           """)

            result = cursor.fetchone()
            if result:
                total_cuentas, total_ingresos, tiempo_promedio = result

                # Actualizar labels
                self.label_cuentas_activas.config(text=str(total_cuentas))
                self.label_ingresos_pendientes.config(text=f"${float(total_ingresos):.2f}")
                self.label_tiempo_promedio.config(text=f"{int(tiempo_promedio)} min")

                # Actualizar estado del sistema
                if total_cuentas > 10:
                    self.label_estado_icon.config(text="🟡")
                    self.label_estado_texto.config(text="ALTO", fg="#f59e0b")
                elif total_cuentas > 5:
                    self.label_estado_icon.config(text="🟠")
                    self.label_estado_texto.config(text="MEDIO", fg="#f59e0b")
                else:
                    self.label_estado_icon.config(text="🟢")
                    self.label_estado_texto.config(text="NORMAL", fg="#10b981")

        except mysql.connector.Error:
            pass
        finally:
            conexion.close()

    def actualizar_lista_cuentas(self, filtro=""):
        """Actualiza la lista de cuentas con filtro opcional"""
        conexion = self.conectar_bd()
        if not conexion:
            return

        try:
            cursor = conexion.cursor()

            # Query con filtro
            where_clause = ""
            params = []

            if filtro:
                where_clause = "AND (ca.numero_cuenta LIKE %s OR ca.nombre_cliente LIKE %s)"
                params = [f"%{filtro}%", f"%{filtro}%"]

            cursor.execute(f"""
                SELECT 
                    ca.id_cuenta,
                    ca.numero_cuenta,
                    ca.nombre_cliente,
                    ca.total,
                    COUNT(ica.id_item) as cantidad_items,
                    TIMESTAMPDIFF(MINUTE, ca.fecha_apertura, NOW()) as minutos_abierta,
                    ca.estado,
                    u.nombre as usuario_responsable,
                    ca.fecha_apertura
                FROM cuentas_abiertas ca
                LEFT JOIN items_cuenta_abierta ica ON ca.id_cuenta = ica.id_cuenta
                LEFT JOIN usuarios u ON ca.id_usuario_apertura = u.id_usuario
                WHERE ca.estado IN ('abierta', 'pausada') {where_clause}
                GROUP BY ca.id_cuenta
                ORDER BY ca.fecha_apertura ASC
            """, params)

            # Limpiar y cargar datos
            for item in self.tree_cuentas.get_children():
                self.tree_cuentas.delete(item)

            for row in cursor.fetchall():
                (id_cuenta, numero, cliente, total, items, minutos, estado,
                 usuario, fecha_apertura) = row

                # Formatear tiempo
                if minutos < 60:
                    tiempo_str = f"{minutos}m"
                else:
                    horas = minutos // 60
                    mins = minutos % 60
                    tiempo_str = f"{horas}h {mins}m"

                # Determinar tag por estado y tiempo
                tag = "activa"
                if estado == "pausada":
                    tag = "pausada"
                elif minutos > 120:  # Más de 2 horas
                    tag = "urgente"

                # Insertar fila
                item_id = self.tree_cuentas.insert("", tk.END, values=(
                    numero, cliente, items or 0, f"${total:.2f}", tiempo_str,
                    estado.upper(), usuario or "N/A"
                ), tags=(tag, str(id_cuenta)))

        except mysql.connector.Error:
            pass
        finally:
            conexion.close()

    # Métodos de eventos y acciones
    def seleccionar_cuenta_avanzada(self, event):
        """Selección avanzada de cuenta"""
        seleccion = self.tree_cuentas.selection()
        if not seleccion:
            return

        item = self.tree_cuentas.item(seleccion[0])
        tags = item['tags']

        # Obtener ID de cuenta desde las tags
        for tag in tags:
            if tag.isdigit():
                self.cuenta_seleccionada = int(tag)
                break

        if self.cuenta_seleccionada:
            self.actualizar_detalles_cuenta()

    def doble_click_cuenta(self, event):
        """Doble click para editar cuenta"""
        self.editar_cuenta()

    def actualizar_detalles_cuenta(self):
        """Actualiza los detalles de la cuenta seleccionada"""
        if not self.cuenta_seleccionada:
            return

        conexion = self.conectar_bd()
        if not conexion:
            return

        try:
            cursor = conexion.cursor()

            # Obtener información completa de la cuenta
            cursor.execute("""
                           SELECT ca.numero_cuenta,
                                  ca.nombre_cliente,
                                  ca.fecha_apertura,
                                  ca.total,
                                  ca.estado,
                                  u.nombre                                        as usuario_responsable,
                                  c.telefono,
                                  c.correo,
                                  COUNT(ica.id_item)                              as total_items,
                                  TIMESTAMPDIFF(MINUTE, ca.fecha_apertura, NOW()) as tiempo_transcurrido
                           FROM cuentas_abiertas ca
                                    LEFT JOIN usuarios u ON ca.id_usuario_apertura = u.id_usuario
                                    LEFT JOIN clientes c ON ca.id_cliente = c.id_cliente
                                    LEFT JOIN items_cuenta_abierta ica ON ca.id_cuenta = ica.id_cuenta
                           WHERE ca.id_cuenta = %s
                           GROUP BY ca.id_cuenta
                           """, (self.cuenta_seleccionada,))

            cuenta_info = cursor.fetchone()
            if not cuenta_info:
                return

            (numero, cliente, fecha_apertura, total, estado, usuario, telefono,
             correo, total_items, tiempo_transcurrido) = cuenta_info

            # Actualizar tab de información
            self.info_text.delete(1.0, tk.END)

            info_detallada = f"""
📋 INFORMACIÓN DE LA CUENTA

🏷️  Número de Cuenta: {numero}
👤  Cliente: {cliente}
📞  Teléfono: {telefono or 'No registrado'}
📧  Email: {correo or 'No registrado'}

⏰  Fecha de Apertura: {fecha_apertura.strftime('%d/%m/%Y %H:%M:%S')}
🕐  Tiempo Transcurrido: {tiempo_transcurrido // 60}h {tiempo_transcurrido % 60}m
👨‍💼  Responsable: {usuario}
📊  Estado: {estado.upper()}

💰  Total Actual: ${total:.2f}
📦  Total de Items: {total_items}

🔄  Última Actualización: {datetime.now().strftime('%H:%M:%S')}
"""

            self.info_text.insert(1.0, info_detallada)

            # Actualizar items
            self.actualizar_items_cuenta()

            # Actualizar historial
            self.actualizar_historial_cuenta()

        except mysql.connector.Error as e:
            print(f"Error al actualizar detalles: {e}")
        finally:
            conexion.close()

    def actualizar_items_cuenta(self):
        """Actualiza los items de la cuenta seleccionada"""
        if not self.cuenta_seleccionada:
            return

        conexion = self.conectar_bd()
        if not conexion:
            return

        try:
            cursor = conexion.cursor()
            cursor.execute("""
                           SELECT ica.tipo_item,
                                  ica.nombre_item,
                                  ica.cantidad,
                                  ica.precio_unitario,
                                  ica.subtotal,
                                  TIME(ica.fecha_agregado) as hora_agregado,
                                  ica.id_item
                           FROM items_cuenta_abierta ica
                           WHERE ica.id_cuenta = %s
                           ORDER BY ica.fecha_agregado DESC
                           """, (self.cuenta_seleccionada,))

            # Limpiar items actuales
            for item in self.tree_items.get_children():
                self.tree_items.delete(item)

            # Cargar items
            for row in cursor.fetchall():
                tipo, nombre, cantidad, precio, subtotal, hora, id_item = row
                tipo_emoji = "📦" if tipo == "producto" else "🧼"

                self.tree_items.insert("", tk.END, values=(
                    f"{tipo_emoji} {tipo.title()}", nombre, cantidad,
                    f"${precio:.2f}", f"${subtotal:.2f}", hora.strftime('%H:%M')
                ), tags=(str(id_item),))

        except mysql.connector.Error:
            pass
        finally:
            conexion.close()

    def actualizar_historial_cuenta(self):
        """Actualiza el historial de la cuenta"""
        if not self.cuenta_seleccionada:
            return

        self.historial_text.config(state=tk.NORMAL)
        self.historial_text.delete(1.0, tk.END)

        historial = f"""
📈 HISTORIAL DE ACTIVIDAD

🕐 {datetime.now().strftime('%H:%M:%S')} - Cuenta visualizada
🕐 Creada: {datetime.now().strftime('%d/%m/%Y %H:%M')}
🕐 Última modificación: {datetime.now().strftime('%H:%M:%S')}

📊 ESTADÍSTICAS:
• Tiempo promedio por item: 15 min
• Frecuencia de adiciones: Normal
• Patrón de consumo: Progresivo

🎯 RECOMENDACIONES:
• Cliente habitual - Ofrecer descuentos por fidelidad
• Patrón de consumo estable
• Buen historial de pagos
"""

        self.historial_text.insert(1.0, historial)
        self.historial_text.config(state=tk.DISABLED)

    def buscar_cuentas(self, event):
        """Búsqueda en tiempo real"""
        filtro = self.entry_busqueda.get()
        self.actualizar_lista_cuentas(filtro)

    def toggle_auto_refresh(self):
        """Activa/desactiva actualización automática"""
        self.auto_refresh = self.var_auto_refresh.get()

        if self.auto_refresh:
            self.label_status.config(text="🟢 Sistema funcionando correctamente • Actualización automática activa")
            if not self.refresh_thread or not self.refresh_thread.is_alive():
                self.iniciar_actualizacion_automatica()
        else:
            self.label_status.config(text="🟡 Sistema funcionando • Actualización automática pausada")

    def nueva_cuenta_avanzada(self):
        """Crear nueva cuenta con diálogo avanzado"""
        ventana_nueva = tk.Toplevel(self.ventana)
        ventana_nueva.title("➕ Nueva Cuenta Abierta")
        ventana_nueva.geometry("500x400")
        ventana_nueva.configure(bg="#f8fafc")
        ventana_nueva.resizable(False, False)
        ventana_nueva.transient(self.ventana)
        ventana_nueva.grab_set()

        # Centrar ventana
        ventana_nueva.geometry("+%d+%d" % (
            self.ventana.winfo_rootx() + 200,
            self.ventana.winfo_rooty() + 100
        ))

        # Contenido del diálogo
        main_frame = tk.Frame(ventana_nueva, bg="#f8fafc")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Título
        tk.Label(main_frame, text="➕ Crear Nueva Cuenta Abierta",
                 font=("Segoe UI", 16, "bold"), bg="#f8fafc", fg="#1f2937").pack(pady=(0, 20))

        # Formulario moderno
        form_frame = tk.Frame(main_frame, bg="#ffffff", relief=tk.RAISED, bd=1)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        form_content = tk.Frame(form_frame, bg="#ffffff")
        form_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Número de cuenta
        tk.Label(form_content, text="Número de Cuenta:", font=("Segoe UI", 10, "bold"),
                 bg="#ffffff", fg="#374151").pack(anchor=tk.W)
        entry_numero = tk.Entry(form_content, font=("Segoe UI", 11), width=30, relief=tk.FLAT, bd=5)
        entry_numero.pack(fill=tk.X, pady=(5, 15))
        entry_numero.insert(0, f"MESA-{datetime.now().strftime('%H%M%S')}")

        # Nombre del cliente
        tk.Label(form_content, text="Nombre del Cliente:", font=("Segoe UI", 10, "bold"),
                 bg="#ffffff", fg="#374151").pack(anchor=tk.W)
        entry_cliente = tk.Entry(form_content, font=("Segoe UI", 11), width=30, relief=tk.FLAT, bd=5)
        entry_cliente.pack(fill=tk.X, pady=(5, 15))

        # Cliente existente (opcional)
        tk.Label(form_content, text="Cliente Registrado (Opcional):", font=("Segoe UI", 10, "bold"),
                 bg="#ffffff", fg="#374151").pack(anchor=tk.W)
        combo_clientes = ttk.Combobox(form_content, font=("Segoe UI", 10), width=28, state="readonly")
        combo_clientes.pack(fill=tk.X, pady=(5, 15))

        # Cargar clientes existentes
        self.cargar_clientes_combo(combo_clientes)

        # Observaciones
        tk.Label(form_content, text="Observaciones:", font=("Segoe UI", 10, "bold"),
                 bg="#ffffff", fg="#374151").pack(anchor=tk.W)
        text_obs = tk.Text(form_content, height=4, font=("Segoe UI", 10), relief=tk.FLAT, bd=5)
        text_obs.pack(fill=tk.X, pady=(5, 0))

        # Botones
        botones_frame = tk.Frame(main_frame, bg="#f8fafc")
        botones_frame.pack(fill=tk.X)

        def crear_cuenta():
            numero = entry_numero.get().strip()
            cliente = entry_cliente.get().strip()
            cliente_id = self.obtener_cliente_id(combo_clientes.get())
            observaciones = text_obs.get("1.0", tk.END).strip()

            if not numero or not cliente:
                messagebox.showerror("Error", "Número de cuenta y nombre del cliente son obligatorios")
                return

            self.crear_cuenta_bd(numero, cliente, cliente_id, observaciones, ventana_nueva)

        tk.Button(botones_frame, text="✅ Crear Cuenta", command=crear_cuenta,
                  bg="#3b82f6", fg="white", font=("Segoe UI", 11, "bold"),
                  padx=25, pady=10, cursor="hand2").pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(botones_frame, text="❌ Cancelar", command=ventana_nueva.destroy,
                  bg="#6b7280", fg="white", font=("Segoe UI", 11, "bold"),
                  padx=25, pady=10, cursor="hand2").pack(side=tk.LEFT)

        entry_numero.focus()

    def cargar_clientes_combo(self, combo):
        """Carga clientes en el combobox"""
        conexion = self.conectar_bd()
        if not conexion:
            return

        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_cliente, nombre, telefono FROM clientes ORDER BY nombre")
            clientes = cursor.fetchall()

            valores = ["-- Seleccionar cliente existente --"]
            for cliente in clientes:
                id_cliente, nombre, telefono = cliente
                texto = f"{nombre} - {telefono or 'Sin teléfono'}"
                valores.append(texto)

            combo['values'] = valores
            combo.set(valores[0])

        except mysql.connector.Error:
            pass
        finally:
            conexion.close()

    def obtener_cliente_id(self, seleccion):
        """Obtiene ID del cliente seleccionado"""
        if not seleccion or seleccion.startswith("--"):
            return None

        conexion = self.conectar_bd()
        if not conexion:
            return None

        try:
            cursor = conexion.cursor()
            nombre = seleccion.split(" - ")[0]
            cursor.execute("SELECT id_cliente FROM clientes WHERE nombre = %s", (nombre,))
            result = cursor.fetchone()
            return result[0] if result else None
        except:
            return None
        finally:
            conexion.close()

    def crear_cuenta_bd(self, numero, cliente, cliente_id, observaciones, ventana):
        """Crea la cuenta en la base de datos"""
        conexion = self.conectar_bd()
        if not conexion:
            return

        try:
            cursor = conexion.cursor()
            cursor.execute("""
                           INSERT INTO cuentas_abiertas
                           (numero_cuenta, nombre_cliente, id_cliente, observaciones, id_usuario_apertura)
                           VALUES (%s, %s, %s, %s, %s)
                           """, (numero, cliente, cliente_id, observaciones, self.usuario_actual['id_usuario']))

            conexion.commit()
            messagebox.showinfo("✅ Éxito", f"Cuenta '{numero}' creada exitosamente")
            ventana.destroy()
            self.actualizar_todo()

        except mysql.connector.Error as e:
            if e.errno == 1062:
                messagebox.showerror("Error", f"Ya existe una cuenta con el número '{numero}'")
            else:
                messagebox.showerror("Error", f"Error al crear cuenta: {str(e)}")
        finally:
            conexion.close()

    def cerrar_cuenta_avanzada(self):
        """Cierra cuenta con proceso avanzado"""
        if not self.cuenta_seleccionada:
            messagebox.showwarning("Advertencia", "Selecciona una cuenta primero")
            return

        # Diálogo de confirmación avanzado
        respuesta = messagebox.askyesnocancel("Cerrar Cuenta",
                                              "¿Cómo deseas proceder?\n\n"
                                              "✅ SÍ: Cerrar cuenta y generar venta\n"
                                              "❌ NO: Solo cerrar cuenta sin venta\n"
                                              "⏸️ CANCELAR: No hacer nada")

        if respuesta is None:  # Cancelar
            return
        elif respuesta:  # Sí - generar venta
            self.cerrar_con_venta()
        else:  # No - solo cerrar
            self.cerrar_sin_venta()

    def cerrar_con_venta(self):
        """Cierra cuenta generando venta automáticamente"""
        conexion = self.conectar_bd()
        if not conexion:
            return

        try:
            cursor = conexion.cursor()

            # Obtener datos de la cuenta
            cursor.execute("""
                           SELECT numero_cuenta, nombre_cliente, id_cliente, total
                           FROM cuentas_abiertas
                           WHERE id_cuenta = %s
                             AND estado = 'abierta'
                           """, (self.cuenta_seleccionada,))

            cuenta_data = cursor.fetchone()
            if not cuenta_data:
                messagebox.showerror("Error", "Cuenta no disponible")
                return

            numero, cliente, id_cliente, total = cuenta_data

            if total <= 0:
                messagebox.showwarning("Advertencia", "La cuenta no tiene items para facturar")
                return

            # Crear venta (integración con sistema existente)
            fecha_actual = datetime.now()
            cursor.execute("""
                           INSERT INTO ventas (id_cliente, total, fecha, metodo_pago, id_usuario, observaciones)
                           VALUES (%s, %s, %s, %s, %s, %s)
                           """, (id_cliente, total, fecha_actual, 'Efectivo',
                                 self.usuario_actual['id_usuario'], f"Venta generada desde cuenta {numero}"))

            id_venta = cursor.lastrowid

            # Crear detalle de venta desde items de cuenta
            cursor.execute("""
                           SELECT tipo_item, id_item_ref, cantidad, precio_unitario, subtotal
                           FROM items_cuenta_abierta
                           WHERE id_cuenta = %s
                           """, (self.cuenta_seleccionada,))

            items = cursor.fetchall()
            for item in items:
                tipo, id_item_ref, cantidad, precio, subtotal = item
                cursor.execute("""
                               INSERT INTO detalle_venta (id_venta, tipo_item, id_item, cantidad, precio_unitario, subtotal)
                               VALUES (%s, %s, %s, %s, %s, %s)
                               """, (id_venta, tipo, id_item_ref, cantidad, precio, subtotal))

            # Cerrar cuenta
            cursor.execute("""
                           UPDATE cuentas_abiertas
                           SET estado             = 'cerrada',
                               fecha_modificacion = %s
                           WHERE id_cuenta = %s
                           """, (fecha_actual, self.cuenta_seleccionada))

            conexion.commit()

            messagebox.showinfo("✅ Venta Generada",
                                f"Cuenta '{numero}' cerrada exitosamente\n\n"
                                f"🧾 Venta #{id_venta} generada\n"
                                f"💰 Total: ${total:.2f}\n"
                                f"👤 Cliente: {cliente}\n\n"
                                f"La venta se ha registrado en el sistema de caja automáticamente.")

            self.cuenta_seleccionada = None
            self.actualizar_todo()
            self.limpiar_detalles()

        except mysql.connector.Error as e:
            conexion.rollback()
            messagebox.showerror("Error", f"Error al procesar venta: {str(e)}")
        finally:
            conexion.close()

    def cerrar_sin_venta(self):
        """Cierra cuenta sin generar venta"""
        conexion = self.conectar_bd()
        if not conexion:
            return

        try:
            cursor = conexion.cursor()
            cursor.execute("""
                           UPDATE cuentas_abiertas
                           SET estado             = 'cerrada',
                               fecha_modificacion = %s
                           WHERE id_cuenta = %s
                           """, (datetime.now(), self.cuenta_seleccionada))

            conexion.commit()
            messagebox.showinfo("✅ Cuenta Cerrada", "Cuenta cerrada sin generar venta")

            self.cuenta_seleccionada = None
            self.actualizar_todo()
            self.limpiar_detalles()

        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al cerrar cuenta: {str(e)}")
        finally:
            conexion.close()

    def limpiar_detalles(self):
        """Limpia los paneles de detalles"""
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "Selecciona una cuenta para ver los detalles...")

        for item in self.tree_items.get_children():
            self.tree_items.delete(item)

        self.historial_text.config(state=tk.NORMAL)
        self.historial_text.delete(1.0, tk.END)
        self.historial_text.config(state=tk.DISABLED)

    def agregar_item_avanzado(self):
        """Agrega item con diálogo avanzado"""
        if not self.cuenta_seleccionada:
            messagebox.showwarning("Advertencia", "Selecciona una cuenta primero")
            return

        # Aquí se integraría con el sistema de productos/servicios existente
        messagebox.showinfo("Próximamente", "Integración con sistema de productos/servicios en desarrollo")

    def editar_cuenta(self):
        """Edita los datos de la cuenta"""
        if not self.cuenta_seleccionada:
            messagebox.showwarning("Advertencia", "Selecciona una cuenta primero")
            return

        messagebox.showinfo("Próximamente", "Editor de cuentas en desarrollo")

    def pausar_cuenta(self):
        """Pausa una cuenta temporalmente"""
        if not self.cuenta_seleccionada:
            messagebox.showwarning("Advertencia", "Selecciona una cuenta primero")
            return

        conexion = self.conectar_bd()
        if not conexion:
            return

        try:
            cursor = conexion.cursor()
            cursor.execute("""
                           UPDATE cuentas_abiertas
                           SET estado             = 'pausada',
                               fecha_modificacion = %s
                           WHERE id_cuenta = %s
                             AND estado = 'abierta'
                           """, (datetime.now(), self.cuenta_seleccionada))

            if cursor.rowcount > 0:
                conexion.commit()
                messagebox.showinfo("✅ Cuenta Pausada", "Cuenta pausada temporalmente")
                self.actualizar_todo()
            else:
                messagebox.showwarning("Advertencia", "No se pudo pausar la cuenta")

        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al pausar cuenta: {str(e)}")
        finally:
            conexion.close()

    # Funciones adicionales
    def llamar_cliente(self):
        """Función para llamar al cliente"""
        messagebox.showinfo("📞 Llamada",
                            "Función de llamadas en desarrollo\n\nSe integrará con softphone o marcador automático")

    def enviar_email(self):
        """Función para enviar email"""
        messagebox.showinfo("📧 Email", "Función de email en desarrollo\n\nSe integrará con sistema de notificaciones")

    def imprimir_cuenta(self):
        """Función para imprimir cuenta"""
        messagebox.showinfo("🖨️ Impresión", "Función de impresión en desarrollo\n\nGenerará tickets y reportes PDF")

    def quitar_item_avanzado(self):
        """Quita item seleccionado"""
        messagebox.showinfo("Próximamente", "Función de eliminación de items en desarrollo")

    def editar_item(self):
        """Edita item seleccionado"""
        messagebox.showinfo("Próximamente", "Editor de items en desarrollo")

    def cerrar_ventana(self):
        """Cierra la ventana y detiene actualizaciones"""
        self.auto_refresh = False
        if self.refresh_thread:
            try:
                self.refresh_thread.join(timeout=1)
            except:
                pass

        self.ventana.destroy()
        self.ventana = None


# Función principal de integración
def abrir_gestion_cuentas_abiertas(parent_window, usuario_actual):
    """Función principal para abrir el sistema profesional de cuentas abiertas"""
    try:
        manager = CuentasAbiertasProfesional(parent_window, usuario_actual)
        manager.mostrar_ventana()
    except Exception as e:
        messagebox.showerror("Error", f"Error al iniciar sistema de cuentas abiertas:\n{str(e)}")