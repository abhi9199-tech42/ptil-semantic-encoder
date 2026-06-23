import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from ptil.encoder import PTILEncoder
from ptil.compact_serializer import CompactCSCSerializer
from ptil.ultra_compact_serializer import UltraCompactCSCSerializer
from ptil.models import ROOT, Operator, Role

encoder = PTILEncoder()
compact = CompactCSCSerializer()
ultra = UltraCompactCSCSerializer()

SENTENCES = [
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

print("=" * 70)
print("MEANING PRESERVATION CHECK")
print("=" * 70)
print()
print("Comparing what each format encodes:")
print()

for text in SENTENCES:
    cscs = encoder.encode(text)
    verbose = encoder.csc_serializer.serialize_multiple(cscs)
    c_ser = compact.serialize_multiple(cscs)
    u_ser = ultra.serialize_multiple(cscs)

    print("INPUT: %s" % text)
    print("  Verbose: %s" % verbose)
    print("  Compact: %s" % c_ser)
    print("  Ultra:   %s" % u_ser)

    # Parse what ultra-compact encodes
    if cscs:
        csc = cscs[0]
        print("  --- Ultra-compact breakdown ---")
        print("    ROOT:    %s (single char)" % ultra.root_codes.get(csc.root, "?"))
        if csc.ops:
            ops_str = "".join(ultra.operator_codes.get(op, "?") for op in csc.ops)
            print("    OPS:     %s -> %s" % (ops_str, " | ".join(op.value for op in csc.ops)))
        if csc.roles:
            for role, entity in sorted(csc.roles.items(), key=lambda x: x[0].value):
                code = ultra.role_codes.get(role, "?")
                compressed = ultra._ultra_compress_entity(entity.normalized)
                print("    ROLE:    %s%s = %s:%s (compressed: %s)" % (
                    code, compressed, role.value, entity.text, entity.normalized))
        if csc.meta:
            meta_code = ultra.meta_codes.get(csc.meta, "?")
            print("    META:    %s = %s" % (meta_code if meta_code else "(empty=assertive)", csc.meta.value))
    print()

# Check if meaning is lost
print("=" * 70)
print("MEANING LOSS ANALYSIS")
print("=" * 70)
print()
print("What ultra-compact LOSES:")
print("  1. Articles (the, a, an) -> intentionally removed (redundant)")
print("  2. Prepositions (to, in, on) -> captured in ROLE codes")
print("  3. Auxiliary verbs (will, has, been) -> captured in OPS codes")
print("  4. Entity text -> compressed to 1-2 chars")
print()
print("What ultra-compact PRESERVES:")
print("  1. ROOT (core meaning: motion, cognition, emotion, etc.)")
print("  2. Operators (tense, negation, modality)")
print("  3. Semantic roles (agent, patient, goal, location)")
print("  4. Meta-attitude (question, command, uncertainty)")
print()
print("What ultra-compact LOSES (problematic):")
print("  1. Specific entity names (Paris -> 'p', boy -> 'b')")
print("  2. Quantity information (three languages -> 'l')")
print("  3. Adjective modifiers (difficult -> 'd')")
print("  4. Multi-word entities (Southeast Asian -> 's')")
print("  5. Contextual nuance that doesnt fit into ROOT/OPS/ROLES")
print()
print("VERDICT:")
print("  Ultra-compact preserves STRUCTURAL meaning (who did what to whom)")
print("  but loses SURFACE meaning (specific names, quantities, modifiers).")
print("  This is a TRADE-OFF, not a loss-free compression.")
