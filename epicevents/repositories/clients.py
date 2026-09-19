"""Accès aux données des clients."""

from sqlalchemy import select

from epicevents.models import Client, Contrat


def lister_clients(session) -> list[Client]:
    """Retourne tous les clients."""
    return session.scalars(select(Client)).all()
