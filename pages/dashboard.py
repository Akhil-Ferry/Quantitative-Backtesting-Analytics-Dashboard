import streamlit as st
import pandas as pd
import numpy as np
from data.sample_data import generate_sample_data, generate_multi_ticker_data
from analytics.statistics import drawdown_analysis, stability_analysis
from visualization.charts import price_chart, drawdown_chart
from config import SAMPLE_TICKERS


def render():
    st.header("Dashboard")
    st.markdown("Load or generate data to get started.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Load Data")
        uploaded_file = st.file_uploader(
            "Upload CSV",
            type=["csv"],
            help="CSV must have columns: date, open, high, low, close, volume",
        )

        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                date_cols = [c for c in df.columns if "date" in c.lower() or "time" in c.lower()]
                if date_cols:
                    df[date_cols[0]] = pd.to_datetime(df[date_cols[0]])
                    df = df.set_index(date_cols[0])
                df.columns = df.columns.str.lower().str.strip()
                required = {"open", "high", "low", "close", "volume"}
                missing = required - set(df.columns)
                if missing:
                    st.error(f"Missing columns: {missing}. Found: {list(df.columns)}")
                else:
                    st.session_state["data"] = df
                    st.session_state["data_source"] = uploaded_file.name
                    st.success(f"Loaded {len(df)} rows from {uploaded_file.name}")
            except Exception as e:
                st.error(f"Error loading file: {e}")

    with col2:
        st.subheader("Generate Sample Data")
        ticker = st.selectbox("Ticker", SAMPLE_TICKERS, index=0)
        start = st.date_input("Start Date", pd.to_datetime("2020-01-01"))
        end = st.date_input("End Date", pd.to_datetime("2024-01-01"))

        if st.button("Generate Sample Data", type="primary", use_container_width=True):
            df = generate_sample_data(ticker, str(start), str(end))
            df["ticker"] = ticker
            st.session_state["data"] = df
            st.session_state["data_source"] = f"Sample: {ticker}"
            st.success(f"Generated {len(df)} rows for {ticker}")

    st.divider()
    data = st.session_state.get("data")

    if data is not None:
        st.subheader(f"Data Preview — {st.session_state.get('data_source', 'Loaded Data')}")
        tab1, tab2, tab3, tab4 = st.tabs(["Preview", "Price Chart", "Statistics", "Raw Data"])

        with tab1:
            col_a, col_b, col_c, col_d, col_e = st.columns(5)
            close = data["close"]
            returns = close.pct_change().dropna()
            col_a.metric("Latest Close", f"${close.iloc[-1]:.2f}", f"{returns.iloc[-1] * 100:.2f}%")
            col_b.metric("Mean Close", f"${close.mean():.2f}")
            col_c.metric("Min Close", f"${close.min():.2f}")
            col_d.metric("Max Close", f"${close.max():.2f}")
            col_e.metric("Std Dev", f"${close.std():.2f}")

            col_f, col_g, col_h, col_i, col_j = st.columns(5)
            col_f.metric("Start Date", str(data.index[0].date() if hasattr(data.index[0], 'date') else data.index[0]))
            col_g.metric("End Date", str(data.index[-1].date() if hasattr(data.index[-1], 'date') else data.index[-1]))
            col_h.metric("Total Days", len(data))
            col_i.metric("Total Return", f"{((close.iloc[-1] / close.iloc[0]) - 1) * 100:.2f}%")
            col_j.metric("Avg Volume", f"{data['volume'].mean():,.0f}")

        with tab2:
            fig = price_chart(data)
            st.plotly_chart(fig, use_container_width=True)

        with tab3:
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("Return Statistics")
                ret = data["close"].pct_change().dropna()
                stats_df = pd.DataFrame({
                    "Statistic": ["Mean", "Median", "Std Dev", "Min", "Max", "Skewness", "Kurtosis"],
                    "Value": [
                        f"{ret.mean() * 100:.4f}%",
                        f"{ret.median() * 100:.4f}%",
                        f"{ret.std() * 100:.4f}%",
                        f"{ret.min() * 100:.4f}%",
                        f"{ret.max() * 100:.4f}%",
                        f"{ret.skew():.4f}",
                        f"{ret.kurtosis():.4f}",
                    ],
                })
                st.dataframe(stats_df, use_container_width=True)

            with col_b:
                st.subheader("Drawdown")
                dd = drawdown_analysis(data["close"].pct_change().fillna(0).add(1).cumprod())
                st.metric("Max Drawdown", f"{dd['max_drawdown'] * 100:.2f}%")
                st.metric("Avg Drawdown", f"{dd['avg_drawdown'] * 100:.2f}%")
                if dd["drawdown_durations"]:
                    st.metric("Avg DD Duration (days)", f"{np.mean(dd['drawdown_durations']):.1f}")
                    st.metric("Max DD Duration (days)", f"{max(dd['drawdown_durations'])}")
                fig = drawdown_chart(dd["drawdown_series"])
                st.plotly_chart(fig, use_container_width=True)

        with tab4:
            st.dataframe(data, use_container_width=True)
            csv = data.to_csv()
            st.download_button(
                "Download CSV", data=csv,
                file_name="data.csv", mime="text/csv",
            )
