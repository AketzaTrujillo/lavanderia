import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import base64


def enviar_correo_simple(destinatario, asunto, mensaje):
    """
    Versión simplificada que garantiza el manejo correcto de caracteres UTF-8.
    """
    # Configura estos valores
    remitente = "tu_correo@gmail.com"  # CAMBIAR por tu correo real
    password = "abcdefghijklmnop"  # CAMBIAR por tu contraseña de aplicación

    try:
        # Crear servidor
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(remitente, password)

        # Crear mensaje simple con codificación correcta
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = asunto

        # Agregar cuerpo en formato UTF-8
        msg.attach(MIMEText(mensaje, 'plain', 'utf-8'))

        # Enviar correo con codificación UTF-8
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()

        print(f"Correo simple enviado exitosamente a {destinatario}")
        return True

    except Exception as e:
        print(f"Error al enviar correo simple: {str(e)}")
        return False


def enviar_correo_html(destinatario, asunto, contenido_html):
    """
    Envía un correo con contenido HTML formateado con codificación UTF-8.

    Args:
        destinatario: Email del destinatario
        asunto: Asunto del correo
        contenido_html: Contenido HTML del correo (plantilla)

    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    # ==== CONFIGURA ESTOS VALORES CON TUS DATOS ====
    remitente = "kevalenciahd09@gmail.com"  # CAMBIA ESTO con tu correo de Gmail
    password = "imwg qdss lkrd nfoo"  # CAMBIA ESTO con tu contraseña de aplicación
    # ============================================

    try:
        # Crear mensaje con formato HTML
        email = MIMEMultipart("alternative")
        email['From'] = remitente
        email['To'] = destinatario
        email['Subject'] = asunto

        # Adjuntar contenido HTML con codificación UTF-8 explícita
        parte_html = MIMEText(contenido_html, 'html', 'utf-8')
        email.attach(parte_html)

        # Crear conexión segura con el servidor
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(remitente, password)
            texto = email.as_string()
            server.sendmail(remitente, destinatario, texto)

        print(f"Correo HTML enviado exitosamente a {destinatario}")
        return True

    except Exception as e:
        print(f"Error al enviar correo HTML: {str(e)}")
        return False


# Plantillas HTML para diferentes tipos de notificaciones
def obtener_plantilla_alta_cliente(nombre, correo):
    """Plantilla HTML para notificación de alta de cliente"""
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Bienvenido a Lavandería</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333333;
                max-width: 600px;
                margin: 0 auto;
            }}
            .container {{
                padding: 20px;
                background-color: #f0f4f8;
                border-radius: 8px;
            }}
            .header {{
                background-color: #558b2f;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 8px 8px 0 0;
                margin-bottom: 20px;
            }}
            .content {{
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .footer {{
                text-align: center;
                padding: 10px;
                font-size: 12px;
                color: #666666;
            }}
            .button {{
                display: inline-block;
                background-color: #558b2f;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 4px;
                margin-top: 15px;
            }}
            .info {{
                background-color: #f9f9f9;
                padding: 15px;
                border-left: 4px solid #558b2f;
                margin-top: 15px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>¡Bienvenido a Lavandería!</h1>
            </div>
            <div class="content">
                <h2>Hola {nombre},</h2>
                <p>¡Gracias por registrarte en nuestro sistema de lavandería! Tu cuenta ha sido creada exitosamente.</p>

                <div class="info">
                    <p><strong>Datos de tu registro:</strong></p>
                    <p><strong>Nombre:</strong> {nombre}</p>
                    <p><strong>Correo:</strong> {correo}</p>
                    <p><strong>Puntos iniciales:</strong> 0</p>
                </div>

                <p>Con tu cuenta podrás:</p>
                <ul>
                    <li>Acumular puntos en cada servicio</li>
                    <li>Recibir promociones especiales</li>
                    <li>Dar seguimiento a tus pedidos</li>
                </ul>

                <center>
                    <a href="#" class="button">Visitar Nuestro Sitio</a>
                </center>
            </div>
            <div class="footer">
                <p>© 2025 Lavandería. Todos los derechos reservados.</p>
                <p>Si no solicitaste este registro, por favor ignora este mensaje.</p>
            </div>
        </div>
    </body>
    </html>
    """


