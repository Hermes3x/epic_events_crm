"""Insère un jeu de données de démonstration, tiré du cahier des charges.

Usage :
    python seed_demo.py

DONNÉES FICTIVES, POUR LE DÉVELOPPEMENT ET LA DÉMONSTRATION UNIQUEMENT.
Les mots de passe ci-dessous sont volontairement triviaux et ne doivent
jamais servir en production.

Le script est idempotent : il ne fait rien si les données existent déjà.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import select

from epicevents.database import Session
from epicevents.models import Client, Collaborateur, Contrat, Evenement, Role
from epicevents.securite import hacher_mot_de_passe


def main() -> None:
    with Session() as session:
        if session.scalar(select(Collaborateur).where(Collaborateur.email == "bill@epicevents.fr")):
            print("Les données de démonstration existent déjà. Rien à faire.")
            return

        commercial = session.scalar(select(Role).where(Role.nom == "commercial"))
        support = session.scalar(select(Role).where(Role.nom == "support"))
        if commercial is None or support is None:
            print("Les rôles sont absents : lancez d'abord  python init_db.py")
            return

        # --- Collaborateurs ---------------------------------------------------
        bill = Collaborateur(
            numero_employe="EE-101", nom_complet="Bill Boquet",
            email="bill@epicevents.fr", role=commercial,
            mot_de_passe_hache=hacher_mot_de_passe("bill123"),
        )
        kate = Collaborateur(
            numero_employe="EE-201", nom_complet="Kate Hastroff",
            email="kate@epicevents.fr", role=support,
            mot_de_passe_hache=hacher_mot_de_passe("kate123"),
        )
        alienor = Collaborateur(
            numero_employe="EE-202", nom_complet="Aliénor Vichum",
            email="alienor@epicevents.fr", role=support,
            mot_de_passe_hache=hacher_mot_de_passe("alienor123"),
        )

        # --- Clients (tous suivis par Bill) ------------------------------------
        john = Client(
            nom_complet="John Ouick", email="john.ouick@gmail.com",
            telephone="+1 234 567 8901", nom_entreprise="Ouick Corp", commercial=bill,
        )
        lou = Client(
            nom_complet="Lou Bouzin", email="jacky@loubouzin.grd",
            telephone="+666 12345", nom_entreprise="Lou Bouzin SA", commercial=bill,
        )
        kevin = Client(
            nom_complet="Kevin Casey", email="kevin@startup.io",
            telephone="+678 123 456 78", nom_entreprise="Cool Startup LLC", commercial=bill,
        )

        # --- Contrats -----------------------------------------------------------
        contrat_john = Contrat(
            client=john, montant_total=Decimal("12000.00"),
            reste_a_payer=Decimal("0.00"), statut=True,          # signé et soldé
        )
        contrat_lou = Contrat(
            client=lou, montant_total=Decimal("8500.00"),
            reste_a_payer=Decimal("3500.00"), statut=True,       # signé, pas soldé
        )
        contrat_kevin = Contrat(
            client=kevin, montant_total=Decimal("4000.00"),
            reste_a_payer=Decimal("4000.00"), statut=False,      # pas encore signé
        )

        # --- Événements ---------------------------------------------------------
        mariage = Evenement(
            nom="John Ouick Wedding", contrat=contrat_john, support=kate,
            date_debut=datetime(2023, 6, 4, 13, 0), date_fin=datetime(2023, 6, 5, 2, 0),
            localisation="53 Rue du Château, 41120 Candé-sur-Beuvron, France",
            nb_invites=75,
            notes="Wedding starts at 3PM, by the river. Catering is organized, "
                  "reception starts at 5PM. Kate needs to organize the DJ for after party.",
        )
        assemblee = Evenement(
            nom="Lou Bouzin General Assembly", contrat=contrat_lou, support=alienor,
            date_debut=datetime(2023, 5, 5, 15, 0), date_fin=datetime(2023, 5, 5, 17, 0),
            localisation="Salle des fêtes de Mufflins", nb_invites=200,
            notes="Assemblée générale des actionnaires (~200 personnes).",
        )
        seminaire = Evenement(
            nom="Lou Bouzin Séminaire", contrat=contrat_lou, support=None,   # PAS de support
            date_debut=datetime(2023, 9, 12, 9, 0), date_fin=datetime(2023, 9, 12, 18, 0),
            localisation="Hôtel du Parc, Mufflins", nb_invites=40,
            notes="Séminaire d'équipe. Support à désigner.",
        )

        session.add_all([bill, kate, alienor, john, lou, kevin,
                         contrat_john, contrat_lou, contrat_kevin,
                         mariage, assemblee, seminaire])
        session.commit()
        print("Données de démonstration insérées :")
        print("   3 collaborateurs (bill@ / kate@ / alienor@epicevents.fr, mot de passe = prénom + 123)")
        print("   3 clients, 3 contrats, 3 événements")


if __name__ == "__main__":
    main()
