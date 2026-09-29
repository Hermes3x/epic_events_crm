"""Tests de l'autorisation par role (epicevents/permissions.py)."""

import pytest

from epicevents.permissions import a_la_permission, exiger_permission


def test_la_gestion_gere_les_collaborateurs(equipe):
    for action in ("creer_collaborateur", "modifier_collaborateur", "supprimer_collaborateur"):
        assert a_la_permission(equipe["gestion"], action) is True


def test_le_commercial_ne_gere_pas_les_collaborateurs(equipe):
    assert a_la_permission(equipe["commercial"], "creer_collaborateur") is False


def test_le_support_ne_gere_pas_les_collaborateurs(equipe):
    assert a_la_permission(equipe["support"], "creer_collaborateur") is False


def test_seul_le_commercial_cree_des_clients(equipe):
    assert a_la_permission(equipe["commercial"], "creer_client") is True
    assert a_la_permission(equipe["gestion"], "creer_client") is False
    assert a_la_permission(equipe["support"], "creer_client") is False


def test_modifier_un_contrat_est_partage(equipe):
    """Gestion et commercial peuvent modifier un contrat, le support non."""
    assert a_la_permission(equipe["gestion"], "modifier_contrat") is True
    assert a_la_permission(equipe["commercial"], "modifier_contrat") is True
    assert a_la_permission(equipe["support"], "modifier_contrat") is False


def test_seule_la_gestion_assigne_un_support(equipe):
    assert a_la_permission(equipe["gestion"], "assigner_support") is True
    assert a_la_permission(equipe["commercial"], "assigner_support") is False
    assert a_la_permission(equipe["support"], "assigner_support") is False


def test_une_action_inconnue_est_refusee(equipe):
    """Refus par defaut : une action non declaree n'est jamais autorisee."""
    assert a_la_permission(equipe["gestion"], "supprimer_la_base") is False


def test_exiger_permission_laisse_passer_si_autorise(equipe):
    exiger_permission(equipe["gestion"], "creer_collaborateur")


def test_exiger_permission_leve_si_refuse(equipe):
    with pytest.raises(PermissionError):
        exiger_permission(equipe["commercial"], "creer_collaborateur")
