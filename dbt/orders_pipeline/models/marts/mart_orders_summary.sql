WITH orders AS (
    SELECT *
    FROM {{ ref('stg_orders') }}
)

SELECT
    status,
    COUNT(*) AS qtd_pedidos,
    SUM(amount) AS receita_total,
    ROUND(AVG(amount), 2) AS ticket_medio,
    MIN(created_at) AS primeiro_pedido,
    MAX(created_at) AS ultimo_pedido
FROM orders
GROUP BY status
ORDER BY receita_total DESC