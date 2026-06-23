"""
PTIL CLI — encode text, search, RAG, server, benchmark.
"""
import sys
import argparse
import json
from typing import List, Optional

from .encoder import PTILEncoder
from .config import PTILConfig
from .models import ROOT, Operator, Role, META


def cmd_encode(args: argparse.Namespace):
    config = PTILConfig(
        language=args.language,
        serialization_format=args.format,
        spaCy_model=args.model,
        unknown_predicate_strategy=args.unknown_strategy,
    )
    enc = PTILEncoder(config=config)
    result = enc.encode_and_serialize(args.text, format=args.format)
    if args.pretty:
        cscs = enc.encode(args.text)
        for i, csc in enumerate(cscs):
            print("CSC #%d:" % (i + 1))
            print("  ROOT:  %s" % csc.root.name)
            print("  OPS:   %s" % [o.name for o in csc.ops])
            roles_str = ", ".join("%s=%s" % (r.name, e.normalized) for r, e in csc.roles.items())
            print("  ROLES: {%s}" % roles_str)
            print("  META:  %s" % (csc.meta.name if csc.meta else "None"))
            print("  RAW:   %s" % result)
    else:
        print(result)


def cmd_encode_file(args: argparse.Namespace):
    config = PTILConfig(
        language=args.language,
        serialization_format=args.format,
        spaCy_model=args.model,
    )
    enc = PTILEncoder(config=config)

    with open(args.file, encoding="utf-8") as f:
        texts = [line.strip() for line in f if line.strip()]

    results = enc.encode_and_serialize_batch(texts, format=args.format)
    out = args.output
    if out:
        with open(out, "w", encoding="utf-8") as f:
            for line in results:
                f.write(line + "\n")
        print("Wrote %d results to %s" % (len(results), out))
    else:
        for text, csc in zip(texts, results):
            print("%s\t%s" % (text, csc))


def cmd_rag(args: argparse.Namespace):
    from .rag import PTILRAG

    if args.action == "create":
        rag = PTILRAG()
        rag.export_index(args.index)
        print("Created index: %s" % args.index)

    elif args.action == "add":
        rag = PTILRAG()
        try:
            rag.import_index(args.index)
        except FileNotFoundError:
            pass
        rag.add_document(args.text)
        rag.export_index(args.index)
        print("Added document to %s" % args.index)

    elif args.action == "add-file":
        rag = PTILRAG()
        try:
            rag.import_index(args.index)
        except FileNotFoundError:
            pass
        with open(args.file, encoding="utf-8") as f:
            texts = [line.strip() for line in f if line.strip()]
        rag.add_documents(texts)
        rag.export_index(args.index)
        print("Added %d documents to %s" % (len(texts), args.index))

    elif args.action == "search":
        rag = PTILRAG()
        rag.import_index(args.index)
        results = rag.search(args.query, top_k=args.top_k)
        for r in results:
            print("[%.2f] %s" % (r["score"], r["text"]))

    elif args.action == "stats":
        rag = PTILRAG()
        rag.import_index(args.index)
        stats = rag.get_stats()
        print("Documents: %d" % stats["total_documents"])
        print("Original: %d bytes" % stats["total_original_bytes"])
        print("Compressed: %d bytes" % stats["total_compressed_bytes"])
        print("Reduction: %.1f%%" % stats["reduction_pct"])


def cmd_serve(args: argparse.Namespace):
    try:
        from .server.app import run_server
    except ImportError:
        print("Error: install server dependencies: pip install ptil[server]", file=sys.stderr)
        sys.exit(1)

    config = PTILConfig(
        language=args.language,
        serialization_format=args.format,
        spaCy_model=args.model,
        enable_metrics=True,
        metrics_port=args.port,
    )
    run_server(config=config, host=args.host, port=args.port)


