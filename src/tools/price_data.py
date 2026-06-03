import yfinance as yf


def get_price_data(ticker: str) -> dict:
    """Fetch live price, volume, beta and volatility for a stock."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="30d")

        if hist.empty:
            return {"error": f"No data found for {ticker}"}

        daily_returns = hist["Close"].pct_change().dropna()
        volatility_30d = round(float(daily_returns.std() * (252 ** 0.5) * 100), 2)

        return {
            "ticker": ticker,
            "current_price": round(info.get("currentPrice", hist["Close"].iloc[-1]), 2),
            "previous_close": round(info.get("previousClose", 0), 2),
            "day_change_pct": round(info.get("regularMarketChangePercent", 0), 2),
            "volume": info.get("regularMarketVolume", 0),
            "avg_volume_10d": info.get("averageVolume10days", 0),
            "beta": info.get("beta", "N/A"),
            "volatility_30d_annualised_pct": volatility_30d,
            "52w_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52w_low": info.get("fiftyTwoWeekLow", "N/A"),
        }
    except Exception as e:
        return {"error": str(e)}


SCHEMA = {
    "name": "get_price_data",
    "description": "Get live price, volume, beta and 30-day volatility for a stock ticker. Use this first to understand baseline risk.",
    "input_schema": {
        "type": "object",
        "properties": {
            "ticker": {"type": "string", "description": "Stock ticker e.g. CBA.AX, AAPL"}
        },
        "required": ["ticker"]
    }
}
