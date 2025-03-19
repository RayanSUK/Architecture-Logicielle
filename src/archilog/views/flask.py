import io
from flask import Flask, request, redirect, url_for, flash, send_file, render_template
import archilog.models as models
import archilog.services as services

# Création de l'application Flask
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Nécessaire pour les messages flash

@app.route("/")  # Route principal
def index():
    entries = models.get_all_entries()
    return render_template("index.html", entries=entries)

@app.route("/add", methods=["GET", "POST"])  # Route pour ajouter une entrée
def add_entry():
    if request.method == "POST":
        name = request.form["name"]
        amount = float(request.form["amount"])
        category = request.form["category"]
        models.create_entry(name, amount, category)
        flash("Entrée ajoutée avec succès !")
        return redirect(url_for("index"))
    return render_template("add.html")

@app.route("/update/<uuid:user_id>", methods=["GET", "POST"])  # Route pour mettre à jour
def update_entry(user_id):
    entry = models.get_entry(user_id)

    if request.method == "POST":
        name = request.form["name"]
        amount = float(request.form["amount"])
        category = request.form["category"]
        models.update_entry(user_id, name, amount, category)
        flash("Entrée mise à jour avec succès !")
        return redirect(url_for("index"))

    return render_template("update.html", entry=entry)

@app.route("/delete/<uuid:user_id>")  # Route pour supprimer une entrée
def delete_entry(user_id):
    models.delete_entry(user_id)
    flash("Entrée supprimée avec succès !")
    return redirect(url_for("index"))

@app.route("/import", methods=["POST"])  # Route pour importer un fichier CSV
def import_csv():
    file = request.files["csv_file"]
    if file:
        services.import_from_csv(io.StringIO(file.stream.read().decode("utf-8")))
        flash("Importation CSV réussie !")
    return redirect(url_for("index"))

@app.route("/export")  # Route pour exporter les données en CSV
def export_csv():
    file_path = "export.csv"
    services.export_to_csv(file_path)
    flash("Exportation CSV réussie !")
    return send_file(file_path, as_attachment=True, download_name="exported_data.csv", mimetype='text/csv')


