"""Commandes sur les clients."""

import click
from rich.console import Console
from rich.table import Table

from epicevents.auth import exiger_connexion
from epicevents.database import Session
from epicevents.repositories.clients import lister_clients

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
