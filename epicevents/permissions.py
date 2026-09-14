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
