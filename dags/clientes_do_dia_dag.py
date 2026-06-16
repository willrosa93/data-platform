import logging
import psycopg2
from datetime import datetime, timedelta

from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

# ---------------------------------------------------------------------------
# Variable — criar na UI: Admin → Variables → + Add
#   Key: tabela_contas   Value: contas
# ---------------------------------------------------------------------------
tabela = Variable.get("tabela_contas", default_var="contas")

# ---------------------------------------------------------------------------
# Retries aplicados a todas as tasks via default_args
# ---------------------------------------------------------------------------
default_args = {
    "retries": 2,
    "retry_delay": timedelta(seconds=30),
}


def buscar_clientes():
    logging.info("Iniciando task buscar_clientes")
    conn = psycopg2.connect(
        host="postgres",
        port=5432,
        database="banco_poo",
        user="postgres",
        password="123456",
        connect_timeout=3,
    )
    logging.info("Conectou no banco_poo")
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM {tabela} WHERE data_criacao >= CURRENT_DATE")
        qtd = cur.fetchone()[0]
        logging.info(f"Contas criadas hoje: {qtd}")

        cur.execute(f"SELECT id, titular FROM {tabela} WHERE data_criacao >= CURRENT_DATE")
        for row in cur.fetchall():
            logging.info(f"  Conta: {row}")
    conn.close()
    logging.info("Finalizou task buscar_clientes")


with DAG(
    dag_id="clientes_do_dia",
    start_date=datetime(2026, 6, 9),
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=["banco_poo", "aprendizado"],
) as dag:

    inicio = BashOperator(
        task_id="inicio",
        bash_command='echo "DAG iniciada em: $(date)"',
    )

    buscar = PythonOperator(
        task_id="buscar_clientes",
        python_callable=buscar_clientes,
    )

    # PostgresOperator usa a Connection cadastrada na UI:
    # Admin → Connections → + Add
    # Conn Id: banco_poo_conn | Conn Type: Postgres
    # Host: host.docker.internal | Schema: banco_poo
    # Login: postgres | Password: 123456 | Port: 5434
    contar_sql = PostgresOperator(
        task_id="contar_contas_sql",
        postgres_conn_id="banco_poo_conn",
        sql=f"SELECT COUNT(*) AS total_contas FROM {tabela};",
    )

    inicio >> buscar >> contar_sql
