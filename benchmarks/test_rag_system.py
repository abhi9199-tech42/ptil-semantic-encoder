import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from ptil import PTILRAG


def main():
    print("=" * 70)
    print("PTIL RAG - FULL SYSTEM TEST")
    print("=" * 70)
    print()

    # Test 1: Create RAG
    print("Test 1: Create RAG instance")
    rag = PTILRAG()
    print("  OK")
    print()

    # Test 2: Add documents
    print("Test 2: Add documents")
    docs = [
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
    ]
    ids = rag.add_documents(docs)
    print("  Added %d documents" % len(ids))
    print()

    # Test 3: Stats
    print("Test 3: Get stats")
    stats = rag.get_stats()
    print("  Documents: %d" % stats["total_documents"])
    print("  Original: %d bytes" % stats["total_original_bytes"])
    print("  Compressed: %d bytes" % stats["total_compressed_bytes"])
    print("  Reduction: %.1f%%" % stats["reduction_pct"])
    print()

    # Test 4: Search
    print("Test 4: Search")
    queries = [
        "school tomorrow",
        "Paris trip",
        "project deadline",
        "weather weekend",
    ]
    for q in queries:
        results = rag.search(q, top_k=2)
        print('  Query: "%s"' % q)
        for r in results:
            print("    [%.2f] %s" % (r["score"], r["text"][:50]))
        print()

    # Test 5: Search with context
    print("Test 5: Search with context")
    results = rag.search_with_context("school", context_window=1)
    print("  Found %d documents (1 match + context)" % len(results))
    for r in results:
        marker = ">>>" if r["is_match"] else "   "
        print("    %s %s" % (marker, r["text"][:50]))
    print()

    # Test 6: Export/Import
    print("Test 6: Export/Import")
    export_path = "test_rag_index.json"
    rag.export_index(export_path)
    print("  Exported to %s" % export_path)

    rag2 = PTILRAG()
    rag2.import_index(export_path)
    print("  Imported %d documents" % len(rag2.documents))
    print()

    # Test 7: Verify import
    print("Test 7: Verify import")
    results2 = rag2.search("school", top_k=1)
    print("  Search after import: %s" % results2[0]["text"][:50])
    print()

    # Cleanup
    import os
    if os.path.exists(export_path):
        os.remove(export_path)

    print("=" * 70)
    print("ALL TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
