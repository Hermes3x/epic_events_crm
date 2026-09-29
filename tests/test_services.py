"""Tests des regles metier (epicevents/services/).

Deux niveaux d'autorisation sont verifies :
  - par ROLE      : le role autorise-t-il cette action ?
  - par PROPRIETE : cet objet appartient-il a l'utilisateur ?
"""

from datetime import datetime
from decimal import Decimal

import pytest

from epicevents.models import Collaborateur
from epicevents.services.clients import creer_client, modifier_client
from epicevents.services.collaborateurs import (
    creer_collaborateur,
    modifier_collaborateur,
    supprimer_collaborateur,
)
from epicevents.services.contrats import creer_contrat, modifier_contrat
from epicevents.services.evenements import (
    assigner_support,
    creer_evenement,
    modifier_evenement,
)


def champs_evenement():
    """Jeu de champs valide pour creer un evenement."""
    return dict(
        nom="Soiree de lancement",
        date_debut=datetime(2027, 11, 15, 18, 0),
        date_fin=datetime(2027, 11, 15, 23, 0),
        localisation="Paris",
        nb_invites=60,
        notes="Cocktail",
    )


# --- Clients : autorisation par role ------------------------------------------


def test_un_commercial_cree_un_client(session, equipe):
    client = creer_client(
        session,
        equipe["commercial"],
        nom_complet="Kevin Casey",
        email="kevin@startup.io",
        telephone="+678 123",
        nom_entreprise="Cool Startup",
    )
    assert client.id is not None


def test_le_client_cree_est_associe_a_son_commercial(session, equipe):
    """Le cahier des charges : le client leur sera automatiquement associe."""
    client = creer_client(
        session,
        equipe["commercial"],
        nom_complet="Kevin Casey",
        email="kevin@startup.io",
        telephone="+678 123",
        nom_entreprise="Cool Startup",
    )
    assert client.commercial_id == equipe["commercial"].id


def test_la_gestion_ne_cree_pas_de_client(session, equipe):
    with pytest.raises(PermissionError):
        creer_client(
            session,
            equipe["gestion"],
            nom_complet="X",
            email="x@x.fr",
            telephone="0",
            nom_entreprise="X",
        )


# --- Clients : autorisation par propriete -------------------------------------


def test_un_commercial_modifie_son_client(session, equipe, donnees):
    modifier_client(session, equipe["commercial"], donnees["client"], telephone="0611223344")
    assert donnees["client"].telephone == "0611223344"


def test_un_commercial_ne_modifie_pas_le_client_d_un_autre(session, equipe, donnees):
    """Meme role, mais l'objet ne lui appartient pas."""
    with pytest.raises(PermissionError):
        modifier_client(session, equipe["commercial2"], donnees["client"], telephone="0000000000")


# --- Contrats : la gestion peut tout, le commercial seulement les siens --------


def test_seule_la_gestion_cree_un_contrat(session, equipe, donnees):
    contrat = creer_contrat(
        session,
        equipe["gestion"],
        donnees["client"],
        montant_total=Decimal("1000.00"),
        reste_a_payer=Decimal("1000.00"),
    )
    assert contrat.id is not None
    with pytest.raises(PermissionError):
        creer_contrat(
            session,
            equipe["commercial"],
            donnees["client"],
            montant_total=Decimal("1000.00"),
            reste_a_payer=Decimal("1000.00"),
        )


def test_un_contrat_est_non_signe_par_defaut(session, equipe, donnees):
    contrat = creer_contrat(
        session,
        equipe["gestion"],
        donnees["client"],
        montant_total=Decimal("1000.00"),
        reste_a_payer=Decimal("1000.00"),
    )
    assert contrat.statut is False


def test_la_gestion_modifie_n_importe_quel_contrat(session, equipe, donnees):
    modifier_contrat(
        session, equipe["gestion"], donnees["contrat_signe"], reste_a_payer=Decimal("0.00")
    )
    assert donnees["contrat_signe"].reste_a_payer == Decimal("0.00")


def test_un_commercial_modifie_le_contrat_de_son_client(session, equipe, donnees):
    modifier_contrat(
        session, equipe["commercial"], donnees["contrat_signe"], reste_a_payer=Decimal("100.00")
    )
    assert donnees["contrat_signe"].reste_a_payer == Decimal("100.00")


def test_un_commercial_ne_modifie_pas_le_contrat_d_un_autre(session, equipe, donnees):
    with pytest.raises(PermissionError):
        modifier_contrat(
            session, equipe["commercial2"], donnees["contrat_signe"], reste_a_payer=Decimal("0.00")
        )


def test_le_support_ne_modifie_aucun_contrat(session, equipe, donnees):
    with pytest.raises(PermissionError):
        modifier_contrat(
            session, equipe["support"], donnees["contrat_signe"], reste_a_payer=Decimal("0.00")
        )


# --- Evenements : la regle metier du contrat signe ----------------------------


