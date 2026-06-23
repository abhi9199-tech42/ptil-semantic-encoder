"""
PTIL + LangChain Integration

Two approaches:
1. Direct Python tool (no server needed)
2. HTTP tool via PTIL REST API server
"""

# ─────────────────────────────────────────────
# APPROACH 1: Direct Python Tool (Recommended)
# ─────────────────────────────────────────────
# No server needed — PTIL runs in-process.

from langchain_core.tools import tool


@tool
def ptil_compress(text: str) -> str:
    """Compress text to 20% of its original size while keeping it readable.

    Args:
        text: The text to compress (e.g. chat messages, logs, documents).

    Returns:
        Compressed representation that is 80% smaller.
    """
    from ptil import PTILEncoder
    from ptil.ultra_compact_serializer import UltraCompactCSCSerializer

    encoder = PTILEncoder()
    serializer = UltraCompactCSCSerializer()
    cscs = encoder.encode(text)
    return serializer.serialize_multiple(cscs)


@tool
def ptil_search(index_path: str, query: str) -> str:
    """Search compressed documents without decompressing.

    Args:
        index_path: Path to the PTIL index JSON file.
        query: What to search for.

    Returns:
        Matching documents with relevance scores.
    """
    import json
    from ptil.rag import PTILRAG

    rag = PTILRAG()
    rag.import_index(index_path)
    results = rag.search(query, top_k=5)

    if not results:
        return "No results found."

    lines = []
    for r in results:
        lines.append(f"[{r['score']:.2f}] {r['text']}")
    return "\n".join(lines)


@tool
def ptil_add_to_memory(index_path: str, text: str) -> str:
    """Store text in compressed agent memory (80% smaller).

    Args:
        index_path: Path to the PTIL index JSON file.
        text: Text to store (e.g. conversation message, observation).

    Returns:
        Confirmation with compression stats.
    """
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
# USAGE WITH LANGCHAIN AGENT
# ─────────────────────────────────────────────

def create_ptil_agent():
    """Create a LangChain agent with PTIL memory tools."""
    from langchain_openai import ChatOpenAI
    from langchain.agents import create_tool_calling_agent, AgentExecutor
    from langchain_core.prompts import ChatPromptTemplate

    llm = ChatOpenAI(model="gpt-4o")
    tools = [ptil_compress, ptil_search, ptil_add_to_memory]

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful agent with compressed memory. "
                   "Use ptil_add_to_memory to store important information. "
                   "Use ptil_search to recall stored information."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


if __name__ == "__main__":
    agent = create_ptil_agent()

    # Store some memories
    agent.invoke({"input": "Store this: The user prefers dark mode and works in UTC-5 timezone."})
    agent.invoke({"input": "Store this: The user's project deadline is March 15, 2026."})

    # Recall memories
    agent.invoke({"input": "What timezone does the user work in?"})


# ─────────────────────────────────────────────
# APPROACH 2: HTTP Tool (Server Required)
# ─────────────────────────────────────────────
# Start server first: ptil serve --port 8000

import requests


@tool
def ptil_encode_http(text: str) -> str:
    """Compress text using PTIL server (requires ptil serve --port 8000).

    Args:
        text: The text to compress.

    Returns:
        Compressed text.
    """
    resp = requests.post(
        "http://localhost:8000/encode",
        json={"text": text, "format": "ultra"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["csc"]


@tool
def ptil_intent_http(text: str) -> str:
    """Classify intent of text using PTIL server.

    Args:
        text: The text to classify.

    Returns:
        JSON with intent, confidence, root, and compressed form.
    """
    resp = requests.post(
        "http://localhost:8000/intent",
        json={"text": text},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    return (
        f"Intent: {data['intent']}\n"
        f"Confidence: {data['confidence']}\n"
        f"Root: {data['root']}\n"
        f"Compressed: {data['ultra_compact']}"
    )
