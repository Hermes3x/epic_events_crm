import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv()

print("Hôte :", os.getenv("DB_HOST"))
print("Port :", os.getenv("DB_PORT"))
print("Nom :", os.getenv("DB_NAME"))
print("Utilisateur :", os.getenv("DB_USER"))
print("Mot de passe :", len(os.getenv("DB_PASSWORD")), "caractères")

url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(url)

with engine.connect() as connection:
    resultat = connection.execute(text("SELECT version();"))
    print("Connecté à :", resultat.scalar())
