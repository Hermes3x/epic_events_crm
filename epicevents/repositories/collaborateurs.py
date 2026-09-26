"""Accès aux données des collaborateurs."""

from sqlalchemy import select

from epicevents.models import Collaborateur


def lister_collaborateurs(session) -> list[Collaborateur]:
    """Retourne tous les collaborateurs."""
    return session.scalars(select(Collaborateur)).all()
