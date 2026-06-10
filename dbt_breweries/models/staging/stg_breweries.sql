select
    id,
    name             as brewery_name,
    brewery_type,
    city,
    state_province   as state,
    country,
    phone,
    website_url,
    latitude,
    longitude
from breweries_raw
where id is not null
