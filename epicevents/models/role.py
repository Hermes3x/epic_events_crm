"""Modèle Role : les trois départements d'Epic Events."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from epicevents.models.base import Base


class Role(Base):
    """Un rôle correspond à un département : commercial, support ou gestion."""

    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(50), unique=True)
    collaborateurs: Mapped[list["Collaborateur"]] = relationship(back_populates="role")


    def __repr__(self) -> str:
        return f"<Role {self.nom}>"
