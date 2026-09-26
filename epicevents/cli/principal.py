"""Point d'assemblage de l'interface en ligne de commande.

Chaque groupe de commandes vit dans son propre module et est rattaché ici.
Le CLI ne contient aucune règle métier : il demande, appelle un service,
puis affiche le résultat.
"""

import click

from epicevents.cli.auth import auth
from epicevents.cli.clients import clients
from epicevents.cli.contrats import contrats
from epicevents.cli.evenements import evenements
from epicevents.cli.collaborateurs import collaborateurs


@click.group()
def cli() -> None:
    """Epic Events CRM — gestion des clients, contrats et évènements."""


cli.add_command(auth)
cli.add_command(clients)
cli.add_command(contrats)
cli.add_command(evenements)
cli.add_command(collaborateurs)
