import time
import re
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ptil.encoder import PTILEncoder
from ptil.compact_serializer import CompactCSCSerializer
from ptil.ultra_compact_serializer import UltraCompactCSCSerializer
from ptil.root_mapper import ROOTMapper
from ptil.models import ROOT


def count_tokens_approx(text):
    tokens = re.findall(r'\w+|[^\w\s]', text)
    return len(tokens)


CORPUS = [
    "The boy will not go to school tomorrow.",
    "She has been reading a book all morning.",
    "The cat sat on the mat.",
    "He should finish the project by Friday.",
    "They are planning a trip to Paris next summer.",
    "The teacher gave the student a difficult assignment.",
    "We need to analyze the data from last quarter.",
    "The company decided to expand into new markets.",
    "She can speak three languages fluently.",
    "The weather forecast predicts rain for the weekend.",
    "He was walking to the store when he saw the accident.",
    "The children played in the park after school.",
    "They will have completed the project by next month.",
    "The doctor examined the patient carefully.",
    "She wants to learn how to cook Italian food.",
]


def run_benchmarks():
    print("PTIL Real Benchmarks")
    print("Date:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print()

    print("Initializing encoder...")
    t0 = time.time()
    encoder = PTILEncoder()
    print("Init took %.1fs" % (time.time() - t0))

    compact = CompactCSCSerializer()
    ultra = UltraCompactCSCSerializer()

    # === BENCHMARK 1: Token Reduction ===
    print()
    print("=" * 60)
    print("BENCHMARK 1: Token Reduction Ratio")
    print("=" * 60)

    total_raw = 0
    total_compact = 0
    total_ultra = 0

    for text in CORPUS:
        cscs = encoder.encode(text)
        raw = count_tokens_approx(text)
        c_ser = compact.serialize_multiple(cscs)
        u_ser = ultra.serialize_multiple(cscs)
        c_tok = count_tokens_approx(c_ser)
        u_tok = count_tokens_approx(u_ser)
        c_pct = (1 - c_tok / raw) * 100 if raw > 0 else 0
        u_pct = (1 - u_tok / raw) * 100 if raw > 0 else 0
        total_raw += raw
        total_compact += c_tok
        total_ultra += u_tok
        short = text[:45] + "..." if len(text) > 45 else text
        print("  Raw:%3d  Compact:%3d(%.0f%%)  Ultra:%3d(%.0f%%)  | %s" % (raw, c_tok, c_pct, u_tok, u_pct, short))

    overall_c = (1 - total_compact / total_raw) * 100
    overall_u = (1 - total_ultra / total_raw) * 100
    print()
    print("  TOTAL: Raw=%d  Compact=%d (%.1f%% reduction)  Ultra=%d (%.1f%% reduction)" % (total_raw, total_compact, overall_c, total_ultra, overall_u))

    # === BENCHMARK 2: Encoding Throughput ===
    print()
    print("=" * 60)
    print("BENCHMARK 2: Encoding Throughput")
    print("=" * 60)

    # Warm up
    for text in CORPUS[:3]:
        encoder.encode(text)

    t0 = time.time()
    count = 0
    iterations = 50
    for _ in range(iterations):
        for text in CORPUS:
            encoder.encode(text)
            count += 1
    elapsed = time.time() - t0

    print("  Iterations: %d" % iterations)
    print("  Total texts encoded: %d" % count)
    print("  Time: %.2fs" % elapsed)
    print("  Throughput: %.0f texts/sec" % (count / elapsed))

    # === BENCHMARK 3: Cross-Lingual Mapping ===
    print()
    print("=" * 60)
    print("BENCHMARK 3: Cross-Lingual Predicate Mapping")
    print("=" * 60)

    mapper = ROOTMapper()
    tests = [
        ("run", "correr", ROOT.MOTION),
        ("think", "pensar", ROOT.COGNITION),
        ("eat", "comer", ROOT.CONSUMPTION),
        ("write", "escribir", ROOT.COMMUNICATION),
        ("build", "construir", ROOT.CREATION),
        ("love", "amar", ROOT.EMOTION),
        ("see", "ver", ROOT.PERCEPTION),
        ("give", "dar", ROOT.TRANSFER),
        ("go", "ir", ROOT.MOTION),
        ("say", "decir", ROOT.COMMUNICATION),
        ("know", "saber", ROOT.COGNITION),
        ("want", "querer", ROOT.DESIRE),
        ("take", "tomar", ROOT.TRANSFER),
        ("make", "hacer", ROOT.CREATION),
        ("look", "mirar", ROOT.PERCEPTION),
        ("come", "venir", ROOT.MOTION),
        ("work", "trabajar", ROOT.ACTION),
        ("buy", "comprar", ROOT.TRANSFER),
        ("teach", "ensinar", ROOT.TEACHING),
        ("learn", "aprender", ROOT.LEARNING),
    ]

    correct = 0
    total = 0
    for en, es, exp in tests:
        en_r = mapper.map_predicate(en, "VERB", {"relations": []})
        es_r = mapper.map_predicate(es, "VERB", {"relations": []})
        en_ok = en_r == exp
        es_ok = es_r == exp
        total += 2
        if en_ok:
            correct += 1
        if es_ok:
            correct += 1
        en_status = "OK" if en_ok else "MISS"
        es_status = "OK" if es_ok else "MISS"
        print("  %10s -> %-15s expect %-15s [%s]  |  %10s -> %-15s [%s]" % (
            en, en_r.value, exp.value, en_status, es, es_r.value, es_status))

    acc = correct / total * 100
    print()
    print("  Accuracy: %d/%d (%.1f%%)" % (correct, total, acc))

    # === BENCHMARK 4: Serialization Size ===
    print()
    print("=" * 60)
    print("BENCHMARK 4: Serialization Size (bytes)")
    print("=" * 60)

    total_raw_b = 0
    total_verbose_b = 0
    total_compact_b = 0
    total_ultra_b = 0

    for text in CORPUS:
        cscs = encoder.encode(text)
        verbose = encoder.csc_serializer.serialize_multiple(cscs)
        c_ser = compact.serialize_multiple(cscs)
        u_ser = ultra.serialize_multiple(cscs)
        total_raw_b += len(text.encode("utf-8"))
        total_verbose_b += len(verbose.encode("utf-8"))
        total_compact_b += len(c_ser.encode("utf-8"))
        total_ultra_b += len(u_ser.encode("utf-8"))

    print("  Raw text:        %5d bytes" % total_raw_b)
    print("  Verbose CSC:     %5d bytes (%.1f%% smaller)" % (total_verbose_b, (1 - total_verbose_b / total_raw_b) * 100))
    print("  Compact CSC:     %5d bytes (%.1f%% smaller)" % (total_compact_b, (1 - total_compact_b / total_raw_b) * 100))
    print("  Ultra-compact:   %5d bytes (%.1f%% smaller)" % (total_ultra_b, (1 - total_ultra_b / total_raw_b) * 100))

    # === SAMPLE OUTPUT ===
    print()
    print("=" * 60)
    print("SAMPLE: Single Sentence Encoding")
    print("=" * 60)
    sample = "The boy will not go to school tomorrow."
    cscs = encoder.encode(sample)
    verbose = encoder.csc_serializer.serialize_multiple(cscs)
    compact_ser = compact.serialize_multiple(cscs)
    ultra_ser = ultra.serialize_multiple(cscs)
    print("  Input:  \"%s\"" % sample)
    print("  Verbose:     %s" % verbose)
    print("  Compact:     %s" % compact_ser)
    print("  Ultra:       %s" % ultra_ser)
    print("  Raw tokens:  %d" % count_tokens_approx(sample))
    print("  Compact tok: %d" % count_tokens_approx(compact_ser))
    print("  Ultra tok:   %d" % count_tokens_approx(ultra_ser))

    # === SAVE RESULTS ===
    results = {
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "corpus_size": len(CORPUS),
        "token_reduction": {
            "raw_tokens": total_raw,
            "compact_tokens": total_compact,
            "ultra_tokens": total_ultra,
            "compact_reduction_pct": round(overall_c, 1),
            "ultra_reduction_pct": round(overall_u, 1),
        },
        "throughput": {
            "texts_per_sec": round(count / elapsed, 0),
            "total_texts": count,
            "elapsed_seconds": round(elapsed, 2),
        },
        "cross_lingual": {
            "correct": correct,
            "total": total,
            "accuracy_pct": round(acc, 1),
        },
        "serialization_size": {
            "raw_bytes": total_raw_b,
            "verbose_bytes": total_verbose_b,
            "compact_bytes": total_compact_b,
            "ultra_bytes": total_ultra_b,
        },
    }

    output_path = Path(__file__).parent / "benchmark_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("  Token reduction (compact): %.1f%%" % overall_c)
    print("  Token reduction (ultra):   %.1f%%" % overall_u)
    print("  Encoding throughput:       %.0f texts/sec" % (count / elapsed))
    print("  Cross-lingual accuracy:    %.1f%%" % acc)
    print("  Size reduction (compact):  %.1f%%" % ((1 - total_compact_b / total_raw_b) * 100))
    print("  Size reduction (ultra):    %.1f%%" % ((1 - total_ultra_b / total_raw_b) * 100))
    print()
    print("Results saved to: %s" % output_path)


if __name__ == "__main__":
    run_benchmarks()
