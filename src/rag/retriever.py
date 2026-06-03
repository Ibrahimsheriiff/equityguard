"""
Retriever — searches ChromaDB for chunks relevant to a query.

This is what the agent calls as a tool. It takes a natural language
query, embeds it, and returns the most semantically similar chunks
from the document store.

This is proper vector RAG — not keyword matching.
"""


from sentence_transformers import SentenceTransformer

CHROMA_PATH = "data/chroma_db"
COLLECTION  = "company_docs"
EMBED_MODEL = "paraphrase-MiniLM-L3-v2"

# Load model once at module level — not on every query
_model      = None
_client     = None
_collection = None


def _load():
    global _model, _client, _collection
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    if _client is None:
        _client     = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = _client.get_collection(COLLECTION)


def retrieve(query: str, ticker: str = "", n_results: int = 3) -> dict:
    """
    Search the vector store for chunks relevant to the query.

    If ticker is provided, filters results to that company only.
    Returns top n_results chunks with their source metadata.
    """
    try:
        _load()

        query_embedding = _model.encode(query).tolist()

        # Filter by ticker if provided
        where = {"ticker": ticker.split(".")[0].upper()} if ticker else None

        results = _collection.query(
            query_embeddings = [query_embedding],
            n_results        = n_results,
            where            = where,
            include          = ["documents", "metadatas", "distances"],
        )

        if not results["documents"] or not results["documents"][0]:
            return {
                "query": query,
                "ticker": ticker,
                "chunks_found": 0,
                "result": "No relevant documents found in the knowledge base.",
            }

        chunks = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            chunks.append({
                "text":       doc,
                "source":     meta.get("filename", "unknown"),
                "relevance":  round(1 - dist, 3),  # Convert distance to similarity score
            })

        # Format for the agent — combine top chunks into readable context
        combined = "\n\n".join(
            f"[Source: {c['source']} | Relevance: {c['relevance']}]\n{c['text']}"
            for c in chunks
        )

        return {
            "query":        query,
            "ticker":       ticker,
            "chunks_found": len(chunks),
            "result":       combined,
        }

    except Exception as e:
        return {
            "query":        query,
            "ticker":       ticker,
            "chunks_found": 0,
            "result":       f"Vector store not ready: {str(e)}. Run python -m src.rag.ingest first.",
        }


SCHEMA = {
    "name": "search_company_knowledge",
    "description": (
        "Searches the internal knowledge base for risk disclosures, company updates "
        "and fundamental information about a stock using semantic vector search. "
        "Use this to get deeper context beyond live price data — for example, "
        "known risks flagged by management, margin pressures, or strategic concerns."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language search query e.g. 'mortgage risk and margin pressure'"
            },
            "ticker": {
                "type": "string",
                "description": "Optional ticker to filter results e.g. CBA.AX"
            },
        },
        "required": ["query"]
    }
}