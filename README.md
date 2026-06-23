# PTIL — Pre-Tokenization Intelligence Layer

**80% text compression that stays searchable. Store 10x more. Search without decompressing.**

## What It Does

PTIL compresses text to 20% of its original size while keeping it searchable:

```
Input:  "The boy will not go to school tomorrow."
Stored: 1FNWaboygschomtmrw  (80% smaller, readable)
```

Search for "school" → finds the original text without decompressing.

## Quick Start

```bash
pip install ptil
python -m spacy download en_core_web_sm
```

```python
from ptil import PTILRAG

# Create RAG system
rag = PTILRAG()

# Add documents (compressed 80%)
rag.add_document("The boy went to school.")
rag.add_document("She read a book all morning.")
rag.add_document("They are planning a trip to Paris.")

# Search (returns original text)
results = rag.search("school")
print(results[0]["text"])  # "The boy went to school."
```

## Setup for AI Agents

PTIL works with any agent framework. Use it as a Python library (in-process) or as a REST API server.

### Docker (Recommended)

```bash
docker compose up -d
```

This starts PTIL (port 8000) + n8n (port 5678). Edit `docker-compose.yml` to change ports or add services.

### Standalone Server

```bash
pip install ptil[server]
python -m spacy download en_core_web_sm
ptil serve --host 0.0.0.0 --port 8000
```

API docs at `http://localhost:8000/docs`.

---

### n8n

**Option A: HTTP Request Node**

1. Start PTIL: `docker compose up -d` or `ptil serve --port 8000`
2. In n8n, add an **HTTP Request** node:
   - Method: `POST`
   - URL: `http://ptil:8000/encode` (Docker) or `http://localhost:8000/encode` (local)
   - Body Content Type: JSON
   - Body: `{"text": "={{$json.input}}", "format": "ultra"}`
3. Use the response `csc` field in downstream nodes.

**Option B: Execute Command Node**

Use the CLI directly in n8n Execute Command nodes:

```
ptil encode "user message here"
ptil rag search --query "user question" --index memory.json
ptil rag add --text "store this" --index memory.json
```

**Option C: Import Workflow**

See `integrations/n8n_workflows.py` for ready-to-import workflow JSON.

---

### LangChain

**Direct Python (no server):**

```python
from langchain_core.tools import tool
from ptil import PTILEncoder
from ptil.ultra_compact_serializer import UltraCompactCSCSerializer
from ptil.rag import PTILRAG

@tool
def ptil_compress(text: str) -> str:
    """Compress text to 20% of original size."""
    encoder = PTILEncoder()
    serializer = UltraCompactCSCSerializer()
    cscs = encoder.encode(text)
    return serializer.serialize_multiple(cscs)

@tool
def ptil_store_memory(text: str) -> str:
    """Store text in compressed agent memory."""
    rag = PTILRAG()
    try:
        rag.import_index("memory.json")
    except FileNotFoundError:
        pass
    rag.add_document(text)
    rag.export_index("memory.json")
    return f"Stored. {rag.get_stats()['reduction_pct']:.1f}% compression."

@tool
def ptil_search_memory(query: str) -> str:
    """Search compressed memory."""
    rag = PTILRAG()
    try:
        rag.import_index("memory.json")
    except FileNotFoundError:
        return "No memories stored."
    results = rag.search(query, top_k=3)
    return "\n".join(f"[{r['score']:.2f}] {r['text']}" for r in results)
```

**HTTP Tool (server required):**

```python
import requests

@tool
def ptil_encode_http(text: str) -> str:
    """Compress text via PTIL server."""
    resp = requests.post("http://localhost:8000/encode",
                         json={"text": text, "format": "ultra"})
    return resp.json()["csc"]
```

Full example: `integrations/langchain_example.py`

---

### CrewAI

