"""Accès aux données des évènements."""

from sqlalchemy import select

from epicevents.models import Evenement, Collaborateur


def lister_evenements(session) -> list[Evenement]:
    """Retourne tous les évènements."""
    return session.scalars(select(Evenement)).all()


def lister_evenements_sans_support(session) -> list[Evenement]:
    """Retourne tous les évènements sans support affecté."""
    return session.scalars(select(Evenement).where(Evenement.support_id.is_(None))).all()


def lister_evenements_du_support(session, collaborateur) -> list[Evenement]:
    """Retourne tous les évènements affecté au collaborateur donné."""
    return session.scalars(select(Evenement).where(Evenement.support_id == collaborateur.id)).all()
