#!/bin/bash
set -e
echo '=== Création de la structure HDFS ==='
docker exec namenode hdfs dfs -mkdir -p /data/transactions
docker exec namenode hdfs dfs -mkdir -p /data/resultats
docker exec namenode hdfs dfs -mkdir -p /user/hive/warehouse
docker exec namenode hdfs dfs -chmod -R 777 /data
docker exec namenode hdfs dfs -chmod -R 777 /user

echo '=== Copie du CSV dans le conteneur NameNode ==='
docker cp /data/transactions_10gb.csv namenode:/tmp/transactions_10gb.csv

echo '=== Upload vers HDFS (peut prendre plusieurs minutes) ==='
docker exec namenode hdfs dfs -put -f \
  /data/transactions_10gb.csv /data/transactions/

echo '=== Vérification de l upload ==='
docker exec namenode hdfs dfs -ls -h /data/transactions/

echo '=== Rapport de fragmentation ==='
docker exec namenode hdfs fsck /data/transactions/ -files -blocks | tail -10

echo '=== Terminé ==='

# Lancer le script :
# chmod +x scripts/setup_hdfs.sh && bash scripts/setup_hdfs.sh