import streamlit as st
import pandas as pd
import numpy as np
from analytics.statistics import (
    rolling_stats, variance_analysis,
    return_distribution,
)
from analytics.indicators import add_all_indicators
from analytics.correlation import correlation_matrix, rolling_correlation
from visualization.charts import (
    price_chart, correlation_heatmap,
    returns_histogram, drawdown_heatmap,
)


def render():
    st.header("Analytics")
    st.markdown("Statistical analysis and technical indicators.")

    data = st.session_state.get("data")
    if data is None:
        st.warning("Upload or generate data first from the Dashboard page.")
        return

    full_data = add_all_indicators(data)

    tab1, tab2, tab3, tab4 = st.tabs([
        "Technical Indicators", "Rolling Statistics",
        "Return Analysis", "Correlation",
    ])

    with tab1:
        st.subheader("Technical Indicators")
        cols = [c for c in full_data.columns if c not in ["open", "high", "low", "volume"]]
        indicators_dict = {}
        indicator_names = ["EMA_12", "EMA_26", "BB_Upper", "BB_Middle", "BB_Lower", "RSI"]
        for name in indicator_names:
            if name in full_data.columns:
                indicators_dict[name] = full_data[name]

        fig = price_chart(data, indicators_dict, "Price with Indicators")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("RSI")
        if "RSI" in full_data.columns:
            import plotly.graph_objects as go
            rsi_fig = go.Figure()
            rsi_fig.add_trace(go.Scatter(
                x=full_data.index, y=full_data["RSI"],
                mode="lines", name="RSI",
                line=dict(color="#ab63fa"),
            ))
            rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
            rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
            rsi_fig.update_layout(
                title="Relative Strength Index",
                template="plotly_dark", height=300,
            )
            st.plotly_chart(rsi_fig, use_container_width=True)

        st.subheader("MACD")
        macd_cols = ["MACD_MACD", "MACD_Signal", "MACD_Histogram"]
        if all(c in full_data.columns for c in macd_cols):
            import plotly.graph_objects as go
            macd_fig = go.Figure()
            macd_fig.add_trace(go.Scatter(
                x=full_data.index, y=full_data["MACD_MACD"],
                mode="lines", name="MACD", line=dict(color="#636efa"),
            ))
            macd_fig.add_trace(go.Scatter(
                x=full_data.index, y=full_data["MACD_Signal"],
                mode="lines", name="Signal", line=dict(color="#ef553b"),
            ))
            colors = ["green" if v >= 0 else "red" for v in full_data["MACD_Histogram"]]
            macd_fig.add_bar(
                x=full_data.index, y=full_data["MACD_Histogram"],
                name="Histogram", marker_color=colors,
            )
            macd_fig.update_layout(
                title="MACD", template="plotly_dark", height=300,
            )
            st.plotly_chart(macd_fig, use_container_width=True)

    with tab2:
        st.subheader("Rolling Statistics")
        close = data["close"]
        roll_df = rolling_stats(close, windows=[20, 50])
        col_a, col_b = st.columns(2)

        with col_a:
            import plotly.graph_objects as go
            mean_fig = go.Figure()
            for col in [c for c in roll_df.columns if "mean" in c]:
                mean_fig.add_trace(go.Scatter(
                    x=roll_df.index, y=roll_df[col],
                    mode="lines", name=col,
                ))
            mean_fig.update_layout(
                title="Rolling Means",
                template="plotly_dark", height=350,
            )
            st.plotly_chart(mean_fig, use_container_width=True)

        with col_b:
            std_fig = go.Figure()
            for col in [c for c in roll_df.columns if "std" in c]:
                std_fig.add_trace(go.Scatter(
                    x=roll_df.index, y=roll_df[col],
                    mode="lines", name=col,
                ))
            std_fig.update_layout(
                title="Rolling Standard Deviations",
                template="plotly_dark", height=350,
            )
            st.plotly_chart(std_fig, use_container_width=True)

        st.subheader("Variance Analysis")
        var_df = variance_analysis(data)
        var_fig = price_chart(
            var_df[["rolling_volatility"]].rename(columns={"rolling_volatility": "close"}),
            {"EWMA Variance": var_df["ewma_variance"]},
            "Volatility Analysis",
        )
        st.plotly_chart(var_fig, use_container_width=True)

    with tab3:
        col_a, col_b = st.columns(2)
        returns = data["close"].pct_change().dropna()

        with col_a:
            fig = returns_histogram(returns)
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            dist = return_distribution(returns)
            st.metric("Skewness", f"{dist['skewness']:.4f}")
            st.metric("Kurtosis (Excess)", f"{dist['kurtosis']:.4f}")
            jb_stat, jb_p = dist["jarque_bera"]
            st.metric("Jarque-Bera", f"{jb_stat:.2f}")
            st.metric("JB p-value", f"{jb_p:.4f}")
            st.caption("p < 0.05 suggests non-normal distribution")

        st.subdivision("Monthly Returns Heatmap")
        monthly_returns = data["close"].resample("ME").last().pct_change().dropna().to_frame("returns")
        if len(monthly_returns) > 1:
            fig = drawdown_heatmap(monthly_returns)
            st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.subheader("Correlation Analysis")
        # use multiple tickers if available
        if "ticker" in data.columns:
            pivot = data.pivot_table(index=data.index, columns="ticker", values="close")
            corr = correlation_matrix(pivot)
        else:
            # create lagged series for auto-correlation
            close = data["close"]
            lag_df = pd.DataFrame({
                "close": close,
                "lag_1": close.shift(1),
                "lag_5": close.shift(5),
                "lag_20": close.shift(20),
            }).dropna()
            corr = correlation_matrix(lag_df)

        fig = correlation_heatmap(corr)
        st.plotly_chart(fig, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            window = st.slider("Rolling Correlation Window", 10, 100, 30)
        with col_b:
            pass

        if len(data.columns) > 1:
            returns = data.select_dtypes(include=[np.number]).pct_change().dropna()
            if returns.shape[1] >= 2:
                roll_corr = rolling_correlation(
                    returns.iloc[:, 0], returns.iloc[:, 1], window
                )
                import plotly.graph_objects as go
                corr_fig = go.Figure()
                corr_fig.add_trace(go.Scatter(
                    x=roll_corr.index, y=roll_corr,
                    mode="lines", name=f"Rolling Corr (w={window})",
                    line=dict(color="#00cc96"),
                ))
                corr_fig.add_hline(y=0, line_dash="dash", line_color="gray")
                corr_fig.update_layout(
                    title="Rolling Correlation",
                    template="plotly_dark", height=350,
                )
                st.plotly_chart(corr_fig, use_container_width=True)
