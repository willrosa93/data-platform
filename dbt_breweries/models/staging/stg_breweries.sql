-- models/staging/stg_breweries.sql
-- ANTES: from breweries_raw
-- AGORA: from {{ source('banco_poo', 'breweries_raw') }}
select
 id,
 name as brewery_name,
 brewery_type,
 city,
 state_province as state,
 country,
 phone,
 website_url,
 latitude,
 longitude
from {{ source('banco_poo', 'breweries_raw') }}
where id is not null