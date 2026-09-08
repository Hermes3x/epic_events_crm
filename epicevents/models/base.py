"""Classe de base commune à tous les modèles."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Classe mère de toutes les tables.

    SQLAlchemy s'en sert pour tenir le catalogue des tables à créer.
    """
