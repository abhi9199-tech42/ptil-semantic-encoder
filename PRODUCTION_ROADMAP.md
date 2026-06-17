# PTIL Production Roadmap

## Current State: Prototype (v0.1.0)

The system is a well-architected proof-of-concept with clean separation of concerns,
rule-based NLP pipelines, and a solid compatibility matrix. It is not production-ready.

---

## Phase 1: Foundation Fixes (v0.2.0) — 2-3 weeks

**Goal:** Eliminate architectural debt, fix correctness issues.

### 1.1 Remove Duplicate spaCy Loading
- **Problem:** `ROLESBinder.__init__` loads a separate spaCy model.
  `bind_roles()` re-processes text through spaCy despite `LinguisticAnalysis` already existing.
- **Fix:** Pass the spaCy `Doc` (or tokens) from `LinguisticAnalyzer` through the pipeline.
  `ROLESBinder` should accept `LinguisticAnalysis` and the original `Doc`, not load its own model.
- **Files:** `ptil/roles_binder.py`, `ptil/encoder.py`, `ptil/linguistic_analyzer.py`

### 1.2 Thread the SpaCy Doc Through the Pipeline
- **Problem:** `LinguisticAnalyzer.analyze()` produces `LinguisticAnalysis` but discards
  the underlying `Doc` object. Downstream components (`roles_binder`) need it for
  noun phrase extraction and dependency traversal.
- **Fix:** Add `doc` field to `LinguisticAnalysis` dataclass. Pass it through the pipeline.
- **Files:** `ptil/models.py`, `ptil/linguistic_analyzer.py`, `ptil/encoder.py`

### 1.3 Fix Token Counting
- **Problem:** `efficiency_analyzer.py` uses regex-based tokenizer simulation. The 60-80%
  reduction claim is unverifiable.
- **Fix:** Integrate `tiktoken` or HuggingFace `tokenizers` for real BPE/WordPiece counting.
  Add a `TokenizerBackend` protocol and inject real tokenizers.
- **Files:** `ptil/efficiency_analyzer.py`, new `ptil/tokenizer_backends.py`

### 1.4 Standardize Return Types
- **Problem:** `_extract_operators()` returns `List[Operator]` but type hint says `List`.
- **Fix:** Audit all return type annotations across all modules.
- **Files:** All `ptil/*.py`

---

## Phase 2: Scale the Ontology (v0.3.0) — 3-4 weeks

**Goal:** Move from 11 ROOTs to 200+, build a real predicate dictionary.

### 2.1 Expand ROOT Ontology
- **Problem:** README claims "300-800 semantic primitives." Only 11 exist.
- **Fix:**
  - Add 50 ROOTs minimum (CATEGORIZATION, EVALUATION, EMOTION, DESIRE, ABILITY,
    OBLIGATION, PERMISSION, PREVENTION, ENABLEMENT, CAUSATION, etc.)
  - Each ROOT gets: name, description, compatible roles, example predicates
  - Store in `ptil/ontology/root_definitions.json`
- **Files:** `ptil/models.py`, new `ptil/ontology/` directory

### 2.2 Build Predicate-ROOT Mapping Database
- **Problem:** ~200 hardcoded entries in `_build_predicate_dictionary()`. No structure.
- **Fix:**
  - Move dictionary to `ptil/ontology/predicate_map.json`
  - Add frequency weights for disambiguation
  - Support loading custom dictionaries from user config
  - Target: 2000+ English predicates, 500+ per additional language
- **Files:** `ptil/root_mapper.py`, new `ptil/ontology/predicate_map.json`

### 2.3 Add Embedding-Based Fallback for Unknown Predicates
- **Problem:** Unknown predicates fall back to `ROOT.CHANGE` or `ROOT.EXISTENCE` with no
  semantic reasoning.
- **Fix:**
  - Use `spaCy` word vectors to find nearest known predicate
  - Add a `ROOTResolver` protocol: `dict_lookup -> vector_similarity -> fallback`
  - Cache results for repeated unknowns
- **Files:** `ptil/root_mapper.py`

### 2.4 Add Role Hierarchy
- **Problem:** 8 flat role definitions. No inheritance or specificity.
- **Fix:**
  - Add role hierarchy: `AGENT > CAUSER`, `PATIENT > AFFECTED`, `THEME > CONTENT`
  - Allow roles to inherit compatibility from parent
  - Store in `ptil/ontology/role_hierarchy.json`
- **Files:** `ptil/models.py`, `ptil/compatibility.py`

---

## Phase 3: Production Hardening (v0.4.0) — 3-4 weeks

**Goal:** Reliability, performance, observability.

### 3.1 Add Structured Logging
- **Problem:** Uses `logging.getLogger(__name__)` inconsistently. No correlation IDs.
- **Fix:**
  - Add `PTILContext` dataclass: request_id, timestamp, language, input_hash
  - Thread context through all components
  - Add JSON log format option for production
- **Files:** All `ptil/*.py`

### 3.2 Add Metrics Collection
- **Problem:** No runtime metrics. `efficiency_analyzer` is offline-only.
- **Fix:**
  - Add `prometheus_client` or `statsd` integration (optional dependency)
  - Track: encode latency, predicate lookup hit rate, unknown predicate rate,
    role binding success rate, token reduction per request
  - Expose via `/metrics` endpoint in API mode
