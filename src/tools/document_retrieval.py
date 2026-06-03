import os

DOCS_PATH = "data/equityguard_rag_docs"


def retrieve_company_docs(ticker: str) -> dict:
    """
    Retrieves internal company documents, risk summaries and market updates
    for a given stock ticker.

    This is the RAG retrieval tool — it searches the document store for
    any files matching the ticker and returns the relevant content.
    """
    if not os.path.exists(DOCS_PATH):
        return {"ticker": ticker, "result": "Document store not found.", "docs_found": 0}

    matched_docs = []
    # Strip exchange suffix — CBA.AX → CBA
    base_ticker = ticker.split(".")[0].upper()

    for filename in os.listdir(DOCS_PATH):
        if base_ticker.lower() in filename.lower():
            filepath = os.path.join(DOCS_PATH, filename)
            with open(filepath, "r") as f:
                content = f.read()
                matched_docs.append({
                    "filename": filename,
                    "content": content,
                })

    if not matched_docs:
        return {
            "ticker": ticker,
            "result": f"No internal documents found for {ticker}.",
            "docs_found": 0,
        }

    combined = "\n\n---\n\n".join(
        f"[{doc['filename']}]\n{doc['content']}" for doc in matched_docs
    )

    return {
        "ticker": ticker,
        "docs_found": len(matched_docs),
        "result": combined,
    }


SCHEMA = {
    "name": "retrieve_company_docs",
    "description": (
        "Retrieves internal company documents, risk disclosures and market updates for a stock. "
        "Use this when you want deeper fundamental context beyond price and technical signals — "
        "for example, known risks flagged by management, margin pressures, or regulatory concerns."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "Stock ticker e.g. CBA.AX, AAPL, BHP.AX"
            }
        },
        "required": ["ticker"]
    }
}