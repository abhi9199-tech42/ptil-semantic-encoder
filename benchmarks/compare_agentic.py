import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from ptil import PTILEncoder, PTILRAG
from ptil.ultra_compact_serializer import UltraCompactCSCSerializer

encoder = PTILEncoder()
ultra = UltraCompactCSCSerializer()

print("=" * 80)
print("PTIL vs EXISTING AGENTIC PRODUCTS")
print("=" * 80)
print()

AGENT_MESSAGES = [
    "I need to book a flight to Paris for next summer",
    "Search for flights from New York to Paris",
    "Found 3 options: $500, $600, $700",
    "User selected the $500 option",
    "Booking confirmed for July 15th",
    "Now I need to find a hotel in Paris",
    "Search for hotels near Eiffel Tower",
    "Found 5 hotels ranging from $100 to $300 per night",
    "User selected Hotel Paris for $150 per night",
    "Hotel booking confirmed",
    "Now I need to book a restaurant",
    "User wants French cuisine near the hotel",
    "Found 3 restaurants",
    "User selected Le Petit Bistro",
    "Restaurant reservation confirmed for July 16th",
    "All bookings complete",
    "Total cost: $500 flight + $150 hotel + $80 restaurant = $730",
    "Trip to Paris is fully planned",
]

print("AGENT MESSAGES (%d messages)" % len(AGENT_MESSAGES))
print("-" * 80)
for i, msg in enumerate(AGENT_MESSAGES):
    print("  %2d. %s" % (i + 1, msg[:60]))
print()

# METHOD 1: Raw storage
print("=" * 80)
print("METHOD 1: RAW STORAGE (ChatGPT, Claude, LangChain)")
print("=" * 80)
raw_total = sum(len(m.split()) for m in AGENT_MESSAGES)
print("  Tokens stored: %d" % raw_total)
print("  Searchable: Yes (keyword)")
print("  Readable: Yes")
print()

# METHOD 2: Vector embeddings
print("=" * 80)
print("METHOD 2: VECTOR EMBEDDINGS (Pinecone, Weaviate, Zep)")
print("=" * 80)
vector_tokens = len(AGENT_MESSAGES) * 1536
print("  Tokens stored: %d (1536-dim vectors)" % vector_tokens)
print("  Searchable: Yes (similarity)")
print("  Readable: No (vectors)")
print()

# METHOD 3: MemGPT
print("=" * 80)
print("METHOD 3: MEMGPT (LLM-based compression)")
print("=" * 80)
memgpt_tokens = int(raw_total * 0.3)
print("  Tokens stored: %d (30%% of raw, LLM summarized)" % memgpt_tokens)
print("  Searchable: Yes (keyword)")
print("  Readable: Yes")
print("  Cost: LLM API calls for each compression")
print()

# METHOD 4: PTIL
print("=" * 80)
print("METHOD 4: PTIL (Semantic compression)")
print("=" * 80)
ptil_codes = []
for msg in AGENT_MESSAGES:
    cscs = encoder.encode(msg)
    code = ultra.serialize_multiple(cscs)
    ptil_codes.append(code)

ptil_tokens = sum(len(c.split()) for c in ptil_codes)
print("  Tokens stored: %d" % ptil_tokens)
print("  Searchable: Yes (ROOT matching)")
print("  Readable: Yes (semantic codes)")
print("  Cost: Zero (local processing)")
print()

print("  PTIL Codes:")
for msg, code in zip(AGENT_MESSAGES, ptil_codes):
    print("    %-55s -> %s" % (msg[:55], code))
print()

# COMPARISON
print("=" * 80)
print("COMPARISON")
print("=" * 80)
print()
print("  Method              Tokens    Reduction   Searchable   Readable   Cost")
print("  " + "-" * 75)
print("  Raw (ChatGPT)       %5d     baseline    Yes          Yes        Free" % raw_total)
print("  Vector (Pinecone)   %5d     %.0f%%        Yes          No         $$$$" % (
    vector_tokens, (1 - vector_tokens / raw_total) * 100))
print("  MemGPT              %5d     %.0f%%        Yes          Yes        $$$" % (
    memgpt_tokens, (1 - memgpt_tokens / raw_total) * 100))
print("  PTIL                %5d     %.0f%%        Yes          Yes        Free" % (
    ptil_tokens, (1 - ptil_tokens / raw_total) * 100))
print()

# RAG TEST
print("=" * 80)
print("RAG TEST: Search agent memory")
print("=" * 80)
print()

rag = PTILRAG()
for msg in AGENT_MESSAGES:
    rag.add_document(msg)

queries = [
    "Paris flight",
    "hotel booking",
    "restaurant",
    "total cost",
]

for q in queries:
    results = rag.search(q, top_k=2)
    print('  Query: "%s"' % q)
    for r in results:
        print("    [%.2f] %s" % (r["score"], r["text"][:50]))
    print()

stats = rag.get_stats()
print("  RAG Stats:")
print("    Documents: %d" % stats["total_documents"])
print("    Original: %d bytes" % stats["total_original_bytes"])
print("    Compressed: %d bytes" % stats["total_compressed_bytes"])
print("    Reduction: %.1f%%" % stats["reduction_pct"])
