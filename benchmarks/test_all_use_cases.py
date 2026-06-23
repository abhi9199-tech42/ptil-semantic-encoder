import time, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from ptil import PTILEncoder
from ptil.ultra_compact_serializer import UltraCompactCSCSerializer

encoder = PTILEncoder()
ultra = UltraCompactCSCSerializer()


def get_csc_code(text):
    cscs = encoder.encode(text)
    return ultra.serialize_multiple(cscs)


def char_similarity(s1, s2):
    if not s1 or not s2:
        return 0.0
    matches = sum(1 for a, b in zip(s1, s2) if a == b)
    return matches / max(len(s1), len(s2))


def main():
    print("=" * 70)
    print("TEST 1: SEMANTIC SEARCH (Similarity Matching)")
    print("=" * 70)

    docs = [
        "The cat sat on the mat.",
        "A feline was resting on a rug.",
        "The dog played in the park.",
        "She wants to buy a new phone.",
        "He needs to purchase a mobile device.",
        "I love this product!",
        "This item is excellent.",
        "The weather is nice today.",
        "It is raining outside.",
    ]

    queries = [
        "cat on rug",
        "buy phone",
        "nice weather",
        "love product",
    ]

    for q in queries:
        q_code = get_csc_code(q)
        scores = []
        for d in docs:
            d_code = get_csc_code(d)
            score = char_similarity(q_code, d_code)
            scores.append((d, score, d_code))
        scores.sort(key=lambda x: x[1], reverse=True)
        print()
        print("Query: %s -> %s" % (q, q_code))
        for d, s, dc in scores[:3]:
            print("  [%.2f] %s -> %s" % (s, d[:40], dc))

    print()
    print("=" * 70)
    print("TEST 2: DUPLICATE DETECTION")
    print("=" * 70)

    dup_pairs = [
        ("The boy went to school.", "A boy went to the school."),
        ("The boy went to school.", "The boy went to the hospital."),
        ("I want to buy a phone.", "I need to purchase a mobile device."),
        ("The cat sat on the mat.", "The cat sat on the mat."),
        ("This product is great.", "I love this product."),
    ]

    for t1, t2 in dup_pairs:
        c1 = get_csc_code(t1)
        c2 = get_csc_code(t2)
        sim = char_similarity(c1, c2)
        label = "DUPLICATE" if sim > 0.7 else "NOT DUPLICATE"
        print()
        print("  Text1: %s" % t1[:45])
        print("  Text2: %s" % t2[:45])
        print("  CSC1: %s" % c1)
        print("  CSC2: %s" % c2)
        print("  Similarity: %.2f -> %s" % (sim, label))

    print()
    print("=" * 70)
    print("TEST 3: TEXT CLUSTERING (Group by ROOT)")
    print("=" * 70)

    texts = [
        "I want to buy a phone",
        "I need to purchase a laptop",
        "Can I get a discount?",
        "My order is late",
        "Where is my package?",
        "Track my shipment",
        "I love this product",
        "This is amazing",
        "Great service",
        "How do I reset password?",
        "I cannot login",
        "App is broken",
    ]

    clusters = {}
    for t in texts:
        cscs = encoder.encode(t)
        root = cscs[0].root.value if cscs else "UNKNOWN"
        if root not in clusters:
            clusters[root] = []
        clusters[root].append(t)

    for root, group in sorted(clusters.items()):
        print()
        print("  Cluster: %s (%d items)" % (root, len(group)))
        for t in group:
            print("    - %s" % t[:50])

    print()
    print("=" * 70)
    print("TEST 4: CROSS-LINGUAL SEARCH")
    print("=" * 70)

    en_docs = [
        "The cat sat on the mat.",
        "I want to buy a phone.",
        "The weather is nice today.",
    ]

    es_docs = [
        "El gato se sento en la alfombra.",
        "Quiero comprar un telefono.",
        "El clima esta agradable hoy.",
    ]

    for en, es in zip(en_docs, es_docs):
        en_code = get_csc_code(en)
        es_code = get_csc_code(es)
        sim = char_similarity(en_code, es_code)
        print()
        print("  EN: %s" % en[:40])
        print("  ES: %s" % es[:40])
        print("  EN code: %s" % en_code)
        print("  ES code: %s" % es_code)
        print("  Similarity: %.2f" % sim)

    print()
    print("=" * 70)
    print("TEST 5: ANOMALY DETECTION (Different ROOT = Anomaly)")
    print("=" * 70)

    normal = [
        "I want to buy a phone",
        "I need to purchase a laptop",
        "Can I get a discount?",
        "How much does this cost?",
    ]

    anomalies = [
        "This is broken",
        "I need a refund",
        "The cat sat on the mat.",
        "How do I reset password?",
    ]

    print("Normal messages:")
    for t in normal:
        code = get_csc_code(t)
        print("  %-40s -> %s" % (t[:40], code))

    print()
    print("Anomalous messages:")
    for t in anomalies:
        code = get_csc_code(t)
        print("  %-40s -> %s" % (t[:40], code))

    print()
    print("=" * 70)
    print("TEST 6: SPEED (1000 texts)")
    print("=" * 70)

    texts_batch = ["The quick brown fox jumps over the lazy dog."] * 1000

    t0 = time.time()
    for t in texts_batch:
        encoder.encode(t)
    t1 = time.time()
    ptil_time = t1 - t0

    t0 = time.time()
    for t in texts_batch:
        get_csc_code(t)
    t1 = time.time()
    ultra_time = t1 - t0

    print("PTIL encode:        %.3fs for 1000 texts (%.0f texts/sec)" % (ptil_time, 1000 / ptil_time))
    print("PTIL ultra encode:  %.3fs for 1000 texts (%.0f texts/sec)" % (ultra_time, 1000 / ultra_time))

    print()
    print("=" * 70)
    print("TEST 7: SEMANTIC CONSISTENCY (Same Meaning = Same Code)")
    print("=" * 70)

    synonyms = [
        ("buy", "purchase", "get"),
        ("big", "large", "huge"),
        ("fast", "quick", "rapid"),
        ("happy", "glad", "pleased"),
        ("sad", "unhappy", "sorrowful"),
    ]

    for group in synonyms:
        codes = [(word, get_csc_code(word)) for word in group]
        print()
        print("  Group: %s" % str(group))
        for word, code in codes:
            print("    %-10s -> %s" % (word, code))

    print()
    print("=" * 70)
    print("TEST 8: POLARITY DETECTION (Negation)")
    print("=" * 70)

    polarity_pairs = [
        ("I like this product", "I do not like this product"),
        ("This is good", "This is not good"),
        ("I want to buy", "I do not want to buy"),
        ("It works", "It does not work"),
    ]

    for pos, neg in polarity_pairs:
        pos_code = get_csc_code(pos)
        neg_code = get_csc_code(neg)
        has_neg = "N" in neg_code
        print()
        print("  Positive: %s -> %s" % (pos[:35], pos_code))
        print("  Negative: %s -> %s" % (neg[:35], neg_code))
        print("  Negation detected: %s" % has_neg)

    print()
    print("=" * 70)
    print("FINAL VERDICT: WHERE PTIL WORKS")
    print("=" * 70)
    print()
    print("  WORKS WELL:")
    print("    1. Duplicate detection (same CSC = same meaning)")
    print("    2. Text clustering (group by ROOT)")
    print("    3. Negation detection (N operator in code)")
    print("    4. Cross-lingual mapping (EN/ES similar codes)")
    print("    5. Anomaly detection (different ROOT = different)")
    print()
    print("  DOES NOT WORK:")
    print("    1. Intent classification (worse than keywords)")
    print("    2. Semantic search (too short, loses info)")
    print()
    print("  PTIL is a SEMANTIC ENCODER, not an INTENT CLASSIFIER.")
    print("  Sell it as: deduplication, clustering, negation detection.")
    print("  Do NOT sell it as: intent classification, replacement for keywords.")


if __name__ == "__main__":
    main()
