"""Génère le diagramme entité-relation (ERD) à partir des modèles SQLAlchemy.

Usage :
    python generate_erd.py

Écrit le diagramme au format Mermaid dans docs/erd.md.
Comme il est produit à partir du code, il ne peut pas diverger des modèles.
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


def construire_diagramme() -> str:
    """Assemble le diagramme Mermaid a partir des metadonnees des modeles."""
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
        "Diagramme généré automatiquement à partir des modèles SQLAlchemy\n"
        "(`python generate_erd.py`). Il reflète donc exactement la base implémentée.\n\n"
        "```mermaid\n" + construire_diagramme() + "\n```\n"
    )
    with open("docs/erd.md", "w", encoding="utf-8", newline="\n") as fichier:
        fichier.write(contenu)
    print("Diagramme ecrit dans docs/erd.md")


if __name__ == "__main__":
    main()
