"""Authentification des collaborateurs et gestion des jetons."""

import os
from datetime import datetime, timedelta, timezone

import jwt

from pathlib import Path

from sqlalchemy import select

from epicevents.models import Collaborateur
from epicevents.securite import verifier_mot_de_passe


def authentifier(session, email: str, mot_de_passe: str) -> Collaborateur | None:
    """Retourne le collaborateur si les identifiants sont valides, sinon None."""
    collaborateur = session.scalar(select(Collaborateur).where(Collaborateur.email == email))
    if collaborateur is None:
        return None
    if not verifier_mot_de_passe(collaborateur.mot_de_passe_hache, mot_de_passe):
        return None
    return collaborateur


def creer_jeton(collaborateur: Collaborateur) -> str:
    """Fabrique un jeton signé, valable 24 heures."""
    contenu = {
        "sub": str(collaborateur.id),
        "role": collaborateur.role.nom,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(contenu, os.getenv("JWT_SECRET"), algorithm="HS256")


FICHIER_JETON = Path.home() / ".epicevents_token"


def sauvegarder_jeton(jeton: str) -> None:
    """Enregistre le jeton dans le fichier de l'utilisateur."""
    FICHIER_JETON.write_text(jeton, encoding="utf-8")


def charger_jeton() -> str | None:
    """Relit le jeton enregistré, ou None s'il n'y en a pas."""
    if not FICHIER_JETON.exists():
        return None
    return FICHIER_JETON.read_text(encoding="utf-8").strip()


def lire_jeton(jeton: str) -> dict | None:
    """Retourne le contenu du jeton s'il est valide et non expiré, sinon None."""
    try:
        return jwt.decode(jeton, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return None


def utilisateur_courant(session) -> Collaborateur | None:
    """Retourne le collaborateur connecté, ou None si personne ne l'est."""
    jeton = charger_jeton()
    if jeton is None:
        return None
    contenu = lire_jeton(jeton)
    if contenu is None:
        return None
    return session.get(Collaborateur, int(contenu["sub"]))
