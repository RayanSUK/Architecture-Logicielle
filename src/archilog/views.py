import io
import click
import uuid
from tabulate import tabulate
import archilog.models as models
import archilog.services as services



from flask import render_template
from flask import Flask, request,redirect,url_for, flash,send_file
#-------------------------PARTIE FLASK-------------------------------------------------


app = Flask(__name__) #Création de l'application flask

app.secret_key = "supersecretkey"  # Nécessaire pour les messages flash


@app.route("/") #route principal
def index():
    entries = models.get_all_entries()
    return render_template("index.html", entries=entries)


@app.route("/add", methods=["GET", "POST"]) #route pour ajouter une entrée
def add_entry():
    if request.method == "POST":
        name = request.form["name"]
        amount = float(request.form["amount"])
        category = request.form["category"]

        models.create_entry(name, amount, category)
        flash("Entrée ajoutée avec succès !")
        return redirect(url_for("index"))

    return render_template("add.html")


@app.route("/update/<uuid:user_id>", methods=["GET", "POST"]) #route pour mettre à jour
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


@app.route("/delete/<uuid:user_id>") #route pour supprimer une entrée
def delete_entry(user_id):
    models.delete_entry(user_id)
    flash("Entrée supprimée avec succès !")
    return redirect(url_for("index"))


@app.route("/import", methods=["POST"]) #route pour importer un fichier csv
def import_csv():
    file = request.files["csv_file"]
    if file:
        services.import_from_csv(io.StringIO(file.stream.read().decode("utf-8")))
        flash("Importation CSV réussie !")
    return redirect(url_for("index"))


@app.route("/export") #route pour exporter les données en csv
def export_csv():
    file_path = "export.csv"
    services.export_to_csv(file_path)
    flash("Exportation CSV réussie !")
    return send_file(file_path, as_attachment=True, download_name="exported_data.csv", mimetype='text/csv')


#-------------------------Fin de partie Flask---------------------------------



#-------------------------Partie CLI avec click ---------------------------------------

@click.group()
def cli():
    pass


@cli.command()
def init_db():
    models.init_db()


@cli.command()
@click.option("-n", "--name", prompt="Name")
@click.option("-a", "--amount", type=float, prompt="Amount")
@click.option("-c", "--category", prompt="Categorie")
def create(name: str, amount: float, category: str | None):
    models.create_entry(name, amount, category)


@cli.command()
@click.option("--id", required=True, type=click.UUID)
def get(id: uuid.UUID):
    entry = models.get_entry(id)
    if entry :
        table = [[entry.id, entry.name, entry.amount, entry.category]]
        headers = ["ID", "Name", "Amount", "Category"]
        click.echo(tabulate(table, headers=headers, tablefmt="grid"))
    else:
        click.echo("Aucune entrée trouvée pour cet ID.")


@cli.command()
@click.option("--as-csv", is_flag=True, help="Ouput a CSV string.")
def get_all(as_csv: bool):
    entries = models.get_all_entries()

    if as_csv:
        click.echo(services.export_to_csv().getvalue())
    else:
        table = [[entry.id, entry.name, entry.amount, entry.category] for entry in entries]
        headers = ["ID", "Name", "Amount", "Category"]
        click.echo(tabulate(table, headers=headers, tablefmt="grid"))


@cli.command()
@click.argument("csv_file", type=click.File("r"))
def import_csv(csv_file):
    services.import_from_csv(csv_file)


@cli.command()
@click.option("--id", type=click.UUID, required=True)
@click.option("-n", "--name", required=True)
@click.option("-a", "--amount", type=float, required=True)
@click.option("-c", "--category", default=None)
def update(id: uuid.UUID, name: str, amount: float, category: str | None):
    models.update_entry(id, name, amount, category)


@cli.command()
@click.option("--id", required=True, type=click.UUID)
def delete(id: uuid.UUID):
    models.delete_entry(id)

@cli.command()
@click.argument("file_path", type=click.Path())
def export_csv(file_path):
    services.export_to_csv(file_path)
    click.echo(f"Données exportées vers {file_path}")
