import click
import uuid
from tabulate import tabulate
import archilog.models as models
import archilog.services as services

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
    if entry:
        table = [[entry.id, entry.name, entry.amount, entry.category]]
        headers = ["ID", "Name", "Amount", "Category"]
        click.echo(tabulate(table, headers=headers, tablefmt="grid"))
    else:
        click.echo("Aucune entrée trouvée pour cet ID.")

@cli.command()
@click.option("--as-csv", is_flag=True, help="Output a CSV string.")
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
    contenu_csv = services.export_to_csv()  # Récupère la chaîne CSV
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(contenu_csv)
    click.echo(f"Données exportées vers {file_path}")
