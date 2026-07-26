APP_TITLE = "Quantitative Backtesting & Analytics Dashboard"
APP_ICON = "📈"
PAGE_CONFIG = {"layout": "wide", "initial_sidebar_state": "expanded"}

DEFAULT_START_DATE = "2020-01-01"
DEFAULT_END_DATE = "2024-01-01"
RISK_FREE_RATE = 0.02

SAMPLE_TICKERS = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "JPM", "V", "JNJ"]

STRATEGY_PARAMS = {
    "SMA Crossover": {
        "short_window": {"min": 5, "max": 100, "default": 20},
        "long_window": {"min": 20, "max": 300, "default": 60},
    },
    "Momentum": {
        "lookback": {"min": 5, "max": 120, "default": 20},
        "threshold": {"min": 0.0, "max": 0.1, "default": 0.02, "step": 0.005},
    },
    "Mean Reversion": {
        "window": {"min": 5, "max": 100, "default": 20},
        "entry_z": {"min": 0.5, "max": 3.0, "default": 2.0, "step": 0.1},
        "exit_z": {"min": 0.0, "max": 1.5, "default": 0.5, "step": 0.1},
    },
    "Bollinger Bands": {
        "window": {"min": 5, "max": 100, "default": 20},
        "num_std": {"min": 1.0, "max": 4.0, "default": 2.0, "step": 0.1},
    },
    "RSI Strategy": {
        "rsi_window": {"min": 5, "max": 50, "default": 14},
        "oversold": {"min": 10, "max": 40, "default": 30},
        "overbought": {"min": 60, "max": 90, "default": 70},
    },
}
