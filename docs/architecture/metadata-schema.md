# Metadata Schema Specification: AtlasRAG

Every document chunk ingested into the AtlasRAG Qdrant vector database payload must adhere to the following standardized JSON metadata schema to support filtering, version tracking, and source attribution.

```json
{
  "document_id": "sha256_hash_string",
  "title": "Standard Operating Procedure: Flood Evacuation",
  "source_url": "[https://repository.disaster.gov/sop-04.pdf](https://repository.disaster.gov/sop-04.pdf)",
  "language": "hi",
  "publication_date": "2025-06-12",
  "document_type": "government_protocol",
  "organization": "National Disaster Management Authority",
  "location": "Region-North",
  "disaster_type": "flood",
  "version": "v2.1",
  "page": 4,
  "section": "3.2 Immediate Relocation",
  "ingestion_timestamp": "2026-06-07T14:30:00Z"
}