import yfinance as yf


def get_technical_signals(ticker: str) -> dict:
    """Calculate RSI, MACD and Bollinger Band position."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="3mo")

        if hist.empty or len(hist) < 30:
            return {"error": f"Not enough data for {ticker}"}

        close = hist["Close"]

        # RSI (14-period)
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        rsi = round(float(100 - (100 / (1 + rs.iloc[-1]))), 1)

        # MACD
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        macd_signal = "bullish" if macd.iloc[-1] > signal.iloc[-1] else "bearish"

        # Bollinger Bands (20-period)
        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        upper_band = sma20 + (2 * std20)
        lower_band = sma20 - (2 * std20)
        current = close.iloc[-1]
        bb_position = round(
            float((current - lower_band.iloc[-1]) /
                  (upper_band.iloc[-1] - lower_band.iloc[-1]) * 100), 1
        )

        return {
            "ticker": ticker,
            "rsi_14": rsi,
            "rsi_signal": "overbought" if rsi > 70 else "oversold" if rsi < 30 else "neutral",
            "macd_signal": macd_signal,
            "bollinger_position_pct": bb_position,
            "bollinger_signal": (
                "near upper band (overbought)" if bb_position > 80
                else "near lower band (oversold)" if bb_position < 20
                else "mid-range"
            ),
        }
    except Exception as e:
        return {"error": str(e)}


SCHEMA = {
    "name": "get_technical_signals",
    "description": "Get RSI, MACD and Bollinger Band signals. Use to assess momentum and overbought/oversold conditions.",
    "input_schema": {
        "type": "object",
        "properties": {
            "ticker": {"type": "string", "description": "Stock ticker symbol"}
        },
        "required": ["ticker"]
    }
}
