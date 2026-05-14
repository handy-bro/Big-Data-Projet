"""
Benchmark Redis vs Hive + Qualité données + Corrélation
Cas Pratique : Cluster Hadoop Multi-Nœuds pour l'Analyse de Transactions E-Commerce Mondiales
Usage : python3 scripts/benchmark.py
"""

import time
import json
import statistics
import redis
from impala.dbapi import connect
import pandas as pd
import numpy as np
from scipy import stats

# ══════════════════════════════════════════════════════════════
# CONNEXIONS
# ══════════════════════════════════════════════════════════════

print("Connexion à Redis...")
r = redis.Redis(
    host='localhost',
    port=6379,
    password='redis2024',
    decode_responses=True
)
r.ping()
print("Redis connecté ✓")

print("Connexion à Hive...")
hive_conn = connect(
    host='localhost',
    port=10000,
    database='ecommerce',
    auth_mechanism='NOSASL'
)
cursor = hive_conn.cursor()
cursor.execute('SHOW DATABASES')
print(cursor.fetchall())
print("Hive connecté ✓")

# ══════════════════════════════════════════════════════════════
# REQUÊTES ANALYTIQUES
# ══════════════════════════════════════════════════════════════

QUERIES = {
    # nombre total de transactions
    'total_transactions': '''
        SELECT COUNT(*) FROM transactions
    ''',

    # chiffre d'affaires total
    'ca_par_categorie': '''
        SELECT
            categorie,
            COUNT(*)                        AS nb,
            ROUND(SUM(prix * quantite), 2)  AS ca
        FROM transactions
        GROUP BY categorie
        ORDER BY ca DESC
    ''',

    # top 10 pays par nombre de transactions et note moyenne
    'top_pays': '''
        SELECT
            pays,
            COUNT(*)                    AS nb,
            ROUND(AVG(note_client), 2)  AS note_moy
        FROM transactions
        GROUP BY pays
        ORDER BY nb DESC
        LIMIT 10
    ''',

    # ratio de succès (statut) par pays
    'taux_statut': '''
        SELECT
            statut,
            COUNT(*) AS nb,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS pct
        FROM transactions
        GROUP BY statut
    ''',
}

# ══════════════════════════════════════════════════════════════
# FONCTIONS DE BENCHMARK
# ══════════════════════════════════════════════════════════════

def bench_hive(name, hql, n=3):
    """
    Exécute une requête Hive n fois et retourne les temps mesurés.
    n=3 pour avoir une moyenne fiable et écart-type.
    """
    times = []
    result = None
    for i in range(n):
        print(f"    Hive run {i+1}/{n}...", end=' ', flush=True)
        t0 = time.perf_counter()
        cursor.execute(hql)
        result = cursor.fetchall()
        elapsed = time.perf_counter() - t0
        times.append(elapsed)
        print(f"{elapsed:.2f}s")
    return times, result


def bench_redis(name, hql, ttl=3600):
    """
    Tente de récupérer le résultat depuis Redis (HIT).
    Si absent (MISS), calcule via Hive et met en cache.
    ttl : durée de vie du cache en secondes (3600 = 1 heure)
    """
    key = f'hive:result:{name}'

    # Tentative HIT
    t0 = time.perf_counter()
    cached = r.get(key)
    hit_t = time.perf_counter() - t0

    if cached:
        return json.loads(cached), hit_t, True

    # MISS -> calcul Hive
    print("    Redis MISS -> calcul Hive...", end=' ', flush=True)
    t0 = time.perf_counter()
    cursor.execute(hql)
    result = cursor.fetchall()
    miss_t = time.perf_counter() - t0
    print(f"{miss_t:.2f}s")

    # Stockage dans Redis
    r.setex(key, ttl, json.dumps(result))
    print(f"    Résultat mis en cache (TTL={ttl}s)")

    return result, miss_t, False


# ══════════════════════════════════════════════════════════════
# QUALITÉ DES DONNÉES
# ══════════════════════════════════════════════════════════════

