"""
Módulo de Generación e Impresión de Tickets para el Sistema de Lavandería
Permite generar tickets con formato personalizado e imprimirlos.
"""

import os
import sys
import tempfile
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import win32print
import win32ui
from PIL import Image, ImageDraw, ImageFont
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Asegurar que podamos importar módulos del sistema
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

try:
    from conexion import conectar_bd
    import utileria as utl
except ImportError as e:
    print(f"Error al importar módulos: {e}")


class Ticket:
    """Clase para gestionar la generación e impresión de tickets"""

    def __init__(self, ancho=80):
        """
        Inicializa un nuevo objeto de ticket

        Args:
            ancho (int): Ancho del ticket en mm (típicamente 80mm para impresoras térmicas estándar)
        """
        self.ancho = ancho
        self.contenido = []
        self.impresora_predeterminada = None
        self.obtener_impresora_predeterminada()

        # Datos de la empresa (estos deberían venir de una configuración en la BD)
        self.nombre_empresa = "Lavandería Exprés"
        self.direccion = "Calle Principal #123, Colonia Centro"
        self.telefono = "555-123-4567"
        self.rfc = "XAXX010101000"
        self.slogan = "¡Limpieza profesional a tu servicio!"

        # Ruta para la carpeta de tickets guardados
        self.carpeta_tickets = os.path.join(script_dir, "tickets")
        if not os.path.exists(self.carpeta_tickets):
            os.makedirs(self.carpeta_tickets)

    def obtener_impresora_predeterminada(self):
        """Obtiene el nombre de la impresora predeterminada en el sistema"""
        try:
            self.impresora_predeterminada = win32print.GetDefaultPrinter()
        except Exception:
            self.impresora_predeterminada = None
            print("No se pudo obtener la impresora predeterminada")

    def agregar_titulo(self, texto):
        """Agrega un título al ticket"""
        self.contenido.append({"tipo": "titulo", "texto": texto})

    def agregar_texto(self, texto):
        """Agrega texto normal al ticket"""
        self.contenido.append({"tipo": "texto", "texto": texto})

    def agregar_texto_centrado(self, texto):
        """Agrega texto centrado al ticket"""
        self.contenido.append({"tipo": "texto_centrado", "texto": texto})

    def agregar_texto_derecha(self, texto):
        """Agrega texto alineado a la derecha al ticket"""
        self.contenido.append({"tipo": "texto_derecha", "texto": texto})

    def agregar_linea(self):
        """Agrega una línea divisoria al ticket"""
        self.contenido.append({"tipo": "linea"})

    def agregar_espacio(self):
        """Agrega un espacio en blanco al ticket"""
        self.contenido.append({"tipo": "espacio"})

    def agregar_producto(self, nombre, cantidad, precio_unitario, subtotal):
        """Agrega un producto al ticket"""
        self.contenido.append({
            "tipo": "producto",
            "nombre": nombre,
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "subtotal": subtotal
        })

    def agregar_total(self, total):
        """Agrega el total al ticket"""
        self.contenido.append({
            "tipo": "total",
            "valor": total
        })

    def agregar_codigo_qr(self, datos):
        """Agrega un código QR al ticket"""
        self.contenido.append({
            "tipo": "qr",
            "datos": datos
        })

    def agregar_encabezado(self):
        """Agrega el encabezado estándar del ticket con los datos de la empresa"""
        self.agregar_texto_centrado(self.nombre_empresa)
        self.agregar_texto_centrado(self.direccion)
        self.agregar_texto_centrado(f"Tel: {self.telefono}")
        self.agregar_texto_centrado(f"RFC: {self.rfc}")
        self.agregar_linea()
        self.agregar_texto_centrado(self.slogan)
        self.agregar_linea()

        # Fecha y hora actual
        fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.agregar_texto(f"Fecha: {fecha_hora}")
        self.agregar_espacio()

    def agregar_pie(self, mensaje_personalizado=None):
        """Agrega el pie estándar del ticket"""
        self.agregar_linea()
        self.agregar_texto_centrado("¡Gracias por su preferencia!")
        if mensaje_personalizado:
            self.agregar_texto_centrado(mensaje_personalizado)

        # Generar un código para seguimiento (podría ser personalizado)
        fecha_codigo = datetime.now().strftime("%Y%m%d%H%M")
        codigo_seguimiento = f"LV{fecha_codigo}"
        self.agregar_texto_centrado(f"Código de seguimiento: {codigo_seguimiento}")

        # Opcional: añadir código QR para seguimiento
        self.agregar_codigo_qr(codigo_seguimiento)

        self.agregar_texto_centrado("Conserve su ticket para cualquier aclaración")
        self.agregar_espacio()

    def generar_pdf(self, nombre_archivo=None, cliente=None, no_venta=None):
        """
        Genera un archivo PDF con el contenido del ticket

        Args:
            nombre_archivo (str, opcional): Nombre del archivo PDF. Si es None, se genera automáticamente.
            cliente (dict, opcional): Datos del cliente para incluir en el ticket.
            no_venta (str, opcional): Número de venta para incluir en el archivo.

        Returns:
            str: Ruta del archivo PDF generado
        """
        if nombre_archivo is None:
            # Generar nombre basado en la fecha y número de venta
            fecha_str = datetime.now().strftime("%Y%m%d%H%M%S")
            if no_venta:
                nombre_archivo = f"ticket_{no_venta}_{fecha_str}.pdf"
            else:
                nombre_archivo = f"ticket_{fecha_str}.pdf"

        # Ruta completa del archivo
        ruta_archivo = os.path.join(self.carpeta_tickets, nombre_archivo)

        # Crear el documento PDF
        doc = SimpleDocTemplate(
            ruta_archivo,
            pagesize=(self.ancho * mm, 300 * mm),  # Alto adaptable, máximo 300mm
            leftMargin=5 * mm,
            rightMargin=5 * mm,
            topMargin=5 * mm,
            bottomMargin=5 * mm
        )

        # Estilos para el contenido
        estilos = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle(
            'titulo',
            parent=estilos['Heading1'],
            alignment=1,  # Centro
            fontSize=12
        )
        estilo_normal = ParagraphStyle(
            'normal',
            parent=estilos['Normal'],
            fontSize=8
        )
        estilo_centrado = ParagraphStyle(
            'centrado',
            parent=estilos['Normal'],
            alignment=1,  # Centro
            fontSize=8
        )
        estilo_derecha = ParagraphStyle(
            'derecha',
            parent=estilos['Normal'],
            alignment=2,  # Derecha
            fontSize=8
        )

        # Lista de elementos para el PDF
        elementos = []

        # Procesar el contenido
        for item in self.contenido:
            tipo = item["tipo"]

            if tipo == "titulo":
                elementos.append(Paragraph(item["texto"], estilo_titulo))
                elementos.append(Spacer(1, 2 * mm))

            elif tipo == "texto":
                elementos.append(Paragraph(item["texto"], estilo_normal))
                elementos.append(Spacer(1, 1 * mm))

            elif tipo == "texto_centrado":
                elementos.append(Paragraph(item["texto"], estilo_centrado))
                elementos.append(Spacer(1, 1 * mm))

            elif tipo == "texto_derecha":
                elementos.append(Paragraph(item["texto"], estilo_derecha))
                elementos.append(Spacer(1, 1 * mm))

            elif tipo == "linea":
                elementos.append(Paragraph("<hr/>", estilo_normal))
                elementos.append(Spacer(1, 1 * mm))

            elif tipo == "espacio":
                elementos.append(Spacer(1, 3 * mm))

            elif tipo == "producto":
                # Crear una tabla para el producto
                datos = [
                    [Paragraph(item["nombre"], estilo_normal), "", "", ""],
                    [
                        f"{item['cantidad']} x",
                        f"${item['precio_unitario']:.2f}",
                        "=",
                        Paragraph(f"${item['subtotal']:.2f}", estilo_derecha)
                    ]
                ]
                tabla = Table(datos, colWidths=[20*mm, 15*mm, 5*mm, 25*mm])
                tabla.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (1, 1), (3, 1), 'RIGHT'),
                ]))
                elementos.append(tabla)
                elementos.append(Spacer(1, 1 * mm))

            elif tipo == "total":
                datos = [["TOTAL:", Paragraph(f"${item['valor']:.2f}", estilo_derecha)]]
                tabla = Table(datos, colWidths=[40*mm, 25*mm])
                tabla.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ]))
                elementos.append(tabla)
                elementos.append(Spacer(1, 2 * mm))

            elif tipo == "qr":
                # Generar código QR
                try:
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=3,
                        border=4,
                    )
                    qr.add_data(item["datos"])
                    qr.make(fit=True)

                    # Guardar temporalmente la imagen QR
                    img_qr = qr.make_image(fill_color="black", back_color="white")
                    temp_qr = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                    img_qr.save(temp_qr.name)

                    # Añadir al PDF centrado
                    elementos.append(Spacer(1, 2 * mm))
                    elementos.append(Paragraph('<img src="{}" width="60" height="60" align="center"/>'.format(temp_qr.name), estilo_centrado))
                    elementos.append(Spacer(1, 2 * mm))
                except Exception as e:
                    print(f"Error al generar código QR: {e}")

        # Construir el PDF
        doc.build(elementos)

        return ruta_archivo

    def imprimir_ticket(self, ruta_pdf=None):
        """
        Imprime el ticket en la impresora predeterminada

        Args:
            ruta_pdf (str, opcional): Ruta del archivo PDF a imprimir. Si es None, se genera uno nuevo.

        Returns:
            bool: True si se imprimió correctamente, False en caso contrario
        """
        if not self.impresora_predeterminada:
            messagebox.showerror("Error", "No se ha configurado una impresora predeterminada")
            return False

        try:
            # Si no se proporciona una ruta, generar un PDF temporal
            if ruta_pdf is None:
                ruta_pdf = self.generar_pdf()

            # Código para enviar a la impresora usando el sistema operativo
            if sys.platform == 'win32':
                # En Windows, usar la API de impresión de Windows
                os.startfile(ruta_pdf, "print")
                return True
            else:
                # En otros sistemas, usar comandos del sistema
                os.system(f"lpr {ruta_pdf}")
                return True

        except Exception as e:
            messagebox.showerror("Error de impresión", f"No se pudo imprimir el ticket: {str(e)}")
            return False

    def mostrar_vista_previa(self, ruta_pdf=None):
        """
        Muestra una vista previa del ticket

        Args:
            ruta_pdf (str, opcional): Ruta del archivo PDF a mostrar. Si es None, se genera uno nuevo.
        """
        try:
            # Si no se proporciona una ruta, generar un PDF temporal
            if ruta_pdf is None:
                ruta_pdf = self.generar_pdf()

            # Abrir el archivo con el visor predeterminado
            os.startfile(ruta_pdf)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mostrar la vista previa: {str(e)}")

    def generar_ticket_venta(self, id_venta, vista_previa=True, imprimir=False):
        """
        Genera un ticket completo para una venta específica

        Args:
            id_venta (int): ID de la venta en la base de datos
            vista_previa (bool): Si se debe mostrar una vista previa
            imprimir (bool): Si se debe imprimir automáticamente

        Returns:
            str: Ruta del archivo PDF generado, o None si hubo un error
        """
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Obtener datos de la venta
            cursor.execute("""
                SELECT v.id_venta, v.fecha, v.total, v.metodo_pago, 
                       c.nombre AS cliente, c.puntos, u.nombre AS vendedor
                FROM ventas v
                LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
                LEFT JOIN usuarios u ON v.id_usuario = u.id_usuario
                WHERE v.id_venta = %s
            """, (id_venta,))

            venta = cursor.fetchone()

            if not venta:
                messagebox.showerror("Error", f"No se encontró la venta con ID {id_venta}")
                return None

            # Obtener detalles de la venta
            cursor.execute("""
                SELECT tipo_item, id_item, cantidad, subtotal 
                FROM detalle_venta 
                WHERE id_venta = %s
            """, (id_venta,))

            detalles = cursor.fetchall()

            # Crear el ticket
            self.contenido = []  # Limpiar contenido previo

            # Encabezado
            self.agregar_encabezado()

            # Información de la venta
            self.agregar_titulo(f"TICKET DE VENTA #{venta[0]}")
            self.agregar_texto(f"Cliente: {venta[4] if venta[4] else 'Cliente General'}")
            if venta[4]:  # Si hay cliente registrado, mostrar puntos
                self.agregar_texto(f"Puntos acumulados: {venta[5]}")

            self.agregar_texto(f"Vendedor: {venta[6]}")
            self.agregar_texto(f"Forma de pago: {venta[3]}")
            self.agregar_linea()

            # Obtener y agregar items al ticket
            for detalle in detalles:
                tipo_item, id_item, cantidad, subtotal = detalle

                # Obtener nombre del item según su tipo
                if tipo_item == 'producto':
                    cursor.execute("SELECT nombre, precio FROM productos WHERE id_producto = %s", (id_item,))
                    item = cursor.fetchone()
                    if item:
                        nombre_item, precio_unitario = item
                        self.agregar_producto(nombre_item, cantidad, precio_unitario, subtotal)

                elif tipo_item == 'servicio':
                    cursor.execute("SELECT nombre, precio FROM servicios WHERE id_servicio = %s", (id_item,))
                    item = cursor.fetchone()
                    if item:
                        nombre_item, precio_unitario = item
                        self.agregar_producto(nombre_item, cantidad, precio_unitario, subtotal)

            # Total
            self.agregar_linea()
            self.agregar_total(venta[2])  # Total de la venta

            # Pie de ticket
            self.agregar_pie("Vuelva pronto")

            # Generar nombre del archivo
            nombre_archivo = f"ticket_venta_{id_venta}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

            # Generar el PDF
            ruta_pdf = self.generar_pdf(nombre_archivo)

            # Mostrar vista previa si se solicita
            if vista_previa:
                self.mostrar_vista_previa(ruta_pdf)

            # Imprimir si se solicita
            if imprimir:
                self.imprimir_ticket(ruta_pdf)

            conexion.close()
            return ruta_pdf

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el ticket: {str(e)}")
            return None

    def generar_ticket_pedido(self, id_pedido, vista_previa=True, imprimir=False):
        """
        Genera un ticket completo para un pedido específico

        Args:
            id_pedido (int): ID del pedido en la base de datos
            vista_previa (bool): Si se debe mostrar una vista previa
            imprimir (bool): Si se debe imprimir automáticamente

        Returns:
            str: Ruta del archivo PDF generado, o None si hubo un error
        """
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Obtener datos del pedido
            cursor.execute("""
                SELECT p.id_pedido, p.fecha_pedido, p.estado, c.nombre AS cliente,
                       (SELECT SUM(dp.cantidad * dp.precio_unitario) 
                        FROM detalle_pedido dp 
                        WHERE dp.id_pedido = p.id_pedido) AS total,
                       p.observaciones
                FROM pedidos p
                LEFT JOIN clientes c ON p.id_cliente = c.id_cliente
                WHERE p.id_pedido = %s
            """, (id_pedido,))

            pedido = cursor.fetchone()

            if not pedido:
                messagebox.showerror("Error", f"No se encontró el pedido con ID {id_pedido}")
                return None

            # Obtener detalles del pedido
            cursor.execute("""
                SELECT s.nombre, dp.cantidad, dp.precio_unitario, 
                       (dp.cantidad * dp.precio_unitario) AS subtotal
                FROM detalle_pedido dp
                JOIN servicios s ON dp.id_item = s.id_servicio
                WHERE dp.id_pedido = %s AND dp.tipo_item = 'servicio'
            """, (id_pedido,))

            detalles = cursor.fetchall()

            # Crear el ticket
            self.contenido = []  # Limpiar contenido previo

            # Encabezado
            self.agregar_encabezado()

            # Información del pedido
            self.agregar_titulo(f"COMPROBANTE DE PEDIDO #{pedido[0]}")
            self.agregar_texto(f"Cliente: {pedido[3]}")
            self.agregar_texto(f"Fecha: {utl.formatear_fecha(pedido[1], '%d/%m/%Y %H:%M')}")
            self.agregar_texto(f"Estado: {pedido[2]}")

            # Si hay observaciones, mostrarlas
            if pedido[5]:
                self.agregar_texto("Observaciones:")
                self.agregar_texto(pedido[5])

            self.agregar_linea()
            self.agregar_texto("DETALLE DEL PEDIDO:")

            # Agregar servicios al ticket
            for servicio in detalles:
                nombre, cantidad, precio_unitario, subtotal = servicio
                self.agregar_producto(nombre, cantidad, precio_unitario, subtotal)

            # Total
            self.agregar_linea()
            self.agregar_total(pedido[4])  # Total del pedido

            # Información de entrega
            self.agregar_espacio()
            self.agregar_texto_centrado(f"Fecha estimada de entrega:")

            # Calcular fecha estimada (ejemplo: 2 días después del pedido)
            from datetime import timedelta
            fecha_pedido = pedido[1]
            fecha_entrega = fecha_pedido + timedelta(days=2)
            self.agregar_texto_centrado(utl.formatear_fecha(fecha_entrega, '%d/%m/%Y'))

            # Pie de ticket
            self.agregar_pie("Presente este comprobante para recoger su pedido")

            # Generar nombre del archivo
            nombre_archivo = f"ticket_pedido_{id_pedido}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

            # Generar el PDF
            ruta_pdf = self.generar_pdf(nombre_archivo)

            # Mostrar vista previa si se solicita
            if vista_previa:
                self.mostrar_vista_previa(ruta_pdf)

            # Imprimir si se solicita
            if imprimir:
                self.imprimir_ticket(ruta_pdf)

            conexion.close()
            return ruta_pdf

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el ticket: {str(e)}")
            return None


