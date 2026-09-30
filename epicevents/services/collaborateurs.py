"""Règles métier sur les collaborateurs."""

from epicevents.permissions import exiger_permission
from epicevents.models import Collaborateur
from epicevents.securite import hacher_mot_de_passe
from epicevents.journalisation import journaliser_collaborateur
from epicevents.validation import valider_email


def creer_collaborateur(session, collaborateur, role, mot_de_passe, **champs):
    """Crée un collaborateur."""
    exiger_permission(collaborateur, "creer_collaborateur")

    if "email" in champs:
        champs["email"] = valider_email(champs["email"])

    cible = Collaborateur(**champs, role=role, mot_de_passe_hache=hacher_mot_de_passe(mot_de_passe))
    session.add(cible)
    session.commit()
    journaliser_collaborateur("creation", cible, collaborateur)
    return cible


def modifier_collaborateur(session, collaborateur, cible, **champs):
    """Modifie un collaborateur."""
    exiger_permission(collaborateur, "modifier_collaborateur")

    if "email" in champs:
        champs["email"] = valider_email(champs["email"])

    for nom, valeur in champs.items():
        setattr(cible, nom, valeur)

    session.commit()
    journaliser_collaborateur("modification", cible, collaborateur)
    return cible


def supprimer_collaborateur(session, collaborateur, cible):
    """Supprime un collaborateur."""
    exiger_permission(collaborateur, "supprimer_collaborateur")

    journaliser_collaborateur("suppression", cible, collaborateur)
    session.delete(cible)
    session.commit()
    return cible
