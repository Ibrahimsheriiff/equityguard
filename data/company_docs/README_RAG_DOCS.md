# EquityGuard RAG Documents

This folder contains starter documents for the EquityGuard RAG system.

## Folder Structure

```text
data/rag_docs/
├── company/
├── education/
└── policy/
```

## Purpose

These documents are designed to help EquityGuard retrieve useful context before generating a stock risk explanation.

## Important Disclaimer

The company files in this starter pack are synthetic sample documents for software testing and portfolio demonstration only. They are not official company announcements, financial reports, or investment research.

For a production system, replace the sample company documents with verified sources such as:
- ASX announcements
- company annual reports
- investor presentations
- official market updates
- regulatory filings

## Suggested RAG Behaviour

The agent should retrieve:
- policy documents when the user asks for financial advice
- education documents when explaining technical indicators or market risk
- company documents when analysing a specific ticker

## Example Retrieval Cases

| User/Agent Situation | Useful Document |
|---|---|
| User asks "Should I buy CBA?" | financial_advice_policy.txt |
| Agent sees high RSI | what_is_rsi.txt |
| Agent sees bearish MACD | what_is_macd.txt |
| Agent sees upcoming earnings | earnings_risk_explainer.txt |
| Agent analyses BHP.AX | BHP_sample_risk_note.txt |
```
