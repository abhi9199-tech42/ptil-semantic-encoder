import time, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from ptil import PTILEncoder
from ptil.ultra_compact_serializer import UltraCompactCSCSerializer

TRAIN_DATA = [
    ("I want to buy a phone", "sales"),
    ("Can I purchase this?", "sales"),
    ("How much does it cost?", "sales"),
    ("Do you have discounts?", "sales"),
    ("I need a refund", "support"),
    ("This is broken", "support"),
    ("Can you help me?", "support"),
    ("I need assistance", "support"),
    ("Where is my order?", "logistics"),
    ("Track my package", "logistics"),
    ("When will it arrive?", "logistics"),
    ("My shipment is late", "logistics"),
    ("I love this product", "feedback"),
    ("This is amazing", "feedback"),
    ("Great service", "feedback"),
    ("Excellent quality", "feedback"),
    ("I want to speak to manager", "escalation"),
    ("This is unacceptable", "escalation"),
    ("I will complain", "escalation"),
    ("How do I reset password?", "tech"),
    ("I cannot login", "tech"),
    ("App keeps crashing", "tech"),
    ("Account is locked", "tech"),
    ("Do you have this in blue?", "product"),
    ("What sizes available?", "product"),
    ("Is this in stock?", "product"),
    ("What colors do you have?", "product"),
    ("What is your return policy?", "faq"),
    ("How do I return this?", "faq"),
    ("What are your hours?", "faq"),
    ("Do you ship internationally?", "faq"),
]

TEST_DATA = [
    ("I want to buy a new phone", "sales"),
    ("My order is late", "logistics"),
    ("I need a refund for this", "support"),
    ("Can you help me with my order?", "support"),
    ("This product is great", "feedback"),
    ("Where is my package?", "logistics"),
    ("I want to speak to a manager", "escalation"),
    ("How do I reset my password?", "tech"),
    ("Do you have this in blue?", "product"),
    ("I love your service", "feedback"),
    ("This is broken", "support"),
    ("Can I get a discount?", "sales"),
    ("Track my order", "logistics"),
    ("I need support", "support"),
    ("What is your return policy?", "faq"),
    ("I want to purchase a laptop", "sales"),
    ("My package is damaged", "support"),
    ("How much is this?", "sales"),
    ("Can I change my order?", "support"),
    ("Where is the nearest store?", "logistics"),
]

KEYWORDS = {
    "buy": "sales", "purchase": "sales", "cost": "sales", "price": "sales", "discount": "sales", "cheap": "sales",
    "refund": "support", "broken": "support", "help": "support", "support": "support", "problem": "support", "assist": "support",
    "late": "logistics", "package": "logistics", "track": "logistics", "shipping": "logistics", "delivery": "logistics", "order": "logistics",
    "great": "feedback", "love": "feedback", "excellent": "feedback", "amazing": "feedback", "good": "feedback",
    "manager": "escalation", "supervisor": "escalation", "complaint": "escalation", "unacceptable": "escalation",
    "password": "tech", "login": "tech", "reset": "tech", "account": "tech", "crash": "tech",
    "blue": "product", "color": "product", "size": "product", "available": "product", "stock": "product",
    "return": "faq", "policy": "faq", "hours": "faq", "ship": "faq",
}

RULES = [
    (r"buy|purchase|discount|price|cost|cheap", "sales"),
    (r"refund|broken|fix|repair|assist|help|support", "support"),
    (r"late|package|track|shipping|delivery|order", "logistics"),
    (r"great|love|excellent|amazing|good|happy", "feedback"),
    (r"manager|supervisor|complaint|unacceptable|escalat", "escalation"),
    (r"password|login|reset|account|crash|lock", "tech"),
    (r"blue|color|size|available|stock", "product"),
    (r"return|policy|hours|ship|international", "faq"),
]

ROOT_TO_DEPT = {
    "DESIRE": "sales", "JOY": "feedback", "ANGER": "escalation",
    "DESTRUCTION": "support", "MOTION": "logistics", "TRANSFER": "support",
    "POSSESSION": "product", "MEMORY": "tech", "COGNITION": "faq",
    "COMMUNICATION": "faq", "EXISTENCE": "logistics", "REQUEST": "support",
    "COOPERATION": "escalation", "EVALUATION": "feedback", "FAILURE": "support",
    "SUCCESS": "feedback", "ACTION": "general", "CHANGE": "support",
    "CREATION": "sales", "STATE": "general", "PROPERTY": "product",
    "QUANTITY": "sales", "TIME_RELATION": "logistics",
}


