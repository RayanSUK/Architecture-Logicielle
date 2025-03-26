import os
from dataclasses import dataclass
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("archilog.log"),
        logging.StreamHandler()
]
)


@dataclass
class Config:
    DATABASE_URL: str
    DEBUG: bool

# Charger les variables d'environnement
database_url = os.getenv('ARCHILOG_DATABASE_URL')
if not database_url:
    raise ValueError('La variable d envirronement nest pas définie')

debug = os.getenv('ARCHILOG_DEBUG',"False") == "True"

config = Config(DATABASE_URL=database_url,DEBUG=debug)


