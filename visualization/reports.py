import pandas as pd
import numpy as np


def summary_report(metrics, initial_capital=10000):
    lines = []
    lines.append("=" * 60)
    lines.append("BACKTEST SUMMARY REPORT")
    lines.append("=" * 60)
    lines.append(f"Initial Capital: ${initial_capital:,.2f}")

    for key, value in metrics.items():
        if key == "Total Trades":
            lines.append(f"{key}: {value}")
        elif isinstance(value, float):
            if "Ratio" in key or "Rate" in key:
                lines.append(f"{key}: {value:.4f}")
            elif "Return" in key:
                lines.append(f"{key}: {value * 100:.2f}%")
            elif "Volatility" in key:
                lines.append(f"{key}: {value * 100:.2f}%")
            elif "Drawdown" in key:
                lines.append(f"{key}: {value * 100:.2f}%")
            else:
                lines.append(f"{key}: {value:.4f}")
        else:
            lines.append(f"{key}: {value}")

    lines.append("=" * 60)
    return "\n".join(lines)


def trade_log(equity_curve):
    trades = []
    in_trade = False
    entry_price = 0
    entry_date = None
    trade_type = None

    for i in range(len(equity_curve)):
        signal = equity_curve["signal"].iloc[i]
        price = equity_curve["close"].iloc[i]
        date = equity_curve.index[i]

        if signal != 0 and not in_trade:
            in_trade = True
            entry_price = price
            entry_date = date
            trade_type = "Long" if signal == 1 else "Short"
        elif signal == 0 and in_trade:
            in_trade = False
            exit_price = price
            pnl = (exit_price - entry_price) / entry_price
            if trade_type == "Short":
                pnl = -pnl
            trades.append({
                "Entry Date": entry_date,
                "Exit Date": date,
                "Type": trade_type,
                "Entry Price": round(entry_price, 2),
                "Exit Price": round(exit_price, 2),
                "PnL %": round(pnl * 100, 2),
            })

    return pd.DataFrame(trades)
