"""
Módulo de utilidades para el Sistema de Gestión de Lavandería
Proporciona funciones comunes utilizadas en diferentes partes de la aplicación
"""

import os
import sys
import tkinter as tk
from PIL import ImageTk, Image
from datetime import datetime


def leer_imagen(path, size):
    """
    Lee una imagen desde un archivo y la redimensiona

    Args:
        path (str): Ruta de la imagen
        size (tuple): Tamaño de la imagen (ancho, alto)

    Returns:
        ImageTk.PhotoImage: Imagen para usar en tkinter
    """
    try:
        return ImageTk.PhotoImage(Image.open(path).resize(size, Image.LANCZOS))
    except Exception as e:
        print(f"Error al cargar la imagen {path}: {e}")
        # Crear una imagen en blanco como fallback
        img = Image.new('RGB', size, color='gray')
        return ImageTk.PhotoImage(img)


def centrar_ventana(ventana, ancho, alto):
    """
    Centra una ventana en la pantalla

    Args:
        ventana (tk.Tk o tk.Toplevel): Ventana a centrar
        ancho (int): Ancho de la ventana
        alto (int): Alto de la ventana

    Returns:
        str: Geometría aplicada a la ventana
    """
    # Obtener dimensiones de la pantalla
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()

    # Calcular posición x e y para centrar la ventana
    x = int((pantalla_ancho / 2) - (ancho / 2))
    y = int((pantalla_alto / 2) - (alto / 2))

    # Establecer geometría
    return ventana.geometry(f"{ancho}x{alto}+{x}+{y}")


def formatear_fecha(fecha, formato='%d/%m/%Y'):
    """
    Convierte un objeto datetime a string con formato específico

    Args:
        fecha (datetime): Fecha a formatear
        formato (str): Formato de salida

    Returns:
        str: Fecha formateada
    """
    if fecha:
        try:
            return fecha.strftime(formato)
        except:
            return ""
    return ""


def validar_numero(entrada):
    """
    Valida si un string puede convertirse a número

    Args:
        entrada (str): String a validar

    Returns:
        bool: True si es un número válido
    """
    if not entrada:
        return False

    try:
        float(entrada.replace(',', '.'))
        return True
    except ValueError:
        return False


def formatear_moneda(valor):
    """
    Formatea un número como moneda

    Args:
        valor (float): Valor a formatear

    Returns:
        str: Valor formateado como moneda
    """
    try:
        return f"${float(valor):,.2f}"
    except:
        return "$0.00"


def aplicar_estilo_tabla(tabla):
    """
    Aplica un estilo mejorado a una tabla (Treeview)

    Args:
        tabla (ttk.Treeview): Tabla a la que aplicar estilo
    """
    style = tk.ttk.Style()

    # Configurar alternancia de colores en las filas
    style.configure(
        "Treeview",
        background="#f0f0f0",
        foreground="black",
        rowheight=25,
        fieldbackground="#f0f0f0"
    )

    # Configurar colores al seleccionar
    style.map(
        'Treeview',
        background=[('selected', '#3a7ff6')],
        foreground=[('selected', 'white')]
    )

    # Configura encabezados
    style.configure(
        "Treeview.Heading",
        background="#3a7ff6",
        foreground="white",
        font=('Helvetica', 10, 'bold')
    )


def mostrar_mensaje(tipo, titulo, mensaje):
    """
    Muestra un cuadro de mensaje con un formato mejorado

    Args:
        tipo (str): Tipo de mensaje: 'info', 'warning', 'error' o 'question'
        titulo (str): Título del mensaje
        mensaje (str): Contenido del mensaje

    Returns:
        bool: True si el usuario selecciona "Sí" (solo para tipo 'question')
    """
    if tipo == 'info':
        return tk.messagebox.showinfo(titulo, mensaje)
    elif tipo == 'warning':
        return tk.messagebox.showwarning(titulo, mensaje)
    elif tipo == 'error':
        return tk.messagebox.showerror(titulo, mensaje)
    elif tipo == 'question':
        return tk.messagebox.askyesno(titulo, mensaje)