"""Tests de l'authentification et des jetons (epicevents/auth.py)."""

import os
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from epicevents.auth import (
    authentifier,
    creer_jeton,
    exiger_connexion,
    lire_jeton,
)


def test_les_bons_identifiants_retournent_le_collaborateur(session, equipe):
    trouve = authentifier(session, "bill@epicevents.fr", "motdepasse-bill")
    assert trouve is not None
    assert trouve.nom_complet == "Bill Boquet"


def test_un_mauvais_mot_de_passe_est_refuse(session, equipe):
    assert authentifier(session, "bill@epicevents.fr", "mauvais") is None


def test_un_email_inconnu_est_refuse(session, equipe):
    assert authentifier(session, "inconnu@epicevents.fr", "motdepasse-bill") is None


def test_les_deux_echecs_sont_indistinguables(session, equipe):
    """Email inconnu et mot de passe faux donnent le meme resultat.

    Repondre differemment permettrait d'enumerer les comptes existants.
    """
    email_inconnu = authentifier(session, "personne@epicevents.fr", "peu-importe")
    mot_de_passe_faux = authentifier(session, "bill@epicevents.fr", "mauvais")
    assert email_inconnu == mot_de_passe_faux is None


def test_le_jeton_ne_contient_aucun_secret(session, equipe):
    """Un JWT est signe mais PAS chiffre : tout le monde peut le lire."""
    jeton = creer_jeton(equipe["commercial"])
    contenu = jwt.decode(jeton, options={"verify_signature": False})
    assert "mot_de_passe" not in contenu
    assert "email" not in contenu
    assert set(contenu) == {"sub", "role", "exp"}


def test_le_jeton_porte_l_identite_et_le_role(session, equipe):
    jeton = creer_jeton(equipe["commercial"])
    contenu = lire_jeton(jeton)
    assert contenu["sub"] == str(equipe["commercial"].id)
    assert contenu["role"] == "commercial"


def test_un_jeton_falsifie_est_refuse(session, equipe):
    jeton = creer_jeton(equipe["commercial"])
    falsifie = jeton[:-1] + ("A" if jeton[-1] != "A" else "B")
    assert lire_jeton(falsifie) is None


def test_un_jeton_signe_avec_une_autre_cle_est_refuse():
    """Sans JWT_SECRET, impossible de fabriquer un jeton valide."""
    pirate = jwt.encode({"sub": "1", "role": "gestion"}, "cle-du-pirate", algorithm="HS256")
    assert lire_jeton(pirate) is None


def test_un_jeton_expire_est_refuse():
    perime = jwt.encode(
        {"sub": "1", "role": "gestion",
         "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
        os.getenv("JWT_SECRET"), algorithm="HS256",
    )
    assert lire_jeton(perime) is None


def test_n_importe_quelle_chaine_est_refusee():
    assert lire_jeton("pas-un-jeton") is None


def test_exiger_connexion_leve_si_personne_n_est_connecte(session, monkeypatch):
    """Sans jeton valide, l'acces aux donnees est impossible."""
    monkeypatch.setattr("epicevents.auth.charger_jeton", lambda: None)
    with pytest.raises(PermissionError):
        exiger_connexion(session)
