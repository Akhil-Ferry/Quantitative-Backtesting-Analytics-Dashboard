import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


def price_chart(data, indicators=None, title="Price Chart"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index, y=data["close"],
        mode="lines", name="Close",
        line=dict(color="#1f77b4", width=2),
    ))
    if indicators:
        for name, series in indicators.items():
            fig.add_trace(go.Scatter(
                x=series.index, y=series,
                mode="lines", name=name,
                line=dict(dash="dash"),
            ))
    fig.update_layout(
        title=title, template="plotly_dark",
        xaxis_title="Date", yaxis_title="Price",
        hovermode="x unified",
        height=500,
    )
    return fig


def equity_curve_chart(equity_curve, benchmark=True):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=equity_curve.index, y=equity_curve["total"],
        mode="lines", name="Strategy",
        line=dict(color="#00cc96", width=2),
    ))
    if benchmark and "benchmark" in equity_curve.columns:
        fig.add_trace(go.Scatter(
            x=equity_curve.index, y=equity_curve["benchmark"],
            mode="lines", name="Buy & Hold",
            line=dict(color="#636efa", width=2, dash="dash"),
        ))
    fig.update_layout(
        title="Equity Curve", template="plotly_dark",
        xaxis_title="Date", yaxis_title="Portfolio Value ($)",
        hovermode="x unified", height=450,
    )
    return fig


def drawdown_chart(drawdown_series):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=drawdown_series.index, y=drawdown_series * 100,
        mode="lines", name="Drawdown",
        fill="tozeroy", line=dict(color="#ef553b", width=1.5),
    ))
    fig.update_layout(
        title="Drawdown Analysis", template="plotly_dark",
        xaxis_title="Date", yaxis_title="Drawdown (%)",
        hovermode="x unified", height=350,
    )
    fig.update_yaxis(ticksuffix="%")
    return fig


def returns_histogram(returns, bins=60):
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=returns.dropna(), nbinsx=bins,
        marker_color="#636efa", opacity=0.75,
        name="Daily Returns",
    ))
    fig.add_vline(
        x=returns.mean(), line_dash="dash",
        line_color="#00cc96", annotation_text="Mean",
    )
    fig.add_vline(
        x=0, line_dash="dot", line_color="#ef553b",
        annotation_text="Zero",
    )
    fig.update_layout(
        title="Return Distribution", template="plotly_dark",
        xaxis_title="Daily Return", yaxis_title="Frequency",
        bargap=0.05, height=350,
    )
    return fig


def correlation_heatmap(corr_matrix):
    fig = px.imshow(
        corr_matrix,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        aspect="auto",
        title="Correlation Matrix",
        template="plotly_dark",
    )
    fig.update_layout(height=500)
    return fig


def drawdown_heatmap(returns):
    df = returns.copy()
    df = df * 100
    monthly = df.resample("ME").sum() if isinstance(df.index, pd.DatetimeIndex) else df
    if monthly.empty or monthly.isna().all().all():
        monthly = df

    years = monthly.index.year
    months = monthly.index.month_name().str[:3] if isinstance(monthly.index, pd.DatetimeIndex) else [""] * len(monthly)

    fig = go.Figure(data=go.Heatmap(
        z=monthly.values if isinstance(monthly, pd.DataFrame) and monthly.shape[1] == 1 else monthly.values,
        x=years,
        y=months if len(set(months)) > 1 else list(range(len(monthly))),
        colorscale="RdYlGn",
        zmid=0,
        text=np.round(monthly.values, 2),
        texttemplate="%{text}",
    ))
    fig.update_layout(
        title="Monthly Returns Heatmap", template="plotly_dark",
        height=400,
    )
    return fig


def performance_radar(metrics_dict):
    categories = ["Sharpe Ratio", "Sortino Ratio", "Calmar Ratio", "Win Rate", "Profit Factor"]
    fig = go.Figure()
    for strategy, metrics in metrics_dict.items():
        values = []
        for cat in categories:
            val = metrics.get(cat, 0)
            if isinstance(val, (int, float)):
                norm = min(max(val / 3, 0), 1) if cat in ["Sharpe Ratio", "Sortino Ratio", "Calmar Ratio"] else val
                values.append(norm)
            else:
                values.append(0)
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself", name=strategy,
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title="Strategy Comparison - Radar", template="plotly_dark",
        height=450,
    )
    return fig


def multi_equity_chart(results):
    fig = go.Figure()
    for name, result in results.items():
        ec = result["equity_curve"]
        fig.add_trace(go.Scatter(
            x=ec.index, y=ec["total"],
            mode="lines", name=name,
        ))
    fig.update_layout(
        title="Strategy Comparison - Equity Curves",
        template="plotly_dark",
        xaxis_title="Date", yaxis_title="Portfolio Value ($)",
        hovermode="x unified", height=500,
    )
    return fig


def signal_chart(data, signals):
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.7, 0.3],
    )
    fig.add_trace(go.Scatter(
        x=data.index, y=data["close"],
        mode="lines", name="Price",
        line=dict(color="#1f77b4"),
    ), row=1, col=1)

    buy_signals = data[signals == 1]
    sell_signals = data[signals == -1]
    fig.add_trace(go.Scatter(
        x=buy_signals.index, y=buy_signals["close"],
        mode="markers", name="Buy",
        marker=dict(color="#00cc96", size=10, symbol="triangle-up"),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=sell_signals.index, y=sell_signals["close"],
        mode="markers", name="Sell",
        marker=dict(color="#ef553b", size=10, symbol="triangle-down"),
    ), row=1, col=1)

    signals_plot = signals.replace(0, np.nan)
    fig.add_trace(go.Scatter(
        x=signals_plot.index, y=signals_plot,
        mode="lines+markers", name="Signal",
        line=dict(color="#ab63fa"),
    ), row=2, col=1)

    fig.update_layout(title="Trading Signals", template="plotly_dark", height=600)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Signal", row=2, col=1)
    return fig
