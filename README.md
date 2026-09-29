# Epic Events CRM

Application de gestion de la relation client (CRM) en ligne de commande, développée pour
Epic Events, entreprise d'organisation d'évènements.

Elle permet de gérer les **clients**, les **contrats** et les **évènements**, avec un contrôle
d'accès par département et une journalisation centralisée des incidents.

---

## Sommaire

- [Prérequis](#prérequis)
- [Installation](#installation)
- [Premier démarrage](#premier-démarrage)
- [Utilisation](#utilisation)
- [Rôles et permissions](#rôles-et-permissions)
- [Schéma de la base de données](#schéma-de-la-base-de-données)
- [Architecture](#architecture)
- [Choix de sécurité](#choix-de-sécurité)
- [Tests](#tests)

---

## Prérequis

- **Python 3.9** ou plus récent
- **PostgreSQL 12** ou plus récent
- Un compte [Sentry](https://sentry.io) (gratuit) pour la journalisation — facultatif en
  développement

---

## Installation

### 1. Récupérer le projet

```bash
git clone https://github.com/Hermes3x/epic_events_crm.git
cd epic_events_crm
```

### 2. Créer l'environnement virtuel

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1      # Windows (PowerShell)
source .venv/bin/activate          # Linux / macOS
```

### 3. Installer les dépendances

```bash
python -m pip install -r requirements.txt
```

Pour développer et lancer les tests :

```bash
python -m pip install -r requirements-dev.txt
```

### 4. Créer la base de données et son utilisateur

L'application se connecte avec un **compte non privilégié**, dédié, qui n'a de droits que sur
sa propre base. Connectez-vous à PostgreSQL avec un compte administrateur :

```sql
CREATE ROLE epicevents_app WITH LOGIN;
\password epicevents_app
CREATE DATABASE epicevents OWNER epicevents_app;
REVOKE ALL ON DATABASE epicevents FROM PUBLIC;
```

> Le `REVOKE` ferme la base à tout autre rôle : par défaut, PostgreSQL autorise n'importe quel
> utilisateur à s'y connecter.

### 5. Configurer les variables d'environnement

Aucun identifiant n'est écrit dans le code. Copiez le modèle et renseignez-le :

```bash
cp .env.example .env
```

| Variable | Rôle |
|---|---|
| `DB_HOST`, `DB_PORT`, `DB_NAME` | connexion à PostgreSQL |
| `DB_USER`, `DB_PASSWORD` | identifiants du compte applicatif |
| `JWT_SECRET` | clé de signature des jetons — voir ci-dessous |
| `SENTRY_DSN` | journalisation ; laisser vide pour la désactiver |

Générez une clé de signature robuste (32 octets) :

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

> Le fichier `.env` est ignoré par git et ne doit **jamais** être versionné.

---

## Premier démarrage

### Créer les tables

```bash
python create_tables.py
```

Le script est idempotent : relancé, il ne recrée pas une table existante.

### Amorcer l'application

```bash
python init_db.py
```

Il crée les trois rôles (`gestion`, `commercial`, `support`) puis demande les informations du
**premier compte de gestion**.

> **Garde-fou** : ce compte n'est créé que si la table `collaborateur` est vide. Une fois le
> premier collaborateur en place, le script devient inerte — il est impossible de se créer un
> compte administrateur en le relançant.

### Se connecter

```bash
python epicevents.py auth login
```

---

## Utilisation

Toutes les commandes suivent la forme `python epicevents.py <groupe> <commande>`.
L'aide est disponible à chaque niveau : `--help`.

### Authentification

| Commande | Effet |
|---|---|
| `auth login` | se connecter et recevoir un jeton (valable 24 h) |
| `auth logout` | supprimer le jeton |
| `auth statut` | afficher le collaborateur connecté |

### Clients

```bash
python epicevents.py clients lister
python epicevents.py clients creer --nom "Kevin Casey" --email kevin@startup.io --telephone "+678 123" --entreprise "Cool Startup"
python epicevents.py clients modifier 1 --telephone 0611223344
```

### Contrats

```bash
python epicevents.py contrats lister
python epicevents.py contrats lister --non-signes
python epicevents.py contrats lister --non-soldes
python epicevents.py contrats lister --les-miens
python epicevents.py contrats creer --client 1 --montant 12000 --reste 12000
python epicevents.py contrats modifier 1 --signer
```

### Évènements

```bash
python epicevents.py evenements lister
python epicevents.py evenements lister --sans-support
python epicevents.py evenements lister --les-miens
python epicevents.py evenements creer --contrat 1 --nom "Mariage Ouick" --debut "04/06/2027 13:00" --fin "05/06/2027 02:00" --lieu "Candé-sur-Beuvron" --invites 75 --notes "Par la rivière"
python epicevents.py evenements modifier 1 --invites 80
python epicevents.py evenements assigner-support 1 --support 3
```

### Collaborateurs

```bash
python epicevents.py collaborateurs lister
python epicevents.py collaborateurs creer --numero EE-101 --nom "Bill Boquet" --email bill@epicevents.fr --role commercial
python epicevents.py collaborateurs modifier 2 --role support
python epicevents.py collaborateurs supprimer 2
```

Les options omises sont demandées interactivement. Les mots de passe ne s'affichent jamais à
l'écran et ne transitent pas par la ligne de commande — ils n'apparaissent donc pas dans
l'historique du terminal.

---

## Rôles et permissions

Chaque collaborateur appartient à un département, qui détermine ses droits. Le rôle est une
**relation vers une table**, jamais une valeur écrite en dur dans la table des collaborateurs.

| Action | Gestion | Commercial | Support |
|---|:---:|:---:|:---:|
| Lire clients, contrats, évènements | ✅ | ✅ | ✅ |
| Créer, modifier, supprimer un collaborateur | ✅ | | |
| Créer un client | | ✅ *(associé automatiquement)* | |
| Modifier un client | | ✅ *les siens* | |
| Créer un contrat | ✅ | | |
| Modifier un contrat | ✅ *tous* | ✅ *les siens* | |
| Créer un évènement | | ✅ *les siens, contrat signé* | |
| Modifier un évènement | ✅ *tous* | | ✅ *les siens* |
| Assigner un support à un évènement | ✅ | | |

Deux niveaux d'autorisation sont appliqués successivement :

1. **par rôle** — le département autorise-t-il cette action ? (`epicevents/permissions.py`)
2. **par propriété** — cet objet appartient-il à l'utilisateur ? (`epicevents/services/`)

Un commercial possède le droit de modifier un client, mais seulement **ses** clients : les deux
vérifications sont nécessaires et indépendantes.

---

## Schéma de la base de données

Le diagramme est dans [`docs/erd.md`](docs/erd.md). Il est **généré depuis les modèles** et ne
peut donc pas diverger du code :

```bash
python generate_erd.py
```

```
role ──1─∞──► collaborateur ──1─∞──► client ──1─∞──► contrat ──1─∞──► evenement
                     └──────────── support (0 ou 1) ────────────────────┘
```

Deux décisions de modélisation :

- **`evenement` ne stocke ni le client ni le commercial.** Ils sont atteints par le chemin
  `evenement → contrat → client → commercial`. Dupliquer l'information ouvrirait la porte à des
  incohérences qu'aucune règle ne permettrait de trancher.
- **`evenement.support_id` est nullable.** Un évènement est créé par le commercial dès la
  signature du contrat ; la gestion lui assigne un support ensuite. C'est ce qui rend possible
  le filtre « évènements sans support ».

---

## Architecture

```
epicevents/
├── models/          la forme des données (SQLAlchemy)
├── repositories/    l'accès aux données — lecture (motif Repository / DAO)
├── services/        les règles métier — permissions, propriété, validation
├── cli/             l'interface utilisateur (click + rich)
├── auth.py          authentification et jetons
├── permissions.py   autorisation par rôle
├── securite.py      hachage des mots de passe
└── journalisation.py  Sentry
```

Chaque couche ne s'adresse qu'à celle du dessous :

| Couche | Question à laquelle elle répond |
|---|---|
| **CLI** | comment demander et afficher ? |
| **Services** | a-t-il le droit ? cet objet est-il le sien ? |
| **Repositories** | comment aller chercher ou écrire ? |
| **Models** | quelle est la forme des données ? |

Le CLI ne contient **aucune** règle métier, et les repositories **aucune** vérification de
droits. Cette séparation limite mécaniquement ce que chaque partie du code peut révéler :
`permissions.py` ne voit jamais un client, il lui est donc impossible de divulguer une donnée
métier dans un message d'erreur.

### Scripts utilitaires

| Script | Rôle |
|---|---|
| `create_tables.py` | crée les tables manquantes (idempotent) |
| `reset_tables.py` | supprime puis recrée les tables — **développement uniquement** |
| `init_db.py` | crée les rôles et le premier compte de gestion |
| `generate_erd.py` | régénère `docs/erd.md` depuis les modèles |

---

## Choix de sécurité

### Injections SQL

Toutes les requêtes passent par l'ORM SQLAlchemy, qui produit du **SQL paramétré** : les valeurs
sont transmises séparément de la requête et ne peuvent jamais être interprétées comme du code.

```sql
SELECT ... FROM contrat WHERE contrat.id = %(pk_1)s
```

La valeur n'apparaît pas dans le texte de la requête. Aucune chaîne SQL n'est construite par
concaténation dans le projet.

### Mots de passe

Hachés avec **argon2id** (`argon2-cffi`), avec un sel aléatoire par mot de passe. Le mot de
passe en clair n'est jamais écrit en base, jamais journalisé, jamais affiché. Deux comptes
partageant le même mot de passe ont des empreintes différentes, ce qui rend inopérantes les
attaques par table précalculée.

### Authentification

Après connexion, l'utilisateur reçoit un **JWT** signé (HS256) contenant uniquement son
identifiant, son rôle et une date d'expiration — ni email, ni mot de passe : un JWT est signé
mais **non chiffré**, tout le monde peut le lire.

Le jeton est stocké dans `~/.epicevents_token`. Ce choix permet de rester connecté d'un terminal
à l'autre, et évite que le jeton apparaisse dans l'historique des commandes — ce qui serait le
cas s'il était passé en argument.

Un jeton **expiré**, **falsifié** ou **signé avec une autre clé** est refusé.

### Moindre privilège

- Le compte PostgreSQL de l'application n'a **aucun attribut** : ni `SUPERUSER`, ni `CREATEDB`,
  ni `CREATEROLE`. Il ne peut agir que sur la base `epicevents`.
- Les données sont cloisonnées par les deux niveaux d'autorisation décrits plus haut.

### Validation des entrées

Les données sont contrôlées au plus tôt, avant d'atteindre le code métier : types (`type=int`),
valeurs autorisées (`click.Choice`), format des dates, existence des objets référencés,
cohérence métier (une date de fin postérieure à la date de début).

### Gestion des erreurs

Aucune trace d'exécution n'est affichée à l'utilisateur : une traceback révélerait
l'arborescence du serveur, les bibliothèques utilisées et leurs versions — donc leurs failles
connues. L'utilisateur reçoit un message d'une ligne ; la trace complète est envoyée à Sentry.

Les erreurs d'authentification ne distinguent pas « email inconnu » de « mot de passe
incorrect », afin d'empêcher l'énumération des comptes.

### Secrets

Aucun identifiant, clé ou mot de passe n'est présent dans le code ni dans le dépôt. Tout est lu
dans `.env`, ignoré par git. Le fichier `.env.example` documente les variables attendues sans
contenir de valeur.

### Journalisation

Sentry reçoit les exceptions inattendues, chaque création, modification ou suppression de
collaborateur, et chaque signature de contrat. L'option `send_default_pii` est désactivée :
aucune donnée personnelle (adresse IP, en-têtes) n'est transmise.

---

## Tests

```bash
python -m pytest
```

Avec le rapport de couverture :

```bash
python -m pytest --cov=epicevents --cov-report=term-missing
```

**54 tests** couvrant le hachage, l'authentification, les jetons, les deux niveaux
d'autorisation et les règles métier.

Les tests s'exécutent sur une base dédiée, `epicevents_test`, jamais sur la base de production.
À créer une fois :

```sql
CREATE DATABASE epicevents_test OWNER epicevents_app;
REVOKE ALL ON DATABASE epicevents_test FROM PUBLIC;
```

Les tables sont recréées avant chaque test : aucun test ne dépend de l'ordre d'exécution ni de
l'état laissé par un autre.

### Couverture et arbitrage

| Module | Couverture |
|---|---|
| `securite.py`, `permissions.py` | 100 % |
| `services/` | 95 à 100 % |
| `models/` | ~94 % |
| `auth.py` | 79 % |
| `cli/`, `repositories/` | non couverts directement |

L'effort a été porté sur **ce qui décide** : le hachage, les autorisations et les règles métier.
L'affichage des tableaux et les requêtes de lecture sont vérifiés manuellement. Les repositories
sont traversés par les tests de services, sans être appelés directement.
