from typing import Dict, List, Set, Optional, Tuple
from .models import ROOT, LinguisticAnalysis
from .ontology.db import OntologyDB


class ROOTMapper:
    def __init__(self):
        self._db = OntologyDB()
        self._fallback_root = ROOT.EXISTENCE
        self._embedding_model = None

    def map_predicate(self, predicate: str, pos_context: str,
                      dependency_context: Dict) -> ROOT:
        normalized_predicate = predicate.lower().strip()

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
            return self._embedding_fallback(predicate) or ROOT.CHANGE
        elif pos_context in ["NN", "NNS", "NNP", "NNPS"]:
            return self._embedding_fallback(predicate) or ROOT.EXISTENCE
        return self._embedding_fallback(predicate) or self._fallback_root

    def _embedding_fallback(self, predicate: str) -> Optional[ROOT]:
        try:
            if self._embedding_model is None:
                import spacy
                self._embedding_model = spacy.load("en_core_web_md")
            doc = self._embedding_model(predicate)
            if not doc.has_vector or doc.vector_norm == 0:
                return None

            best_root = None
            best_sim = -1.0
            for root_name in self._db.get_all_roots():
                try:
                    root_token = self._embedding_model(root_name.lower().replace("_", " "))
                    if root_token.has_vector and root_token.vector_norm > 0:
                        sim = doc.similarity(root_token)
                        if sim > best_sim:
                            best_sim = sim
                            best_root = ROOT[root_name]
                except (KeyError, ValueError):
                    continue

            if best_sim > 0.4:
                return best_root
        except Exception:
            pass
        return None

    def get_all_predicates_for_root(self, root: ROOT) -> List[str]:
        cur = self._db.connect().execute(
            "SELECT predicate FROM predicates WHERE root_id = (SELECT id FROM roots WHERE name = ?) ORDER BY predicate",
            (root.name,)
        )
        return [row["predicate"] for row in cur.fetchall()]

    def is_predicate_known(self, predicate: str) -> bool:
        return self._db.is_predicate_known(predicate)