def test_un_commercial_cree_un_evenement_sur_un_contrat_signe(session, equipe, donnees):
    evenement = creer_evenement(
        session, equipe["commercial"], donnees["contrat_signe"], **champs_evenement()
    )
    assert evenement.id is not None


def test_aucun_evenement_sur_un_contrat_non_signe(session, equipe, donnees):
    """Creer un evenement pour un de leurs clients QUI A SIGNE un contrat."""
    with pytest.raises(PermissionError):
        creer_evenement(
            session, equipe["commercial"], donnees["contrat_non_signe"], **champs_evenement()
        )


def test_pas_d_evenement_sur_le_contrat_d_un_autre_commercial(session, equipe, donnees):
    with pytest.raises(PermissionError):
        creer_evenement(
            session, equipe["commercial2"], donnees["contrat_signe"], **champs_evenement()
        )


def test_un_evenement_nait_sans_support(session, equipe, donnees):
    """Le support est assigne plus tard par la gestion : la colonne est nullable."""
    evenement = creer_evenement(
        session, equipe["commercial"], donnees["contrat_signe"], **champs_evenement()
    )
    assert evenement.support is None


# --- Evenements : modification et assignation ---------------------------------


def test_le_support_modifie_son_evenement(session, equipe, donnees):
    donnees["evenement"].support = equipe["support"]
    session.commit()
    modifier_evenement(session, equipe["support"], donnees["evenement"], nb_invites=99)
    assert donnees["evenement"].nb_invites == 99


def test_un_support_ne_modifie_pas_l_evenement_d_un_autre(session, equipe, donnees):
    donnees["evenement"].support = equipe["support"]
    session.commit()
    with pytest.raises(PermissionError):
        modifier_evenement(session, equipe["support2"], donnees["evenement"], nb_invites=1)


def test_la_gestion_modifie_tout_evenement(session, equipe, donnees):
    """La gestion n'est le support d'aucun evenement, et les modifie tous."""
    modifier_evenement(session, equipe["gestion"], donnees["evenement"], nb_invites=42)
    assert donnees["evenement"].nb_invites == 42


def test_la_gestion_assigne_un_support(session, equipe, donnees):
    assigner_support(session, equipe["gestion"], donnees["evenement"], equipe["support"])
    assert donnees["evenement"].support_id == equipe["support"].id


def test_un_commercial_n_assigne_pas_de_support(session, equipe, donnees):
    with pytest.raises(PermissionError):
        assigner_support(session, equipe["commercial"], donnees["evenement"], equipe["support"])


def test_on_n_assigne_que_des_collaborateurs_du_support(session, equipe, donnees):
    """Erreur de donnee et non de droit : la gestion a le droit, elle se trompe de personne."""
    with pytest.raises(ValueError):
        assigner_support(session, equipe["gestion"], donnees["evenement"], equipe["commercial"])


# --- Collaborateurs : reserve a la gestion ------------------------------------


def test_la_gestion_cree_un_collaborateur(session, equipe, roles):
    nouveau = creer_collaborateur(
        session,
        equipe["gestion"],
        roles["support"],
        "motdepasse-zoe",
        numero_employe="EE-777",
        nom_complet="Zoe Durand",
        email="zoe@epicevents.fr",
    )
    assert nouveau.id is not None


def test_le_mot_de_passe_d_un_nouveau_collaborateur_est_hache(session, equipe, roles):
    """Le mot de passe en clair ne doit jamais atteindre la base."""
    nouveau = creer_collaborateur(
        session,
        equipe["gestion"],
        roles["support"],
        "motdepasse-zoe",
        numero_employe="EE-777",
        nom_complet="Zoe Durand",
        email="zoe@epicevents.fr",
    )
    assert "motdepasse-zoe" not in nouveau.mot_de_passe_hache
    assert nouveau.mot_de_passe_hache.startswith("$argon2id$")


def test_un_commercial_ne_cree_pas_de_collaborateur(session, equipe, roles):
    with pytest.raises(PermissionError):
        creer_collaborateur(
            session,
            equipe["commercial"],
            roles["support"],
            "x",
            numero_employe="EE-666",
            nom_complet="X",
            email="x@x.fr",
        )


def test_la_gestion_change_le_departement_d_un_collaborateur(session, equipe, roles):
    """Modifier un collaborateur, y compris son departement."""
    cible = equipe["commercial2"]
    modifier_collaborateur(session, equipe["gestion"], cible, role=roles["support"])
    assert cible.role.nom == "support"


def test_la_gestion_supprime_un_collaborateur(session, equipe):
    cible_id = equipe["support2"].id
    supprimer_collaborateur(session, equipe["gestion"], equipe["support2"])
    assert session.get(Collaborateur, cible_id) is None


def test_un_support_ne_supprime_pas_de_collaborateur(session, equipe):
    with pytest.raises(PermissionError):
        supprimer_collaborateur(session, equipe["support"], equipe["commercial"])
