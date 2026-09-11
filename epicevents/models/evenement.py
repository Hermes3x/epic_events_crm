"""Modèle Evènement : les évènements."""
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from epicevents.models.base import Base


class Evenement(Base):
    """Un évènement."""

    __tablename__ = "evenement"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(100))
    date_debut: Mapped[datetime] = mapped_column(DateTime)
    date_fin: Mapped[datetime] = mapped_column(DateTime)
    localisation: Mapped[str] = mapped_column(String(100))
    nb_invites: Mapped[int] = mapped_column()
    notes: Mapped[str] = mapped_column(Text)

    contrat_id: Mapped[int] = mapped_column(ForeignKey("contrat.id"))
    support_id: Mapped[int | None] = mapped_column(ForeignKey("collaborateur.id"))

    contrat: Mapped["Contrat"] = relationship(back_populates="evenements")
    support: Mapped["Collaborateur | None"] = relationship(back_populates="evenements")

    def __repr__(self) -> str:
        return f"<Evenement {self.nom}>"
