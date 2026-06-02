# 🛡️ EquityGuard

I built this because I invest in ASX stocks and I was tired of manually checking price movements, reading news and trying to figure out if a stock was actually risky or just volatile. I wanted something that could do that investigation for me and give me a straight answer.

![Dashboard](screenshots/dashboard.png)

## What it does

You pick a stock. The agent investigates it — live price, technicals, news, earnings calendar — and comes back with a risk score and an explanation of why.

![Result](screenshots/result.png)

## The part I'm most proud of

It's not a wrapper. Most AI finance tools just call a fixed sequence of APIs and paste the results into a prompt. That's not an agent, that's a pipeline.

EquityGuard uses a ReAct loop — the model reads what it finds and decides what to look at next. If it spots unusual volume it goes to check news. If news is clean it might stop early. If earnings are in 3 days it flags that as the dominant risk. The investigation path isn't preset — it emerges from what the data actually shows.

```
You:   "How risky is CBA.AX?"

Agent: I need to check price first              → calls get_price_data
Agent: Volume is 36% of average, that's odd    → calls get_news_sentiment  
Agent: Found a mortgage slowdown headline       → calls get_earnings_risk
Agent: Earnings already passed, no event risk  → enough, synthesise

Result: 5/10 Medium — here's exactly why
```

## Stack

- **Anthropic Claude API** — the reasoning engine
- **yfinance** — live ASX and US market data
- **pandas** — RSI, MACD, Bollinger Bands computed from scratch
- **Streamlit** — the UI
- No agent frameworks — the loop is ~80 lines of plain Python

## Run it

```bash
git clone https://github.com/Ibrahimsheriiff/equityguard.git
cd equityguard
pip install anthropic yfinance pandas requests python-dotenv streamlit
echo 'ANTHROPIC_API_KEY=your-key' > .env
python -m streamlit run app.py
```