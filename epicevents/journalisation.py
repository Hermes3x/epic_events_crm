"""Journalisation des évènements de l'application avec Sentry.

Le cahier des charges impose de consigner :
  - toutes les exceptions inattendues ;
  - chaque création ou modification d'un collaborateur ;
  - la signature d'un contrat.

Le DSN est lu dans la variable d'environnement SENTRY_DSN. S'il est absent,
l'application fonctionne normalement mais sans journalisation : c'est le cas
en développement et pendant les tests.

Aucune donnée personnelle n'est transmise (send_default_pii=False) : les
rapports ne contiennent ni adresse IP, ni en-tête, ni coordonnées de client.
"""

import os

import sentry_sdk
from dotenv import load_dotenv

load_dotenv()


def initialiser() -> bool:
    """Démarre la journalisation Sentry. Retourne True si elle est active."""
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return False

    sentry_sdk.init(
        dsn=dsn,
        # Aucune donnee personnelle dans les rapports : c'est un CRM.
        send_default_pii=False,
        # Toutes les exceptions sont remontees, aucune mesure de performance.
        traces_sample_rate=0.0,
    )
    return True


def journaliser_exception(exception: BaseException) -> None:
    """Consigne une exception inattendue."""
    sentry_sdk.capture_exception(exception)


def journaliser_collaborateur(action: str, collaborateur, auteur) -> None:
    """Consigne la création, la modification ou la suppression d'un collaborateur.

    action : "creation", "modification" ou "suppression".
    """
    sentry_sdk.capture_message(
        f"Collaborateur {action} : {collaborateur.nom_complet} "
        f"({collaborateur.numero_employe}, {collaborateur.role.nom}) "
        f"par {auteur.nom_complet}",
        level="info",
    )


def journaliser_signature_contrat(contrat, auteur) -> None:
    """Consigne la signature d'un contrat."""
    sentry_sdk.capture_message(
        f"Contrat {contrat.id} signé : {contrat.client.nom_complet}, "
        f"{contrat.montant_total} € — par {auteur.nom_complet}",
        level="info",
    )
