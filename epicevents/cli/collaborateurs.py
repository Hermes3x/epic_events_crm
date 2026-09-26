"""Commande sur les collaborateurs"""

import click
from rich.console import Console
from rich.table import Table

from epicevents.auth import exiger_connexion
from epicevents.database import Session
from epicevents.repositories.collaborateurs import lister_collaborateurs

console = Console()


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
        tableau.add_column("Id")
        tableau.add_column("N° employe")
        tableau.add_column("Nom complet")
        tableau.add_column("Email")
        tableau.add_column("Role")
        tableau.add_column("Clients")
        tableau.add_column("Evenements")

        for collaborateur in resultats:
            tableau.add_row(
                str(collaborateur.id),
                str(collaborateur.numero_employe),
                collaborateur.nom_complet,
                collaborateur.email,
                collaborateur.role.nom,
                str(len(collaborateur.clients)),
                str(len(collaborateur.evenements)),
            )

        console.print(tableau)
