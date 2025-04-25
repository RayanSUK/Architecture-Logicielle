
import logging
import uuid
from typing import Optional
from uuid import UUID

from flask import Flask, Blueprint, jsonify,Response
from spectree import SpecTree, SecurityScheme , BaseFile
from pydantic import BaseModel, Field
from flask_httpauth import HTTPTokenAuth
import archilog.models as models
import io

from archilog import services

api = Blueprint("api", __name__, url_prefix="/api")
auth = HTTPTokenAuth(scheme="Bearer")
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
    security=[{"bearer_token":  []}] # applique a toute les routes
)
#On veux proteger certaine routes avec des tokens de type Bearer


TOKENS = {
    "admin-token": "admin", #role admin
    "user-token": "user" #role user
}

#vérifiaction
@auth.verify_token
def verify_token(token):
    return TOKENS.get(token)

@auth.get_user_roles
def get_user_roles(user):
    return user



#-------------MODELS------------
class EntryInput(BaseModel):
    name: str = Field(min_length=2, max_length=100, description="Nom de l'entrée")
    amount: float = Field(gt=0, description="Montant de l'entrée")
    category: Optional[str] = Field(default=None, description="Catégorie optionnelle")


class File(BaseModel):
    file: BaseFile


#--------------------Route------------------
@api.route("/")  # Exiger la connexion via un token
@auth.login_required
def index():
    # Exemple d'affichage de données ou d'informations de l'API
    logging.info("Route /api/ a été atteinte")
    return jsonify(message="Bienvenue sur l'API de gestion des entrées ! Vous êtes connecté en tant que {}".format(auth.current_user())), 200

@api.route("/user", methods=["POST"])
@auth.login_required(role="admin")
@spec.validate(json=EntryInput, tags=["user"])
def add_entry(json: EntryInput):
    # Extraction des données depuis le modèle validé
    name = json.name
    amount = json.amount
    category = json.category

    # Appel à la fonction create_entry pour insérer dans la BD
    models.create_entry(name, amount, category)

    # Réponse de succès
    return {"message": "Création réussie de l'entrée!"}, 201


#CA MARCHE
@api.route("/user", methods=["GET"])
@auth.login_required
@spec.validate(tags=["user"])
def get_all():
    entries = models.get_all_entries()
    return jsonify([entry.__dict__ for entry in entries])


#CA MARCHE
@api.route("/user/<uuid:id>", methods=["GET"])
@auth.login_required(role="admin")
@spec.validate(tags=["user"])
def get_one(id):
    entry = models.get_entry(id)
    return jsonify(entry.__dict__)


@api.route("/user/<uuid:id>", methods=["PUT"])
@auth.login_required(role="admin")
@spec.validate(json=EntryInput, tags=["user"])
def update_entry(id:UUID, json: EntryInput):
    models.update_entry(id, json.name, json.amount, json.category)
    return {"message": "Mise à jour réussie"}


# CA MARCHE
@api.route("/user/<uuid:id>", methods=["DELETE"])
@auth.login_required(role="admin")
@spec.validate( tags=["user"])
def delete_entry(id:uuid.UUID):
    models.delete_entry(id)
    return {"message": "Suppression réussie"}



#CA MARCHE
@api.route("/user/import", methods=["POST"])
@spec.validate(tags=["user"])
@auth.login_required(role="admin")
def import_from_csv(form: File):
    filestream = io.StringIO(form.file.read().decode("utf-8"))
    services.import_from_csv(filestream)
    return jsonify({"message":"CSV importer avec succés"}),201

#CA MARCHE
@api.route("/user/export", methods=["GET"])
@auth.login_required
@spec.validate(tags=["user"])
def export_csv():
    try:
        # Appeler la fonction export_to_csv pour générer les données CSV en mémoire
        csv_data = services.export_to_csv()

        # Retourner la réponse avec le contenu CSV
        return Response(
            csv_data,  # Données CSV générées
            content_type="text/csv",  # Type MIME pour CSV
            headers={"Content-Disposition": "attachment;filename=export.csv"}
            # Indiquer un téléchargement avec un nom de fichier
        )
    except Exception as e:
        logging.exception("Erreur lors de l'exportation des données en CSV via l'API.")
        return {"message": "Une erreur est survenue lors de l'exportation."}, 500