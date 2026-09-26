"""Commandes sur les évènements."""

import click
from rich.console import Console
from rich.table import Table

from epicevents.auth import exiger_connexion
from epicevents.database import Session
from epicevents.repositories.evenements import lister_evenements

console = Console()


@click.group()
def evenements() -> None:
    """Consultation et gestion des évènements."""


@evenements.command(name="lister")
def lister() -> None:
    """Affiche tous les évènements."""
    with Session() as session:
        exiger_connexion(session)
        resultats = lister_evenements(session)

        tableau = Table(title="Evenements")
        tableau.add_column("Id")
        tableau.add_column("Nom", max_width=25, no_wrap=True)
        tableau.add_column("Client", max_width=25, no_wrap=True)
        tableau.add_column("Debut")
        tableau.add_column("Fin")
        tableau.add_column("Support")
        tableau.add_column("Lieu", max_width=25, no_wrap=True)
        tableau.add_column("Nb invités")

        for evenement in resultats:
            tableau.add_row(
                str(evenement.id),
                evenement.nom,
                evenement.contrat.client.nom_complet,
                evenement.date_debut.strftime("%d/%m/%Y"),
                evenement.date_fin.strftime("%d/%m/%Y"),
                evenement.support.nom_complet if evenement.support else "—",
                evenement.localisation,
                str(evenement.nb_invites),
            )

        console.print(tableau)
