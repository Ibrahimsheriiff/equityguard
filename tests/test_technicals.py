"""
Tests for technical indicator calculations.
Uses synthetic price data — no live API calls needed.
"""

import pandas as pd
import numpy as np


def make_price_series(n=60, start=100, volatility=2):
    """Generate a synthetic price series for testing."""
    np.random.seed(42)
    changes = np.random.randn(n) * volatility
    prices  = start + np.cumsum(changes)
    return pd.Series(prices)


def calculate_rsi(close, period=14):
    delta = close.diff()
    gain  = delta.where(delta > 0, 0).rolling(period).mean()
    loss  = -delta.where(delta < 0, 0).rolling(period).mean()
    rs    = gain / loss
    return 100 - (100 / (1 + rs))


def calculate_bollinger_position(close, period=20):
    sma   = close.rolling(period).mean()
    std   = close.rolling(period).std()
    upper = sma + (2 * std)
    lower = sma - (2 * std)
    current = close.iloc[-1]
    return float((current - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1]) * 100)


# ── RSI tests ──────────────────────────────────────────────────────────────

def test_rsi_in_valid_range():
    close = make_price_series(60)
    rsi   = calculate_rsi(close).dropna()
    assert (rsi >= 0).all() and (rsi <= 100).all()

def test_rsi_overbought_on_rising_prices():
    # Steadily rising prices should push RSI toward overbought
    close = pd.Series(range(1, 61, 1), dtype=float)
    rsi   = calculate_rsi(close).iloc[-1]
    assert rsi > 70, f"Expected RSI > 70 for rising prices, got {rsi:.1f}"

def test_rsi_oversold_on_falling_prices():
    # Steadily falling prices should push RSI toward oversold
    close = pd.Series(range(60, 0, -1), dtype=float)
    rsi   = calculate_rsi(close).iloc[-1]
    assert rsi < 30, f"Expected RSI < 30 for falling prices, got {rsi:.1f}"

def test_rsi_requires_enough_data():
    close = make_price_series(10)  # Too few for 14-period RSI
    rsi   = calculate_rsi(close)
    assert rsi.dropna().empty or len(rsi.dropna()) < 5


# ── Bollinger Band tests ───────────────────────────────────────────────────

def test_bollinger_position_is_numeric():
    close    = make_price_series(60)
    position = calculate_bollinger_position(close)
    assert isinstance(position, float)

def test_bollinger_position_range():
    # For normal price series, position should be between -50 and 150
    # (can exceed 0-100 during extreme moves)
    close    = make_price_series(60)
    position = calculate_bollinger_position(close)
    assert -50 < position < 150, f"Bollinger position {position:.1f} is extreme"

def test_high_price_near_upper_band():
    # Gradually rising prices should push position toward upper band
    close = pd.Series([100 + i * 0.5 for i in range(60)], dtype=float)
    pos   = calculate_bollinger_position(close)
    assert not np.isnan(pos), "Bollinger position should not be NaN"
    assert pos > 50, f"Expected position > 50 for rising prices, got {pos:.1f}"