-- ── 1. Créer la base de données ──────────────────────────────────────────────
CREATE DATABASE IF NOT EXISTS ecommerce
    COMMENT 'Base de données du cas pratique Big Data';

USE ecommerce;


-- ── 2. Table externe sur le CSV brut HDFS ────────────────────────────────────
CREATE EXTERNAL TABLE IF NOT EXISTS transactions (
    transaction_id  STRING    COMMENT 'Identifiant unique de transaction',
    user_id         STRING    COMMENT 'Identifiant client',
    produit         STRING    COMMENT 'Nom du produit',
    categorie       STRING    COMMENT 'Catégorie produit',
    prix            DOUBLE    COMMENT 'Prix unitaire en EUR',
    quantite        INT       COMMENT 'Quantité commandée',
    pays            STRING    COMMENT 'Pays du client',
    ts              TIMESTAMP COMMENT 'Horodatage transaction',
    note_client     INT       COMMENT 'Note client 1 à 5',
    statut          STRING    COMMENT 'Statut de la commande',
    description     STRING    COMMENT 'Description texte libre'
)
COMMENT 'Table externe transactions e-commerce — 10 Go'
ROW FORMAT DELIMITED
    FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/data/transactions/'
TBLPROPERTIES ('skip.header.line.count' = '1');


-- ── 3. Table ORC optimisée ───────────────────────────────────────────────────
SET hive.exec.dynamic.partition      = true;
SET hive.exec.dynamic.partition.mode = nonstrict;

CREATE TABLE IF NOT EXISTS transactions_orc
    PARTITIONED BY (pays STRING)
    CLUSTERED BY (categorie) INTO 8 BUCKETS
    STORED AS ORC
    TBLPROPERTIES ('orc.compress' = 'SNAPPY')
AS
SELECT
    transaction_id,
    user_id,
    produit,
    categorie,
    prix,
    quantite,
    ts,
    note_client,
    statut,
    description,
    pays
FROM transactions;


-- ── 4. Vérifications ─────────────────────────────────────────────────────────
DESCRIBE FORMATTED transactions;

SELECT
    COUNT(*) AS total_lignes
FROM transactions;


-- ── 5. Requêtes d'exploration ─────────────────────────────────────────────────
SELECT
    categorie,
    COUNT(*)                        AS nb_transactions,
    ROUND(AVG(prix), 2)             AS prix_moyen,
    ROUND(SUM(prix * quantite), 2)  AS chiffre_affaires
FROM transactions
GROUP BY categorie
ORDER BY chiffre_affaires DESC;