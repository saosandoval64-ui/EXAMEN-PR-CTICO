import json
import os
import random
import secrets
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

import mailer
import models

auth_bp = Blueprint("auth", __name__)

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.environ.get(
    "GOOGLE_REDIRECT_URI", "http://127.0.0.1:5000/google/callback"
)
GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v3/userinfo"

CODE_TTL_MINUTES = 30
RESEND_COOLDOWN_SECONDS = 60

ADMIN_CORREO = os.environ.get("ADMIN_CORREO", "perlazasandoval9@gmail.com")
ADMIN_CLAVE = os.environ.get("ADMIN_CLAVE", "123456")


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def is_valid_email(correo):
    correo = correo.strip()
    if correo.count("@") != 1:
        return False
    local, _, domain = correo.partition("@")
    if not local or "." in local or " " in local:
        return False
    if "." not in domain or domain.startswith(".") or domain.endswith("."):
        return False
    return " " not in domain


def normalize_email(correo):
    return correo.strip().lower()


def google_configured():
    return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = models.get_user(user_id)
    if not user:
        session.clear()
        return None
    return user


def login_user(user):
    session.clear()
    session["user_id"] = user["id"]
    session.permanent = True
    session.permanent_session_lifetime = timedelta(days=7)


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if current_user() is None:
            flash("Inicia sesión para continuar.", "error")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapper


def _code_sent_recently():
    sent_at = session.get("code_sent_at")
    if not sent_at:
        return False
    return (datetime.now(timezone.utc) - sent_at).total_seconds() < RESEND_COOLDOWN_SECONDS


def ensure_admin():
    correo = normalize_email(ADMIN_CORREO)
    if models.get_user_by_correo(correo):
        return None
    return models.create_user(
        nombre="Administrador",
        correo=correo,
        clave_hash=generate_password_hash(ADMIN_CLAVE),
        verificado=1,
        es_admin=1,
        creado_en=now_iso(),
    )


@auth_bp.route("/registro", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = normalize_email(request.form.get("correo", ""))
        clave = request.form.get("clave", "")

        if not nombre:
            flash("Escribe tu nombre.", "error")
            return redirect(url_for("auth.register"))

        if not is_valid_email(correo):
            flash("Escribe un correo válido, por ejemplo nombre@dominio.com.", "error")
            return redirect(url_for("auth.register"))

        if len(clave) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "error")
            return redirect(url_for("auth.register"))

        if models.get_user_by_correo(correo):
            flash("Ya existe una cuenta con ese correo.", "error")
            return redirect(url_for("auth.register"))

        codigo = f"{random.SystemRandom().randrange(0, 1000000):06d}"
        user_id = models.create_user(
            nombre=nombre,
            correo=correo,
            clave_hash=generate_password_hash(clave),
            verificado=0,
            codigo_verificacion=codigo,
            creado_en=now_iso(),
        )
        ensure_admin()
        mailer.send_verification_code(correo, nombre, codigo)
        session["code_sent_at"] = datetime.now(timezone.utc)
        session["pending_user_id"] = user_id

        if mailer.smtp_configured():
            flash("Te enviamos un código de 6 dígitos a tu correo.", "success")
        else:
            flash(f"SMTP sin configurar: tu código de verificación es {codigo}.", "error")
        return redirect(url_for("auth.verify"))

    return render_template("registro.html", google_ready=google_configured())


