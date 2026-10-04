import os
import smtplib
from email.message import EmailMessage

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
MAIL_FROM = os.environ.get("MAIL_FROM", SMTP_USER or "libroteca@example.com")
MAIL_FROM_NAME = os.environ.get("MAIL_FROM_NAME", "Libroteca")

# Sin credenciales el sistema funciona en modo desarrollo: el código se
# devuelve en la respuesta para poder completar el flujo sin SMTP configurado.
DEV_MODE = not (SMTP_USER and SMTP_PASSWORD)


def smtp_configured():
    return not DEV_MODE


def _plain_body(subject, text):
    return (
        "Hola,\n\n"
        f"{text}\n\n"
        "---\n"
        f"{MAIL_FROM_NAME} · Libroteca\n"
        "Este es un mensaje automático, por favor no respondas a este correo.\n"
    )


def send_verification_code(destinatario, nombre, codigo):
    subject = f"Verifica tu correo en Libroteca · código {codigo}"
    text = (
        f"Hola {nombre},\n\n"
        "Confirma tu correo para poder escribir reseñas en la biblioteca. "
        f"Tu código de verificación es: {codigo}\n\n"
        "El código vence en 30 minutos."
    )
    return _send(destinatario, subject, text)


def send_welcome(destinatario, nombre):
    subject = "¡Correo verificado en Libroteca!"
    text = (
        f"Listo {nombre}, tu correo ya está confirmado.\n\n"
        "Ya puedes iniciar sesión, marcar favoritos y publicar reseñas "
        "de los libros que leas."
    )
    return _send(destinatario, subject, text)


def _send(destinatario, subject, text):
    if DEV_MODE:
        print(f"[mailer: modo desarrollo] {subject} -> {destinatario}\n{_plain_body(subject, text)}")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{MAIL_FROM_NAME} <{MAIL_FROM}>"
    msg["To"] = destinatario
    msg.set_content(text)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            server.starttls()
            if SMTP_USER:
                server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as exc:  # noqa: BLE001 - el registro no debe caerse por SMTP
        print(f"[mailer] no se pudo enviar a {destinatario}: {exc}")
        return False