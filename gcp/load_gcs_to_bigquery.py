import os
from google.cloud import bigquery

PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
DATASET    = "breweries_raw"     # dataset no BigQuery
TABLE      = "breweries"           # tabela que será criada/substituída


def load_to_bq(gcs_uri: str = None, **context) -> None:
    """Carrega JSON do GCS para BigQuery. Lê gcs_uri do XCom se não passado."""
    # Se chamado pelo Airflow, pega o URI da task anterior via XCom
    if gcs_uri is None:
        gcs_uri = context["ti"].xcom_pull(task_ids="api_para_cloud_storage")

    client    = bigquery.Client()
    table_ref = f"{PROJECT_ID}.{DATASET}.{TABLE}"

    job_config = bigquery.LoadJobConfig(
        source_format     = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect        = True,
        write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    job = client.load_table_from_uri(gcs_uri, table_ref, job_config=job_config)
    job.result()   # espera terminar

    table = client.get_table(table_ref)
    print(f"Carregadas {table.num_rows} linhas em {table_ref}")


if __name__ == "__main__":
    import datetime
    hoje = datetime.date.today().isoformat()
    load_to_bq(f"gs://project-e57dc814-3be0-44da-96e-datalake/raw/breweries/breweries_{hoje}.json")