@auth_bp.route("/verificar", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
        pending = session.get("pending_user_id")
        user = models.get_user(pending) if pending else None

        if not user:
            flash("Inicia sesión de nuevo para verificar tu correo.", "error")
            return redirect(url_for("auth.login"))

        if _code_sent_recently() and request.form.get("reenviar"):
            flash("Espera un minuto antes de pedir otro código.", "error")
            return redirect(url_for("auth.verify"))

        if codigo != user["codigo_verificacion"]:
            flash("El código no coincide. Revisa el correo e inténtalo de nuevo.", "error")
            return redirect(url_for("auth.verify"))

        models.mark_user_verified(user["id"])
        session.pop("code_sent_at", None)
        mailer.send_welcome(user["correo"], user["nombre"])
        login_user(user)
        flash("¡Correo verificado! Ya puedes escribir reseñas.", "success")
        return redirect(url_for("web.index"))

    return render_template("verificar.html")


@auth_bp.route("/verificar/reenviar", methods=["POST"])
def resend_code():
    pending = session.get("pending_user_id")
    user = models.get_user(pending) if pending else None
    if not user:
        flash("No hay una verificación pendiente.", "error")
        return redirect(url_for("auth.login"))

    if _code_sent_recently():
        flash("Espera un minuto antes de pedir otro código.", "error")
        return redirect(url_for("auth.verify"))

    codigo = f"{random.SystemRandom().randrange(0, 1000000):06d}"
    models.set_verification_code(user["id"], codigo)
    session["code_sent_at"] = datetime.now(timezone.utc)
    mailer.send_verification_code(user["correo"], user["nombre"], codigo)

    if mailer.smtp_configured():
        flash("Te enviamos un código nuevo.", "success")
    else:
        flash(f"SMTP sin configurar: tu código es {codigo}.", "error")
    return redirect(url_for("auth.verify"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = normalize_email(request.form.get("correo", ""))
        clave = request.form.get("clave", "")
        user = models.get_user_by_correo(correo)

        if not user or not user["clave_hash"] or not check_password_hash(
            user["clave_hash"], clave
        ):
            flash("Correo o contraseña incorrectos.", "error")
            return redirect(url_for("auth.login", next=request.args.get("next")))

        if user["bloqueado"]:
            flash(
                "Esta cuenta está bloqueada por un administrador. Escribe al soporte "
                "si crees que es un error.",
                "error",
            )
            return redirect(url_for("auth.login"))

        if not user["verificado"]:
            session["pending_user_id"] = user["id"]
            flash("Primero debes verificar tu correo.", "error")
            return redirect(url_for("auth.verify"))

        login_user(user)
        flash(f"Hola de nuevo, {user['nombre']}.", "success")
        destino = request.args.get("next") or url_for("web.index")
        if not destino.startswith("/"):
            destino = url_for("web.index")
        return redirect(destino)

    return render_template("login.html", google_ready=google_configured())


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("web.index"))


@auth_bp.route("/google/login")
def google_login():
    if not google_configured():
        flash(
            "El acceso con Google aún no está configurado. Define GOOGLE_CLIENT_ID y "
            "GOOGLE_CLIENT_SECRET en el entorno.",
            "error",
        )
        return redirect(url_for("auth.login"))

    state = secrets.token_urlsafe(24)
    session["oauth_state"] = state
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
        "access_type": "offline",
    }
    return redirect(f"{GOOGLE_AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}")


@auth_bp.route("/google/callback")
def google_callback():
    if not google_configured():
        return redirect(url_for("auth.login"))

    if request.args.get("error"):
        flash("Cancelaste el acceso con Google.", "error")
        return redirect(url_for("auth.login"))

    if not secrets.compare_digest(request.args.get("state", ""), session.pop("oauth_state", "")):
        flash("No pudimos validar el inicio de sesión con Google. Inténtalo otra vez.", "error")
        return redirect(url_for("auth.login"))

    code = request.args.get("code")
    if not code:
        flash("Google no devolvió un código de autorización.", "error")
        return redirect(url_for("auth.login"))

    try:
        token = _exchange_code(code)
        profile = _fetch_profile(token)
    except (urllib.error.URLError, ValueError, KeyError) as exc:
        current_app.logger.warning("Google OAuth falló: %s", exc)
        flash("No se pudo completar el acceso con Google.", "error")
        return redirect(url_for("auth.login"))

    correo = normalize_email(profile.get("email", ""))
    google_id = profile.get("sub", "")
    if not correo or "@" not in correo:
        flash("Google no devolvió un correo válido.", "error")
        return redirect(url_for("auth.login"))

    nombre = profile.get("name") or correo.split("@")[0]
    avatar = profile.get("picture", "")
    user = models.get_user_by_correo(correo) or models.get_user_by_google_id(google_id)

    if user:
        models.link_google_account(user["id"], google_id, avatar)
        user = models.get_user(user["id"])
    else:
        user_id = models.create_user(
            nombre=nombre,
            correo=correo,
            clave_hash="",
            google_id=google_id,
            avatar_url=avatar,
            verificado=1,
            creado_en=now_iso(),
        )
        user = models.get_user(user_id)
        if correo == ADMIN_CORREO:
            ensure_admin()

    login_user(user)
    flash(f"Bienvenido a {user['nombre']}, entraste con Google.", "success")
    return redirect(url_for("web.index"))


def _exchange_code(code):
    payload = urllib.parse.urlencode(
        {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
    ).encode()
    req = urllib.request.Request(
        GOOGLE_TOKEN_ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)["access_token"]


def _fetch_profile(access_token):
    req = urllib.request.Request(
        GOOGLE_USERINFO_ENDPOINT,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)