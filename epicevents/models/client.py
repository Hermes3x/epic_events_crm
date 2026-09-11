"""Modèle Client : les clients d'Epic Events."""
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from epicevents.models.base import Base




class Client(Base):
    """Un client d'Epic Events, rattachable à un contrat."""

    __tablename__ = "client"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom_complet: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    telephone: Mapped[str] = mapped_column(String(20))
    nom_entreprise: Mapped[str] = mapped_column(String(100))
    date_creation: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    date_derniere_maj: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    commercial_id: Mapped[int] = mapped_column(ForeignKey("collaborateur.id"))
    
    commercial: Mapped["Collaborateur"] = relationship(back_populates="clients")
    contrats: Mapped[list["Contrat"]] = relationship(back_populates="client")


    def __repr__(self) -> str:
        return f"<Client {self.nom_complet}>"
