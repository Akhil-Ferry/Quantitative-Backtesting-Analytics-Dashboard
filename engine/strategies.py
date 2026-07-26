import numpy as np
import pandas as pd


def sma_crossover(data, short_window=20, long_window=60):
    df = data.copy()
    df["SMA_short"] = df["close"].rolling(window=short_window).mean()
    df["SMA_long"] = df["close"].rolling(window=long_window).mean()
    df["signal"] = 0
    df.loc[df["SMA_short"] > df["SMA_long"], "signal"] = 1
    df.loc[df["SMA_short"] <= df["SMA_long"], "signal"] = -1
    return df


def momentum_strategy(data, lookback=20, threshold=0.02):
    df = data.copy()
    df["returns"] = df["close"].pct_change(lookback)
    df["signal"] = 0
    df.loc[df["returns"] > threshold, "signal"] = 1
    df.loc[df["returns"] < -threshold, "signal"] = -1
    return df


def mean_reversion(data, window=20, entry_z=2.0, exit_z=0.5):
    df = data.copy()
    df["sma"] = df["close"].rolling(window=window).mean()
    df["std"] = df["close"].rolling(window=window).std()
    df["z_score"] = (df["close"] - df["sma"]) / df["std"]

    df["signal"] = 0
    in_position = False
    for i in range(len(df)):
        if pd.isna(df["z_score"].iloc[i]):
            continue
        if not in_position and df["z_score"].iloc[i] < -entry_z:
            df.loc[df.index[i], "signal"] = 1
            in_position = True
        elif not in_position and df["z_score"].iloc[i] > entry_z:
            df.loc[df.index[i], "signal"] = -1
            in_position = True
        elif in_position and abs(df["z_score"].iloc[i]) < exit_z:
            df.loc[df.index[i], "signal"] = 0
            in_position = False
    return df


def bollinger_bands(data, window=20, num_std=2):
    df = data.copy()
    df["sma"] = df["close"].rolling(window=window).mean()
    df["std"] = df["close"].rolling(window=window).std()
    df["upper"] = df["sma"] + num_std * df["std"]
    df["lower"] = df["sma"] - num_std * df["std"]

    df["signal"] = 0
    in_position = False
    position_type = None
    for i in range(len(df)):
        if pd.isna(df["upper"].iloc[i]):
            continue
        if not in_position and df["close"].iloc[i] < df["lower"].iloc[i]:
            df.loc[df.index[i], "signal"] = 1
            in_position = True
            position_type = "long"
        elif not in_position and df["close"].iloc[i] > df["upper"].iloc[i]:
            df.loc[df.index[i], "signal"] = -1
            in_position = True
            position_type = "short"
        elif in_position and position_type == "long" and df["close"].iloc[i] > df["sma"].iloc[i]:
            df.loc[df.index[i], "signal"] = 0
            in_position = False
            position_type = None
        elif in_position and position_type == "short" and df["close"].iloc[i] < df["sma"].iloc[i]:
            df.loc[df.index[i], "signal"] = 0
            in_position = False
            position_type = None
    return df


def rsi_strategy(data, rsi_window=14, oversold=30, overbought=70):
    df = data.copy()
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta.where(delta < 0, 0.0))
    avg_gain = gain.rolling(window=rsi_window).mean()
    avg_loss = loss.rolling(window=rsi_window).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi"] = 100 - (100 / (1 + rs))

    df["signal"] = 0
    in_position = False
    for i in range(len(df)):
        if pd.isna(df["rsi"].iloc[i]):
            continue
        if not in_position and df["rsi"].iloc[i] < oversold:
            df.loc[df.index[i], "signal"] = 1
            in_position = True
        elif not in_position and df["rsi"].iloc[i] > overbought:
            df.loc[df.index[i], "signal"] = -1
            in_position = True
        elif in_position and oversold <= df["rsi"].iloc[i] <= overbought:
            df.loc[df.index[i], "signal"] = 0
            in_position = False
    return df


STRATEGY_REGISTRY = {
    "SMA Crossover": sma_crossover,
    "Momentum": momentum_strategy,
    "Mean Reversion": mean_reversion,
    "Bollinger Bands": bollinger_bands,
    "RSI Strategy": rsi_strategy,
}
