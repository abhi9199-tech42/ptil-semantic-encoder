"""
PTIL Claude Middleware - Drop-in replacement for Claude API calls.

The simplest way to add privacy-safe AI to your app.
Just wrap your Claude calls with PTIL compression.

Usage:
    from ptil.claude_middleware import safe_claude

    # Instead of calling Claude directly:
    # response = claude.messages.create(...)

    # Use safe_claude:
    answer = safe_claude(
        api_key="sk-ant-...",
        context="Your company data here",
        question="What does this data show?"
    )
"""

import os
from typing import Optional, Dict, Any


def safe_claude(
    api_key: Optional[str] = None,
    context: str = "",
    question: str = "",
    model: str = "claude-sonnet-4-20250514",
    compression: str = "verbose",
    max_tokens: int = 1024,
    temperature: float = 0.0,
) -> str:
    """
    One-liner to ask Claude with compressed data.
    
    Company data is compressed before sending.
    Claude never sees raw text.
    
    Args:
        api_key: Anthropic API key (or ANTHROPIC_API_KEY env var)
        context: Company data to compress
        question: Question about the data
        model: Claude model
        compression: "verbose", "compact", or "ultra"
        max_tokens: Max response tokens
        temperature: Response temperature
        
    Returns:
        Claude's answer as a string
        
    Example:
        answer = safe_claude(
            context="Q3 revenue was $2.4M, up 15%",
            question="What is the revenue trend?"
        )
        print(answer)  # "Revenue grew 15% from the previous quarter."
    """
    from .claude_proxy import ClaudeProxy
    
    if api_key is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "API key required. Pass api_key= or set ANTHROPIC_API_KEY env var."
            )
    
    proxy = ClaudeProxy(
        api_key=api_key,
        model=model,
        compression=compression,
    )
    
    result = proxy.ask(
        context=context,
        question=question,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    
    return result["answer"]


def safe_claude_stream(
    api_key: Optional[str] = None,
    context: str = "",
    question: str = "",
    model: str = "claude-sonnet-4-20250514",
    compression: str = "verbose",
    max_tokens: int = 1024,
    temperature: float = 0.0,
):
    """
    Stream Claude's response with compressed data.
    
    Yields chunks of the response as they arrive.
    """
    from .claude_proxy import ClaudeProxy
    
    if api_key is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "API key required. Pass api_key= or set ANTHROPIC_API_KEY env var."
            )
    
    proxy = ClaudeProxy(
        api_key=api_key,
        model=model,
        compression=compression,
    )
    
    yield from proxy.ask_stream(
        context=context,
        question=question,
        max_tokens=max_tokens,
        temperature=temperature,
    )


def compress_for_claude(
    text: str,
    compression: str = "verbose",
    spacy_model: str = "en_core_web_sm",
) -> Dict[str, Any]:
    """
    Compress text for Claude without making an API call.
    
    Useful for:
    - Pre-processing data before sending
    - Estimating token savings
    - Debugging compression
    
    Args:
        text: Text to compress
        compression: "verbose", "compact", or "ultra"
        spacy_model: spaCy model name
        
    Returns:
        Dict with compressed text and stats
    """
    from .encoder import PTILEncoder
    from .csc_serializer import CSCSerializer
    from .compact_serializer import CompactCSCSerializer
    from .ultra_compact_serializer import UltraCompactCSCSerializer
    
    encoder = PTILEncoder(model_name=spacy_model)
    
    if compression == "ultra":
        serializer = UltraCompactCSCSerializer()
    elif compression == "compact":
        serializer = CompactCSCSerializer()
    else:
        serializer = CSCSerializer()
    
    cscs = encoder.encode(text)
    compressed = serializer.serialize_multiple(cscs) if cscs else text
    
    raw_tokens = len(text.split())
    comp_tokens = len(compressed.split())
    
    return {
        "original": text,
        "compressed": compressed,
        "raw_tokens": raw_tokens,
        "compressed_tokens": comp_tokens,
        "reduction_pct": round(
            (1 - comp_tokens / raw_tokens) * 100, 1
        ) if raw_tokens > 0 else 0,
    }
