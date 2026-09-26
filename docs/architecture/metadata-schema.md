# Metadata Schema & Provenance Architecture: AtlasRAG

## 1. Architectural Status & Scope
* **Design Status:** Designed / Proposed (Milestone 3 Baseline Architecture).
* **Scope:** This document defines the formal metadata schema, payload indexing configurations for Qdrant, provenance chains, and metadata lifecycle rules for the AtlasRAG system. At Milestone 3, this schema represents a formal architectural specification designed to govern subsequent implementation in Milestone 4.

---

## 2. Metadata Lifecycle Flow Diagram
The metadata lifecycle ensures rigorous traceability from raw document ingestion through vector storage, hybrid retrieval, and final grounded citation generation:

```text
Raw Document
    ↓
[Document Identity Generation] (Deterministic SHA-256 derived from canonical source ID + content)
    ↓
[Metadata Extraction & Normalization] (Assignment of structured fields: language, disaster_type, version, etc.)
    ↓
[Chunking Subsystem] (Hierarchical recursive splitting into token-constrained segments)
    ↓
[Chunk Metadata Generation] (Binding chunk_id, chunk_index, page_start/end, and content_hash)
    ↓
[Index Storage] (Payload indexing in Qdrant Vector Store & BM25 index)
    ↓
[Retrieval & Re-Ranking] (Payload filtering and candidate re-scoring)
    ↓
[Citation Mapping & Provenance Generation] (Binding generated claims to source document and chunk IDs)


## 3. Provenance Chain & Identifier Relationships
To support end-to-end auditability and document versioning, AtlasRAG defines a strict hierarchical provenance chain:
$$\text{Document} \rightarrow \text{document\_id} \rightarrow \text{Chunk} \rightarrow \text{chunk\_id} \rightarrow \text{Retrieval} \rightarrow \text{Citation}$$

### Relationship Definitions:
1. **`document_id`:** Identifies the logical source document. Computed deterministically via SHA-256 hash derived from a canonical identifier combination (e.g., normalized issuer string + document title + initial publication date).
2. **`version`:** Represents the revision state of the source document (e.g., `"v2.1"`). When a document is updated, its version increments, generating a new logical document or version-bound payload set.
3. **`content_hash`:** A SHA-256 hash computed specifically over the exact raw text content of an individual chunk. This supports reproducibility, exact chunk deduplication, and integrity verification.
4. **`chunk_id`:** A composite or deterministic unique identifier assigned to an individual chunk (e.g., `{document_id}_chunk_{chunk_index}`), ensuring that every segment retrievable by the hybrid engine has a distinct, traceable address.

---

## 4. Canonical JSON Metadata Schema Specification

```json
{
  "document_id": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "chunk_id": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855_chunk_004",
  "chunk_index": 4,
  "content_hash": "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce",
  "title": "Example Standard Operating Procedure: Flood Evacuation (Example)",
  "source_url": "[https://example.org/documents/sop-04.pdf](https://example.org/documents/sop-04.pdf)",
  "language": "hi",
  "language_confidence": null,
  "publication_date": "2025-06-12",
  "document_type": "government_protocol",
  "organization": "Example National Authority (Example)",
  "location": "Region-North (Example)",
  "disaster_type": "flood",
  "version": "v2.1",
  "page_start": 4,
  "page_end": 5,
  "page": 4,
  "section": "3.2 Immediate Relocation",
  "ingestion_timestamp": "2026-06-07T14:30:00Z"
}

| Field Name | Data Type | Nullable | Source | Filterable (Qdrant) | Citation-Critical | Purpose & Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`document_id`** | String (SHA-256) | No | Deterministic Hash | Yes | **Yes** | Uniquely identifies the logical source document. |
| **`chunk_id`** | String | No | System Generated | No | **Yes** | Uniquely identifies the individual retrieved chunk. |
| **`chunk_index`** | Integer | No | Chunker Pipeline | No | No | Identifies the ordinal position of the chunk within the document. |
| **`content_hash`** | String (SHA-256) | No | Chunk Text | No | No | Identifies exact chunk content for deduplication and reproducibility. |
| **`title`** | String | Yes | Parser / Extractor | No | **Yes** | Human-readable title of the source document. |
| **`source_url`** | String (URI) | Yes | Ingestion Config | No | **Yes** | External reference URL pointing to the original document. |
| **`language`** | String (ISO Code) | Yes | Language Identifier | **Yes** | No | Primary language code of the text snippet (`en`, `hi`, `mr`). |
| **`language_confidence`**| Float | Yes | Language Detector | No | No | Optional confidence score from language identification; set to `null` if unprovided. |
| **`publication_date`** | String (ISO Date) | Yes | Document Metadata | **Yes** | No | Official publication date of the source document. |
| **`document_type`** | String | Yes | Ingestion Config | **Yes** | No | Category of document (`government_protocol`, `field_report`, etc.). |
| **`organization`** | String | Yes | Document Metadata | **Yes** | No | Issuing organization or agency. |
| **`location`** | String | Yes | Document Metadata | **Yes** | No | Geographic region or jurisdiction associated with the text. |
| **`disaster_type`** | String | Yes | Document Metadata | **Yes** | No | Disaster classification (`flood`, `earthquake`, `cyclone`, etc.). |
| **`version`** | String | Yes | Document Metadata | **Yes** | No | Document revision version identifier (`v1.0`, `v2.1`). |
| **`page_start`** | Integer | Yes | Parser / Extractor | No | **Yes** | Starting page number in the source document where the chunk begins. |
| **`page_end`** | Integer | Yes | Parser / Extractor | No | **Yes** | Ending page number in the source document where the chunk concludes. |
| **`page`** | Integer | Yes | Parser / Extractor | No | No | Legacy compatibility field representing the primary start page. |
| **`section`** | String | Yes | Parser / Extractor | No | **Yes** | Hierarchical section header or title enclosing the chunk. |
| **`ingestion_timestamp`| String (ISO Datetime)| No | System Clock | No | No | Timestamp recording when the chunk was ingested into the system. |

## 6. Metadata Integrity & Derivation Rules
1. **Derivation Rule:** All metadata must be derived from source documents, reliable ingestion configurations, or deterministic processing.
2. **Null Fallback Rule:** If a metadata field cannot be reliably determined or extracted from the source, it must be assigned a `null` value rather than fabricating, guessing, or estimating a placeholder.
3. **Extraction vs. Inference:** Extracted metadata (derived directly from document headers or text) must be strictly distinguished from inferred metadata (predicted by auxiliary models). At Milestone 3, all metadata is specified as extracted or configuration-bound.