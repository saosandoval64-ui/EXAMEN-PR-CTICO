import os
from datetime import timedelta

from flask import Flask, url_for

import models
from api import api_bp
from auth import auth_bp, current_user, ensure_admin
from routes import web_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "clave-secreta-de-biblioteca")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.template_filter("image_url")
def image_url_filter(value):
    if not value:
        return None
    if value.startswith(("http://", "https://")):
        return value
    if value.startswith(("uploads/", "portadas/")):
        return url_for("static", filename=value)
    return None


def make_initials(name):
    parts = [p for p in str(name or "").split()]
    if not parts:
        return "?"
    return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()


app.jinja_env.globals["initials"] = make_initials


@app.context_processor
def inject_current_user():
    return {"current_user": current_user()}


app.register_blueprint(web_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp, url_prefix="/api")

models.init_db()
ensure_admin()

os.makedirs(os.path.join(app.root_path, "static", "uploads"), exist_ok=True)

if __name__ == "__main__":
    app.run(debug=True)