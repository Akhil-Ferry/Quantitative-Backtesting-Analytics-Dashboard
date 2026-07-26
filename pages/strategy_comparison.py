import streamlit as st
import pandas as pd
from engine.backtest import run_multi_backtest, compare_strategies
from config import STRATEGY_PARAMS
from visualization.charts import multi_equity_chart, performance_radar
from engine.metrics import metrics_dataframe


def render():
    st.header("Strategy Comparison")
    st.markdown("Compare multiple strategies side-by-side.")

    data = st.session_state.get("data")
    if data is None:
        st.warning("Upload or generate data first from the Dashboard page.")
        return

    st.subheader("Select Strategies to Compare")
    all_strategies = list(STRATEGY_PARAMS.keys())
    selected = st.multiselect(
        "Strategies", all_strategies,
        default=all_strategies[:3],
    )

    if not selected:
        st.info("Select at least one strategy.")
        return

    initial_capital = st.number_input(
        "Initial Capital ($)", min_value=1000, value=10000,
        step=1000, key="compare_capital",
    )

    strategies_config = {}
    with st.expander("Configure Strategy Parameters", expanded=False):
        cols = st.columns(len(selected))
        for i, name in enumerate(selected):
            with cols[i]:
                st.markdown(f"**{name}**")
                params = {}
                if name in STRATEGY_PARAMS:
                    for param_name, config in STRATEGY_PARAMS[name].items():
                        if "step" in config:
                            params[param_name] = st.slider(
                                param_name.replace("_", " ").title(),
                                key=f"{name}_{param_name}",
                                min_value=config["min"],
                                max_value=config["max"],
                                value=config["default"],
                                step=config["step"],
                            )
                        else:
                            params[param_name] = st.slider(
                                param_name.replace("_", " ").title(),
                                key=f"{name}_{param_name}",
                                min_value=config["min"],
                                max_value=config["max"],
                                value=config["default"],
                            )
                strategies_config[name] = params

    if st.button("Compare Strategies", type="primary"):
        with st.spinner("Running backtests..."):
            results = run_multi_backtest(data, strategies_config, initial_capital)

        st.divider()
        st.subheader("Results")

        comparison_df = compare_strategies(results)
        st.dataframe(comparison_df.style.format(
            {col: "{:.4f}" for col in comparison_df.select_dtypes(include="float").columns}
        ), use_container_width=True)

        csv = comparison_df.to_csv(index=False)
        st.download_button(
            "Download Comparison CSV", data=csv,
            file_name="strategy_comparison.csv", mime="text/csv",
        )

        chart_tabs = st.tabs(["Equity Curves", "Radar Chart", "Metrics Summary"])

        with chart_tabs[0]:
            fig = multi_equity_chart(results)
            st.plotly_chart(fig, use_container_width=True)

        with chart_tabs[1]:
            metrics_dict = {name: r["metrics"] for name, r in results.items()}
            fig = performance_radar(metrics_dict)
            st.plotly_chart(fig, use_container_width=True)

        with chart_tabs[2]:
            metrics_df = metrics_dataframe(
                {name: r["metrics"] for name, r in results.items()}
            )
            metrics_pivot = metrics_df.pivot_table(
                index="Strategy", columns="Metric", values="Value"
            )
            st.dataframe(
                metrics_pivot.style.background_gradient(cmap="RdYlGn", axis=None),
                use_container_width=True,
            )
