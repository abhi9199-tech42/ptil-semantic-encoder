import logging
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from .models import CSC
from .encoder import PTILEncoder
from .csc_serializer import CSCSerializer
from .tokenizer_backends import create_tokenizer_backend, TokenizerBackend


@dataclass
class EfficiencyMetrics:
    """Metrics for token reduction efficiency analysis."""
    raw_text: str
    csc_serialized: str
    raw_token_count: int
    csc_token_count: int
    reduction_percentage: float
    reduction_ratio: float

    def __str__(self) -> str:
        return (f"EfficiencyMetrics(raw_tokens={self.raw_token_count}, "
                f"csc_tokens={self.csc_token_count}, "
                f"reduction={self.reduction_percentage:.1f}%)")


class EfficiencyAnalyzer:
    """
    Measures and validates token reduction efficiency against real tokenizers.
    """

    def __init__(self, encoder: Optional[PTILEncoder] = None,
                 tokenizer_backend: Optional[TokenizerBackend] = None):
        self.logger = logging.getLogger(__name__)
        self.encoder = encoder or PTILEncoder()
        self.serializer = CSCSerializer()
        self._tokenizer_backend = tokenizer_backend or create_tokenizer_backend()

        self.min_reduction_percentage = 60.0
        self.max_reduction_percentage = 80.0

    def analyze_text(self, text: str, tokenizer_type: str = "bpe", format: str = "ultra") -> EfficiencyMetrics:
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")

        try:
            cscs = self.encoder.encode(text)
            csc_serialized = self.encoder.encode_and_serialize(text, format=format)

            raw_token_count = self._tokenizer_backend.count_tokens(text, tokenizer_type)
            csc_token_count = self._tokenizer_backend.count_tokens(csc_serialized, tokenizer_type)

            reduction_percentage = self._calculate_reduction_percentage(
                raw_token_count, csc_token_count
            )
            reduction_ratio = raw_token_count / max(csc_token_count, 1)

            metrics = EfficiencyMetrics(
                raw_text=text,
                csc_serialized=csc_serialized,
                raw_token_count=raw_token_count,
                csc_token_count=csc_token_count,
                reduction_percentage=reduction_percentage,
                reduction_ratio=reduction_ratio
            )

            self.logger.debug(f"Analyzed text efficiency: {metrics}")
            return metrics

        except Exception as e:
            self.logger.error(f"Efficiency analysis failed for text '{text[:50]}...': {e}")
            raise RuntimeError(f"Efficiency analysis failed: {e}")

    def analyze_batch(self, texts: List[str],
                      tokenizer_type: str = "bpe", format: str = "ultra") -> List[EfficiencyMetrics]:
        if not texts:
            raise ValueError("Text list cannot be empty")

        results = []
        failed_count = 0

        for i, text in enumerate(texts):
            try:
                metrics = self.analyze_text(text, tokenizer_type, format)
                results.append(metrics)
            except Exception as e:
                self.logger.warning(f"Failed to analyze text {i}: {e}")
                failed_count += 1

        if failed_count > 0:
            self.logger.warning(f"Failed to analyze {failed_count}/{len(texts)} texts")

        return results

    def validate_efficiency_target(self, metrics: EfficiencyMetrics) -> bool:
        return (self.min_reduction_percentage <= metrics.reduction_percentage <=
                self.max_reduction_percentage)

    def validate_batch_efficiency(self, metrics_list: List[EfficiencyMetrics]) -> Dict[str, Any]:
        if not metrics_list:
            raise ValueError("Metrics list cannot be empty")

        reductions = [m.reduction_percentage for m in metrics_list]
        ratios = [m.reduction_ratio for m in metrics_list]

        avg_reduction = sum(reductions) / len(reductions)
        min_reduction = min(reductions)
        max_reduction = max(reductions)
        avg_ratio = sum(ratios) / len(ratios)

        meeting_target = sum(1 for m in metrics_list if self.validate_efficiency_target(m))
        target_percentage = (meeting_target / len(metrics_list)) * 100

        overall_valid = (avg_reduction >= self.min_reduction_percentage and
                         target_percentage >= 80.0)

        return {
            "overall_valid": overall_valid,
            "total_texts": len(metrics_list),
            "meeting_target": meeting_target,
            "target_percentage": target_percentage,
            "average_reduction": avg_reduction,
            "statistics": {
                "avg_reduction_percentage": avg_reduction,
                "min_reduction_percentage": min_reduction,
                "max_reduction_percentage": max_reduction,
                "avg_reduction_ratio": avg_ratio
            },
            "target_range": {
                "min": self.min_reduction_percentage,
                "max": self.max_reduction_percentage
            }
        }

    def generate_efficiency_report(self, metrics_list: List[EfficiencyMetrics]) -> str:
        if not metrics_list:
            return "No metrics available for report generation."

        validation = self.validate_batch_efficiency(metrics_list)
        stats = validation["statistics"]

        report_lines = [
            "PTIL Token Reduction Efficiency Report",
            "=" * 40,
            f"Total texts analyzed: {validation['total_texts']}",
            f"Texts meeting target: {validation['meeting_target']} "
            f"({validation['target_percentage']:.1f}%)",
            f"Target range: {validation['target_range']['min']}-"
            f"{validation['target_range']['max']}% reduction",
            "",
            "Statistics:",
            f"  Average reduction: {stats['avg_reduction_percentage']:.1f}%",
            f"  Minimum reduction: {stats['min_reduction_percentage']:.1f}%",
            f"  Maximum reduction: {stats['max_reduction_percentage']:.1f}%",
            f"  Average ratio: {stats['avg_reduction_ratio']:.2f}x",
            "",
            f"Overall validation: {'PASS' if validation['overall_valid'] else 'FAIL'}",
        ]

        if len(metrics_list) <= 5:
            report_lines.extend(["", "Detailed Results:", "-" * 20])

            for i, metrics in enumerate(metrics_list):
                status = "PASS" if self.validate_efficiency_target(metrics) else "FAIL"
                report_lines.append(
                    f"{i+1}. {status} - {metrics.reduction_percentage:.1f}% reduction "
                    f"({metrics.raw_token_count} -> {metrics.csc_token_count} tokens)"
                )
                report_lines.append(f"   Text: {metrics.raw_text[:60]}...")
                report_lines.append(f"   CSC:  {metrics.csc_serialized[:60]}...")
                report_lines.append("")

        return "\n".join(report_lines)

    def _calculate_reduction_percentage(self, raw_count: int, csc_count: int) -> float:
        if raw_count == 0:
            return 0.0
        reduction = raw_count - csc_count
        return (reduction / raw_count) * 100.0
