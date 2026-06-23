"""
Ultra-Compact CSC Serializer for PTIL semantic encoder.

This module provides maximum compression to achieve 80% token reduction
through aggressive optimization while maintaining semantic completeness.
"""

from typing import List, Dict, Set
from .models import CSC, ROOT, Operator, Role, META


class UltraCompactCSCSerializer:
    """
    Ultra-compact serializer achieving maximum token efficiency.
    
    Uses single-character codes, eliminates redundancy, and applies
    aggressive compression to reach 80% token reduction target.
    """
    
    def __init__(self):
        """Initialize with ultra-compact encoding mappings."""
        # ROOT mappings - single chars (digits, uppercase, symbols)
        self.root_codes = {
            ROOT.MOTION: "1",
            ROOT.TRANSFER: "2",
            ROOT.COMMUNICATION: "3",
            ROOT.COGNITION: "4",
            ROOT.PERCEPTION: "5",
            ROOT.CREATION: "6",
            ROOT.DESTRUCTION: "7",
            ROOT.CHANGE: "8",
            ROOT.POSSESSION: "9",
            ROOT.INTENTION: "A",
            ROOT.EXISTENCE: "0",
            ROOT.EMOTION: "B",
            ROOT.DESIRE: "C",
            ROOT.PREFERENCE: "D",
            ROOT.JOY: "E",
            ROOT.SADNESS: "F",
            ROOT.ANGER: "G",
            ROOT.FEAR: "H",
            ROOT.EVALUATION: "I",
            ROOT.COMPARISON: "J",
            ROOT.JUDGMENT: "K",
            ROOT.APPROVAL: "L",
            ROOT.CRITICISM: "M",
            ROOT.SOCIAL: "N",
            ROOT.COOPERATION: "O",
            ROOT.CONFLICT: "P",
            ROOT.AGREEMENT: "Q",
            ROOT.PROMISE: "R",
            ROOT.THREAT: "S",
            ROOT.REQUEST: "T",
            ROOT.CAUSATION: "U",
            ROOT.PREVENTION: "V",
            ROOT.ENABLEMENT: "W",
            ROOT.ATTEMPT: "X",
            ROOT.SUCCESS: "Y",
            ROOT.FAILURE: "Z",
            ROOT.ANALYSIS: "!",
            ROOT.MEMORY: "@",
            ROOT.LEARNING: "#",
            ROOT.TEACHING: "$",
            ROOT.DECISION: "%",
            ROOT.BELIEF: "^",
            ROOT.STATE: "&",
            ROOT.PROPERTY: "*",
            ROOT.QUANTITY: "(",
            ROOT.TIME_RELATION: ")",
            ROOT.LOCATION_STATE: "-",
            ROOT.EXPERIENCE: "+",
            ROOT.ASSISTANCE: "[",
            ROOT.TRAVEL: "]",
            ROOT.CAUSE_EFFECT: "{",
            ROOT.ACTION: "}",
            ROOT.CONSUMPTION: "<",
            ROOT.REFUSAL: ">",
        }
        
        # Operator mappings - single characters (hex-like)
        self.operator_codes = {
            # Temporal (most common first)
            Operator.FUTURE: "F",
            Operator.PAST: "P", 
            Operator.PRESENT: "R",
            # Polarity (very common)
            Operator.NEGATION: "N",
            Operator.AFFIRMATION: "Y",
            # Aspect
            Operator.CONTINUOUS: "C",
            Operator.COMPLETED: "D",
            Operator.HABITUAL: "H",
            # Modality
            Operator.POSSIBLE: "M",
            Operator.NECESSARY: "E",
            Operator.OBLIGATORY: "O",
            Operator.PERMITTED: "T",
            # Causation
            Operator.CAUSATIVE: "U",
            Operator.SELF_INITIATED: "S",
            Operator.FORCED: "G",
            # Direction
            Operator.DIRECTION_IN: "I",
            Operator.DIRECTION_OUT: "J",
            Operator.TOWARD: "W",
            Operator.AWAY: "Z"
        }
        
        # Role mappings - single letters (most common first)
        self.role_codes = {
            Role.AGENT: "a",
            Role.THEME: "t",
            Role.GOAL: "g",
            Role.LOCATION: "l",
            Role.TIME: "m",
            Role.SOURCE: "s",
            Role.PATIENT: "p",
            Role.INSTRUMENT: "i",
            Role.EXPERIENCER: "e",
            Role.STIMULUS: "u",
            Role.STANDARD: "d",
            Role.VERDICT: "v",
            Role.RESULT: "r",
            Role.PATH: "h",
            Role.ATTRIBUTE: "b",
            Role.VALUE: "w",
            Role.COMPARISON: "c",
            Role.CONTENT: "n",
            Role.MANNER: "y",
        }
        
        # META mappings - single digits (most common first)
        self.meta_codes = {
            META.ASSERTIVE: "",   # Most common - omit entirely!
            META.QUESTION: "?",   # Natural symbol
            META.COMMAND: "!",    # Natural symbol
            META.UNCERTAIN: "~",  # Tilde for uncertainty
            META.EVIDENTIAL: "^", # Caret for evidence
            META.EMOTIVE: "*",    # Star for emotion
            META.IRONIC: "#"      # Hash for irony
        }
        
        # Ultra-aggressive entity compression dictionary
        self.entity_dict = self._build_entity_dictionary()
        
        # Create reverse mappings
        self.code_to_root = {v: k for k, v in self.root_codes.items()}
        self.code_to_operator = {v: k for k, v in self.operator_codes.items()}
        self.code_to_role = {v: k for k, v in self.role_codes.items()}
        self.code_to_meta = {v: k for k, v in self.meta_codes.items() if v}  # Skip empty
    
    def _build_entity_dictionary(self) -> Dict[str, str]:
        """Build ultra-compact entity dictionary."""
        return {
            # Remove articles entirely
            "the": "",
            "a": "",
            "an": "",
            "this": "",
            "that": "",
            
            # People - single letters
            "boy": "b",
            "girl": "g",
            "man": "m", 
            "woman": "w",
            "child": "c",
            "person": "p",
            "student": "s",
            "teacher": "t",
            "he": "h",
            "she": "s",
            "they": "t",
            "we": "w",
            "i": "i",
            "you": "u",
            
            # Places - single letters
            "school": "s",
            "house": "h",
            "home": "h",
            "library": "l",
            "park": "p",
            "store": "s",
            "office": "o",
            "room": "r",
            "kitchen": "k",
            "bedroom": "b",
            
            # Objects - single letters
            "book": "b",
            "car": "c",
            "phone": "p",
            "computer": "c",
            "table": "t",
            "chair": "c",
            "door": "d",
            "window": "w",
            "mat": "m",
            "cat": "c",
            "dog": "d",
            
            # Time - single letters
            "tomorrow": "T",
            "yesterday": "Y", 
            "today": "D",
            "morning": "M",
            "evening": "E",
            "night": "N",
            "day": "D",
            "week": "W",
            "month": "M",
            "year": "Y",
            
            # Actions (usually captured in ROOT, but for entities)
            "work": "w",
            "project": "p",
            "task": "t",
            "job": "j",
            "meeting": "m",
            "class": "c",
            "lesson": "l",
            
            # Remove auxiliary/modal verbs (captured in OPS)
            "will": "",
            "would": "",
            "should": "",
            "could": "",
            "might": "",
            "must": "",
            "have": "",
            "has": "",
            "had": "",
            "been": "",
            "being": "",
            "is": "",
            "are": "",
            "was": "",
            "were": "",
            "not": "",  # Captured in negation operator
            
            # Prepositions (often redundant with roles)
            "to": "",
            "in": "",
            "on": "",
            "at": "",
            "from": "",
            "with": "",
            "by": "",
            "for": "",
            
            # Common adjectives - first letter
            "big": "b",
            "small": "s",
            "good": "g",
            "bad": "b",
            "new": "n",
            "old": "o",
            "fast": "f",
            "slow": "s",
            "hot": "h",
            "cold": "c",
        }
    
    def serialize(self, csc: CSC) -> str:
        """
        Serialize CSC to ultra-compact format.
        
        Format: 1FNagsl?
        - ROOT: single digit/letter (1)
        - OPS: concatenated single chars (FN = FUTURE+NEGATION)
        - ROLES: role+entity pairs (a=agent:boy, g=goal:school, l=location, m=time)
        - META: single symbol (? for question, ! for command, empty for assertive)
        
        Args:
            csc: CSC structure to serialize
            
        Returns:
            str: Ultra-compact serialized CSC
        """
        if csc is None:
            raise ValueError("CSC cannot be None")
        
        result = ""
        
        # 1. ROOT (mandatory) - single character
        if csc.root is None:
            raise ValueError("ROOT component is mandatory")
        
        root_code = self.root_codes.get(csc.root)
        if root_code is None:
            raise ValueError(f"Unknown ROOT: {csc.root}")
        result += root_code
        
        # 2. OPS (if present) - concatenated single characters
        if csc.ops:
            for op in csc.ops:
                op_code = self.operator_codes.get(op)
                if op_code is None:
                    raise ValueError(f"Unknown operator: {op}")
                result += op_code
        
        # 3. ROLES (if present) - role letter + compressed entity
        if csc.roles:
            # Sort roles for consistency, prioritize common ones
            role_priority = {
                Role.AGENT: 0,
                Role.THEME: 1,
                Role.GOAL: 2,
                Role.LOCATION: 3,
                Role.TIME: 4,
                Role.SOURCE: 5,
                Role.PATIENT: 6,
                Role.INSTRUMENT: 7,
                Role.EXPERIENCER: 8,
                Role.STIMULUS: 9,
                Role.STANDARD: 10,
                Role.VERDICT: 11,
                Role.RESULT: 12,
                Role.PATH: 13,
                Role.ATTRIBUTE: 14,
                Role.VALUE: 15,
                Role.COMPARISON: 16,
                Role.CONTENT: 17,
                Role.MANNER: 18,
            }
            
            sorted_roles = sorted(
                csc.roles.items(), 
                key=lambda x: role_priority.get(x[0], 99)
            )
            
            for role, entity in sorted_roles:
                role_code = self.role_codes.get(role)
                if role_code is None:
                    raise ValueError(f"Unknown role: {role}")
                
                # Ultra-compress entity
                entity_compressed = self._ultra_compress_entity(entity.normalized)
                if entity_compressed:  # Only add if not empty
                    result += role_code + entity_compressed
        
        # 4. META (if present and not assertive) - single symbol
        if csc.meta is not None and csc.meta != META.ASSERTIVE:
            meta_code = self.meta_codes.get(csc.meta)
            if meta_code is None:
                raise ValueError(f"Unknown META: {csc.meta}")
            result += meta_code
        
        return result
    
    def serialize_multiple(self, csc_list: List[CSC]) -> str:
        """
        Serialize multiple CSCs with minimal separation.
        
        Args:
            csc_list: List of CSC structures
            
        Returns:
            str: Ultra-compact serialized CSCs
        """
        if not csc_list:
            return ""
        
        # For multiple CSCs, use minimal separator
        serialized_cscs = []
        for csc in csc_list:
            serialized = self.serialize(csc)
            if serialized:
                serialized_cscs.append(serialized)
        
        # Use single space as separator (minimal)
        return " ".join(serialized_cscs)
    
    def _ultra_compress_entity(self, entity_text: str) -> str:
        """
        Compress entity text keeping meaning readable.
        Preserves time, objects, and names that explain the sentence.
        
        Args:
            entity_text: Original entity text
            
        Returns:
            str: Compressed entity (3-4 chars, readable)
        """
        if not entity_text:
            return ""
        
        text = entity_text.lower().strip()
        
        # Time words - keep readable
        time_words = {
            "tomorrow": "tmrw",
            "yesterday": "yest",
            "today": "tday",
            "morning": "morn",
            "evening": "eve",
            "night": "nite",
            "monday": "mon",
            "tuesday": "tue",
            "wednesday": "wed",
            "thursday": "thu",
            "friday": "fri",
            "saturday": "sat",
            "sunday": "sun",
            "next week": "nwk",
            "last week": "lwk",
            "next month": "nmo",
            "last month": "lmo",
            "next year": "nyr",
            "last year": "lyr",
            "now": "now",
            "soon": "soon",
            "later": "later",
            "before": "befor",
            "after": "after",
            "quarter": "qrt",
            "summer": "sumr",
            "winter": "wint",
            "spring": "spr",
            "autumn": "autm",
            "weekend": "wknd",
            "week": "wk",
            "month": "mo",
            "year": "yr",
            "day": "day",
            "hour": "hr",
        }
        
        # Object words - keep readable
        object_words = {
            "phone": "phon",
            "laptop": "lapt",
            "computer": "comp",
            "book": "book",
            "car": "car",
            "house": "house",
            "school": "scho",
            "office": "offi",
            "store": "stor",
            "park": "park",
            "mat": "mat",
            "cat": "cat",
            "dog": "dog",
            "boy": "boy",
            "girl": "girl",
            "man": "man",
            "woman": "womn",
            "child": "chld",
            "student": "stdnt",
            "teacher": "teach",
            "doctor": "doc",
            "order": "ordr",
            "package": "pkg",
            "product": "prod",
            "password": "pass",
            "account": "acct",
            "manager": "mgr",
            "discount": "disc",
            "refund": "refnd",
            "policy": "poly",
            "weather": "wthr",
            "rain": "rain",
            "snow": "snow",
        }
        
        # Check time words first
        if text in time_words:
            return time_words[text]
        
        # Check object words
        if text in object_words:
            return object_words[text]
        
        # Remove articles/determiners
        words_to_remove = {"the", "a", "an", "this", "that", "is", "are", "was", "were", "has", "have", "had", "all", "by", "to", "in", "on", "at", "from", "with"}
        words = text.split()
        filtered = [w for w in words if w not in words_to_remove]
        
        if not filtered:
            return ""
        
        # Compress each word to first 3-4 chars
        compressed_parts = []
        for word in filtered:
            if word in time_words:
                compressed_parts.append(time_words[word])
            elif word in object_words:
                compressed_parts.append(object_words[word])
            elif len(word) <= 3:
                compressed_parts.append(word)
            else:
                compressed_parts.append(word[:4])
        
        result = "".join(compressed_parts)
        
        # Limit to 4 characters
        return result[:4] if result else ""
    
    def estimate_compression_ratio(self, original_text: str, ultra_compact: str) -> float:
        """
        Estimate compression ratio for ultra-compact format.
        
        Args:
            original_text: Original text
            ultra_compact: Ultra-compact serialized format
            
        Returns:
            float: Compression ratio
        """
        if not ultra_compact:
            return 1.0
        
        # Simulate tokenization
        original_tokens = len(original_text.split())
        compact_tokens = max(1, len(ultra_compact) // 3)  # Very aggressive estimate
        
        return original_tokens / compact_tokens
    
    def get_format_description(self) -> str:
        """Get description of ultra-compact format."""
        return """
Ultra-Compact CSC Format:
- ROOT: Single digit/letter (1=MOTION, 0=EXISTENCE, etc.)
- OPS: Concatenated letters (FN=FUTURE+NEGATION, P=PAST, etc.)
- ROLES: role+entity (ab=agent:boy, gs=goal:school, etc.)
- META: Symbol (?=question, !=command, empty=assertive)

Examples:
- "1FNabgs" = MOTION + FUTURE+NEGATION + agent:boy + goal:school
- "0Rtb?" = EXISTENCE + PRESENT + theme:book + QUESTION
- "4Paw" = COGNITION + PAST + agent:woman

Target: 80%+ token reduction through maximum compression.
"""
    
    def validate_ultra_compact_format(self, serialized: str) -> bool:
        """
        Validate ultra-compact format.
        
        Args:
            serialized: Ultra-compact serialized string
            
        Returns:
            bool: True if valid format
        """
        if not serialized or not serialized.strip():
            return False
        
        # Should not contain verbose format markers
        if any(char in serialized for char in ["<", ">", "=", "|"]):
            return False
        
        # Should start with ROOT code
        valid_starts = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()-+[]{}<>"
        if serialized[0] not in valid_starts:
            return False
        
        return True