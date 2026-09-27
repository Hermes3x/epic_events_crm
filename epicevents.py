"""Point d'entrée de l'application Epic Events CRM.

Usage :
    python epicevents.py --help
"""

import sys

from epicevents.cli.principal import cli

if __name__ == "__main__":
    try:
        cli()
    except (PermissionError, ValueError) as e:
        print(f"Erreur : {e}")
        sys.exit(1)
