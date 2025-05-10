

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import os
import sys
import utileria as utl
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import seaborn as sns
import calendar
import locale
import io
from PIL import Image, ImageTk
import webbrowser
import json

# Intentar configurar locale para fechas en español
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')
    except:
        pass  # Si no funciona, se usará el locale por defecto

# Asegurar que podamos importar módulos del sistema
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

try:
    from conexion import conectar_bd
except ImportError as e:
    print(f"Error al importar módulos: {e}")


class Reportes:
    """Clase para la generación y visualización de reportes avanzados"""

    def __init__(self, ventana_padre=None):
        # Si hay una ventana padre, crear Toplevel en lugar de Tk
        if ventana_padre:
            self.ventana = tk.Toplevel(ventana_padre)
        else:
            self.ventana = tk.Tk()

        self.ventana.title("Reportes y Estadísticas - Lavandería")
        self.ventana.geometry("1200x750")
        self.ventana.config(bg="#f5f5f5")
        self.ventana.resizable(True, True)

        if ventana_padre:
            # Centrar la ventana si existe una ventana padre
            utl.centrar_ventana(self.ventana, 1200, 750)
            # Hacer esta ventana modal
            self.ventana.transient(ventana_padre)
            self.ventana.grab_set()

        # Establecer ícono si existe
        try:
            if os.path.exists("Img/lavadora.ico"):
                self.ventana.iconbitmap("Img/lavadora.ico")
        except Exception:
            pass  # Si no se puede cargar el ícono, continuar sin él

        # Crear directorio para reportes si no existe
        self.directorio_reportes = os.path.join(script_dir, "reportes")
        if not os.path.exists(self.directorio_reportes):
            os.makedirs(self.directorio_reportes)

        # Configurar tema para gráficas
        plt.style.use('ggplot')
        sns.set_style("whitegrid")

        # Variables para la aplicación
        self.datos_grafico = None
        self.ultima_consulta_sql = None
        self.ultimo_resultado_consulta = None
        self.filtros_adicionales = {}

        # Configurar ploteo de gráficos
        sns.set_palette("colorblind")

        # Construir la interfaz
        self.construir_interfaz()

        if not ventana_padre:
            self.ventana.mainloop()

    def construir_interfaz(self):
        """Construye la interfaz gráfica del módulo de reportes"""
        # Frame principal con padding
        self.frame_principal = tk.Frame(self.ventana, bg="#f5f5f5", padx=20, pady=20)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)

        # Título con estilo
        titulo_frame = tk.Frame(self.frame_principal, bg="#f5f5f5")
        titulo_frame.pack(fill=tk.X, pady=(0, 20))

        titulo = tk.Label(
            titulo_frame,
            text="REPORTES Y ESTADÍSTICAS",
            font=("Helvetica", 18, "bold"),
            bg="#f5f5f5",
            fg="#3a7ff6"
        )
        titulo.pack()

        subtitulo = tk.Label(
            titulo_frame,
            text="Generación de informes y visualizaciones",
            font=("Helvetica", 12),
            bg="#f5f5f5",
            fg="#666a88"
        )
        subtitulo.pack(pady=(5, 0))

        # Separador
        separador = ttk.Separator(self.frame_principal, orient="horizontal")
        separador.pack(fill=tk.X, pady=(0, 20))

        # Frame para filtros y controles
        self.frame_controles = tk.LabelFrame(self.frame_principal, text="Filtros y Opciones", bg="#f5f5f5", padx=10, pady=10)
        self.frame_controles.pack(fill=tk.X, pady=10)

        # Crear notebooks y configurar pestañas
        self.configurar_filtros()
        self.crear_notebook()

        # Footer con botones
        self.crear_footer()

        # Inicializar con el primer tipo de reporte
        self.cambiar_tipo_reporte()

    def configurar_filtros(self):
        """Configura los filtros para los reportes"""
        # Primera fila: Tipo de reporte y periodo
        frame_fila1 = tk.Frame(self.frame_controles, bg="#f5f5f5")
        frame_fila1.pack(fill=tk.X, pady=5)

        # Tipo de reporte
        frame_tipo = tk.Frame(frame_fila1, bg="#f5f5f5")
        frame_tipo.pack(side=tk.LEFT, padx=10)

        tk.Label(
            frame_tipo,
            text="Tipo de Reporte:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        # Opciones de reportes disponibles
        opciones_reportes = [
            "Ventas por Periodo",
            "Productos Más Vendidos",
            "Servicios Más Solicitados",
            "Clientes Frecuentes",
            "Ingresos Mensuales",
            "Pedidos por Estado",
            "Rentabilidad de Servicios",
            "Comportamiento de Clientes",
            "Dashboard General"
        ]

        self.tipo_reporte = tk.StringVar(value=opciones_reportes[0])
        combo_tipo = ttk.Combobox(
            frame_tipo,
            textvariable=self.tipo_reporte,
            values=opciones_reportes,
            width=20,
            state="readonly"
        )
        combo_tipo.pack(side=tk.LEFT, padx=5)
        combo_tipo.bind("<<ComboboxSelected>>", self.cambiar_tipo_reporte)

        # Periodo
        frame_fecha = tk.Frame(frame_fila1, bg="#f5f5f5")
        frame_fecha.pack(side=tk.LEFT, padx=20)

        tk.Label(
            frame_fecha,
            text="Período:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        # Opciones de períodos
        opciones_periodos = [
            "Hoy",
            "Ayer",
            "Esta Semana",
            "Semana Pasada",
            "Este Mes",
            "Mes Pasado",
            "Último Trimestre",
            "Este Año",
            "Personalizado"
        ]

        self.periodo = tk.StringVar(value=opciones_periodos[4])  # Por defecto "Este Mes"
        combo_periodo = ttk.Combobox(
            frame_fecha,
            textvariable=self.periodo,
            values=opciones_periodos,
            width=15,
            state="readonly"
        )
        combo_periodo.pack(side=tk.LEFT, padx=5)
        combo_periodo.bind("<<ComboboxSelected>>", self.cambiar_periodo)

        # Frame para fechas personalizadas
        self.frame_fechas_personalizadas = tk.Frame(frame_fila1, bg="#f5f5f5")

        tk.Label(
            self.frame_fechas_personalizadas,
            text="Desde:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        # Fecha de inicio y fin
        hoy = date.today()
        primer_dia_mes = hoy.replace(day=1)

        self.fecha_inicio = tk.StringVar(value=primer_dia_mes.strftime("%Y-%m-%d"))
        self.fecha_fin = tk.StringVar(value=hoy.strftime("%Y-%m-%d"))

        entry_fecha_inicio = tk.Entry(
            self.frame_fechas_personalizadas,
            textvariable=self.fecha_inicio,
            font=("Helvetica", 11),
            width=10
        )
        entry_fecha_inicio.pack(side=tk.LEFT, padx=2)

        tk.Label(
            self.frame_fechas_personalizadas,
            text="Hasta:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        entry_fecha_fin = tk.Entry(
            self.frame_fechas_personalizadas,
            textvariable=self.fecha_fin,
            font=("Helvetica", 11),
            width=10
        )
        entry_fecha_fin.pack(side=tk.LEFT, padx=2)

        # Segunda fila: Filtros adicionales según el tipo de reporte
        self.frame_fila2 = tk.Frame(self.frame_controles, bg="#f5f5f5")
        self.frame_fila2.pack(fill=tk.X, pady=5)

        # Variables para filtros adicionales
        self.filtro_cliente = tk.StringVar()
        self.filtro_vendedor = tk.StringVar()
        self.filtro_pago = tk.StringVar(value="Todos")
        self.filtro_estado = tk.StringVar(value="Todos")

        # Botones de acción
        frame_botones = tk.Frame(self.frame_controles, bg="#f5f5f5")
        frame_botones.pack(fill=tk.X, pady=5)

        # Botón para generar reporte
        btn_generar = tk.Button(
            frame_botones,
            text="Generar Reporte",
            font=("Helvetica", 11),
            bg="#3a7ff6",
            fg="white",
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.generar_reporte
        )
        btn_generar.pack(side=tk.RIGHT, padx=10)

        # Botones adicionales
        btn_exportar = tk.Button(
            frame_botones,
            text="Exportar",
            font=("Helvetica", 11),
            bg="#4caf50",
            fg="white",
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.exportar_reporte
        )
        btn_exportar.pack(side=tk.RIGHT, padx=5)

        btn_guardar_plantilla = tk.Button(
            frame_botones,
            text="Guardar como Plantilla",
            font=("Helvetica", 11),
            bg="#ff9800",
            fg="white",
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.guardar_plantilla
        )
        btn_guardar_plantilla.pack(side=tk.RIGHT, padx=5)

    def crear_notebook(self):
        """Crea el notebook con las pestañas para datos y gráficos"""
        self.notebook = ttk.Notebook(self.frame_principal)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Pestañas
        self.tab_tabla = tk.Frame(self.notebook, bg="#f5f5f5")
        self.tab_grafico = tk.Frame(self.notebook, bg="#f5f5f5")
        self.tab_dashboard = tk.Frame(self.notebook, bg="#f5f5f5")

        self.notebook.add(self.tab_tabla, text="Datos")
        self.notebook.add(self.tab_grafico, text="Gráficos")
        self.notebook.add(self.tab_dashboard, text="Dashboard")

        # Configurar pestañas
        self.configurar_tab_tabla()
        self.configurar_tab_grafico()
        self.configurar_tab_dashboard()

    def configurar_tab_tabla(self):
        """Configura la pestaña con la vista de datos en tabla"""
        # Frame para la tabla
        frame_tabla = tk.Frame(self.tab_tabla, bg="#f5f5f5")
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)

        # Frame para controles de la tabla
        frame_controles_tabla = tk.Frame(frame_tabla, bg="#f5f5f5")
        frame_controles_tabla.pack(fill=tk.X, pady=5)

        # Botón para buscar en la tabla
        tk.Label(
            frame_controles_tabla,
            text="Buscar:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        self.busqueda_tabla = tk.StringVar()
        entry_busqueda = tk.Entry(
            frame_controles_tabla,
            textvariable=self.busqueda_tabla,
            font=("Helvetica", 11),
            width=25
        )
        entry_busqueda.pack(side=tk.LEFT, padx=5)
        entry_busqueda.bind("<KeyRelease>", self.filtrar_tabla)

        # Botón para limpiar filtros
        btn_limpiar = tk.Button(
            frame_controles_tabla,
            text="Limpiar Filtros",
            font=("Helvetica", 11),
            bg="#e0e0e0",
            command=self.limpiar_filtros_tabla
        )
        btn_limpiar.pack(side=tk.LEFT, padx=5)

        # Tabla de datos
        self.tabla_reporte = ttk.Treeview(frame_tabla)

        # Aplicar estilo a la tabla
        estilo_tabla = ttk.Style()
        estilo_tabla.configure("Treeview",
                               background="#ffffff",
                               foreground="#333333",
                               rowheight=25,
                               fieldbackground="#ffffff")
        estilo_tabla.map('Treeview',
                         background=[('selected', '#3a7ff6')],
                         foreground=[('selected', '#ffffff')])

        # Scrollbars
        scrollbar_y = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_reporte.yview)
        self.tabla_reporte.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_x = ttk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL, command=self.tabla_reporte.xview)
        self.tabla_reporte.configure(xscrollcommand=scrollbar_x.set)

        # Empaquetar elementos
        self.tabla_reporte.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Frame para resumen
        self.frame_resumen = tk.LabelFrame(self.tab_tabla, text="Resumen", bg="#f5f5f5", padx=10, pady=10)
        self.frame_resumen.pack(fill=tk.X, pady=10, padx=5)

    def configurar_tab_grafico(self):
        """Configura la pestaña para visualizaciones gráficas"""
        # Frame para controles del gráfico
        frame_controles_grafico = tk.Frame(self.tab_grafico, bg="#f5f5f5")
        frame_controles_grafico.pack(fill=tk.X, pady=5)

        # Tipo de gráfico
        tk.Label(
            frame_controles_grafico,
            text="Tipo de Gráfico:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        self.tipo_grafico = tk.StringVar(value="Barras")
        opciones_graficos = ["Barras", "Líneas", "Pastel", "Área", "Barras Horizontales", "Dispersión", "Calor"]
        combo_grafico = ttk.Combobox(
            frame_controles_grafico,
            textvariable=self.tipo_grafico,
            values=opciones_graficos,
            width=15,
            state="readonly"
        )
        combo_grafico.pack(side=tk.LEFT, padx=5)
        combo_grafico.bind("<<ComboboxSelected>>", lambda e: self.actualizar_grafico())

        # Opciones de estilo
        tk.Label(
            frame_controles_grafico,
            text="Estilo:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        self.estilo_grafico = tk.StringVar(value="predeterminado")
        estilos_disponibles = ["predeterminado", "colorblind", "pastel", "dark", "deep", "muted", "bright"]
        combo_estilo = ttk.Combobox(
            frame_controles_grafico,
            textvariable=self.estilo_grafico,
            values=estilos_disponibles,
            width=15,
            state="readonly"
        )
        combo_estilo.pack(side=tk.LEFT, padx=5)
        combo_estilo.bind("<<ComboboxSelected>>", lambda e: self.cambiar_estilo_grafico())

        # Botones adicionales
        btn_colores = tk.Button(
            frame_controles_grafico,
            text="Personalizar Colores",
            font=("Helvetica", 10),
            bg="#3a7ff6",
            fg="white",
            command=self.personalizar_colores
        )
        btn_colores.pack(side=tk.LEFT, padx=10)

        btn_guardar_img = tk.Button(
            frame_controles_grafico,
            text="Guardar como Imagen",
            font=("Helvetica", 10),
            bg="#4caf50",
            fg="white",
            command=self.guardar_grafico_como_imagen
        )
        btn_guardar_img.pack(side=tk.LEFT, padx=10)

        # Frame para el gráfico
        self.frame_grafico = tk.Frame(self.tab_grafico, bg="white", padx=10, pady=10)
        self.frame_grafico.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)

        # Figura inicial vacía
        self.fig = plt.Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, self.frame_grafico)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def configurar_tab_dashboard(self):
        """Configura la pestaña para el dashboard interactivo"""
        # Frame para el dashboard
        frame_dashboard = tk.Frame(self.tab_dashboard, bg="#f5f5f5")
        frame_dashboard.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Mensaje inicial
        self.lbl_dashboard_info = tk.Label(
            frame_dashboard,
            text="Seleccione 'Dashboard General' como tipo de reporte para ver el panel interactivo",
            font=("Helvetica", 14),
            bg="#f5f5f5",
            fg="#666a88"
        )
        self.lbl_dashboard_info.pack(pady=50)

        # Frames para gráficos en el dashboard
        self.dashboard_frames = []

        # Configuración de layout para dashboard (2x2)
        for i in range(4):
            frame = tk.Frame(frame_dashboard, bg="white", bd=1, relief=tk.GROOVE)
            self.dashboard_frames.append(frame)

        # Inicialmente no mostramos los frames del dashboard

    def crear_footer(self):
        """Crea el footer con botones de acción"""
        frame_footer = tk.Frame(self.frame_principal, bg="#f5f5f5")
        frame_footer.pack(fill=tk.X, pady=10)

        # Botón para volver
        btn_volver = tk.Button(
            frame_footer,
            text="Volver",
            font=("Helvetica", 11),
            bg="#e53935",
            fg="white",
            width=10,
            cursor="hand2",
            command=self.ventana.destroy
        )
        btn_volver.pack(side=tk.RIGHT, padx=10)

        # Botón de ayuda
        btn_ayuda = tk.Button(
            frame_footer,
            text="Ayuda",
            font=("Helvetica", 11),
            bg="#3a7ff6",
            fg="white",
            width=10,
            cursor="hand2",
            command=self.mostrar_ayuda
        )
        btn_ayuda.pack(side=tk.RIGHT, padx=10)

    def cambiar_tipo_reporte(self, event=None):
        """Actualiza la interfaz según el tipo de reporte seleccionado"""
        tipo_seleccionado = self.tipo_reporte.get()

        # Limpiar tabla existente
        for item in self.tabla_reporte.get_children():
            self.tabla_reporte.delete(item)

        # Limpiar frame para filtros adicionales
        for widget in self.frame_fila2.winfo_children():
            widget.destroy()

        # Configurar columnas según el tipo de reporte
        if tipo_seleccionado == "Ventas por Periodo":
            columnas = ('fecha', 'id_venta', 'cliente', 'total', 'metodo_pago', 'usuario')
            self.tabla_reporte['columns'] = columnas

            # Configurar encabezados
            self.tabla_reporte.heading('fecha', text='Fecha')
            self.tabla_reporte.heading('id_venta', text='ID Venta')
            self.tabla_reporte.heading('cliente', text='Cliente')
            self.tabla_reporte.heading('total', text='Total')
            self.tabla_reporte.heading('metodo_pago', text='Método de Pago')
            self.tabla_reporte.heading('usuario', text='Vendedor')

            # Configurar anchos
            self.tabla_reporte.column('fecha', width=100, anchor=tk.CENTER)
            self.tabla_reporte.column('id_venta', width=70, anchor=tk.CENTER)
            self.tabla_reporte.column('cliente', width=200)
            self.tabla_reporte.column('total', width=100, anchor=tk.E)
            self.tabla_reporte.column('metodo_pago', width=120, anchor=tk.CENTER)
            self.tabla_reporte.column('usuario', width=150)

            # Filtros adicionales
            self.crear_filtros_ventas()

        elif tipo_seleccionado == "Productos Más Vendidos":
            columnas = ('id_producto', 'nombre', 'cantidad_total', 'ingresos_total', 'precio_promedio')
            self.tabla_reporte['columns'] = columnas

            self.tabla_reporte.heading('id_producto', text='ID')
            self.tabla_reporte.heading('nombre', text='Producto')
            self.tabla_reporte.heading('cantidad_total', text='Cantidad Vendida')
            self.tabla_reporte.heading('ingresos_total', text='Ingresos Generados')
            self.tabla_reporte.heading('precio_promedio', text='Precio Promedio')

            self.tabla_reporte.column('id_producto', width=50, anchor=tk.CENTER)
            self.tabla_reporte.column('nombre', width=300)
            self.tabla_reporte.column('cantidad_total', width=120, anchor=tk.CENTER)
            self.tabla_reporte.column('ingresos_total', width=150, anchor=tk.E)
            self.tabla_reporte.column('precio_promedio', width=120, anchor=tk.E)

        elif tipo_seleccionado == "Servicios Más Solicitados":
            columnas = ('id_servicio', 'nombre', 'cantidad_total', 'ingresos_total', 'precio_promedio')
            self.tabla_reporte['columns'] = columnas

            self.tabla_reporte.heading('id_servicio', text='ID')
            self.tabla_reporte.heading('nombre', text='Servicio')
            self.tabla_reporte.heading('cantidad', text='Cantidad')
            self.tabla_reporte.heading('ingresos', text='Ingresos')
            self.tabla_reporte.heading('costos', text='Costos')
            self.tabla_reporte.heading('margen', text='Margen')
            self.tabla_reporte.heading('rentabilidad', text='Rentabilidad %')

            self.tabla_reporte.column('id_servicio', width=50, anchor=tk.CENTER)
            self.tabla_reporte.column('nombre', width=200)
            self.tabla_reporte.column('cantidad', width=80, anchor=tk.CENTER)
            self.tabla_reporte.column('ingresos', width=120, anchor=tk.E)
            self.tabla_reporte.column('costos', width=120, anchor=tk.E)
            self.tabla_reporte.column('margen', width=120, anchor=tk.E)
            self.tabla_reporte.column('rentabilidad', width=120, anchor=tk.E)

        elif tipo_seleccionado == "Comportamiento de Clientes":
            columnas = ('id_cliente', 'nombre', 'frecuencia', 'recencia', 'valor', 'categoria', 'potencial')
            self.tabla_reporte['columns'] = columnas

            self.tabla_reporte.heading('id_cliente', text='ID')
            self.tabla_reporte.heading('nombre', text='Cliente')
            self.tabla_reporte.heading('frecuencia', text='Frecuencia')
            self.tabla_reporte.heading('recencia', text='Recencia (días)')
            self.tabla_reporte.heading('valor', text='Valor')
            self.tabla_reporte.heading('categoria', text='Categoría')
            self.tabla_reporte.heading('potencial', text='Potencial')

            self.tabla_reporte.column('id_cliente', width=50, anchor=tk.CENTER)
            self.tabla_reporte.column('nombre', width=200)
            self.tabla_reporte.column('frecuencia', width=80, anchor=tk.CENTER)
            self.tabla_reporte.column('recencia', width=120, anchor=tk.CENTER)
            self.tabla_reporte.column('valor', width=100, anchor=tk.E)
            self.tabla_reporte.column('categoria', width=120, anchor=tk.CENTER)
            self.tabla_reporte.column('potencial', width=150, anchor=tk.CENTER)

        elif tipo_seleccionado == "Dashboard General":
            # Para el dashboard, configuramos una vista simplificada
            columnas = ('metrica', 'valor', 'variacion')
            self.tabla_reporte['columns'] = columnas

            self.tabla_reporte.heading('metrica', text='Métrica')
            self.tabla_reporte.heading('valor', text='Valor')
            self.tabla_reporte.heading('variacion', text='Variación')

            self.tabla_reporte.column('metrica', width=200)
            self.tabla_reporte.column('valor', width=150, anchor=tk.CENTER)
            self.tabla_reporte.column('variacion', width=150, anchor=tk.CENTER)

            # Configurar el dashboard
            self.configurar_dashboard()

        # Aplicar el periodo actual
        self.cambiar_periodo()

    def crear_filtros_ventas(self):
        """Crea filtros específicos para el reporte de ventas"""
        # Frame para método de pago
        frame_metodo = tk.Frame(self.frame_fila2, bg="#f5f5f5")
        frame_metodo.pack(side=tk.LEFT, padx=10)

        tk.Label(
            frame_metodo,
            text="Método de Pago:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        # Valores para el combo de métodos de pago
        metodos_pago = ["Todos", "Efectivo", "Tarjeta", "Transferencia", "Puntos", "Otro"]
        combo_metodo = ttk.Combobox(
            frame_metodo,
            textvariable=self.filtro_pago,
            values=metodos_pago,
            width=12,
            state="readonly"
        )
        combo_metodo.pack(side=tk.LEFT, padx=5)

        # Frame para cliente
        frame_cliente = tk.Frame(self.frame_fila2, bg="#f5f5f5")
        frame_cliente.pack(side=tk.LEFT, padx=10)

        tk.Label(
            frame_cliente,
            text="Cliente:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        entry_cliente = tk.Entry(
            frame_cliente,
            textvariable=self.filtro_cliente,
            font=("Helvetica", 11),
            width=15
        )
        entry_cliente.pack(side=tk.LEFT, padx=5)

        # Frame para vendedor
        frame_vendedor = tk.Frame(self.frame_fila2, bg="#f5f5f5")
        frame_vendedor.pack(side=tk.LEFT, padx=10)

        tk.Label(
            frame_vendedor,
            text="Vendedor:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        entry_vendedor = tk.Entry(
            frame_vendedor,
            textvariable=self.filtro_vendedor,
            font=("Helvetica", 11),
            width=15
        )
        entry_vendedor.pack(side=tk.LEFT, padx=5)

    def crear_filtros_pedidos(self):
        """Crea filtros específicos para el reporte de pedidos"""
        # Frame para estado
        frame_estado = tk.Frame(self.frame_fila2, bg="#f5f5f5")
        frame_estado.pack(side=tk.LEFT, padx=10)

        tk.Label(
            frame_estado,
            text="Estado:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        # Valores para el combo de estados
        estados = ["Todos", "Recibido", "En proceso", "Listo para entrega", "Entregado", "Cancelado"]
        combo_estado = ttk.Combobox(
            frame_estado,
            textvariable=self.filtro_estado,
            values=estados,
            width=15,
            state="readonly"
        )
        combo_estado.pack(side=tk.LEFT, padx=5)

        # Frame para cliente
        frame_cliente = tk.Frame(self.frame_fila2, bg="#f5f5f5")
        frame_cliente.pack(side=tk.LEFT, padx=10)

        tk.Label(
            frame_cliente,
            text="Cliente:",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        ).pack(side=tk.LEFT, padx=5)

        entry_cliente = tk.Entry(
            frame_cliente,
            textvariable=self.filtro_cliente,
            font=("Helvetica", 11),
            width=15
        )
        entry_cliente.pack(side=tk.LEFT, padx=5)

    def configurar_dashboard(self):
        """Configura la pestaña de dashboard para visualizaciones múltiples"""
        # Ocultar mensaje inicial
        self.lbl_dashboard_info.pack_forget()

        # Configurar frames para el dashboard
        frame_dashboard = self.tab_dashboard

        # Limpiar frames existentes
        for widget in frame_dashboard.winfo_children():
            if widget != self.lbl_dashboard_info:
                widget.destroy()

        # Crear 4 frames para gráficos en un grid 2x2
        frame_top_left = tk.LabelFrame(frame_dashboard, text="Ventas por Periodo", bg="white", padx=5, pady=5)
        frame_top_left.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        frame_top_right = tk.LabelFrame(frame_dashboard, text="Servicios Más Solicitados", bg="white", padx=5, pady=5)
        frame_top_right.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        frame_bottom_left = tk.LabelFrame(frame_dashboard, text="Pedidos por Estado", bg="white", padx=5, pady=5)
        frame_bottom_left.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        frame_bottom_right = tk.LabelFrame(frame_dashboard, text="Clientes Frecuentes", bg="white", padx=5, pady=5)
        frame_bottom_right.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Configurar grid
        frame_dashboard.columnconfigure(0, weight=1)
        frame_dashboard.columnconfigure(1, weight=1)
        frame_dashboard.rowconfigure(0, weight=1)
        frame_dashboard.rowconfigure(1, weight=1)

        # Guardar referencias a los frames
        self.dashboard_frames = [frame_top_left, frame_top_right, frame_bottom_left, frame_bottom_right]

        # Crear figuras para cada sección
        self.dashboard_figs = []
        self.dashboard_canvas = []

        for frame in self.dashboard_frames:
            fig = plt.Figure(figsize=(5, 3), dpi=100)
            canvas = FigureCanvasTkAgg(fig, frame)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.dashboard_figs.append(fig)
            self.dashboard_canvas.append(canvas)

    def cambiar_periodo(self, event=None):
        """Actualiza las fechas según el periodo seleccionado"""
        periodo = self.periodo.get()

        # Ocultar o mostrar frame de fechas personalizadas
        if periodo == "Personalizado":
            self.frame_fechas_personalizadas.pack(side=tk.LEFT, padx=10)
        else:
            self.frame_fechas_personalizadas.pack_forget()

            # Calcular fechas según el periodo seleccionado
            hoy = date.today()

            if periodo == "Hoy":
                self.fecha_inicio.set(hoy.strftime("%Y-%m-%d"))
                self.fecha_fin.set(hoy.strftime("%Y-%m-%d"))

            elif periodo == "Ayer":
                ayer = hoy - timedelta(days=1)
                self.fecha_inicio.set(ayer.strftime("%Y-%m-%d"))
                self.fecha_fin.set(ayer.strftime("%Y-%m-%d"))

            elif periodo == "Esta Semana":
                # Lunes de esta semana
                inicio_semana = hoy - timedelta(days=hoy.weekday())
                self.fecha_inicio.set(inicio_semana.strftime("%Y-%m-%d"))
                self.fecha_fin.set(hoy.strftime("%Y-%m-%d"))

            elif periodo == "Semana Pasada":
                # Lunes de la semana pasada
                inicio_semana_pasada = hoy - timedelta(days=hoy.weekday() + 7)
                # Domingo de la semana pasada
                fin_semana_pasada = inicio_semana_pasada + timedelta(days=6)
                self.fecha_inicio.set(inicio_semana_pasada.strftime("%Y-%m-%d"))
                self.fecha_fin.set(fin_semana_pasada.strftime("%Y-%m-%d"))

            elif periodo == "Este Mes":
                # Primer día del mes actual
                inicio_mes = hoy.replace(day=1)
                self.fecha_inicio.set(inicio_mes.strftime("%Y-%m-%d"))
                self.fecha_fin.set(hoy.strftime("%Y-%m-%d"))

            elif periodo == "Mes Pasado":
                # Primer día del mes pasado
                if hoy.month == 1:
                    inicio_mes_pasado = hoy.replace(year=hoy.year - 1, month=12, day=1)
                else:
                    inicio_mes_pasado = hoy.replace(month=hoy.month - 1, day=1)

                # Último día del mes pasado
                ultimo_dia = hoy.replace(day=1) - timedelta(days=1)
                self.fecha_inicio.set(inicio_mes_pasado.strftime("%Y-%m-%d"))
                self.fecha_fin.set(ultimo_dia.strftime("%Y-%m-%d"))

            elif periodo == "Último Trimestre":
                # Hace tres meses
                mes_inicio = hoy.month - 3
                año_inicio = hoy.year
                if mes_inicio <= 0:
                    mes_inicio += 12
                    año_inicio -= 1

                inicio_trimestre = date(año_inicio, mes_inicio, 1)
                self.fecha_inicio.set(inicio_trimestre.strftime("%Y-%m-%d"))
                self.fecha_fin.set(hoy.strftime("%Y-%m-%d"))

            elif periodo == "Este Año":
                # Primer día del año
                inicio_año = hoy.replace(month=1, day=1)
                self.fecha_inicio.set(inicio_año.strftime("%Y-%m-%d"))
                self.fecha_fin.set(hoy.strftime("%Y-%m-%d"))

    def generar_reporte(self):
        """Genera el reporte según el tipo y fecha seleccionados"""
        tipo_reporte = self.tipo_reporte.get()
        fecha_inicio = self.fecha_inicio.get()
        fecha_fin = self.fecha_fin.get()

        # Validar fechas
        try:
            date.fromisoformat(fecha_inicio)
            date.fromisoformat(fecha_fin)
        except ValueError:
            messagebox.showwarning("Formato incorrecto", "Las fechas deben tener el formato YYYY-MM-DD")
            return

        # Limpiar tabla
        for item in self.tabla_reporte.get_children():
            self.tabla_reporte.delete(item)

        # Limpiar resumen
        for widget in self.frame_resumen.winfo_children():
            widget.destroy()

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Generar reporte según el tipo seleccionado
            if tipo_reporte == "Ventas por Periodo":
                self.generar_reporte_ventas(cursor, fecha_inicio, fecha_fin)

            elif tipo_reporte == "Productos Más Vendidos":
                self.generar_reporte_productos(cursor, fecha_inicio, fecha_fin)

            elif tipo_reporte == "Servicios Más Solicitados":
                self.generar_reporte_servicios(cursor, fecha_inicio, fecha_fin)

            elif tipo_reporte == "Clientes Frecuentes":
                self.generar_reporte_clientes(cursor, fecha_inicio, fecha_fin)

            elif tipo_reporte == "Ingresos Mensuales":
                self.generar_reporte_ingresos_mensuales(cursor, fecha_inicio, fecha_fin)

            elif tipo_reporte == "Pedidos por Estado":
                self.generar_reporte_pedidos_estado(cursor, fecha_inicio, fecha_fin)

            elif tipo_reporte == "Rentabilidad de Servicios":
                self.generar_reporte_rentabilidad(cursor, fecha_inicio, fecha_fin)

            elif tipo_reporte == "Comportamiento de Clientes":
                self.generar_reporte_comportamiento_clientes(cursor, fecha_inicio, fecha_fin)

            elif tipo_reporte == "Dashboard General":
                self.generar_dashboard(cursor, fecha_inicio, fecha_fin)

            conexion.close()

            # Actualizar gráfico
            self.actualizar_grafico()

            # Mostrar mensaje de éxito
            tk.Label(
                self.frame_resumen,
                text="Reporte generado exitosamente",
                font=("Helvetica", 10),
                bg="#f5f5f5",
                fg="#4caf50"
            ).pack(side=tk.RIGHT, padx=10)

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar el reporte: {str(e)}")
            print(f"Error detallado: {e}")  # Para depuración

    def generar_reporte_ventas(self, cursor, fecha_inicio, fecha_fin):
        """Genera reporte de ventas en el periodo seleccionado"""
        condiciones = ["DATE(v.fecha) >= %s", "DATE(v.fecha) <= %s"]
        parametros = [fecha_inicio, fecha_fin]

        # Filtro método de pago
        if self.filtro_pago.get() != "Todos":
            condiciones.append("v.metodo_pago = %s")
            parametros.append(self.filtro_pago.get())

        # Filtro cliente
        if self.filtro_cliente.get().strip() != "":
            condiciones.append("c.nombre LIKE %s")
            parametros.append(f"%{self.filtro_cliente.get().strip()}%")

        # Filtro vendedor
        if self.filtro_vendedor.get().strip() != "":
            condiciones.append("u.nombre LIKE %s")
            parametros.append(f"%{self.filtro_vendedor.get().strip()}%")

        # Unir condiciones y generar consulta final
        where_clause = " AND ".join(condiciones)

        consulta = f"""
            SELECT 
                DATE(v.fecha) as fecha, 
                v.id_venta, 
                c.nombre as cliente, 
                v.total, 
                v.metodo_pago, 
                u.nombre as vendedor
            FROM ventas v
            LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
            LEFT JOIN usuarios u ON v.id_usuario = u.id_usuario
            WHERE {where_clause}
            ORDER BY v.fecha DESC
        """

        # Guardar consulta para posible reutilización
        self.ultima_consulta_sql = consulta

        cursor.execute(consulta, parametros)
        ventas = cursor.fetchall()

        # Guardar resultado para gráficos
        self.ultimo_resultado_consulta = ventas

        # Variables para el resumen
        total_ventas = 0
        cantidad_ventas = 0
        metodos_pago = {}

        # Insertar datos en la tabla
        for venta in ventas:
            fecha, id_venta, cliente, total, metodo_pago, vendedor = venta

            # Formatear datos
            fecha_formateada = fecha.strftime("%d/%m/%Y")
            cliente_nombre = cliente if cliente else "Cliente General"
            total_formateado = f"${float(total):.2f}"

            # Insertar en la tabla con color según método de pago
            item_id = self.tabla_reporte.insert('', tk.END, values=(
                fecha_formateada,
                id_venta,
                cliente_nombre,
                total_formateado,
                metodo_pago,
                vendedor or "No asignado"
            ))

            # Aplicar color para diferentes métodos de pago
            if metodo_pago == "Efectivo":
                self.tabla_reporte.item(item_id, tags=("efectivo",))
            elif metodo_pago == "Tarjeta":
                self.tabla_reporte.item(item_id, tags=("tarjeta",))
            elif metodo_pago == "Transferencia":
                self.tabla_reporte.item(item_id, tags=("transferencia",))

            # Configurar colores para los tags
            self.tabla_reporte.tag_configure("efectivo", background="#e8f5e9")
            self.tabla_reporte.tag_configure("tarjeta", background="#e3f2fd")
            self.tabla_reporte.tag_configure("transferencia", background="#fff8e1")

            # Actualizar totales
            total_ventas += float(total)
            cantidad_ventas += 1

            # Contar métodos de pago
            if metodo_pago in metodos_pago:
                metodos_pago[metodo_pago] += 1
            else:
                metodos_pago[metodo_pago] = 1

        # Mostrar resumen en el frame de resumen
        lbl_total = tk.Label(
            self.frame_resumen,
            text=f"Total Ventas: ${total_ventas:.2f}",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5"
        )
        lbl_total.pack(side=tk.LEFT, padx=20, pady=5)

        lbl_cantidad = tk.Label(
            self.frame_resumen,
            text=f"Cantidad: {cantidad_ventas}",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        lbl_cantidad.pack(side=tk.LEFT, padx=20, pady=5)

        if cantidad_ventas > 0:
            lbl_promedio = tk.Label(
                self.frame_resumen,
                text=f"Promedio: ${(total_ventas / cantidad_ventas):.2f}",
                font=("Helvetica", 11),
                bg="#f5f5f5"
            )
            lbl_promedio.pack(side=tk.LEFT, padx=20, pady=5)

        # Guardar datos para gráficos
        self.datos_grafico = {
            'tipo': 'ventas',
            'ventas': ventas,
            'total': total_ventas,
            'cantidad': cantidad_ventas,
            'metodos_pago': metodos_pago
        }

    def generar_reporte_productos(self, cursor, fecha_inicio, fecha_fin):
        """Genera reporte de productos más vendidos"""
        # Consulta SQL para obtener productos más vendidos
        consulta = """
            SELECT 
                p.id_producto, 
                p.nombre, 
                SUM(dv.cantidad) as cantidad_total,
                SUM(dv.subtotal) as ingresos_total,
                SUM(dv.subtotal) / SUM(dv.cantidad) as precio_promedio
            FROM detalle_venta dv
            JOIN productos p ON dv.id_item = p.id_producto
            JOIN ventas v ON dv.id_venta = v.id_venta
            WHERE dv.tipo_item = 'producto'
            AND DATE(v.fecha) BETWEEN %s AND %s
            GROUP BY p.id_producto, p.nombre
            ORDER BY cantidad_total DESC
        """

        cursor.execute(consulta, (fecha_inicio, fecha_fin))
        productos = cursor.fetchall()

        self.ultimo_resultado_consulta = productos

        # Variables para el resumen
        total_ingresos = 0
        total_unidades = 0

        # Insertar datos en la tabla
        for producto in productos:
            id_producto, nombre, cantidad, ingresos, precio_promedio = producto

            # Formatear datos
            cantidad_formateada = int(cantidad)
            ingresos_formateados = f"${float(ingresos):.2f}"
            precio_promedio_formateado = f"${float(precio_promedio):.2f}"

            # Insertar en la tabla
            self.tabla_reporte.insert('', tk.END, values=(
                id_producto,
                nombre,
                cantidad_formateada,
                ingresos_formateados,
                precio_promedio_formateado
            ))

            # Actualizar totales
            total_ingresos += float(ingresos)
            total_unidades += int(cantidad)

        # Mostrar resumen en el frame de resumen
        lbl_total_ingresos = tk.Label(
            self.frame_resumen,
            text=f"Total Ingresos: ${total_ingresos:.2f}",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5"
        )
        lbl_total_ingresos.pack(side=tk.LEFT, padx=20, pady=5)

        lbl_total_unidades = tk.Label(
            self.frame_resumen,
            text=f"Total Unidades: {total_unidades}",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        lbl_total_unidades.pack(side=tk.LEFT, padx=20, pady=5)

        lbl_productos = tk.Label(
            self.frame_resumen,
            text=f"Productos Diferentes: {len(productos)}",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        lbl_productos.pack(side=tk.LEFT, padx=20, pady=5)

        # Guardar datos para gráficos
        self.datos_grafico = {
            'tipo': 'productos',
            'productos': productos,
            'total_ingresos': total_ingresos,
            'total_unidades': total_unidades
        }

    def generar_reporte_servicios(self, cursor, fecha_inicio, fecha_fin):
        """Genera reporte de servicios más solicitados"""
        # Consulta SQL para obtener servicios más solicitados
        consulta = """
            SELECT 
                s.id_servicio, 
                s.nombre, 
                SUM(dv.cantidad) as cantidad_total,
                SUM(dv.subtotal) as ingresos_total,
                SUM(dv.subtotal) / SUM(dv.cantidad) as precio_promedio
            FROM detalle_venta dv
            JOIN servicios s ON dv.id_item = s.id_servicio
            JOIN ventas v ON dv.id_venta = v.id_venta
            WHERE dv.tipo_item = 'servicio'
            AND DATE(v.fecha) BETWEEN %s AND %s
            GROUP BY s.id_servicio, s.nombre
            ORDER BY cantidad_total DESC
        """

        cursor.execute(consulta, (fecha_inicio, fecha_fin))
        servicios = cursor.fetchall()

        self.ultimo_resultado_consulta = servicios

        # Variables para el resumen
        total_ingresos = 0
        total_servicios = 0

        # Insertar datos en la tabla
        for servicio in servicios:
            id_servicio, nombre, cantidad, ingresos, precio_promedio = servicio

            # Formatear datos
            cantidad_formateada = int(cantidad)
            ingresos_formateados = f"${float(ingresos):.2f}"
            precio_promedio_formateado = f"${float(precio_promedio):.2f}"

            # Insertar en la tabla
            self.tabla_reporte.insert('', tk.END, values=(
                id_servicio,
                nombre,
                cantidad_formateada,
                ingresos_formateados,
                precio_promedio_formateado
            ))

            # Actualizar totales
            total_ingresos += float(ingresos)
            total_servicios += int(cantidad)

        # Mostrar resumen en el frame de resumen
        lbl_total_ingresos = tk.Label(
            self.frame_resumen,
            text=f"Total Ingresos: ${total_ingresos:.2f}",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5"
        )
        lbl_total_ingresos.pack(side=tk.LEFT, padx=20, pady=5)

        lbl_total_servicios = tk.Label(
            self.frame_resumen,
            text=f"Total Servicios: {total_servicios}",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        lbl_total_servicios.pack(side=tk.LEFT, padx=20, pady=5)

        lbl_servicios = tk.Label(
            self.frame_resumen,
            text=f"Servicios Diferentes: {len(servicios)}",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        lbl_servicios.pack(side=tk.LEFT, padx=20, pady=5)

        # Guardar datos para gráficos
        self.datos_grafico = {
            'tipo': 'servicios',
            'servicios': servicios,
            'total_ingresos': total_ingresos,
            'total_servicios': total_servicios
        }

    def generar_reporte_clientes(self, cursor, fecha_inicio, fecha_fin):
        """Genera reporte de clientes frecuentes"""
        # Consulta SQL para obtener clientes frecuentes
        consulta = """
            SELECT 
                c.id_cliente, 
                c.nombre, 
                COUNT(DISTINCT v.id_venta) as visitas,
                SUM(v.total) as gasto_total,
                c.puntos,
                MAX(v.fecha) as ultima_visita,
                SUM(v.total) / COUNT(DISTINCT v.id_venta) as promedio_compra
            FROM clientes c
            JOIN ventas v ON c.id_cliente = v.id_cliente
            WHERE DATE(v.fecha) BETWEEN %s AND %s
            GROUP BY c.id_cliente, c.nombre, c.puntos
            ORDER BY visitas DESC, gasto_total DESC
        """

        cursor.execute(consulta, (fecha_inicio, fecha_fin))
        clientes = cursor.fetchall()

        self.ultimo_resultado_consulta = clientes

        # Variables para el resumen
        total_clientes = len(clientes)
        total_visitas = 0
        total_gasto = 0

        # Insertar datos en la tabla
        for cliente in clientes:
            id_cliente, nombre, visitas, gasto, puntos, ultima_visita, promedio_compra = cliente

            # Formatear datos
            gasto_formateado = f"${float(gasto):.2f}"
            ultima_visita_formateada = ultima_visita.strftime("%d/%m/%Y")
            promedio_compra_formateado = f"${float(promedio_compra):.2f}"

            # Insertar en la tabla
            self.tabla_reporte.insert('', tk.END, values=(
                id_cliente,
                nombre,
                visitas,
                gasto_formateado,
                puntos,
                ultima_visita_formateada,
                promedio_compra_formateado
            ))

            # Actualizar totales
            total_visitas += int(visitas)
            total_gasto += float(gasto)

        # Mostrar resumen en el frame de resumen
        lbl_total_clientes = tk.Label(
            self.frame_resumen,
            text=f"Total Clientes: {total_clientes}",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5"
        )
        lbl_total_clientes.pack(side=tk.LEFT, padx=20, pady=5)

        lbl_total_visitas = tk.Label(
            self.frame_resumen,
            text=f"Total Visitas: {total_visitas}",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        lbl_total_visitas.pack(side=tk.LEFT, padx=20, pady=5)

        lbl_total_gasto = tk.Label(
            self.frame_resumen,
            text=f"Gasto Total: ${total_gasto:.2f}",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        lbl_total_gasto.pack(side=tk.LEFT, padx=20, pady=5)

        if total_clientes > 0:
            lbl_promedio = tk.Label(
                self.frame_resumen,
                text=f"Promedio por Cliente: ${(total_gasto / total_clientes):.2f}",
                font=("Helvetica", 11),
                bg="#f5f5f5"
            )
            lbl_promedio.pack(side=tk.LEFT, padx=20, pady=5)

        # Guardar datos para gráficos
        self.datos_grafico = {
            'tipo': 'clientes',
            'clientes': clientes,
            'total_clientes': total_clientes,
            'total_visitas': total_visitas,
            'total_gasto': total_gasto
        }

    def generar_reporte_ingresos_mensuales(self, cursor, fecha_inicio, fecha_fin):
        """Genera reporte de ingresos mensuales"""
        # Consulta SQL para obtener ingresos por mes
        consulta_ventas = """
            SELECT 
                YEAR(v.fecha) as año, 
                MONTH(v.fecha) as mes,
                COUNT(v.id_venta) as cant_ventas,
                SUM(v.total) as total_ventas
            FROM ventas v
            WHERE DATE(v.fecha) BETWEEN %s AND %s
            GROUP BY YEAR(v.fecha), MONTH(v.fecha)
            ORDER BY YEAR(v.fecha), MONTH(v.fecha)
        """

        consulta_servicios = """
            SELECT 
                YEAR(v.fecha) as año, 
                MONTH(v.fecha) as mes,
                COUNT(DISTINCT dv.id_detalle) as cant_servicios,
                SUM(dv.subtotal) as total_servicios
            FROM detalle_venta dv
            JOIN ventas v ON dv.id_venta = v.id_venta
            WHERE dv.tipo_item = 'servicio'
            AND DATE(v.fecha) BETWEEN %s AND %s
            GROUP BY YEAR(v.fecha), MONTH(v.fecha)
            ORDER BY YEAR(v.fecha), MONTH(v.fecha)
        """

        cursor.execute(consulta_ventas, (fecha_inicio, fecha_fin))
        ventas_por_mes = cursor.fetchall()

        cursor.execute(consulta_servicios, (fecha_inicio, fecha_fin))
        servicios_por_mes = cursor.fetchall()

        # Crear diccionario para combinar datos
        datos_por_mes = {}

        # Procesar ventas
        for venta in ventas_por_mes:
            año, mes, cant_ventas, total_ventas = venta
            clave = f"{año}-{mes}"

            if clave not in datos_por_mes:
                datos_por_mes[clave] = {
                    'año': año,
                    'mes': mes,
                    'cant_ventas': cant_ventas,
                    'total_ventas': total_ventas,
                    'cant_servicios': 0,
                    'total_servicios': 0
                }
            else:
                datos_por_mes[clave]['cant_ventas'] = cant_ventas
                datos_por_mes[clave]['total_ventas'] = total_ventas

        # Procesar servicios
        for servicio in servicios_por_mes:
            año, mes, cant_servicios, total_servicios = servicio
            clave = f"{año}-{mes}"

            if clave not in datos_por_mes:
                datos_por_mes[clave] = {
                    'año': año,
                    'mes': mes,
                    'cant_ventas': 0,
                    'total_ventas': 0,
                    'cant_servicios': cant_servicios,
                    'total_servicios': total_servicios
                }
            else:
                datos_por_mes[clave]['cant_servicios'] = cant_servicios
                datos_por_mes[clave]['total_servicios'] = total_servicios

        # Variables para el resumen
        total_general = 0
        total_ventas = 0
        total_servicios = 0

        self.ultimo_resultado_consulta = list(datos_por_mes.values())

        # Insertar datos en la tabla
        for clave in sorted(datos_por_mes.keys()):
            datos = datos_por_mes[clave]

            # Obtener nombre del mes
            try:
                nombre_mes = calendar.month_name[datos['mes']]
            except:
                nombre_mes = f"Mes {datos['mes']}"

            # Calcular total general del mes
            total_general_mes = float(datos['total_ventas']) + float(datos['total_servicios'])

            # Formatear datos
            mes_formateado = f"{nombre_mes} {datos['año']}"
            total_ventas_formateado = f"${float(datos['total_ventas']):.2f}"
            total_servicios_formateado = f"${float(datos['total_servicios']):.2f}"
            total_general_formateado = f"${total_general_mes:.2f}"

            # Insertar en la tabla
            self.tabla_reporte.insert('', tk.END, values=(
                mes_formateado,
                datos['cant_ventas'],
                total_ventas_formateado,
                datos['cant_servicios'],
                total_servicios_formateado,
                total_general_formateado
            ))

            # Actualizar totales
            total_general += total_general_mes
            total_ventas += float(datos['total_ventas'])
            total_servicios += float(datos['total_servicios'])

        # Mostrar resumen en el frame de resumen
        lbl_total_general = tk.Label(
            self.frame_resumen,
            text=f"Total General: ${total_general:.2f}",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5"
        )
        lbl_total_general.pack(side=tk.LEFT, padx=20, pady=5)

        lbl_total_ventas = tk.Label(
            self.frame_resumen,
            text=f"Total Ventas: ${total_ventas:.2f}",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        lbl_total_ventas.pack(side=tk.LEFT, padx=20, pady=5)

        lbl_total_servicios = tk.Label(
            self.frame_resumen,
            text=f"Total Servicios: ${total_servicios:.2f}",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        lbl_total_servicios.pack(side=tk.LEFT, padx=20, pady=5)

        # Guardar datos para gráficos
        self.datos_grafico = {
            'tipo': 'ingresos_mensuales',
            'datos_por_mes': datos_por_mes,
            'total_general': total_general,
            'total_ventas': total_ventas,
            'total_servicios': total_servicios
        }

    def generar_reporte_pedidos_estado(self, cursor, fecha_inicio, fecha_fin):
        """Genera reporte de pedidos por estado"""
        # Condiciones para filtros
        condiciones = ["DATE(fecha_pedido) BETWEEN %s AND %s"]
        parametros = [fecha_inicio, fecha_fin]

        # Filtro de cliente
        if self.filtro_cliente.get().strip():
            condiciones.append("p.id_cliente IN (SELECT id_cliente FROM clientes WHERE nombre LIKE %s)")
            parametros.append(f'%{self.filtro_cliente.get().strip()}%')

        # Filtro de estado específico
        if self.filtro_estado.get() != "Todos":
            condiciones.append("p.estado = %s")
            parametros.append(self.filtro_estado.get())

        # Construir WHERE clause
        where_clause = " AND ".join(condiciones)

        # Consulta para obtener pedidos por estado con tiempo promedio
        consulta = f"""
            SELECT 
                p.estado, 
                COUNT(*) as cantidad,
                AVG(TIMESTAMPDIFF(HOUR, p.fecha_pedido, 
                    CASE 
                        WHEN p.estado = 'Entregado' THEN (
                            SELECT MAX(fecha_hora)
                            FROM historial_estados_pedido
                            WHERE id_pedido = p.id_pedido AND estado_nuevo = 'Entregado'
                        )
                        ELSE NOW() 
                    END
                )) as tiempo_promedio
            FROM pedidos p
            WHERE {where_clause}
            GROUP BY p.estado
            ORDER BY COUNT(*) DESC
        """

        cursor.execute(consulta, parametros)
        pedidos_por_estado = cursor.fetchall()

        # Guardar para visualizaciones
        self.ultimo_resultado_consulta = pedidos_por_estado

        # Calcular total para porcentajes
        total_pedidos = sum(estado[1] for estado in pedidos_por_estado)

        # Variables para el resumen
        estados = {}

        # Insertar datos en la tabla
        for estado in pedidos_por_estado:
            nombre_estado, cantidad, tiempo_promedio = estado

            # Calcular porcentaje
            porcentaje = (cantidad / total_pedidos * 100) if total_pedidos > 0 else 0

            # Formatear datos
            porcentaje_formateado = f"{porcentaje:.2f}%"

            # Formatear tiempo promedio
            if tiempo_promedio is not None:
                horas = int(tiempo_promedio)
                dias = horas // 24
                horas_resto = horas % 24
                tiempo_formateado = f"{dias}d {horas_resto}h"
            else:
                tiempo_formateado = "N/A"

            # Insertar en la tabla con colores según estado
            item_id = self.tabla_reporte.insert('', tk.END, values=(
                nombre_estado,
                cantidad,
                porcentaje_formateado,
                tiempo_formateado
            ))

            self.tabla_reporte.item(item_id, tags=(nombre_estado.lower().replace(" ", "_"),))

            # Guardar para el resumen
            estados[nombre_estado] = cantidad

        # Configurar colores para estados
        self.tabla_reporte.tag_configure("recibido", background="#ffecb3")
        self.tabla_reporte.tag_configure("en_proceso", background="#e3f2fd")
        self.tabla_reporte.tag_configure("listo_para_entrega", background="#e8f5e9")
        self.tabla_reporte.tag_configure("entregado", background="#c8e6c9")
        self.tabla_reporte.tag_configure("cancelado", background="#ffcdd2")

        # Mostrar resumen en el frame de resumen
        lbl_total_pedidos = tk.Label(
            self.frame_resumen,
            text=f"Total Pedidos: {total_pedidos}",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5"
        )
        lbl_total_pedidos.pack(side=tk.LEFT, padx=20, pady=5)

        # Mostrar cantidad de cada estado importante
        estados_importantes = ["Recibido", "En proceso", "Listo para entrega", "Entregado"]
        for estado in estados_importantes:
            cantidad = estados.get(estado, 0)
            porcentaje = (cantidad / total_pedidos * 100) if total_pedidos > 0 else 0

            lbl_estado = tk.Label(
                self.frame_resumen,
                text=f"{estado}: {cantidad} ({porcentaje:.1f}%)",
                font=("Helvetica", 11),
                bg="#f5f5f5"
            )
            lbl_estado.pack(side=tk.LEFT, padx=10, pady=5)

        # Guardar datos para gráficos
        self.datos_grafico = {
            'tipo': 'pedidos_estado',
            'pedidos_por_estado': pedidos_por_estado,
            'total_pedidos': total_pedidos
        }

    def generar_reporte_rentabilidad(self, cursor, fecha_inicio, fecha_fin):
        """Genera reporte de rentabilidad de servicios"""
        consulta = """
            SELECT 
                s.id_servicio,
                s.nombre,
                SUM(dv.cantidad) as cantidad,
                SUM(dv.subtotal) as ingresos,
                SUM(dv.cantidad * s.costo_base) as costos,
                SUM(dv.subtotal) - SUM(dv.cantidad * s.costo_base) as margen,
                (SUM(dv.subtotal) - SUM(dv.cantidad * s.costo_base)) / SUM(dv.subtotal) * 100 as rentabilidad
            FROM detalle_venta dv
            JOIN servicios s ON dv.id_item = s.id_servicio
            JOIN ventas v ON dv.id_venta = v.id_venta
            WHERE dv.tipo_item = 'servicio'
            AND DATE(v.fecha) BETWEEN %s AND %s
            GROUP BY s.id_servicio, s.nombre
            ORDER BY margen DESC
        """

        cursor.execute(consulta, (fecha_inicio, fecha_fin))
        servicios = cursor.fetchall()

        self.ultimo_resultado_consulta = servicios

        # Variables para el resumen
        total_ingresos = 0
        total_costos = 0
        total_margen = 0

        # Insertar datos en la tabla
        for servicio in servicios:
            id_servicio, nombre, cantidad, ingresos, costos, margen, rentabilidad = servicio

            # Formatear datos
            ingresos_formateados = f"${float(ingresos):.2f}"
            costos_formateados = f"${float(costos):.2f}"
            margen_formateado = f"${float(margen):.2f}"
            rentabilidad_formateada = f"{float(rentabilidad):.2f}%"

            # Insertar en la tabla con colores según rentabilidad
            item_id = self.tabla_reporte.insert('', tk.END, values=(
                id_servicio,
                nombre,
                int(cantidad),
                ingresos_formateados,
                costos_formateados,
                margen_formateado,
                rentabilidad_formateada
            ))

            # Aplicar colores según rentabilidad
            if rentabilidad >= 40:
                self.tabla_reporte.item(item_id, tags=("alta_rentabilidad",))
            elif rentabilidad >= 20:
                self.tabla_reporte.item(item_id, tags=("media_rentabilidad",))
            else:
                self.tabla_reporte.item(item_id, tags=("baja_rentabilidad",))

            # Configurar colores
            self.tabla_reporte.tag_configure("alta_rentabilidad", background="#c8e6c9")
            self.tabla_reporte.tag_configure("media_rentabilidad", background="#fff9c4")
            self.tabla_reporte.tag_configure("baja_rentabilidad", background="#ffccbc")

            # Acumular totales
            total_ingresos += float(ingresos)
            total_costos += float(costos)
            total_margen += float(margen)

        # Calcular rentabilidad promedio
        rentabilidad_promedio = (total_margen / total_ingresos * 100) if total_ingresos > 0 else 0

        # Mostrar resumen en el frame de resumen
        lbl_ingresos = tk.Label(
            self.frame_resumen,
            text=f"Ingresos Totales: ${total_ingresos:.2f}",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5"
        )
        lbl_ingresos.pack(side=tk.LEFT, padx=20, pady=5)

        lbl_costos = tk.Label(
            self.frame_resumen,
            text=f"Costos Totales: ${total_costos:.2f}",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        lbl_costos.pack(side=tk.LEFT, padx=20, pady=5)

        lbl_margen = tk.Label(
            self.frame_resumen,
            text=f"Margen Total: ${total_margen:.2f}",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        lbl_margen.pack(side=tk.LEFT, padx=20, pady=5)

        lbl_rentabilidad = tk.Label(
            self.frame_resumen,
            text=f"Rentabilidad Promedio: {rentabilidad_promedio:.2f}%",
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        lbl_rentabilidad.pack(side=tk.LEFT, padx=20, pady=5)

        # Guardar datos para gráficos
        self.datos_grafico = {
            'tipo': 'rentabilidad',
            'servicios': servicios,
            'total_ingresos': total_ingresos,
            'total_costos': total_costos,
            'total_margen': total_margen,
            'rentabilidad_promedio': rentabilidad_promedio
        }

    def generar_reporte_comportamiento_clientes(self, cursor, fecha_inicio, fecha_fin):
        """Genera reporte de comportamiento de clientes (RFM Analysis)"""
        # Consulta para obtener datos RFM (Recencia, Frecuencia, Valor Monetario)
        consulta = """
            SELECT 
                c.id_cliente,
                c.nombre,
                COUNT(v.id_venta) as frecuencia,
                DATEDIFF(CURRENT_DATE, MAX(DATE(v.fecha))) as recencia,
                SUM(v.total) as valor,
                CASE 
                    WHEN COUNT(v.id_venta) > 5 AND DATEDIFF(CURRENT_DATE, MAX(DATE(v.fecha))) < 30 THEN 'VIP'
                    WHEN COUNT(v.id_venta) > 3 AND DATEDIFF(CURRENT_DATE, MAX(DATE(v.fecha))) < 60 THEN 'Regular'
                    WHEN DATEDIFF(CURRENT_DATE, MAX(DATE(v.fecha))) > 90 THEN 'Inactivo'
                    ELSE 'Ocasional'
                END as categoria,
                CASE
                    WHEN COUNT(v.id_venta) > 5 AND DATEDIFF(CURRENT_DATE, MAX(DATE(v.fecha))) < 30 THEN 'Alto'
                    WHEN COUNT(v.id_venta) > 3 AND DATEDIFF(CURRENT_DATE, MAX(DATE(v.fecha))) < 60 THEN 'Medio'
                    ELSE 'Bajo'
                END as potencial
            FROM clientes c
            JOIN ventas v ON c.id_cliente = v.id_cliente
            WHERE DATE(v.fecha) BETWEEN %s AND %s
            GROUP BY c.id_cliente, c.nombre
            ORDER BY frecuencia DESC, recencia ASC
        """

        cursor.execute(consulta, (fecha_inicio, fecha_fin))
        clientes = cursor.fetchall()

        self.ultimo_resultado_consulta = clientes

        # Variables para el resumen
        total_clientes = len(clientes)
        categorias = {}
        potenciales = {}

        # Insertar datos en la tabla
        for cliente in clientes:
            id_cliente, nombre, frecuencia, recencia, valor, categoria, potencial = cliente

            # Formatear datos
            valor_formateado = f"${float(valor):.2f}"

            # Insertar en la tabla con colores según categoría
            item_id = self.tabla_reporte.insert('', tk.END, values=(
                id_cliente,
                nombre,
                frecuencia,
                recencia,
                valor_formateado,
                categoria,
                potencial
            ))

            # Aplicar colores según categoría
            self.tabla_reporte.item(item_id, tags=(categoria.lower(),))

            # Configurar colores
            self.tabla_reporte.tag_configure("vip", background="#c8e6c9")
            self.tabla_reporte.tag_configure("regular", background="#e3f2fd")
            self.tabla_reporte.tag_configure("ocasional", background="#fff9c4")
            self.tabla_reporte.tag_configure("inactivo", background="#ffccbc")

            # Contabilizar categorías
            if categoria in categorias:
                categorias[categoria] += 1
            else:
                categorias[categoria] = 1

            # Contabilizar potenciales
            if potencial in potenciales:
                potenciales[potencial] += 1
            else:
                potenciales[potencial] = 1

        # Mostrar resumen en el frame de resumen
        lbl_total_clientes = tk.Label(
            self.frame_resumen,
            text=f"Total Clientes: {total_clientes}",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5"
        )
        lbl_total_clientes.pack(side=tk.LEFT, padx=20, pady=5)

        # Mostrar conteo por categoría
        for categoria, cantidad in categorias.items():
            lbl_categoria = tk.Label(
                self.frame_resumen,
                text=f"{categoria}: {cantidad}",
                font=("Helvetica", 11),
                bg="#f5f5f5"
            )
            lbl_categoria.pack(side=tk.LEFT, padx=10, pady=5)

        # Guardar datos para gráficos
        self.datos_grafico = {
            'tipo': 'comportamiento_clientes',
            'clientes': clientes,
            'categorias': categorias,
            'potenciales': potenciales
        }

    def generar_dashboard(self, cursor, fecha_inicio, fecha_fin):
        """Genera el dashboard general con múltiples visualizaciones"""
        # Mostrar pestaña de dashboard
        self.notebook.select(self.tab_dashboard)

        # Limpiar tabla de resumen
        for item in self.tabla_reporte.get_children():
            self.tabla_reporte.delete(item)

        # Generar datos para cada sección del dashboard
        # 1. Ventas por periodo (gráfico superior izquierdo)
        consulta_ventas = """
            SELECT 
                DATE(fecha) as fecha, 
                SUM(total) as total
            FROM ventas
            WHERE DATE(fecha) BETWEEN %s AND %s
            GROUP BY DATE(fecha)
            ORDER BY fecha
        """

        cursor.execute(consulta_ventas, (fecha_inicio, fecha_fin))
        ventas_diarias = cursor.fetchall()

        # 2. Servicios más solicitados (gráfico superior derecho)
        consulta_servicios = """
            SELECT 
                s.nombre, 
                SUM(dv.cantidad) as cantidad
            FROM detalle_venta dv
            JOIN servicios s ON dv.id_item = s.id_servicio
            JOIN ventas v ON dv.id_venta = v.id_venta
            WHERE dv.tipo_item = 'servicio'
            AND DATE(v.fecha) BETWEEN %s AND %s
            GROUP BY s.nombre
            ORDER BY cantidad DESC
            LIMIT 5
        """

        cursor.execute(consulta_servicios, (fecha_inicio, fecha_fin))
        top_servicios = cursor.fetchall()

        # 3. Pedidos por estado (gráfico inferior izquierdo)
        consulta_pedidos = """
            SELECT 
                estado, 
                COUNT(*) as cantidad
            FROM pedidos
            WHERE DATE(fecha_pedido) BETWEEN %s AND %s
            GROUP BY estado
        """

        cursor.execute(consulta_pedidos, (fecha_inicio, fecha_fin))
        pedidos_por_estado = cursor.fetchall()

        # 4. Clientes frecuentes (gráfico inferior derecho)
        consulta_clientes = """
            SELECT 
                c.nombre, 
                COUNT(v.id_venta) as visitas
            FROM clientes c
            JOIN ventas v ON c.id_cliente = v.id_cliente
            WHERE DATE(v.fecha) BETWEEN %s AND %s
            GROUP BY c.nombre
            ORDER BY visitas DESC
            LIMIT 5
        """

        cursor.execute(consulta_clientes, (fecha_inicio, fecha_fin))
        top_clientes = cursor.fetchall()

        # Generar métricas resumidas para la tabla
        # Total de ventas
        consulta_total_ventas = """
            SELECT 
                COUNT(*) as cantidad, 
                SUM(total) as total,
                AVG(total) as promedio
            FROM ventas
            WHERE DATE(fecha) BETWEEN %s AND %s
        """

        cursor.execute(consulta_total_ventas, (fecha_inicio, fecha_fin))
        resumen_ventas = cursor.fetchone()

        # Calcular variación respecto al periodo anterior
        periodo_actual = (datetime.strptime(fecha_fin, '%Y-%m-%d') - datetime.strptime(fecha_inicio, '%Y-%m-%d')).days
        fecha_inicio_anterior = (datetime.strptime(fecha_inicio, '%Y-%m-%d') - timedelta(days=periodo_actual)).strftime('%Y-%m-%d')
        fecha_fin_anterior = (datetime.strptime(fecha_inicio, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')

        consulta_periodo_anterior = """
            SELECT 
                COUNT(*) as cantidad, 
                SUM(total) as total
            FROM ventas
            WHERE DATE(fecha) BETWEEN %s AND %s
        """

        cursor.execute(consulta_periodo_anterior, (fecha_inicio_anterior, fecha_fin_anterior))
        resumen_anterior = cursor.fetchone()

        # Insertar datos en la tabla de resumen
        if resumen_ventas and resumen_anterior:
            cantidad_actual, total_actual, promedio_actual = resumen_ventas
            cantidad_anterior, total_anterior = resumen_anterior

            # Calcular variaciones
            var_cantidad = ((cantidad_actual - cantidad_anterior) / cantidad_anterior * 100) if cantidad_anterior else 100
            var_total = ((total_actual - total_anterior) / total_anterior * 100) if total_anterior else 100

            # Insertar en tabla
            self.tabla_reporte.insert('', tk.END, values=(
                "Total Ventas",
                f"${float(total_actual):.2f}",
                f"{var_total:+.2f}%" if var_total else "N/A"
            ))

            self.tabla_reporte.insert('', tk.END, values=(
                "Cantidad de Ventas",
                cantidad_actual,
                f"{var_cantidad:+.2f}%" if var_cantidad else "N/A"
            ))

            self.tabla_reporte.insert('', tk.END, values=(
                "Ticket Promedio",
                f"${float(promedio_actual):.2f}",
                "N/A"
            ))

        # Total de pedidos activos
        consulta_pedidos_activos = """
            SELECT 
                COUNT(*) as cantidad
            FROM pedidos
            WHERE estado NOT IN ('Entregado', 'Cancelado')
            AND DATE(fecha_pedido) BETWEEN %s AND %s
        """

        cursor.execute(consulta_pedidos_activos, (fecha_inicio, fecha_fin))
        pedidos_activos = cursor.fetchone()

        if pedidos_activos:
            self.tabla_reporte.insert('', tk.END, values=(
                "Pedidos Activos",
                pedidos_activos[0],
                "N/A"
            ))

        # Generar gráficos del dashboard
        self.generar_graficos_dashboard(
            ventas_diarias,
            top_servicios,
            pedidos_por_estado,
            top_clientes
        )

    def generar_graficos_dashboard(self, ventas_diarias, top_servicios, pedidos_por_estado, top_clientes):
        """Genera los gráficos para el dashboard general"""
        # Limpiar figuras existentes
        for fig in self.dashboard_figs:
            fig.clear()

        # 1. Gráfico de ventas por periodo (línea)
        ax1 = self.dashboard_figs[0].add_subplot(111)

        if ventas_diarias:
            fechas = [venta[0] for venta in ventas_diarias]
            totales = [float(venta[1]) for venta in ventas_diarias]

            ax1.plot(fechas, totales, marker='o', linestyle='-', color='#3a7ff6', linewidth=2)
            ax1.set_title('Ventas Diarias', fontsize=12)
            ax1.set_ylabel('Ventas ($)')
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            ax1.tick_params(axis='x', rotation=45)
            ax1.grid(True, linestyle='--', alpha=0.7)

            # Agregar texto del total
            total_ventas = sum(totales)
            ax1.text(0.02, 0.95, f'Total: ${total_ventas:.2f}', transform=ax1.transAxes,
                     fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
        else:
            ax1.text(0.5, 0.5, 'No hay datos disponibles', ha='center', va='center', fontsize=12)

        self.dashboard_figs[0].tight_layout()
        self.dashboard_canvas[0].draw()

        # 2. Gráfico de servicios más solicitados (barras)
        ax2 = self.dashboard_figs[1].add_subplot(111)

        if top_servicios:
            servicios = [servicio[0] for servicio in top_servicios]
            cantidades = [int(servicio[1]) for servicio in top_servicios]

            # Truncar nombres largos
            servicios_short = [s[:15] + '...' if len(s) > 15 else s for s in servicios]

            bars = ax2.barh(servicios_short, cantidades, color='#4caf50')
            ax2.set_title('Top 5 Servicios', fontsize=12)
            ax2.set_xlabel('Cantidad')

            # Añadir etiquetas de datos
            for bar in bars:
                width = bar.get_width()
                ax2.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                         f'{width:.0f}', ha='left', va='center', fontsize=9)
        else:
            ax2.text(0.5, 0.5, 'No hay datos disponibles', ha='center', va='center', fontsize=12)

        self.dashboard_figs[1].tight_layout()
        self.dashboard_canvas[1].draw()

        # 3. Gráfico de pedidos por estado (pie)
        ax3 = self.dashboard_figs[2].add_subplot(111)

        if pedidos_por_estado:
            estados = [estado[0] for estado in pedidos_por_estado]
            cantidades = [int(estado[1]) for estado in pedidos_por_estado]

            # Colores para cada estado
            colores = []
            for estado in estados:
                if estado == "Recibido":
                    colores.append('#ffecb3')
                elif estado == "En proceso":
                    colores.append('#e3f2fd')
                elif estado == "Listo para entrega":
                    colores.append('#e8f5e9')
                elif estado == "Entregado":
                    colores.append('#c8e6c9')
                elif estado == "Cancelado":
                    colores.append('#ffcdd2')
                else:
                    colores.append('#e0e0e0')

            wedges, texts, autotexts = ax3.pie(
                cantidades,
                labels=estados,
                autopct='%1.1f%%',
                startangle=90,
                colors=colores,
                wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
                textprops={'fontsize': 9}
            )

            for autotext in autotexts:
                autotext.set_fontsize(8)

            ax3.set_title('Pedidos por Estado', fontsize=12)
            ax3.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        else:
            ax3.text(0.5, 0.5, 'No hay datos disponibles', ha='center', va='center', fontsize=12)

        self.dashboard_figs[2].tight_layout()
        self.dashboard_canvas[2].draw()

        # 4. Gráfico de clientes frecuentes (barras)
        ax4 = self.dashboard_figs[3].add_subplot(111)

        if top_clientes:
            clientes = [cliente[0] for cliente in top_clientes]
            visitas = [int(cliente[1]) for cliente in top_clientes]

            # Truncar nombres largos
            clientes_short = [c[:15] + '...' if len(c) > 15 else c for c in clientes]

            bars = ax4.barh(clientes_short, visitas, color='#9c27b0')
            ax4.set_title('Top 5 Clientes', fontsize=12)
            ax4.set_xlabel('Visitas')

            # Añadir etiquetas de datos
            for bar in bars:
                width = bar.get_width()
                ax4.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                         f'{width:.0f}', ha='left', va='center', fontsize=9)
        else:
            ax4.text(0.5, 0.5, 'No hay datos disponibles', ha='center', va='center', fontsize=12)

        self.dashboard_figs[3].tight_layout()
        self.dashboard_canvas[3].draw()

    def actualizar_grafico(self):
        """Actualiza el gráfico según los datos y tipo seleccionado"""
        # Verificar si hay datos para graficar
        if not hasattr(self, 'datos_grafico') or not self.datos_grafico:
            return

        # Limpiar figura actual
        self.fig.clear()

        # Obtener tipo de gráfico seleccionado
        tipo_grafico = self.tipo_grafico.get()

        # Aplicar estilo seleccionado
        estilo = self.estilo_grafico.get()
        if estilo != "predeterminado":
            sns.set_palette(estilo)

        # Crear subplot
        ax = self.fig.add_subplot(111)

        # Generar gráfico según el tipo de reporte
        if self.datos_grafico['tipo'] == 'ventas':
            self.graficar_ventas(ax, tipo_grafico)

        elif self.datos_grafico['tipo'] == 'productos':
            self.graficar_productos(ax, tipo_grafico)

        elif self.datos_grafico['tipo'] == 'servicios':
            self.graficar_servicios(ax, tipo_grafico)

        elif self.datos_grafico['tipo'] == 'clientes':
            self.graficar_clientes(ax, tipo_grafico)

        elif self.datos_grafico['tipo'] == 'ingresos_mensuales':
            self.graficar_ingresos_mensuales(ax, tipo_grafico)

        elif self.datos_grafico['tipo'] == 'pedidos_estado':
            self.graficar_pedidos_estado(ax, tipo_grafico)

        elif self.datos_grafico['tipo'] == 'rentabilidad':
            self.graficar_rentabilidad(ax, tipo_grafico)

        elif self.datos_grafico['tipo'] == 'comportamiento_clientes':
            self.graficar_comportamiento_clientes(ax, tipo_grafico)

        # Ajustar layout y redimensionar
        self.fig.tight_layout()

        # Actualizar canvas
        self.canvas.draw()

    def graficar_ventas(self, ax, tipo_grafico):
        """Genera gráfico de ventas"""
        ventas = self.datos_grafico['ventas']

        # Agrupar ventas por fecha para gráfico
        ventas_por_fecha = {}
        for venta in ventas:
            fecha = venta[0]  # La fecha está en la primera posición
            # Convertir a string para usar como clave
            fecha_str = fecha.strftime("%d/%m/%Y") if isinstance(fecha, datetime) else str(fecha)

            if fecha_str in ventas_por_fecha:
                ventas_por_fecha[fecha_str] += float(venta[3])  # El total está en la cuarta posición
            else:
                ventas_por_fecha[fecha_str] = float(venta[3])

        # Ordenar por fecha
        fechas = sorted(ventas_por_fecha.keys(),
                        key=lambda x: datetime.strptime(x, "%d/%m/%Y") if "/" in x else datetime.strptime(x, "%Y-%m-%d"))
        totales = [ventas_por_fecha[fecha] for fecha in fechas]

        # Crear gráfico según tipo seleccionado
        if tipo_grafico == "Barras":
            ax.bar(fechas, totales, color='skyblue', edgecolor='navy')

            # Agregar etiquetas de valores
            for i, v in enumerate(totales):
                ax.text(i, v + 0.1, f'${v:.2f}', ha='center', fontsize=8, rotation=90)

        elif tipo_grafico == "Líneas":
            ax.plot(fechas, totales, marker='o', linestyle='-', color='blue', linewidth=2)

            # Agregar etiquetas de valores en puntos
            for i, v in enumerate(totales):
                ax.annotate(f'${v:.2f}', (fechas[i], v),
                            textcoords="offset points",
                            xytext=(0, 10),
                            ha='center',
                            fontsize=8)

        elif tipo_grafico == "Área":
            ax.fill_between(fechas, totales, color='skyblue', alpha=0.5)
            ax.plot(fechas, totales, color='navy')

        elif tipo_grafico == "Pastel":
            # Para gráfico de pastel, mostrar por método de pago
            metodos_pago = self.datos_grafico['metodos_pago']
            labels = list(metodos_pago.keys())
            sizes = list(metodos_pago.values())

            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
                   colors=sns.color_palette("bright", len(labels)),
                   wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            ax.set_title('Distribución por Método de Pago')
            return  # Salir temprano para no aplicar configuración estándar

        elif tipo_grafico == "Barras Horizontales":
            ax.barh(fechas, totales, color='skyblue', edgecolor='navy')

            # Agregar etiquetas de valores
            for i, v in enumerate(totales):
                ax.text(v + 0.1, i, f'${v:.2f}', va='center', fontsize=8)

        elif tipo_grafico == "Calor":
            # Para el mapa de calor, necesitamos reorganizar los datos
            # Convertir las fechas a objetos datetime
            fechas_dt = [datetime.strptime(fecha, "%d/%m/%Y") if "/" in fecha else datetime.strptime(fecha, "%Y-%m-%d")
                       for fecha in fechas]

            # Extraer día de la semana y semana
            dias_semana = [dt.strftime('%A') for dt in fechas_dt]
            semanas = [dt.strftime('%W') for dt in fechas_dt]

            # Crear matriz para el mapa de calor
            dias_unicos = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            semanas_unicas = sorted(set(semanas))

            data = np.zeros((len(dias_unicos), len(semanas_unicas)))

            for fecha, total, dia, semana in zip(fechas_dt, totales, dias_semana, semanas):
                dia_idx = dias_unicos.index(dia)
                semana_idx = semanas_unicas.index(semana)
                data[dia_idx][semana_idx] = total

            # Crear mapa de calor
            sns.heatmap(data, ax=ax, annot=True, fmt=".1f", cmap="YlGnBu",
                       xticklabels=[f"Sem {s}" for s in semanas_unicas],
                       yticklabels=dias_unicos)

            ax.set_title('Mapa de Calor de Ventas por Día y Semana')
            return  # Salir temprano para no aplicar configuración estándar

        # Configuración del gráfico
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Total ($)')
        ax.set_title('Ventas por Fecha')
        ax.grid(True, linestyle='--', alpha=0.7)

        # Rotar etiquetas si hay muchas fechas
        if len(fechas) > 5:
            plt.xticks(rotation=45, ha='right')

        # Agregar línea de tendencia
        if len(totales) > 1 and tipo_grafico in ["Líneas", "Área"]:
            z = np.polyfit(range(len(totales)), totales, 1)
            p = np.poly1d(z)
            ax.plot(fechas, p(range(len(totales))), "r--", linewidth=1)

    def graficar_productos(self, ax, tipo_grafico):
        """Genera gráfico de productos más vendidos"""
        productos = self.datos_grafico['productos']

        # Limitar a los 10 productos más vendidos para mejor visualización
        top_productos = productos[:10] if len(productos) > 10 else productos

        nombres = [producto[1] for producto in top_productos]
        cantidades = [int(producto[2]) for producto in top_productos]
        ingresos = [float(producto[3]) for producto in top_productos]

        # Acortar nombres largos
        nombres_cortos = [nombre[:20] + "..." if len(nombre) > 20 else nombre for nombre in nombres]

        # Crear gráfico según tipo seleccionado
        if tipo_grafico == "Barras":
            # Crear dos ejes para mostrar cantidades e ingresos
            ax2 = ax.twinx()

            # Barras de cantidad
            bars1 = ax.bar([i - 0.2 for i in range(len(nombres_cortos))], cantidades, width=0.4,
                          color='skyblue', label='Cantidad')

            # Barras de ingresos
            bars2 = ax2.bar([i + 0.2 for i in range(len(nombres_cortos))], ingresos, width=0.4,
                           color='salmon', label='Ingresos ($)')

            # Etiquetas
            ax.set_xticks(range(len(nombres_cortos)))
            ax.set_xticklabels(nombres_cortos, rotation=45, ha='right')

            # Leyenda combinada
            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

            # Etiquetas de ejes
            ax.set_ylabel('Cantidad')
            ax2.set_ylabel('Ingresos ($)')
            ax.set_title('Top Productos por Cantidad y Ventas')

        elif tipo_grafico == "Líneas":
            # No es ideal para esta visualización, usar gráfico de puntos
            ax.plot(nombres_cortos, cantidades, marker='o', linestyle='-', color='blue', label='Cantidad')

            # Crear eje secundario para ingresos
            ax2 = ax.twinx()
            ax2.plot(nombres_cortos, ingresos, marker='s', linestyle='--', color='red', label='Ingresos ($)')

            # Rotar etiquetas
            plt.xticks(rotation=45, ha='right')

            # Leyenda combinada
            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

            ax.set_ylabel('Cantidad')
            ax2.set_ylabel('Ingresos ($)')
            ax.set_title('Productos por Cantidad e Ingresos')

        elif tipo_grafico == "Pastel":
            # Para gráfico de pastel, mostrar por cantidades
            plt.rcParams.update({'font.size': 9})
            wedges, texts, autotexts = ax.pie(cantidades, labels=nombres_cortos, autopct='%1.1f%%',
                                            startangle=90, colors=plt.cm.tab20.colors,
                                            wedgeprops={'edgecolor': 'white', 'linewidth': 1})

            # Hacer etiquetas más pequeñas
            plt.setp(texts, size=8)
            plt.setp(autotexts, size=8, weight='bold')

            ax.axis('equal')
            ax.set_title('Distribución de Productos Vendidos')

        elif tipo_grafico == "Barras Horizontales":
            # Invertir el orden para que el más vendido aparezca arriba
            nombres_cortos = nombres_cortos[::-1]
            cantidades = cantidades[::-1]
            ingresos = ingresos[::-1]

            # Crear dos ejes para mostrar cantidades e ingresos
            ax.barh(nombres_cortos, cantidades, color='skyblue', alpha=0.7, label='Cantidad')
            ax2 = ax.twiny()
            ax2.barh(nombres_cortos, ingresos, color='salmon', alpha=0.5, label='Ingresos ($)')

            # Etiquetas de datos
            for i, v in enumerate(cantidades):
                ax.text(v + 0.5, i, f'{v}', va='center', fontsize=8)

            # Leyenda
            ax.legend(loc='lower right')
            ax2.legend(loc='upper right')

            ax.set_title('Productos por Cantidad y Ventas')
            ax.set_xlabel('Cantidad')
            ax2.set_xlabel('Ingresos ($)')

        elif tipo_grafico == "Área":
            # Esta visualización no es ideal para comparar productos
            # Se implementa como gráfico de áreas apiladas
            ax.fill_between(nombres_cortos, cantidades, alpha=0.5, color='skyblue', label='Cantidad')
            ax.plot(nombres_cortos, cantidades, 'o-', color='blue')

            ax2 = ax.twinx()
            ax2.plot(nombres_cortos, ingresos, 's--', color='red', label='Ingresos ($)')

            # Rotar etiquetas
            plt.xticks(rotation=45, ha='right')

            # Leyenda combinada
            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

            ax.set_ylabel('Cantidad')
            ax2.set_ylabel('Ingresos ($)')
            ax.set_title('Productos por Cantidad e Ingresos')

        elif tipo_grafico == "Dispersión":
            # Este tipo de gráfico es ideal para ver la relación entre cantidad e ingresos
            ax.scatter(cantidades, ingresos, c=range(len(cantidades)), cmap='viridis',
                     s=100, alpha=0.7, edgecolors='black')

            # Añadir etiquetas a cada punto
            for i, txt in enumerate(nombres_cortos):
                ax.annotate(txt, (cantidades[i], ingresos[i]),
                          xytext=(5, 5), textcoords='offset points', fontsize=8)

            ax.set_xlabel('Cantidad Vendida')
            ax.set_ylabel('Ingresos ($)')
            ax.set_title('Relación entre Cantidad e Ingresos por Producto')
            ax.grid(True, linestyle='--', alpha=0.7)

        elif tipo_grafico == "Calor":
            # Para un mapa de calor, necesitamos una matriz 2D
            # Podemos mostrar la relación entre productos, cantidades e ingresos

            # Crear una matriz normalizada
            data = []
            for i, nombre in enumerate(nombres_cortos):
                fila = [nombre, cantidades[i], ingresos[i], ingresos[i]/cantidades[i]]
                data.append(fila)

            # Convertir a DataFrame
            import pandas as pd
            df = pd.DataFrame(data, columns=['Producto', 'Cantidad', 'Ingresos', 'Precio Unitario'])

            # Crear matriz para el mapa de calor (normalizando los valores)
            matriz = df.iloc[:, 1:].apply(lambda x: (x - x.min()) / (x.max() - x.min()), axis=0)

            # Crear mapa de calor
            sns.heatmap(matriz.T, ax=ax, annot=True, fmt=".2f", cmap="YlGnBu",
                       xticklabels=nombres_cortos,
                       yticklabels=['Cantidad', 'Ingresos', 'Precio Unit.'])

            ax.set_title('Análisis de Productos (Valores Normalizados)')
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
            return  # Salir temprano para no aplicar configuración estándar

    def graficar_servicios(self, ax, tipo_grafico):
        """Genera gráfico de servicios más solicitados"""
        servicios = self.datos_grafico['servicios']

        # Limitar a los 10 servicios más solicitados para mejor visualización
        top_servicios = servicios[:10] if len(servicios) > 10 else servicios

        nombres = [servicio[1] for servicio in top_servicios]
        cantidades = [int(servicio[2]) for servicio in top_servicios]
        ingresos = [float(servicio[3]) for servicio in top_servicios]

        # Acortar nombres largos
        nombres_cortos = [nombre[:20] + "..." if len(nombre) > 20 else nombre for nombre in nombres]

        # La implementación de la visualización es similar a la de productos
        # Pero con colores diferentes para diferenciarlos

        if tipo_grafico == "Barras":
            ax2 = ax.twinx()
            bars1 = ax.bar([i - 0.2 for i in range(len(nombres_cortos))], cantidades, width=0.4,
                          color='lightgreen', label='Cantidad')
            bars2 = ax2.bar([i + 0.2 for i in range(len(nombres_cortos))], ingresos, width=0.4,
                           color='orange', label='Ingresos ($)')

            ax.set_xticks(range(len(nombres_cortos)))
            ax.set_xticklabels(nombres_cortos, rotation=45, ha='right')

            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

            ax.set_ylabel('Cantidad')
            ax2.set_ylabel('Ingresos ($)')
            ax.set_title('Top Servicios por Cantidad y Ventas')

        elif tipo_grafico == "Líneas":
            ax.plot(nombres_cortos, cantidades, marker='o', linestyle='-', color='green', label='Cantidad')

            ax2 = ax.twinx()
            ax2.plot(nombres_cortos, ingresos, marker='s', linestyle='--', color='orange', label='Ingresos ($)')

            plt.xticks(rotation=45, ha='right')

            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

            ax.set_ylabel('Cantidad')
            ax2.set_ylabel('Ingresos ($)')
            ax.set_title('Servicios por Cantidad e Ingresos')

        elif tipo_grafico == "Pastel":
            plt.rcParams.update({'font.size': 9})
            wedges, texts, autotexts = ax.pie(cantidades, labels=nombres_cortos, autopct='%1.1f%%',
                                            startangle=90, colors=plt.cm.Set3.colors,
                                            wedgeprops={'edgecolor': 'white', 'linewidth': 1})

            plt.setp(texts, size=8)
            plt.setp(autotexts, size=8, weight='bold')

            ax.axis('equal')
            ax.set_title('Distribución de Servicios Solicitados')

        elif tipo_grafico == "Barras Horizontales":
            nombres_cortos = nombres_cortos[::-1]
            cantidades = cantidades[::-1]
            ingresos = ingresos[::-1]

            ax.barh(nombres_cortos, cantidades, color='lightgreen', alpha=0.7, label='Cantidad')
            ax2 = ax.twiny()
            ax2.barh(nombres_cortos, ingresos, color='orange', alpha=0.5, label='Ingresos ($)')

            for i, v in enumerate(cantidades):
                ax.text(v + 0.5, i, f'{v}', va='center', fontsize=8)

            ax.legend(loc='lower right')
            ax2.legend(loc='upper right')

            ax.set_title('Servicios por Cantidad y Ventas')
            ax.set_xlabel('Cantidad')
            ax2.set_xlabel('Ingresos ($)')

        elif tipo_grafico == "Área":
            ax.fill_between(nombres_cortos, cantidades, alpha=0.5, color='lightgreen', label='Cantidad')
            ax.plot(nombres_cortos, cantidades, 'o-', color='green')

            ax2 = ax.twinx()
            ax2.plot(nombres_cortos, ingresos, 's--', color='orange', label='Ingresos ($)')

            plt.xticks(rotation=45, ha='right')

            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

            ax.set_ylabel('Cantidad')
            ax2.set_ylabel('Ingresos ($)')
            ax.set_title('Servicios por Cantidad e Ingresos')

        elif tipo_grafico == "Dispersión":
            ax.scatter(cantidades, ingresos, c=range(len(cantidades)), cmap='Greens',
                     s=100, alpha=0.7, edgecolors='black')

            for i, txt in enumerate(nombres_cortos):
                ax.annotate(txt, (cantidades[i], ingresos[i]),
                          xytext=(5, 5), textcoords='offset points', fontsize=8)

            ax.set_xlabel('Cantidad Solicitada')
            ax.set_ylabel('Ingresos ($)')
            ax.set_title('Relación entre Cantidad e Ingresos por Servicio')
            ax.grid(True, linestyle='--', alpha=0.7)

        elif tipo_grafico == "Calor":
            # Similar a productos
            data = []
            for i, nombre in enumerate(nombres_cortos):
                fila = [nombre, cantidades[i], ingresos[i], ingresos[i]/cantidades[i]]
                data.append(fila)

            import pandas as pd
            df = pd.DataFrame(data, columns=['Servicio', 'Cantidad', 'Ingresos', 'Precio Unitario'])
            matriz = df.iloc[:, 1:].apply(lambda x: (x - x.min()) / (x.max() - x.min()), axis=0)

            sns.heatmap(matriz.T, ax=ax, annot=True, fmt=".2f", cmap="YlGnBu",
                       xticklabels=nombres_cortos,
                       yticklabels=['Cantidad', 'Ingresos', 'Precio Unit.'])

            ax.set_title('Análisis de Servicios (Valores Normalizados)')
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right='ID')
            self.tabla_reporte.heading('nombre', text='Servicio')
            self.tabla_reporte.heading('cantidad_total', text='Cantidad Solicitada')
            self.tabla_reporte.heading('ingresos_total', text='Ingresos Generados')
            self.tabla_reporte.heading('precio_promedio', text='Precio Promedio')

            self.tabla_reporte.column('id_servicio', width=50, anchor=tk.CENTER)
            self.tabla_reporte.column('nombre', width=300)
            self.tabla_reporte.column('cantidad_total', width=120, anchor=tk.CENTER)
            self.tabla_reporte.column('ingresos_total', width=150, anchor=tk.E)
            self.tabla_reporte.column('precio_promedio', width=120, anchor=tk.E)

        elif tipo_seleccionado == "Clientes Frecuentes":
            columnas = ('id_cliente', 'nombre', 'visitas', 'gasto_total', 'puntos', 'ultima_visita', 'promedio_compra')
            self.tabla_reporte['columns'] = columnas

            self.tabla_reporte.heading('id_cliente', text='ID')
            self.tabla_reporte.heading('nombre', text='Cliente')
            self.tabla_reporte.heading('visitas', text='Visitas')
            self.tabla_reporte.heading('gasto_total', text='Gasto Total')
            self.tabla_reporte.heading('puntos', text='Puntos')
            self.tabla_reporte.heading('ultima_visita', text='Última Visita')
            self.tabla_reporte.heading('promedio_compra', text='Promedio/Compra')

            self.tabla_reporte.column('id_cliente', width=50, anchor=tk.CENTER)
            self.tabla_reporte.column('nombre', width=200)
            self.tabla_reporte.column('visitas', width=80, anchor=tk.CENTER)
            self.tabla_reporte.column('gasto_total', width=100, anchor=tk.E)
            self.tabla_reporte.column('puntos', width=80, anchor=tk.CENTER)
            self.tabla_reporte.column('ultima_visita', width=120, anchor=tk.CENTER)
            self.tabla_reporte.column('promedio_compra', width=120, anchor=tk.E)

        elif tipo_seleccionado == "Ingresos Mensuales":
            columnas = ('mes', 'ventas', 'total_ventas', 'servicios', 'total_servicios', 'total_general')
            self.tabla_reporte['columns'] = columnas

            self.tabla_reporte.heading('mes', text='Mes')
            self.tabla_reporte.heading('ventas', text='Cant. Ventas')
            self.tabla_reporte.heading('total_ventas', text='Total Ventas')
            self.tabla_reporte.heading('servicios', text='Cant. Servicios')
            self.tabla_reporte.heading('total_servicios', text='Total Servicios')
            self.tabla_reporte.heading('total_general', text='Total General')

            self.tabla_reporte.column('mes', width=100, anchor=tk.W)
            self.tabla_reporte.column('ventas', width=100, anchor=tk.CENTER)
            self.tabla_reporte.column('total_ventas', width=120, anchor=tk.E)
            self.tabla_reporte.column('servicios', width=120, anchor=tk.CENTER)
            self.tabla_reporte.column('total_servicios', width=120, anchor=tk.E)
            self.tabla_reporte.column('total_general', width=120, anchor=tk.E)

        elif tipo_seleccionado == "Pedidos por Estado":
            columnas = ('estado', 'cantidad', 'porcentaje', 'tiempo_promedio')
            self.tabla_reporte['columns'] = columnas

            self.tabla_reporte.heading('estado', text='Estado')
            self.tabla_reporte.heading('cantidad', text='Cantidad')
            self.tabla_reporte.heading('porcentaje', text='Porcentaje')
            self.tabla_reporte.heading('tiempo_promedio', text='Tiempo Promedio')

            self.tabla_reporte.column('estado', width=150, anchor=tk.W)
            self.tabla_reporte.column('cantidad', width=100, anchor=tk.CENTER)
            self.tabla_reporte.column('porcentaje', width=100, anchor=tk.CENTER)
            self.tabla_reporte.column('tiempo_promedio', width=150, anchor=tk.CENTER)

            # Filtros adicionales
            self.crear_filtros_pedidos()

        elif tipo_seleccionado == "Rentabilidad de Servicios":
            columnas = ('id_servicio', 'nombre', 'cantidad', 'ingresos', 'costos', 'margen', 'rentabilidad')
            self.tabla_reporte['columns'] = columnas

            self.tabla_reporte.heading('id_servicio', text