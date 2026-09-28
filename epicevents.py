"""Point d'entrée de l'application Epic Events CRM.

Usage :
    python epicevents.py --help
"""

import sys

from epicevents.cli.principal import cli
from epicevents.journalisation import initialiser, journaliser_exception

if __name__ == "__main__":
    initialiser()
    try:
        cli()
    except (PermissionError, ValueError) as e:
        print(f"Erreur : {e}")
        sys.exit(1)

    except Exception as e:
        journaliser_exception(e)
        print("Une erreur inattendue est survenue. L'incident a été signalé.")
        sys.exit(1)
