with source as (
    select * from `project-e57dc814-3be0-44da-96e.ecommerce.orders`
),

renamed as (
    select
        order_id,
        customer_id,
        amount,
        status,
        created_at
    from source
)

select * from renamed
