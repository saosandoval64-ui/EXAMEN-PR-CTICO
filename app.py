from flask import Flask

import models
from api import api_bp
from routes import web_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = "clave-secreta-de-biblioteca"
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.register_blueprint(web_bp)
app.register_blueprint(api_bp, url_prefix="/api")

models.init_db()

if __name__ == "__main__":
    app.run(debug=True)