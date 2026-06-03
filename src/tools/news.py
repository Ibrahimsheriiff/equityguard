import yfinance as yf


def get_news_sentiment(ticker: str, company_name: str = "") -> dict:
    """Fetch recent headlines for a stock."""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news[:8]

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
        }
    except Exception as e:
        return {"error": str(e)}


SCHEMA = {
    "name": "get_news_sentiment",
    "description": "Fetch recent news headlines for the stock. Use to detect negative news events or sentiment shifts.",
    "input_schema": {
        "type": "object",
        "properties": {
            "ticker": {"type": "string", "description": "Stock ticker symbol"},
            "company_name": {"type": "string", "description": "Company name (optional)"}
        },
        "required": ["ticker"]
    }
}
