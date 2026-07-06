-- ============================================================================
-- 03_jointures.sql
-- Jointures : INNER JOIN, LEFT JOIN, self-join, jointure multiple.
-- ============================================================================


-- Question metier : quel est le chiffre d'affaires total et le nombre de
-- ventes par categorie de produit ?
-- Technique SQL : INNER JOIN entre la table de faits et une dimension.
SELECT
    p.category AS categorie,
    COUNT(*) AS nb_ventes,
    ROUND(SUM(f.revenue), 2) AS chiffre_affaires
FROM fact_sales AS f
INNER JOIN dim_product AS p
    ON f.product_key = p.product_key
GROUP BY
    p.category
ORDER BY
    chiffre_affaires DESC;


-- Question metier : combien de ventes ne sont rattachees a aucun client
-- identifie (ventes anonymes en caisse) ?
-- Technique SQL : LEFT JOIN pour conserver les lignes sans correspondance,
-- puis filtre sur la cle de jointure absente (customer_key IS NULL).
SELECT
    COUNT(*) AS nb_ventes_anonymes
FROM fact_sales AS f
LEFT JOIN dim_customer AS c
    ON f.customer_key = c.customer_key
WHERE
    c.customer_key IS NULL;


-- Question metier : quels magasins physiques partagent la meme ville et sont
-- donc en concurrence directe l'un avec l'autre ?
-- Technique SQL : self-join sur dim_store (comparaison d'une table avec elle-meme).
SELECT
    s1.city AS ville,
    s1.store_name AS magasin_1,
    s2.store_name AS magasin_2
FROM dim_store AS s1
INNER JOIN dim_store AS s2
    ON s1.city = s2.city
   AND s1.store_key < s2.store_key   -- evite les doublons (A,B)/(B,A) et l'auto-appariement
WHERE s1.store_type != 'En ligne'
  AND s2.store_type != 'En ligne'
ORDER BY
    ville;


-- Question metier : quel est le detail complet (produit, magasin, client,
-- date) des ventes du mois de decembre 2025, le dernier mois d'historique ?
-- Technique SQL : jointure multiple traversant l'integralite du schema en
-- etoile (une table de faits + ses quatre dimensions).
SELECT
    d.full_date AS date_vente,
    pr.product_name AS produit,
    pr.category AS categorie,
    st.store_name AS magasin,
    st.city AS ville,
    COALESCE(cu.customer_name, 'Anonyme') AS client,
    f.quantity AS quantite,
    f.revenue AS chiffre_affaires
FROM fact_sales AS f
INNER JOIN dim_date AS d
    ON f.date_key = d.date_key
INNER JOIN dim_product AS pr
    ON f.product_key = pr.product_key
INNER JOIN dim_store AS st
    ON f.store_key = st.store_key
LEFT JOIN dim_customer AS cu
    ON f.customer_key = cu.customer_key
WHERE d.year = 2025
  AND d.month = 12
ORDER BY
    d.full_date DESC, chiffre_affaires DESC
LIMIT 20;
