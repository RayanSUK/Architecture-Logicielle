from flask import Flask #Prérequis
from spectree import SpecTree, SecurityScheme
from pydantic import BaseModel, Field #Utilisation
from flask_httpauth import HTTPTokenAuth

from src.archilog.views.web_ui import auth

app = Flask(__name__)
spec = SpecTree("Flask") #Validation automatique des donneés entrante, generation doc SWAGGER et securité TOkens


#------------------Authentification avec token sur Swagger-------------
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
TOKENS={
    "admin-token":"admin", #role admin
    "user-token":"user" #role user
}

#vérifiaction
@auth.verify_token
def verify_token(token):
    return TOKENS.get(token)

#-------------MODELS------------
class UserData(BaseModel): #le model
    name: str = Field(min_length=2,max_lenght=40)
    amount: int = Field(gt=0, lt=150)
    category: str = Field(min_length=2, max_length=40)

@app.route("/api/users", methods=["POST"])
@spec.validate(tags=["api"])
def user_profil(json: UserData):
    return {"username":json.name}

