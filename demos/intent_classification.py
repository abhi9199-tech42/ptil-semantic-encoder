"""
Intent Classification Demo
Routes customer messages to the right department.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ptil import PTILEncoder


def classify_intent(text, encoder):
    cscs = encoder.encode(text)
    if not cscs:
        return {"intent": "unknown", "department": "general"}

    csc = cscs[0]
    root = csc.root.value

    intent_map = {
        "DESIRE": "sales",
        "JOY": "feedback",
        "ANGER": "complaint",
        "FEAR": "support",
        "DESTRUCTION": "support",
        "MOTION": "logistics",
        "TRANSFER": "billing",
        "POSSESSION": "product",
        "MEMORY": "tech_support",
        "COGNITION": "information",
        "COMMUNICATION": "general",
        "EXISTENCE": "general",
        "CREATION": "feature_request",
        "COOPERATION": "escalation",
        "REQUEST": "support",
        "EVALUATION": "feedback",
        "SUCCESS": "feedback",
        "FAILURE": "support",
    }

    department = intent_map.get(root, "general")
    confidence = 0.9 if csc.ops else 0.7

    return {
        "intent": root,
        "department": department,
        "confidence": confidence,
        "ops": [op.value for op in csc.ops],
    }


def main():
    encoder = PTILEncoder()

    messages = [
        "I want to buy a new phone",
        "My order hasn't arrived yet",
        "I'm very happy with your product!",
        "This is terrible, I want a refund",
        "How do I reset my password?",
        "Can you track my package?",
        "I need to speak to a manager",
        "Do you have this in blue?",
        "The app keeps crashing",
        "I love your customer service!",
    ]

    print("=" * 70)
    print("INTENT CLASSIFICATION DEMO")
    print("=" * 70)
    print()

    for msg in messages:
        result = classify_intent(msg, encoder)
        print("Message: \"%s\"" % msg)
        print("  Intent:      %s" % result["intent"])
        print("  Department:  %s" % result["department"])
        print("  Confidence:  %.1f%%" % (result["confidence"] * 100))
        print("  Operators:   %s" % result["ops"])
        print()

    print("=" * 70)
    print("ROUTING SUMMARY")
    print("=" * 70)

    departments = {}
    for msg in messages:
        result = classify_intent(msg, encoder)
        dept = result["department"]
        if dept not in departments:
            departments[dept] = []
        departments[dept].append(msg)

    for dept, msgs in sorted(departments.items()):
        print("\n  %s (%d messages):" % (dept.upper(), len(msgs)))
        for msg in msgs:
            print("    - %s" % msg[:50])


if __name__ == "__main__":
    main()
