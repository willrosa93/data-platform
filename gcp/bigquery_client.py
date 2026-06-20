from google.cloud import bigquery

def main():
    client = bigquery.Client()
    project_id = client.project

    query = f"""
        SELECT 
            status,
            COUNT(*) AS qtd_pedidos,
            SUM(amount) AS receita_total,
            ROUND(AVG(amount), 2) AS ticket_medio
        FROM `{project_id}.ecommerce.orders`
        GROUP BY status
        ORDER BY receita_total DESC
    """

    print(f"Consultando projeto: {project_id}\n")

    results = client.query(query).result()

    for row in results:
        print(row)

if __name__ == "__main__":
    main()