def keyword_classify(text):
    text_lower = text.lower()
    for keyword, dept in KEYWORDS.items():
        if keyword in text_lower:
            return dept
    return "general"


def regex_classify(text):
    for pattern, dept in RULES:
        if re.search(pattern, text.lower()):
            return dept
    return "general"


def ptil_classify(text):
    cscs = encoder.encode(text)
    root = cscs[0].root.value if cscs else "UNKNOWN"
    return ROOT_TO_DEPT.get(root, "general")


def ptil_classify_confident(text, threshold=0.8):
    cscs = encoder.encode(text)
    if not cscs:
        return "general"
    csc = cscs[0]
    root = csc.root.value
    dept = ROOT_TO_DEPT.get(root, "general")
    confidence = 0.9 if len(csc.ops) >= 1 else 0.6
    if confidence < threshold:
        return "general"
    return dept


def hybrid_classify(text):
    kw_result = keyword_classify(text)
    if kw_result != "general":
        return kw_result
    return ptil_classify(text)


def main():
    global encoder
    encoder = PTILEncoder()

    methods = [
        ("Keywords", keyword_classify),
        ("Regex", regex_classify),
        ("PTIL", ptil_classify),
        ("PTIL+Confidence", ptil_classify_confident),
        ("Hybrid (PTIL+KW)", hybrid_classify),
    ]

    print("=" * 80)
    print("COMPREHENSIVE COMPARISON: 5 METHODS")
    print("=" * 80)
    print()

    results_summary = []

    for method_name, classify_fn in methods:
        correct = 0
        total = 0
        t0 = time.time()
        for text, expected in TEST_DATA:
            result = classify_fn(text)
            ok = result == expected
            if ok:
                correct += 1
            total += 1
        elapsed = time.time() - t0
        acc = correct / total * 100
        results_summary.append((method_name, correct, total, acc, elapsed))
        print("%s: %d/%d (%.1f%%) in %.3fs" % (method_name, correct, total, acc, elapsed))

    print()
    print("=" * 80)
    print("DETAILED BREAKDOWN: ALL METHODS ON EVERY TEST CASE")
    print("=" * 80)
    print()
    print("  %-42s Expected     KW       Regex    PTIL     Hybrid" % "Input")
    print("  " + "-" * 95)

    for text, expected in TEST_DATA:
        kw = keyword_classify(text)
        rg = regex_classify(text)
        pt = ptil_classify(text)
        hy = hybrid_classify(text)
        kw_mark = "+" if kw == expected else "x"
        rg_mark = "+" if rg == expected else "x"
        pt_mark = "+" if pt == expected else "x"
        hy_mark = "+" if hy == expected else "x"
        print("  %-42s %-12s %-8s %-8s %-8s %-8s" % (
            text[:42], expected, kw_mark, rg_mark, pt_mark, hy_mark))

    print()
    print("=" * 80)
    print("ERROR ANALYSIS: WHERE EACH METHOD FAILS")
    print("=" * 80)
    print()

    for method_name, classify_fn in methods:
        fails = []
        for text, expected in TEST_DATA:
            result = classify_fn(text)
            if result != expected:
                fails.append((text, expected, result))
        if fails:
            print("%s fails on %d cases:" % (method_name, len(fails)))
            for text, expected, result in fails:
                print("  -> \"%s\"" % text[:50])
                print("     Expected: %s, Got: %s" % (expected, result))
            print()

    print("=" * 80)
    print("WHEN PTIL BEATS KEYWORDS")
    print("=" * 80)
    print()

    ptil_wins = 0
    kw_wins = 0
    for text, expected in TEST_DATA:
        kw = keyword_classify(text)
        pt = ptil_classify(text)
        if pt == expected and kw != expected:
            ptil_wins += 1
            print("  PTIL wins:  \"%s\" -> %s (expected %s)" % (text[:45], pt, expected))
        elif kw == expected and pt != expected:
            kw_wins += 1
            print("  KW wins:    \"%s\" -> %s (expected %s)" % (text[:45], kw, expected))

    print()
    print("  PTIL wins: %d times" % ptil_wins)
    print("  Keywords win: %d times" % kw_wins)

    print()
    print("=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print()
    print("  %-20s %8s %8s %10s" % ("Method", "Accuracy", "Speed", "Verdict"))
    print("  " + "-" * 50)
    for name, correct, total, acc, elapsed in results_summary:
        verdict = "BEST" if acc >= 80 else ("OK" if acc >= 60 else "BAD")
        print("  %-20s %6.0f%% %8.3fs %10s" % (name, acc, elapsed, verdict))


if __name__ == "__main__":
    main()
