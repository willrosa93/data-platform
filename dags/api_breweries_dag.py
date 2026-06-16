import logging
import psycopg2
import requests
import pandas as pd
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

# ─── CONFIGURAÇÃO ────────────────────────────────────────────────────────────
BASE_URL = "https://api.openbrewerydb.org/v1/breweries"

default_args = {
    "retries": 2,
    "retry_delay": timedelta(seconds=30),
}


# ─── FUNÇÃO DE INGESTÃO ───────────────────────────────────────────────────────
# Esta função é Python puro — não sabe que existe Airflow.
# O Airflow só a chama no momento certo (via PythonOperator).
def ingesta_breweries():

    # ── 1. BUSCAR ────────────────────────────────────────────────────────────
    todos = []
    for page in range(1, 4):   # busca páginas 1, 2 e 3 (150 cervejarias)
        resp = requests.get(BASE_URL, params={"per_page": 50, "page": page})
        resp.raise_for_status()  # lança erro se status >= 400
        lote = resp.json()
        if not lote:              # lista vazia = acabou a paginação
            break
        todos.extend(lote)
        logging.info(f"Página {page}: {len(lote)} registros")

    logging.info(f"Total buscado da API: {len(todos)}")

    # ── 2. TRANSFORMAR ───────────────────────────────────────────────────────
    df = pd.DataFrame(todos)

    # selecionar só as colunas que a tabela tem
    colunas = ["id", "name", "brewery_type", "city",
               "state_province", "country", "phone",
               "website_url", "latitude", "longitude"]
    df = df[colunas].copy()

    # latitude/longitude chegam como string — converter para número
    # errors="coerce": se não conseguir converter, vira NaN (não quebra o pipeline)
    df["latitude"]  = pd.to_numeric(df["latitude"],  errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    registros = df.to_dict("records")  # lista de dicts — formato que o psycopg2 espera
    logging.info(f"Registros preparados para inserção: {len(registros)}")

    # ── 3. INSERIR ───────────────────────────────────────────────────────────
    # host="postgres" funciona porque o container do Airflow está na mesma rede Docker
    conn = psycopg2.connect(
        host="postgres", port=5432, database="banco_poo",
        user="postgres", password="123456",
    )

    sql = """
        INSERT INTO breweries_raw
            (id, name, brewery_type, city, state_province, country,
             phone, website_url, latitude, longitude)
        VALUES
            (%(id)s, %(name)s, %(brewery_type)s, %(city)s, %(state_province)s,
             %(country)s, %(phone)s, %(website_url)s, %(latitude)s, %(longitude)s)
        ON CONFLICT (id) DO NOTHING
    """
    # ON CONFLICT (id) DO NOTHING = se a cervejaria já existe, ignora (não duplica)

    with conn.cursor() as cur:
        cur.executemany(sql, registros)
        logging.info(f"Inseridos/ignorados: {len(registros)} registros")

    conn.commit()
    conn.close()


# ─── DAG ─────────────────────────────────────────────────────────────────────
with DAG(
    dag_id="api_breweries",
    start_date=datetime(2026, 6, 9),
    schedule=None,       # execução manual (sem agendamento automático)
    catchup=False,
    default_args=default_args,
    tags=["breweries", "ingestao"],
) as dag:

    # Task 1: loga a data/hora de início
    inicio = BashOperator(
        task_id="inicio",
        bash_command='echo "Ingestão breweries iniciada em: $(date)"',
    )

    # Task 2: executa a função de ingestão (busca API + insere no banco)
    ingesta = PythonOperator(
        task_id="ingesta_breweries",
        python_callable=ingesta_breweries,   # sem parênteses!
    )

    # Task 3: conta as linhas na tabela para confirmar que os dados chegaram
    validar = PostgresOperator(
        task_id="validar_carga",
        postgres_conn_id="banco_poo_conn",   # Connection cadastrada na UI do Airflow
        sql="SELECT COUNT(*) AS total_breweries FROM breweries_raw;",
    )

    # Define a ordem: inicio → ingesta → validar
    inicio >> ingesta >> validar