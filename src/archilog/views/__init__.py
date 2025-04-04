from flask import Flask
from archilog.views.web_ui import web_ui
from archilog.views.api import api,spec
def create_app():
    app = Flask(__name__)

    # Charger la configuration
    app.config.from_prefixed_env(prefix='ARCHILOG_FLASK')

    #Enregistrer les bluePRints
    app.register_blueprint(web_ui)
    app.register_blueprint(api) #nouveau

    spec.register(app) #important pour Swagger

    return app
