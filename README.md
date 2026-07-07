# SQL Toolbox : fondamentaux SQL sur un schéma en étoile retail

Un portfolio SQL couvrant les fondamentaux, du `CREATE TABLE` à la jointure, appliqué à un cas retail réaliste. Chaque requête répond à une vraie question métier et l'ensemble s'exécute en **une seule commande**, sans base de données à installer.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-OLAP-FFF000?logo=duckdb&logoColor=black)
![uv](https://img.shields.io/badge/uv-gestionnaire%20de%20paquets-DE5FE9?logo=uv&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-DDL%20%7C%20DML%20%7C%20jointures-4479A1?logo=postgresql&logoColor=white)

---

## Démarrage rapide

**Prérequis :** Python 3.11+ et [uv](https://docs.astral.sh/uv/).

```bash
uv run run.py
```

C'est tout. En quelques secondes, cette commande unique :

1. génère un jeu de données synthétique reproductible (seed fixe) dans `data/*.csv` ;
2. Crée une base DuckDB en mémoire et y charge ces données à partir du schéma `sql/00_schema.sql` ;
3. Exécute dans l'ordre les cinq fichiers SQL du dossier `sql/` et affiche, pour chaque requête, la question métier posée, la technique démontrée et un extrait lisible du résultat.

`uv` télécharge et installe automatiquement les dépendances (DuckDB, pandas, numpy) dans un environnement virtuel local lors du premier lancement. DuckDB s'exécute directement dans le processus Python.

---

## Pourquoi ce projet

La maîtrise des fondamentaux SQL (créer et faire évoluer une table, insérer/modifier/supprimer des données, croiser plusieurs tables, agréger) est le socle sur lequel repose toute analyse de données, et c'est ce socle que ce dépôt met en avant, proprement et sans détour. Chaque requête part d'une vraie question métier, reste dans un périmètre que je maîtrise réellement (pas de technique utilisée sans pouvoir l'expliquer en entretien), et suit un format commenté et formaté proprement. Pas de `SELECT *` de démonstration : uniquement du raisonnement métier traduit en SQL, sur un cas retail réaliste plutôt que des tables jouets.

---

## Ce que le projet démontre

- **DDL** : `CREATE TABLE`, `ALTER TABLE` (ajout et renommage de colonne), `DROP TABLE`.
- **DML** : `INSERT`, `UPDATE`, `DELETE`, chacun vérifié par un `SELECT` avant/après.
- **Sélection de base** : `WHERE`, `ORDER BY`, `LIMIT`, `DISTINCT`.
- **Jointures** : `INNER JOIN`, `LEFT JOIN`, self-join, et une jointure traversant l'intégralité du schéma en étoile.
- **Agrégations** : `GROUP BY` (une ou plusieurs colonnes) avec `HAVING`, `COUNT`/`SUM`/`AVG`/`MIN`/`MAX`.
- **Qualité de données** : intégrité référentielle (`LEFT JOIN`), valeurs manquantes (`CASE WHEN`), doublons (`GROUP BY`/`HAVING`), valeurs aberrantes (`WHERE` et `JOIN`, sans statistiques avancées).

---

## Modèle de données

Schéma en étoile classique : une table de faits, quatre dimensions.

| Table | Contenu | Volume |
|---|---|---|
| `fact_sales` | Une ligne = un produit vendu, dans un magasin, à une date donnée, à un client identifié ou non | ~100 000 lignes, 2 ans d'historique (2024-2025) |
| `dim_date` | Calendrier complet (année, trimestre, mois, jour de semaine...) | 731 jours |
| `dim_product` | Catalogue produit (8 catégories : Épicerie, Boissons, High-tech...) | 176 produits |
| `dim_store` | Points de vente | 19 magasins (18 physiques + 1 canal en ligne) |
| `dim_customer` | Base client | 6 000 clients (particuliers et professionnels) |

Les données sont générées par `data/generate_data.py` avec une saisonnalité réaliste (pic de fin d'année, creux estival), une tendance de croissance sur les deux ans, et une part du canal en ligne qui augmente avec le temps. Quelques anomalies sont injectées volontairement (doublons, valeurs aberrantes, clés orphelines, valeurs manquantes) : elles servent de terrain de jeu concret à `sql/05_qualite_donnees.sql`, conçu pour les détecter.

---

## Tour des fichiers SQL

| Fichier | Techniques démontrées | Exemple de question métier |
|---|---|---|
| `00_schema.sql` | `CREATE TABLE`, `ALTER TABLE`, `DROP TABLE` | Comment définir le schéma en étoile, puis faire évoluer une table existante ? |
| `01_selection.sql` | `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `DISTINCT` | Quels sont les 10 produits les plus chers du catalogue ? |
| `02_dml.sql` | `INSERT`, `UPDATE`, `DELETE` | Un client s'inscrit, change de statut puis exerce son droit à l'oubli : comment gérer son cycle de vie ? |
| `03_jointures.sql` | `INNER JOIN`, `LEFT JOIN`, self-join, jointure multiple | Quels magasins d'une même ville sont en concurrence directe ? |
| `04_agregations.sql` | `GROUP BY`, `HAVING`, `COUNT`/`SUM`/`AVG`/`MIN`/`MAX` | Quels produits génèrent plus de 15 000 € de chiffre d'affaires cumulé ? |
| `05_qualite_donnees.sql` | `LEFT JOIN` (anti-jointure), `CASE WHEN`, `GROUP BY`/`HAVING` | La table de faits contient-elle des clés orphelines ou des doublons ? |

Chaque requête est précédée de deux lignes de commentaire (question métier, puis technique SQL démontrée), visibles aussi bien en console qu'en lisant directement les fichiers `.sql`.

Aperçu d'une requête de `05_qualite_donnees.sql` : plutôt qu'un seuil fixe (un produit High-tech coûte naturellement plus cher qu'un produit d'épicerie), chaque vente est comparée à son propre prix catalogue via une jointure :

```
 sale_id                    produit        categorie  prix_vente  prix_catalogue
    8054 Levi's Vetements homme n22   Textile & Mode      367.84           57.57
   76582    Eram Vetements femme n1   Textile & Mode      271.23           41.86
   45816  Nestle Lait infantile n10             Bebe      122.44           13.74
```

---

## Enseignements clés

Quelques constats tirés directement des requêtes de `03_jointures.sql`, `04_agregations.sql` et `05_qualite_donnees.sql` :

1. **Effet Pareto sur la marge.** La catégorie High-tech concentre 46 % du chiffre d'affaires pour à peine 7 % des ventes en volume : une poignée de références premium porte l'essentiel de la marge, un point à surveiller au niveau des stocks.
2. **Bascule vers le e-commerce.** Le chiffre d'affaires progresse de 26 % entre 2024 et 2025, porté notamment par le canal en ligne, qui passe de 8 % à 13 % du chiffre d'affaires total sur la période.
3. **Angle mort côté client.** 15 % des ventes ne sont rattachées à aucun client identifié, autant de données invisibles pour le programme de fidélité et pour toute analyse client future.
4. **Une base saine mais pas parfaite.** Les contrôles qualité identifient précisément 15 lignes à clé de dimension invalide, 63 doublons probables et 25 valeurs aberrantes (quantité ou prix) : moins de 0,1 % des lignes, mais des anomalies concrètes et actionnables plutôt qu'un simple "ça a l'air propre".

---

## Structure du dépôt

```
.
├── README.md
├── pyproject.toml
├── run.py                        Point d'entrée unique (uv run run.py)
├── data/
│   └── generate_data.py          Génération du jeu de données synthétique
└── sql/
    ├── 00_schema.sql              DDL : CREATE TABLE, ALTER TABLE, DROP TABLE
    ├── 01_selection.sql           SELECT, WHERE, ORDER BY, LIMIT, DISTINCT
    ├── 02_dml.sql                 INSERT, UPDATE, DELETE
    ├── 03_jointures.sql           INNER JOIN, LEFT JOIN, self-join, jointure multiple
    ├── 04_agregations.sql         GROUP BY, HAVING, COUNT/SUM/AVG/MIN/MAX
    └── 05_qualite_donnees.sql     Contrôles qualité des données
```

---

## Stack technique

- **Python 3.11+**
- **DuckDB** : moteur SQL analytique embarqué (OLAP), sans serveur à installer, performant sur des volumes de plusieurs millions de lignes.
- **uv** : gestion de l'environnement et des dépendances via `pyproject.toml`, pour une installation reproductible en une commande.
- **pandas / numpy** : utilisés uniquement pour la génération du jeu de données synthétique, pas pour l'analyse, qui reste entièrement en SQL.

---

## Note sur les données

Toutes les données sont synthétiques, générées avec une seed fixe (42) pour une reproductibilité totale d'une exécution à l'autre. Aucune donnée réelle n'est utilisée.
