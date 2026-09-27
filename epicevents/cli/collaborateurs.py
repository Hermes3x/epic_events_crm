"""Commandes sur les collaborateurs."""

import click
from rich.console import Console
from rich.table import Table
from sqlalchemy import select

from epicevents.auth import exiger_connexion
from epicevents.database import Session
from epicevents.models import Collaborateur, Role
from epicevents.repositories.collaborateurs import lister_collaborateurs
from epicevents.services.collaborateurs import (
    creer_collaborateur,
    modifier_collaborateur,
    supprimer_collaborateur,
)

console = Console()

ROLES_VALIDES = ("gestion", "commercial", "support")


def _trouver_role(session, nom: str) -> Role:
    """Retourne le rôle portant ce nom, ou lève une erreur explicite."""
    role = session.scalar(select(Role).where(Role.nom == nom))
    if role is None:
        raise ValueError(
            f"Rôle inconnu : '{nom}'. Valeurs possibles : {', '.join(ROLES_VALIDES)}."
        )
    return role


def _trouver_collaborateur(session, collaborateur_id: int) -> Collaborateur:
    """Retourne le collaborateur portant cet id, ou lève une erreur explicite."""
    cible = session.get(Collaborateur, collaborateur_id)
    if cible is None:
        raise ValueError(f"Aucun collaborateur avec l'id {collaborateur_id}.")
    return cible


@click.group()
def collaborateurs() -> None:
    """Consultation et gestion des collaborateurs."""


@collaborateurs.command(name="lister")
def lister() -> None:
    """Affiche tous les collaborateurs."""
    with Session() as session:
        exiger_connexion(session)
        resultats = lister_collaborateurs(session)

        tableau = Table(title="Collaborateurs")
        tableau.add_column("Id", justify="right")
        tableau.add_column("N° employé")
        tableau.add_column("Nom complet", max_width=22, no_wrap=True)
        tableau.add_column("Email", max_width=26, no_wrap=True)
        tableau.add_column("Rôle")
        tableau.add_column("Clients", justify="right")
        tableau.add_column("Évènements", justify="right")

        for collaborateur in resultats:
            tableau.add_row(
                str(collaborateur.id),
                collaborateur.numero_employe,
                collaborateur.nom_complet,
                collaborateur.email,
                collaborateur.role.nom,
                str(len(collaborateur.clients)),
                str(len(collaborateur.evenements)),
            )

        console.print(tableau)


@collaborateurs.command(name="creer")
@click.option("--numero", prompt="N° d'employé", help="Numéro d'employé (unique).")
@click.option("--nom", prompt="Nom complet", help="Nom et prénom.")
@click.option("--email", prompt="Email", help="Adresse email (unique).")
@click.option("--role", "role_nom", prompt="Rôle (gestion/commercial/support)",
              type=click.Choice(ROLES_VALIDES), help="Département du collaborateur.")
@click.option("--mot-de-passe", prompt="Mot de passe", hide_input=True,
              confirmation_prompt=True, help="Mot de passe (sera haché).")
def creer(numero: str, nom: str, email: str, role_nom: str, mot_de_passe: str) -> None:
    """Crée un collaborateur (réservé à l'équipe de gestion)."""
    with Session() as session:
        moi = exiger_connexion(session)
        role = _trouver_role(session, role_nom)

        nouveau = creer_collaborateur(
            session, moi, role, mot_de_passe,
            numero_employe=numero, nom_complet=nom, email=email,
        )
        click.echo(
            f"Collaborateur créé : {nouveau.nom_complet} "
            f"(id {nouveau.id}, {nouveau.role.nom})"
        )


@collaborateurs.command(name="modifier")
@click.argument("collaborateur_id", type=int)
@click.option("--numero", help="Nouveau numéro d'employé.")
@click.option("--nom", help="Nouveau nom complet.")
@click.option("--email", help="Nouvelle adresse email.")
@click.option("--role", "role_nom", type=click.Choice(ROLES_VALIDES),
              help="Nouveau département.")
def modifier(
    collaborateur_id: int, numero: str | None, nom: str | None,
    email: str | None, role_nom: str | None,
) -> None:
    """Modifie un collaborateur, département inclus (équipe de gestion)."""
    with Session() as session:
        moi = exiger_connexion(session)
        cible = _trouver_collaborateur(session, collaborateur_id)

        champs = {}
        if numero is not None:
            champs["numero_employe"] = numero
        if nom is not None:
            champs["nom_complet"] = nom
        if email is not None:
            champs["email"] = email
        if role_nom is not None:
            champs["role"] = _trouver_role(session, role_nom)

        if not champs:
            raise ValueError("Aucun champ à modifier. Voir --help pour les options.")

        modifier_collaborateur(session, moi, cible, **champs)
        click.echo(
            f"Collaborateur modifié : {cible.nom_complet} "
            f"(id {cible.id}, {cible.role.nom})"
        )


@collaborateurs.command(name="supprimer")
@click.argument("collaborateur_id", type=int)
@click.confirmation_option(prompt="Confirmez-vous la suppression de ce collaborateur ?")
def supprimer(collaborateur_id: int) -> None:
    """Supprime un collaborateur (réservé à l'équipe de gestion)."""
    with Session() as session:
        moi = exiger_connexion(session)
        cible = _trouver_collaborateur(session, collaborateur_id)

        if cible.id == moi.id:
            raise ValueError("Vous ne pouvez pas supprimer votre propre compte.")

        nom = cible.nom_complet
        supprimer_collaborateur(session, moi, cible)
        click.echo(f"Collaborateur supprimé : {nom}")
