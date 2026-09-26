"""Commandes de connexion et de déconnexion."""

import click

from epicevents.auth import (
    FICHIER_JETON,
    authentifier,
    creer_jeton,
    sauvegarder_jeton,
)
from epicevents.database import Session



@click.group()
def auth() -> None:
    """Connexion et déconnexion."""


@auth.command()
def logout() -> None:
    """Supprime le jeton enregistré et déconnecte l'utilisateur."""
    FICHIER_JETON.unlink(missing_ok=True)
    click.echo("Déconnecté.")


@auth.command()
def login() -> None:
    """Crée le jeton, l'enregistre et connecte l'utilisateur."""
    with Session() as session:

        email = click.prompt("Email")
        mot_de_passe = click.prompt("Mot de passe", hide_input=True)

        collaborateur = authentifier(session, email, mot_de_passe)
        if collaborateur is None:
            click.echo("Identifiants invalides.")
            return

        sauvegarder_jeton(creer_jeton(collaborateur))
        click.echo("Connecté.")