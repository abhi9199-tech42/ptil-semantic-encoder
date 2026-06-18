"""Feature extraction for learned ROOT mapping."""

from typing import Dict, List, Optional, Tuple
import numpy as np

POS_VOCAB = {
    "VB": 0, "VBD": 1, "VBG": 2, "VBN": 3, "VBP": 4, "VBZ": 5,
    "NN": 6, "NNS": 7, "NNP": 8, "NNPS": 9,
    "JJ": 10, "JJR": 11, "JJS": 12,
    "RB": 13, "RBR": 14, "RBS": 15,
    "MD": 16, "TO": 17, "IN": 18, "DT": 19,
    "CC": 20, "PRP": 21, "PRP$": 22, "WDT": 23,
    "UNKNOWN": 24,
}


def pos_to_onehot(pos_tag: str) -> np.ndarray:
    arr = np.zeros(len(POS_VOCAB), dtype=np.float32)
    idx = POS_VOCAB.get(pos_tag, POS_VOCAB["UNKNOWN"])
    arr[idx] = 1.0
    return arr


class FeatureExtractor:
    def __init__(self, spacy_model_name: str = "en_core_web_md"):
        self._nlp = None
        self._model_name = spacy_model_name

    def _lazy_load_spacy(self):
        if self._nlp is None:
            import spacy
            self._nlp = spacy.load(self._model_name)

    def extract(self, predicate: str, pos_tag: str,
                dep_relations: Optional[List[str]] = None) -> np.ndarray:
        self._lazy_load_spacy()
        vec = self._predicate_vector(predicate)
        pos_vec = pos_to_onehot(pos_tag)
        dep_vec = self._dep_features(dep_relations or [])
        return np.concatenate([vec, pos_vec, dep_vec])

    def _predicate_vector(self, predicate: str) -> np.ndarray:
        doc = self._nlp(predicate.lower().replace("_", " "))
        if doc.has_vector and doc.vector_norm > 0:
            return doc.vector
        return np.zeros(self._nlp.vocab.vectors_length, dtype=np.float32)

    @staticmethod
    def _dep_features(relations: List[str]) -> np.ndarray:
        deps = {"nsubj": 0, "dobj": 1, "iobj": 2, "prep": 3, "aux": 4,
                "neg": 5, "advmod": 6, "amod": 7, "pobj": 8}
        arr = np.zeros(len(deps), dtype=np.float32)
        for r in relations:
            if r in deps:
                arr[deps[r]] = 1.0
        return arr

    def feature_dim(self) -> int:
        self._lazy_load_spacy()
        return self._nlp.vocab.vectors_length + len(POS_VOCAB) + 9

    @property
    def vector_dim(self) -> int:
        self._lazy_load_spacy()
        return self._nlp.vocab.vectors_length
