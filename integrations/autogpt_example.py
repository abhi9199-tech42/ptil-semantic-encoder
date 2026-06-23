"""
PTIL + AutoGPT / OpenAGI Integration

Provides compressed memory for autonomous agents.
"""

from autogpt_core.agent import Agent
from autogpt_core.tool import Tool


# ─────────────────────────────────────────────
# PTIL Tools for AutoGPT
# ─────────────────────────────────────────────

def compress_text(text: str) -> str:
    """Compress text to 20% of original size."""
    from ptil import PTILEncoder
    from ptil.ultra_compact_serializer import UltraCompactCSCSerializer

    encoder = PTILEncoder()
    serializer = UltraCompactCSCSerializer()
    cscs = encoder.encode(text)
    return serializer.serialize_multiple(cscs)


def search_memory(query: str) -> str:
    """Search compressed agent memory."""
    from ptil.rag import PTILRAG

    rag = PTILRAG()
    try:
        rag.import_index("agent_memory.json")
    except FileNotFoundError:
        return "No memory stored."

    results = rag.search(query, top_k=3)
    if not results:
        return "No results."

    return "\n".join(f"[{r['score']:.2f}] {r['text']}" for r in results)


def store_memory(text: str) -> str:
    """Store text in compressed agent memory (80% smaller)."""
    from ptil.rag import PTILRAG

    rag = PTILRAG()
    try:
        rag.import_index("agent_memory.json")
    except FileNotFoundError:
        pass

    rag.add_document(text)
    rag.export_index("agent_memory.json")
    stats = rag.get_stats()
    return f"Stored. {stats['total_documents']} docs, {stats['reduction_pct']:.1f}% compression."


# ─────────────────────────────────────────────
# AutoGPT Agent Setup
# ─────────────────────────────────────────────

def create_agent():
    tools = [
        Tool("compress_text", compress_text, "Compress text to 20% size"),
        Tool("search_memory", search_memory, "Search compressed memory"),
        Tool("store_memory", store_memory, "Store in compressed memory"),
    ]

    agent = Agent(
        name="PTIL Agent",
        description="An agent with compressed memory using PTIL.",
        tools=tools,
        memory_enabled=True,
    )

    return agent


if __name__ == "__main__":
    agent = create_agent()
    # AutoGPT handles the execution loop
    # Agent will use store_memory and search_memory automatically
    pass
