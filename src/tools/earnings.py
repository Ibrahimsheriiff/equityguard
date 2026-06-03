import yfinance as yf
from datetime import datetime


def get_earnings_risk(ticker: str) -> dict:
    """Check how close the next earnings date is."""
    try:
        stock = yf.Ticker(ticker)
        calendar = stock.calendar

        if not calendar or not isinstance(calendar, dict):
            return {"ticker": ticker, "earnings_risk": "unknown", "note": "No earnings date found"}

        earnings_date = list(calendar.values())[0]
        if hasattr(earnings_date, 'date'):
            earnings_date = earnings_date.date()

        days_to = (earnings_date - datetime.now().date()).days

        if days_to < 0:
            risk = "past — already reported"
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


SCHEMA = {
    "name": "get_earnings_risk",
    "description": "Check days until next earnings report. Stocks are riskier close to earnings.",
    "input_schema": {
        "type": "object",
        "properties": {
            "ticker": {"type": "string", "description": "Stock ticker symbol"}
        },
        "required": ["ticker"]
    }
}
