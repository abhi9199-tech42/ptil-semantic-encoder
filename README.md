# PTIL — Pre-Tokenization Intelligence Layer

A deterministic semantic abstraction system that converts raw natural language text into compact, structured meaning representations called **Compressed Semantic Code (CSC)**.

> **Status:** Research prototype (v0.1.0). See [Production Roadmap](PRODUCTION_ROADMAP.md) for plans.

## What It Does

PTIL sits between raw text and tokenizers. It strips away surface-level syntactic variation and replaces it with a structured semantic representation:

```
Input:  "The boy runs to school."
Output: ROOT=MOTION  OPS=PRESENT  AGENT=boy  GOAL=school  META=ASSERTIVE
```

Same meaning, same output — regardless of language:

```
"El niño corre a la escuela."  →  ROOT=MOTION  OPS=PRESENT  AGENT=niño  GOAL=escuela  META=ASSERTIVE
"Le garçon court à l'école."   →  ROOT=MOTION  OPS=PRESENT  AGENT=garçon  GOAL=école  META=ASSERTIVE
```

## Architecture

```
Text ──► LinguisticAnalyzer ──► ROOTMapper ──► OPSExtractor ──► ROLESBinder ──► METADetector ──► CSC
              (spaCy)         (dictionary)    (rule-based)    (dependency)    (keyword)        │
                                                                                               ▼
                                                                                     Serializer (verbose/compact/ultra)
```

### Four-Layer CSC Structure

| Layer | Purpose | Example |
|-------|---------|---------|
| **ROOT** | Semantic event/state type | `MOTION`, `TRANSFER`, `COGNITION` |
| **OPS** | Tense, aspect, polarity, modality | `PAST`, `NEGATION`, `CONTINUOUS` |
| **ROLES** | Semantic role bindings | `AGENT=boy`, `GOAL=school` |
| **META** | Speech act / epistemic marker | `ASSERTIVE`, `QUESTION`, `UNCERTAIN` |

### Serialization Formats

```python
from ptil import PTILEncoder
encoder = PTILEncoder()

text = "The boy runs to school."

encoder.encode_and_serialize(text, format="verbose")
# <ROOT=MOTION> <OPS=PRESENT> <AGENT=boy> <GOAL=school> <META=ASSERTIVE>

encoder.encode_and_serialize(text, format="compact")
# R:MOTION O:PRESENT A:boy G:school M:ASSERTIVE

encoder.encode_and_serialize(text, format="ultra")
# M|P|A:boy|G:school|AS
```

## Installation

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

**Dependencies:** `spacy>=3.4.0`, `pytest>=7.0.0`, `hypothesis>=6.0.0`

### Supported Languages

| Language | spaCy Model | Status |
|----------|-------------|--------|
| English | `en_core_web_sm` | Primary |
| Spanish | `es_core_news_sm` | Supported |
| French | `fr_core_news_sm` | Supported |
| German | `de_core_news_sm` | Supported |
| Italian | `it_core_news_sm` | Supported |
| Portuguese | `pt_core_news_sm` | Partial |
| Dutch | `nl_core_news_sm` | Partial |
| Chinese | `zh_core_web_sm` | Partial |
| Japanese | `ja_core_news_sm` | Partial |
| Russian | `ru_core_news_sm` | Partial |

## Usage

### Basic Encoding

```python
from ptil import PTILEncoder

encoder = PTILEncoder()
cscs = encoder.encode("The boy runs to school.")

for csc in cscs:
    print(f"ROOT: {csc.root.value}")
    print(f"OPS: {[op.value for op in csc.ops]}")
    print(f"ROLES: {[(role.value, entity.text) for role, entity in csc.roles.items()]}")
    print(f"META: {csc.meta.value if csc.meta else None}")
```

### Language-Specific Encoding

