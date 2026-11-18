# Stock Market dbt project

This dbt project transforms daily stock prices loaded into Snowflake into a monthly analytics table for the Power BI dashboard.

## Data flow

1. The Python ETL writes the combined dataset to `../data/all_stocks.csv`.
2. The optional Azure and Snowflake loading steps put that data in `STOCK_MARKET.RAW.STOCK_PRICES`.
3. `stg_stock_prices` reads the raw table, removes exact duplicate rows, and creates a daily key from ticker and date.
4. `mart_stock_prices` aggregates the daily rows to one row per ticker and month.

The staging model removes fully identical rows only. If two rows share a ticker and date but have different values, the `stock_id` uniqueness test fails so the conflict is visible.

## Configure and run

Install dbt with the Snowflake adapter and configure a `stock_market` profile in `~/.dbt/profiles.yml`. The profile must point to the Snowflake account that contains database `STOCK_MARKET` and schema `RAW`.

From this directory, run:

```bash
dbt deps
dbt run
dbt test
```

Cloud execution requires valid Snowflake credentials and a provisioned warehouse. No credentials or live cloud environment are included in this repository. See the root README for the end-to-end setup and CSV loading instructions.

## Models and tests

- `stg_stock_prices` is a view at daily ticker/date grain. Its key is `stock_id`.
- `mart_stock_prices` is a table at ticker/month grain. `avg_daily_return` is stored as a fraction (`0.002` means `0.2%`); format it as a percentage in Power BI.
- YAML tests check the staging key for uniqueness and nulls, and require ticker and date values.
- `tests/assert_high_price_is_greater_than_low.sql` fails when a staged row has a high price below its low price.
