"""
PTIL Claude Proxy Demo - Privacy-safe AI for company data.

This example shows how to use PTIL to compress company data
before sending it to Claude, ensuring:
- 82% fewer tokens (cost savings)
- Data stays on YOUR server (privacy)
- Claude sees semantic tokens, not raw text (compliance)

Setup:
    pip install ptil anthropic
    export ANTHROPIC_API_KEY=sk-ant-...
"""

import os
from ptil import ClaudeProxy, compress_for_claude


def demo_compression():
    """Demo 1: Compress text without calling Claude."""
    print("=" * 60)
    print("DEMO 1: Text Compression")
    print("=" * 60)

    texts = [
        "The company's Q3 revenue was $2.4M, up 15% from last quarter.",
        "Our new product launch increased user engagement by 40%.",
        "The board approved the merger pending regulatory approval.",
        "Customer churn decreased to 2.3% after the new retention program.",
    ]

    for text in texts:
        result = compress_for_claude(text, compression="verbose")
        print(f"\nOriginal:    {result['original']}")
        print(f"Compressed:  {result['compressed']}")
        print(f"Tokens:      {result['raw_tokens']} → {result['compressed_tokens']} ({result['reduction_pct']}% reduction)")


def demo_claude_proxy():
    """Demo 2: Ask Claude with compressed data."""
    print("\n" + "=" * 60)
    print("DEMO 2: Claude Proxy (Privacy-Safe)")
    print("=" * 60)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Skipping Demo 2: Set ANTHROPIC_API_KEY env var to run.")
        return

    proxy = ClaudeProxy(api_key=api_key, compression="verbose")

    # Company data (would be sensitive in production)
    company_data = """
    Q3 2024 Financial Summary:
    - Revenue: $2.4M (up 15% from Q2)
    - Operating costs: $1.8M
    - Net profit: $600K
    - Customer count: 1,247 (up 8%)
    - Churn rate: 2.3% (down from 3.1%)
    """

    questions = [
        "What was the revenue growth?",
        "What is the profit margin?",
        "How many customers do we have?",
    ]

    for question in questions:
        print(f"\nQuestion: {question}")
        print("-" * 40)

        result = proxy.ask(context=company_data, question=question)

        print(f"Answer: {result['answer']}")
        print(f"Tokens sent: {result['tokens_sent']} (was {result['raw_tokens']})")
        print(f"Savings: {result['estimated_cost_savings']}")


def demo_batch_processing():
    """Demo 3: Process multiple data chunks."""
    print("\n" + "=" * 60)
    print("DEMO 3: Batch Processing")
    print("=" * 60)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Skipping Demo 3: Set ANTHROPIC_API_KEY env var to run.")
        return

    proxy = ClaudeProxy(api_key=api_key, compression="verbose")

    items = [
        {
            "context": "Employee count: 45 (up from 38 last quarter)",
            "question": "How many employees do we have?",
        },
        {
            "context": "Server uptime: 99.97% (3.6 minutes downtime)",
            "question": "What is the uptime percentage?",
        },
    ]

    results = proxy.batch_ask(items)

    for item, result in zip(items, results):
        print(f"\nQ: {item['question']}")
        print(f"A: {result['answer']}")
        print(f"   Tokens: {result['tokens_sent']} ({result['estimated_cost_savings']} savings)")


def demo_streaming():
    """Demo 4: Stream Claude's response."""
    print("\n" + "=" * 60)
    print("DEMO 4: Streaming Response")
    print("=" * 60)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Skipping Demo 4: Set ANTHROPIC_API_KEY env var to run.")
        return

    from ptil import safe_claude_stream

    context = "Project Alpha: 85% complete, on track for December launch, budget $120K of $150K used."

    print("Streaming answer...\n")
    for chunk in safe_claude_stream(
        api_key=api_key,
        context=context,
        question="Give me a project status summary.",
    ):
        print(chunk, end="", flush=True)
    print()


def demo_middleware():
    """Demo 5: Simple one-liner middleware."""
    print("\n" + "=" * 60)
    print("DEMO 5: One-Liner Middleware")
    print("=" * 60)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Skipping Demo 5: Set ANTHROPIC_API_KEY env var to run.")
        return

    from ptil import safe_claude

    answer = safe_claude(
        api_key=api_key,
        context="User 12345 logged in from New York at 3:45 PM EST",
        question="Where did the user log in from?",
    )

    print(f"Answer: {answer}")


if __name__ == "__main__":
    print("PTIL Claude Proxy - Privacy-Safe AI Demo")
    print("=" * 60)

    demo_compression()
    demo_claude_proxy()
    demo_batch_processing()
    demo_streaming()
    demo_middleware()

    print("\n" + "=" * 60)
    print("All demos complete!")
    print("=" * 60)
