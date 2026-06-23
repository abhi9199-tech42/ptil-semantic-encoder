"""
PTIL + Flowise Integration

Use PTIL as a custom tool in Flowise chatflows.
"""

# ─────────────────────────────────────────────
# Flowise Custom Tool Setup
# ─────────────────────────────────────────────
# Option A: Use HTTP Request Tool node in Flowise
#   Method: POST
#   URL: http://localhost:8000/encode
#   Body: {"text": "{{input}}", "format": "ultra"}
#
# Option B: Create a custom Flowise tool (see below)

import requests
from pydantic import BaseModel, Field


class PTILCompressInput(BaseModel):
    text: str = Field(description="Text to compress")


class PTILSearchInput(BaseModel):
    query: str = Field(description="Search query")
    index_path: str = Field(default="flowise_memory.json", description="Path to index file")


def ptil_compress_flowise(text: str) -> str:
    """Compress text to 20% of original size."""
    from ptil import PTILEncoder
    from ptil.ultra_compact_serializer import UltraCompactCSCSerializer

    encoder = PTILEncoder()
    serializer = UltraCompactCSCSerializer()
    cscs = encoder.encode(text)
    return serializer.serialize_multiple(cscs)


def ptil_search_flowise(query: str, index_path: str = "flowise_memory.json") -> str:
    """Search compressed documents."""
    from ptil.rag import PTILRAG

    rag = PTILRAG()
    try:
        rag.import_index(index_path)
    except FileNotFoundError:
        return "No documents stored yet."

    results = rag.search(query, top_k=3)
    if not results:
        return "No results found."

    return "\n".join(f"[{r['score']:.2f}] {r['text']}" for r in results)


def ptil_store_flowise(text: str, index_path: str = "flowise_memory.json") -> str:
    """Store text in compressed memory."""
    from ptil.rag import PTILRAG

    rag = PTILRAG()
    try:
        rag.import_index(index_path)
    except FileNotFoundError:
        pass

    rag.add_document(text)
    rag.export_index(index_path)
    stats = rag.get_stats()
    return f"Stored. {stats['total_documents']} docs, {stats['reduction_pct']:.1f}% compression."


# ─────────────────────────────────────────────
# Register as Flowise Custom Tool
# ─────────────────────────────────────────────
# In Flowise, go to:
#   Settings > Tools > Add Custom Tool
#
# Name: PTIL Compress
# Description: Compress text to 20% of original size
# Script:
#   (paste the ptil_compress_flowise function above)
#
# Then use it in your chatflow as a tool node.
