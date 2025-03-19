import os
from flask import Flask
from dataclasses import dataclass

@dataclass
class Config:
    DATABASE_URL: str
    DEBUG: bool

# Charger les variables d'environnement
config = Config(
    DATABASE_URL=os.getenv("ARCHILOG_DATABASE_URL", ""),
    DEBUG=os.getenv("ARCHILOG_DEBUG", "False") == "True"
)

# Créer l'application Flask
def create_app():
    app = Flask(__name__)

    # Charger la configuration
    app.config.from_mapping(
        DATABASE_URL=config.DATABASE_URL,
        DEBUG=config.DEBUG,
        SECRET_KEY=os.getenv("ARCHILOG_FLASK_SECRET_KEY", "defaultsecret")
    )

    # Enregistrer les Blueprints
    from archilog.views import api, web_ui
    app.register_blueprint(api)
    app.register_blueprint(web_ui)

    return app
