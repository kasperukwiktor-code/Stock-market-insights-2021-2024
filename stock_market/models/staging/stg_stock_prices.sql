with source as (
    select
        date,
        ticker,
        close,
        high,
        low,
        open,
        volume,
        daily_return,
        moving_avg_7d,
        year,
        month
    from {{ source('raw', 'stock_prices') }}
    where close is not null
),

-- Remove only fully identical copies. Conflicting rows for one ticker/date
-- remain visible and are caught by the model's unique-key test.
deduplicated as (
    select distinct *
    from source
)

select
    {{ dbt_utils.generate_surrogate_key(['ticker', 'date']) }} as stock_id,
    date,
    ticker,
    close,
    high,
    low,
    open,
    volume,
    daily_return,
    moving_avg_7d,
    year,
    month
from deduplicated
