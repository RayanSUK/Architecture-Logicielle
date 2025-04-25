import uuid
from sqlalchemy import Column, create_engine, MetaData, Table, String, Float
from dataclasses import dataclass

from archilog import config

engine = create_engine(config.DATABASE_URL, echo=False)
metadata = MetaData()

tableTest = Table(
    "users",
    metadata,
    Column("id", String, primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("name", String, nullable=False),
    Column("amount", Float, nullable=False),
    Column("category", String, nullable=True)
)


def init_db():
    """initialise la base de données en créant la table"""
    metadata.create_all(engine)
    print("La base de donne a bien ete creer")


@dataclass
class Entry:
    """Modèle représentant une entrée de la table"""
    id: str  # <-- changé de uuid.UUID à str
    name: str
    amount: float
    category: str | None

    @classmethod
    def from_db(cls, id: str, name: str, amount: float, category: str | None):
        return cls(id, name, amount, category)


def create_entry(name: str, amount: float, category: str | None = None) -> None:
    """Insère une nouvelle entrée dans la bd"""
    stmt = tableTest.insert().values(id=str(uuid.uuid4()), name=name, amount=amount, category=category)
    with engine.begin() as con:
        con.execute(stmt)


def get_entry(id: str | uuid.UUID) -> Entry:
    """Récupère une entrée par son ID"""
    stmt = tableTest.select().where(tableTest.c.id == str(id))  # converti en str
    with engine.begin() as con:
        result = con.execute(stmt).fetchone()
        if result:
            return Entry.from_db(*result)
        else:
            raise Exception("Entre non trouve")


def get_all_entries() -> list[Entry]:
    """Récupère toutes les entrées de la bd"""
    stmt = tableTest.select()
    with engine.begin() as con:
        results = con.execute(stmt).fetchall()
        return [Entry.from_db(*r) for r in results]


def update_entry(id: str | uuid.UUID, name: str, amount: float, category: str | None) -> None:
    """Met à jour une entrée de la bd (nécessite son id)"""
    stmt = tableTest.update().where(tableTest.c.id == str(id)).values(name=name, amount=amount, category=category)
    with engine.begin() as con:
        con.execute(stmt)


def delete_entry(id: str | uuid.UUID) -> None:
    """Supprime une entrée de la bd (nécessite son id)"""
    stmt = tableTest.delete().where(tableTest.c.id == str(id))
    with engine.begin() as con:
        con.execute(stmt)
