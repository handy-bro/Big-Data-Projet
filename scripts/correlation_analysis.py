"""
Analyse de Corrélation — Transactions E-Commerce Mondiales
Cas Pratique : Cluster Hadoop Multi-Nœuds
Usage : python3 scripts/correlation_analysis.py
"""

import json
import subprocess
import pandas as pd
import numpy as np
from scipy import stats

# ══════════════════════════════════════════════════════════════
# EXTRACTION DES DONNÉES VIA BEELINE
# ══════════════════════════════════════════════════════════════

def run_beeline(hql):
    """Lance une requête via beeline et retourne les lignes CSV"""
    cmd = [
        "sudo", "docker", "exec", "hiveserver",
        "beeline",
        "-u", "jdbc:hive2://localhost:10000/ecommerce;auth=noSasl",
        "--outputformat=csv2",
        "--silent=true",
        "-e", hql
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    lines = [
        l.strip() for l in proc.stdout.split('\n')
        if l.strip()
        and not l.startswith('SLF4J')
        and not l.startswith('Beeline')
        and not l.startswith('Connecting')
        and not l.startswith('Connected')
        and not l.startswith('Transaction')
        and not l.startswith('Closing')
        and not l.startswith('WARNING')
    ]
    return lines


print("="*60)
print(" ANALYSE DE CORRÉLATION")
print(" Transactions E-Commerce Mondiales -- 10 GB")
print("="*60)

# ══════════════════════════════════════════════════════════════
# EXTRACTION ÉCHANTILLON (1% aléatoire)
# ══════════════════════════════════════════════════════════════

print("\nExtraction échantillon 1% depuis Hive...")
print("(Cela peut prendre 3 à 10 minutes)")

lines = run_beeline("""
    SELECT
        prix,
        quantite,
        note_client,
        statut,
        categorie,
        pays
    FROM transactions
    TABLESAMPLE(BUCKET 1 OUT OF 100 ON RAND())
    LIMIT 50000
""")

# Parse CSV
data = []
for line in lines[1:]:  # Skip header
    parts = line.split(',')
    if len(parts) >= 6:
        try:
            data.append({
                'prix':     float(parts[0]),
                'qte':      int(parts[1]),
                'note':     int(parts[2]),
                'statut':   parts[3].strip(),
                'categorie':parts[4].strip(),
                'pays':     parts[5].strip(),
            })
        except (ValueError, IndexError):
            continue

df = pd.DataFrame(data)
print(f"Échantillon extrait : {len(df):,} lignes")

# ══════════════════════════════════════════════════════════════
# QUALITÉ DES DONNÉES
# ══════════════════════════════════════════════════════════════

print("\n" + "="*60)
print(" QUALITÉ DES DONNÉES")
print("="*60)

print(f"\nTaille de l'échantillon : {len(df):,} lignes")

print('\n--- Valeurs nulles ---')
print(df.isnull().sum().to_string())

print('\n--- Doublons ---')
# Pas de transaction_id dans cet échantillon
print("Lignes dupliquées exactes :", df.duplicated().sum())

print('\n--- Outliers prix (Z-Score, seuil=3) ---')
z_scores = np.abs(stats.zscore(df['prix'].dropna()))
out_prix = (z_scores > 3).sum()
print(f"Outliers : {out_prix} ({out_prix/len(df)*100:.2f}%)")
print(f"Prix min : {df['prix'].min():.2f}  |  Prix max : {df['prix'].max():.2f}")
print(f"Prix moyen : {df['prix'].mean():.2f}  |  Ecart-type : {df['prix'].std():.2f}")

print('\n--- Outliers quantité (IQR) ---')
q1, q3 = df['qte'].quantile([0.25, 0.75])
iqr = q3 - q1
borne_basse = q1 - 1.5 * iqr
borne_haute = q3 + 1.5 * iqr
out_qte = df[(df['qte'] < borne_basse) | (df['qte'] > borne_haute)].shape[0]
print(f"Q1={q1:.0f}  Q3={q3:.0f}  IQR={iqr:.0f}")
print(f"Bornes : [{borne_basse:.0f}, {borne_haute:.0f}]")
print(f"Outliers : {out_qte} ({out_qte/len(df)*100:.2f}%)")

print('\n--- Distribution notes clients (1 à 5) ---')
dist_notes = df['note'].value_counts().sort_index()
for note, count in dist_notes.items():
    barre = '#' * int(count / len(df) * 50)
    print(f"  Note {note} : {barre} {count:,} ({count/len(df)*100:.1f}%)")

print('\n--- Distribution statuts ---')
for statut, count in df['statut'].value_counts().items():
    print(f"  {statut:<15} : {count:,} ({count/len(df)*100:.1f}%)")

print('\n--- Top 5 catégories ---')
for cat, count in df['categorie'].value_counts().head(5).items():
    print(f"  {cat:<20} : {count:,} ({count/len(df)*100:.1f}%)")

# ══════════════════════════════════════════════════════════════
# CORRÉLATIONS
# ══════════════════════════════════════════════════════════════

print("\n" + "="*60)
print(" ANALYSE DE CORRÉLATION")
print("="*60)

num = df[['prix', 'qte', 'note']].dropna()
print(f"\nDonnées : {len(num):,} lignes")

# Pearson
print('\n--- Corrélation de Pearson (relation linéaire) ---')
pearson = num.corr(method='pearson').round(4)
print(pearson.to_string())

# Spearman
print('\n--- Corrélation de Spearman (relation de rang) ---')
spearman_results = {}
for col in ['prix', 'qte']:
    corr, p_value = stats.spearmanr(num[col], num['note'])
    sig = 'SIGNIFICATIF' if p_value < 0.05 else 'non significatif'
    print(f"  Spearman({col}, note) = {corr:.4f}  p={p_value:.4e}  [{sig}]")
    spearman_results[f'{col}_note'] = {
        'corr': round(corr, 4),
        'p_value': round(p_value, 6),
        'significatif': p_value < 0.05
    }

# Interprétation
print('\n--- Interprétation ---')
corr_prix, p_prix = stats.spearmanr(num['prix'], num['note'])
corr_qte, p_qte   = stats.spearmanr(num['qte'],  num['note'])

if abs(corr_prix) < 0.1:
    print("  Prix vs Note     : Correlation tres faible")
    print("                     Le prix n'influence pas la satisfaction client")
elif corr_prix > 0:
    print("  Prix vs Note     : Correlation positive")
    print("                     Les produits chers sont mieux notes")
else:
    print("  Prix vs Note     : Correlation negative")
    print("                     Les produits chers sont moins bien notes")

if abs(corr_qte) < 0.1:
    print("  Quantite vs Note : Correlation tres faible")
    print("                     La quantite commandee n'influence pas la note")
elif corr_qte > 0:
    print("  Quantite vs Note : Correlation positive")
else:
    print("  Quantite vs Note : Correlation negative")

# ══════════════════════════════════════════════════════════════
# EXPORT JSON
# ══════════════════════════════════════════════════════════════

results = {
    'echantillon_taille': len(df),
    'qualite': {
        'nulls':         df.isnull().sum().to_dict(),
        'outliers_prix': int(out_prix),
        'outliers_qte':  int(out_qte),
        'prix_min':      round(df['prix'].min(), 2),
        'prix_max':      round(df['prix'].max(), 2),
        'prix_moyen':    round(df['prix'].mean(), 2),
        'prix_std':      round(df['prix'].std(), 2),
    },
    'pearson':  pearson.to_dict(),
    'spearman': spearman_results,
    'distribution_notes':  df['note'].value_counts().sort_index().to_dict(),
    'distribution_statuts': df['statut'].value_counts().to_dict(),
}

output_path = '/tmp/correlation_results.json'
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (bool, np.bool_)):
            return int(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        return super().default(obj)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False, cls=CustomEncoder)

print(f"\n{'='*60}")
print(f"Résultats exportés : {output_path}")
print(f"{'='*60}")