"""Génère les diagrammes de la base de données à partir des modèles SQLAlchemy.

Usage :
    python generate_erd.py

Écrit deux diagrammes Mermaid dans docs/erd.md :
  - une vue d'ensemble en notation UML (cardinalités 1 et *) ;
  - un schéma détaillé avec les colonnes et les contraintes.

Comme ils sont produits à partir du code, ils ne peuvent pas diverger des modèles.
"""

import os

from epicevents.models import Base

TYPES_SQL_VERS_MERMAID = {
    "INTEGER": "int",
    "VARCHAR": "string",
    "TEXT": "string",
    "DATETIME": "datetime",
    "TIMESTAMP": "datetime",
    "NUMERIC": "decimal",
    "BOOLEAN": "boolean",
}


def type_mermaid(colonne) -> str:
    """Traduit un type SQLAlchemy en type lisible par Mermaid."""
    nom = str(colonne.type).split("(")[0].upper()
    return TYPES_SQL_VERS_MERMAID.get(nom, "string")


def construire_cardinalites() -> str:
    """Assemble la vue d'ensemble en notation UML (1 et *).

    Mermaid rend les cardinalites explicitement dans un classDiagram, ce que
    ne fait pas un erDiagram (notation en patte d'oie). Les deux diagrammes
    decrivent le meme modele ; celui-ci se lit plus vite.
    """
    lignes = ["classDiagram"]
    for table in Base.metadata.sorted_tables:
        for colonne in table.columns:
            for fk in colonne.foreign_keys:
                cible = fk.column.table.name
                # Une cle etrangere facultative autorise zero occurrence cote parent.
                cote_parent = "0..1" if colonne.nullable else "1"
                lignes.append(
                    '    {} "{}" --> "*" {} : {}'.format(
                        cible.capitalize(),
                        cote_parent,
                        table.name.capitalize(),
                        colonne.name,
                    )
                )
    return "\n".join(lignes)


def construire_diagramme() -> str:
    """Assemble le schema detaille a partir des metadonnees des modeles."""
    lignes = ["erDiagram"]

    # Les liens entre tables, deduits des cles etrangeres.
    for table in Base.metadata.sorted_tables:
        for colonne in table.columns:
            for fk in colonne.foreign_keys:
                cible = fk.column.table.name
                # "|o" = zero ou un (colonne facultative), "||" = exactement un
                cardinalite = "|o" if colonne.nullable else "||"
                lignes.append(
                    '    {} {}--o{{ {} : "{}"'.format(
                        cible, cardinalite, table.name, colonne.name
                    )
                )

    # Les colonnes de chaque table.
    for table in Base.metadata.sorted_tables:
        lignes.append("")
        lignes.append("    {} {{".format(table.name))
        for colonne in table.columns:
            marques = []
            if colonne.primary_key:
                marques.append("PK")
            if colonne.foreign_keys:
                marques.append("FK")
            if colonne.unique:
                marques.append("UK")
            suffixe = " " + ",".join(marques) if marques else ""
            lignes.append(
                "        {} {}{}".format(type_mermaid(colonne), colonne.name, suffixe)
            )
        lignes.append("    }")

    return "\n".join(lignes)


def main() -> None:
    os.makedirs("docs", exist_ok=True)
    contenu = (
        "# Schéma de la base de données\n\n"
        "Diagrammes générés automatiquement à partir des modèles SQLAlchemy\n"
        "(`python generate_erd.py`). Ils reflètent donc exactement la base implémentée.\n\n"
        "## Vue d'ensemble — cardinalités\n\n"
        "```mermaid\n" + construire_cardinalites() + "\n```\n\n"
        "## Schéma détaillé — tables, colonnes et contraintes\n\n"
        "Notation entité-association : `||` exactement un · `|o` zéro ou un · "
        "`o{` plusieurs.\n"
        "`PK` clé primaire · `FK` clé étrangère · `UK` contrainte d'unicité.\n\n"
        "```mermaid\n" + construire_diagramme() + "\n```\n"
    )
    with open("docs/erd.md", "w", encoding="utf-8", newline="\n") as fichier:
        fichier.write(contenu)
    print("Diagrammes ecrits dans docs/erd.md")


if __name__ == "__main__":
    main()