def analyse_qualite():
    """
    Analyse la qualité des données sur un échantillon aléatoire.
    TABLESAMPLE évite de scanner 10GB entièrement.
    """
    print('\n' + '='*60)
    print(' QUALITE DES DONNEES')
    print('='*60)

    print("Extraction d'un échantillon aléatoire (1% des données)...")
    cursor.execute('''
        SELECT
            transaction_id,
            user_id,
            prix,
            quantite,
            note_client,
            statut
        FROM transactions
        TABLESAMPLE(BUCKET 1 OUT OF 100 ON RAND())
        LIMIT 50000
    ''')

    df = pd.DataFrame(
        cursor.fetchall(),
        columns=['txn_id', 'user_id', 'prix', 'qte', 'note', 'statut']
    )

    print(f"\nTaille de l'échantillon : {len(df):,} lignes")

    # Valeurs nulles
    print('\n--- Valeurs nulles ---')
    nulls = df.isnull().sum()
    print(nulls.to_string())

    # Doublons
    print('\n--- Doublons ---')
    dupes = df['txn_id'].duplicated().sum()
    print(f"Doublons transaction_id : {dupes} ({dupes/len(df)*100:.2f}%)")

    # Outliers prix - méthode Z-Score
    print('\n--- Outliers prix (méthode Z-Score, seuil=3) ---')
    z_scores = np.abs(stats.zscore(df['prix'].dropna()))
    out_prix = (z_scores > 3).sum()
    print(f"Outliers détectés : {out_prix} ({out_prix/len(df)*100:.2f}%)")
    print(f"Prix min : {df['prix'].min():.2f}  |  Prix max : {df['prix'].max():.2f}")
    print(f"Prix moyen : {df['prix'].mean():.2f}  |  Ecart-type : {df['prix'].std():.2f}")

    # Outliers quantité - méthode IQR
    print('\n--- Outliers quantite (méthode IQR) ---')
    q1, q3 = df['qte'].quantile([0.25, 0.75])
    iqr = q3 - q1
    borne_basse = q1 - 1.5 * iqr
    borne_haute = q3 + 1.5 * iqr
    out_qte = df[(df['qte'] < borne_basse) | (df['qte'] > borne_haute)].shape[0]
    print(f"Q1={q1:.0f}  Q3={q3:.0f}  IQR={iqr:.0f}")
    print(f"Bornes : [{borne_basse:.0f}, {borne_haute:.0f}]")
    print(f"Outliers détectés : {out_qte} ({out_qte/len(df)*100:.2f}%)")

    # Distribution des notes
    print('\n--- Distribution des notes clients (1 à 5) ---')
    dist_notes = df['note'].value_counts().sort_index()
    for note, count in dist_notes.items():
        barre = '#' * int(count / len(df) * 50)
        print(f"  Note {note:.0f} : {barre} {count:,} ({count/len(df)*100:.1f}%)")

    # Distribution des statuts
    print('\n--- Distribution des statuts ---')
    dist_statuts = df['statut'].value_counts()
    for statut, count in dist_statuts.items():
        print(f"  {statut:<15} : {count:,} ({count/len(df)*100:.1f}%)")

    return df


# ══════════════════════════════════════════════════════════════
# ANALYSE DE CORRÉLATION
# ══════════════════════════════════════════════════════════════

