from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.schemas import RiskRequest, RiskResponse, TraceStep
from src.agent.react_loop import run_agent
from src.safety.financial_guardrails import is_financial_advice_request, refusal_message
from src.evaluation.evaluator import run_evaluation
import yfinance as yf
import re

app = FastAPI(
    title="EquityGuard API",
    description="AI-powered equity risk assessment using a custom ReAct agent.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "EquityGuard API", "version": "1.0.0"}


@app.get("/price/{ticker}")
def get_price(ticker: str):
    try:
        t     = yf.Ticker(ticker)
        info  = t.info
        price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        prev  = info.get("previousClose", price)
        chg   = round(((price - prev) / prev) * 100, 2) if prev else 0
        return {"ticker": ticker, "price": round(price, 2), "change": chg}
    except Exception as e:
        return {"ticker": ticker, "price": 0, "change": 0}


@app.post("/analyse", response_model=RiskResponse)
def analyse_stock(request: RiskRequest):
    ticker = request.ticker.strip().upper()
    query  = request.user_query or f"Assess the current risk level of {ticker}"

    if is_financial_advice_request(query):
        raise HTTPException(status_code=400, detail=refusal_message())

    result, trace = run_agent(query, ticker=ticker, verbose=False)

    score_match = re.search(r'(\d+)/10', result)
    risk_score  = int(score_match.group(1)) if score_match else None
    risk_label  = (
        "Low Risk"    if risk_score and risk_score <= 3 else
        "High Risk"   if risk_score and risk_score >= 7 else
        "Medium Risk"
    )

    trace_steps = [
        TraceStep(
            step_number         = step.step_number,
            thought             = step.thought,
            tool_name           = step.tool_name,
            tool_input          = step.tool_input,
            tool_output_summary = step.tool_output_summary,
            timestamp           = step.timestamp,
        )
        for step in trace.steps
    ]

    return RiskResponse(
        ticker       = ticker,
        risk_score   = risk_score,
        risk_label   = risk_label,
        explanation  = result,
        tools_called = [s.tool_name for s in trace.steps],
        trace        = trace_steps,
    )


@app.get("/evaluate")
def evaluate():
    results = run_evaluation(run_agent)
    return results


@app.get("/health")
def detailed_health():
    return {
        "status": "ok",
        "agent": "ReAct loop",
        "tools": ["get_price_data", "get_technical_signals",
                  "get_news_sentiment", "get_earnings_risk",
                  "retrieve_company_docs", "search_company_knowledge"],
    }