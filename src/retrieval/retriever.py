import math
import re
from collections import Counter
from typing import List, Dict, Any, Set
from src.utils.sanitizer import safe_log_warning, safe_log_info

# Common English stop words
STOP_WORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}


def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase alphanumeric tokens."""
    if not text:
        return []
    words = re.findall(r"\b[a-zA-Z0-9_-]{2,}\b", text.lower())
    tokens = [w for w in words if w not in STOP_WORDS]
    
    # Generate bigrams for phrase matching
    bigrams = []
    if len(tokens) >= 2:
        for i in range(len(tokens) - 1):
            bigrams.append(f"{tokens[i]}_{tokens[i+1]}")
    return tokens + bigrams


class KnowledgeBaseRetriever:
    """
    High-performance Knowledge Base Retriever using TF-IDF and BM25 principles.
    Provides sub-millisecond retrieval, relevance thresholding, title-weighting,
    and graceful fallback when the knowledge base is empty or queries are vague.
    """

    def __init__(
        self,
        chunks: List[Dict[str, Any]],
        min_relevance_score: float = 0.04
    ):
        self.chunks = chunks or []
        self.min_relevance_score = min_relevance_score
        self.doc_count = len(self.chunks)
        self.doc_tokens: List[List[str]] = []
        self.doc_freqs: Counter = Counter()
        self.doc_lengths: List[int] = []
        self.avg_doc_length: float = 1.0

        if self.chunks:
            total_len = 0
            for chunk in self.chunks:
                # Weight document name and path higher by repeating them
                text = (
                    f"{chunk.get('document', '')} {chunk.get('document', '')} "
                    f"{chunk.get('path', '')} {chunk.get('section', '')} "
                    f"{chunk.get('content', '')}"
                )
                tokens = tokenize(text)
                self.doc_tokens.append(tokens)
                total_len += len(tokens)
                self.doc_lengths.append(len(tokens))

                # Count unique terms in this document for IDF
                unique_terms = set(tokens)
                for term in unique_terms:
                    self.doc_freqs[term] += 1

            self.avg_doc_length = total_len / max(self.doc_count, 1)
            safe_log_info(f"KnowledgeBaseRetriever indexed {self.doc_count} chunks with {len(self.doc_freqs)} terms.")
        else:
            safe_log_info("KnowledgeBaseRetriever initialized with 0 chunks.")

    def _idf(self, term: str) -> float:
        """Compute smooth Inverse Document Frequency."""
        df = self.doc_freqs.get(term, 0)
        if df == 0:
            return 0.0
        return math.log(1.0 + (self.doc_count - df + 0.5) / (df + 0.5))

    def search(
        self,
        query: str,
        top_k: int = 3,
        min_score: float | None = None
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base chunks for query relevance.

        Args:
            query: Ticket subject and body text
            top_k: Maximum number of chunks to return
            min_score: Minimum relevance threshold

        Returns:
            List of matching chunk dictionaries with 'score' attached, sorted by relevance descending.
        """
        threshold = min_score if min_score is not None else self.min_relevance_score

        if not self.chunks or not query or not query.strip():
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        query_tf = Counter(query_tokens)
        query_vector: Dict[str, float] = {}
        for term, count in query_tf.items():
            idf = self._idf(term)
            if idf > 0:
                query_vector[term] = count * idf

        if not query_vector:
            # All query terms are unknown or stop words
            return []

        q_norm = math.sqrt(sum(v * v for v in query_vector.values()))
        if q_norm == 0:
            return []

        # Score documents using cosine similarity on TF-IDF vectors
        scores: List[tuple[int, float]] = []
        k1 = 1.2
        b = 0.75

        for doc_idx, doc_toks in enumerate(self.doc_tokens):
            if not doc_toks:
                continue

            doc_tf = Counter(doc_toks)
            doc_len = self.doc_lengths[doc_idx]
            dot_product = 0.0
            doc_norm_sq = 0.0

            for term, q_weight in query_vector.items():
                if term in doc_tf:
                    # BM25 frequency scaling
                    raw_tf = doc_tf[term]
                    norm_tf = (raw_tf * (k1 + 1.0)) / (raw_tf + k1 * (1.0 - b + b * (doc_len / self.avg_doc_length)))
                    idf = self._idf(term)
                    d_weight = norm_tf * idf
                    dot_product += q_weight * d_weight
                    doc_norm_sq += d_weight * d_weight

            if dot_product > 0:
                doc_norm = math.sqrt(doc_norm_sq) if doc_norm_sq > 0 else 1.0
                cosine_sim = dot_product / (q_norm * doc_norm)
                
                # Check for exact substring match of prominent query words
                chunk_content_lower = self.chunks[doc_idx].get("content", "").lower()
                query_lower = query.lower()
                
                # Bonus for exact key terms
                if any(w in chunk_content_lower for w in query_tokens if len(w) > 4):
                    cosine_sim = min(1.0, cosine_sim * 1.1)

                if cosine_sim >= threshold:
                    scores.append((doc_idx, cosine_sim))

        # Sort descending by score
        scores.sort(key=lambda x: x[1], reverse=True)

        results: List[Dict[str, Any]] = []
        seen_documents: Set[str] = set()

        for doc_idx, score in scores:
            chunk = self.chunks[doc_idx].copy()
            chunk["score"] = round(min(1.0, float(score)), 4)
            results.append(chunk)

            if len(results) >= top_k:
                break

        return results