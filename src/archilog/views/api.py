import logging

from flask import Flask, Blueprint, jsonify #Prérequis
from spectree import SpecTree, SecurityScheme
from pydantic import BaseModel, Field #Utilisation
from flask_httpauth import HTTPTokenAuth

import archilog.models as models




app = Flask(__name__)
api = Blueprint("api", __name__, url_prefix="/api")

#------------------Authentification avec token sur Swagger-------------
#Validation automatique des donneés entrante, generation doc SWAGGER et securité TOkens
spec = SpecTree(
    "flask",
    security_schemes=[
        SecurityScheme(
            name="bearer_token", #nom de la sécurité
            data={"type":"http","scheme":"bearer"} #token de type Bearer
        )
    ],
    security=[{"bearer_token":[]}] # applique a toute les routes
)
#On veux proteger certaine routes avec des tokens de type Bearer

auth = HTTPTokenAuth(scheme="Bearer")
TOKENS = {
    "admin-token": "admin", #role admin
    "user-token": "user" #role user
}

#vérifiaction
@auth.verify_token
def verify_token(token):
    return TOKENS.get(token)

spec.register(api)

#-------------MODELS------------
class EntryInput(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    amount: float
    category: str | None = None

class EntryOutput(BaseModel):
    id: str
    name: str
    amount: float
    category: str | None

#--------------------Route------------------
@api.route("/")
@auth.login_required  # Exiger la connexion via un token
def index():
    # Exemple d'affichage de données ou d'informations de l'API
    logging.info("Route /api/ a été atteinte")
    return jsonify(message="Bienvenue sur l'API de gestion des entrées ! Vous êtes connecté en tant que {}".format(auth.current_user())), 200

@api.route("/entries", methods=["POST"])
@spec.validate(tags=["api"])
@auth.login_required(role="admin")
def add_entry(json: EntryInput):
    entry_id = models.create_entry(json.name, json.amount, json.category)
    entry = models.get_entry(entry_id)
    return jsonify(entry.to_dict()), 201

