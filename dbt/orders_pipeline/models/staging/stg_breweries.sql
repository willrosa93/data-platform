-- Staging: limpeza e padronização
{{ config(materialized='view') }}

SELECT
    id,
    name                                AS brewery_name,
    LOWER(brewery_type)                 AS brewery_type,
    city,
    UPPER(state_province)               AS state,
    UPPER(country)                      AS country,
    phone,
    website_url,
    CAST(latitude  AS FLOAT64)          AS latitude,
    CAST(longitude AS FLOAT64)          AS longitude
FROM {{ source('breweries_raw', 'breweries') }}
WHERE id IS NOT NULL