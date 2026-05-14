#!/bin/bash
set -e

# Chemin absolu vers les données (évite les problèmes avec sudo et ~)
DATA_PATH="/home/princesse/Bureau/Big-Data-Projet/data/transactions_10gb.csv"

echo '=== Création de la structure HDFS ==='
docker exec namenod2 hdfs dfs -mkdir -p /data/transactions
docker exec namenod2 hdfs dfs -mkdir -p /data/resultats
docker exec namenod2 hdfs dfs -mkdir -p /user/hive/warehouse
docker exec namenod2 hdfs dfs -chmod -R 777 /data
docker exec namenod2 hdfs dfs -chmod -R 777 /user

echo '=== Vérification du fichier CSV sur le host ==='
if [ ! -f "$DATA_PATH" ]; then
    echo "ERREUR : Fichier introuvable -> $DATA_PATH"
    exit 1
fi
echo "Fichier trouvé : $(ls -lh $DATA_PATH | awk '{print $5, $9}')"

echo '=== Copie du CSV dans le conteneur NameNode ==='
docker cp "$DATA_PATH" namenod2:/tmp/transactions_10gb.csv

echo '=== Upload vers HDFS (peut prendre plusieurs minutes) ==='
docker exec namenod2 bash -c "echo '172.20.0.6 datanode1' >> /etc/hosts"
docker exec namenod2 hdfs dfs -put -f /tmp/transactions_10gb.csv /data/transactions/

echo '=== Nettoyage du fichier temporaire dans le conteneur ==='
docker exec namenod2 rm -f /tmp/transactions_10gb.csv

echo '=== Vérification de l upload ==='
docker exec namenod2 hdfs dfs -ls -h /data/transactions/

echo '=== Rapport de fragmentation ==='
docker exec namenod2 hdfs fsck /data/transactions/ -files -blocks | tail -10

echo '=== Terminé ==='