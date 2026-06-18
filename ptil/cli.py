"""
PTIL CLI — encode text, run server, benchmark.
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
            print(f"CSC #{i + 1}:")
            print(f"  ROOT:  {csc.root.name}")
            print(f"  OPS:   {[o.name for o in csc.ops]}")
            roles_str = ", ".join(f"{r.name}={e.normalized}" for r, e in csc.roles.items())
            print(f"  ROLES: {{{roles_str}}}")
            print(f"  META:  {csc.meta.name if csc.meta else 'None'}")
            print(f"  RAW:   {result}")
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
        print(f"Wrote {len(results)} results to {out}")
    else:
        for text, csc in zip(texts, results):
            print(f"{text}\t{csc}")


def cmd_serve(args: argparse.Namespace):
    try:
        from .server.app import run_server
    except ImportError:
        print("Error: install server dependencies: pip install ptil-semantic-encoder[server]", file=sys.stderr)
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
        print(f"{elapsed * 1000:6.1f}ms  {len(cscs)} CSC(s)  '{text[:50]}'")

    total_elapsed = time.perf_counter() - total_start
    print(f"\n---")
    print(f"Total: {len(texts)} texts, {total_tokens} tokens, {total_cscs} CSCs")
    print(f"Time:  {total_elapsed * 1000:.0f}ms ({total_elapsed / len(texts) * 1000:.0f}ms avg)")
    print(f"Rate:  {total_tokens / total_elapsed:.0f} tokens/sec")


def cmd_cache(args: argparse.Namespace):
    from .encoder import PTILEncoder
    config = PTILConfig(spaCy_model=args.model, language=args.language)
    enc = PTILEncoder(config=config)

    if args.action == "stats":
        stats = enc.get_cache_stats()
        print(f"Cache entries: {stats['size']}")
    elif args.action == "clear":
        enc.clear_cache()
        print("Cache cleared")


def main():
    parser = argparse.ArgumentParser(prog="ptil", description="PTIL Semantic Encoder CLI")
    parser.add_argument("--version", action="version", version="%(prog)s 0.4.0")

    sub = parser.add_subparsers(dest="command")

    # encode
    p_encode = sub.add_parser("encode", help="Encode a single text")
    p_encode.add_argument("text", help="Text to encode")
    p_encode.add_argument("--format", choices=["verbose", "compact", "ultra"], default="verbose")
    p_encode.add_argument("--language", default="en")
    p_encode.add_argument("--model", default="en_core_web_sm")
    p_encode.add_argument("--unknown-strategy", default="vector_fallback")
    p_encode.add_argument("--pretty", action="store_true", help="Show detailed CSC breakdown")
    p_encode.set_defaults(func=cmd_encode)

    # encode-file
    pf = sub.add_parser("encode-file", help="Encode lines from a file")
    pf.add_argument("file", help="Input file path")
    pf.add_argument("--output", "-o", help="Output file path (default: stdout)")
    pf.add_argument("--format", choices=["verbose", "compact", "ultra"], default="verbose")
    pf.add_argument("--language", default="en")
    pf.add_argument("--model", default="en_core_web_sm")
    pf.set_defaults(func=cmd_encode_file)

    # serve
    p_serve = sub.add_parser("serve", help="Start REST API server")
    p_serve.add_argument("--host", default="0.0.0.0")
    p_serve.add_argument("--port", type=int, default=8000)
    p_serve.add_argument("--format", choices=["verbose", "compact", "ultra"], default="verbose")
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
