"""Commandes sur les évènements."""

from datetime import datetime

import click
from rich.console import Console
from rich.table import Table

from epicevents.auth import exiger_connexion
from epicevents.database import Session
from epicevents.models import Collaborateur, Contrat, Evenement
from epicevents.repositories.evenements import (
    lister_evenements,
    lister_evenements_du_support,
    lister_evenements_sans_support,
)
from epicevents.services.evenements import (
    assigner_support,
    creer_evenement,
    modifier_evenement,
)

console = Console()

FORMAT_DATE = "%d/%m/%Y %H:%M"


def _lire_date(valeur: str) -> datetime:
    """Convertit une saisie 'JJ/MM/AAAA HH:MM' en datetime."""
    try:
        return datetime.strptime(valeur, FORMAT_DATE)
    except ValueError:
        raise ValueError(
            f"Date invalide : '{valeur}'. Format attendu : JJ/MM/AAAA HH:MM "
            "(exemple : 04/06/2027 13:00)"
        )


@click.group()
def evenements() -> None:
    """Consultation et gestion des évènements."""


@evenements.command(name="lister")
@click.option("--sans-support", is_flag=True, help="Uniquement les évènements sans support assigné.")
@click.option("--les-miens", is_flag=True, help="Uniquement les évènements dont je suis le support.")
def lister(sans_support: bool, les_miens: bool) -> None:
    """Affiche les évènements, avec filtres optionnels."""
    with Session() as session:
        moi = exiger_connexion(session)

        if sans_support:
            resultats = lister_evenements_sans_support(session)
            titre = "Évènements sans support assigné"
        elif les_miens:
            resultats = lister_evenements_du_support(session, moi)
            titre = f"Évènements suivis par {moi.nom_complet}"
        else:
            resultats = lister_evenements(session)
            titre = "Évènements"

        tableau = Table(title=titre)
        tableau.add_column("Id", justify="right")
        tableau.add_column("Nom", max_width=22, no_wrap=True)
        tableau.add_column("Client", max_width=16, no_wrap=True)
        tableau.add_column("Début")
        tableau.add_column("Support", max_width=16, no_wrap=True)
        tableau.add_column("Lieu", max_width=22, no_wrap=True)
        tableau.add_column("Invités", justify="right")

        for evenement in resultats:
            tableau.add_row(
                str(evenement.id),
                evenement.nom,
                evenement.contrat.client.nom_complet,
                evenement.date_debut.strftime(FORMAT_DATE),
                evenement.support.nom_complet if evenement.support else "—",
                evenement.localisation,
                str(evenement.nb_invites),
            )

        console.print(tableau)


@evenements.command(name="creer")
@click.option("--contrat", "contrat_id", type=int, prompt="Id du contrat", help="Id du contrat signé.")
@click.option("--nom", prompt="Nom de l'évènement", help="Nom de l'évènement.")
@click.option("--debut", prompt="Début (JJ/MM/AAAA HH:MM)", help="Date et heure de début.")
@click.option("--fin", prompt="Fin (JJ/MM/AAAA HH:MM)", help="Date et heure de fin.")
@click.option("--lieu", prompt="Lieu", help="Lieu de l'évènement.")
@click.option("--invites", type=int, prompt="Nombre d'invités", help="Nombre de participants.")
@click.option("--notes", prompt="Notes", default="", help="Notes libres.")
def creer(
    contrat_id: int, nom: str, debut: str, fin: str,
    lieu: str, invites: int, notes: str,
) -> None:
    """Crée un évènement pour un de ses clients dont le contrat est signé."""
    with Session() as session:
        moi = exiger_connexion(session)

        contrat = session.get(Contrat, contrat_id)
        if contrat is None:
            raise ValueError(f"Aucun contrat avec l'id {contrat_id}.")

        date_debut = _lire_date(debut)
        date_fin = _lire_date(fin)
        if date_fin <= date_debut:
            raise ValueError("La date de fin doit être postérieure à la date de début.")

        evenement = creer_evenement(
            session, moi, contrat,
            nom=nom, date_debut=date_debut, date_fin=date_fin,
            localisation=lieu, nb_invites=invites, notes=notes,
        )
        click.echo(f"Évènement créé : {evenement.nom} (id {evenement.id}, sans support)")


@evenements.command(name="modifier")
@click.argument("evenement_id", type=int)
@click.option("--nom", help="Nouveau nom.")
@click.option("--debut", help="Nouvelle date de début (JJ/MM/AAAA HH:MM).")
@click.option("--fin", help="Nouvelle date de fin (JJ/MM/AAAA HH:MM).")
@click.option("--lieu", help="Nouveau lieu.")
@click.option("--invites", type=int, help="Nouveau nombre d'invités.")
@click.option("--notes", help="Nouvelles notes.")
def modifier(
    evenement_id: int, nom: str | None, debut: str | None, fin: str | None,
    lieu: str | None, invites: int | None, notes: str | None,
) -> None:
    """Modifie un évènement (gestion : tous · support : les siens)."""
    with Session() as session:
        moi = exiger_connexion(session)

        evenement = session.get(Evenement, evenement_id)
        if evenement is None:
            raise ValueError(f"Aucun évènement avec l'id {evenement_id}.")

        champs = {}
        if nom is not None:
            champs["nom"] = nom
        if debut is not None:
            champs["date_debut"] = _lire_date(debut)
        if fin is not None:
            champs["date_fin"] = _lire_date(fin)
        if lieu is not None:
            champs["localisation"] = lieu
        if invites is not None:
            champs["nb_invites"] = invites
        if notes is not None:
            champs["notes"] = notes

        if not champs:
            raise ValueError("Aucun champ à modifier. Voir --help pour les options.")

        modifier_evenement(session, moi, evenement, **champs)
        click.echo(f"Évènement modifié : {evenement.nom} (id {evenement.id})")


@evenements.command(name="assigner-support")
@click.argument("evenement_id", type=int)
@click.option("--support", "support_id", type=int, prompt="Id du collaborateur support",
              help="Id du collaborateur du département support.")
def assigner(evenement_id: int, support_id: int) -> None:
    """Assigne un collaborateur support à un évènement (équipe de gestion)."""
    with Session() as session:
        moi = exiger_connexion(session)

        evenement = session.get(Evenement, evenement_id)
        if evenement is None:
            raise ValueError(f"Aucun évènement avec l'id {evenement_id}.")

        cible = session.get(Collaborateur, support_id)
        if cible is None:
            raise ValueError(f"Aucun collaborateur avec l'id {support_id}.")

        assigner_support(session, moi, evenement, cible)
        click.echo(f"{cible.nom_complet} est maintenant le support de « {evenement.nom} ».")