def obtener_plantilla_actualizacion_puntos(nombre, mensaje, puntos_nuevos, motivo):
    """Plantilla HTML para notificación de actualización de puntos"""
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Actualización de Puntos - Lavandería</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333333;
                max-width: 600px;
                margin: 0 auto;
            }}
            .container {{
                padding: 20px;
                background-color: #f0f4f8;
                border-radius: 8px;
            }}
            .header {{
                background-color: #00796b;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 8px 8px 0 0;
                margin-bottom: 20px;
            }}
            .content {{
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .footer {{
                text-align: center;
                padding: 10px;
                font-size: 12px;
                color: #666666;
            }}
            .points-box {{
                background-color: #e0f2f1;
                border: 2px solid #00796b;
                border-radius: 8px;
                padding: 15px;
                text-align: center;
                margin: 20px 0;
            }}
            .points-value {{
                font-size: 36px;
                font-weight: bold;
                color: #00796b;
            }}
            .reason {{
                background-color: #f9f9f9;
                padding: 15px;
                border-left: 4px solid #00796b;
                margin-top: 15px;
            }}
            .button {{
                display: inline-block;
                background-color: #00796b;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 4px;
                margin-top: 15px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Actualización de Puntos</h1>
            </div>
            <div class="content">
                <h2>Hola {nombre},</h2>
                <p>Tus puntos de fidelidad han sido actualizados.</p>

                <div class="points-box">
                    <p>{mensaje}</p>
                    <p>Tus puntos actuales:</p>
                    <div class="points-value">{puntos_nuevos}</div>
                </div>

                <div class="reason">
                    <p><strong>Motivo:</strong> {motivo}</p>
                </div>

                <p>Puedes usar tus puntos para obtener descuentos en tus próximos servicios.</p>

                <center>
                    <a href="#" class="button">Ver Mi Cuenta</a>
                </center>
            </div>
            <div class="footer">
                <p>© 2025 Lavandería. Todos los derechos reservados.</p>
                <p>Este es un mensaje automático, por favor no responder.</p>
            </div>
        </div>
    </body>
    </html>
    """


def obtener_plantilla_baja_cliente(nombre):
    """Plantilla HTML para notificación de baja de cliente"""
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Confirmación de Baja - Lavandería</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333333;
                max-width: 600px;
                margin: 0 auto;
            }}
            .container {{
                padding: 20px;
                background-color: #f0f4f8;
                border-radius: 8px;
            }}
            .header {{
                background-color: #757575;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 8px 8px 0 0;
                margin-bottom: 20px;
            }}
            .content {{
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .footer {{
                text-align: center;
                padding: 10px;
                font-size: 12px;
                color: #666666;
            }}
            .message-box {{
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                margin: 20px 0;
            }}
            .button {{
                display: inline-block;
                background-color: #757575;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 4px;
                margin-top: 15px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Confirmación de Baja</h1>
            </div>
            <div class="content">
                <h2>Hola {nombre},</h2>
                <p>Lamentamos informarte que tu cuenta ha sido dada de baja en nuestro sistema.</p>

                <div class="message-box">
                    <p>Tu información ha sido procesada y ya no está activa en nuestro sistema.</p>
                </div>

                <p>Queremos agradecerte por haber sido cliente de nuestra lavandería. Si en algún momento deseas volver a utilizar nuestros servicios, siempre serás bienvenido/a.</p>

                <p>Si consideras que esto ha sido un error o deseas volver a registrarte, por favor contáctanos.</p>

                <center>
                    <a href="#" class="button">Contactar Servicio al Cliente</a>
                </center>
            </div>
            <div class="footer">
                <p>© 2025 Lavandería. Todos los derechos reservados.</p>
                <p>Este es un mensaje automático, por favor no responder.</p>
            </div>
        </div>
    </body>
    </html>
    """


# Ejemplo de uso
if __name__ == "__main__":
    destinatario_prueba = "kevalenciahd09@gmail.com"  # Cambia por un correo válido para pruebas

    # Ejemplo de alta de cliente
    html_alta = obtener_plantilla_alta_cliente("Juan Pérez", destinatario_prueba)
    enviar_correo_html(destinatario_prueba, "Bienvenido a Lavanderia", html_alta)

    # Ejemplo de actualización de puntos
    html_puntos = obtener_plantilla_actualizacion_puntos(
        "Juan Pérez",
        "Se agregaron 50 puntos a tu cuenta.",
        150,
        "Compra de servicio premium"
    )
    enviar_correo_html(destinatario_prueba, "Actualizacion de Puntos", html_puntos)

    # Ejemplo de baja de cliente
    html_baja = obtener_plantilla_baja_cliente("Juan Pérez")
    enviar_correo_html(destinatario_prueba, "Confirmacion de Baja", html_baja)