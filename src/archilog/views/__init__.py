from flask import Flask
from archilog.views.web_ui import web_ui
def create_app():
    app = Flask(__name__)

    # Charger la configuration
    app.config.from_prefixed_env(prefix='ARCHILOG_FLASK')

    #Enregistrer les bluePRints
    app.register_blueprint(web_ui)
    return app
