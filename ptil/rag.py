"""
PTIL RAG - Retrieval-Augmented Generation with semantic compression.

Store documents compressed 80%. Search them without decompressing.
Return original text when found.
"""

import time
import re
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field

from . import PTILEncoder
from .ultra_compact_serializer import UltraCompactCSCSerializer


@dataclass
class Document:
    id: str
    text: str
    compressed: str
    keywords: List[str]
    metadata: Dict = field(default_factory=dict)


class PTILRAG:
    """
    RAG system using PTIL compression + keyword search.
    
    - Store: Compress 80%, extract keywords
    - Search: Match keywords, return original
    - Benefit: Small storage, fast search, original text
    
    Usage:
        rag = PTILRAG()
        rag.add_document("The boy went to school.")
        rag.add_document("She read a book.")
        
        results = rag.search("school")
        for r in results:
            print(r["text"])
    """
    
    def __init__(self):
        self.encoder = PTILEncoder()
        self.ultra = UltraCompactCSCSerializer()
        self.documents: Dict[str, Document] = {}
        self.inverted_index: Dict[str, List[str]] = {}
    
    def add_document(self, text: str, doc_id: str = None, metadata: Dict = None) -> str:
        """Add document to the RAG system."""
        if doc_id is None:
            doc_id = str(len(self.documents))
        
        compressed = self._compress(text)
        keywords = self._extract_keywords(text)
        
        doc = Document(
            id=doc_id,
            text=text,
            compressed=compressed,
            keywords=keywords,
            metadata=metadata or {}
        )
        
        self.documents[doc_id] = doc
        
        for keyword in keywords:
            if keyword not in self.inverted_index:
                self.inverted_index[keyword] = []
            self.inverted_index[keyword].append(doc_id)
        
        return doc_id
    
    def add_documents(self, texts: List[str], metadata: List[Dict] = None) -> List[str]:
        """Add multiple documents."""
        ids = []
        for i, text in enumerate(texts):
            meta = metadata[i] if metadata else None
            doc_id = self.add_document(text, metadata=meta)
            ids.append(doc_id)
        return ids
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search documents using keyword matching."""
        query_keywords = self._extract_keywords(query)
        
        doc_scores = {}
        for keyword in query_keywords:
            if keyword in self.inverted_index:
                for doc_id in self.inverted_index[keyword]:
                    if doc_id not in doc_scores:
                        doc_scores[doc_id] = 0
                    doc_scores[doc_id] += 1
        
        results = []
        for doc_id, score in sorted(doc_scores.items(), key=lambda x: -x[1]):
            doc = self.documents[doc_id]
            results.append({
                "id": doc_id,
                "text": doc.text,
                "score": score / len(query_keywords) if query_keywords else 0,
                "compressed": doc.compressed,
                "metadata": doc.metadata,
            })
        
        return results[:top_k]
    
    def search_with_context(self, query: str, context_window: int = 1) -> List[Dict]:
        """Search and return surrounding documents for context."""
        results = self.search(query, top_k=1)
        
        if not results:
            return []
        
        doc_ids = list(self.documents.keys())
        matched_idx = doc_ids.index(results[0]["id"])
        
        start = max(0, matched_idx - context_window)
        end = min(len(doc_ids), matched_idx + context_window + 1)
        
        context_docs = []
        for i in range(start, end):
            doc = self.documents[doc_ids[i]]
            context_docs.append({
                "id": doc.id,
                "text": doc.text,
                "compressed": doc.compressed,
                "is_match": i == matched_idx,
                "metadata": doc.metadata,
            })
        
        return context_docs
    
    def get_stats(self) -> Dict:
        """Get RAG system statistics."""
        total_original = sum(len(d.text.encode("utf-8")) for d in self.documents.values())
        total_compressed = sum(len(d.compressed.encode("utf-8")) for d in self.documents.values())
        
        return {
            "total_documents": len(self.documents),
            "total_original_bytes": total_original,
            "total_compressed_bytes": total_compressed,
            "compression_ratio": total_compressed / total_original if total_original > 0 else 0,
            "reduction_pct": (1 - total_compressed / total_original) * 100 if total_original > 0 else 0,
        }
    
    def _compress(self, text: str) -> str:
        """Compress text using PTIL."""
        cscs = self.encoder.encode(text)
        return self.ultra.serialize_multiple(cscs)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
                       "have", "has", "had", "do", "does", "did", "will", "would", "could",
                       "should", "may", "might", "can", "shall", "to", "of", "in", "for",
                       "on", "with", "at", "by", "from", "as", "into", "through", "during",
                       "before", "after", "above", "below", "between", "out", "off", "over",
                       "under", "again", "further", "then", "once", "here", "there", "when",
                       "where", "why", "how", "all", "both", "each", "few", "more", "most",
                       "other", "some", "such", "no", "nor", "not", "only", "own", "same",
                       "so", "than", "too", "very", "s", "t", "just", "don", "now"}
        
        words = re.findall(r'\w+', text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return keywords
    
    def export_index(self, path: str):
        """Export index to JSON."""
        data = {
            "documents": {
                doc_id: {
                    "text": doc.text,
                    "compressed": doc.compressed,
                    "keywords": doc.keywords,
                    "metadata": doc.metadata,
                }
                for doc_id, doc in self.documents.items()
            }
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    
    def import_index(self, path: str):
        """Import index from JSON."""
        with open(path, "r") as f:
            data = json.load(f)
        
        for doc_id, doc_data in data["documents"].items():
            doc = Document(
                id=doc_id,
                text=doc_data["text"],
                compressed=doc_data["compressed"],
                keywords=doc_data.get("keywords", []),
                metadata=doc_data.get("metadata", {}),
            )
            self.documents[doc_id] = doc
            for keyword in doc.keywords:
                if keyword not in self.inverted_index:
                    self.inverted_index[keyword] = []
                self.inverted_index[keyword].append(doc_id)
