import csv
import dataclasses
import io

from archilog.models import create_entry, get_all_entries, Entry


def export_to_csv():
    """Exporte toutes les entrées de la base de données vers un fichier CSV en mémoire."""

    # Créer un buffer en mémoire pour stocker le CSV
    csv_buffer = io.StringIO()

    # Créer un writer pour écrire dans le buffer en mémoire
    csv_writer = csv.writer(csv_buffer)

    # Écrire l'en-tête du CSV (les colonnes)
    csv_writer.writerow(["id", "name", "amount", "category"])

    # Écrire les données de la base de données dans le CSV
    for entry in get_all_entries():
        csv_writer.writerow([entry.id, entry.name, entry.amount, entry.category])

    # Remettre le curseur au début du buffer pour la lecture
    csv_buffer.seek(0)

    # Retourner le buffer sous forme de texte
    return csv_buffer.getvalue()


def import_from_csv(csv_file: io.StringIO) -> None:
    """Importe des entrées depuis un fichier CSV et les ajoute à la base de données.

    Args:
        csv_file (io.StringIO): texte contenant les données CSV."""
    csv_reader = csv.DictReader(
        csv_file,
        fieldnames=[f.name for f in dataclasses.fields(Entry)],
        delimiter=","
    )

    next(csv_reader)  # Ignorer l'en-tête

    for row in csv_reader:
        amount = float(row["amount"]) if row["amount"] and row["amount"].strip() else 0.0 #permet d'éviter les erreurs et garantir que la valeur amount est toujours un float valide

        create_entry(
            name=row["name"].strip() if row["name"] else "Nom inconnu",
            amount=amount,
            category=row["category"].strip() if row["category"] else "Non spécifié",
        )
