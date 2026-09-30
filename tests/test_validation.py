"""Tests de la validation des donnees saisies (epicevents/validation.py)."""

import pytest

from epicevents.validation import valider_email


def test_un_email_valide_est_accepte():
    assert valider_email("bill@epicevents.fr") == "bill@epicevents.fr"


def test_un_email_avec_points_et_tirets_est_accepte():
    """Les adresses reelles contiennent souvent des points et des tirets."""
    assert valider_email("jean.dupont@sous-domaine.co.uk") == "jean.dupont@sous-domaine.co.uk"


def test_un_email_sans_arobase_est_refuse():
    with pytest.raises(ValueError):
        valider_email("pasunemail")


def test_un_email_sans_domaine_est_refuse():
    with pytest.raises(ValueError):
        valider_email("bill@")


def test_un_email_sans_extension_est_refuse():
    with pytest.raises(ValueError):
        valider_email("bill@epicevents")


def test_un_email_sans_partie_locale_est_refuse():
    with pytest.raises(ValueError):
        valider_email("@epicevents.fr")


def test_un_email_contenant_un_espace_est_refuse():
    with pytest.raises(ValueError):
        valider_email("bill boquet@epicevents.fr")


def test_une_chaine_vide_est_refusee():
    with pytest.raises(ValueError):
        valider_email("")


def test_le_message_d_erreur_cite_la_valeur_refusee():
    """L'utilisateur doit voir quelle saisie a ete rejetee."""
    with pytest.raises(ValueError, match="pasunemail"):
        valider_email("pasunemail")
