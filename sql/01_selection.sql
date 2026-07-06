-- ============================================================================
-- 01_selection.sql
-- Bases du SELECT : WHERE, ORDER BY, LIMIT, DISTINCT, sur une seule table.
-- ============================================================================


-- Question metier : quelles categories de produits l'enseigne propose-t-elle ?
-- Technique SQL : SELECT DISTINCT pour lister les valeurs uniques d'une colonne.
SELECT DISTINCT
    category AS categorie
FROM dim_product
ORDER BY
    categorie;


-- Question metier : quels sont les produits de la categorie High-tech, du
-- plus cher au moins cher ?
-- Technique SQL : SELECT avec WHERE (filtre) et ORDER BY (tri).
SELECT
    product_name AS produit,
    brand AS marque,
    unit_price AS prix_vente
FROM dim_product
WHERE
    category = 'High-tech'
ORDER BY
    prix_vente DESC;


-- Question metier : quels clients se sont inscrits au programme de fidelite
-- au cours de l'annee 2025 ?
-- Technique SQL : WHERE sur une plage de dates, ORDER BY.
SELECT
    customer_name AS client,
    segment,
    signup_date AS date_inscription
FROM dim_customer
WHERE
    signup_date >= DATE '2025-01-01'
    AND signup_date <= DATE '2025-12-31'
ORDER BY
    date_inscription;


-- Question metier : quelles lignes de vente ont genere plus de 500 euros de
-- chiffre d'affaires a elles seules ?
-- Technique SQL : WHERE sur une colonne numerique, ORDER BY, LIMIT.
SELECT
    sale_id AS vente_id,
    date_key,
    product_key,
    quantity AS quantite,
    revenue AS chiffre_affaires
FROM fact_sales
WHERE
    revenue > 500
ORDER BY
    chiffre_affaires DESC
LIMIT 20;


-- Question metier : quels sont les 10 produits les plus chers du catalogue ?
-- Technique SQL : ORDER BY combine a LIMIT pour obtenir un "top N".
SELECT
    product_name AS produit,
    category AS categorie,
    unit_price AS prix_vente
FROM dim_product
ORDER BY
    prix_vente DESC
LIMIT 10;
