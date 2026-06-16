-- models/marts/mart_brewery_by_state.sql
-- Top estados com mais cervejarias (fato + dimensão localização)
{{ config(materialized='table') }}
select
 country,
 state,
 brewery_type,
count(*) as total_breweries
from {{ ref('stg_breweries') }}
where state is not null
and country is not null
group by 1, 2, 3
order by 4 desc