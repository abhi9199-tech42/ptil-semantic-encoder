"""
Chatbot Router Demo
Route messages to handlers based on semantic meaning.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ptil import PTILEncoder


ROOT_TO_HANDLER = {
    "DESIRE": "sales_team",
    "JOY": "feedback_system",
    "ANGER": "escalation_manager",
    "FEAR": "support_agent",
    "DESTRUCTION": "support_ticket",
    "MOTION": "logistics_api",
    "TRANSFER": "billing_system",
    "POSSESSION": "product_catalog",
    "MEMORY": "password_reset",
    "COGNITION": "knowledge_base",
    "COMMUNICATION": "general_reply",
    "EXISTENCE": "status_check",
    "CREATION": "feature_request_queue",
    "COOPERATION": "human_agent",
    "REQUEST": "support_ticket",
    "EVALUATION": "review_system",
    "SUCCESS": "positive_feedback",
    "FAILURE": "error_handler",
    "LEARNING": "tutorial_bot",
    "TEACHING": "onboarding_flow",
}

ROOT_TO_PRIORITY = {
    "ANGER": "high",
    "DESTRUCTION": "high",
    "FEAR": "high",
    "FAILURE": "high",
    "DESIRE": "medium",
    "REQUEST": "medium",
    "COOPERATION": "high",
    "JOY": "low",
    "EXISTENCE": "low",
    "COMMUNICATION": "low",
}


def route_message(text, encoder):
    cscs = encoder.encode(text)
    if not cscs:
        return {
            "handler": "general_reply",
            "priority": "low",
            "root": "UNKNOWN",
            "suggested_response": "I'm not sure how to help with that.",
        }

    csc = cscs[0]
    root = csc.root.value

    handler = ROOT_TO_HANDLER.get(root, "general_reply")
    priority = ROOT_TO_PRIORITY.get(root, "low")

    responses = {
        "DESIRE": "Let me connect you with our sales team!",
        "ANGER": "I understand your frustration. Let me escalate this immediately.",
        "DESTRUCTION": "I'm sorry to hear that. Let me create a support ticket.",
        "FEAR": "Don't worry, I'll help you resolve this.",
        "JOY": "Great to hear! Thank you for your feedback.",
        "MEMORY": "Let me help you reset your password.",
        "POSSESSION": "Here's what we have available:",
        "REQUEST": "I'll look into that for you.",
        "COOPERATION": "Let me transfer you to a human agent.",
        "FAILURE": "I see the issue. Let me troubleshoot this.",
    }

    return {
        "handler": handler,
        "priority": priority,
        "root": root,
        "ops": [op.value for op in csc.ops],
        "suggested_response": responses.get(root, "How can I help you?"),
    }


def main():
    encoder = PTILEncoder()

    messages = [
        "I want to buy 3 phones",
        "This product is broken!",
        "I'm so happy with your service!",
        "I can't log into my account",
        "Where is my order?",
        "I want to speak to a manager",
        "How does this work?",
        "I need a refund",
        "Can you help me?",
        "This is the best product ever!",
    ]

    print("=" * 70)
    print("CHATBOT ROUTER DEMO")
    print("=" * 70)
    print()

    for msg in messages:
        result = route_message(msg, encoder)
        print("Message: \"%s\"" % msg)
        print("  Handler:     %s" % result["handler"])
        print("  Priority:    %s" % result["priority"])
        print("  Root:        %s" % result["root"])
        print("  Response:    %s" % result["suggested_response"])
        print()

    print("=" * 70)
    print("HANDLER DISTRIBUTION")
    print("=" * 70)

    handler_counts = {}
    for msg in messages:
        result = route_message(msg, encoder)
        handler = result["handler"]
        handler_counts[handler] = handler_counts.get(handler, 0) + 1

    for handler, count in sorted(handler_counts.items(), key=lambda x: -x[1]):
        print("  %-25s %d messages" % (handler, count))


if __name__ == "__main__":
    main()
