from pathlib import Path

import pandas as pd
import yfinance as yf


TICKERS = ["TSLA", "AAPL", "MSFT", "PLTR", "AMD", "LMT", "AVGO"]
START_DATE = "2021-01-01"
END_DATE = "2025-01-01"  # yfinance treats end as exclusive
DATA_FOLDER = Path(__file__).resolve().parents[1] / "data"


def extract_data(ticker: str) -> pd.DataFrame:
    df = yf.download(
        ticker,
        start=START_DATE,
        end=END_DATE,
        auto_adjust=True,
        progress=False,
    )
    if df.empty:
        raise RuntimeError(f"No price data returned for {ticker}.")

    # yfinance may return MultiIndex columns even for a single ticker. Support
    # either (price, ticker) or (ticker, price) ordering explicitly.
    if isinstance(df.columns, pd.MultiIndex):
        if ticker in df.columns.get_level_values(-1):
            df = df.xs(ticker, axis=1, level=-1)
        elif ticker in df.columns.get_level_values(0):
            df = df.xs(ticker, axis=1, level=0)
        else:
            raise RuntimeError(f"Could not identify {ticker} in the downloaded columns.")

    df = df.reset_index()
    df.columns = [str(column).lower() for column in df.columns]
    if "date" not in df.columns and "datetime" in df.columns:
        df = df.rename(columns={"datetime": "date"})
    df["ticker"] = ticker
    return df


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    required = ["date", "open", "high", "low", "close", "volume", "ticker"]
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(f"Downloaded data is missing required columns: {', '.join(missing)}")

    # Remove incomplete source observations before deriving returns and rolling
    # averages. The first return and first six 7-day averages remain null by design.
    df = df.dropna(subset=["date", "open", "high", "low", "close", "volume"]).copy()
    df["daily_return"] = df["close"].pct_change(fill_method=None)
    df["moving_avg_7d"] = df["close"].rolling(window=7, min_periods=7).mean()
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    return df


def run_pipeline() -> pd.DataFrame:
    DATA_FOLDER.mkdir(parents=True, exist_ok=True)
    frames = []

    for ticker in TICKERS:
        print(f"Processing {ticker}...")
        frame = transform_data(extract_data(ticker))
        if frame.empty:
            raise RuntimeError(f"No usable price rows remain for {ticker}.")
        frames.append(frame)

    all_data = pd.concat(frames, ignore_index=True)
    output_file = DATA_FOLDER / "all_stocks.csv"
    all_data.to_csv(output_file, index=False)
    print(f"Saved {len(all_data):,} rows to {output_file}")
    return all_data


if __name__ == "__main__":
    run_pipeline()
