import logging
import hashlib
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from .models import CSC, ROOT, META, Operator, Role, Entity, LinguisticAnalysis
from .linguistic_analyzer import LinguisticAnalyzer
from .root_mapper import ROOTMapper
from .ops_extractor import OPSExtractor
from .roles_binder import ROLESBinder
from .meta_detector import METADetector
from .csc_generator import CSCGenerator
from .csc_serializer import CSCSerializer
from .compact_serializer import CompactCSCSerializer
from .ultra_compact_serializer import UltraCompactCSCSerializer
from .config import PTILConfig
from .logging_context import PTILContext, PTILogger, set_context
from .cache import LRUCache
from .metrics import MetricsCollector


@dataclass
class TrainingConfig:
    format_type: str = "standard"
    csc_weight: float = 1.0
    original_weight: float = 1.0
    separator: str = " "
    include_brackets: bool = True


class PTILEncoder:
    def __init__(self, model_name: str = "en_core_web_sm", language: Optional[str] = None,
                 config: Optional[PTILConfig] = None):
        resolved = (config or PTILConfig()).resolve()
        if model_name != "en_core_web_sm":
            resolved.spaCy_model = model_name
        if language is not None:
            resolved.language = language

        self.config = resolved
        self.logger = PTILogger(__name__, json_format=resolved.log_json)
        self.language = resolved.language
        self.metrics = MetricsCollector() if resolved.enable_metrics else None
        self.cache = LRUCache(capacity=resolved.cache_size, ttl_seconds=resolved.cache_ttl_seconds)
        self.training_config = TrainingConfig()

        try:
            self.linguistic_analyzer = LinguisticAnalyzer(resolved.spaCy_model, resolved.language)
            self.root_mapper = ROOTMapper()
            self.ops_extractor = OPSExtractor()
            self.roles_binder = ROLESBinder()
            self.meta_detector = METADetector()
            self.csc_generator = CSCGenerator()
            self.csc_serializer = CSCSerializer()
            self.compact_serializer = CompactCSCSerializer()
            self.ultra_compact_serializer = UltraCompactCSCSerializer()

            self.logger.info(f"PTILEncoder initialized", model=resolved.spaCy_model, language=resolved.language)
        except Exception as e:
            self.logger.error(f"Failed to initialize PTILEncoder", error=str(e))
            raise RuntimeError(f"PTILEncoder initialization failed: {e}")

    @classmethod
    def from_config(cls, config: PTILConfig) -> "PTILEncoder":
        return cls(config=config)

    @classmethod
    def create_for_language(cls, language: str) -> "PTILEncoder":
        analyzer = LinguisticAnalyzer.create_for_language(language)
        return cls(model_name=analyzer.model_name, language=language)

    def _make_context(self, text: str, component: str = "") -> PTILContext:
        ctx = PTILContext.create(
            language=self.language,
            input_text=text,
            component=component or self.__class__.__name__,
        )
        set_context(ctx)
        return ctx

    def _cache_key(self, text: str, fmt: str = "") -> str:
        raw = f"{text}|{self.language}|{self.config.spaCy_model}|{fmt}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def encode(self, text: str) -> List[CSC]:
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        if not text or not text.strip():
            self.logger.warning("Empty input text provided")
            return []

        ctx = self._make_context(text)
        cache_key = self._cache_key(text)

        cached = self.cache.get(cache_key)
        if cached is not None:
            self.logger.info("Cache hit", request_id=ctx.request_id)
            if self.metrics:
                self.metrics.increment("cache_hit")
            return cached

        if self.metrics:
            self.metrics.increment("encode_requests")

        try:
            with self.metrics.timing("encode") if self.metrics else _null_context():
                analysis = self._perform_linguistic_analysis(text)
                if not analysis.tokens:
                    return []

                cscs = self._generate_cscs_from_analysis(text, analysis)
                self.cache.set(cache_key, cscs)
                self.logger.debug(f"Generated {len(cscs)} CSC(s)", request_id=ctx.request_id)
                return cscs
        except Exception as e:
            self.logger.error(f"Encoding failed", error=str(e), request_id=ctx.request_id)
            return self._create_fallback_csc(text)

    def encode_batch(self, texts: List[str]) -> List[List[CSC]]:
        if not texts:
            return []
        results = []
        for text in texts:
            try:
                results.append(self.encode(text))
            except Exception as e:
                self.logger.error(f"Batch encoding failed for item", error=str(e))
                results.append([])
        return results

    def encode_and_serialize(self, text: str, format: str = "verbose") -> str:
        try:
            cscs = self.encode(text)
            if not cscs:
                return ""

            if format == "ultra":
                return self.ultra_compact_serializer.serialize_multiple(cscs)
            elif format == "compact":
                return self.compact_serializer.serialize_multiple(cscs)
            else:
                return self.csc_serializer.serialize_multiple(cscs)
        except Exception as e:
            self.logger.error(f"Serialization failed", error=str(e))
            return ""

    def encode_and_serialize_batch(self, texts: List[str], format: str = "verbose") -> List[str]:
        results = []
        for t in texts:
            try:
                results.append(self.encode_and_serialize(t, format))
            except Exception as e:
                self.logger.error(f"Batch serialization failed for item", error=str(e))
                results.append("")
        return results

    def encode_for_training(self, text: str, config: Optional[TrainingConfig] = None) -> str:
        if config is None:
            config = self.training_config
        try:
            csc_serialized = self.encode_and_serialize(text, format="verbose")
            return self._format_for_training(csc_serialized, text, config)
        except Exception as e:
            self.logger.error(f"Training format generation failed", error=str(e))
            return f"[TEXT] {text}" if config.include_brackets else text

    def set_training_config(self, config: TrainingConfig) -> None:
        self.training_config = config
        self.logger.info(f"Training configuration updated", format=config.format_type)

    def get_training_config(self) -> TrainingConfig:
        return self.training_config

    def _format_for_training(self, csc_serialized: str, original_text: str,
                             config: TrainingConfig) -> str:
        if config.format_type == "csc_only":
            return f"[CSC] {csc_serialized}" if config.include_brackets else csc_serialized
        elif config.format_type == "mixed":
            csc_part = f"[CSC] {csc_serialized}" if config.include_brackets else csc_serialized
            text_part = f"[TEXT] {original_text}" if config.include_brackets else original_text
            csc_repeats = max(1, int(config.csc_weight))
            text_repeats = max(1, int(config.original_weight))
            parts = [csc_part] * csc_repeats + [text_part] * text_repeats
            return config.separator.join(parts)
        else:
            csc_part = f"[CSC] {csc_serialized}" if config.include_brackets else csc_serialized or "[CSC] "
            text_part = f"[TEXT] {original_text}" if config.include_brackets else original_text
            return f"{csc_part}{config.separator}{text_part}"

    def _perform_linguistic_analysis(self, text: str) -> LinguisticAnalysis:
        try:
            return self.linguistic_analyzer.analyze(text)
        except Exception as e:
            self.logger.warning(f"Linguistic analysis failed", error=str(e))
            tokens = text.split()
            return LinguisticAnalysis(
                tokens=tokens,
                lemmas=tokens,
                pos_tags=["NOUN"] * len(tokens),
                dependencies=[],
                negation_markers=[],
                tense_markers={},
                aspect_markers={}
            )

    def _generate_cscs_from_analysis(self, text: str, analysis: LinguisticAnalysis) -> List[CSC]:
        cscs = []
        try:
            predicates = self._identify_predicates(analysis)
            if not predicates:
                csc = self._create_single_csc(text, analysis, fallback=True)
                if csc:
                    cscs.append(csc)
            else:
                for predicate_info in predicates:
                    csc = self._create_single_csc(text, analysis, predicate_info)
                    if csc:
                        cscs.append(csc)
        except Exception as e:
            self.logger.error(f"CSC generation failed", error=str(e))
            fallback_csc = self._create_single_csc(text, analysis, fallback=True)
            if fallback_csc:
                cscs.append(fallback_csc)
        return cscs

    def _identify_predicates(self, analysis: LinguisticAnalysis) -> List[Dict[str, Any]]:
        predicates = []
        lemmas = getattr(analysis, "lemmas", analysis.tokens)
        for i, (token, pos) in enumerate(zip(analysis.tokens, analysis.pos_tags)):
            if pos in ["VERB", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
                predicates.append({
                    "token": token, "lemma": lemmas[i] if i < len(lemmas) else token,
                    "index": i, "pos": pos
                })
        if not predicates:
            for i, (token, pos) in enumerate(zip(analysis.tokens, analysis.pos_tags)):
                if pos in ["NOUN", "ADJ"]:
                    lemma = lemmas[i] if i < len(lemmas) else token
                    if self.root_mapper.is_predicate_known(token) or self.root_mapper.is_predicate_known(lemma):
                        predicates.append({
                            "token": token, "lemma": lemma, "index": i, "pos": pos
                        })
        return predicates

    def _create_single_csc(self, text: str, analysis: LinguisticAnalysis,
                           predicate_info: Optional[Dict[str, Any]] = None,
                           fallback: bool = False) -> Optional[CSC]:
        try:
            root = self._map_root(analysis, predicate_info, fallback)
            ops = self._extract_operators(analysis)
            roles = self._bind_roles(analysis, root)
            meta = self._detect_meta(analysis)
            return self.csc_generator.generate_csc(root, ops, roles, meta)
        except Exception as e:
            self.logger.warning(f"Single CSC creation failed", error=str(e))
            if not fallback:
                return self._create_single_csc(text, analysis, fallback=True)
            return None

    def _map_root(self, analysis: LinguisticAnalysis,
                  predicate_info: Optional[Dict[str, Any]] = None,
                  fallback: bool = False) -> ROOT:
        try:
            if fallback or not predicate_info:
                return ROOT.EXISTENCE
            predicate = predicate_info.get("lemma", predicate_info["token"])
            pos_context = predicate_info["pos"]
            dependency_context = {"relations": [dep[1] for dep in analysis.dependencies]}
            return self.root_mapper.map_predicate(predicate, pos_context, dependency_context)
        except Exception as e:
            self.logger.warning(f"ROOT mapping failed", error=str(e))
            return ROOT.EXISTENCE

    def _extract_operators(self, analysis: LinguisticAnalysis) -> List[Operator]:
        try:
            return self.ops_extractor.extract_operators(analysis)
        except Exception as e:
            self.logger.warning(f"Operator extraction failed", error=str(e))
            return []

    def _bind_roles(self, analysis: LinguisticAnalysis, root: ROOT) -> Dict[Role, Entity]:
        try:
            return self.roles_binder.bind_roles(analysis, root)
        except Exception as e:
            self.logger.warning(f"Role binding failed", error=str(e))
            return {}

    def _detect_meta(self, analysis: LinguisticAnalysis) -> Optional[META]:
        try:
            return self.meta_detector.detect_meta(analysis)
        except Exception as e:
            self.logger.warning(f"META detection failed", error=str(e))
            return None

    def _create_fallback_csc(self, text: str) -> List[CSC]:
        try:
            return [self.csc_generator.generate_csc(ROOT.EXISTENCE, [], {}, None)]
        except Exception:
            return []

    def get_component_status(self) -> Dict[str, bool]:
        components = [
            ("linguistic_analyzer", self.linguistic_analyzer),
            ("root_mapper", self.root_mapper),
            ("ops_extractor", self.ops_extractor),
            ("roles_binder", self.roles_binder),
            ("meta_detector", self.meta_detector),
            ("csc_generator", self.csc_generator),
            ("csc_serializer", self.csc_serializer),
        ]
        return {name: comp is not None for name, comp in components}

    def get_cache_stats(self) -> Dict[str, Any]:
        return {"size": self.cache.size, "keys": self.cache.keys()}

    def clear_cache(self):
        self.cache.clear()
        self.logger.info("Cache cleared")

    def get_metrics_snapshot(self) -> Optional[Dict[str, Any]]:
        return self.metrics.snapshot() if self.metrics else None


class _null_context:
    def __enter__(self): return self
    def __exit__(self, *args): pass