```python
from crewai import Agent, Tool

@Tool("compress_text")
def compress_text(text: str) -> str:
    """Compress text to 20% of original size."""
    from ptil import PTILEncoder
    from ptil.ultra_compact_serializer import UltraCompactCSCSerializer
    encoder = PTILEncoder()
    serializer = UltraCompactCSCSerializer()
    return serializer.serialize_multiple(encoder.encode(text))

@Tool("store_memory")
def store_memory(text: str) -> str:
    """Store in compressed memory."""
    from ptil.rag import PTILRAG
    rag = PTILRAG()
    try:
        rag.import_index("crew_memory.json")
    except FileNotFoundError:
        pass
    rag.add_document(text)
    rag.export_index("crew_memory.json")
    return f"Stored. {rag.get_stats()['reduction_pct']:.1f}% compression."

@Tool("search_memory")
def search_memory(query: str) -> str:
    """Search compressed memory."""
    from ptil.rag import PTILRAG
    rag = PTILRAG()
    try:
        rag.import_index("crew_memory.json")
    except FileNotFoundError:
        return "No memory stored."
    results = rag.search(query, top_k=3)
    return "\n".join(f"[{r['score']:.2f}] {r['text']}" for r in results)

researcher = Agent(
    role="Researcher",
    goal="Find and store information",
    tools=[compress_text, store_memory, search_memory],
)
```

Full example: `integrations/crewai_example.py`

---

### AutoGPT

```python
from ptil.rag import PTILRAG
from ptil import PTILEncoder
from ptil.ultra_compact_serializer import UltraCompactCSCSerializer

def store_memory(text: str) -> str:
    """Store text in compressed agent memory (80% smaller)."""
    rag = PTILRAG()
    try:
        rag.import_index("agent_memory.json")
    except FileNotFoundError:
        pass
    rag.add_document(text)
    rag.export_index("agent_memory.json")
    stats = rag.get_stats()
    return f"Stored. {stats['total_documents']} docs, {stats['reduction_pct']:.1f}% compression."

def search_memory(query: str) -> str:
    """Search compressed agent memory."""
    rag = PTILRAG()
    try:
        rag.import_index("agent_memory.json")
    except FileNotFoundError:
        return "No memory stored."
    results = rag.search(query, top_k=3)
    return "\n".join(f"[{r['score']:.2f}] {r['text']}" for r in results)
```

Full example: `integrations/autogpt_example.py`

---

### Dify

**HTTP Request Node:**
- Method: `POST`
- URL: `http://ptil:8000/encode`
- Body: `{"text": "{{user_input}}", "format": "ultra"}`

**Custom Tool:** See `integrations/dify_example.py` for the tool provider manifest and wrapper class.

---

### Flowise

**HTTP Request Tool:**
- Method: `POST`
- URL: `http://ptil:8000/encode`
- Body: `{"text": "{{input}}", "format": "ultra"}`

**Custom Tool:** See `integrations/flowise_example.py` for tool functions you can register directly in Flowise.

---

### Open WebUI

1. Go to **Workspace > Tools > Create Tool**
2. Name: `PTIL Compress`
3. Paste the function from `integrations/openwebui_example.py`
4. Enable the tool in your chat

Tools available: `ptil_compress`, `ptil_store`, `ptil_recall`

---

### Any Framework (Generic HTTP)

PTIL exposes a standard REST API. Any framework that can make HTTP requests can use it:

```bash
# Compress
curl -X POST http://localhost:8000/encode \
  -H "Content-Type: application/json" \
  -d '{"text": "your text", "format": "ultra"}'

# Classify intent
curl -X POST http://localhost:8000/intent \
  -H "Content-Type: application/json" \
  -d '{"text": "I want to buy a phone"}'

# Health check
curl http://localhost:8000/health
```

### Integration Files

| File | Framework |
|------|-----------|
| `integrations/langchain_example.py` | LangChain (direct + HTTP) |
| `integrations/crewai_example.py` | CrewAI |
| `integrations/autogpt_example.py` | AutoGPT |
| `integrations/dify_example.py` | Dify |
| `integrations/flowise_example.py` | Flowise |
| `integrations/openwebui_example.py` | Open WebUI |
| `integrations/n8n_workflows.py` | n8n workflows |

---

