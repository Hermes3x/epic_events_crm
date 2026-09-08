"""Supprime puis recrée toutes les tables de l'application.

Usage :
    python reset_tables.py

ATTENTION : toutes les données des tables du CRM sont perdues.
À n'utiliser qu'en phase de conception des modèles.

Seules les tables déclarées dans les modèles sont concernées :
aucune autre base ni aucune autre table n'est touchée.
"""

from epicevents.database import engine
from epicevents.models import Base


def main() -> None:
    tables = ", ".join(sorted(Base.metadata.tables))
    print("Tables concernees :", tables)
    reponse = input("Supprimer et recreer ces tables ? (oui/non) : ")
    if reponse.strip().lower() != "oui":
        print("Annule.")
        return

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Tables recreees :", tables)


if __name__ == "__main__":
    main()