# Función para invocar directamente desde otros módulos
def imprimir_ticket_venta(id_venta, vista_previa=True, imprimir=True):
    """
    Genera e imprime un ticket de venta

    Args:
        id_venta (int): ID de la venta
        vista_previa (bool): Mostrar vista previa
        imprimir (bool): Imprimir directamente

    Returns:
        str: Ruta del PDF generado o None si hay error
    """
    ticket = Ticket()
    return ticket.generar_ticket_venta(id_venta, vista_previa, imprimir)


def imprimir_ticket_pedido(id_pedido, vista_previa=True, imprimir=True):
    """
    Genera e imprime un ticket de pedido

    Args:
        id_pedido (int): ID del pedido
        vista_previa (bool): Mostrar vista previa
        imprimir (bool): Imprimir directamente

    Returns:
        str: Ruta del PDF generado o None si hay error
    """
    ticket = Ticket()
    return ticket.generar_ticket_pedido(id_pedido, vista_previa, imprimir)


# Para pruebas independientes
if __name__ == "__main__":
    # Crear un ticket de prueba
    ticket = Ticket()

    # Agregar contenido de prueba
    ticket.agregar_encabezado()
    ticket.agregar_titulo("TICKET DE PRUEBA")
    ticket.agregar_texto("Cliente: Juan Pérez")
    ticket.agregar_linea()

    # Productos de ejemplo
    ticket.agregar_producto("Lavado de camisa", 3, 25.00, 75.00)
    ticket.agregar_producto("Planchado", 5, 15.00, 75.00)
    ticket.agregar_producto("Servicio express", 1, 50.00, 50.00)

    # Total
    ticket.agregar_linea()
    ticket.agregar_total(200.00)

    # Pie de ticket
    ticket.agregar_pie("¡Promoción 2x1 en lavado de camisas!")

    # Generar PDF y mostrar vista previa
    ruta_pdf = ticket.generar_pdf("ticket_prueba.pdf")
    ticket.mostrar_vista_previa(ruta_pdf)

    # Opcionalmente imprimir
    # ticket.imprimir_ticket(ruta_pdf)