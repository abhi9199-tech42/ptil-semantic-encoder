"""
Learned ROOT mapper that combines the learned classifier with the original DB-based mapper.

This mapper uses a trained classifier for predictions when available, falling back to
the original predicate dictionary and disambiguation logic for unknown predicates.
"""

from typing import Dict, List, Optional, Tuple
from .features import FeatureExtractor
from .classifier import ROOTClassifier
from ..models import ROOT, LinguisticAnalysis
from ..ontology.db import OntologyDB


class LearnedROOTMapper:
    def __init__(self, model_path: Optional[str] = None, spacy_model: str = "en_core_web_md"):
        self._db = OntologyDB()
        self._fallback_root = ROOT.EXISTENCE
        self._feature_extractor = FeatureExtractor(spacy_model_name=spacy_model)
        self._classifier: Optional[ROOTClassifier] = None

        if model_path and self._load_model(model_path):
            print(f"Loaded learned model from {model_path}")
        else:
            print("No learned model loaded - using original ROOT mapper")

    def _load_model(self, path: str) -> bool:
        try:
            self._classifier = ROOTClassifier.load(path)
            return True
        except Exception as e:
            print(f"Failed to load learned model: {e}")
            return False

    def map_predicate(self, predicate: str, pos_context: str,
                      dependency_context: Dict) -> ROOT:
        normalized_predicate = predicate.lower().strip()

        # First try the learned classifier if available
        if self._classifier is not None:
            try:
                features = self._feature_extractor.extract(predicate, pos_context)
                root_name, confidence = self._classifier.predict(features)

                # Use the classifier prediction if confidence is high enough
                if confidence >= 0.7:
                    return ROOT[root_name]
            except Exception:
                pass

        # Fall back to the original DB-based logic
        results = self._db.get_predicate_roots(normalized_predicate)
        if results:
            if len(results) == 1:
                return ROOT[results[0][0]]
            return self._disambiguate([r[0] for r in results], pos_context, dependency_context)

        return self._handle_unknown_predicate(normalized_predicate, pos_context)

    def _disambiguate(self, candidate_names: List[str], pos_context: str,
                      dependency_context: Dict) -> ROOT:
        if not candidate_names:
            return self._fallback_root

        action_roots = {ROOT.MOTION, ROOT.TRANSFER, ROOT.COMMUNICATION,
                        ROOT.CREATION, ROOT.DESTRUCTION, ROOT.CHANGE,
                        ROOT.CONSUMPTION, ROOT.TRAVEL, ROOT.ACTION}

        if pos_context in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
            for name in candidate_names:
                if ROOT[name] in action_roots:
                    return ROOT[name]

        if pos_context in ["NN", "NNS", "NNP", "NNPS"]:
            state_roots = {ROOT.EXISTENCE, ROOT.POSSESSION, ROOT.COGNITION,
                           ROOT.STATE, ROOT.PROPERTY}
            for name in candidate_names:
                if ROOT[name] in state_roots:
                    return ROOT[name]

        if dependency_context:
            if "dobj" in dependency_context.get("relations", []):
                transitive_roots = {ROOT.TRANSFER, ROOT.CREATION, ROOT.DESTRUCTION,
                                    ROOT.PERCEPTION, ROOT.COMMUNICATION,
                                    ROOT.CONSUMPTION}
                for name in candidate_names:
                    if ROOT[name] in transitive_roots:
                        return ROOT[name]

        return ROOT[candidate_names[0]]

    def _handle_unknown_predicate(self, predicate: str, pos_context: str) -> ROOT:
        if pos_context in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
            return ROOT.CHANGE
        elif pos_context in ["NN", "NNS", "NNP", "NNPS"]:
            return ROOT.EXISTENCE
        return self._fallback_root

    def is_predicate_known(self, predicate: str) -> bool:
        return self._db.is_predicate_known(predicate)

    def get_all_predicates_for_root(self, root: ROOT) -> List[str]:
        cur = self._db.connect().execute(
            "SELECT predicate FROM predicates WHERE root_id = (SELECT id FROM roots WHERE name = ?) ORDER BY predicate",
            (root.name,)
        )
        return [row["predicate"] for row in cur.fetchall()]

    def is_trained(self) -> bool:
        return self._classifier is not None

    def get_classifier_stats(self) -> Dict[str, any]:
        if not self._classifier:
            return {"status": "no_model_loaded"}

        return {
            "status": "model_loaded",
            "classes": len(self._classifier.root_names),
            "feature_dim": self._feature_extractor.feature_dim(),
            "vector_dim": self._feature_extractor.vector_dim,
        }
