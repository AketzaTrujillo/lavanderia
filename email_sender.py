import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_codigo(destinatario, codigo):
    remitente = "correo_envio@gmail.com"
    contrasena = "contrasena_generada"

    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = 'Recuperación de contraseña - Lavandería'

    cuerpo = f"""
    Hola, recibiste este correo porque solicitaste recuperar tu contraseña.
    
    Tu código de verificación es: {codigo}

    Si no lo solicitaste, ignora este mensaje.
    """

    mensaje.attach(MIMEText(cuerpo, 'plain', 'utf-8'))


    try:
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(remitente, contrasena)
        servidor.send_message(mensaje)
        servidor.quit()
        return True
    except Exception as e:
        print("Error al enviar correo:", e)
        return False
