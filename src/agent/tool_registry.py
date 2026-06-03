import json
from src.tools.price_data import get_price_data, SCHEMA as PRICE_SCHEMA
from src.tools.technicals import get_technical_signals, SCHEMA as TECH_SCHEMA
from src.tools.news import get_news_sentiment, SCHEMA as NEWS_SCHEMA
from src.tools.earnings import get_earnings_risk, SCHEMA as EARNINGS_SCHEMA
from src.tools.document_retrieval import retrieve_company_docs, SCHEMA as DOCS_SCHEMA
from src.rag.retriever import retrieve as rag_retrieve, SCHEMA as RAG_SCHEMA


def _rag_tool(query: str, ticker: str = "") -> dict:
    return rag_retrieve(query=query, ticker=ticker)


TOOL_FUNCTIONS = {
    "get_price_data":          get_price_data,
    "get_technical_signals":   get_technical_signals,
    "get_news_sentiment":      get_news_sentiment,
    "get_earnings_risk":       get_earnings_risk,
    "retrieve_company_docs":   retrieve_company_docs,
    "search_company_knowledge": _rag_tool,
}

TOOL_SCHEMAS = [
    PRICE_SCHEMA,
    TECH_SCHEMA,
    NEWS_SCHEMA,
    EARNINGS_SCHEMA,
    DOCS_SCHEMA,
    RAG_SCHEMA,
]


def execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name not in TOOL_FUNCTIONS:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    result = TOOL_FUNCTIONS[tool_name](**tool_input)
    return json.dumps(result, default=str)