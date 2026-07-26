import streamlit as st
import pandas as pd
from engine.backtest import run_backtest
from engine.metrics import calculate_metrics
from visualization.charts import (
    equity_curve_chart, drawdown_chart,
    returns_histogram, signal_chart,
)
from visualization.reports import summary_report, trade_log
from analytics.statistics import drawdown_analysis
from config import STRATEGY_PARAMS


def render():
    st.header("Backtest Engine")
    st.markdown("Configure and run backtests on historical data.")

    data = st.session_state.get("data")
    if data is None:
        st.warning("Upload or generate data first from the Dashboard page.")
        return

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Strategy Configuration")
        strategy_name = st.selectbox(
            "Select Strategy", list(STRATEGY_PARAMS.keys())
        )

        params = {}
        if strategy_name in STRATEGY_PARAMS:
            for param_name, config in STRATEGY_PARAMS[strategy_name].items():
                if "step" in config:
                    params[param_name] = st.slider(
                        param_name.replace("_", " ").title(),
                        min_value=config["min"],
                        max_value=config["max"],
                        value=config["default"],
                        step=config["step"],
                    )
                else:
                    params[param_name] = st.slider(
                        param_name.replace("_", " ").title(),
                        min_value=config["min"],
                        max_value=config["max"],
                        value=config["default"],
                    )

        initial_capital = st.number_input(
            "Initial Capital ($)", min_value=1000, value=10000, step=1000
        )

        run_button = st.button("Run Backtest", type="primary", use_container_width=True)

    if run_button or st.session_state.get("backtest_triggered"):
        st.session_state["backtest_triggered"] = True

        with st.spinner("Running backtest..."):
            result = run_backtest(data, strategy_name, params, initial_capital)

        with col2:
            st.subheader("Performance Summary")
            metrics = result["metrics"]
            mcol1, mcol2, mcol3, mcol4 = st.columns(4)
            mcol1.metric("Total Return", f"{metrics['Total Return'] * 100:.2f}%")
            mcol2.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")
            mcol3.metric("Max Drawdown", f"{metrics['Max Drawdown'] * 100:.2f}%")
            mcol4.metric("Total Trades", str(metrics["Total Trades"]))

            mcol5, mcol6, mcol7, mcol8 = st.columns(4)
            mcol5.metric("Ann. Return", f"{metrics['Annualized Return'] * 100:.2f}%")
            mcol6.metric("Ann. Volatility", f"{metrics['Annualized Volatility'] * 100:.2f}%")
            mcol7.metric("Win Rate", f"{metrics['Win Rate'] * 100:.2f}%")
            mcol8.metric("Profit Factor", f"{metrics['Profit Factor']:.2f}")

        st.divider()
        chart_tabs = st.tabs(["Equity Curve", "Drawdown", "Returns", "Signals", "Trade Log"])

        with chart_tabs[0]:
            fig = equity_curve_chart(result["equity_curve"])
            st.plotly_chart(fig, use_container_width=True)

        with chart_tabs[1]:
            dd = drawdown_analysis(result["equity_curve"]["total"])
            fig = drawdown_chart(dd["drawdown_series"])
            st.plotly_chart(fig, use_container_width=True)
            st.info(f"Max Drawdown: **{dd['max_drawdown'] * 100:.2f}%** | "
                    f"Avg Drawdown: **{dd['avg_drawdown'] * 100:.2f}%**")

        with chart_tabs[2]:
            returns = result["equity_curve"]["total"].pct_change()
            fig = returns_histogram(returns)
            st.plotly_chart(fig, use_container_width=True)

        with chart_tabs[3]:
            fig = signal_chart(data, result["equity_curve"]["signal"])
            st.plotly_chart(fig, use_container_width=True)

        with chart_tabs[4]:
            trades_df = trade_log(result["equity_curve"])
            if not trades_df.empty:
                st.dataframe(trades_df, use_container_width=True)
                csv = trades_df.to_csv(index=False)
                st.download_button(
                    "Download Trade Log", data=csv,
                    file_name="trade_log.csv", mime="text/csv",
                )
            else:
                st.info("No trades executed.")

        st.subheader("Raw Report")
        st.text(summary_report(metrics, initial_capital))
