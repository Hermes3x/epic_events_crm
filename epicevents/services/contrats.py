"""Règles métier sur les contrats."""

from epicevents.permissions import exiger_permission
from epicevents.models import Contrat


def creer_contrat(session, collaborateur, client, **champs):
    """Crée un contrat, si le collaborateur y est autorisé"""
    exiger_permission(collaborateur, "creer_contrat")

    contrat = Contrat(**champs, client=client)
    session.add(contrat)
    session.commit()
    return contrat


def modifier_contrat(session, collaborateur, contrat, **champs):
    """Modifie un contrat, si le collaborateur en est responsable (commercial = son propre contrat / gestion = tous les contrats)."""
    exiger_permission(collaborateur, "modifier_contrat")

    if collaborateur.role.nom == "commercial":
        if contrat.client.commercial_id != collaborateur.id:
            raise PermissionError("Vous n'êtes pas affecté à la gestion de ce contrat")

    for nom, valeur in champs.items():
        setattr(contrat, nom, valeur)
    session.commit()
    return contrat
