import csv, random, datetime, pathlib, subprocess

CSV_PATH = pathlib.Path('/tmp/pipeline_orders.csv')

DBT_DIR = pathlib.Path(
    '~/person_projects/data-platform/dbt/orders_pipeline'
).expanduser()

def get_project():
    return subprocess.check_output(
        ['gcloud', 'config', 'get-value', 'project'],
        text=True
    ).strip()

def generate_csv(rows=500):
    statuses = ['paid', 'pending', 'refund']
    data = []

    for i in range(1, rows + 1):
        dt = datetime.datetime(
            2026, 6,
            random.randint(1, 21),
            random.randint(0, 23),
            random.randint(0, 59)
        )

        data.append({
            'order_id': i,
            'customer_id': random.randint(100, 200),
            'amount': round(random.uniform(10, 1000), 2),
            'status': random.choice(statuses),
            'created_at': dt.strftime('%Y-%m-%d %H:%M:%S') + ' UTC',
        })

    with CSV_PATH.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=data[0].keys())
        w.writeheader()
        w.writerows(data)

    print(f'[1/4] CSV gerado: {CSV_PATH} ({rows} linhas)')


def upload_gcs(project):
    dest = f'gs://{project}-datalake/raw/pipeline_orders.csv'

    subprocess.run(['gsutil', 'cp', str(CSV_PATH), dest], check=True)

    print(f'[2/4] Upload GCS: {dest}')
    return dest


def load_bigquery(gcs_uri):
    subprocess.run([
        'bq', 'load',
        '--source_format=CSV',
        '--skip_leading_rows=1',
        '--autodetect',
        '--replace',
        'ecommerce.orders_pipeline',
        gcs_uri,
    ], check=True)

    print('[3/4] Load BigQuery: ecommerce.orders_pipeline')


def run_dbt():
    subprocess.run(['dbt', 'run'], cwd=DBT_DIR, check=True)
    print('[4/4] dbt run concluído')


if __name__ == '__main__':
    project = get_project()
    print(f'Pipeline iniciado — projeto: {project}\n')

    generate_csv()
    uri = upload_gcs(project)
    load_bigquery(uri)
    run_dbt()

    print('\nPipeline concluído com sucesso! ✓')