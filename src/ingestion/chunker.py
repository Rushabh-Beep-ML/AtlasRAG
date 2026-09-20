"""
Configurable Semantic & Token Chunker Module for AtlasRAG Ingestion Pipeline.
Implements recursive text chunking with configurable target chunk size and overlap,
ensuring end-to-end inheritance of provenance metadata.
"""

import logging
from typing import List, Dict, Any, Optional
from src.ingestion.normalizer import TextNormalizer
from src.ingestion.metadata import MetadataEngine, ChunkMetadata
from src.ingestion.language import LanguageDetector

logger = logging.getLogger(__name__)


class ConfigurableChunker:
    """
    Splits document pages into text chunks adhering to baseline configuration parameters
    (default: 512 tokens target size, 64-token overlap) while binding precise provenance.
    """

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64):
        """
        Initializes the chunker with configurable parameters.
        Note: 512/64 are M3 baseline configurable values, NOT experimentally optimized optima.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _approximate_token_split(self, text: str) -> List[str]:
        """
        Splits text into chunks based on whitespace/character approximations or sentence boundaries.
        A robust production implementation can utilize tiktoken or HuggingFace tokenizers;
        here we use a clean character/word-level sliding window approximation to avoid heavy dependency lock-in.
        """
        if not text:
            return []

        # Simple whitespace tokenization approximation (1 token ~= 4 chars or 1 word)
        words = text.split()
        if not words:
            return []

        chunks = []
        # Approximate words per chunk (assuming average word is ~5 chars, 512 tokens ~ 400 words)
        # For precision control, we use word-based sliding window:
        words_per_chunk = max(50, int(self.chunk_size * 0.75))
        overlap_words = max(5, int(self.chunk_overlap * 0.75))

        start = 0
        while start < len(words):
            end = start + words_per_chunk
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            if chunk_text.strip():
                chunks.append(chunk_text)
            
            if end >= len(words):
                break
            start += (words_per_chunk - overlap_words)

        return chunks

    def chunk_document(
        self,
        parsed_doc: Dict[str, Any],
        raw_metadata: Optional[Dict[str, Any]] = None
    ) -> List[ChunkMetadata]:
        """
        Processes a loaded document (containing pages) and produces a list of fully validated
        ChunkMetadata objects ready for dense and sparse index preparation.
        """
        if not parsed_doc.get("success", False):
            logger.warning("Attempted to chunk an unsuccessful or empty document parse result.")
            return []

        raw_metadata = raw_metadata or {}
        file_name = parsed_doc.get("file_name", "unknown_source")
        title = raw_metadata.get("title", file_name)
        source_identifier = raw_metadata.get("source_url", file_name)

        # Generate deterministic document_id
        document_id = MetadataEngine.generate_document_id(title, source_identifier)

        all_chunks: List[ChunkMetadata] = []
        global_chunk_index = 0

        pages = parsed_doc.get("pages", [])
        for page in pages:
            normalized_page_text = TextNormalizer.normalize(page.text)
            if not normalized_page_text:
                continue

            page_number = page.page_number
            section = page.section

            # Split page text into chunks
            text_segments = self._approximate_token_split(normalized_page_text)

            for segment in text_segments:
                # Detect language for the chunk
                lang, conf = LanguageDetector.detect(segment)

                # Build validated metadata matching M3 schema
                chunk_meta = MetadataEngine.build_metadata(
                    document_id=document_id,
                    chunk_index=global_chunk_index,
                    chunk_text=segment,
                    raw_metadata=raw_metadata,
                    language=lang,
                    language_confidence=conf,
                    page_start=page_number,
                    page_end=page_number,
                    section=section
                )

                all_chunks.append(chunk_meta)
                global_chunk_index += 1

        logger.info(f"Successfully chunked document '{title}': generated {len(all_chunks)} chunks.")
        return all_chunks