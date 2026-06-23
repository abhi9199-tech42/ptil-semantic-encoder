"""
PTIL + Dify Integration

Two approaches:
1. HTTP Request tool (no code needed in Dify)
2. Custom tool via Dify's Tool Provider
"""

# ─────────────────────────────────────────────
# APPROACH 1: Use in Dify Workflow (HTTP Node)
# ─────────────────────────────────────────────
# Step 1: Start PTIL server
#   ptil serve --host 0.0.0.0 --port 8000
#
# Step 2: In Dify, add an HTTP Request node:
#   Method: POST
#   URL: http://ptil:8000/encode  (if using docker-compose)
#        http://localhost:8000/encode (if running locally)
#   Headers: Content-Type: application/json
#   Body: {"text": "{{user_input}}", "format": "ultra"}
#
# Step 3: Use the response in your workflow
#   The response contains: text, csc, format, language

# ─────────────────────────────────────────────
# APPROACH 2: Dify Custom Tool Provider
# ─────────────────────────────────────────────
# Create a file called ptil_tool.py for Dify's tool system:

import requests


class PTILTool:
    """Dify-compatible PTIL tool provider."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def compress(self, text: str) -> dict:
        """Compress text using PTIL."""
        resp = requests.post(
            f"{self.base_url}/encode",
            json={"text": text, "format": "ultra"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def classify_intent(self, text: str) -> dict:
        """Classify intent of text."""
        resp = requests.post(
            f"{self.base_url}/intent",
            json={"text": text},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def classify_batch(self, texts: list) -> dict:
        """Classify intent of multiple texts."""
        resp = requests.post(
            f"{self.base_url}/intent/batch",
            json={"texts": texts},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def health(self) -> dict:
        """Check if PTIL server is running."""
        resp = requests.get(f"{self.base_url}/health", timeout=5)
        resp.raise_for_status()
        return resp.json()


# Dify Tool Provider manifest (ptil_manifest.json):
"""
{
  "api_base": "http://localhost:8000",
  "tools": [
    {
      "name": "ptil_compress",
      "label": "PTIL Compress",
      "description": "Compress text to 20% of original size",
      "parameters": [
        {
          "name": "text",
          "type": "string",
          "required": true,
          "label": "Text to compress"
        }
      ]
    },
    {
      "name": "ptil_classify",
      "label": "PTIL Intent",
      "description": "Classify intent and extract meaning from text",
      "parameters": [
        {
          "name": "text",
          "type": "string",
          "required": true,
          "label": "Text to classify"
        }
      ]
    }
  ]
}
"""
