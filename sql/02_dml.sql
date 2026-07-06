-- ============================================================================
-- 02_dml.sql
-- Bases du DML : INSERT, UPDATE, DELETE, verifies par SELECT a chaque etape.
-- ============================================================================
-- Le client cree ici (customer_key = 999999) est ajoute puis supprime dans ce
-- meme fichier : les autres fichiers du projet retrouvent donc toujours les
-- donnees d'origine, quel que soit l'ordre d'execution.


-- Question metier : un nouveau client vient de s'inscrire au programme de
-- fidelite en magasin, comment l'ajouter a la base ?
-- Technique SQL : INSERT INTO ... VALUES.
INSERT INTO dim_customer (customer_key, customer_name, segment, city, region, signup_date)
VALUES (999999, 'Julien Petit', 'Particulier', 'Paris', 'Ile-de-France', DATE '2026-01-15');


-- Verification : le nouveau client apparait-il bien dans la table ?
-- Technique SQL : SELECT avec WHERE sur la cle primaire.
SELECT
    customer_key,
    customer_name AS client,
    segment,
    city AS ville
FROM dim_customer
WHERE
    customer_key = 999999;


-- Question metier : ce client nous informe qu'il s'agit en realite d'un
-- compte professionnel, comment corriger son dossier ?
-- Technique SQL : UPDATE ... SET ... WHERE.
UPDATE dim_customer
SET segment = 'Professionnel'
WHERE
    customer_key = 999999;


-- Verification : le segment a-t-il bien ete mis a jour ?
SELECT
    customer_key,
    customer_name AS client,
    segment
FROM dim_customer
WHERE
    customer_key = 999999;


-- Question metier : ce client exerce son droit a l'oubli (RGPD) et demande
-- la suppression de son compte, comment y repondre ?
-- Technique SQL : DELETE FROM ... WHERE.
DELETE FROM dim_customer
WHERE
    customer_key = 999999;


-- Verification : le client a-t-il bien ete supprime (0 ligne attendue) ?
SELECT
    COUNT(*) AS nb_lignes_restantes
FROM dim_customer
WHERE
    customer_key = 999999;
