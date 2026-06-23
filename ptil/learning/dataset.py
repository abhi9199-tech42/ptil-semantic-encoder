"""Build labeled training dataset from the ontology DB."""

from typing import List, Tuple, Optional
import numpy as np

from ..ontology.db import OntologyDB
from .features import FeatureExtractor


def build_dataset(feature_extractor: FeatureExtractor,
                  min_weight: float = 0.5) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    db = OntologyDB()
    conn = db.connect()

    cur = conn.execute("""
        SELECT p.predicate, p.language, r.name as root_name
        FROM predicates p
        JOIN roots r ON p.root_id = r.id
        WHERE p.weight >= ?
        ORDER BY p.predicate
    """, (min_weight,))

    rows = cur.fetchall()
    if not rows:
        return np.empty((0, feature_extractor.feature_dim()), dtype=np.float32), \
               np.empty(0, dtype=np.int64), []

    root_names = db.get_all_roots()
    root_to_idx = {name: i for i, name in enumerate(root_names)}

    features = []
    labels = []
    skipped = 0

    for predicate, language, root_name in rows:
        idx = root_to_idx.get(root_name)
        if idx is None:
            skipped += 1
            continue

        pos_tag = "VB" if language == "en" else "VB"
        try:
            vec = feature_extractor.extract(predicate, pos_tag)
            features.append(vec)
            labels.append(idx)
        except Exception:
            skipped += 1

    if not features:
        return np.empty((0, feature_extractor.feature_dim()), dtype=np.float32), \
               np.empty(0, dtype=np.int64), root_names

    return np.stack(features), np.array(labels, dtype=np.int64), root_names


def train_dev_split(features: np.ndarray, labels: np.ndarray,
                    test_ratio: float = 0.2, seed: int = 42):
    from sklearn.model_selection import train_test_split
    from collections import Counter
    min_count = min(Counter(labels).values()) if len(labels) > 0 else 0
    if min_count < 2:
        return train_test_split(features, labels, test_size=test_ratio,
                                random_state=seed)
    return train_test_split(features, labels, test_size=test_ratio,
                            random_state=seed, stratify=labels)
