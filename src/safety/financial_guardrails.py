ADVICE_KEYWORDS = [
    "should i buy",
    "should i sell",
    "buy or sell",
    "guaranteed profit",
    "make money",
    "which stock should i buy",
    "tell me what to invest in",
    "is it a good investment",
    "will it go up",
    "will it go down",
    "should i invest",
    "make me rich",
    "which stock will make",
]


def is_financial_advice_request(user_query: str) -> bool:
    query = user_query.lower()
    return any(keyword in query for keyword in ADVICE_KEYWORDS)


def refusal_message() -> str:
    return (
        "I can analyse risk factors, volatility, technical signals, news and earnings risk, "
        "but I cannot tell you whether you personally should buy, sell or hold a stock. "
        "This is educational information only and not financial advice. "
        "Please consult a licensed financial adviser before making investment decisions."
    )


DISCLAIMER = (
    "\n\n---\n"
    "⚠️ This assessment is for informational purposes only and does not constitute financial advice. "
    "Always consult a licensed financial adviser before making investment decisions."
)