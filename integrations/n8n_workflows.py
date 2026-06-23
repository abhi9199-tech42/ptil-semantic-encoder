"""
PTIL n8n Workflow Templates

These are the HTTP Request node configurations for n8n.
Import them into n8n or configure manually.
"""

# ─────────────────────────────────────────────
# Workflow 1: Compress Text on Webhook
# ─────────────────────────────────────────────
# Trigger: Webhook (POST /compress)
# Action: HTTP Request to PTIL
# Response: Compressed text

WORKFLOW_COMPRESS = {
    "name": "PTIL Compress Text",
    "nodes": [
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "compress",
                "responseMode": "responseNode",
            },
            "name": "Webhook",
            "type": "n8n-nodes-base.webhook",
            "position": [250, 300],
        },
        {
            "parameters": {
                "method": "POST",
                "url": "http://ptil:8000/encode",
                "sendBody": True,
                "bodyParameters": {
                    "parameters": [
                        {"name": "text", "value": "={{$json.body.text}}"},
                        {"name": "format", "value": "ultra"},
                    ]
                },
                "options": {},
            },
            "name": "PTIL Compress",
            "type": "n8n-nodes-base.httpRequest",
            "position": [500, 300],
        },
        {
            "parameters": {
                "respondWith": "json",
                "responseBody": "={{$json}}",
            },
            "name": "Respond",
            "type": "n8n-nodes-base.respondToWebhook",
            "position": [750, 300],
        },
    ],
    "connections": {
        "Webhook": {"main": [[{"node": "PTIL Compress", "type": "main", "index": 0}]]},
        "PTIL Compress": {"main": [[{"node": "Respond", "type": "main", "index": 0}]]},
    },
}


# ─────────────────────────────────────────────
# Workflow 2: Classify Intent
# ─────────────────────────────────────────────
# Trigger: Webhook (POST /classify)
# Action: HTTP Request to PTIL /intent
# Response: Intent classification

WORKFLOW_CLASSIFY = {
    "name": "PTIL Classify Intent",
    "nodes": [
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "classify",
                "responseMode": "responseNode",
            },
            "name": "Webhook",
            "type": "n8n-nodes-base.webhook",
            "position": [250, 300],
        },
        {
            "parameters": {
                "method": "POST",
                "url": "http://ptil:8000/intent",
                "sendBody": True,
                "bodyParameters": {
                    "parameters": [
                        {"name": "text", "value": "={{$json.body.text}}"},
                    ]
                },
                "options": {},
            },
            "name": "PTIL Classify",
            "type": "n8n-nodes-base.httpRequest",
            "position": [500, 300],
        },
        {
            "parameters": {
                "respondWith": "json",
                "responseBody": "={{$json}}",
            },
            "name": "Respond",
            "type": "n8n-nodes-base.respondToWebhook",
            "position": [750, 300],
        },
    ],
    "connections": {
        "Webhook": {"main": [[{"node": "PTIL Classify", "type": "main", "index": 0}]]},
        "PTIL Classify": {"main": [[{"node": "Respond", "type": "main", "index": 0}]]},
    },
}


# ─────────────────────────────────────────────
# Workflow 3: Compress → Store → Search Loop
# ─────────────────────────────────────────────
# Trigger: Webhook (POST /memory)
# Actions: Store compressed, search when queried

WORKFLOW_MEMORY = {
    "name": "PTIL Agent Memory",
    "nodes": [
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "memory",
                "responseMode": "responseNode",
            },
            "name": "Webhook",
            "type": "n8n-nodes-base.webhook",
            "position": [250, 300],
        },
        {
            "parameters": {
                "conditions": {
                    "string": [
                        {"value1": "={{$json.body.action}}", "value2": "store"}
                    ]
                },
            },
            "name": "Is Store?",
            "type": "n8n-nodes-base.if",
            "position": [500, 300],
        },
        {
            "parameters": {
                "command": "ptil rag add --text '={{$json.body.text}}'",
            },
            "name": "Store in PTIL",
            "type": "n8n-nodes-base.executeCommand",
            "position": [750, 200],
        },
        {
            "parameters": {
                "command": "ptil rag search --query '={{$json.body.text}}'",
            },
            "name": "Search PTIL",
            "type": "n8n-nodes-base.executeCommand",
            "position": [750, 400],
        },
        {
            "parameters": {
                "respondWith": "json",
                "responseBody": "={{$json.stdout}}",
            },
            "name": "Respond",
            "type": "n8n-nodes-base.respondToWebhook",
            "position": [1000, 300],
        },
    ],
}


# ─────────────────────────────────────────────
# Quick Setup Commands
# ─────────────────────────────────────────────
SETUP = """
# Start PTIL + n8n together:
docker compose up -d

# n8n will be at: http://localhost:5678
# PTIL will be at: http://localhost:8000

# In n8n, create a new workflow and add HTTP Request nodes:
#   URL: http://ptil:8000/encode
#   Method: POST
#   Body: {"text": "your text", "format": "ultra"}

# Or use the CLI directly in Execute Command nodes:
#   ptil encode "your text"
#   ptil rag search --query "your query"
"""
