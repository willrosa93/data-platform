-- Mart: agregação por tipo de cervejaria
{{ config(materialized='table') }}

SELECT
    brewery_type,
    country,
    COUNT(*)                        AS total,
    COUNTIF(website_url IS NOT NULL) AS com_website,
    COUNTIF(phone IS NOT NULL)      AS com_telefone
FROM {{ ref('stg_breweries') }}
GROUP BY brewery_type, country
ORDER BY total DESC