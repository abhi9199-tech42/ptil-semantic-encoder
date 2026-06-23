
import pytest
from ptil import PTILEncoder, ROOT, Operator, Role, META
from ptil.linguistic_analyzer import LinguisticAnalyzer
from ptil.ops_extractor import OPSExtractor
from ptil.roles_binder import ROLESBinder
from ptil.meta_detector import METADetector
from ptil.csc_generator import CSCGenerator
from ptil.models import LinguisticAnalysis, CSC

class TestOPSExtractorErrorHandling:
    """Test error handling in OPSExtractor."""
    
    def test_contradictory_tense_markers(self):
        """Test handling of contradictory tense markers (e.g., markers for both past and future)."""
        extractor = OPSExtractor()
        # Simulate an analysis with conflicting tense markers
        analysis = LinguisticAnalysis(
            tokens=["will", "went"],
            pos_tags=["MD", "VBD"],
            dependencies=[],
            negation_markers=[],
            # Intentionally contradictory
            tense_markers={"future": [0], "past": [1]},
            aspect_markers={}
        )
        
        ops = extractor.extract_operators(analysis)
        # Should deterministically pick one or handle gracefully without crashing
        tenses = [op for op in ops if op in {Operator.PAST, Operator.FUTURE, Operator.PRESENT}]
        assert len(tenses) <= 1  # Should resolve to at most one primary tense
    
    def test_empty_analysis_ops(self):
        """Test extraction from completely empty analysis."""
        extractor = OPSExtractor()
        analysis = LinguisticAnalysis(
            tokens=[],
            pos_tags=[],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        ops = extractor.extract_operators(analysis)
        assert isinstance(ops, list)
        # Should probably default to PRESENT or empty
        assert Operator.PRESENT in ops or len(ops) == 0

class TestROLESBinderErrorHandling:
    """Test error handling in ROLESBinder."""
    
    def test_missing_subject_object(self):
        """Test binding when no clear subject or object exists (e.g. imperative or fragments)."""
        binder = ROLESBinder()
        analysis = LinguisticAnalysis(
            tokens=["Run", "!"],
            pos_tags=["VB", "."],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        roles = binder.bind_roles(analysis, ROOT.MOTION)
        assert isinstance(roles, dict)
        
    def test_passive_without_agent(self):
        """Test passive voice where agent is missing ('The window was broken')."""
        binder = ROLESBinder()
        analyzer = LinguisticAnalyzer()
        analysis = analyzer.analyze("The window was broken")
        roles = binder.bind_roles(analysis, ROOT.CHANGE)
        
        assert Role.AGENT not in roles

class TestMETADetectorErrorHandling:
    """Test error handling in METADetector."""
    
    def test_mixed_signals(self):
        """Test sentence with declarative structure but question mark."""
        detector = METADetector()
        # "You are going?"
        analysis = LinguisticAnalysis(
            tokens=["You", "are", "going", "?"],
            pos_tags=["PRP", "VBP", "VBG", "."],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        # Should prioritize punctuation ? -> QUESTION
        meta = detector.detect_meta(analysis)
        assert meta == META.QUESTION

    def test_empty_tokens_meta(self):
        """Test meta detection on empty tokens."""
        detector = METADetector()
        analysis = LinguisticAnalysis(
            tokens=[],
            pos_tags=[],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        meta = detector.detect_meta(analysis)
        # Default to ASSERTIVE or None
        assert meta is None or meta == META.ASSERTIVE

class TestCSCGeneratorErrorHandling:
    """Test error handling in CSCGenerator."""
    
    def test_missing_root_generation(self):
        """Test generation when ROOT is missing (should raise or handle)."""
        generator = CSCGenerator()
        try:
            csc = CSC(root=None, ops=[], roles={})
            result = generator.generate_csc(csc.root, csc.ops, csc.roles, csc.meta)
            assert result is None or result.root is None, "Should handle None ROOT gracefully"
        except (ValueError, TypeError):
            pass

class TestPTILEncoderResilience:
    """Test high-level resilience of the encoder."""
    
    def test_partial_failure_recovery(self):
        """If one component fails, does the pipeline crash or degrade?"""
        encoder = PTILEncoder()
        
        original = encoder.root_mapper.map_predicate
        encoder.root_mapper.map_predicate = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
        try:
            cscs = encoder.encode("The boy runs")
            assert isinstance(cscs, list)
        finally:
            encoder.root_mapper.map_predicate = original

    def test_extreme_recursion_depth(self):
        """Test highly nested sentence structures."""
        encoder = PTILEncoder()
        # excessively nested "that" clauses
        text = "He said that she said that he thought that I knew that..." + ("that it was true " * 20)
        try:
            cscs = encoder.encode(text)
            assert len(cscs) > 0
        except RecursionError:
            pytest.fail("Encoder crashed on recursion depth")
        except Exception as e:
            pytest.fail(f"Encoder failed on deeply nested text with {type(e).__name__}: {e}")

    def test_conflicting_unicode_directionality(self):
        """Test BIDI text attacks."""
        encoder = PTILEncoder()
        # RTL and LTR mixed
        text = "The \u202e esrever \u202c boy."  # "The reverse boy" with override chars
        cscs = encoder.encode(text)
        assert isinstance(cscs, list)
