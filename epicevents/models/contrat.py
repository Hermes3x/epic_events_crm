"""Modèle Contrat : les contrats d'évènement."""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from epicevents.models.base import Base




class Contrat(Base):
    """Un contrat entre un client et un évènement."""

    __tablename__ = "contrat"

    id: Mapped[int] = mapped_column(primary_key=True)
    montant_total: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    reste_a_payer: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    date_creation: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    statut: Mapped[bool] = mapped_column(Boolean, default=False)

    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"))
    client: Mapped["Client"] = relationship(back_populates="contrats")
    evenements: Mapped[list["Evenement"]] = relationship(back_populates="contrat")


    def __repr__(self) -> str:
        return f"<Contrat {self.id} - {self.montant_total} €>"