def analyse_correlation(df):
    """
    Analyse les corrélations entre prix, quantité et note client.
    Utilise Pearson (linéaire) et Spearman (rang, robuste aux outliers).
    """
    print('\n' + '='*60)
    print(' ANALYSE DE CORRELATION')
    print('='*60)

    num = df[['prix', 'qte', 'note']].dropna()
    print(f"Données utilisées : {len(num):,} lignes (après suppression des nulls)")

    # Pearson
    print('\n--- Corrélation de Pearson (relation linéaire) ---')
    pearson_matrix = num.corr(method='pearson').round(4)
    print(pearson_matrix.to_string())

    # Spearman
    print('\n--- Corrélation de Spearman (relation de rang) ---')
    for col in ['prix', 'qte']:
        corr, p_value = stats.spearmanr(num[col], num['note'])
        sig = 'significatif' if p_value < 0.05 else 'non significatif'
        print(f"  Spearman({col}, note) = {corr:.4f}  |  p-value = {p_value:.4e}  |  {sig}")

    # Interprétation
    print('\n--- Interprétation ---')
    corr_prix_note, p_prix = stats.spearmanr(num['prix'], num['note'])
    corr_qte_note, p_qte = stats.spearmanr(num['qte'], num['note'])

    if abs(corr_prix_note) < 0.1:
        print("  Prix vs Note     : Correlation tres faible -> le prix n'influence pas la note")
    elif corr_prix_note > 0:
        print("  Prix vs Note     : Correlation positive -> produits chers mieux notes")
    else:
        print("  Prix vs Note     : Correlation negative -> produits chers moins bien notes")

    if abs(corr_qte_note) < 0.1:
        print("  Quantite vs Note : Correlation tres faible -> la quantite n'influence pas la note")
    elif corr_qte_note > 0:
        print("  Quantite vs Note : Correlation positive -> grandes commandes mieux notees")
    else:
        print("  Quantite vs Note : Correlation negative -> grandes commandes moins bien notees")

    return {
        'pearson': pearson_matrix.to_dict(),
        'spearman_prix_note': {'corr': round(corr_prix_note, 4), 'p_value': round(p_prix, 6)},
        'spearman_qte_note':  {'corr': round(corr_qte_note,  4), 'p_value': round(p_qte,  6)},
    }


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    print('='*60)
    print(' BENCHMARK REDIS vs HIVE')
    print(' Transactions E-Commerce Mondiales -- 10 GB')
    print('='*60)

    results = {}

    for name, hql in QUERIES.items():
        print(f'\n' + '-'*60)
        print(f'Requête : {name}')
        print('-'*60)

        # Benchmark Hive
        hive_times, _ = bench_hive(name, hql)
        hive_avg = statistics.mean(hive_times)
        hive_std = statistics.stdev(hive_times) if len(hive_times) > 1 else 0
        print(f'\n  > Hive  (moyenne 3 runs) : {hive_avg:.3f}s +/- {hive_std:.3f}s')

        # Benchmark Redis MISS
        _, miss_t, _ = bench_redis(name, hql)
        print(f'  > Redis MISS             : {miss_t:.3f}s')

        # Benchmark Redis HIT
        _, hit_t, _ = bench_redis(name, hql)
        speedup = hive_avg / hit_t if hit_t > 0 else 0
        print(f'  > Redis HIT              : {hit_t*1000:.2f}ms  (speedup x{speedup:.0f})')

        results[name] = {
            'hive_avg_s':   round(hive_avg, 3),
            'hive_std_s':   round(hive_std, 3),
            'redis_miss_s': round(miss_t, 3),
            'redis_hit_ms': round(hit_t * 1000, 2),
            'speedup':      round(speedup, 0),
        }

    # Tableau récapitulatif
    print('\n' + '='*60)
    print(' RESULTATS FINAUX')
    print('='*60)
    print(f'{"Requete":<25} {"Hive(s)":<12} {"Redis MISS(s)":<15} {"Redis HIT(ms)":<15} Speedup')
    print('-'*80)
    for name, d in results.items():
        print(
            f'{name:<25} '
            f'{d["hive_avg_s"]:<12} '
            f'{d["redis_miss_s"]:<15} '
            f'{d["redis_hit_ms"]:<15} '
            f'x{d["speedup"]:.0f}'
        )

    # Qualité des données
    df = analyse_qualite()

    # Corrélations
    corr_results = analyse_correlation(df)

    # Export JSON
    final_results = {
        'benchmark':   results,
        'correlation': corr_results,
    }

    output_path = '/tmp/benchmark_results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False)

    print(f'\n' + '='*60)
    print(f'Résultats exportés : {output_path}')
    print('='*60)


if __name__ == '__main__':
    main()