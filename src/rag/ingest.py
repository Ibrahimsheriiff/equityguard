"""
Ingest — memory-efficient version.
Processes one file at a time and uses the smallest available model.
"""

import os
import gc
import chromadb
from sentence_transformers import SentenceTransformer
from src.rag.chunking import chunk_document

DOCS_PATH   = "data/company_docs"
CHROMA_PATH = "data/chroma_db"
COLLECTION  = "company_docs"
EMBED_MODEL = "paraphrase-MiniLM-L3-v2"  # Smallest model — ~17MB vs 90MB


def build_vector_store():
    print("Loading embedding model...")
    model = SentenceTransformer(EMBED_MODEL)

    print("Connecting to ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION)

    if not os.path.exists(DOCS_PATH):
        print(f"No documents found at {DOCS_PATH}")
        return

    files = [f for f in os.listdir(DOCS_PATH) if f.endswith(".txt")]
    print(f"Found {len(files)} files\n")

    total_chunks = 0

    # Process ONE file at a time to keep memory low
    for filename in files:
        filepath = os.path.join(DOCS_PATH, filename)
        with open(filepath, "r") as f:
            content = f.read()

        ticker = filename.split("_")[0].upper()
        chunks = chunk_document(ticker, filename, content)

        if not chunks:
            continue

        texts      = [c["text"] for c in chunks]
        embeddings = model.encode(texts, batch_size=4, show_progress_bar=False).tolist()

        collection.add(
            ids        = [c["id"] for c in chunks],
            embeddings = embeddings,
            documents  = texts,
            metadatas  = [
                {"ticker": c["ticker"], "filename": c["filename"], "chunk_index": c["chunk_index"]}
                for c in chunks
            ],
        )

        total_chunks += len(chunks)
        print(f"  ✓ {filename} — {len(chunks)} chunks")

        # Free memory after each file
        gc.collect()

    print(f"\nDone. {total_chunks} chunks stored in ChromaDB at {CHROMA_PATH}")


if __name__ == "__main__":
    build_vector_store()