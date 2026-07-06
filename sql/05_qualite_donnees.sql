-- ============================================================================
-- 05_qualite_donnees.sql
-- Controles qualite : integrite referentielle, nulls, doublons, valeurs
-- aberrantes. Ces requetes sont concues pour trouver les anomalies injectees
-- volontairement par data/generate_data.py (voir sa docstring).
-- ============================================================================


-- Question metier : existe-t-il des ventes qui referencent un produit
-- inexistant dans le catalogue ?
-- Technique SQL : LEFT JOIN puis filtre sur la cle de la dimension absente
-- (IS NULL). C'est la methode standard pour verifier une integrite
-- referentielle qui n'est pas imposee par une contrainte FOREIGN KEY
-- (volontairement absente ici, cf. sql/00_schema.sql).
SELECT
    COUNT(*) AS nb_lignes_orphelines
FROM fact_sales AS f
LEFT JOIN dim_product AS p
    ON f.product_key = p.product_key
WHERE
    p.product_key IS NULL;


-- Question metier : existe-t-il des ventes qui referencent un magasin
-- inexistant ?
-- Technique SQL : meme principe, LEFT JOIN puis IS NULL.
SELECT
    COUNT(*) AS nb_lignes_orphelines
FROM fact_sales AS f
LEFT JOIN dim_store AS s
    ON f.store_key = s.store_key
WHERE
    s.store_key IS NULL;


-- Question metier : existe-t-il des ventes rattachees a un client qui
-- n'existe pas reellement dans la base (different d'une vente simplement
-- anonyme, ou customer_key est NULL) ?
-- Technique SQL : LEFT JOIN puis IS NULL, combine a une condition sur la
-- colonne d'origine pour exclure les vraies ventes anonymes.
SELECT
    COUNT(*) AS nb_lignes_orphelines
FROM fact_sales AS f
LEFT JOIN dim_customer AS c
    ON f.customer_key = c.customer_key
WHERE
    f.customer_key IS NOT NULL
    AND c.customer_key IS NULL;


-- Question metier : les colonnes qui doivent toujours etre renseignees
-- contiennent-elles des valeurs manquantes ?
-- Technique SQL : CASE WHEN combine a SUM pour compter des occurrences selon
-- une condition, colonne par colonne, en une seule passe sur la table (pas de
-- customer_key ici : un client NULL y est une vente anonyme valide, pas un
-- defaut de saisie).
SELECT
    COUNT(*) AS nb_lignes_total,
    CAST(SUM(CASE WHEN date_key IS NULL THEN 1 ELSE 0 END) AS INTEGER) AS date_key_nulle,
    CAST(SUM(CASE WHEN product_key IS NULL THEN 1 ELSE 0 END) AS INTEGER) AS product_key_nulle,
    CAST(SUM(CASE WHEN store_key IS NULL THEN 1 ELSE 0 END) AS INTEGER) AS store_key_nulle,
    CAST(SUM(CASE WHEN quantity IS NULL THEN 1 ELSE 0 END) AS INTEGER) AS quantity_nulle,
    CAST(SUM(CASE WHEN revenue IS NULL THEN 1 ELSE 0 END) AS INTEGER) AS revenue_nulle
FROM fact_sales;


-- Question metier : certaines ventes ont-elles ete enregistrees plusieurs
-- fois a l'identique (par exemple un double scan en caisse) ?
-- Technique SQL : GROUP BY sur la cle metier complete de la vente puis
-- HAVING COUNT(*) > 1 pour isoler les combinaisons dupliquees.
SELECT
    date_key,
    product_key,
    store_key,
    customer_key,
    quantity,
    unit_price,
    COUNT(*) AS nb_occurrences
FROM fact_sales
GROUP BY
    date_key, product_key, store_key, customer_key, quantity, unit_price
HAVING
    COUNT(*) > 1
ORDER BY
    nb_occurrences DESC;


-- Question metier : quelles lignes de vente ont une quantite anormalement
-- elevee (superieure a 20 unites sur une seule ligne, largement au-dessus du
-- plus gros panier professionnel observe), a verifier manuellement ?
-- Technique SQL : WHERE avec un seuil metier simple.
SELECT
    sale_id,
    product_key,
    quantity,
    unit_price,
    revenue
FROM fact_sales
WHERE
    quantity > 20
ORDER BY
    quantity DESC;


-- Question metier : quelles ventes ont un prix unitaire tres eloigne du prix
-- catalogue du produit concerne (erreur de saisie possible) ? Un seuil fixe
-- ne fonctionnerait pas ici (un produit High-tech coute naturellement plus
-- cher qu'un produit d'epicerie) : on compare donc chaque vente a son propre
-- prix catalogue plutot qu'a un seuil unique.
-- Technique SQL : JOIN avec la dimension produit, puis WHERE sur le rapport
-- entre le prix de vente reel et le prix catalogue.
SELECT
    f.sale_id,
    p.product_name AS produit,
    p.category AS categorie,
    f.unit_price AS prix_vente,
    p.unit_price AS prix_catalogue
FROM fact_sales AS f
INNER JOIN dim_product AS p
    ON f.product_key = p.product_key
WHERE
    f.unit_price > 2 * p.unit_price
ORDER BY
    f.unit_price DESC;
