"""Accès aux données des contrats."""

from sqlalchemy import select

from epicevents.models import Contrat, Client


def lister_contrats(session) -> list[Contrat]:
    """Retourne tous les contrats."""
    return session.scalars(select(Contrat)).all()


def lister_contrats_non_signes(session) -> list[Contrat]:
    """Retourne tous les contrats non signés."""
    return session.scalars(select(Contrat).where(Contrat.statut.is_(False))).all()


def lister_contrats_non_soldes(session) -> list[Contrat]:
    """Retourne tous les contrats non soldés."""
    return session.scalars(select(Contrat).where(Contrat.reste_a_payer > 0)).all()


def lister_contrats_du_commercial(session, commercial) -> list[Contrat]:
    """Retourne tous les contrats d'un commercial"""
    return session.scalars(select(Contrat).join(Client).where(Client.commercial_id == commercial.id)).all()
