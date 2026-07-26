import pandas as pd
import numpy as np


def correlation_matrix(data):
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    else:
        df = data.select_dtypes(include=[np.number])
    return df.corr()


def rolling_correlation(series1, series2, window=30):
    return series1.rolling(window).corr(series2)


def cross_correlation(series1, series2, max_lag=20):
    s1 = series1 - series1.mean()
    s2 = series2 - series2.mean()
    n = len(s1)
    result = {}
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            c = np.corrcoef(s1[:n + lag], s2[-lag:])[0, 1] if n + lag > 0 else 0
        elif lag > 0:
            c = np.corrcoef(s1[lag:], s2[:n - lag])[0, 1] if n - lag > 0 else 0
        else:
            c = np.corrcoef(s1, s2)[0, 1]
        result[lag] = c if not np.isnan(c) else 0
    return result


def pairwise_correlation(data, window=60):
    if isinstance(data, pd.DataFrame) and "close" in data.columns:
        close_prices = data.pivot_table(
            index=data.index, columns="symbol", values="close"
        ) if "symbol" in data.columns else data[["close"]].rename(
            columns={"close": "Asset"}
        )
    else:
        close_prices = data

    returns = close_prices.pct_change().dropna()
    return returns.rolling(window).corr()
