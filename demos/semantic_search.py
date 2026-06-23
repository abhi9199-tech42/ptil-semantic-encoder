"""
Semantic Search Demo
Find documents with similar meaning using CSC codes.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ptil import PTILEncoder
from ptil.ultra_compact_serializer import UltraCompactCSCSerializer


def compute_similarity(csc1_str, csc2_str):
    if csc1_str == csc2_str:
        return 1.0
    if not csc1_str or not csc2_str:
        return 0.0

    min_len = min(len(csc1_str), len(csc2_str))
    if min_len == 0:
        return 0.0

    matches = sum(1 for a, b in zip(csc1_str, csc2_str) if a == b)
    return matches / max(len(csc1_str), len(csc2_str))


def search(query, documents, encoder, ultra, top_k=3):
    query_cscs = encoder.encode(query)
    query_ultra = ultra.serialize_multiple(query_cscs)

    scored = []
    for doc in documents:
        doc_cscs = encoder.encode(doc)
        doc_ultra = ultra.serialize_multiple(doc_cscs)
        sim = compute_similarity(query_ultra, doc_ultra)
        scored.append((doc, sim, doc_ultra))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def main():
    encoder = PTILEncoder()
    ultra = UltraCompactCSCSerializer()

    documents = [
        "The cat sat on the mat.",
        "A feline was resting on a rug.",
        "The dog played in the park.",
        "She wants to buy a new phone.",
        "He needs to purchase a mobile device.",
        "The weather is nice today.",
        "It is raining outside.",
        "I love this product!",
        "This item is excellent.",
        "Can you help me with my homework?",
        "I need assistance with my assignment.",
        "The boy went to school.",
        "A child walked to the classroom.",
    ]

    queries = [
        "cat on rug",
        "buy phone",
        "nice weather",
        "help homework",
        "child at school",
    ]

    print("=" * 70)
    print("SEMANTIC SEARCH DEMO")
    print("=" * 70)
    print()
    print("Documents indexed: %d" % len(documents))
    print()

    for query in queries:
        results = search(query, documents, encoder, ultra)
        print("Query: \"%s\"" % query)
        for doc, score, ultra_code in results:
            marker = ">>>" if score > 0.5 else "   "
            print("  %s [%.2f] %s" % (marker, score, doc[:50]))
        print()


if __name__ == "__main__":
    main()
