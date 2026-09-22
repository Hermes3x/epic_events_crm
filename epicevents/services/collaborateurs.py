"""Règles métier sur les collaborateurs."""

from epicevents.permissions import exiger_permission
from epicevents.models import Collaborateur
from epicevents.securite import hacher_mot_de_passe


def creer_collaborateur(session, collaborateur, role, mot_de_passe, **champs):
    """Crée un collaborateur."""
    exiger_permission(collaborateur, "creer_collaborateur")

    cible = Collaborateur(**champs, role=role, mot_de_passe_hache=hacher_mot_de_passe(mot_de_passe))
    session.add(cible)
    session.commit()
    return cible


def modifier_collaborateur(session, collaborateur, cible, **champs):
    """Modifie un collaborateur."""
    exiger_permission(collaborateur, "modifier_collaborateur")

    for nom, valeur in champs.items():
        setattr(cible, nom, valeur)

    session.commit()
    return cible


def supprimer_collaborateur(session, collaborateur, cible):
    """Supprime un collaborateur."""
    exiger_permission(collaborateur, "supprimer_collaborateur")

    session.delete(cible)
    session.commit()
    return cible
