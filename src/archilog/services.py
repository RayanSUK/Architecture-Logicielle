import csv
import dataclasses
import io

from archilog.models import create_entry, get_all_entries, Entry


def export_to_csv(file_path: str):
    """Exporte toutes les entrées de la base de données vers un fichier CSV.
    Args:
        file_path (str): Chemin du fichier CSV où enregistrer les données."""
    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.DictWriter(
            csvfile, fieldnames=[f.name for f in dataclasses.fields(Entry)]
        )
        csv_writer.writeheader()
        for todo in get_all_entries():
            csv_writer.writerow(dataclasses.asdict(todo))


def import_from_csv(csv_file: io.StringIO) -> None:
    """Importe des entrées depuis un fichier CSV et les ajoute à la base de données.

    Args:
        csv_file (io.StringIO): texte contenant les données CSV."""
    csv_reader = csv.DictReader(
        csv_file,
        fieldnames=[f.name for f in dataclasses.fields(Entry)],
        delimiter=";"
    )

    next(csv_reader)  # Ignorer l'en-tête

    for row in csv_reader:
        amount = float(row["amount"]) if row["amount"] and row["amount"].strip() else 0.0 #permet d'éviter les erreurs et garantir que la valeur amount est toujours un float valide

        create_entry(
            name=row["name"].strip() if row["name"] else "Nom inconnu",
            amount=amount,
            category=row["category"].strip() if row["category"] else "Non spécifié",
        )
