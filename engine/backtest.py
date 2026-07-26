import pandas as pd
import numpy as np
from .strategies import STRATEGY_REGISTRY
from .metrics import calculate_metrics


def run_backtest(data, strategy_name, params=None, initial_capital=10000.0):
    if strategy_name not in STRATEGY_REGISTRY:
        raise ValueError(f"Unknown strategy: {strategy_name}")

    params = params or {}
    strategy_fn = STRATEGY_REGISTRY[strategy_name]
    df = strategy_fn(data.copy(), **params)

    df["position"] = df["signal"].shift(1).fillna(0)
    df["daily_return"] = df["position"] * df["close"].pct_change().fillna(0)
    df["strategy_returns"] = df["daily_return"]

    df["total"] = initial_capital * (1 + df["strategy_returns"]).cumprod()
    df["benchmark"] = initial_capital * (1 + df["close"].pct_change().fillna(0)).cumprod()
    df["total"] = df["total"].fillna(initial_capital)
    df["benchmark"] = df["benchmark"].fillna(initial_capital)

    fees = params.get("fees", 0.001)
    trades = df["signal"].diff().fillna(0).abs() > 0
    df.loc[trades, "strategy_returns"] -= fees

    metrics = calculate_metrics(df, risk_free_rate=0.02)

    return {
        "equity_curve": df,
        "metrics": metrics,
        "strategy_name": strategy_name,
        "initial_capital": initial_capital,
    }


def run_multi_backtest(data, strategies_config, initial_capital=10000.0):
    results = {}
    for strategy_name, params in strategies_config.items():
        result = run_backtest(data, strategy_name, params, initial_capital)
        results[strategy_name] = result
    return results


def compare_strategies(results):
    comparisons = []
    for name, result in results.items():
        row = {"Strategy": name}
        row.update(result["metrics"])
        comparisons.append(row)
    return pd.DataFrame(comparisons)
