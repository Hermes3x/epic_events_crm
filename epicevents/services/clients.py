"""Règles métier sur les clients."""

from epicevents.permissions import exiger_permission
from epicevents.models import Client


def creer_client(session, collaborateur, **champs):
    """Crée un client et l'associe automatiquement au commercial qui le crée."""
    exiger_permission(collaborateur, "creer_client")

    client = Client(**champs, commercial=collaborateur)
    session.add(client)
    session.commit()

    return client


def modifier_client(session, collaborateur, client, **champs):
    """Modifie un client, si le collaborateur en est responsable."""
    exiger_permission(collaborateur, "modifier_client")

    if client.commercial_id != collaborateur.id:
        raise PermissionError("Ce client n'est pas le vôtre.")

    for nom, valeur in champs.items():
        setattr(client, nom, valeur)
    session.commit()
    return client
