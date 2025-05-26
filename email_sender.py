import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def enviar_codigo(destinatario, codigo):
    remitente = "cleanandwhite.business@gmail.com"
    contrasena = "yigdyxuhdveeppbi"  # Contraseña de aplicación de Gmail

    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = 'Recuperación de contraseña - Clean & White'

    cuerpo = f"""
    Hola, recibiste este correo porque solicitaste recuperar tu contraseña.

    Tu código de verificación es: {codigo}

    Si no lo solicitaste, ignora este mensaje.

    Atentamente,
    Equipo de Clean & White
    """

    mensaje.attach(MIMEText(cuerpo, 'plain', 'utf-8'))

    try:
        print(f"🔄 Intentando enviar código de recuperación a: {destinatario}")
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(remitente, contrasena)
        servidor.send_message(mensaje)
        servidor.quit()
        print(f"✅ Código enviado exitosamente a {destinatario}")
        return True
    except Exception as e:
        print(f"❌ Error al enviar correo: {e}")
        return False