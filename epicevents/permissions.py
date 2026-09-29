"""Permissions accordées à chaque rôle.

Deux natures de permission coexistent :

- par rôle : l'action est autorisée sur tous les objets (ex. la gestion
  modifie tous les contrats) ;
- par propriété : l'action n'est autorisée que sur les objets de
  l'utilisateur (ex. le commercial modifie SES clients). Cette seconde
  vérification se fait dans le code métier, en comparant l'objet à
  l'utilisateur courant.

La lecture de tous les clients, contrats et événements est accordée à
tout collaborateur authentifié, quel que soit son rôle.
"""

PERMISSIONS = {
    "gestion": {
        "creer_collaborateur",
        "modifier_collaborateur",
        "supprimer_collaborateur",
        "creer_contrat",
        "modifier_contrat",
        "assigner_support",
        "modifier_evenement",
    },
    "commercial": {
        "creer_client",
        "modifier_client",
        "modifier_contrat",
        "creer_evenement"
    },
    "support": {
        "modifier_evenement"
    },
}


def a_la_permission(collaborateur, action: str) -> bool:
    """Indique si le rôle du collaborateur autorise cette action."""
    return action in PERMISSIONS[collaborateur.role.nom]


def exiger_permission(collaborateur, action: str) -> None:
    """Laisse passer si le rôle autorise l'action, lève PermissionError sinon.

    Le message indique quels rôles détiennent l'action. Cette information est
    structurelle — les trois départements sont connus de tous les employés —
    et ne divulgue aucune donnée métier : cette fonction ne voit jamais de
    client, de contrat ni d'évènement.
    """
    if a_la_permission(collaborateur, action):
        return

    roles_autorises = [role for role, actions in PERMISSIONS.items() if action in actions]

    if not roles_autorises:
        raise PermissionError(f"L'action « {action} » n'existe pas.")

    raise PermissionError(
        f"L'action « {action} » n'est pas autorisée pour le rôle "
        f"« {collaborateur.role.nom} ». Rôles autorisés : {', '.join(roles_autorises)}."
    )
