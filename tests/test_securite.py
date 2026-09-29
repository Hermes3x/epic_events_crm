"""Tests du hachage des mots de passe (epicevents/securite.py)."""

from epicevents.securite import hacher_mot_de_passe, verifier_mot_de_passe


def test_le_mot_de_passe_n_est_jamais_stocke_en_clair():
    empreinte = hacher_mot_de_passe("motdepasse-secret")
    assert "motdepasse-secret" not in empreinte


def test_l_empreinte_est_bien_de_l_argon2():
    empreinte = hacher_mot_de_passe("azerty123")
    assert empreinte.startswith("$argon2id$")


def test_le_bon_mot_de_passe_est_accepte():
    empreinte = hacher_mot_de_passe("azerty123")
    assert verifier_mot_de_passe(empreinte, "azerty123") is True


def test_un_mauvais_mot_de_passe_est_refuse():
    empreinte = hacher_mot_de_passe("azerty123")
    assert verifier_mot_de_passe(empreinte, "azerty124") is False


def test_un_mot_de_passe_vide_est_refuse():
    empreinte = hacher_mot_de_passe("azerty123")
    assert verifier_mot_de_passe(empreinte, "") is False


def test_le_salage_produit_deux_empreintes_differentes():
    """Deux hachages du meme mot de passe different : c'est le sel.

    Sans sel, un attaquant reconnaitrait tous les comptes partageant
    un mot de passe courant (attaque par table arc-en-ciel).
    """
    premiere = hacher_mot_de_passe("identique")
    seconde = hacher_mot_de_passe("identique")
    assert premiere != seconde


def test_les_deux_empreintes_salees_restent_verifiables():
    premiere = hacher_mot_de_passe("identique")
    seconde = hacher_mot_de_passe("identique")
    assert verifier_mot_de_passe(premiere, "identique") is True
    assert verifier_mot_de_passe(seconde, "identique") is True
