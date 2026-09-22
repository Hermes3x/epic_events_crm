"""Règles métier sur les évènements."""

from epicevents.permissions import exiger_permission
from epicevents.models import Evenement


def creer_evenement(session, collaborateur, contrat, **champs):
    """Crée un évenement, si le contrat est signé et que le commercial en est responsable"""
    exiger_permission(collaborateur, "creer_evenement")

    if not contrat.statut:
        raise PermissionError("L'évènement n'a pas pu etre créé : le contrat n'est pas encore signé. ")
    if collaborateur.role.nom == "commercial":
        if contrat.client.commercial_id != collaborateur.id:
            raise PermissionError("Ce contrat n'est pas le vôtre.")

    evenement = Evenement(**champs, contrat=contrat)
    session.add(evenement)
    session.commit()
    return evenement


def modifier_evenement(session, collaborateur, evenement, **champs):
    """Modifie un evenement, si le collaborateur en est responsable (support)."""
    exiger_permission(collaborateur, "modifier_evenement")

    if evenement.support_id != collaborateur.id:
        raise PermissionError("Vous n'êtes pas affecté à la gestion de cet évènement")

    for nom, valeur in champs.items():
        setattr(evenement, nom, valeur)
    session.commit()
    return evenement


def assigner_support(session, collaborateur, evenement, cible):
    """assigne un collaborateur du support à un évènement."""
    exiger_permission(collaborateur, "assigner_support")

    if cible.role.nom != "support":
        raise ValueError("Ce collaborateur n'est pas du département support.")

    evenement.support = cible

    session.commit()
    return evenement