```python
from ptil import PTILEncoder

en = PTILEncoder.create_for_language("en")
es = PTILEncoder.create_for_language("es")

en.encode("The boy runs.")      # ROOT: MOTION
es.encode("El niño corre.")     # ROOT: MOTION
```

### Training Integration

```python
from ptil import PTILEncoder, TrainingConfig

encoder = PTILEncoder()

# Standard: [CSC] + [ORIGINAL_TEXT]
config = TrainingConfig(format_type="standard")
encoder.set_training_config(config)
output = encoder.encode_for_training("The boy runs to school.")
# [CSC] <ROOT=MOTION> <OPS=PRESENT> <AGENT=boy> <GOAL=school> <META=ASSERTIVE> [TEXT] The boy runs to school.

# CSC-only for fine-tuning
config = TrainingConfig(format_type="csc_only")
encoder.set_training_config(config)
output = encoder.encode_for_training("The boy runs to school.")
# [CSC] <ROOT=MOTION> <OPS=PRESENT> <AGENT=boy> <GOAL=school> <META=ASSERTIVE>
```

## Project Structure

```
ptil/
├── __init__.py                  # Package exports
├── models.py                    # ROOT, Operator, Role, META, CSC dataclasses
├── compatibility.py             # ROOT-ROLE compatibility matrix
├── encoder.py                   # Main pipeline orchestrator
├── linguistic_analyzer.py       # spaCy-based POS/dependency/negation/tense extraction
├── root_mapper.py               # Predicate → ROOT dictionary mapping
├── ops_extractor.py             # Rule-based operator extraction
├── roles_binder.py              # Dependency → semantic role binding
├── meta_detector.py             # Speech act / epistemic detection
├── csc_generator.py             # CSC assembly with validation
├── csc_serializer.py            # Verbose format: <ROOT=X> <OPS=Y>
├── compact_serializer.py        # Compact format: R:X O:Y
├── ultra_compact_serializer.py  # Ultra format: X|Y
├── efficiency_analyzer.py       # Token reduction measurement
├── tokenizer_compatibility.py   # BPE/Unigram/WordPiece validation
└── cross_lingual_validator.py   # Cross-language consistency checks

tests/                           # 20 test files (unit + property-based)
examples/                        # 5 demo scripts
docs/                            # Quick start, user guide, API reference
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Property-based tests (Hypothesis)
pytest tests/test_encoder_properties.py -v

# Integration tests
pytest tests/test_integration_all_requirements.py -v

# Cross-lingual tests
pytest tests/test_cross_lingual_properties.py -v
```

- 20 test files covering all components
- Property-based tests using Hypothesis
- Integration tests for end-to-end scenarios

## Known Limitations

| Limitation | Impact | Planned Fix |
|------------|--------|-------------|
| Only 11 ROOT primitives (vs. 300-800 planned) | Limited semantic coverage | Phase 2: expand ontology |
| Dictionary-based ROOT mapping (~200 entries) | Struggles with unseen predicates | Phase 5: learned fallback |
| Duplicate spaCy model loading in `ROLESBinder` | ~2x memory usage | Phase 1: fix pipeline threading |
| Simulated token counting (not real tokenizers) | Efficiency claims unverified | Phase 1: integrate tiktoken |
| Keyword-based META detection | No contextual understanding | Phase 5: learned classifiers |

## Roadmap

See [PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md) for the full 5-phase plan:

1. **Foundation Fixes** — Remove duplicate spaCy loads, real token counting
2. **Scale Ontology** — 200+ ROOTs, 2000+ predicates, embedding fallback
3. **Production Hardening** — Logging, metrics, config, batch processing, caching
4. **API & Integration** — FastAPI server, CLI, gRPC, PyPI packaging
5. **Intelligence Layer** — Learned ROOT mapping, cross-lingual embeddings

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgments

Built with [spaCy](https://spacy.io/), [Hypothesis](https://hypothesis.readthedocs.io/), and [pytest](https://pytest.org/).