- **Files:** New `ptil/metrics.py`, modifications to `ptil/encoder.py`

### 3.3 Add Configuration System
- **Problem:** `TrainingConfig` is the only config. No way to tune behavior.
- **Fix:**
  - Create `PTILConfig` dataclass:
    ```
    language: str = "en"
    spaCy_model: str = "en_core_web_sm"
    unknown_predicate_strategy: str = "vector_fallback"  # or "fallback_root", "raise"
    serialization_format: str = "verbose"
    enable_metrics: bool = False
    log_level: str = "INFO"
    custom_predicate_map: Optional[Path] = None
    ```
  - Support loading from `ptil.json` or environment variables
- **Files:** New `ptil/config.py`, modifications to `ptil/encoder.py`

### 3.4 Add Batch Processing
- **Problem:** `encode()` processes one text at a time. No batching.
- **Fix:**
  - Add `encode_batch(texts: List[str]) -> List[List[CSC]]`
  - Parallelize spaCy processing with `nlp.pipe()` (multiprocessing)
  - Add `max_workers` and `batch_size` config options
- **Files:** `ptil/encoder.py`

### 3.5 Add Caching Layer
- **Problem:** Re-encoding identical text does redundant work.
- **Fix:**
  - Add `LRUCache` keyed by `(text, language, config_hash)`
  - Configurable cache size and TTL
  - Optional Redis backend for distributed deployments
- **Files:** New `ptil/cache.py`, modifications to `ptil/encoder.py`

---

## Phase 4: API & Integration (v0.5.0) — 3-4 weeks

**Goal:** Usable as a service, not just a library.

### 4.1 REST API
- **Fix:**
  - FastAPI server with `/encode`, `/encode/batch`, `/health`, `/metrics`
  - Request/response Pydantic models
  - Rate limiting, request validation
  - Docker image with multi-stage build
- **Files:** New `ptil/server/` directory

### 4.2 CLI Tool
- **Fix:**
  - `ptil encode "text" --format ultra --language en`
  - `ptil serve --port 8000 --workers 4`
  - `ptil benchmark --input file.txt --format compact`
- **Files:** New `ptil/cli.py`

### 4.3 gRPC Interface
- **Fix:**
  - Proto definition for `PTILEncode`, `PTILEncodeBatch`, `PTILHealth`
  - Streaming support for large batches
- **Files:** New `ptil/proto/` directory

### 4.4 SDK Packaging
- **Fix:**
  - Proper `pyproject.toml` (replace `setup.py`)
  - Wheel builds for Python 3.9-3.13
  - Publish to PyPI with `ptil-semantic-encoder` name
  - Type stubs for `py.typed`
- **Files:** `pyproject.toml`, `ptil/py.typed`

---

## Phase 5: Intelligence Layer (v0.6.0+) — Ongoing

**Goal:** Move from rules to learned components.

### 5.1 Learned ROOT Mapping
- Train a classifier on `(predicate, POS, dependency_context) -> ROOT`
- Use contrastive learning: same-ROOT predicates are positives
- Start with 2000 labeled examples, expand to 20k
- Fallback to dictionary for unknown predicates

### 5.2 Cross-Lingual Embedding Alignment
- Use XLM-R or LaBSE embeddings
- Align predicate vectors across languages
- Enable zero-shot ROOT mapping for unseen languages

### 5.3 Active Learning Pipeline
- Flag low-confidence encodings (multiple ROOT candidates, fallback usage)
- Human-in-the-loop labeling interface
- Continuous model improvement

### 5.4 CSC Diff and Merge
- Compute semantic distance between two CSCs
- Merge CSCs from compound sentences
- Detect paraphrases (same meaning, different surface)

---

## Dependency Roadmap

| Phase | New Dependencies | Optional |
|-------|-----------------|----------|
| 1 | `tiktoken` or `tokenizers` | — |
| 2 | — | `numpy` (for vector fallback) |
| 3 | — | `prometheus-client`, `redis` |
| 4 | `fastapi`, `uvicorn`, `grpcio`, `protobuf` | — |
| 5 | `torch`, `transformers`, `sentence-transformers` | `wandb` |

---

## Testing Strategy Per Phase

| Phase | Test Coverage Target | New Test Types |
|-------|---------------------|----------------|
| 1 | 95% (current: ~98%) | Fix broken tests from refactor |
| 2 | 90% on new ontology | Property-based tests for new ROOTs |
| 3 | 95% | Load tests, integration tests with metrics |
| 4 | 90% API coverage | API contract tests, Docker smoke tests |
| 5 | 85% on learned components | Adversarial tests, regression benchmarks |

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| spaCy model quality varies by language | Incorrect linguistic analysis | Validate per-language, provide model quality scores |
| Dictionary-based ROOT mapping ceiling | Low accuracy on domain text | Phase 5 learned fallback is the exit strategy |
| Token counting mismatch with real tokenizers | Efficiency claims invalid | Phase 1.3 fixes this with real tokenizers |
| Multi-language predicate coverage gaps | Poor cross-lingual consistency | Prioritize top 5 languages, community contributions for others |
| Breaking changes in spaCy API | Pipeline breaks on upgrade | Pin spaCy version, add CI matrix testing |
