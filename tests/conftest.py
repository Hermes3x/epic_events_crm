"""Configuration commune aux tests.

Les tests tournent sur une base PostgreSQL dédiée (epicevents_test), jamais
sur la base de production. Les tables sont recréées avant chaque test, ce qui
garantit que l'ordre d'exécution n'a aucune influence sur les résultats.
"""

import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from epicevents.models import Base, Client, Collaborateur, Contrat, Evenement, Role
from epicevents.securite import hacher_mot_de_passe

load_dotenv()

URL_TEST = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database="epicevents_test",
)

moteur_test = create_engine(URL_TEST)
SessionTest = sessionmaker(bind=moteur_test)


@pytest.fixture
def session():
    """Ouvre une session sur une base vide, et nettoie après le test."""
    Base.metadata.drop_all(moteur_test)
    Base.metadata.create_all(moteur_test)
    session = SessionTest()
    yield session
    session.close()


@pytest.fixture
def roles(session):
    """Les trois rôles de l'entreprise."""
    roles = {nom: Role(nom=nom) for nom in ("gestion", "commercial", "support")}
    session.add_all(roles.values())
    session.commit()
    return roles


@pytest.fixture
def equipe(session, roles):
    """Un collaborateur de chaque rôle, plus un second commercial.

    Le second commercial permet de tester l'autorisation par propriété :
    un commercial ne doit pas pouvoir modifier les clients d'un autre.
    """
    membres = {
        "gestion": Collaborateur(
            numero_employe="EE-001", nom_complet="Dawn Stanley",
            email="dawn@epicevents.fr", role=roles["gestion"],
            mot_de_passe_hache=hacher_mot_de_passe("motdepasse-dawn"),
        ),
        "commercial": Collaborateur(
            numero_employe="EE-101", nom_complet="Bill Boquet",
            email="bill@epicevents.fr", role=roles["commercial"],
            mot_de_passe_hache=hacher_mot_de_passe("motdepasse-bill"),
        ),
        "commercial2": Collaborateur(
            numero_employe="EE-102", nom_complet="Marie Dupont",
            email="marie@epicevents.fr", role=roles["commercial"],
            mot_de_passe_hache=hacher_mot_de_passe("motdepasse-marie"),
        ),
        "support": Collaborateur(
            numero_employe="EE-201", nom_complet="Kate Hastroff",
            email="kate@epicevents.fr", role=roles["support"],
            mot_de_passe_hache=hacher_mot_de_passe("motdepasse-kate"),
        ),
        "support2": Collaborateur(
            numero_employe="EE-202", nom_complet="Aliénor Vichum",
            email="alienor@epicevents.fr", role=roles["support"],
            mot_de_passe_hache=hacher_mot_de_passe("motdepasse-alienor"),
        ),
    }
    session.add_all(membres.values())
    session.commit()
    return membres


@pytest.fixture
def donnees(session, equipe):
    """Un client, un contrat signé et un évènement sans support."""
    from datetime import datetime
    from decimal import Decimal

    client = Client(
        nom_complet="John Ouick", email="john.ouick@gmail.com",
        telephone="+1 234 567 8901", nom_entreprise="Ouick Corp",
        commercial=equipe["commercial"],
    )
    contrat_signe = Contrat(
        client=client, montant_total=Decimal("12000.00"),
        reste_a_payer=Decimal("4000.00"), statut=True,
    )
    contrat_non_signe = Contrat(
        client=client, montant_total=Decimal("5000.00"),
        reste_a_payer=Decimal("5000.00"), statut=False,
    )
    evenement = Evenement(
        nom="John Ouick Wedding", contrat=contrat_signe, support=None,
        date_debut=datetime(2027, 6, 4, 13, 0), date_fin=datetime(2027, 6, 5, 2, 0),
        localisation="Candé-sur-Beuvron", nb_invites=75, notes="Par la rivière.",
    )
    session.add_all([client, contrat_signe, contrat_non_signe, evenement])
    session.commit()
    return {
        "client": client,
        "contrat_signe": contrat_signe,
        "contrat_non_signe": contrat_non_signe,
        "evenement": evenement,
    }
