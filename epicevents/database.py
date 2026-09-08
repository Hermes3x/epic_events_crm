"""Configuration de la connexion à la base de données.

Les identifiants sont lus dans le fichier .env, jamais écrits en dur ici.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(DATABASE_URL)

# Fabrique de sessions : chaque session est une conversation avec la base.
Session = sessionmaker(bind=engine)