## RAG System

Store documents compressed 80%. Search them without decompressing. Return original text.

```python
from ptil import PTILRAG

rag = PTILRAG()

# Add documents
documents = [
    "The boy will not go to school tomorrow.",
    "She has been reading a book all morning.",
    "They are planning a trip to Paris next summer.",
]
rag.add_documents(documents)

# Get stats
stats = rag.get_stats()
print(f"Documents: {stats['total_documents']}")
print(f"Compression: {stats['reduction_pct']:.1f}%")

# Search
results = rag.search("Paris trip", top_k=3)
for r in results:
    print(f"[{r['score']:.2f}] {r['text']}")

# Search with context
context = rag.search_with_context("school", context_window=1)
for doc in context:
    marker = ">>>" if doc["is_match"] else "   "
    print(f"{marker} {doc['text']}")

# Export/Import index
rag.export_index("my_index.json")
rag.import_index("my_index.json")
```

## Compression Formats

| Format | Example | Reduction | Readable | Use Case |
|--------|---------|-----------|----------|----------|
| Verbose | `<ROOT=MOTION> <OPS=PRESENT> <AGENT=boy>` | 0% | Yes | Debugging |
| Compact | `R1 O2 A:boy G:school` | -19% | Yes | Legacy |
| Ultra | `1FNWaboygschomtmrw` | 61% | Yes | Storage + Search |
| Ultra-Ultra | `1FNW1` | 82% | Partial | Max compression |

## Performance

| Metric | Result |
|--------|--------|
| Encoding throughput | **12,792 texts/sec** |
| Token reduction (ultra) | **61%** |
| Byte reduction (ultra) | **61%** |
| Byte reduction (UU) | **82%** |
| Cross-lingual accuracy | **95% English, 60% Spanish** |

## Use Cases

| Use Case | How It Works | Value |
|----------|-------------|-------|
| **Chat storage** | Store 10x more messages | Save DB costs |
| **Log retention** | Keep 10x more logs | Compliance |
| **Document search** | Search without decompressing | Fast retrieval |
| **Email archiving** | Store 10x more emails | Storage savings |
| **Legal discovery** | Compress case documents | Cost reduction |

## API Server

```bash
ptil serve --host 0.0.0.0 --port 8000
```

```bash
# Encode text
curl -X POST http://localhost:8000/encode \
  -H "Content-Type: application/json" \
  -d '{"text": "The boy went to school."}'

# Classify intent
curl -X POST http://localhost:8000/intent \
  -H "Content-Type: application/json" \
  -d '{"text": "I want to buy a phone"}'
```

## Supported Languages

| Language | Model | Accuracy |
|----------|-------|----------|
| English | `en_core_web_sm` | 95% |
| Spanish | `es_core_news_sm` | 60% |
| French | `fr_core_news_sm` | Supported |
| German | `de_core_news_sm` | Supported |

## Project Structure

```
ptil/
├── models.py                    # ROOT, Operator, Role, META, CSC
├── encoder.py                   # Main pipeline
├── rag.py                       # RAG system
├── ultra_compact_serializer.py  # 61% compression, readable
├── ultra_ultra_serializer.py    # 82% compression
├── config.py                    # Configuration
├── cache.py                     # LRU cache
├── metrics.py                   # Performance metrics
├── cli.py                       # Command-line interface
├── server/
│   └── app.py                   # FastAPI REST API
├── ontology/                    # SQLite (54 ROOTs, 3924 predicates)
└── learning/                    # ML components
integrations/                    # Framework integrations
├── langchain_example.py         # LangChain (direct + HTTP)
├── crewai_example.py            # CrewAI
├── autogpt_example.py           # AutoGPT
├── dify_example.py              # Dify
├── flowise_example.py           # Flowise
├── openwebui_example.py         # Open WebUI
└── n8n_workflows.py             # n8n workflow templates
Dockerfile                       # Container image
docker-compose.yml               # PTIL + n8n
```

## Testing

```bash
pytest tests/ -v
```

161 tests passing.

## License

MIT
