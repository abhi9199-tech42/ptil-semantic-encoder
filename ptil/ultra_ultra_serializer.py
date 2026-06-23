"""
Ultra-Ultra Compact CSC Serializer - Maximum compression using enumeration.

Takes ultra-compact output and compresses further using:
- Dots for repeated ROOT/OPS patterns
- Numbers for common role sequences
- Short codes for frequent combinations
"""

from typing import List, Dict
from .models import CSC, ROOT, Operator, Role, META


class UltraUltraCompactSerializer:
    """
    Maximum compression by enumerating common ultra-compact patterns.
    
    Takes ultra-compact output like "1FNWaboygschomtmrw" and compresses to:
    - Dots for repeated ROOT patterns
    - Numbers for common role sequences
    - Short codes for frequent combinations
    """
    
    def __init__(self):
        """Initialize with pattern dictionaries."""
        # Common ultra-compact patterns -> short codes
        self.pattern_map = {
            # Common full patterns
            "0Plm": "0.",
            "0Plmat": "0M",
            "0R": "0R",
            "1PWabgs": "1S",
            "1FNabgs": "1N",
            "2Pateachtassi": "2T",
            "3RMasheplang": "3C",
            "4Pashetbook": "4B",
            "5PWahe": "5A",
            "6RWahe": "6A",
            "7Ptt": "7D",
            "8PWIacompgmark": "8M",
            "9Rla": "9P",
            "ARWatheyttripgparimsumr": "IT",
            "CRWZmqrt": "DQ",
            "IROaforetrainmwknd": "EW",
            "YROahetprojmfri": "SF",
        }
        
        # Role sequence patterns -> short codes
        self.role_sequences = {
            "aboygschomtmrw": "1",
            "aboygscho": "2",
            "ashebook": "3",
            "asheplang": "4",
            "aheprojmfri": "5",
            "atheyttripgparimsumr": "6",
            "ateachtassi": "7",
            "acompgmark": "8",
            "aforetrainmwknd": "9",
            "achldlparkmscho": "A",
            "adoctpati": "B",
            "ashe": "C",
            "awe": "D",
            "acomp": "E",
            "amat": "F",
        }
        
        # OPS patterns -> short codes
        self.ops_patterns = {
            "FNW": "f",  # FUTURE+NEGATION+TOWARD
            "PW": "p",   # PAST+TOWARD
            "RW": "r",   # PRESENT+TOWARD
            "RO": "o",   # PRESENT+OBLIGATORY
            "RM": "m",   # PRESENT+POSSIBLE
            "P": "a",    # PAST
            "R": "b",    # PRESENT
            "F": "c",    # FUTURE
            "PWI": "d",  # PAST+TOWARD+DIRECTION_IN
            "CRWZ": "e", # DESIRE+PRESENT+TOWARD+AWAY
        }
        
        # Reverse mappings for decompression
        self.short_to_pattern = {v: k for k, v in self.pattern_map.items()}
        self.short_to_role = {v: k for k, v in self.role_sequences.items()}
        self.short_to_ops = {v: k for k, v in self.ops_patterns.items()}
    
    def compress(self, ultra_compact: str) -> str:
        """
        Compress ultra-compact output to ultra-ultra compact.
        
        Args:
            ultra_compact: Ultra-compact string like "1FNWaboygschomtmrw"
            
        Returns:
            str: Ultra-ultra compact string like "1N"
        """
        if not ultra_compact:
            return ""
        
        # Check if full pattern matches
        if ultra_compact in self.pattern_map:
            return self.pattern_map[ultra_compact]
        
        # Try to compress by parts
        parts = ultra_compact.split()
        compressed_parts = []
        
        for part in parts:
            if part in self.pattern_map:
                compressed_parts.append(self.pattern_map[part])
            else:
                # Try to compress the role sequence
                compressed = self._compress_roles(part)
                compressed_parts.append(compressed)
        
        return " ".join(compressed_parts)
    
    def decompress(self, ultra_ultra: str) -> str:
        """
        Decompress ultra-ultra compact back to ultra-compact.
        
        Args:
            ultra_ultra: Ultra-ultra compact string
            
        Returns:
            str: Ultra-compact string
        """
        if not ultra_ultra:
            return ""
        
        # Check if it's a full pattern
        if ultra_ultra in self.short_to_pattern:
            return self.short_to_pattern[ultra_ultra]
        
        # Try to decompress by parts
        parts = ultra_ultra.split()
        decompressed_parts = []
        
        for part in parts:
            if part in self.short_to_pattern:
                decompressed_parts.append(self.short_to_pattern[part])
            else:
                # Try to decompress the role sequence
                decompressed = self._decompress_roles(part)
                decompressed_parts.append(decompressed)
        
        return " ".join(decompressed_parts)
    
    def _compress_roles(self, ultra_part: str) -> str:
        """Compress role sequence in ultra-compact part."""
        # Try to match role sequences
        for role_seq, short in self.role_sequences.items():
            if role_seq in ultra_part:
                compressed = ultra_part.replace(role_seq, short)
                return compressed
        
        # Try to compress OPS
        for ops, short in self.ops_patterns.items():
            if ops in ultra_part:
                compressed = ultra_part.replace(ops, short)
                return compressed
        
        # No compression possible, return as-is (lossless passthrough)
        return ultra_part
    
    def _decompress_roles(self, ultra_ultra_part: str) -> str:
        """Decompress role sequence in ultra-ultra compact part."""
        # Try to decompress role sequences
        for short, role_seq in self.short_to_role.items():
            if ultra_ultra_part.startswith(short):
                return ultra_ultra_part.replace(short, role_seq, 1)
        
        # Try to decompress OPS
        for short, ops in self.short_to_ops.items():
            if ultra_ultra_part.startswith(short):
                return ultra_ultra_part.replace(short, ops, 1)
        
        return ultra_ultra_part
    
    def serialize(self, csc: CSC) -> str:
        """Serialize CSC to ultra-ultra compact format."""
        # First get ultra-compact
        from .ultra_compact_serializer import UltraCompactCSCSerializer
        ultra = UltraCompactCSCSerializer()
        ultra_code = ultra.serialize(csc)
        
        # Then compress further
        return self.compress(ultra_code)
    
    def serialize_multiple(self, csc_list: List[CSC]) -> str:
        """Serialize multiple CSCs to ultra-ultra compact format."""
        if not csc_list:
            return ""
        
        codes = []
        for csc in csc_list:
            code = self.serialize(csc)
            if code:
                codes.append(code)
        
        return " ".join(codes)
    
    def get_compression_stats(self, ultra_compact: str, ultra_ultra: str) -> Dict:
        """Get compression statistics."""
        return {
            "ultra_length": len(ultra_compact),
            "ultra_ultra_length": len(ultra_ultra),
            "compression_ratio": len(ultra_compact) / len(ultra_ultra) if ultra_ultra else 0,
            "bytes_saved": len(ultra_compact) - len(ultra_ultra),
        }
