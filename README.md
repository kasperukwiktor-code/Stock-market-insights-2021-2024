# Stock Market Insights (2021–2024)

## 📊 Project Overview
End-to-end data pipeline for analyzing stock market trends across 7 companies (Jan 2021 – Dec 2024).
Built to demonstrate a production-style analytics engineering workflow using a modern data stack.

**Companies analyzed:** TSLA, AAPL, MSFT, PLTR, AMD, LMT, AVGO

## 🧱 Architecture
yfinance API → Python ETL → Azure Blob Storage → Snowflake → dbt → Power BI

| Layer | Tool | Purpose |
|---|---|---|
| Extraction | Python + yfinance | Pull historical OHLCV data |
| Storage | Azure Blob Storage | Raw data landing zone (Bronze) |
| Loading | Snowflake external stage + `COPY INTO` | Load raw CSVs from Blob into the RAW schema |
| Warehouse | Snowflake | Cloud data warehouse |
| Transformation | dbt Core | Staging + mart models, data tests |
| Visualization | Power BI | Interactive dashboard |

## ⚙️ Tech Stack
Python · SQL · dbt Core · Snowflake · Azure Blob Storage · Power BI · Git

## 📁 Project Structure
```
Stock-market-insights-2021-2025/
├── etl/
│   ├── extract_stock_data.py   # Extract & transform via yfinance
│   └── upload_to_blob.py       # Upload CSV to Azure Blob
├── stock_market/               # dbt project
│   └── models/
│       ├── staging/            # stg_stock_prices (view)
│       └── mart/               # mart_stock_prices (table)
├── data/                       # Local CSV output
├── Images/                     # Dashboard screenshot
└── README.md
```

## 📈 dbt Models
**Staging** — `stg_stock_prices`
- Cleans and validates raw data from the Snowflake RAW schema
- Filters nulls, standardizes column names

**Mart** — `mart_stock_prices`
- Grain: one row per ticker per month
- Metrics: avg/min/max close price, avg daily return, total volume, 7-day moving average

**Data tests** (`schema.yml`): `unique` and `not_null` checks on model keys.

## 📊 Dashboard (Power BI)
![Dashboard](Images/dashboard.png)
- Monthly closing price trends per ticker
- Stock popularity ranking by trading volume (shares traded)
- Return vs. Price Level scatter plot (avg daily return vs. avg closing price)
- KPIs: earliest/latest reporting period, total volume, avg daily return, ticker count

## 🔑 Key Results
- 7 tickers × 4 years = ~7,000 daily records processed
- AVGO and PLTR had the highest average daily return (~0.2%/day)
- LMT had the lowest average daily return (~0.05%/day) at the highest price level
- Average daily return is an arithmetic mean and does not account for volatility

## 🚀 How to Run
```bash
# 1. Install dependencies
pip install yfinance pandas azure-storage-blob python-dotenv dbt-snowflake

# 2. Create a .env file in the project root
echo 'AZURE_CONNECTION_STRING=<your-connection-string>' > .env

# 3. Extract and upload raw data (container: raw-data)
python etl/extract_stock_data.py
python etl/upload_to_blob.py

# 4. Load from Blob into Snowflake (RAW schema) via external stage
#    COPY INTO RAW.<table> FROM @<external_stage> FILE_FORMAT = (TYPE = CSV SKIP_HEADER = 1);

# 5. Run dbt (Snowflake credentials in ~/.dbt/profiles.yml)
cd stock_market
dbt run
dbt test
```

## ⚠️ Limitations & Next Steps
- **Risk metrics:** replace the price-level axis with standard deviation of daily returns and add a Sharpe ratio for a proper risk/return view
- **Volume:** ranking is based on shares traded; traded value (close × volume) would remove the bias towards low-priced stocks
- **Incremental loads:** the pipeline reloads the full history on every run
- **Orchestration:** scheduling (GitHub Actions / Airflow) is not set up yet
