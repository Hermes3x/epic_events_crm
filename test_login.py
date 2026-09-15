"""Test manuel de la chaîne d'authentification complète.

Usage :
    python test_login.py

Simule un login (email + mot de passe), enregistre le jeton, puis vérifie
que utilisateur_courant() retrouve bien le collaborateur connecté.
"""

from getpass import getpass

from epicevents.auth import (
    authentifier,
    creer_jeton,
    sauvegarder_jeton,
    utilisateur_courant,
)
from epicevents.database import Session


def main() -> None:
    email = input("Email : ")
    mot_de_passe = getpass("Mot de passe : ")

    with Session() as session:
        collaborateur = authentifier(session, email, mot_de_passe)
        if collaborateur is None:
            print("Identifiants invalides.")
            return

        sauvegarder_jeton(creer_jeton(collaborateur))
        print("Jeton enregistre.")

        print("Utilisateur courant :", utilisateur_courant(session))


if __name__ == "__main__":
    main()
