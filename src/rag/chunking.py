"""
Chunking — splits documents into smaller pieces before embedding.

Why chunk? Because embedding models have a token limit (~512 tokens).
A full annual report would overflow. Chunking splits it into overlapping
windows so no context is lost at boundaries.
"""


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks.

    chunk_size: max characters per chunk
    overlap: characters shared between consecutive chunks
             (prevents losing context at chunk boundaries)
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to break at a sentence boundary instead of mid-word
        if end < len(text):
            # Look for a full stop or newline near the end of the chunk
            boundary = text.rfind(".", start, end)
            if boundary == -1:
                boundary = text.rfind("\n", start, end)
            if boundary != -1 and boundary > start:
                end = boundary + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap  # Overlap with previous chunk

    return chunks


def chunk_document(ticker: str, filename: str, content: str) -> list[dict]:
    """
    Chunk a document and attach metadata to each chunk.
    Metadata is stored alongside the embedding in ChromaDB.
    """
    chunks = chunk_text(content)
    return [
        {
            "text": chunk,
            "ticker": ticker,
            "filename": filename,
            "chunk_index": i,
            "id": f"{ticker}_{filename}_{i}",
        }
        for i, chunk in enumerate(chunks)
    ]