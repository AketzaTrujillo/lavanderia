

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

    def guardar_grafico_como_imagen(self):
        """Guarda el gráfico actual como una imagen"""
        # Verificar si hay un gráfico para guardar
        if not hasattr(self, 'fig') or self.fig is None:
            messagebox.showwarning("Sin gráfico", "No hay un gráfico para guardar. Genere un reporte primero.")
            return

        # Tipo de archivo
        filetypes = [
            ("PNG", "*.png"),
            ("JPEG", "*.jpg"),
            ("SVG", "*.svg"),
            ("PDF", "*.pdf")
        ]

        # Solicitar nombre de archivo
        filename = filedialog.asksaveasfilename(
            title="Guardar gráfico como",
            filetypes=filetypes,
            defaultextension=".png"
        )

        if filename:
            try:
                # Guardar figura actual
                self.fig.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Éxito", f"Gráfico guardado como {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la imagen: {str(e)}")
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

    def calcular_rfm_real(self, cursor, fecha_inicio, fecha_fin):
        """Calcula datos RFM reales para análisis de clientes"""
        # Consulta SQL para obtener métricas RFM reales de la base de datos
        consulta_rfm = """
            SELECT 
                c.id_cliente,
                c.nombre,
                COUNT(v.id_venta) as frecuencia,
                DATEDIFF(CURRENT_DATE, MAX(DATE(v.fecha))) as recencia,
                SUM(v.total) as valor_monetario,
                CASE 
                    WHEN COUNT(v.id_venta) > 5 AND DATEDIFF(CURRENT_DATE, MAX(DATE(v.fecha))) < 30 THEN 'VIP'
                    WHEN COUNT(v.id_venta) > 3 AND DATEDIFF(CURRENT_DATE, MAX(DATE(v.fecha))) < 60 THEN 'Regular'
                    WHEN DATEDIFF(CURRENT_DATE, MAX(DATE(v.fecha))) > 90 THEN 'Inactivo'
                    ELSE 'Ocasional'
                END as categoria
            FROM clientes c
            JOIN ventas v ON c.id_cliente = v.id_cliente
            WHERE DATE(v.fecha) BETWEEN %s AND %s
            GROUP BY c.id_cliente, c.nombre
            ORDER BY valor_monetario DESC, frecuencia DESC
        """

        cursor.execute(consulta_rfm, (fecha_inicio, fecha_fin))
        resultados = cursor.fetchall()

        return resultados

    def graficar_comportamiento_clientes(self, ax, tipo_grafico):
        """Genera gráfico de comportamiento de clientes basado en datos reales de la BD"""
        # Obtener datos del historial de clientes directamente de la base de datos
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Consulta para análisis RFM (Recencia, Frecuencia, Valor Monetario)
            consulta_rfm = """
                SELECT 
                    c.id_cliente,
                    c.nombre,
                    COUNT(v.id_venta) as frecuencia,
                    DATEDIFF(CURRENT_DATE, MAX(DATE(v.fecha))) as recencia,
                    SUM(v.total) as valor_monetario,
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
                ORDER BY valor_monetario DESC, frecuencia DESC
            """

            cursor.execute(consulta_rfm, (self.fecha_inicio.get(), self.fecha_fin.get()))
            clientes_rfm = cursor.fetchall()

            # Consulta para obtener distribución de categorías
            consulta_categorias = """
                SELECT 
                    CASE 
                        WHEN COUNT(v.id_venta) > 5 AND DATEDIFF(CURRENT_DATE, MAX(DATE(v.fecha))) < 30 THEN 'VIP'
                        WHEN COUNT(v.id_venta) > 3 AND DATEDIFF(CURRENT_DATE, MAX(DATE(v.fecha))) < 60 THEN 'Regular'
                        WHEN DATEDIFF(CURRENT_DATE, MAX(DATE(v.fecha))) > 90 THEN 'Inactivo'
                        ELSE 'Ocasional'
                    END as categoria,
                    COUNT(DISTINCT c.id_cliente) as total_clientes
                FROM clientes c
                JOIN ventas v ON c.id_cliente = v.id_cliente
                WHERE DATE(v.fecha) BETWEEN %s AND %s
                GROUP BY 
                    CASE 
                        WHEN COUNT(v.id_venta) > 5 AND DATEDIFF(CURRENT_DATE, MAX(DATE(v.fecha))) < 30 THEN 'VIP'
                        WHEN COUNT(v.id_venta) > 3 AND DATEDIFF(CURRENT_DATE, MAX(DATE(v.fecha))) < 60 THEN 'Regular'
                        WHEN DATEDIFF(CURRENT_DATE, MAX(DATE(v.fecha))) > 90 THEN 'Inactivo'
                        ELSE 'Ocasional'
                    END
            """

            cursor.execute(consulta_categorias, (self.fecha_inicio.get(), self.fecha_fin.get()))
            categorias_clientes = {row[0]: row[1] for row in cursor.fetchall()}

            if tipo_grafico == "Pastel":
                # Gráfico de torta para distribución de categorías
                labels = list(categorias_clientes.keys())
                sizes = list(categorias_clientes.values())

                # Colores para categorías
                colores = []
                for cat in labels:
                    if cat == "VIP":
                        colores.append('#4CAF50')
                    elif cat == "Regular":
                        colores.append('#2196F3')
                    elif cat == "Ocasional":
                        colores.append('#FFC107')
                    else:  # Inactivo
                        colores.append('#F44336')

                wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                                  startangle=90, colors=colores,
                                                  wedgeprops={'edgecolor': 'white', 'linewidth': 1})

                ax.axis('equal')
                ax.set_title('Distribución de Clientes por Categoría')

            elif tipo_grafico == "Barras":
                # Gráfico de barras para conteo por categoría
                categorias_nombres = list(categorias_clientes.keys())
                categorias_valores = list(categorias_clientes.values())

                # Ordenar por frecuencia
                indices = np.argsort(categorias_valores)
                categorias_nombres = [categorias_nombres[i] for i in indices]
                categorias_valores = [categorias_valores[i] for i in indices]

                # Colores para categorías
                colores = []
                for cat in categorias_nombres:
                    if cat == "VIP":
                        colores.append('#4CAF50')
                    elif cat == "Regular":
                        colores.append('#2196F3')
                    elif cat == "Ocasional":
                        colores.append('#FFC107')
                    else:  # Inactivo
                        colores.append('#F44336')

                bars = ax.bar(categorias_nombres, categorias_valores, color=colores)

                # Agregar etiquetas de valor
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
                            f'{height}', ha='center', va='bottom', fontsize=9)

                ax.set_xlabel('Categoría')
                ax.set_ylabel('Cantidad de Clientes')
                ax.set_title('Distribución de Clientes por Categoría')

            elif tipo_grafico == "Barras Horizontales":
                # Gráfico horizontal para mejor visualización de categoria vs. cantidad
                categorias_nombres = list(categorias_clientes.keys())
                categorias_valores = list(categorias_clientes.values())

                # Ordenar por frecuencia descendente
                indices = np.argsort(categorias_valores)[::-1]
                categorias_nombres = [categorias_nombres[i] for i in indices]
                categorias_valores = [categorias_valores[i] for i in indices]

                # Colores para categorías
                colores = []
                for cat in categorias_nombres:
                    if cat == "VIP":
                        colores.append('#4CAF50')
                    elif cat == "Regular":
                        colores.append('#2196F3')
                    elif cat == "Ocasional":
                        colores.append('#FFC107')
                    else:  # Inactivo
                        colores.append('#F44336')

                bars = ax.barh(categorias_nombres, categorias_valores, color=colores)

                # Agregar etiquetas de valor
                for bar in bars:
                    width = bar.get_width()
                    ax.text(width + 0.1, bar.get_y() + bar.get_height() / 2.,
                            f'{width}', ha='left', va='center', fontsize=9)

                ax.set_ylabel('Categoría')
                ax.set_xlabel('Cantidad de Clientes')
                ax.set_title('Distribución de Clientes por Categoría')

            elif tipo_grafico == "Dispersión":
                # Gráfico de dispersión para RFM
                # Limitar a 20 clientes para mejor visualización
                top_clientes = clientes_rfm[:20] if len(clientes_rfm) > 20 else clientes_rfm

                # Extraer datos RFM
                nombres = [cliente[1] for cliente in top_clientes]
                frecuencias = [int(cliente[2]) for cliente in top_clientes]
                recencias = [int(cliente[3]) for cliente in top_clientes]
                valores = [float(cliente[4]) for cliente in top_clientes]
                categorias_cliente = [cliente[5] for cliente in top_clientes]

                # Colores según categoría
                colores = []
                for cat in categorias_cliente:
                    if cat == "VIP":
                        colores.append('#4CAF50')
                    elif cat == "Regular":
                        colores.append('#2196F3')
                    elif cat == "Ocasional":
                        colores.append('#FFC107')
                    else:  # Inactivo
                        colores.append('#F44336')

                # Tamaño del punto basado en valor monetario
                tamaños = [max(50, min(500, v / 10)) for v in valores]

                # Crear gráfico de dispersión
                scatter = ax.scatter(frecuencias, recencias, c=colores, s=tamaños, alpha=0.7, edgecolors='black')

                # Agregar etiquetas a los puntos
                for i, txt in enumerate(nombres):
                    ax.annotate(txt[:10], (frecuencias[i], recencias[i]),
                                xytext=(5, 5), textcoords='offset points', fontsize=8)

                # Invertir eje Y para que menor recencia (más reciente) esté arriba
                ax.invert_yaxis()

                ax.set_xlabel('Frecuencia (Visitas)')
                ax.set_ylabel('Recencia (Días)')
                ax.set_title('Análisis RFM - Recencia vs Frecuencia')
                ax.grid(True, linestyle='--', alpha=0.7)

                # Agregar leyenda para categorías
                import matplotlib.patches as mpatches
                vip_patch = mpatches.Patch(color='#4CAF50', label='VIP')
                regular_patch = mpatches.Patch(color='#2196F3', label='Regular')
                ocasional_patch = mpatches.Patch(color='#FFC107', label='Ocasional')
                inactivo_patch = mpatches.Patch(color='#F44336', label='Inactivo')

                ax.legend(handles=[vip_patch, regular_patch, ocasional_patch, inactivo_patch],
                          loc='best')

            elif tipo_grafico == "Líneas" or tipo_grafico == "Área":
                # Obtener evolución real de categorías de clientes por mes
                consulta_evolucion = """
                    SELECT 
                        DATE_FORMAT(v.fecha, '%Y-%m') as mes,
                        CASE 
                            WHEN COUNT(DISTINCT v.id_venta) > 5 AND 
                                 DATEDIFF(LAST_DAY(DATE(v.fecha)), 
                                          CAST(CONCAT(SUBSTRING_INDEX(DATE_FORMAT(v.fecha, '%Y-%m'), '-', 1), '-', 
                                                    SUBSTRING_INDEX(DATE_FORMAT(v.fecha, '%Y-%m'), '-', -1), '-01') AS DATE)
                                         ) < 30 THEN 'VIP'
                            WHEN COUNT(DISTINCT v.id_venta) > 3 THEN 'Regular'
                            WHEN COUNT(DISTINCT v.id_venta) > 1 THEN 'Ocasional'
                            ELSE 'Inactivo'
                        END as categoria,
                        COUNT(DISTINCT c.id_cliente) as cantidad
                    FROM clientes c
                    JOIN ventas v ON c.id_cliente = v.id_cliente
                    WHERE DATE(v.fecha) BETWEEN DATE_SUB(%s, INTERVAL 6 MONTH) AND %s
                    GROUP BY 
                        DATE_FORMAT(v.fecha, '%Y-%m'),
                        CASE 
                            WHEN COUNT(DISTINCT v.id_venta) > 5 AND 
                                 DATEDIFF(LAST_DAY(DATE(v.fecha)), 
                                          CAST(CONCAT(SUBSTRING_INDEX(DATE_FORMAT(v.fecha, '%Y-%m'), '-', 1), '-', 
                                                    SUBSTRING_INDEX(DATE_FORMAT(v.fecha, '%Y-%m'), '-', -1), '-01') AS DATE)
                                         ) < 30 THEN 'VIP'
                            WHEN COUNT(DISTINCT v.id_venta) > 3 THEN 'Regular'
                            WHEN COUNT(DISTINCT v.id_venta) > 1 THEN 'Ocasional'
                            ELSE 'Inactivo'
                        END
                    ORDER BY mes, categoria
                """

                cursor.execute(consulta_evolucion, (self.fecha_inicio.get(), self.fecha_fin.get()))
                resultados = cursor.fetchall()

                # Procesar resultados
                meses_unicos = sorted(set(r[0] for r in resultados))

                # Convertir a formato legible
                meses_formato = []
                for mes in meses_unicos:
                    try:
                        fecha = datetime.strptime(mes, '%Y-%m')
                        meses_formato.append(fecha.strftime('%b %Y'))
                    except:
                        meses_formato.append(mes)

                # Estructurar datos por categoría
                datos_categoria = {
                    'VIP': [0] * len(meses_unicos),
                    'Regular': [0] * len(meses_unicos),
                    'Ocasional': [0] * len(meses_unicos),
                    'Inactivo': [0] * len(meses_unicos)
                }

                # Llenar datos reales de evolución
                for resultado in resultados:
                    mes = resultado[0]
                    categoria = resultado[1]
                    cantidad = resultado[2]

                    if categoria in datos_categoria and mes in meses_unicos:
                        mes_idx = meses_unicos.index(mes)
                        datos_categoria[categoria][mes_idx] = cantidad

                # Colores para categorías
                colors = {
                    'VIP': '#4CAF50',
                    'Regular': '#2196F3',
                    'Ocasional': '#FFC107',
                    'Inactivo': '#F44336'
                }

                # Crear gráfico con datos reales
                for categoria, valores in datos_categoria.items():
                    if tipo_grafico == "Líneas":
                        ax.plot(meses_formato, valores, 'o-', linewidth=2,
                                label=categoria, color=colors.get(categoria, '#999999'))
                    else:  # Área
                        ax.fill_between(meses_formato, valores, alpha=0.4,
                                        label=categoria, color=colors.get(categoria, '#999999'))
                        ax.plot(meses_formato, valores, 'o-', linewidth=1, color=colors.get(categoria, '#999999'))

                ax.set_title('Evolución de Clientes por Categoría')
                ax.set_ylabel('Cantidad')
                ax.legend()
                ax.grid(True, linestyle='--', alpha=0.7)
                plt.xticks(rotation=45, ha='right')

            elif tipo_grafico == "Calor":
                # Crear matriz para mapa de calor con las métricas RFM
                # Limitar a 10 clientes para mejor visualización
                top_clientes = clientes_rfm[:10]

                if not top_clientes:
                    ax.text(0.5, 0.5, 'No hay datos suficientes para este análisis',
                            ha='center', va='center', fontsize=12)
                    return

                # Extraer datos
                nombres = [cliente[1][:15] for cliente in top_clientes]
                frecuencias = [int(cliente[2]) for cliente in top_clientes]
                recencias = [int(cliente[3]) for cliente in top_clientes]
                valores = [float(cliente[4]) for cliente in top_clientes]

                # Normalizar los valores para mejor visualización
                max_frecuencia = max(frecuencias) if frecuencias else 1
                max_recencia = max(recencias) if recencias else 1
                max_valor = max(valores) if valores else 1

                norm_frecuencias = [f / max_frecuencia for f in frecuencias]
                # Invertir recencia para que 1.0 sea lo más reciente
                norm_recencias = [1 - (r / max_recencia) for r in recencias]
                norm_valores = [v / max_valor for v in valores]

                # Crear matriz para el mapa de calor
                matriz = np.array([norm_recencias, norm_frecuencias, norm_valores])

                # Crear mapa de calor
                sns.heatmap(matriz, ax=ax, cmap="YlGnBu", annot=True, fmt=".2f",
                            xticklabels=nombres,
                            yticklabels=['Recencia', 'Frecuencia', 'Valor'])

                ax.set_title('Análisis RFM por Cliente (Valores Normalizados)')
                ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

            # Cerrar conexión
            conexion.close()

        except Exception as e:
            print(f"Error en gráfico de comportamiento de clientes: {e}")
            import traceback
            traceback.print_exc()
            ax.text(0.5, 0.5, f'Error al obtener datos: {str(e)}',
                    ha='center', va='center', fontsize=10, wrap=True)

    def crear_grafico_radar_rfm(self, ax, datos_rfm):
        """Crea un gráfico de radar para el análisis RFM con datos reales"""
        try:
            import matplotlib.pyplot as plt
            from matplotlib.path import Path
            from matplotlib.spines import Spine
            from matplotlib.transforms import Affine2D

            # Limitar a 5 clientes para mejor visualización
            datos_rfm = datos_rfm[:5]

            # Número de variables
            N = 3
            theta = np.linspace(0, 2 * np.pi, N, endpoint=False)

            # Completar el círculo
            theta = np.append(theta, theta[0])

            # Configurar ejes radiales
            ax.set_theta_zero_location('N')
            ax.set_theta_direction(-1)
            ax.set_rlabel_position(0)

            # Normalizar valores para el gráfico radar
            max_frecuencia = max(d[2] for d in datos_rfm)
            max_recencia = max(d[3] for d in datos_rfm)
            max_valor = max(d[4] for d in datos_rfm)

            # Etiquetas
            labels = ['Frecuencia', 'Recencia', 'Valor', 'Frecuencia']
            ax.set_xticks(theta)
            ax.set_xticklabels(labels)

            # Dibujar para cada cliente
            for dato in datos_rfm:
                nombre = dato[1][:15]
                frecuencia_norm = dato[2] / max_frecuencia
                # Invertir recencia (menor es mejor)
                recencia_norm = 1 - (dato[3] / max_recencia) if max_recencia > 0 else 0
                valor_norm = dato[4] / max_valor if max_valor > 0 else 0

                values = [frecuencia_norm, recencia_norm, valor_norm, frecuencia_norm]
                ax.plot(theta, values, 'o-', linewidth=2, label=nombre)
                ax.fill(theta, values, alpha=0.25)

            ax.set_ylim(0, 1)
            ax.set_title('Análisis RFM por Cliente')
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

        except Exception as e:
            print(f"Error en gráfico radar: {e}")
            ax.text(0.5, 0.5, 'Error al generar gráfico de radar',
                    ha='center', va='center', fontsize=10)

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

    # Para la pestaña Dashboard, asegurar que se usen datos reales
    def generar_graficos_dashboard(self, ventas_diarias, top_servicios, pedidos_por_estado, top_clientes):
        """Genera los gráficos para el dashboard general con datos reales"""
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
                     fontsize=10, verticalalignment='top',
                     bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
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

    def graficar_clientes(self, ax, tipo_grafico):
        """Genera gráfico de clientes frecuentes"""
        clientes = self.datos_grafico['clientes']

        # Limitar a los 10 clientes más frecuentes
        top_clientes = clientes[:10] if len(clientes) > 10 else clientes

        nombres = [cliente[1] for cliente in top_clientes]
        visitas = [int(cliente[2]) for cliente in top_clientes]
        gastos = [float(cliente[3]) for cliente in top_clientes]

        # Acortar nombres largos
        nombres_cortos = [nombre[:20] + "..." if len(nombre) > 20 else nombre for nombre in nombres]

        if tipo_grafico == "Barras":
            # Barras para visitas y gastos
            ax2 = ax.twinx()
            bars1 = ax.bar([i - 0.2 for i in range(len(nombres_cortos))], visitas, width=0.4,
                           color='#6495ED', label='Visitas')
            bars2 = ax2.bar([i + 0.2 for i in range(len(nombres_cortos))], gastos, width=0.4,
                            color='#FF7F50', label='Gasto ($)')

            ax.set_xticks(range(len(nombres_cortos)))
            ax.set_xticklabels(nombres_cortos, rotation=45, ha='right')

            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

            ax.set_ylabel('Visitas')
            ax2.set_ylabel('Gasto ($)')
            ax.set_title('Clientes Frecuentes por Visitas y Gasto')

        elif tipo_grafico == "Pastel":
            # Gráfico de pastel para mostrar proporción de visitas
            plt.rcParams.update({'font.size': 9})
            wedges, texts, autotexts = ax.pie(visitas, labels=nombres_cortos, autopct='%1.1f%%',
                                              startangle=90, colors=plt.cm.Pastel1.colors,
                                              wedgeprops={'edgecolor': 'white', 'linewidth': 1})

            plt.setp(texts, size=8)
            plt.setp(autotexts, size=8, weight='bold')

            ax.axis('equal')
            ax.set_title('Distribución de Visitas por Cliente')

        elif tipo_grafico == "Barras Horizontales":
            # Invertir orden para mejor visualización
            nombres_cortos = nombres_cortos[::-1]
            visitas = visitas[::-1]
            gastos = gastos[::-1]

            ax.barh(nombres_cortos, visitas, color='#6495ED', alpha=0.7, label='Visitas')
            ax2 = ax.twiny()
            ax2.barh(nombres_cortos, gastos, color='#FF7F50', alpha=0.5, label='Gasto ($)')

            for i, v in enumerate(visitas):
                ax.text(v + 0.5, i, f'{v}', va='center', fontsize=8)

            ax.legend(loc='lower right')
            ax2.legend(loc='upper right')

            ax.set_title('Clientes por Visitas y Gasto Total')
            ax.set_xlabel('Visitas')
            ax2.set_xlabel('Gasto ($)')

        elif tipo_grafico == "Dispersión":
            # Gráfico de dispersión para relacionar visitas con gasto
            ax.scatter(visitas, gastos, c=range(len(visitas)), cmap='plasma',
                       s=100, alpha=0.7, edgecolors='black')

            for i, txt in enumerate(nombres_cortos):
                ax.annotate(txt, (visitas[i], gastos[i]),
                            xytext=(5, 5), textcoords='offset points', fontsize=8)

            ax.set_xlabel('Número de Visitas')
            ax.set_ylabel('Gasto Total ($)')
            ax.set_title('Relación entre Visitas y Gasto por Cliente')
            ax.grid(True, linestyle='--', alpha=0.7)

        elif tipo_grafico == "Líneas":
            # Para clientes, usamos un enfoque diferente mostrando su evolución de gasto
            try:
                for i, cliente in enumerate(top_clientes):
                    if i < 5:  # Limitar a 5 clientes para evitar sobrecarga visual
                        ax.plot([1, 2, 3], [gastos[i] * 0.7, gastos[i], gastos[i] * 1.1],
                                marker='o', label=nombres_cortos[i])

                ax.set_xticks([1, 2, 3])
                ax.set_xticklabels(['Periodo Previo', 'Actual', 'Proyección'])
                ax.set_ylabel('Gasto ($)')
                ax.set_title('Evolución de Gasto por Cliente')
                ax.legend(loc='best')
                ax.grid(True, linestyle='--', alpha=0.7)
            except:
                ax.text(0.5, 0.5, 'No hay suficientes datos para este gráfico',
                        ha='center', va='center', fontsize=12)

        elif tipo_grafico == "Área" or tipo_grafico == "Calor":
            # Para estos tipos, mostramos un análisis RFM (Recencia, Frecuencia, Monetización)
            try:
                # Preparar datos para RFM
                datos_rfm = []
                for cliente in top_clientes:
                    # Normalizar los valores entre 0 y 1 para mejor visualización
                    recencia = min(int(cliente[3]) / 100, 1)  # Días desde última compra
                    frecuencia = min(int(cliente[2]) / 10, 1)  # Número de visitas
                    monetizacion = min(float(cliente[3]) / 1000, 1)  # Gasto total

                    datos_rfm.append([cliente[1], recencia, frecuencia, monetizacion])

                if tipo_grafico == "Área":
                    # Gráfico de radar para análisis RFM
                    from matplotlib.path import Path
                    from matplotlib.spines import Spine
                    from matplotlib.transforms import Affine2D

                    # Número de variables
                    N = 3
                    theta = np.linspace(0, 2 * np.pi, N, endpoint=False)

                    # Completar el círculo
                    theta = np.append(theta, theta[0])

                    # Configurar ejes radiales
                    ax.set_theta_zero_location('N')
                    ax.set_theta_direction(-1)
                    ax.set_rlabel_position(0)

                    # Etiquetas
                    labels = ['Recencia', 'Frecuencia', 'Monetización', 'Recencia']
                    ax.set_xticks(theta)
                    ax.set_xticklabels(labels)

                    for i, cliente in enumerate(datos_rfm[:5]):  # Limitar a 5 clientes
                        values = [cliente[1], cliente[2], cliente[3], cliente[1]]
                        ax.plot(theta, values, 'o-', linewidth=2, label=cliente[0][:15])
                        ax.fill(theta, values, alpha=0.25)

                    ax.set_ylim(0, 1)
                    ax.set_title('Análisis RFM por Cliente')
                    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

                elif tipo_grafico == "Calor":
                    # Crear matriz para mapa de calor
                    matrix = np.zeros((len(datos_rfm[:10]), 3))
                    for i, cliente in enumerate(datos_rfm[:10]):
                        matrix[i, 0] = cliente[1]  # Recencia
                        matrix[i, 1] = cliente[2]  # Frecuencia
                        matrix[i, 2] = cliente[3]  # Monetización

                    sns.heatmap(matrix, ax=ax, cmap="YlGnBu",
                                xticklabels=['Recencia', 'Frecuencia', 'Monetización'],
                                yticklabels=[d[0][:15] for d in datos_rfm[:10]],
                                annot=True, fmt=".2f")

                    ax.set_title('Análisis RFM por Cliente (Valores Normalizados)')
            except Exception as e:
                print(f"Error en visualización RFM: {e}")
                ax.text(0.5, 0.5, 'No se pudo generar este tipo de gráfico con los datos disponibles',
                        ha='center', va='center', fontsize=10)

    def graficar_ingresos_mensuales(self, ax, tipo_grafico):
        """Genera gráfico de ingresos mensuales"""
        datos_por_mes = self.datos_grafico['datos_por_mes']

        # Preparar los datos
        meses = []
        ingresos_ventas = []
        ingresos_servicios = []

        for clave in sorted(datos_por_mes.keys()):
            datos = datos_por_mes[clave]

            # Obtener nombre del mes
            try:
                nombre_mes = calendar.month_name[datos['mes']]
            except:
                nombre_mes = f"Mes {datos['mes']}"

            etiqueta_mes = f"{nombre_mes[:3]} {datos['año']}"

            meses.append(etiqueta_mes)
            ingresos_ventas.append(float(datos['total_ventas']))
            ingresos_servicios.append(float(datos['total_servicios']))

        # Crear gráfico según tipo seleccionado
        if tipo_grafico == "Barras":
            # Barras apiladas
            width = 0.8

            # Crear barras apiladas
            p1 = ax.bar(meses, ingresos_ventas, width, color='#4CAF50', label='Ventas')
            p2 = ax.bar(meses, ingresos_servicios, width, bottom=ingresos_ventas,
                        color='#2196F3', label='Servicios')

            # Agregar etiquetas con totales
            for i in range(len(meses)):
                total = ingresos_ventas[i] + ingresos_servicios[i]
                ax.text(i, total + 10, f"${total:.0f}", ha='center', fontsize=8)

            ax.set_title('Ingresos Mensuales')
            ax.set_ylabel('Ingresos ($)')
            ax.set_xticks(range(len(meses)))
            ax.set_xticklabels(meses, rotation=45, ha='right')
            ax.legend()

        elif tipo_grafico == "Líneas":
            # Gráfico de líneas para tendencia
            totales = [v + s for v, s in zip(ingresos_ventas, ingresos_servicios)]

            ax.plot(meses, ingresos_ventas, 'o-', color='#4CAF50', linewidth=2, label='Ventas')
            ax.plot(meses, ingresos_servicios, 's-', color='#2196F3', linewidth=2, label='Servicios')
            ax.plot(meses, totales, '^-', color='#F44336', linewidth=3, label='Total')

            ax.set_title('Tendencia de Ingresos Mensuales')
            ax.set_ylabel('Ingresos ($)')
            plt.xticks(rotation=45, ha='right')
            ax.legend()
            ax.grid(True, linestyle='--', alpha=0.7)

            # Agregar línea de tendencia para el total
            if len(totales) > 1:
                z = np.polyfit(range(len(totales)), totales, 1)
                p = np.poly1d(z)
                ax.plot(meses, p(range(len(totales))), "k--", alpha=0.5, linewidth=1)

        elif tipo_grafico == "Área":
            # Gráfico de área apilada
            ax.fill_between(meses, ingresos_ventas, color='#4CAF50', alpha=0.7, label='Ventas')
            ax.fill_between(meses, [v + s for v, s in zip(ingresos_ventas, ingresos_servicios)],
                            ingresos_ventas, color='#2196F3', alpha=0.7, label='Servicios')

            ax.set_title('Ingresos Mensuales por Categoría')
            ax.set_ylabel('Ingresos ($)')
            plt.xticks(rotation=45, ha='right')
            ax.legend()
            ax.grid(True, linestyle='--', alpha=0.7)

        elif tipo_grafico == "Pastel":
            # Para gráfico de pastel, mostrar el total por mes
            totales = [ingresos_ventas[i] + ingresos_servicios[i] for i in range(len(meses))]

            plt.rcParams.update({'font.size': 9})
            wedges, texts, autotexts = ax.pie(totales, labels=meses, autopct='%1.1f%%',
                                              startangle=90, colors=plt.cm.tab20.colors,
                                              wedgeprops={'edgecolor': 'white', 'linewidth': 1})

            plt.setp(texts, size=8)
            plt.setp(autotexts, size=8, weight='bold')

            ax.axis('equal')
            ax.set_title('Distribución de Ingresos por Mes')

        elif tipo_grafico == "Barras Horizontales":
            # Preparar datos para barras horizontales (invertimos el orden)
            meses_inv = meses[::-1]
            ventas_inv = ingresos_ventas[::-1]
            servicios_inv = ingresos_servicios[::-1]

            # Crear barras apiladas horizontales
            ax.barh(meses_inv, ventas_inv, color='#4CAF50', label='Ventas')
            ax.barh(meses_inv, servicios_inv, left=ventas_inv, color='#2196F3', label='Servicios')

            # Agregar etiquetas con totales
            for i in range(len(meses_inv)):
                total = ventas_inv[i] + servicios_inv[i]
                ax.text(total + 10, i, f"${total:.0f}", va='center', fontsize=8)

            ax.set_title('Ingresos Mensuales por Categoría')
            ax.set_xlabel('Ingresos ($)')
            ax.legend()

        elif tipo_grafico == "Calor":
            # Crear matriz para mapa de calor
            data = np.array([ingresos_ventas, ingresos_servicios])

            # Normalizar para mejor visualización
            data_norm = data / data.max()

            sns.heatmap(data_norm, ax=ax, cmap="YlGnBu", annot=True, fmt=".2f",
                        xticklabels=meses,
                        yticklabels=['Ventas', 'Servicios'])

            ax.set_title('Distribución de Ingresos (Normalizado)')
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

    def graficar_pedidos_estado(self, ax, tipo_grafico):
        """Genera gráfico de pedidos por estado"""
        pedidos_por_estado = self.datos_grafico['pedidos_por_estado']

        # Preparar datos
        estados = [p[0] for p in pedidos_por_estado]
        cantidades = [int(p[1]) for p in pedidos_por_estado]
        tiempos = [float(p[2]) if p[2] is not None else 0 for p in pedidos_por_estado]

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

        if tipo_grafico == "Barras":
            # Barras para cantidad
            bars = ax.bar(estados, cantidades, color=colores)

            # Añadir etiquetas sobre las barras
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
                        f'{height:.0f}', ha='center', va='bottom', fontsize=9)

            ax.set_xlabel('Estado')
            ax.set_ylabel('Cantidad')
            ax.set_title('Cantidad de Pedidos por Estado')

        elif tipo_grafico == "Pastel":
            # Gráfico de torta para distribución
            wedges, texts, autotexts = ax.pie(cantidades, labels=estados, autopct='%1.1f%%',
                                              startangle=90, colors=colores,
                                              wedgeprops={'edgecolor': 'white', 'linewidth': 1})

            ax.axis('equal')
            ax.set_title('Distribución de Pedidos por Estado')

        elif tipo_grafico == "Barras Horizontales":
            # Ordenar datos para mejor visualización
            indices = np.argsort(cantidades)
            estados_ord = [estados[i] for i in indices]
            cantidades_ord = [cantidades[i] for i in indices]
            colores_ord = [colores[i] for i in indices]

            bars = ax.barh(estados_ord, cantidades_ord, color=colores_ord)

            # Añadir etiquetas
            for bar in bars:
                width = bar.get_width()
                ax.text(width + 0.1, bar.get_y() + bar.get_height() / 2.,
                        f'{width:.0f}', ha='left', va='center', fontsize=9)

            ax.set_xlabel('Cantidad')
            ax.set_title('Cantidad de Pedidos por Estado')


        elif tipo_grafico == "Líneas" or tipo_grafico == "Área":

            # Obtener evolución temporal real de la base de datos

            try:

                conexion = conectar_bd()

                cursor = conexion.cursor()

                # Consultar datos de evolución semanal

                consulta_evolucion = """

                    SELECT 

                        YEARWEEK(fecha_pedido) as semana,

                        estado,

                        COUNT(*) as cantidad

                    FROM pedidos

                    WHERE DATE(fecha_pedido) BETWEEN %s AND %s

                    GROUP BY YEARWEEK(fecha_pedido), estado

                    ORDER BY semana

                """

                cursor.execute(consulta_evolucion, (self.fecha_inicio.get(), self.fecha_fin.get()))

                resultados = cursor.fetchall()

                # Procesar resultados

                semanas_unicas = sorted(set(r[0] for r in resultados))

                # Convertir números de semana a etiquetas legibles

                fechas = []

                for semana in semanas_unicas:
                    # Extraer año y número de semana

                    year = int(str(semana)[:4])

                    week = int(str(semana)[4:])

                    # Crear etiqueta

                    fechas.append(f"Sem {week}/{year}")

                datos_evolucion = {estado: [0] * len(semanas_unicas) for estado in estados}

                # Llenar datos reales

                for resultado in resultados:

                    semana_idx = semanas_unicas.index(resultado[0])

                    estado = resultado[1]

                    cantidad = resultado[2]

                    if estado in datos_evolucion:
                        datos_evolucion[estado][semana_idx] = cantidad

                # Crear gráfico con datos reales

                for estado in estados:

                    if estado in datos_evolucion:

                        if tipo_grafico == "Líneas":

                            ax.plot(fechas, datos_evolucion[estado], 'o-', linewidth=2, label=estado)

                        else:  # Área

                            ax.fill_between(fechas, datos_evolucion[estado], alpha=0.4, label=estado)

                            ax.plot(fechas, datos_evolucion[estado], 'o-', linewidth=1)

                ax.set_title('Evolución de Pedidos por Estado')

                ax.set_ylabel('Cantidad')

                ax.legend()

                ax.grid(True, linestyle='--', alpha=0.7)

                plt.xticks(rotation=45, ha='right')

                conexion.close()


            except Exception as e:

                print(f"Error en gráfico de evolución: {e}")

                ax.text(0.5, 0.5, 'Error al obtener datos de evolución',

                        ha='center', va='center', fontsize=12)

        elif tipo_grafico == "Dispersión":
            # Gráfico de dispersión para relacionar cantidad con tiempo promedio

            # Filtrar estados sin tiempo promedio
            estados_filtrados = []
            cantidades_filtradas = []
            tiempos_filtrados = []
            colores_filtrados = []

            for i, (estado, cantidad, tiempo) in enumerate(zip(estados, cantidades, tiempos)):
                if tiempo > 0:
                    estados_filtrados.append(estado)
                    cantidades_filtradas.append(cantidad)
                    tiempos_filtrados.append(tiempo)
                    colores_filtrados.append(colores[i])

            if not estados_filtrados:
                ax.text(0.5, 0.5, 'No hay datos de tiempo disponibles para este gráfico',
                        ha='center', va='center', fontsize=12)
                return

            # Convertir horas a días para mejor visualización
            tiempos_dias = [t / 24 for t in tiempos_filtrados]

            ax.scatter(cantidades_filtradas, tiempos_dias, c=colores_filtrados,
                       s=100, alpha=0.7, edgecolors='black')

            for i, txt in enumerate(estados_filtrados):
                ax.annotate(txt, (cantidades_filtradas[i], tiempos_dias[i]),
                            xytext=(5, 5), textcoords='offset points', fontsize=9)

            ax.set_xlabel('Cantidad de Pedidos')
            ax.set_ylabel('Tiempo Promedio (días)')
            ax.set_title('Relación entre Cantidad y Tiempo Promedio por Estado')
            ax.grid(True, linestyle='--', alpha=0.7)


        elif tipo_grafico == "Calor":

            # Obtener datos reales de transición entre estados

            try:

                conexion = conectar_bd()

                cursor = conexion.cursor()

                # Verificar si existe la tabla de historial

                cursor.execute("""

                    SELECT COUNT(*) 

                    FROM information_schema.tables 

                    WHERE table_schema = DATABASE() 

                    AND table_name = 'historial_estados_pedido'

                """)

                tabla_existe = cursor.fetchone()[0] > 0

                if tabla_existe:

                    # Consultar historial de cambios de estado

                    consulta_transicion = """

                        SELECT 

                            estado_anterior,

                            estado_nuevo,

                            COUNT(*) as cantidad

                        FROM historial_estados_pedido

                        WHERE id_pedido IN (

                            SELECT id_pedido FROM pedidos 

                            WHERE DATE(fecha_pedido) BETWEEN %s AND %s

                        )

                        GROUP BY estado_anterior, estado_nuevo

                    """

                    cursor.execute(consulta_transicion, (self.fecha_inicio.get(), self.fecha_fin.get()))

                    transiciones = cursor.fetchall()

                    # Crear matriz de transición

                    matriz_transicion = np.zeros((len(estados), len(estados)))

                    # Llenar con datos reales

                    for transicion in transiciones:

                        if transicion[0] in estados and transicion[1] in estados:
                            i = estados.index(transicion[0])

                            j = estados.index(transicion[1])

                            matriz_transicion[i, j] = transicion[2]

                    # Crear mapa de calor

                    sns.heatmap(matriz_transicion, ax=ax, cmap="YlGnBu", annot=True, fmt=".0f",

                                xticklabels=estados,

                                yticklabels=estados)

                    ax.set_title('Matriz de Transición entre Estados')

                else:

                    # Si no existe la tabla, usar distribución actual como alternativa

                    consulta_distribución = """

                        SELECT estado, COUNT(*) as cantidad

                        FROM pedidos

                        WHERE DATE(fecha_pedido) BETWEEN %s AND %s

                        GROUP BY estado

                    """

                    cursor.execute(consulta_distribución, (self.fecha_inicio.get(), self.fecha_fin.get()))

                    distribución = {estado: 0 for estado in estados}

                    for resultado in cursor.fetchall():

                        if resultado[0] in distribución:
                            distribución[resultado[0]] = resultado[1]

                    # Crear matriz para el mapa de calor

                    matriz = np.zeros((len(estados), 1))

                    for i, estado in enumerate(estados):
                        matriz[i, 0] = distribución[estado]

                    sns.heatmap(matriz, ax=ax, cmap="YlGnBu", annot=True, fmt=".0f",

                                yticklabels=estados,

                                xticklabels=['Cantidad'])

                    ax.set_title('Distribución de Pedidos por Estado')

                conexion.close()


            except Exception as e:

                print(f"Error en matriz de transición: {e}")

                ax.text(0.5, 0.5, 'Error al obtener datos de transición de estados',

                        ha='center', va='center', fontsize=12)

    def graficar_rentabilidad(self, ax, tipo_grafico):
        """Genera gráfico de rentabilidad de servicios"""
        servicios = self.datos_grafico['servicios']

        # Limitar a los 10 servicios más rentables
        top_servicios = servicios[:10] if len(servicios) > 10 else servicios

        nombres = [s[1] for s in top_servicios]
        margenes = [float(s[5]) for s in top_servicios]
        rentabilidades = [float(s[6]) for s in top_servicios]
        ingresos = [float(s[3]) for s in top_servicios]
        costos = [float(s[4]) for s in top_servicios]

        # Acortar nombres largos
        nombres_cortos = [nombre[:15] + "..." if len(nombre) > 15 else nombre for nombre in nombres]

        if tipo_grafico == "Barras":
            # Barras para margen y rentabilidad
            x = np.arange(len(nombres_cortos))
            width = 0.4

            ax2 = ax.twinx()
            bars1 = ax.bar(x - width / 2, margenes, width, color='#4CAF50', label='Margen ($)')
            bars2 = ax2.bar(x + width / 2, rentabilidades, width, color='#FFC107', label='Rentabilidad (%)')

            ax.set_xticks(x)
            ax.set_xticklabels(nombres_cortos, rotation=45, ha='right')

            # Agregar etiquetas a las barras
            for bar in bars1:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2., height + 1,
                        f'${height:.0f}', ha='center', va='bottom', fontsize=7)

            for bar in bars2:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width() / 2., height + 1,
                         f'{height:.1f}%', ha='center', va='bottom', fontsize=7)

            # Leyenda combinada
            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

            ax.set_ylabel('Margen ($)')
            ax2.set_ylabel('Rentabilidad (%)')
            ax.set_title('Rentabilidad por Servicio')

        elif tipo_grafico == "Pastel":
            # Gráfico de torta para rentabilidad
            # Usar colores basados en rentabilidad
            colores = []
            for r in rentabilidades:
                if r >= 40:
                    colores.append('#4CAF50')  # Verde para alta rentabilidad
                elif r >= 20:
                    colores.append('#FFC107')  # Amarillo para rentabilidad media
                else:
                    colores.append('#F44336')  # Rojo para baja rentabilidad

            wedges, texts, autotexts = ax.pie(margenes, labels=nombres_cortos, autopct='%1.1f%%',
                                              startangle=90, colors=colores,
                                              wedgeprops={'edgecolor': 'white', 'linewidth': 1})

            plt.setp(texts, size=8)
            plt.setp(autotexts, size=8, weight='bold')

            ax.axis('equal')
            ax.set_title('Distribución de Margen por Servicio')

        elif tipo_grafico == "Barras Horizontales":
            # Ordenar para mejor visualización
            indices = np.argsort(rentabilidades)
            nombres_ord = [nombres_cortos[i] for i in indices]
            rentabilidades_ord = [rentabilidades[i] for i in indices]

            # Colores basados en rentabilidad
            colores = []
            for r in rentabilidades_ord:
                if r >= 40:
                    colores.append('#4CAF50')  # Verde para alta rentabilidad
                elif r >= 20:
                    colores.append('#FFC107')  # Amarillo para rentabilidad media
                else:
                    colores.append('#F44336')  # Rojo para baja rentabilidad

            bars = ax.barh(nombres_ord, rentabilidades_ord, color=colores)

            # Línea de referencia para rentabilidad objetivo (30%)
            ax.axvline(x=30, color='black', linestyle='--', alpha=0.7)
            ax.text(30, len(nombres_ord) - 1, 'Objetivo (30%)', rotation=90,
                    va='bottom', ha='right', fontsize=8)

            # Añadir etiquetas
            for bar in bars:
                width = bar.get_width()
                ax.text(width + 0.5, bar.get_y() + bar.get_height() / 2.,
                        f'{width:.1f}%', ha='left', va='center', fontsize=8)

            ax.set_xlabel('Rentabilidad (%)')
            ax.set_title('Rentabilidad por Servicio')

        elif tipo_grafico == "Líneas" or tipo_grafico == "Área":
            # Para estos tipos, mostrar comparación de ingresos vs costos y margen
            x = np.arange(len(nombres_cortos))

            if tipo_grafico == "Líneas":
                ax.plot(nombres_cortos, ingresos, 'o-', color='#4CAF50', linewidth=2, label='Ingresos')
                ax.plot(nombres_cortos, costos, 's-', color='#F44336', linewidth=2, label='Costos')
                ax.plot(nombres_cortos, margenes, '^-', color='#2196F3', linewidth=2, label='Margen')
            else:  # Área
                ax.fill_between(x, ingresos, costos, color='#4CAF50', alpha=0.5, label='Margen')
                ax.plot(x, ingresos, 'o-', color='green', label='Ingresos')
                ax.plot(x, costos, 's-', color='red', label='Costos')

                ax.set_xticks(x)
                ax.set_xticklabels(nombres_cortos, rotation=45, ha='right')

            ax.set_title('Análisis de Ingresos, Costos y Margen por Servicio')
            ax.set_ylabel('Monto ($)')
            ax.legend()
            ax.grid(True, linestyle='--', alpha=0.7)


        elif tipo_grafico == "Dispersión":

            # Gráfico de dispersión para relacionar ingresos con rentabilidad

            ax.scatter(ingresos, rentabilidades, c=margenes, cmap='viridis',

                       s=100, alpha=0.7, edgecolors='black')

            for i, txt in enumerate(nombres_cortos):
                ax.annotate(txt, (ingresos[i], rentabilidades[i]),

                            xytext=(5, 5), textcoords='offset points', fontsize=8)

            ax.set_xlabel('Ingresos ($)')

            ax.set_ylabel('Rentabilidad (%)')

            ax.set_title('Relación entre Ingresos y Rentabilidad por Servicio')

            ax.grid(True, linestyle='--', alpha=0.7)

            # Agregar líneas de referencia

            ax.axhline(y=30, color='black', linestyle='--', alpha=0.5)

            ax.text(min(ingresos), 30, 'Objetivo 30%', va='bottom', ha='left', fontsize=8)


        elif tipo_grafico == "Calor":

            # Crear matriz para mapa de calor con ingresos, costos, margen y rentabilidad

            data = []

            for i, nombre in enumerate(nombres_cortos):
                fila = [nombre, ingresos[i], costos[i], margenes[i], rentabilidades[i]]

                data.append(fila)

            # Convertir a DataFrame

            import pandas as pd

            df = pd.DataFrame(data, columns=['Servicio', 'Ingresos', 'Costos', 'Margen', 'Rentabilidad'])

            # Normalizar los valores para mejor visualización

            matriz = df.iloc[:, 1:].apply(lambda x: (x - x.min()) / (x.max() - x.min()), axis=0)

            sns.heatmap(matriz.T, ax=ax, annot=True, fmt=".2f", cmap="YlGnBu",

                        xticklabels=nombres_cortos,

                        yticklabels=['Ingresos', 'Costos', 'Margen', 'Rentabilidad'])

            ax.set_title('Análisis de Rentabilidad (Valores Normalizados)')

            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

        def graficar_comportamiento_clientes(self, ax, tipo_grafico):

            """Genera gráfico de comportamiento de clientes"""

            clientes = self.datos_grafico['clientes']

            categorias = self.datos_grafico['categorias']

            if tipo_grafico == "Pastel":

                # Gráfico de torta para distribución de categorías

                labels = list(categorias.keys())

                sizes = list(categorias.values())

                # Colores para categorías

                colores = []

                for cat in labels:

                    if cat == "VIP":

                        colores.append('#4CAF50')

                    elif cat == "Regular":

                        colores.append('#2196F3')

                    elif cat == "Ocasional":

                        colores.append('#FFC107')

                    else:  # Inactivo

                        colores.append('#F44336')

                wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',

                                                  startangle=90, colors=colores,

                                                  wedgeprops={'edgecolor': 'white', 'linewidth': 1})

                ax.axis('equal')

                ax.set_title('Distribución de Clientes por Categoría')


            elif tipo_grafico == "Barras":

                # Gráfico de barras para conteo por categoría

                categorias_nombres = list(categorias.keys())

                categorias_valores = list(categorias.values())

                # Ordenar por frecuencia

                indices = np.argsort(categorias_valores)

                categorias_nombres = [categorias_nombres[i] for i in indices]

                categorias_valores = [categorias_valores[i] for i in indices]

                # Colores para categorías

                colores = []

                for cat in categorias_nombres:

                    if cat == "VIP":

                        colores.append('#4CAF50')

                    elif cat == "Regular":

                        colores.append('#2196F3')

                    elif cat == "Ocasional":

                        colores.append('#FFC107')

                    else:  # Inactivo

                        colores.append('#F44336')

                bars = ax.bar(categorias_nombres, categorias_valores, color=colores)

                # Agregar etiquetas de valor

                for bar in bars:
                    height = bar.get_height()

                    ax.text(bar.get_x() + bar.get_width() / 2., height + 0.1,

                            f'{height}', ha='center', va='bottom', fontsize=9)

                ax.set_xlabel('Categoría')

                ax.set_ylabel('Cantidad de Clientes')

                ax.set_title('Distribución de Clientes por Categoría')


            elif tipo_grafico == "Barras Horizontales":

                # Gráfico horizontal para mejor visualización de categoria vs. cantidad

                categorias_nombres = list(categorias.keys())

                categorias_valores = list(categorias.values())

                # Ordenar por frecuencia descendente

                indices = np.argsort(categorias_valores)[::-1]

                categorias_nombres = [categorias_nombres[i] for i in indices]

                categorias_valores = [categorias_valores[i] for i in indices]

                # Colores para categorías

                colores = []

                for cat in categorias_nombres:

                    if cat == "VIP":

                        colores.append('#4CAF50')

                    elif cat == "Regular":

                        colores.append('#2196F3')

                    elif cat == "Ocasional":

                        colores.append('#FFC107')

                    else:  # Inactivo

                        colores.append('#F44336')

                bars = ax.barh(categorias_nombres, categorias_valores, color=colores)

                # Agregar etiquetas de valor

                for bar in bars:
                    width = bar.get_width()

                    ax.text(width + 0.1, bar.get_y() + bar.get_height() / 2.,

                            f'{width}', ha='left', va='center', fontsize=9)

                ax.set_ylabel('Categoría')

                ax.set_xlabel('Cantidad de Clientes')

                ax.set_title('Distribución de Clientes por Categoría')


            elif tipo_grafico == "Dispersión":

                # Gráfico de dispersión para RFM

                # Limitar a 20 clientes para mejor visualización

                top_clientes = clientes[:20]

                # Extraer datos RFM

                nombres = [cliente[1] for cliente in top_clientes]

                frecuencias = [int(cliente[2]) for cliente in top_clientes]

                recencias = [int(cliente[3]) for cliente in top_clientes]

                valores = [float(cliente[4]) for cliente in top_clientes]

                categorias_cliente = [cliente[5] for cliente in top_clientes]

                # Colores según categoría

                colores = []

                for cat in categorias_cliente:

                    if cat == "VIP":

                        colores.append('#4CAF50')

                    elif cat == "Regular":

                        colores.append('#2196F3')

                    elif cat == "Ocasional":

                        colores.append('#FFC107')

                    else:  # Inactivo

                        colores.append('#F44336')

                # Tamaño del punto basado en valor monetario

                tamaños = [max(50, min(500, v / 10)) for v in valores]

                # Crear gráfico de dispersión

                scatter = ax.scatter(frecuencias, recencias, c=colores, s=tamaños, alpha=0.7, edgecolors='black')

                # Agregar etiquetas a los puntos

                for i, txt in enumerate(nombres):
                    ax.annotate(txt[:10], (frecuencias[i], recencias[i]),

                                xytext=(5, 5), textcoords='offset points', fontsize=8)

                # Invertir eje Y para que menor recencia (más reciente) esté arriba

                ax.invert_yaxis()

                ax.set_xlabel('Frecuencia (Visitas)')

                ax.set_ylabel('Recencia (Días)')

                ax.set_title('Análisis RFM - Recencia vs Frecuencia')

                ax.grid(True, linestyle='--', alpha=0.7)

                # Agregar leyenda para categorías

                import matplotlib.patches as mpatches

                vip_patch = mpatches.Patch(color='#4CAF50', label='VIP')

                regular_patch = mpatches.Patch(color='#2196F3', label='Regular')

                ocasional_patch = mpatches.Patch(color='#FFC107', label='Ocasional')

                inactivo_patch = mpatches.Patch(color='#F44336', label='Inactivo')

                ax.legend(handles=[vip_patch, regular_patch, ocasional_patch, inactivo_patch],

                          loc='best')


            elif tipo_grafico == "Líneas" or tipo_grafico == "Área":

                # Para estos tipos, mostrar evolución de categorías (simulada)

                # En un caso real, estos datos vendrían de la base de datos

                # Simular evolución de categorías por mes

                meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']

                data = {

                    'VIP': [categorias.get('VIP', 0) * 0.8,

                            categorias.get('VIP', 0) * 0.85,

                            categorias.get('VIP', 0) * 0.9,

                            categorias.get('VIP', 0) * 0.95,

                            categorias.get('VIP', 0),

                            categorias.get('VIP', 0) * 1.05],

                    'Regular': [categorias.get('Regular', 0) * 0.7,

                                categorias.get('Regular', 0) * 0.8,

                                categorias.get('Regular', 0) * 0.9,

                                categorias.get('Regular', 0) * 0.95,

                                categorias.get('Regular', 0),

                                categorias.get('Regular', 0) * 1.1],

                    'Ocasional': [categorias.get('Ocasional', 0) * 0.9,

                                  categorias.get('Ocasional', 0) * 0.95,

                                  categorias.get('Ocasional', 0),

                                  categorias.get('Ocasional', 0) * 1.05,

                                  categorias.get('Ocasional', 0) * 1.1,

                                  categorias.get('Ocasional', 0) * 1.15],

                    'Inactivo': [categorias.get('Inactivo', 0) * 1.1,

                                 categorias.get('Inactivo', 0) * 1.05,

                                 categorias.get('Inactivo', 0),

                                 categorias.get('Inactivo', 0) * 0.95,

                                 categorias.get('Inactivo', 0) * 0.9,

                                 categorias.get('Inactivo', 0) * 0.85]

                }

                # Colores para categorías

                colors = {

                    'VIP': '#4CAF50',

                    'Regular': '#2196F3',

                    'Ocasional': '#FFC107',

                    'Inactivo': '#F44336'

                }

                if tipo_grafico == "Líneas":

                    for categoria, valores in data.items():

                        if categoria in categorias:  # Solo mostrar categorías que existen

                            ax.plot(meses, valores, 'o-', linewidth=2,

                                    label=categoria, color=colors[categoria])

                else:  # Área

                    for categoria, valores in data.items():

                        if categoria in categorias:  # Solo mostrar categorías que existen

                            ax.fill_between(meses, valores, alpha=0.4,

                                            label=categoria, color=colors[categoria])

                            ax.plot(meses, valores, 'o-', linewidth=1, color=colors[categoria])

                ax.set_title('Evolución de Clientes por Categoría')

                ax.set_ylabel('Cantidad')

                ax.legend()

                ax.grid(True, linestyle='--', alpha=0.7)


            elif tipo_grafico == "Calor":

                # Crear matriz para mapa de calor con las métricas RFM

                # Limitar a 10 clientes para mejor visualización

                top_clientes = clientes[:10]

                # Extraer datos

                nombres = [cliente[1][:15] for cliente in top_clientes]

                frecuencias = [int(cliente[2]) for cliente in top_clientes]

                recencias = [int(cliente[3]) for cliente in top_clientes]

                valores = [float(cliente[4]) for cliente in top_clientes]

                # Normalizar los valores para mejor visualización

                max_frecuencia = max(frecuencias)

                max_recencia = max(recencias)

                max_valor = max(valores)

                norm_frecuencias = [f / max_frecuencia for f in frecuencias]

                # Invertir recencia para que 1.0 sea lo más reciente

                norm_recencias = [1 - (r / max_recencia) for r in recencias]

                norm_valores = [v / max_valor for v in valores]

                # Crear matriz para el mapa de calor

                matriz = np.array([norm_recencias, norm_frecuencias, norm_valores])

                sns.heatmap(matriz, ax=ax, cmap="YlGnBu", annot=True, fmt=".2f",

                            xticklabels=nombres,

                            yticklabels=['Recencia', 'Frecuencia', 'Valor'])

                ax.set_title('Análisis RFM por Cliente (Valores Normalizados)')

                ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

        def cambiar_estilo_grafico(self):

            """Cambia el estilo del gráfico según la selección del usuario"""

            estilo = self.estilo_grafico.get()

            if estilo == "predeterminado":

                plt.style.use('ggplot')

                sns.set_style("whitegrid")

            else:

                try:

                    sns.set_palette(estilo)

                except:

                    pass

            # Actualizar gráfico con el nuevo estilo

            self.actualizar_grafico()

        def personalizar_colores(self):

            """Permite al usuario personalizar los colores del gráfico"""

            # Esta función abrirá diálogos para seleccionar colores

            colors = []

            # Determinar cuántos colores necesitamos según el tipo de gráfico

            num_colors = 1

            if hasattr(self, 'datos_grafico'):

                tipo_datos = self.datos_grafico.get('tipo', '')

                if tipo_datos == 'ventas':

                    num_colors = 2  # Ventas y métodos de pago

                elif tipo_datos in ['productos', 'servicios']:

                    num_colors = 3  # Productos/servicios, cantidades, ingresos

                elif tipo_datos == 'clientes':

                    num_colors = len(self.datos_grafico.get('categorias', {}).keys())

                elif tipo_datos == 'pedidos_estado':

                    num_colors = len(self.datos_grafico.get('pedidos_por_estado', []))

                else:

                    num_colors = 4  # Predeterminado para otros tipos

            # Solicitar colores al usuario

            for i in range(min(num_colors, 5)):  # Limitar a máximo 5 colores para no ser tedioso

                color = colorchooser.askcolor(title=f"Seleccione color {i + 1}")[1]

                if color:

                    colors.append(color)

                else:

                    break

            # Si se seleccionaron colores, actualizar paleta y gráfico

            if colors:
                sns.set_palette(colors)

                self.actualizar_grafico()

        def guardar_grafico_como_imagen(self):

            """Guarda el gráfico actual como una imagen"""

            # Tipo de archivo

            filetypes = [

                ("PNG", "*.png"),

                ("JPEG", "*.jpg"),

                ("SVG", "*.svg"),

                ("PDF", "*.pdf")

            ]

            # Solicitar nombre de archivo

            filename = filedialog.asksaveasfilename(

                title="Guardar gráfico como",

                filetypes=filetypes,

                defaultextension=".png"

            )

            if filename:

                try:

                    # Guardar figura actual

                    self.fig.savefig(filename, dpi=300, bbox_inches='tight')

                    messagebox.showinfo("Éxito", f"Gráfico guardado como {filename}")

                except Exception as e:

                    messagebox.showerror("Error", f"No se pudo guardar la imagen: {str(e)}")

        def exportar_reporte(self):

            """Exporta el reporte actual en varios formatos"""

            # Comprobar si hay datos para exportar

            if not hasattr(self, 'ultimo_resultado_consulta') or not self.ultimo_resultado_consulta:
                messagebox.showwarning("Sin datos", "No hay datos para exportar.")

                return

            # Mostrar opciones de exportación

            ventana_exportar = tk.Toplevel(self.ventana)

            ventana_exportar.title("Exportar Reporte")

            ventana_exportar.geometry("400x300")

            ventana_exportar.config(bg="#f5f5f5")

            ventana_exportar.transient(self.ventana)

            ventana_exportar.grab_set()

            utl.centrar_ventana(ventana_exportar, 400, 300)

            tk.Label(

                ventana_exportar,

                text="Seleccione formato de exportación:",

                font=("Helvetica", 12, "bold"),

                bg="#f5f5f5",

                pady=10

            ).pack()

            # Variables para las opciones

            var_excel = tk.IntVar(value=1)

            var_csv = tk.IntVar(value=0)

            var_pdf = tk.IntVar(value=0)

            var_html = tk.IntVar(value=0)

            # Frame para checkboxes

            frame_opciones = tk.Frame(ventana_exportar, bg="#f5f5f5", pady=10)

            frame_opciones.pack(fill=tk.X, padx=20)

            # Checkboxes para formatos

            cb_excel = tk.Checkbutton(

                frame_opciones,

                text="Excel (.xlsx)",

                variable=var_excel,

                font=("Helvetica", 11),

                bg="#f5f5f5"

            )

            cb_excel.grid(row=0, column=0, sticky=tk.W, pady=5)

            cb_csv = tk.Checkbutton(

                frame_opciones,

                text="CSV (.csv)",

                variable=var_csv,

                font=("Helvetica", 11),

                bg="#f5f5f5"

            )

            cb_csv.grid(row=1, column=0, sticky=tk.W, pady=5)

            cb_pdf = tk.Checkbutton(

                frame_opciones,

                text="PDF (.pdf)",

                variable=var_pdf,

                font=("Helvetica", 11),

                bg="#f5f5f5"

            )

            cb_pdf.grid(row=2, column=0, sticky=tk.W, pady=5)

            cb_html = tk.Checkbutton(

                frame_opciones,

                text="HTML (.html)",

                variable=var_html,

                font=("Helvetica", 11),

                bg="#f5f5f5"

            )

            cb_html.grid(row=3, column=0, sticky=tk.W, pady=5)

            # Opciones adicionales

            tk.Label(

                ventana_exportar,

                text="Opciones:",

                font=("Helvetica", 12, "bold"),

                bg="#f5f5f5",

                pady=5

            ).pack(anchor=tk.W, padx=20)

            var_incluir_grafico = tk.IntVar(value=1)

            cb_grafico = tk.Checkbutton(

                ventana_exportar,

                text="Incluir gráfico en la exportación",

                variable=var_incluir_grafico,

                font=("Helvetica", 11),

                bg="#f5f5f5"

            )

            cb_grafico.pack(anchor=tk.W, padx=20, pady=5)

            # Botones de acción

            frame_botones = tk.Frame(ventana_exportar, bg="#f5f5f5", pady=10)

            frame_botones.pack(fill=tk.X, padx=20, pady=10)

            btn_exportar = tk.Button(

                frame_botones,

                text="Exportar",

                bg="#4CAF50",

                fg="white",

                font=("Helvetica", 11),

                width=10,

                command=lambda: self.realizar_exportacion(

                    var_excel.get(), var_csv.get(), var_pdf.get(), var_html.get(),

                    var_incluir_grafico.get(), ventana_exportar

                )

            )

            btn_exportar.pack(side=tk.LEFT, padx=10)

            btn_cancelar = tk.Button(

                frame_botones,

                text="Cancelar",

                bg="#F44336",

                fg="white",

                font=("Helvetica", 11),

                width=10,

                command=ventana_exportar.destroy

            )

            btn_cancelar.pack(side=tk.LEFT, padx=10)

        def realizar_exportacion(self, excel, csv, pdf, html, incluir_grafico, ventana):
            """Realiza la exportación en los formatos seleccionados"""
            # Obtener nombre de archivo base
            filename = filedialog.asksaveasfilename(
                title="Guardar reporte como",
                defaultextension=".xlsx"
            )

            if not filename:
                return

            # Quitar extensión para usar como base
            filename_base = os.path.splitext(filename)[0]

            # Convertir datos a DataFrame
            try:
                import pandas as pd
                from datetime import datetime

                # Obtener títulos de columnas
                columnas = [col['text'] for col in self.tabla_reporte['columns']]

                # Crear DataFrame con los datos
                datos = []
                for item in self.tabla_reporte.get_children():
                    valores = self.tabla_reporte.item(item, 'values')
                    datos.append(valores)

                df = pd.DataFrame(datos, columns=columnas)

                # Exportar según formatos seleccionados
                if excel:
                    try:
                        # Crear un ExcelWriter
                        excel_file = f"{filename_base}.xlsx"
                        writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')

                        # Escribir los datos en la primera hoja
                        df.to_excel(writer, sheet_name='Datos', index=False)

                        # Añadir hoja con resumen
                        resumen = pd.DataFrame({
                            'Métrica': ['Fecha de Generación', 'Tipo de Reporte', 'Periodo', 'Total de Registros'],
                            'Valor': [
                                datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                self.tipo_reporte.get(),
                                f"{self.fecha_inicio.get()} a {self.fecha_fin.get()}",
                                len(datos)
                            ]
                        })
                        resumen.to_excel(writer, sheet_name='Resumen', index=False)

                        # Si se solicitó incluir gráfico
                        if incluir_grafico:
                            # Guardar gráfico como imagen en memoria
                            img_buf = io.BytesIO()
                            self.fig.savefig(img_buf, format='png', dpi=150)
                            img_buf.seek(0)

                            # Insertar imagen en hoja de Excel
                            worksheet = writer.sheets['Resumen']
                            worksheet.insert_image('D5', 'grafico.png', {'image_data': img_buf})

                        # Guardar archivo Excel
                        writer.close()

                    except Exception as e:
                        messagebox.showerror("Error Excel", f"Error al exportar a Excel: {str(e)}")

                if csv:
                    try:
                        csv_file = f"{filename_base}.csv"
                        df.to_csv(csv_file, index=False)
                    except Exception as e:
                        messagebox.showerror("Error CSV", f"Error al exportar a CSV: {str(e)}")

                if pdf:
                    try:
                        from reportlab.lib import colors
                        from reportlab.lib.pagesizes import letter
                        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
                        from reportlab.lib.styles import getSampleStyleSheet

                        pdf_file = f"{filename_base}.pdf"
                        doc = SimpleDocTemplate(pdf_file, pagesize=letter)

                        # Lista de elementos para el PDF
                        elements = []

                        # Estilos
                        styles = getSampleStyleSheet()

                        # Título del reporte
                        title_style = styles['Heading1']
                        title = Paragraph(f"Reporte: {self.tipo_reporte.get()}", title_style)
                        elements.append(title)
                        elements.append(Spacer(1, 10))

                        # Información del reporte
                        info_style = styles['Normal']
                        fecha_gen = Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                                              info_style)
                        periodo = Paragraph(f"Periodo: {self.fecha_inicio.get()} a {self.fecha_fin.get()}", info_style)
                        elements.append(fecha_gen)
                        elements.append(periodo)
                        elements.append(Spacer(1, 20))

                        # Si se solicitó incluir gráfico
                        if incluir_grafico:
                            # Guardar gráfico como imagen temporal
                            img_temp = f"{filename_base}_temp.png"
                            self.fig.savefig(img_temp, format='png', dpi=150, bbox_inches='tight')

                            # Agregar imagen al PDF
                            img = Image(img_temp)
                            img.drawHeight = 300
                            img.drawWidth = 500
                            elements.append(img)
                            elements.append(Spacer(1, 20))

                        # Tabla de datos
                        data = [columnas]  # Encabezados
                        for row in datos:
                            # Convertir cualquier none a string vacío
                            data.append([str(cell) if cell is not None else '' for cell in row])

                        # Crear tabla
                        table = Table(data)

                        # Estilo de tabla
                        style = TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 12),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 1), (-1, -1), 9),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ])

                        # Aplicar estilo a la tabla
                        table.setStyle(style)

                        # Agregar tabla al PDF
                        elements.append(table)

                        # Generar PDF
                        doc.build(elements)

                        # Eliminar imagen temporal si existe
                        if incluir_grafico and os.path.exists(img_temp):
                            os.remove(img_temp)

                    except Exception as e:
                        messagebox.showerror("Error PDF", f"Error al exportar a PDF: {str(e)}")

                if html:
                    try:
                        html_file = f"{filename_base}.html"

                        # Crear contenido HTML con Bootstrap para estilo
                        html_string = """
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Reporte de Lavandería</title>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1">
                            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
                            <style>
                                body { padding: 20px; }
                                .report-header { margin-bottom: 30px; }
                                .table-container { margin-top: 20px; }
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <div class="report-header">
                                    <h1>Reporte: {}</h1>
                                    <p><strong>Fecha:</strong> {}</p>
                                    <p><strong>Periodo:</strong> {} a {}</p>
                                </div>
                        """.format(
                            self.tipo_reporte.get(),
                            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                            self.fecha_inicio.get(),
                            self.fecha_fin.get()
                        )

                        # Agregar gráfico si se solicitó
                        if incluir_grafico:
                            # Guardar gráfico como imagen
                            img_path = f"{filename_base}_grafico.png"
                            self.fig.savefig(img_path, format='png', dpi=150, bbox_inches='tight')

                            # Agregar imagen al HTML
                            html_string += f"""
                                <div class="graph-container text-center">
                                    <img src="{os.path.basename(img_path)}" class="img-fluid" alt="Gráfico">
                                </div>
                            """

                        # Agregar tabla de datos
                        html_string += """
                                <div class="table-container">
                                    <h2>Datos del Reporte</h2>
                                    <table class="table table-striped table-hover">
                                        <thead class="table-dark">
                                            <tr>
                        """

                        # Encabezados
                        for col in columnas:
                            html_string += f"<th>{col}</th>"

                        html_string += """
                                            </tr>
                                        </thead>
                                        <tbody>
                        """

                        # Filas de datos
                        for row in datos:
                            html_string += "<tr>"
                            for cell in row:
                                html_string += f"<td>{cell}</td>"
                            html_string += "</tr>"

                        # Cierre de tabla y documento
                        html_string += """
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </body>
                        </html>
                        """

                        # Guardar HTML
                        with open(html_file, 'w', encoding='utf-8') as f:
                            f.write(html_string)

                    except Exception as e:
                        messagebox.showerror("Error HTML", f"Error al exportar a HTML: {str(e)}")

                # Mostrar mensaje de éxito
                formatos_exportados = []
                if excel: formatos_exportados.append("Excel")
                if csv: formatos_exportados.append("CSV")
                if pdf: formatos_exportados.append("PDF")
                if html: formatos_exportados.append("HTML")

                if formatos_exportados:
                    messagebox.showinfo(
                        "Exportación exitosa",
                        f"Reporte exportado en los siguientes formatos: {', '.join(formatos_exportados)}"
                    )

                    # Preguntar si desea abrir alguno de los archivos generados
                    if messagebox.askyesno("Abrir archivo", "¿Desea abrir alguno de los archivos generados?"):
                        if excel:
                            webbrowser.open(f"{filename_base}.xlsx")
                        elif pdf:
                            webbrowser.open(f"{filename_base}.pdf")
                        elif html:
                            webbrowser.open(f"{filename_base}.html")

            except Exception as e:
                messagebox.showerror("Error de exportación", f"Error general: {str(e)}")

            finally:
                # Cerrar ventana de exportación
                ventana.destroy()

    def exportar_reporte(self):
        """Exporta el reporte actual a diferentes formatos"""
        # Verificar si hay datos para exportar
        if not hasattr(self, 'ultimo_resultado_consulta') or not self.ultimo_resultado_consulta:
            messagebox.showwarning("Sin datos", "No hay datos para exportar. Genere un reporte primero.")
            return

        # Mostrar opciones de exportación (código que ya teníamos en realizar_exportacion)
        ventana_exportar = tk.Toplevel(self.ventana)
        ventana_exportar.title("Exportar Reporte")
        ventana_exportar.geometry("400x300")
        ventana_exportar.config(bg="#f5f5f5")
        ventana_exportar.transient(self.ventana)
        ventana_exportar.grab_set()

        utl.centrar_ventana(ventana_exportar, 400, 300)

        tk.Label(
            ventana_exportar,
            text="Seleccione formato de exportación:",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5",
            pady=10
        ).pack()

        # Variables para las opciones
        var_excel = tk.IntVar(value=1)
        var_csv = tk.IntVar(value=0)
        var_pdf = tk.IntVar(value=0)
        var_html = tk.IntVar(value=0)

        # Frame para checkboxes
        frame_opciones = tk.Frame(ventana_exportar, bg="#f5f5f5", pady=10)
        frame_opciones.pack(fill=tk.X, padx=20)

        # Checkboxes para formatos
        cb_excel = tk.Checkbutton(
            frame_opciones,
            text="Excel (.xlsx)",
            variable=var_excel,
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        cb_excel.grid(row=0, column=0, sticky=tk.W, pady=5)

        cb_csv = tk.Checkbutton(
            frame_opciones,
            text="CSV (.csv)",
            variable=var_csv,
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        cb_csv.grid(row=1, column=0, sticky=tk.W, pady=5)

        cb_pdf = tk.Checkbutton(
            frame_opciones,
            text="PDF (.pdf)",
            variable=var_pdf,
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        cb_pdf.grid(row=2, column=0, sticky=tk.W, pady=5)

        cb_html = tk.Checkbutton(
            frame_opciones,
            text="HTML (.html)",
            variable=var_html,
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        cb_html.grid(row=3, column=0, sticky=tk.W, pady=5)

        # Opciones adicionales
        tk.Label(
            ventana_exportar,
            text="Opciones:",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5",
            pady=5
        ).pack(anchor=tk.W, padx=20)

        var_incluir_grafico = tk.IntVar(value=1)
        cb_grafico = tk.Checkbutton(
            ventana_exportar,
            text="Incluir gráfico en la exportación",
            variable=var_incluir_grafico,
            font=("Helvetica", 11),
            bg="#f5f5f5"
        )
        cb_grafico.pack(anchor=tk.W, padx=20, pady=5)

        # Botones de acción
        frame_botones = tk.Frame(ventana_exportar, bg="#f5f5f5", pady=10)
        frame_botones.pack(fill=tk.X, padx=20, pady=10)

        btn_exportar = tk.Button(
            frame_botones,
            text="Exportar",
            bg="#4CAF50",
            fg="white",
            font=("Helvetica", 11),
            width=10,
            command=lambda: self.realizar_exportacion(
                var_excel.get(), var_csv.get(), var_pdf.get(), var_html.get(),
                var_incluir_grafico.get(), ventana_exportar
            )
        )
        btn_exportar.pack(side=tk.LEFT, padx=10)

        btn_cancelar = tk.Button(
            frame_botones,
            text="Cancelar",
            bg="#F44336",
            fg="white",
            font=("Helvetica", 11),
            width=10,
            command=ventana_exportar.destroy
        )
        btn_cancelar.pack(side=tk.LEFT, padx=10)

    def personalizar_colores(self):
        """Permite al usuario personalizar los colores del gráfico"""
        # Esta función abrirá diálogos para seleccionar colores
        colors = []

        # Determinar cuántos colores necesitamos según el tipo de gráfico
        num_colors = 1

        if hasattr(self, 'datos_grafico'):
            tipo_datos = self.datos_grafico.get('tipo', '')

            if tipo_datos == 'ventas':
                num_colors = 2  # Ventas y métodos de pago
            elif tipo_datos in ['productos', 'servicios']:
                num_colors = 3  # Productos/servicios, cantidades, ingresos
            elif tipo_datos == 'clientes':
                num_colors = len(self.datos_grafico.get('categorias', {}).keys())
            elif tipo_datos == 'pedidos_estado':
                num_colors = len(self.datos_grafico.get('pedidos_por_estado', []))
            else:
                num_colors = 4  # Predeterminado para otros tipos

        # Solicitar colores al usuario
        for i in range(min(num_colors, 5)):  # Limitar a máximo 5 colores para no ser tedioso
            color = colorchooser.askcolor(title=f"Seleccione color {i + 1}")[1]
            if color:
                colors.append(color)
            else:
                break

        # Si se seleccionaron colores, actualizar paleta y gráfico
        if colors:
            sns.set_palette(colors)
            self.actualizar_grafico()

    def guardar_plantilla(self):
        """Guarda la configuración actual como una plantilla reutilizable"""
        # Solicitar nombre para la plantilla
        nombre = simpledialog.askstring(
            "Guardar plantilla",
            "Nombre para la plantilla:",
            parent=self.ventana
        )

        if not nombre:
            return

        # Crear directorio para plantillas si no existe
        plantillas_dir = os.path.join(self.directorio_reportes, "plantillas")
        if not os.path.exists(plantillas_dir):
            os.makedirs(plantillas_dir)

        # Obtener la configuración actual
        configuracion = {
            "tipo_reporte": self.tipo_reporte.get(),
            "periodo": self.periodo.get(),
            "fecha_inicio": self.fecha_inicio.get(),
            "fecha_fin": self.fecha_fin.get(),
            "filtros": {
                "cliente": self.filtro_cliente.get(),
                "vendedor": self.filtro_vendedor.get(),
                "pago": self.filtro_pago.get(),
                "estado": self.filtro_estado.get()
            },
            "tipo_grafico": self.tipo_grafico.get(),
            "estilo_grafico": self.estilo_grafico.get()
        }

        # Guardar configuración como JSON
        try:
            filename = os.path.join(plantillas_dir, f"{nombre}.json")
            with open(filename, 'w') as f:
                json.dump(configuracion, f, indent=4)

            messagebox.showinfo(
                "Éxito",
                f"Plantilla '{nombre}' guardada correctamente.\nPuede cargarla en futuras sesiones."
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la plantilla: {str(e)}")

    def cargar_plantilla(self):
        """Carga una plantilla de configuración guardada"""
        # Crear directorio para plantillas si no existe
        plantillas_dir = os.path.join(self.directorio_reportes, "plantillas")
        if not os.path.exists(plantillas_dir):
            os.makedirs(plantillas_dir)
            messagebox.showinfo("Sin plantillas", "No hay plantillas guardadas.")
            return

        # Buscar archivos de plantilla
        plantillas = [f for f in os.listdir(plantillas_dir) if f.endswith('.json')]

        if not plantillas:
            messagebox.showinfo("Sin plantillas", "No hay plantillas guardadas.")
            return

        # Crear ventana para seleccionar plantilla
        ventana_plantillas = tk.Toplevel(self.ventana)
        ventana_plantillas.title("Cargar Plantilla")
        ventana_plantillas.geometry("400x300")
        ventana_plantillas.config(bg="#f5f5f5")
        ventana_plantillas.transient(self.ventana)
        ventana_plantillas.grab_set()

        utl.centrar_ventana(ventana_plantillas, 400, 300)

        tk.Label(
            ventana_plantillas,
            text="Seleccione una plantilla:",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5",
            pady=10
        ).pack()

        # Lista de plantillas
        frame_lista = tk.Frame(ventana_plantillas, bg="#f5f5f5")
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        listbox = tk.Listbox(
            frame_lista,
            font=("Helvetica", 11),
            width=40,
            height=10
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Llenar listbox con nombres de plantillas
        for plantilla in plantillas:
            nombre = os.path.splitext(plantilla)[0]
            listbox.insert(tk.END, nombre)

        # Botones de acción
        frame_botones = tk.Frame(ventana_plantillas, bg="#f5f5f5", pady=10)
        frame_botones.pack(fill=tk.X, padx=20, pady=10)

        def cargar_seleccionada():
            if listbox.curselection():
                nombre = listbox.get(listbox.curselection())
                archivo = os.path.join(plantillas_dir, f"{nombre}.json")
                self.aplicar_plantilla(archivo)
                ventana_plantillas.destroy()
            else:
                messagebox.showwarning("Selección requerida", "Por favor, seleccione una plantilla.")

        btn_cargar = tk.Button(
            frame_botones,
            text="Cargar",
            bg="#4CAF50",
            fg="white",
            font=("Helvetica", 11),
            width=10,
            command=cargar_seleccionada
        )
        btn_cargar.pack(side=tk.LEFT, padx=10)

        btn_eliminar = tk.Button(
            frame_botones,
            text="Eliminar",
            bg="#F44336",
            fg="white",
            font=("Helvetica", 11),
            width=10,
            command=lambda: self.eliminar_plantilla(listbox, plantillas_dir)
        )
        btn_eliminar.pack(side=tk.LEFT, padx=10)

        btn_cancelar = tk.Button(
            frame_botones,
            text="Cancelar",
            bg="#9E9E9E",
            fg="white",
            font=("Helvetica", 11),
            width=10,
            command=ventana_plantillas.destroy
        )
        btn_cancelar.pack(side=tk.LEFT, padx=10)

        # Doble clic para seleccionar
        listbox.bind("<Double-Button-1>", lambda e: cargar_seleccionada())

    def eliminar_plantilla(self, listbox, directorio):
        """Elimina una plantilla seleccionada"""
        if not listbox.curselection():
            messagebox.showwarning("Selección requerida", "Por favor, seleccione una plantilla.")
            return

        nombre = listbox.get(listbox.curselection())
        archivo = os.path.join(directorio, f"{nombre}.json")

        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de eliminar la plantilla '{nombre}'?\nEsta acción no se puede deshacer."
        )

        if confirmar:
            try:
                os.remove(archivo)
                listbox.delete(listbox.curselection())
                messagebox.showinfo("Éxito", f"Plantilla '{nombre}' eliminada correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la plantilla: {str(e)}")

    def aplicar_plantilla(self, archivo):
        """Aplica la configuración de una plantilla cargada"""
        try:
            with open(archivo, 'r') as f:
                config = json.load(f)

            # Aplicar configuración
            self.tipo_reporte.set(config.get("tipo_reporte", "Ventas por Periodo"))
            self.periodo.set(config.get("periodo", "Este Mes"))
            self.fecha_inicio.set(config.get("fecha_inicio", ""))
            self.fecha_fin.set(config.get("fecha_fin", ""))

            # Aplicar filtros
            filtros = config.get("filtros", {})
            self.filtro_cliente.set(filtros.get("cliente", ""))
            self.filtro_vendedor.set(filtros.get("vendedor", ""))
            self.filtro_pago.set(filtros.get("pago", "Todos"))
            self.filtro_estado.set(filtros.get("estado", "Todos"))

            # Configurar gráficos
            self.tipo_grafico.set(config.get("tipo_grafico", "Barras"))
            self.estilo_grafico.set(config.get("estilo_grafico", "predeterminado"))

            # Actualizar interfaz para el tipo de reporte
            self.cambiar_tipo_reporte()

            # Forzar la visibilidad correcta del frame de fechas
            if self.periodo.get() == "Personalizado":
                self.frame_fechas_personalizadas.pack(side=tk.LEFT, padx=10)
            else:
                self.frame_fechas_personalizadas.pack_forget()

            messagebox.showinfo("Plantilla cargada", "La plantilla se ha aplicado correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la plantilla: {str(e)}")

    def filtrar_tabla(self, event=None):
        """Filtra los datos de la tabla según el texto de búsqueda"""
        texto_busqueda = self.busqueda_tabla.get().lower()

        # Si no hay texto de búsqueda, mostrar todos los items
        if not texto_busqueda:
            for item in self.tabla_reporte.get_children():
                self.tabla_reporte.item(item, tags=self.tabla_reporte.item(item)['tags'])
                self.tabla_reporte.detach(item)
                self.tabla_reporte.reattach(item, '', 'end')
            return

        # Recorrer todos los items
        for item in self.tabla_reporte.get_children():
            values = [str(v).lower() for v in self.tabla_reporte.item(item)['values']]

            # Si el texto de búsqueda está en alguno de los valores
            if any(texto_busqueda in value for value in values):
                # Mantener el item visible y marcarlo con color
                self.tabla_reporte.item(item, tags=(*self.tabla_reporte.item(item)['tags'], 'encontrado'))
                self.tabla_reporte.detach(item)
                self.tabla_reporte.reattach(item, '', 'end')
            else:
                # Ocultar el item temporalmente
                self.tabla_reporte.detach(item)

        # Configurar color para coincidencias
        self.tabla_reporte.tag_configure('encontrado', background='#e3f2fd')

    def limpiar_filtros_tabla(self):
        """Limpia los filtros de búsqueda de la tabla"""
        self.busqueda_tabla.set("")

        # Restaurar todos los items
        for item in self.tabla_reporte.get_children():
            self.tabla_reporte.item(item, tags=())

        # Mostrar también los items ocultos
        for item in self.tabla_reporte.get_children("hidden"):
            self.tabla_reporte.reattach(item, '', 'end')

    def mostrar_ayuda(self):
        """Muestra información de ayuda sobre el módulo de reportes"""
        ventana_ayuda = tk.Toplevel(self.ventana)
        ventana_ayuda.title("Ayuda - Reportes y Estadísticas")
        ventana_ayuda.geometry("600x500")
        ventana_ayuda.config(bg="#f5f5f5")

        utl.centrar_ventana(ventana_ayuda, 600, 500)

        # Crear notebook para organizar la ayuda
        notebook = ttk.Notebook(ventana_ayuda)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Función para crear pestañas de ayuda
        def crear_tab_ayuda(titulo, contenido):
            tab = tk.Frame(notebook, bg="#f5f5f5")
            notebook.add(tab, text=titulo)

            # Frame con scroll
            frame_canvas = tk.Frame(tab)
            frame_canvas.pack(fill=tk.BOTH, expand=True)

            canvas = tk.Canvas(frame_canvas, bg="#f5f5f5")
            scrollbar = ttk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)

            # Frame donde pondremos el contenido
            frame_contenido = tk.Frame(canvas, bg="#f5f5f5")

            # Configurar scrolling
            frame_contenido.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            # Crear ventana en el canvas
            canvas.create_window((0, 0), window=frame_contenido, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Empaquetar elementos
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Mostrar contenido
            for i, (titulo_seccion, texto) in enumerate(contenido):
                if titulo_seccion:
                    tk.Label(
                        frame_contenido,
                        text=titulo_seccion,
                        font=("Helvetica", 12, "bold"),
                        bg="#f5f5f5",
                        fg="#3a7ff6"
                    ).grid(row=i*2, column=0, sticky=tk.W, padx=10, pady=(10, 5))

                tk.Label(
                    frame_contenido,
                    text=texto,
                    font=("Helvetica", 11),
                    bg="#f5f5f5",
                    justify=tk.LEFT,
                    wraplength=550
                ).grid(row=i*2+1, column=0, sticky=tk.W, padx=10, pady=(0, 10))

            return tab

        # Contenido de la pestaña general
        contenido_general = [
            ("¿Qué es el módulo de reportes?",
             "El módulo de reportes proporciona visualizaciones y análisis detallados de los datos del sistema de lavandería. "
             "Permite generar informes sobre ventas, productos, servicios, clientes y más, con opciones de filtrado, visualización "
             "y exportación."),

            ("Tipos de reportes disponibles",
             "• Ventas por Periodo: Analiza las ventas realizadas en un período específico.\n"
             "• Productos Más Vendidos: Muestra los productos con mayor demanda.\n"
             "• Servicios Más Solicitados: Identifica los servicios más populares.\n"
             "• Clientes Frecuentes: Analiza los patrones de visita de los clientes.\n"
             "• Ingresos Mensuales: Visualiza los ingresos agrupados por mes.\n"
             "• Pedidos por Estado: Muestra la distribución de pedidos según su estado.\n"
             "• Rentabilidad de Servicios: Analiza márgenes y rentabilidad de cada servicio.\n"
             "• Comportamiento de Clientes: Utiliza análisis RFM para segmentar clientes.\n"
             "• Dashboard General: Presenta un resumen visual de las métricas clave."),

            ("¿Cómo usar el módulo?",
             "1. Seleccione el tipo de reporte que desea generar.\n"
             "2. Elija el período que desea analizar (o fechas personalizadas).\n"
             "3. Configure los filtros adicionales si es necesario.\n"
             "4. Haga clic en 'Generar Reporte'.\n"
             "5. Explore los datos en la pestaña 'Datos' o visualizaciones en 'Gráficos'.\n"
             "6. Personalice las visualizaciones con diferentes tipos de gráficos.\n"
             "7. Exporte los resultados en varios formatos según sus necesidades.")
        ]

        # Contenido de la pestaña de gráficos
        contenido_graficos = [
            ("Tipos de gráficos disponibles",
             "• Barras: Ideal para comparar valores entre categorías.\n"
             "• Líneas: Perfecto para mostrar tendencias a lo largo del tiempo.\n"
             "• Pastel: Muestra la proporción de cada categoría respecto al total.\n"
             "• Área: Similar a líneas, pero rellena el área bajo la curva.\n"
             "• Barras Horizontales: Útil cuando hay muchas categorías o nombres largos.\n"
             "• Dispersión: Muestra relaciones entre dos variables numéricas.\n"
             "• Calor: Visualiza matrices de datos con colores según intensidad."),

            ("Personalización de gráficos",
             "• Estilos: Cambie la apariencia general del gráfico con diferentes paletas de colores.\n"
             "• Colores personalizados: Defina sus propios colores para elementos específicos.\n"
             "• Exportación de imágenes: Guarde el gráfico como imagen en varios formatos (PNG, JPG, PDF, SVG)."),

            ("Consejos para visualizaciones efectivas",
             "• Use barras para comparaciones directas entre categorías.\n"
             "• Use líneas para mostrar tendencias temporales.\n"
             "• Utilice gráficos de pastel solo cuando tenga pocas categorías (máximo 5-7).\n"
             "• Los gráficos de calor son ideales para mostrar correlaciones y patrones complejos.\n"
             "• Para datos con muchas categorías, utilice barras horizontales.")
        ]

        # Contenido de la pestaña de exportación
        contenido_exportacion = [
            ("Formatos de exportación disponibles",
             "• Excel (.xlsx): Incluye múltiples hojas con datos, resumen y gráficos.\n"
             "• CSV (.csv): Formato simple para importar en otras aplicaciones.\n"
             "• PDF (.pdf): Informe profesional con datos y gráficos.\n"
             "• HTML (.html): Página web interactiva que puede abrirse en cualquier navegador."),

            ("Exportación de gráficos",
             "Los gráficos se pueden exportar como imágenes independientes o incluirse en los informes "
             "Excel, PDF y HTML. Para guardar un gráfico como imagen, utilice el botón 'Guardar como Imagen' "
             "en la pestaña de gráficos."),

            ("Plantillas de reportes",
             "Las plantillas le permiten guardar configuraciones de reportes para uso futuro:\n"
             "• Guardar plantilla: Almacena la configuración actual (tipo, filtros, período, etc.).\n"
             "• Cargar plantilla: Aplica una configuración guardada anteriormente.\n"
             "• Eliminar plantilla: Borra plantillas que ya no necesita.")
        ]

        # Crear pestañas
        crear_tab_ayuda("General", contenido_general)
        crear_tab_ayuda("Gráficos", contenido_graficos)
        crear_tab_ayuda("Exportación", contenido_exportacion)

        # Botón para cerrar
        btn_cerrar = tk.Button(
            ventana_ayuda,
            text="Cerrar",
            bg="#3a7ff6",
            fg="white",
            font=("Helvetica", 11),
            width=10,
            command=ventana_ayuda.destroy
        )
        btn_cerrar.pack(pady=10)


# Función para abrir el módulo desde otras partes del sistema
def abrir_reportes(ventana_padre=None):
    return Reportes(ventana_padre)


# Para pruebas independientes
if __name__ == "__main__":
    Reportes()