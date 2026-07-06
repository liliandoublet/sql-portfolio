-- ============================================================================
-- 04_agregations.sql
-- Agregations : GROUP BY, HAVING, COUNT / SUM / AVG / MIN / MAX.
-- ============================================================================


-- Question metier : quels produits generent plus de 15 000 euros de chiffre
-- d'affaires cumule sur toute la periode (produits "locomotives") ?
-- Technique SQL : GROUP BY avec filtre post-agregation HAVING.
SELECT
    pr.product_name AS produit,
    pr.category AS categorie,
    ROUND(SUM(f.revenue), 2) AS chiffre_affaires,
    SUM(f.quantity) AS quantite_vendue
FROM fact_sales AS f
INNER JOIN dim_product AS pr
    ON f.product_key = pr.product_key
GROUP BY
    pr.product_name, pr.category
HAVING
    SUM(f.revenue) > 15000
ORDER BY
    chiffre_affaires DESC;


-- Question metier : quel est le chiffre d'affaires total par region ?
-- Technique SQL : GROUP BY sur une seule colonne.
SELECT
    st.region AS region,
    ROUND(SUM(f.revenue), 2) AS chiffre_affaires
FROM fact_sales AS f
INNER JOIN dim_store AS st
    ON f.store_key = st.store_key
GROUP BY
    st.region
ORDER BY
    chiffre_affaires DESC;


-- Question metier : quel est le chiffre d'affaires total par annee ?
-- Technique SQL : GROUP BY sur une seule colonne, issue d'une jointure avec
-- la dimension date.
SELECT
    d.year AS annee,
    ROUND(SUM(f.revenue), 2) AS chiffre_affaires
FROM fact_sales AS f
INNER JOIN dim_date AS d
    ON f.date_key = d.date_key
GROUP BY
    d.year
ORDER BY
    annee;


-- Question metier : comment le chiffre d'affaires du canal en ligne
-- evolue-t-il par rapport aux magasins physiques, annee apres annee ?
-- Technique SQL : GROUP BY sur plusieurs colonnes (annee, type de magasin).
SELECT
    d.year AS annee,
    st.store_type AS type_magasin,
    ROUND(SUM(f.revenue), 2) AS chiffre_affaires
FROM fact_sales AS f
INNER JOIN dim_date AS d
    ON f.date_key = d.date_key
INNER JOIN dim_store AS st
    ON f.store_key = st.store_key
GROUP BY
    d.year, st.store_type
ORDER BY
    annee, type_magasin;


-- Question metier : comment se repartit le chiffre d'affaires par segment
-- de clientele et par type de magasin ?
-- Technique SQL : GROUP BY sur plusieurs colonnes en meme temps.
SELECT
    COALESCE(cu.segment, 'Anonyme') AS segment,
    st.store_type AS type_magasin,
    ROUND(SUM(f.revenue), 2) AS chiffre_affaires
FROM fact_sales AS f
INNER JOIN dim_store AS st
    ON f.store_key = st.store_key
LEFT JOIN dim_customer AS cu
    ON f.customer_key = cu.customer_key
GROUP BY
    COALESCE(cu.segment, 'Anonyme'), st.store_type
ORDER BY
    segment, type_magasin;


-- Question metier : quel est le prix moyen, minimum et maximum des produits
-- au sein de chaque categorie ?
-- Technique SQL : plusieurs fonctions d'agregation (AVG, MIN, MAX) dans la
-- meme requete.
SELECT
    category AS categorie,
    ROUND(AVG(unit_price), 2) AS prix_moyen,
    MIN(unit_price) AS prix_min,
    MAX(unit_price) AS prix_max
FROM dim_product
GROUP BY
    category
ORDER BY
    prix_moyen DESC;
