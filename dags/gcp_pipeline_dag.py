import sys
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

sys.path.insert(0, "/opt/airflow/gcp")
from ingest_api_to_gcs import run as ingest_run
from load_gcs_to_bigquery import load_to_bq

DBT_DIR = "/opt/airflow/dbt/orders_pipeline"  # montar volume dbt/ também

with DAG(
    dag_id="gcp_pipeline",
    start_date=datetime(2026, 6, 22),
    schedule=None,
    catchup=False,
    tags=["gcp", "ingestao", "dbt"],
) as dag:

    ingestao = PythonOperator(
        task_id="api_para_cloud_storage",
        python_callable=ingest_run,
    )

    carga_bq = PythonOperator(
        task_id="carregar_bigquery",
        python_callable=load_to_bq,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_DIR} && dbt run",
    )

    # Ordem: ingestão → carrega BQ → dbt
    ingestao >> carga_bq >> dbt_run