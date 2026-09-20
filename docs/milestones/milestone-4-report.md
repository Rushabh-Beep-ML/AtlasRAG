# Milestone 4 — Core Implementation & Ingestion Pipeline

## 1. Objective
Milestone 4 translates the M3 architectural designs into an operational document ingestion and knowledge-preparation foundation for AtlasRAG, establishing structured document loading, normalization, metadata extraction, language identification, and chunking.

## 2. Implemented Pipeline
The operational data flow follows this sequence:
Raw Documents → Document Loading → Parsing → Text Normalization → Metadata Extraction → Language Identification → Configurable Chunking → Validation → Embedding Preparation / Future Index Preparation

* **Implemented Components**: Document loader (PDF, TXT, MD, HTML), Unicode NFC normalizer, Pydantic metadata engine with SHA-256 hashing, language detector wrapper (`langdetect`), and word-level configurable chunker.
* **Reserved Components (Future Milestones)**: Dense vector embedding generation (`BAAI/bge-m3`), Qdrant vector indexing, BM25 sparse indexing, Reciprocal Rank Fusion (RRF), and cross-encoder reranking.

## 3. Document Loading
* **Supported Formats**: PDF (via PyMuPDF), Plain Text (`.txt`, `.md`), and HTML (`.html`, `.htm`).
* **PDF Page Preservation**: Extracted page-by-page via `fitz`, preserving page numbers and section boundaries into structured `DocumentPage` objects.
* **Error & Edge Handling**: Gracefully catches missing files, empty files, and unsupported formats, returning structured error dictionaries (`success: False`).
* **DOCX Scope**: Microsoft Word (`.docx`) is not currently implemented as it is outside the required M3 ingestion scope.

## 4. Text Normalization
* **Unicode Normalization**: Applies Unicode Normalization Form C (NFC) for consistent representation of multilingual scripts.
* **Whitespace & Control Characters**: Sanitizes anomalous control characters while preserving structural spacing, collapsing excessive newlines, and normalizing horizontal spacing.
* **Multilingual Preservation**: Preserves English, Hindi, and Marathi characters natively without performing any automated machine translation.

## 5. Metadata & Provenance
Implements the authoritative 18-field Pydantic metadata schema (`ChunkMetadata`).
* **Deterministic Identifiers**: Generates deterministic SHA-256 `document_id` (from title and source URL) and `content_hash` (from chunk text).
* **Chunk IDs**: Formatted as `{document_id}_chunk_{chunk_index:04d}`.
* **Provenance & Fallbacks**: Inherits parent metadata across chunks, binds page and section ranges, and applies `None` defaults for unprovided fields.

## 6. Language Identification
* **Implementation**: Wraps `langdetect` to identify document and chunk languages (`en`, `hi`, `mr`) with probability confidence scoring.
* **Fallbacks**: Returns `(None, None)` for inputs shorter than 10 characters or upon encountering detection exceptions. Universal coverage is not claimed.

## 7. Chunking
> **Important Note**: The current M4 implementation uses a configurable word-level sliding-window approximation of the M3 512-token / 64-token baseline. It is not a true subword-tokenizer implementation.

* **Evaluation**: Tokenizer-integrated subword chunking will be evaluated and integrated during Milestone 5 when the embedding encoder is initialized. Default parameters are baseline configurations, not experimentally optimized optima.

## 8. Testing
* **Test Suite**: Implemented in `tests/test_ingestion.py`.
* **Execution Result**: **6 tests passed.**
* **Command**:
  ```powershell
  $env:PYTHONPATH = (Get-Location).Path
  pytest -v

## 9. Dependencies
Defined in pyproject.toml:

Runtime: pydantic>=2.0.0, pymupdf>=1.23.0, langdetect>=1.0.9.

Development: pytest>=7.0.0, black>=23.0.0, ruff>=0.1.0.

Python Requirement: >=3.10.

## 10. M3 Contract Compliance
Reconciliation against M3 specifications confirmed:

Zero missing metadata fields.

Zero semantic metadata deviations.

DOCX absence is fully aligned with M3 scope.

Word-level chunking is formally clarified as an interim implementation.

## 11. Research Integrity
Designed: M3 architecture and baseline specifications.

Implemented: M4 ingestion pipeline components.

Validated: Only behaviors covered by the executed unit test suite.

Excluded Claims: No claims of optimal performance, production readiness, empirical superiority, complete multilingual coverage, zero hallucination, or retrieval quality validation are made.

## 12. M4 Limitations
Word-level chunking approximation.

Limited current unit test coverage breadth.

DOCX format unsupported.

Dense/sparse embedding and indexing remain future work.