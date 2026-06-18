"""Learned ROOT classifier with sklearn."""

import pickle
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Dict
import numpy as np

logger = logging.getLogger(__name__)


class ROOTClassifier:
    def __init__(self, root_names: List[str]):
        self.root_names = root_names
        self._model = None
        self._label_encoder = {name: i for i, name in enumerate(root_names)}

    @property
    def is_trained(self) -> bool:
        return self._model is not None

    def train(self, features: np.ndarray, labels: np.ndarray):
        try:
            from sklearn.linear_model import LogisticRegression
        except ImportError:
            raise ImportError("scikit-learn is required for training. pip install scikit-learn")

        self._model = LogisticRegression(
            C=1.0, multi_class="multinomial", solver="lbfgs",
            max_iter=1000, random_state=42, n_jobs=-1,
        )
        self._model.fit(features, labels)
        logger.info(f"Trained ROOTClassifier: {len(self.root_names)} classes, "
                    f"{features.shape[0]} samples, {features.shape[1]} features")

    def predict(self, feature_vec: np.ndarray) -> Tuple[str, float]:
        if self._model is None:
            raise RuntimeError("No trained model")
        probs = self._model.predict_proba(feature_vec.reshape(1, -1))[0]
        pred_idx = int(np.argmax(probs))
        confidence = float(probs[pred_idx])
        return self.root_names[pred_idx], confidence

    def predict_top_k(self, feature_vec: np.ndarray, k: int = 3) -> List[Tuple[str, float]]:
        if self._model is None:
            raise RuntimeError("No trained model")
        probs = self._model.predict_proba(feature_vec.reshape(1, -1))[0]
        top_k = np.argsort(probs)[::-1][:k]
        return [(self.root_names[i], float(probs[i])) for i in top_k]

    def save(self, path: str):
        data = {
            "root_names": self.root_names,
            "model": self._model,
        }
        with open(path, "wb") as f:
            pickle.dump(data, f)
        logger.info(f"Model saved to {path}")

    @classmethod
    def load(cls, path: str) -> "ROOTClassifier":
        with open(path, "rb") as f:
            data = pickle.load(f)
        obj = cls(data["root_names"])
        obj._model = data["model"]
        logger.info(f"Model loaded from {path} ({len(obj.root_names)} classes)")
        return obj
