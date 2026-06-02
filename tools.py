import yfinance as yf
import requests
import json
from datetime import datetime, timedelta

# ── TOOL 1: Price & volatility ─────────────────────────────────────────────
def get_price_data(ticker: str) -> dict:
    """Fetch live price, volume, beta and volatility for a stock."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="30d")

        if hist.empty:
            return {"error": f"No data found for {ticker}"}

        # Calculate 30-day volatility (std of daily returns)
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


# ── TOOL 2: Technical indicators ───────────────────────────────────────────
def get_technical_signals(ticker: str) -> dict:
    """Calculate RSI, MACD signal and Bollinger Band position."""
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


# ── TOOL 3: News sentiment ─────────────────────────────────────────────────
def get_news_sentiment(ticker: str, company_name: str = "") -> dict:
    """Fetch recent headlines for the stock via yfinance (free, no key needed)."""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news[:8]  # last 8 articles

        if not news:
            return {"ticker": ticker, "headlines": [], "note": "No recent news found"}

        headlines = []
        for article in news:
            content = article.get("content", {})
            headlines.append({
                "title": content.get("title", "N/A"),
                "published": content.get("pubDate", "N/A"),
                "summary": content.get("summary", "")[:200],
            })

        return {
            "ticker": ticker,
            "headline_count": len(headlines),
            "headlines": headlines,
            "note": "Sentiment interpretation is for the agent to reason about",
        }
    except Exception as e:
        return {"error": str(e)}


# ── TOOL 4: Earnings calendar ──────────────────────────────────────────────
def get_earnings_risk(ticker: str) -> dict:
    """Check how close the next earnings date is (higher risk near earnings)."""
    try:
        stock = yf.Ticker(ticker)
        calendar = stock.calendar

        if calendar is None or not isinstance(calendar, dict):
            return {
                "ticker": ticker,
                
                "earnings_risk": "unknown",
                "note": "No earnings date found"
            }

        earnings_date = list(calendar.values())[0]  # first upcoming date

        # Handle both Timestamp and datetime
        if hasattr(earnings_date, 'date'):
            earnings_date = earnings_date.date()

        days_to = (earnings_date - datetime.now().date()).days

        if days_to < 0:
            risk = "past"
        elif days_to <= 7:
            risk = "very high — earnings within 1 week"
        elif days_to <= 21:
            risk = "elevated — earnings within 3 weeks"
        elif days_to <= 42:
            risk = "moderate — earnings within 6 weeks"
        else:
            risk = "low — earnings far out"

        return {
            "ticker": ticker,
            "next_earnings_date": str(earnings_date),
            "days_to_earnings": days_to,
            "earnings_risk": risk,
        }
    except Exception as e:
        return {"ticker": ticker, "earnings_risk": "unknown", "error": str(e)}


# ── TOOL REGISTRY (used by the agent loop) ────────────────────────────────
# Maps tool name → function. Agent calls by name, we dispatch here.
TOOL_FUNCTIONS = {
    "get_price_data": get_price_data,
    "get_technical_signals": get_technical_signals,
    "get_news_sentiment": get_news_sentiment,
    "get_earnings_risk": get_earnings_risk,
}

def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool by name and return result as JSON string."""
    if tool_name not in TOOL_FUNCTIONS:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    result = TOOL_FUNCTIONS[tool_name](**tool_input)
    return json.dumps(result, default=str)


# ── TOOL SCHEMAS (what we pass to Claude so it knows what tools exist) ─────
TOOL_SCHEMAS = [
    {
        "name": "get_price_data",
        "description": "Get live price, volume, beta and 30-day volatility for a stock ticker. Use this first to understand baseline risk.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol e.g. CBA.AX, AAPL, TSLA"
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "get_technical_signals",
        "description": "Get RSI, MACD and Bollinger Band signals. Use to assess momentum and overbought/oversold conditions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol"}
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "get_news_sentiment",
        "description": "Fetch recent news headlines for the stock. Use to detect negative news events or sentiment shifts.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol"},
                "company_name": {"type": "string", "description": "Company name for context (optional)"}
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "get_earnings_risk",
        "description": "Check days until next earnings report. Stocks are riskier close to earnings. Use this to flag earnings proximity risk.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol"}
            },
            "required": ["ticker"]
        }
    },
]