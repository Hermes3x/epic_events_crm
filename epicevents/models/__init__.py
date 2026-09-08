"""Modèles de données de l'application.

Tous les modèles sont importés ici afin que SQLAlchemy les connaisse
dès que le paquet est chargé : c'est ce qui permet aux relations
déclarées par leur nom (ex. "Collaborateur") d'être résolues.
"""

from epicevents.models.base import Base
from epicevents.models.client import Client
from epicevents.models.collaborateur import Collaborateur
from epicevents.models.contrat import Contrat
from epicevents.models.evenement import Evenement
from epicevents.models.role import Role

__all__ = ["Base", "Client", "Collaborateur", "Contrat", "Evenement", "Role"]
