import pandas as pd
import numpy as np
from scipy import stats


def rolling_stats(series, windows=[20, 50, 200]):
    results = pd.DataFrame(index=series.index)
    for w in windows:
        results[f"mean_{w}"] = series.rolling(w).mean()
        results[f"std_{w}"] = series.rolling(w).std()
        results[f"skew_{w}"] = series.rolling(w).skew()
        results[f"kurt_{w}"] = series.rolling(w).kurt()
    return results


def variance_analysis(data, window=20):
    df = data.copy()
    if "close" in df.columns:
        series = df["close"]
    else:
        series = df.iloc[:, 0]

    returns = series.pct_change().dropna()
    rolling_var = returns.rolling(window).var()
    rolling_vol = returns.rolling(window).std() * np.sqrt(252)
    ewma_var = returns.ewm(span=window).var()
    return pd.DataFrame({
        "returns": returns,
        "rolling_variance": rolling_var,
        "rolling_volatility": rolling_vol,
        "ewma_variance": ewma_var,
    })


def drawdown_analysis(equity_curve):
    cumulative = (1 + equity_curve.pct_change().fillna(0)).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative / running_max) - 1
    dd_duration = _drawdown_durations(drawdown)
    return {
        "drawdown_series": drawdown,
        "max_drawdown": drawdown.min(),
        "avg_drawdown": drawdown[drawdown < 0].mean() if (drawdown < 0).any() else 0,
        "drawdown_durations": dd_duration,
    }


def _drawdown_durations(drawdown_series):
    is_dd = drawdown_series < 0
    durations = []
    current = 0
    for val in is_dd:
        if val:
            current += 1
        elif current > 0:
            durations.append(current)
            current = 0
    if current > 0:
        durations.append(current)
    return durations


def return_distribution(returns, bins=50):
    hist, bin_edges = np.histogram(returns.dropna(), bins=bins)
    skew = stats.skew(returns.dropna())
    kurt = stats.kurtosis(returns.dropna())
    jb_stat, jb_p = stats.jarque_bera(returns.dropna())
    return {
        "histogram": (hist, bin_edges),
        "skewness": skew,
        "kurtosis": kurt,
        "jarque_bera": (jb_stat, jb_p),
    }


def stability_analysis(data, window=20):
    df = data.copy()
    if "close" in df.columns:
        series = df["close"]
    else:
        series = df.iloc[:, 0]

    returns = series.pct_change().dropna()
    rolling_sharpe = (returns.rolling(window).mean() / returns.rolling(window).std()) * np.sqrt(252)
    return rolling_sharpe.replace([np.inf, -np.inf], np.nan)
