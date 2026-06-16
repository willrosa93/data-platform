-- models/marts/mart_brewery_by_type.sql
-- Conta quantas cervejarias existem por tipo
-- Este é um modelo FATO: a métrica é a contagem
{{ config(materialized='table') }}
select
 brewery_type,
count(*) as total_breweries,
count(distinct country) as countries_present,
round(count(*) * 100.0 / sum(count(*)) over (), 2) as pct_total
from {{ ref('stg_breweries') }}
where brewery_type is not null
group by 1
order by 2 desc