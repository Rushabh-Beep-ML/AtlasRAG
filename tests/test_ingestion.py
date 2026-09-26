"""
Unit Test Suite for AtlasRAG Ingestion Pipeline.
Validates normalization, deterministic hashing, language identification,
document loading edge cases, and chunk provenance binding.
"""

import pytest
from src.ingestion.normalizer import TextNormalizer
from src.ingestion.metadata import MetadataEngine, ChunkMetadata
from src.ingestion.language import LanguageDetector
from src.ingestion.loader import DocumentLoader, DocumentPage
from src.ingestion.chunker import ConfigurableChunker


def test_text_normalizer_unicode_and_whitespace():
    """Test Unicode NFC normalization and whitespace sanitation."""
    raw_text = "  Emergency   Flood\n\nResponse   \r\nProtocol\t\t2026. "
    normalized = TextNormalizer.normalize(raw_text)
    
    assert "Emergency Flood" in normalized
    assert "Response\nProtocol 2026." in normalized
    assert TextNormalizer.normalize(None) == ""
    assert TextNormalizer.normalize("") == ""


def test_deterministic_metadata_hashing():
    """Test deterministic document_id and content_hash generation via SHA-256."""
    title = "Flood Evacuation SOP"
    source = "https://example.org/sop.pdf"
    
    doc_id_1 = MetadataEngine.generate_document_id(title, source)
    doc_id_2 = MetadataEngine.generate_document_id(title, source)
    
    # Must be deterministic and 64 hex characters (SHA-256)
    assert doc_id_1 == doc_id_2
    assert len(doc_id_1) == 64

    text_content = "Immediate relocation required for Sector 4."
    c_hash = MetadataEngine.generate_content_hash(text_content)
    assert len(c_hash) == 64


def test_metadata_null_fallback_rules():
    """Test that unprovided metadata fields correctly default to null (None)."""
    meta = MetadataEngine.build_metadata(
        document_id="dummy_doc_id",
        chunk_index=0,
        chunk_text="Test disaster response text."
    )
    
    assert meta.document_id == "dummy_doc_id"
    assert meta.chunk_index == 0
    assert meta.title is None
    assert meta.source_url is None
    assert meta.organization is None
    assert meta.language_confidence is None


def test_language_detector_fallback():
    """Test language detection with supported languages and insufficient text."""
    # English text
    lang_en, conf_en = LanguageDetector.detect("Emergency evacuation procedures must be followed strictly by all units.")
    assert lang_en == "en"
    assert conf_en is not None

    # Insufficient text should gracefully return (None, None)
    lang_none, conf_none = LanguageDetector.detect("abc")
    assert lang_none is None
    assert conf_none is None


def test_document_loader_missing_file():
    """Test document loader handling of non-existent files."""
    result = DocumentLoader.load_document("non_existent_file_999.pdf")
    assert result["success"] is False
    assert result["error"] == "File not found"
    assert result["pages"] == []


def test_configurable_chunker_provenance():
    """Test that the chunker generates valid chunks with inherited provenance metadata."""
    mock_parsed_doc = {
        "success": True,
        "file_name": "test_flood_doc.pdf",
        "total_pages": 1,
        "pages": [
            DocumentPage(
                page_number=1,
                text="Heavy rainfall has triggered severe flooding in district alpha. Immediate rescue teams deployed.",
                section="1.0 Overview"
            )
        ],
        "error": None
    }

    raw_metadata = {
        "title": "District Alpha Flood Report",
        "source_url": "https://example.org/report.pdf",
        "disaster_type": "flood",
        "location": "District Alpha"
    }

    chunker = ConfigurableChunker(chunk_size=50, chunk_overlap=10)
    chunks = chunker.chunk_document(mock_parsed_doc, raw_metadata=raw_metadata)

    assert len(chunks) > 0
    for idx, chunk in enumerate(chunks):
        assert isinstance(chunk, ChunkMetadata)
        assert chunk.chunk_index == idx
        assert chunk.document_id is not None
        assert chunk.chunk_id.endswith(f"chunk_{idx:04d}")
        assert chunk.disaster_type == "flood"
        assert chunk.page_start == 1
        assert chunk.section == "1.0 Overview"
        assert chunk.content_hash is not None