import pandas as pd
import numpy as np
from numpy.random import default_rng


def generate_sample_data(ticker="AAPL", start="2020-01-01", end="2024-01-01", seed=42):
    rng = default_rng(seed)
    dates = pd.bdate_range(start=start, end=end)
    n = len(dates)
    price = 100.0
    prices = []
    volatility = 0.015

    trend = 0.0004
    for _ in range(n):
        shock = rng.normal(trend, volatility)
        price *= np.exp(shock)
        prices.append(price)

    prices = np.array(prices)
    data = pd.DataFrame(index=dates)
    data["open"] = prices * (1 + rng.normal(0, 0.005, n))
    data["high"] = prices * (1 + abs(rng.normal(0, 0.01, n)))
    data["low"] = prices * (1 - abs(rng.normal(0, 0.01, n)))
    data["close"] = prices
    data["volume"] = rng.integers(1_000_000, 100_000_000, n)

    for col in ["open", "high", "low"]:
        data[col] = np.maximum(data[col], 0.01)
    data["high"] = data[["open", "close", "high"]].max(axis=1)
    data["low"] = data[["open", "close", "low"]].min(axis=1)

    return data.round(2)


def generate_multi_ticker_data(tickers, start="2020-01-01", end="2024-01-01", seed=42):
    rng = default_rng(seed)
    base = generate_sample_data("BASE", start, end, seed)
    data_frames = []

    for i, ticker in enumerate(tickers):
        df = base.copy()
        beta = rng.uniform(0.5, 1.5)
        alpha = rng.normal(0, 0.0002)
        noise = rng.normal(0, 0.01, len(df))
        returns = df["close"].pct_change().fillna(0) * beta + alpha + noise
        start_price = rng.uniform(20, 500)
        prices = start_price * (1 + returns).cumprod()
        df["open"] = prices * (1 + rng.normal(0, 0.005, len(df)))
        df["high"] = prices * (1 + abs(rng.normal(0, 0.008, len(df))))
        df["low"] = prices * (1 - abs(rng.normal(0, 0.008, len(df))))
        df["close"] = prices
        df["volume"] = rng.integers(500_000, 200_000_000, len(df))
        df["ticker"] = ticker
        data_frames.append(df)

    combined = pd.concat(data_frames)
    return combined
