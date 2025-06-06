import io
from flask import Flask, request, redirect, url_for, flash, send_file, render_template, Blueprint, abort
import archilog.models as models
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import archilog.services as services
import logging

from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField
from wtforms.validators import DataRequired, NumberRange, Length

web_ui = Blueprint("web_ui", __name__, url_prefix="/")
#-----------------------partie authentifiaction---------------------

app = Flask(__name__)
auth = HTTPBasicAuth()
users = {
    "admin": {
        "password": generate_password_hash("admin"),
        "role": "admin"
    },
    "user": {
        "password": generate_password_hash("user"),
        "role": "user"
    }
}

app.secret_key = "supersecretkey"  # Nécessaire pour les messages flash

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users[username]["password"], password):
        return users[username]["role"]  # Retourne le rôle de l'utilisateur
    return None

# Fonction pour obtenir le rôle de l'utilisateur
@auth.get_user_roles
def get_user_roles(username):
    user = users.get(username)
    if user:
        return user["role"]
    return None
#-----------------------partie WTF form---------------------


class EntryForm(FlaskForm):
    name = StringField('Nom', validators=[DataRequired(), Length(min=3, max=50)])
    amount = DecimalField('Montant', validators=[DataRequired(), NumberRange(min=0.01, message="Le montant doit être supérieur à 0")])
    category = StringField('Catégorie', validators=[DataRequired(), Length(min=1, max=50)])
#-----------------------------------------------------------





@web_ui.route("/")  # Route principal
@auth.login_required  # Exiger une connexion pour afficher la page
def index():
    entries = models.get_all_entries()
    logging.info("Affichage des entrées avec succès.")
    return f"Hello, {auth.current_user()}!"+ render_template("index.html", entries=entries) 


    
@web_ui.route("/add", methods=["GET", "POST"])  # Route pour ajouter une entrée
@auth.login_required(role="admin")  # Seuls les admins peuvent ajouter des entrées
def add_entry():
    form = EntryForm()  # Pour le WTF form, on a tout changé
    if form.validate_on_submit():
        name = form.name.data
        amount = form.amount.data
        category = form.category.data
        try:
            models.create_entry(name, amount, category)  # Enregistre l'entrée
            flash("Entrée ajoutée avec succès !")
            logging.info(f"Entrée ajoutée : {name}, {amount}, {category}")
            return redirect(url_for("web_ui.index"))
        except Exception as e:
            logging.exception("Erreur lors de l'ajout de l'entrée.")
            flash("Une erreur est survenue lors de l'ajout de l'entrée.", "error")
    return render_template("add.html", form=form)  # Renvoie le formulaire à afficher

@web_ui.route("/update/<uuid:user_id>", methods=["GET", "POST"])  # Route pour mettre à jour
@auth.login_required(role="admin")
def update_entry(user_id):
    try:
        entry = models.get_entry(user_id)
        form = EntryForm(obj=entry)  # Préremplit le formulaire avec les données
        if form.validate_on_submit():
            name = form.name.data
            amount = form.amount.data
            category = form.category.data
            models.update_entry(user_id, name, amount, category)  # Met à jour l'entrée
            flash("Entrée mise à jour avec succès !")
            logging.info(f"Entrée mise à jour : {name}, {amount}, {category}")
            return redirect(url_for("web_ui.index"))
        return render_template("update.html", form=form)  # Renvoie le formulaire avec les données existantes
    except Exception as e:
        logging.exception(f"Erreur lors de la mise à jour de l'entrée avec l'ID {user_id}.")
        flash("Une erreur est survenue lors de la mise à jour de l'entrée.", "error")
        return redirect(url_for("web_ui.index"))

@web_ui.route("/delete/<uuid:user_id>")  # Route pour supprimer une entrée
@auth.login_required(role="admin")
def delete_entry(user_id):
    try:
        models.delete_entry(user_id)
        flash("Entrée supprimée avec succès !")
        logging.info(f"Entrée supprimée : ID {user_id}")
        return redirect(url_for("web_ui.index"))
    except Exception as e:
        logging.exception(f"Erreur lors de la suppression de l'entrée avec l'ID {user_id}.")
        flash("Une erreur est survenue lors de la suppression de l'entrée.", "error")
        return redirect(url_for("web_ui.index"))

@web_ui.route("/import", methods=["POST"])  # Route pour importer un fichier CSV
@auth.login_required(role="admin")
def import_csv():
    try:
        file = request.files["csv_file"]
        if file:
            services.import_from_csv(io.StringIO(file.stream.read().decode("utf-8")))
            flash("Importation CSV réussie !")
            logging.info("Fichier CSV importé avec succès.")
        return redirect(url_for("web_ui.index"))
    except Exception as e:
        logging.exception("Erreur lors de l'importation du fichier CSV.")
        flash("Une erreur est survenue lors de l'importation du fichier CSV.", "error")
        return redirect(url_for("web_ui.index"))

@web_ui.route("/export")  # Route pour exporter les données en CSV
def export_csv():
    try:
        # Appeler la fonction export_to_csv pour obtenir le CSV généré en mémoire
        csv_data = services.export_to_csv()  # Pas besoin de paramètre ici

        # Convertir le texte CSV en un objet BytesIO pour l'envoyer avec send_file
        return send_file(
            io.BytesIO(csv_data.encode('utf-8')),  # Convertir en bytes
            mimetype="text/csv",
            as_attachment=True,
            download_name="export.csv"  # Nom du fichier téléchargé
        )
    except Exception as e:
        logging.exception("Erreur lors de l'exportation des données en CSV.")
        flash("Une erreur est survenue lors de l'exportation.", "error")
        return redirect(url_for("web_ui.index"))

@web_ui.errorhandler(500)
def handle_internal_error(error):
    flash("Erreur interne du serveur", "error")
    logging.exception(error)
    return redirect(url_for("web_ui.index"))


# Gestionnaire d'erreurs 404 (page introuvable)
def register_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(error):
        flash("Page non trouvée", "error")
        logging.error(f"Erreur 404: {error} - Page introuvable.")  # Logue l'erreur 404
        return redirect(url_for('web_ui.index'))

# Route de test pour simuler une erreur 500
@web_ui.get("/users/create")
def users_create_form():
    abort(500)  # Force une erreur 500 pour tester le gestionnaire
    return render_template("index.html")

