import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_correo(destinatario, asunto, mensaje):
    # Configuración del servidor SMTP de Gmail
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    remitente = "Jh666957@gmail.com"
    contraseña = "Gatitosblancos"

    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(mensaje, 'plain'))

    try:
        # Conectar al servidor SMTP y enviar el correo
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Iniciar TLS
        server.login(remitente, contraseña)
        server.send_message(msg)
        print("Correo enviado correctamente.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:
        server.quit()

# Uso de la función
enviar_correo("Jhoanhp2002yahoo.es@gmail.com", "Asunto del correo", "Este es el cuerpo del correo.")