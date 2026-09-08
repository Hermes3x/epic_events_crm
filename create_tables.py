"""Crée dans la base toutes les tables déclarées par les modèles.

Usage :
    python create_tables.py

Le script est idempotent : relancé, il ne recrée pas une table existante.
"""

from epicevents.database import engine
from epicevents.models import Base


def main() -> None:
    Base.metadata.create_all(engine)
    tables = ", ".join(sorted(Base.metadata.tables))
    print("Tables declarees par les modeles :", tables)


if __name__ == "__main__":
    main()
