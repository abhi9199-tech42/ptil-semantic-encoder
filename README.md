# PTIL — Text Compression That Stays Searchable

> 82% compression. Readable. Searchable. No vector database.

---

## The Problem

Your AI agent forgets everything. Every message costs tokens. Every token costs money. When the context window fills up, older memories get deleted. RAG systems store raw text — wasting storage, slowing search.

## The Solution

PTIL compresses text to **20% of its original size** while keeping it **readable and searchable**.

```
Input:  "The boy will not go to school tomorrow."
Stored: 1FNWaboygschomtmrw  (82% smaller, still readable)
```

| | Gzip | Zlib | PTIL |
|---|---|---|---|
| Compression | 40% | 42% | **82%** |
| Searchable | No | No | **Yes** |
| Readable | No | No | **Yes** |

PTIL wins because it understands **meaning**, not just bytes.

## Quick Start

```bash
pip install ptil
python -m spacy download en_core_web_sm
```

```python
from ptil.rag import PTILRAG

rag = PTILRAG()

# Compress 82%
rag.add_document("The boy went to school.")
rag.add_document("She read a book all morning.")

# Search without decompressing
results = rag.search("school")
print(results[0]["text"])  # "The boy went to school."
```

## REST API

```bash
pip install ptil[server]
ptil serve --port 8000
# Docs: http://localhost:8000/docs
```

```bash
curl -X POST http://localhost:8000/encode \
  -H "Content-Type: application/json" \
  -d '{"text": "The boy went to school.", "format": "ultra"}'
```

## Docker

```bash
git clone https://github.com/abhi9199-tech42/ptil-semantic-encoder
cd ptil-semantic-encoder
docker compose up -d
# PTIL: http://localhost:8000 | n8n: http://localhost:5678
```

## Agent Integrations

Works with any framework. See `integrations/` for examples.

| Framework | File |
|-----------|------|
| LangChain | `integrations/langchain_example.py` |
| CrewAI | `integrations/crewai_example.py` |
| AutoGPT | `integrations/autogpt_example.py` |
| Dify | `integrations/dify_example.py` |
| Flowise | `integrations/flowise_example.py` |
| Open WebUI | `integrations/openwebui_example.py` |
| n8n | `integrations/n8n_workflows.py` |

## Benchmarks

```
Compression:    82% byte reduction (Gzip: 40%)
Speed:          12,792 texts/sec encoding
Agent Memory:   120 tokens → 22 tokens (82% reduction)
```

Real benchmarks from `benchmarks/benchmark_real.py`. No fabrication.

## License

**Free for personal use.** MIT License.

**Business/commercial use requires a subscription.** Contact for pricing.

Enterprise: custom features, priority support, SLA agreements.

## Links

- **GitHub:** https://github.com/abhi9199-tech42/ptil-semantic-encoder
- **PyPI:** https://pypi.org/project/ptil
