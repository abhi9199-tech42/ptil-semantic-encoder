"""Train the ROOT classifier from the ontology database."""

import sys
import logging
import argparse

from .features import FeatureExtractor
from .dataset import build_dataset, train_dev_split
from .classifier import ROOTClassifier

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Train ROOT classifier")
    parser.add_argument("--output", "-o", default="ptil/learning/root_classifier.pkl",
                        help="Output model path")
    parser.add_argument("--spacy-model", default="en_core_web_md",
                        help="spaCy model for word vectors")
    parser.add_argument("--min-weight", type=float, default=0.5,
                        help="Minimum predicate weight to include")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    logger.info("Building feature extractor...")
    fe = FeatureExtractor(spacy_model_name=args.spacy_model)

    logger.info("Building dataset from ontology...")
    features, labels, root_names = build_dataset(fe, min_weight=args.min_weight)
    logger.info(f"Dataset: {features.shape[0]} samples, "
                f"{features.shape[1]} features, {len(root_names)} classes")

    if features.shape[0] == 0:
        logger.error("Empty dataset — nothing to train")
        sys.exit(1)

    logger.info("Training classifier...")
    clf = ROOTClassifier(root_names)
    clf.train(features, labels)

    X_train, X_test, y_train, y_test = train_dev_split(features, labels)
    logger.info(f"Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")

    train_acc = clf._model.score(X_train, y_train)
    test_acc = clf._model.score(X_test, y_test)
    logger.info(f"Train accuracy: {train_acc:.3f}")
    logger.info(f"Test accuracy:  {test_acc:.3f}")

    clf.save(args.output)
    logger.info("Done.")


if __name__ == "__main__":
    main()
