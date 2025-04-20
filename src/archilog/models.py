import uuid

from sqlalchemy import Column, create_engine,MetaData,Table,Uuid,String,Float
from dataclasses import dataclass

from archilog import config


engine = create_engine(config.DATABASE_URL, echo=False)
metadata = MetaData() #stocke les métadonnées dans la bd
#créer la table users dans la bd
tableTest = Table(
    "users",
    metadata,
    Column("id", Uuid, primary_key=True, default=uuid.uuid4),
    Column("name", String, nullable=False),
    Column("amount", Float, nullable=False),
    Column("category",String, nullable=True)
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


