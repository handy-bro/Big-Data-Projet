Write-Host "=== Création de la structure HDFS ===" -ForegroundColor Cyan
docker exec namenod2 hdfs dfs -mkdir -p /data/transactions
docker exec namenod2 hdfs dfs -mkdir -p /data/resultats
docker exec namenod2 hdfs dfs -mkdir -p /user/hive/warehouse
docker exec namenod2 hdfs dfs -chmod -R 777 /data
docker exec namenod2 hdfs dfs -chmod -R 777 /user

Write-Host "=== Copie du CSV dans le conteneur ===" -ForegroundColor Cyan
docker cp E:\SCHOOL\BigData\data\transactions_10gb.csv namenod2:/tmp/transactions_10gb.csv

Write-Host "=== Upload vers HDFS ===" -ForegroundColor Cyan
docker exec namenod2 hdfs dfs -put -f /tmp/transactions_10gb.csv /data/transactions/

Write-Host "=== Vérification ===" -ForegroundColor Cyan
docker exec namenod2 hdfs dfs -ls -h /data/transactions/

Write-Host "=== Fragmentation ===" -ForegroundColor Cyan
docker exec namenod2 hdfs fsck /data/transactions/ -files -blocks

Write-Host "=== Terminé ===" -ForegroundColor Green