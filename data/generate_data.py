import csv
import random
import time
import os
from faker import Faker

fake = Faker(['fr_FR', 'en_US', 'de_DE', 'es_ES'])

CATEGORIES = ['Electronique', 'Vetements', 'Alimentaire', 'Sports', 'Maison', 'Beaute', 'Informatique']
STATUTS    = ['confirme', 'en_attente', 'annule', 'livre', 'rembourse']
PAYS       = ['France', 'Cameroun', 'Allemagne', 'USA', 'Senegal', 'Maroc', 'Belgique', 'Espagne']

OUTPUT_FILE = r'E:\SCHOOL\BigData\data\transactions_10gb.csv'
TARGET_BYTES = 10 * 1024 * 1024 * 1024  # 10 Go


def generate_row(i):
    return {
        'transaction_id': f'TXN{i:012d}',
        'user_id':        f'USR{random.randint(1, 500000):08d}',
        'produit':        fake.bs()[:50],
        'categorie':      random.choice(CATEGORIES),
        'prix':           round(random.uniform(1.0, 2000.0), 2),
        'quantite':       random.randint(1, 50),
        'pays':           random.choice(PAYS),
        'timestamp':      fake.date_time_between(start_date='-2y', end_date='now').isoformat(),
        'note_client':    random.randint(1, 5),
        'statut':         random.choice(STATUTS),
        'description':    fake.sentence(nb_words=20),
    }


def main():
    print(f'Génération de {TARGET_BYTES / (1024**3):.1f} Go...')
    start  = time.time()
    fields = [
        'transaction_id', 'user_id', 'produit', 'categorie',
        'prix', 'quantite', 'pays', 'timestamp',
        'note_client', 'statut', 'description',
    ]

    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        i = 0
        while os.path.getsize(OUTPUT_FILE) < TARGET_BYTES:
            writer.writerow(generate_row(i))
            i += 1

            if i % 500_000 == 0:
                gb      = os.path.getsize(OUTPUT_FILE) / (1024**3)
                elapsed = time.time() - start
                print(f'  {gb:.2f} Go | {i:,} lignes | {elapsed:.0f}s')

    size_gb = os.path.getsize(OUTPUT_FILE) / (1024**3)
    elapsed = time.time() - start
    print(f'Terminé : {size_gb:.2f} Go, {i:,} lignes, {elapsed:.0f}s')


if __name__ == '__main__':
    main()