def cmd_benchmark(args: argparse.Namespace):
    import time

    config = PTILConfig(
        language=args.language,
        spaCy_model=args.model,
    )
    enc = PTILEncoder(config=config)

    if args.input:
        with open(args.input, encoding="utf-8") as f:
            texts = [line.strip() for line in f if line.strip()]
    else:
        texts = [
            "The boy runs home.",
            "She will not go to school tomorrow.",
            "The scientist carefully analyzed the data.",
            "They have been working on the project all day.",
            "I eat food and drink water.",
        ]

    total_start = time.perf_counter()
    total_tokens = 0
    total_cscs = 0

    for text in texts:
        start = time.perf_counter()
        cscs = enc.encode(text)
        elapsed = time.perf_counter() - start
        total_tokens += len(text.split())
        total_cscs += len(cscs)
        print("%6.1fms  %d CSC(s)  '%s'" % (elapsed * 1000, len(cscs), text[:50]))

    total_elapsed = time.perf_counter() - total_start
    print()
    print("---")
    print("Total: %d texts, %d tokens, %d CSCs" % (len(texts), total_tokens, total_cscs))
    print("Time:  %.0fms (%.0fms avg)" % (total_elapsed * 1000, total_elapsed / len(texts) * 1000))
    print("Rate:  %.0f tokens/sec" % (total_tokens / total_elapsed))


def cmd_cache(args: argparse.Namespace):
    from .encoder import PTILEncoder
    config = PTILConfig(spaCy_model=args.model, language=args.language)
    enc = PTILEncoder(config=config)

    if args.action == "stats":
        stats = enc.get_cache_stats()
        print("Cache entries: %d" % stats["size"])
    elif args.action == "clear":
        enc.clear_cache()
        print("Cache cleared")


def main():
    parser = argparse.ArgumentParser(prog="ptil", description="PTIL - 80% text compression that stays searchable")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    sub = parser.add_subparsers(dest="command")

    # encode
    p_encode = sub.add_parser("encode", help="Encode a single text")
    p_encode.add_argument("text", help="Text to encode")
    p_encode.add_argument("--format", choices=["verbose", "compact", "ultra"], default="ultra")
    p_encode.add_argument("--language", default="en")
    p_encode.add_argument("--model", default="en_core_web_sm")
    p_encode.add_argument("--unknown-strategy", default="vector_fallback")
    p_encode.add_argument("--pretty", action="store_true", help="Show detailed CSC breakdown")
    p_encode.set_defaults(func=cmd_encode)

    # encode-file
    pf = sub.add_parser("encode-file", help="Encode lines from a file")
    pf.add_argument("file", help="Input file path")
    pf.add_argument("--output", "-o", help="Output file path (default: stdout)")
    pf.add_argument("--format", choices=["verbose", "compact", "ultra"], default="ultra")
    pf.add_argument("--language", default="en")
    pf.add_argument("--model", default="en_core_web_sm")
    pf.set_defaults(func=cmd_encode_file)

    # rag
    p_rag = sub.add_parser("rag", help="RAG system - store and search documents")
    p_rag.add_argument("action", choices=["create", "add", "add-file", "search", "stats"])
    p_rag.add_argument("--index", default="ptil_index.json", help="Index file path")
    p_rag.add_argument("--text", help="Text to add (for 'add' action)")
    p_rag.add_argument("--file", help="File with texts (for 'add-file' action)")
    p_rag.add_argument("--query", help="Search query (for 'search' action)")
    p_rag.add_argument("--top-k", type=int, default=5, help="Number of results")
    p_rag.set_defaults(func=cmd_rag)

    # serve
    p_serve = sub.add_parser("serve", help="Start REST API server")
    p_serve.add_argument("--host", default="0.0.0.0")
    p_serve.add_argument("--port", type=int, default=8000)
    p_serve.add_argument("--format", choices=["verbose", "compact", "ultra"], default="ultra")
    p_serve.add_argument("--language", default="en")
    p_serve.add_argument("--model", default="en_core_web_sm")
    p_serve.set_defaults(func=cmd_serve)

    # benchmark
    p_bench = sub.add_parser("benchmark", help="Run performance benchmark")
    p_bench.add_argument("--input", help="Input file (one sentence per line, optional)")
    p_bench.add_argument("--language", default="en")
    p_bench.add_argument("--model", default="en_core_web_sm")
    p_bench.set_defaults(func=cmd_benchmark)

    # cache
    p_cache = sub.add_parser("cache", help="Manage encode cache")
    p_cache.add_argument("action", choices=["stats", "clear"])
    p_cache.add_argument("--language", default="en")
    p_cache.add_argument("--model", default="en_core_web_sm")
    p_cache.set_defaults(func=cmd_cache)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
