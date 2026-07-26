import numpy as np
import pandas as pd


def calculate_metrics(equity_curve, risk_free_rate=0.02):
    returns = equity_curve["total"].pct_change().dropna()
    if len(returns) == 0:
        return {}

    total_return = equity_curve["total"].iloc[-1] / equity_curve["total"].iloc[0] - 1
    n_days = len(returns)
    ann_return = (1 + total_return) ** (252 / n_days) - 1 if n_days > 0 else 0
    ann_vol = returns.std() * np.sqrt(252)
    sharpe = (ann_return - risk_free_rate) / ann_vol if ann_vol > 0 else 0
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative / running_max) - 1
    max_drawdown = drawdown.min()

    positive = returns[returns > 0]
    negative = returns[returns < 0]
    win_rate = len(positive) / len(returns) if len(returns) > 0 else 0
    avg_win = positive.mean() if len(positive) > 0 else 0
    avg_loss = negative.mean() if len(negative) > 0 else 0
    profit_factor = abs(positive.sum() / negative.sum()) if negative.sum() != 0 else np.inf

    calmar = ann_return / abs(max_drawdown) if max_drawdown != 0 else 0
    sortino = (ann_return - risk_free_rate) / (negative.std() * np.sqrt(252)) if len(negative) > 0 and negative.std() > 0 else 0

    return {
        "Total Return": total_return,
        "Annualized Return": ann_return,
        "Annualized Volatility": ann_vol,
        "Sharpe Ratio": sharpe,
        "Sortino Ratio": sortino,
        "Max Drawdown": max_drawdown,
        "Calmar Ratio": calmar,
        "Win Rate": win_rate,
        "Average Win": avg_win,
        "Average Loss": avg_loss,
        "Profit Factor": profit_factor,
        "Total Trades": _count_trades(equity_curve),
    }


def _count_trades(equity_curve):
    if "signal" not in equity_curve.columns:
        return 0
    signal_diff = equity_curve["signal"].diff().fillna(0)
    return int((signal_diff != 0).sum())


def metrics_dataframe(metrics_dict):
    rows = []
    for strategy, metrics in metrics_dict.items():
        for key, value in metrics.items():
            if isinstance(value, float):
                rows.append({"Strategy": strategy, "Metric": key, "Value": value})
    return pd.DataFrame(rows)
