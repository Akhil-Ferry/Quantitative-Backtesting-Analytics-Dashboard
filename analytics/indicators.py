import pandas as pd
import numpy as np


def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()


def rsi(series, window=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta.where(delta < 0, 0.0))
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def macd(series, fast=12, slow=26, signal=9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return pd.DataFrame({
        "MACD": macd_line,
        "Signal": signal_line,
        "Histogram": histogram,
    })


def bollinger(series, window=20, num_std=2):
    sma = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    return pd.DataFrame({
        "Middle": sma,
        "Upper": sma + num_std * std,
        "Lower": sma - num_std * std,
    })


def atr(data, window=14):
    high, low, close = data["high"], data["low"], data["close"]
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=window).mean()


def add_all_indicators(data):
    df = data.copy()
    close = df["close"]
    df["EMA_12"] = ema(close, 12)
    df["EMA_26"] = ema(close, 26)
    df["RSI"] = rsi(close)
    macd_df = macd(close)
    df = pd.concat([df, macd_df.add_prefix("MACD_")], axis=1)
    bollinger_df = bollinger(close)
    df = pd.concat([df, bollinger_df.add_prefix("BB_")], axis=1)
    if all(c in df.columns for c in ["high", "low"]):
        df["ATR"] = atr(df)
    return df
