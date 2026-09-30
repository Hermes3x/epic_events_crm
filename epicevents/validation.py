"""Validation des données saisies par l'utilisateur."""

import re

MOTIF_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")


def valider_email(email: str) -> str:
    """Retourne l'email s'il est valide, lève ValueError sinon."""
    if MOTIF_EMAIL.match(email) is None:
        raise ValueError(f"Adresse email invalide : {email}")
    return email
