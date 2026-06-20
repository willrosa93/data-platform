import csv
import random
import datetime
import pathlib

statuses = ['paid', 'pending', 'refund']
rows = []

for i in range(1, 201):
    dt = datetime.datetime(
        2026, 6,
        random.randint(1, 17),
        random.randint(0, 23),
        random.randint(0, 59),
    )
    rows.append({
        'order_id':    i,
        'customer_id': random.randint(100, 150),
        'amount':      round(random.uniform(10, 500), 2),
        'status':      random.choice(statuses),
        'created_at':  dt.strftime('%Y-%m-%d %H:%M:%S') + ' UTC',
    })

out = pathlib.Path('/tmp/orders_bulk.csv')
with out.open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

print(f'Gerado: {out}  ({len(rows)} linhas)')
