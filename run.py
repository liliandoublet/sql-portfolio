"""
Point d'entree unique du projet : regenere les donnees synthetiques, charge le
schema en etoile dans DuckDB, puis execute et affiche chaque requete SQL des
fichiers sql/01 a sql/05 dans l'ordre pedagogique du README.

Usage : uv run run.py
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

import duckdb
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent / "data"))
import generate_data  # noqa: E402

ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"
SQL_DIR = ROOT_DIR / "sql"

TABLE_FILES = [
    ("dim_date", "dim_date.csv"),
    ("dim_product", "dim_product.csv"),
    ("dim_store", "dim_store.csv"),
    ("dim_customer", "dim_customer.csv"),
    ("fact_sales", "fact_sales.csv"),
]

QUERY_FILES = [
    "01_selection.sql",
    "02_dml.sql",
    "03_jointures.sql",
    "04_agregations.sql",
    "05_qualite_donnees.sql",
]

PREVIEW_ROWS = 8


def print_title(text: str, char: str = "=") -> None:
    print(f"\n{char * 78}\n{text}\n{char * 78}")


def build_database() -> duckdb.DuckDBPyConnection:
    """Regenere les CSV sources (seed fixe = resultat identique a chaque
    execution) puis construit une base DuckDB en memoire a partir du schema
    et des fichiers CSV."""
    print_title("1. GENERATION DES DONNEES SYNTHETIQUES")
    counts = generate_data.generate(DATA_DIR)
    for table, count in counts.items():
        print(f"  - {table:15s} {count:>8,d} lignes".replace(",", " "))

    con = duckdb.connect(database=":memory:")
    con.execute((SQL_DIR / "00_schema.sql").read_text(encoding="utf-8"))

    print_title("2. CHARGEMENT DANS DUCKDB")
    for table, filename in TABLE_FILES:
        csv_path = DATA_DIR / filename
        con.execute(f"COPY {table} FROM '{csv_path.as_posix()}' (HEADER)")
        n_rows = con.sql(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  - {table:15s} charge depuis {filename:20s} ({n_rows:>8,d} lignes)".replace(",", " "))

    return con


def split_statements(sql_text: str) -> list[tuple[str, str]]:
    """Decoupe un fichier .sql en blocs (commentaire, requete). Un bloc
    commence par une suite de lignes de commentaire ('-- ...') qui expliquent
    la question metier et la technique demontree, suivies de la requete
    elle-meme jusqu'au ';' terminal.

    Le decoupage se fait ligne par ligne (et non par un split global sur ';')
    car les commentaires peuvent eux-memes contenir des ';' en tant que
    ponctuation ; seul un ';' en fin de ligne de code termine une requete."""
    # Supprime le bandeau d'en-tete du fichier (entre deux lignes de '=').
    sql_text = re.sub(r"-- =+\n.*?-- =+\n", "", sql_text, flags=re.DOTALL)

    blocks = []
    comment_lines: list[str] = []
    code_lines: list[str] = []

    for line in sql_text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("--"):
            comment_lines.append(stripped)
        elif stripped or code_lines:
            code_lines.append(line)
            if stripped.endswith(";"):
                comment = "\n".join(l.strip("- ").strip() for l in comment_lines if l.strip())
                query = "\n".join(code_lines).strip()
                blocks.append((comment, query))
                comment_lines, code_lines = [], []

    return blocks


def run_query_file(con: duckdb.DuckDBPyConnection, filename: str) -> None:
    print_title(f"FICHIER : sql/{filename}", char="-")
    sql_text = (SQL_DIR / filename).read_text(encoding="utf-8")

    for i, (comment, query) in enumerate(split_statements(sql_text), start=1):
        print(f"\n[{filename} #{i}]")
        print(comment)
        result = con.sql(query)
        if result is None:
            # DDL (CREATE/ALTER/DROP) et DML (INSERT/UPDATE/DELETE) ne renvoient
            # aucune ligne : on se contente de confirmer l'execution.
            print("(instruction executee)")
            continue
        df = result.df()
        with pd.option_context("display.max_columns", None, "display.width", 120):
            print(df.head(PREVIEW_ROWS).to_string(index=False))
        if len(df) > PREVIEW_ROWS:
            print(f"... ({len(df)} lignes au total, {PREVIEW_ROWS} premieres affichees)")


def main() -> None:
    start = time.time()
    print_title("PORTFOLIO SQL ANALYTIQUE, SCHEMA EN ETOILE RETAIL (DUCKDB)")

    con = build_database()

    for filename in QUERY_FILES:
        run_query_file(con, filename)

    elapsed = time.time() - start
    print_title(f"TERMINE EN {elapsed:.1f}S. {len(QUERY_FILES)} FICHIERS SQL EXECUTES.")


if __name__ == "__main__":
    main()
