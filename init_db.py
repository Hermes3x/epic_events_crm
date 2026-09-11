"""Amorçage de la base : données indispensables au premier démarrage."""

import getpass

from sqlalchemy import select

from epicevents.database import Session
from epicevents.models import Collaborateur, Role
from epicevents.securite import hacher_mot_de_passe



ROLES = ["gestion", "commercial", "support"]


def creer_roles(session) -> None:
    """Crée les trois rôles s'ils n'existent pas encore."""
    crees = 0
    for nom in ROLES:
        existant = session.scalar(select(Role).where(Role.nom == nom))
        if existant is None:
            session.add(Role(nom=nom))
            crees += 1
    session.commit()
    print(f"{crees} rôle(s) créé(s), {len(ROLES) - crees} déjà présent(s).")


def creer_premier_gestionnaire(session) -> None:
    """Crée l'utilisateur 0, uniquement si aucun collaborateur n'existe."""
    if session.scalar(select(Collaborateur)) is not None:
        print("Un collaborateur existe déjà : aucun compte créé.")
        return

    numero_employe = input("Votre n° d'employé : ")
    nom_complet = input("Nom et prénom : ")
    while True:
        email = input("Votre email : ")
        confirmation_email = input("Confirmez votre email : ")
        if email == confirmation_email:
            break
        print("Les emails ne correspondent pas. Recommencez.")

    while True:
        mot_de_passe = getpass.getpass("Mot de passe : ")
        confirmation = getpass.getpass("Confirmez le mot de passe : ")
        if mot_de_passe == confirmation:
            break
        print("Les mots de passe ne correspondent pas. Recommencez.")

    role_gestion = session.scalar(select(Role).where(Role.nom == "gestion"))

    gestionnaire = Collaborateur(
        numero_employe=numero_employe,
        nom_complet=nom_complet,
        email=email,
        mot_de_passe_hache=hacher_mot_de_passe(mot_de_passe),
        role=role_gestion,
    )
    session.add(gestionnaire)
    session.commit()
    print(f"Compte gestion créé pour {nom_complet}.")



def main() -> None:
    with Session() as session:
        creer_roles(session)
        creer_premier_gestionnaire(session)


if __name__ == "__main__":
    main()

