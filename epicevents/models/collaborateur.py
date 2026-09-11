"""Modèle Collaborateur : les employés d'Epic Events."""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from epicevents.models.base import Base


class Collaborateur(Base):
    """Un employé d'Epic Events, rattaché à un département."""

    __tablename__ = "collaborateur"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero_employe: Mapped[str] = mapped_column(String(20), unique=True)
    nom_complet: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    mot_de_passe_hache: Mapped[str] = mapped_column(String(255))

    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"))
    role: Mapped["Role"] = relationship(back_populates="collaborateurs")

    clients: Mapped[list["Client"]] = relationship(back_populates="commercial")
    evenements: Mapped[list["Evenement"]] = relationship(back_populates="support")


    def __repr__(self) -> str:
        return f"<Collaborateur {self.nom_complet}>"
