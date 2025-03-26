import io
from flask import Flask, request, redirect, url_for, flash, send_file, render_template, Blueprint, abort
import archilog.models as models
import archilog.services as services



#-----------------------partie WTF form---------------------
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField
from wtforms.validators import DataRequired, NumberRange, Length

class EntryForm(FlaskForm):
    name = StringField('Nom', validators=[DataRequired(), Length(min=3, max=50)])
    amount = DecimalField('Montant', validators=[DataRequired(), NumberRange(min=0.01, message="Le montant doit être supérieur à 0")])
    category = StringField('Catégorie', validators=[DataRequired(), Length(min=1, max=50)])
#-----------------------------------------------------------

web_ui = Blueprint("web_ui", __name__, url_prefix="/")

# Création de l'application Flask
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Nécessaire pour les messages flash

@web_ui.route("/")  # Route principal
def index():
    entries = models.get_all_entries()
    return render_template("index.html", entries=entries)

@web_ui.route("/add", methods=["GET", "POST"])  # Route pour ajouter une entrée
def add_entry():
    form = EntryForm() #Pour le wtf form on à tout changer
    if form.validate_on_submit():
        name = form.name.data
        amount = form.amount.data
        category = form.category.data
        models.create_entry(name, amount, category)  # Enregistre l'entrée
        flash("Entrée ajoutée avec succès !")
        return redirect(url_for("web_ui.index"))

    return render_template("add.html", form=form)  # Renvoie le formulaire à afficher

@web_ui.route("/update/<uuid:user_id>", methods=["GET", "POST"])  # Route pour mettre à jour
def update_entry(user_id):
    entry = models.get_entry(user_id)
    form = EntryForm(obj=entry) #préremplit le fomrulaire avec les données
    if form.validate_on_submit():
        name = form.name.data
        amount = form.amount.data
        category = form.category.data
        models.update_entry(user_id, name, amount, category)  # Met à jour l'entrée
        flash("Entrée mise à jour avec succès !")
        return redirect(url_for("web_ui.index"))

    return render_template("update.html", form=form)  # Renvoie le formulaire avec les données existantes

@web_ui.route("/delete/<uuid:user_id>")  # Route pour supprimer une entrée
def delete_entry(user_id):
    models.delete_entry(user_id)
    flash("Entrée supprimée avec succès !")
    return redirect(url_for("web_ui.index"))

@web_ui.route("/import", methods=["POST"])  # Route pour importer un fichier CSV
def import_csv():
    file = request.files["csv_file"]
    if file:
        services.import_from_csv(io.StringIO(file.stream.read().decode("utf-8")))
        flash("Importation CSV réussie !")
    return redirect(url_for("web_ui.index"))

@web_ui.route("/export")  # Route pour exporter les données en CSV
def export_csv():
    file_path = "export.csv"
    services.export_to_csv(file_path)
    flash("Exportation CSV réussie !")
    return redirect(url_for("web_ui.index"))


@web_ui.get("/users/create") #Pour tester ya juste a rajouter cette route
def users_create_form():
    abort(500)

@app.errorhandler(500)
def handle_internal_error(error):
    flash("Erreur interne du serveur", "error")
    return redirect(url_for("web_ui.index"))
