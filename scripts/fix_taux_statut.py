"""
Benchmark taux_statut uniquement
Utilise beeline via subprocess (contournement problème thrift_sasl)
"""

import time
import json
import subprocess
import statistics
import redis

# ── Redis ────────────────────────────────────────────────────
r = redis.Redis(
    host='localhost',
    port=6379,
    password='redis2024',
    decode_responses=True
)
r.ping()
print("Redis connecté ✓")

# ── Requête ──────────────────────────────────────────────────
HQL = """
SELECT statut,
       COUNT(*) AS nb,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS pct
FROM ecommerce.transactions
GROUP BY statut;
"""

BEELINE_CMD = [
    "sudo", "docker", "exec", "hiveserver",
    "beeline",
    "-u", "jdbc:hive2://localhost:10000/ecommerce;auth=noSasl",
    "--outputformat=csv2",
    "--silent=true",
    "-e", HQL
]

def run_hive():
    """Lance beeline et retourne (temps_secondes, résultat)"""
    t0 = time.perf_counter()
    proc = subprocess.run(
        BEELINE_CMD,
        capture_output=True,
        text=True
    )
    elapsed = time.perf_counter() - t0
    # Parse les lignes CSV (ignore les lignes SLF4J)
    lines = [l for l in proc.stdout.split('\n')
             if l.strip() and not l.startswith('SLF4J')
             and not l.startswith('Beeline')
             and not l.startswith('Connecting')
             and not l.startswith('Connected')
             and not l.startswith('Transaction')
             and not l.startswith('Closing')]
    return elapsed, lines

# ── Benchmark Hive (3 runs) ───────────────────────────────────
print("\n" + "="*60)
print("Requête : taux_statut")
print("="*60)

times = []
result_lines = []
for i in range(3):
    print(f"    Hive run {i+1}/3...", end=' ', flush=True)
    elapsed, lines = run_hive()
    times.append(elapsed)
    result_lines = lines
    print(f"{elapsed:.2f}s")

hive_avg = statistics.mean(times)
hive_std = statistics.stdev(times)
print(f"\n  > Hive (moyenne 3 runs) : {hive_avg:.3f}s +/- {hive_std:.3f}s")
print(f"\n  Résultat :")
for line in result_lines:
    print(f"    {line}")

# ── Redis MISS ────────────────────────────────────────────────
key = 'hive:result:taux_statut'
print(f"\n  > Redis MISS -> calcul Hive...", end=' ', flush=True)
miss_elapsed, miss_lines = run_hive()
r.setex(key, 86400, json.dumps(miss_lines))
print(f"{miss_elapsed:.2f}s")
print(f"    Résultat mis en cache (TTL=86400s)")

# ── Redis HIT ─────────────────────────────────────────────────
t0 = time.perf_counter()
cached = r.get(key)
hit_t = time.perf_counter() - t0
speedup = hive_avg / hit_t if hit_t > 0 else 0

print(f"  > Redis MISS             : {miss_elapsed:.3f}s")
print(f"  > Redis HIT              : {hit_t*1000:.2f}ms  (speedup x{speedup:.0f})")

# ── Résumé final ──────────────────────────────────────────────
print("\n" + "="*60)
print(" RÉSULTATS COMPLETS DU BENCHMARK")
print("="*60)
print(f"{'Requête':<25} {'Hive(s)':<12} {'Redis HIT(ms)':<15} Speedup")
print("-"*60)

resultats = {
    'total_transactions': {'hive_avg_s': 1056.661, 'redis_hit_ms': 0.57,  'speedup': 1860230},
    'ca_par_categorie':   {'hive_avg_s': 1120.398, 'redis_hit_ms': 0.56,  'speedup': 2000385},
    'top_pays':           {'hive_avg_s': 208.631,  'redis_hit_ms': 3.22,  'speedup': 64806},
    'taux_statut':        {
        'hive_avg_s':   round(hive_avg, 3),
        'redis_hit_ms': round(hit_t * 1000, 2),
        'speedup':      round(speedup, 0)
    },
}

for name, d in resultats.items():
    print(f"{name:<25} {d['hive_avg_s']:<12} {d['redis_hit_ms']:<15} x{d['speedup']:.0f}")

# ── Export JSON ───────────────────────────────────────────────
output = {
    'benchmark': resultats,
    'taux_statut_detail': {
        'runs': times,
        'hive_std_s': round(hive_std, 3),
        'redis_miss_s': round(miss_elapsed, 3),
    }
}

with open('/tmp/benchmark_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n✅ Résultats exportés : /tmp/benchmark_results.json")