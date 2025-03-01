import csv
import sqlalchemy
import uuid
import sqlalchemy as sa
from sqlalchemy import Column, create_engine,MetaData,Table,Uuid,String,Float
from dataclasses import dataclass



engine = create_engine("sqlite:///data.db", echo=False)
metadata = MetaData() #stocke les métadonnées dans la bd
#créer la table users dans la bd
tableTest = Table(
    "users",
    metadata,
    Column("id", Uuid, primary_key=True, default=uuid.uuid4),
    Column("name", String, nullable=False),
    Column("amount", Float, nullable=False),
    Column("category",String, nullable=False)
)


def init_db():
    """initialise la base de données en créant la table"""
    metadata.create_all(engine)
    print("La base de donne a bien ete creer") #pas d'accent dans les phrases car le terminal ne reconnait pas


@dataclass
class Entry:
    """Modèle représenant une entrée de la table"""
    id: uuid.UUID
    name: str
    amount: float
    category: str | None

    @classmethod
    def from_db(cls, id: uuid.UUID, name: str, amount: float, category: str | None):
        return cls(id, name, amount, category)



def create_entry(name: str, amount: float, category: str | None = None) -> None:
    """Insère une nouvelle entrée dna sla bd"""
    stmt = tableTest.insert().values(id=uuid.uuid4(),name=name, amount=amount, category=category)
    with engine.begin() as con:
        con.execute(stmt)

def get_entry(id: uuid.UUID) -> Entry:
    """Récupère une entrée par son ID"""
    stmt = tableTest.select().where(tableTest.c.id == id)
    with engine.begin() as con:  #avec engine.connect il faut faire le commit manuellement alors quee avec begin non
        result = con.execute(stmt).fetchone()
        if result:
            return Entry.from_db(*result)
        else:
            raise Exception("Entre non trouve")


def get_all_entries() -> list[Entry]:
    """Récupère toute les entrées de la bd"""
    stmt = tableTest.select()
    with engine.begin() as con:
        results = con.execute(stmt).fetchall()
        return [Entry.from_db(*r) for r in results]



def update_entry(id: uuid.UUID, name: str, amount: float, category: str | None) -> None:
    """Met à jour une entrée de la bd (nécessite son id)"""
    stmt = tableTest.update().where(tableTest.c.id == id).values(name=name, amount=amount, category=category)
    with engine.begin() as con:
        con.execute(stmt)


def delete_entry(id: uuid.UUID) -> None:
    """Supprime une entrée de la bd (nécessite son id)"""
    stmt = tableTest.delete().where(tableTest.c.id == id)
    with engine.begin() as con:
        con.execute(stmt)


def import_from_csv(file_path: str) -> None:
    """Importe des données depuis un fichier csv"""
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')  # Prend en compte le délimiteur ;
        next(reader)  # Ignorer l'en-tête

        for row in reader:
            id = uuid.UUID(row[0])  # Utiliser UUID correctement
            name = row[1]
            amount = float(row[2])
            category = row[3]

            stmt = tableTest.insert().values(id=id, name=name, amount=amount, category=category)
            with engine.begin() as con:
                con.execute(stmt)


    print(f"Importation terminee depuis {file_path}")



def export_to_csv(file_path: str) -> None:
    """Exporte les données de la base vers un fichier CSV (nécessite un chemin de destination dans un fichier csv existant)"""
    stmt = tableTest.select()
    with engine.begin() as con:
        results = con.execute(stmt).fetchall()

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Name", "Amount", "Category"])  # Écrire l'en-tête
        for row in results:
            writer.writerow([row.id, row.name, row.amount, row.category])  # Écrire les données
    print(f"Les donnees ont ete exportees vers {file_path}")