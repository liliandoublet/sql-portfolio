-- ============================================================================
-- 00_schema.sql
-- Definition du schema en etoile retail : 4 dimensions + 1 table de faits.
-- ============================================================================
-- Remarque de conception : aucune contrainte FOREIGN KEY n'est declaree sur
-- fact_sales. Le jeu de donnees contient volontairement quelques cles
-- orphelines (voir data/generate_data.py) afin que sql/05_qualite_donnees.sql
-- puisse demontrer comment les detecter par la requete plutot que de les
-- voir rejetees silencieusement au chargement.

CREATE TABLE dim_date (
    date_key      INTEGER PRIMARY KEY,   -- format AAAAMMJJ, ex. 20240115
    full_date     DATE NOT NULL,
    year          INTEGER NOT NULL,
    quarter       INTEGER NOT NULL,
    month         INTEGER NOT NULL,
    month_name    VARCHAR NOT NULL,
    day           INTEGER NOT NULL,
    day_of_week   INTEGER NOT NULL,      -- 1 = lundi ... 7 = dimanche
    day_name      VARCHAR NOT NULL,
    week_of_year  INTEGER NOT NULL,
    is_weekend    BOOLEAN NOT NULL
);

CREATE TABLE dim_product (
    product_key   INTEGER PRIMARY KEY,
    product_name  VARCHAR NOT NULL,
    category      VARCHAR NOT NULL,
    subcategory   VARCHAR NOT NULL,
    brand         VARCHAR NOT NULL,
    unit_cost     DECIMAL(10, 2) NOT NULL,
    unit_price    DECIMAL(10, 2) NOT NULL
);

CREATE TABLE dim_store (
    store_key     INTEGER PRIMARY KEY,
    store_name    VARCHAR NOT NULL,
    store_type    VARCHAR NOT NULL,      -- Centre-ville / Peripherie / En ligne
    city          VARCHAR NOT NULL,
    region        VARCHAR NOT NULL,
    opening_date  DATE NOT NULL
);

CREATE TABLE dim_customer (
    customer_key  INTEGER PRIMARY KEY,
    customer_name VARCHAR NOT NULL,
    segment       VARCHAR NOT NULL,      -- Particulier / Professionnel
    city          VARCHAR NOT NULL,
    region        VARCHAR NOT NULL,
    signup_date   DATE NOT NULL
);

CREATE TABLE fact_sales (
    sale_id        BIGINT PRIMARY KEY,
    date_key       INTEGER NOT NULL,     -- reference logique dim_date
    product_key    INTEGER NOT NULL,     -- reference logique dim_product (peut etre orpheline, cf. remarque ci-dessus)
    store_key      INTEGER NOT NULL,     -- reference logique dim_store (peut etre orpheline)
    customer_key   INTEGER,              -- NULL = vente anonyme (pas de carte de fidelite)
    quantity       DOUBLE,               -- DOUBLE (et non INTEGER) car quelques valeurs sont NULL par construction
    unit_price     DECIMAL(10, 2) NOT NULL,
    discount_rate  DECIMAL(4, 2) NOT NULL,
    revenue        DECIMAL(12, 2) NOT NULL,
    cost           DECIMAL(12, 2) NOT NULL,
    margin         DECIMAL(12, 2) NOT NULL
);


-- ============================================================================
-- DDL complementaire : ALTER TABLE et DROP TABLE.
-- Demonstration isolee sur une table de test, sans lien avec le schema
-- ci-dessus, pour ne pas perturber le chargement des donnees qui suit.
-- ============================================================================

-- Creation d'une table de demonstration.
CREATE TABLE table_test (
    id   INTEGER PRIMARY KEY,
    nom  VARCHAR NOT NULL
);

-- Ajout d'une colonne apres coup (besoin qui apparait une fois la table en usage).
ALTER TABLE table_test ADD COLUMN commentaire VARCHAR;

-- Renommage d'une colonne (ex. pour clarifier son contenu).
ALTER TABLE table_test RENAME COLUMN nom TO nom_complet;

-- Suppression de la table de demonstration, devenue inutile.
DROP TABLE table_test;
