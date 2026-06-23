"""
PTIL + Open WebUI Integration

Add PTIL as a tool function in Open WebUI.
"""

# ─────────────────────────────────────────────
# Open WebUI Tool Function
# ─────────────────────────────────────────────
# In Open WebUI:
#   1. Go to Workspace > Tools > Create Tool
#   2. Name: PTIL Compress
#   3. Paste the function below
#   4. Save and enable

TOOL_FUNCTION = '''
def ptil_compress(text: str) -> str:
    """Compress text to 20% of original size while keeping it readable.

    Args:
        text: The text to compress

    Returns:
        Compressed text (80% smaller)
    """
    from ptil import PTILEncoder
    from ptil.ultra_compact_serializer import UltraCompactCSCSerializer

    encoder = PTILEncoder()
    serializer = UltraCompactCSCSerializer()
    cscs = encoder.encode(text)
    return serializer.serialize_multiple(cscs)


def ptil_store(text: str) -> str:
    """Store text in compressed agent memory.

    Args:
        text: Text to remember

    Returns:
        Confirmation with compression stats
    """
    from ptil.rag import PTILRAG

    rag = PTILRAG()
    try:
        rag.import_index("openwebui_memory.json")
    except FileNotFoundError:
        pass

    rag.add_document(text)
    rag.export_index("openwebui_memory.json")
    stats = rag.get_stats()
    return f"Remembered. {stats['total_documents']} items, {stats['reduction_pct']:.1f}% compressed."


def ptil_recall(query: str) -> str:
    """Search compressed memory for information.

    Args:
        query: What to search for

    Returns:
        Matching memories with relevance scores
    """
    from ptil.rag import PTILRAG

    rag = PTILRAG()
    try:
        rag.import_index("openwebui_memory.json")
    except FileNotFoundError:
        return "No memories stored yet."

    results = rag.search(query, top_k=5)
    if not results:
        return "No matching memories found."

    return "\\n".join(f"[{r['score']:.2f}] {r['text']}" for r in results)
'''

# ─────────────────────────────────────────────
# Alternative: HTTP API Tool
# ─────────────────────────────────────────────
# If running PTIL as a server (docker compose up):
# In Open WebUI, use the "HTTP" tool type:
#   URL: http://ptil:8000/encode
#   Method: POST
#   Headers: Content-Type: application/json
#   Body: {"text": "{{input}}", "format": "ultra"}
