"""Commandes sur les contrats."""

import click
from rich.console import Console
from rich.table import Table

from epicevents.auth import exiger_connexion
from epicevents.database import Session
from epicevents.repositories.contrats import lister_contrats

console = Console()


@click.group()
def contrats() -> None:
    """Consultation et gestion des contrats."""


@contrats.command(name="lister")
def lister() -> None:
    """Affiche tous les contrats."""
    with Session() as session:
        exiger_connexion(session)
        resultats = lister_contrats(session)

        tableau = Table(title="Contrats")
        tableau.add_column("client")
        tableau.add_column("Contrat Id")
        tableau.add_column("evenements")
        tableau.add_column("montant_total")
        tableau.add_column("reste_a_payer")
        tableau.add_column("date_creation")
        tableau.add_column("contrat signé")

        for contrat in resultats:
            tableau.add_row(               
                contrat.client.nom_complet,
                str(contrat.id),
                str(len(contrat.evenements)),
                str(contrat.montant_total),
                str(contrat.reste_a_payer),
                contrat.date_creation.strftime("%d/%m/%Y"),
                "oui" if contrat.statut else "non",
            )

        console.print(tableau)
