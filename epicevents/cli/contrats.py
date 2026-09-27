"""Commandes sur les contrats."""

import click
from rich.console import Console
from rich.table import Table

from epicevents.auth import exiger_connexion
from epicevents.database import Session
from epicevents.models import Client, Contrat
from epicevents.repositories.contrats import (
    lister_contrats,
    lister_contrats_du_commercial,
    lister_contrats_non_signes,
    lister_contrats_non_soldes,
)
from epicevents.services.contrats import creer_contrat, modifier_contrat

console = Console()


@click.group()
def contrats() -> None:
    """Consultation et gestion des contrats."""


@contrats.command(name="lister")
@click.option("--non-signes", is_flag=True, help="Uniquement les contrats non signés.")
@click.option("--non-soldes", is_flag=True, help="Uniquement les contrats non entièrement payés.")
@click.option("--les-miens", is_flag=True, help="Uniquement les contrats de mes clients.")
def lister(non_signes: bool, non_soldes: bool, les_miens: bool) -> None:
    """Affiche les contrats, avec filtres optionnels."""
    with Session() as session:
        moi = exiger_connexion(session)

        if non_signes:
            resultats = lister_contrats_non_signes(session)
            titre = "Contrats non signés"
        elif non_soldes:
            resultats = lister_contrats_non_soldes(session)
            titre = "Contrats non soldés"
        elif les_miens:
            resultats = lister_contrats_du_commercial(session, moi)
            titre = f"Contrats de {moi.nom_complet}"
        else:
            resultats = lister_contrats(session)
            titre = "Contrats"

        tableau = Table(title=titre)
        tableau.add_column("Id", justify="right")
        tableau.add_column("Client", max_width=20, no_wrap=True)
        tableau.add_column("Montant total", justify="right")
        tableau.add_column("Reste à payer", justify="right")
        tableau.add_column("Signé")
        tableau.add_column("Évènements", justify="right")

        for contrat in resultats:
            tableau.add_row(
                str(contrat.id),
                contrat.client.nom_complet,
                str(contrat.montant_total),
                str(contrat.reste_a_payer),
                "oui" if contrat.statut else "non",
                str(len(contrat.evenements)),
            )

        console.print(tableau)


@contrats.command(name="creer")
@click.option("--client", "client_id", type=int, prompt="Id du client", help="Id du client concerné.")
@click.option("--montant", type=float, prompt="Montant total", help="Montant total du contrat.")
@click.option("--reste", type=float, prompt="Reste à payer", help="Montant restant à payer.")
def creer(client_id: int, montant: float, reste: float) -> None:
    """Crée un contrat pour un client (réservé à l'équipe de gestion)."""
    with Session() as session:
        moi = exiger_connexion(session)

        client = session.get(Client, client_id)
        if client is None:
            raise ValueError(f"Aucun client avec l'id {client_id}.")

        contrat = creer_contrat(
            session, moi, client,
            montant_total=montant, reste_a_payer=reste,
        )
        click.echo(
            f"Contrat créé : id {contrat.id} pour {client.nom_complet} "
            f"({contrat.montant_total} €, non signé)"
        )


@contrats.command(name="modifier")
@click.argument("contrat_id", type=int)
@click.option("--montant", type=float, help="Nouveau montant total.")
@click.option("--reste", type=float, help="Nouveau reste à payer.")
@click.option("--signer", is_flag=True, help="Marquer le contrat comme signé.")
def modifier(contrat_id: int, montant: float | None, reste: float | None, signer: bool) -> None:
    """Modifie un contrat (gestion : tous · commercial : ceux de ses clients)."""
    with Session() as session:
        moi = exiger_connexion(session)

        contrat = session.get(Contrat, contrat_id)
        if contrat is None:
            raise ValueError(f"Aucun contrat avec l'id {contrat_id}.")

        champs = {}
        if montant is not None:
            champs["montant_total"] = montant
        if reste is not None:
            champs["reste_a_payer"] = reste
        if signer:
            champs["statut"] = True

        if not champs:
            raise ValueError("Aucun champ à modifier. Voir --help pour les options.")

        modifier_contrat(session, moi, contrat, **champs)
        click.echo(
            f"Contrat modifié : id {contrat.id} "
            f"({contrat.montant_total} €, reste {contrat.reste_a_payer} €, "
            f"{'signé' if contrat.statut else 'non signé'})"
        )
