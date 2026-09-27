"""Commandes sur les clients."""

import click
from rich.console import Console
from rich.table import Table

from epicevents.auth import exiger_connexion
from epicevents.database import Session
from epicevents.models import Client
from epicevents.repositories.clients import lister_clients
from epicevents.services.clients import creer_client, modifier_client

console = Console()


@click.group()
def clients() -> None:
    """Consultation et gestion des clients."""


@clients.command(name="lister")
def lister() -> None:
    """Affiche tous les clients."""
    with Session() as session:
        exiger_connexion(session)
        resultats = lister_clients(session)

        tableau = Table(title="Clients")
        tableau.add_column("Id", justify="right")
        tableau.add_column("Nom")
        tableau.add_column("Entreprise")
        tableau.add_column("Email")
        tableau.add_column("Commercial")

        for client in resultats:
            tableau.add_row(
                str(client.id),
                client.nom_complet,
                client.nom_entreprise,
                client.email,
                client.commercial.nom_complet,
            )

        console.print(tableau)


@clients.command(name="creer")
@click.option("--nom", prompt="Nom complet", help="Nom complet du client.")
@click.option("--email", prompt="Email", help="Adresse email.")
@click.option("--telephone", prompt="Téléphone", help="Numéro de téléphone.")
@click.option("--entreprise", prompt="Entreprise", help="Nom de l'entreprise.")
def creer(nom: str, email: str, telephone: str, entreprise: str) -> None:
    """Crée un client, associé automatiquement au commercial connecté."""
    with Session() as session:
        moi = exiger_connexion(session)
        client = creer_client(
            session, moi,
            nom_complet=nom, email=email, telephone=telephone, nom_entreprise=entreprise,
        )
        click.echo(f"Client créé : {client.nom_complet} (id {client.id})")


@clients.command(name="modifier")
@click.argument("client_id", type=int)
@click.option("--nom", help="Nouveau nom complet.")
@click.option("--email", help="Nouvelle adresse email.")
@click.option("--telephone", help="Nouveau numéro de téléphone.")
@click.option("--entreprise", help="Nouveau nom d'entreprise.")
def modifier(
    client_id: int,
    nom: str | None,
    email: str | None,
    telephone: str | None,
    entreprise: str | None,
) -> None:
    """Modifie un client dont on est le commercial responsable."""
    with Session() as session:
        moi = exiger_connexion(session)

        client = session.get(Client, client_id)
        if client is None:
            raise ValueError(f"Aucun client avec l'id {client_id}.")

        champs = {}
        if nom is not None:
            champs["nom_complet"] = nom
        if email is not None:
            champs["email"] = email
        if telephone is not None:
            champs["telephone"] = telephone
        if entreprise is not None:
            champs["nom_entreprise"] = entreprise

        if not champs:
            raise ValueError("Aucun champ à modifier. Voir --help pour les options.")

        modifier_client(session, moi, client, **champs)
        click.echo(f"Client modifié : {client.nom_complet} (id {client.id})")
