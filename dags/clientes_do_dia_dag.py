import logging
import psycopg2
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


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
        cur.execute("SELECT COUNT(*) FROM contas WHERE data_criacao >= CURRENT_DATE")
        qtd = cur.fetchone()[0]
        logging.info(f"Contas criadas hoje: {qtd}")

        cur.execute("SELECT id, titular FROM contas WHERE data_criacao >= CURRENT_DATE")
        for row in cur.fetchall():
            logging.info(f"  Conta: {row}")
    conn.close()
    logging.info("Finalizou task buscar_clientes")


with DAG(
    dag_id="clientes_do_dia",
    start_date=datetime(2026, 6, 9),
    schedule=None,
    catchup=False,
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

    inicio >> buscar
