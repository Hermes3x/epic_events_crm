"""Hachage et vérification des mots de passe."""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_hasher = PasswordHasher()


def hacher_mot_de_passe(mot_de_passe: str) -> str:
    """Retourne l'empreinte argon2 du mot de passe fourni."""
    return _hasher.hash(mot_de_passe)


def verifier_mot_de_passe(empreinte: str, mot_de_passe: str) -> bool:
    """Indique si le mot de passe correspond à l'empreinte stockée."""
    try:
        return _hasher.verify(empreinte, mot_de_passe)
    except VerifyMismatchError:
        return False
