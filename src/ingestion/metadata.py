"""
Metadata and Provenance Engine for AtlasRAG Ingestion Pipeline.
Implements deterministic SHA-256 hashing, Pydantic metadata schema validation,
and strict null-fallback rules for M3 compliance.
"""

import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class ChunkMetadata(BaseModel):
    """
    Strict Pydantic data model representing the canonical M3 metadata schema
    for an individual document chunk, ensuring provenance traceability.
    """
    document_id: str = Field(..., description="Deterministic SHA-256 hash of the logical source document.")
    chunk_id: str = Field(..., description="Unique composite chunk identifier.")
    chunk_index: int = Field(..., ge=0, description="Ordinal position of the chunk within the document.")
    content_hash: str = Field(..., description="SHA-256 hash of the exact raw text content of the chunk.")
    
    title: Optional[str] = Field(default=None, description="Human-readable title of the source document.")
    source_url: Optional[str] = Field(default=None, description="External reference URL or file path.")
    language: Optional[str] = Field(default=None, description="Detected ISO language code (en, hi, mr).")
    language_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Confidence score from language detector.")
    publication_date: Optional[str] = Field(default=None, description="ISO publication date string.")
    document_type: Optional[str] = Field(default=None, description="Document classification category.")
    organization: Optional[str] = Field(default=None, description="Issuing organization or agency.")
    location: Optional[str] = Field(default=None, description="Geographic region or jurisdiction.")
    disaster_type: Optional[str] = Field(default=None, description="Disaster classification (flood, earthquake, etc.).")
    version: Optional[str] = Field(default="v1.0", description="Document revision version identifier.")
    
    page_start: Optional[int] = Field(default=None, ge=1, description="Starting page number in the source document.")
    page_end: Optional[int] = Field(default=None, ge=1, description="Ending page number in the source document.")
    page: Optional[int] = Field(default=None, ge=1, description="Legacy compatibility start page.")
    section: Optional[str] = Field(default=None, description="Hierarchical section header or title enclosing the chunk.")
    ingestion_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z", description="UTC ingestion timestamp.")

    def to_qdrant_payload(self) -> Dict[str, Any]:
        """Converts the Pydantic model into a dictionary suitable for Qdrant payload storage."""
        return self.model_dump()


class MetadataEngine:
    """
    Engine responsible for generating deterministic identifiers, computing content hashes,
    and constructing validated chunk metadata structures.
    """

    @staticmethod
    def compute_sha256(text: str) -> str:
        """Computes a hexadecimal SHA-256 hash for a given input string."""
        if not text:
            return hashlib.sha256(b"").hexdigest()
        return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()

    @classmethod
    def generate_document_id(cls, title: str, source_identifier: str) -> str:
        """
        Generates a deterministic document_id using a normalized combination
        of the document title and source identifier/path.
        """
        canonical_string = f"{title.strip().lower()}:{source_identifier.strip().lower()}"
        return cls.compute_sha256(canonical_string)

    @classmethod
    def generate_chunk_id(cls, document_id: str, chunk_index: int) -> str:
        """Generates a unique traceable chunk identifier."""
        return f"{document_id}_chunk_{chunk_index:04d}"

    @classmethod
    def generate_content_hash(cls, chunk_text: str) -> str:
        """Computes a integrity content hash specifically over chunk text."""
        return cls.compute_sha256(chunk_text)

    @classmethod
    def build_metadata(
        cls,
        document_id: str,
        chunk_index: int,
        chunk_text: str,
        raw_metadata: Optional[Dict[str, Any]] = None,
        language: Optional[str] = None,
        language_confidence: Optional[float] = None,
        page_start: Optional[int] = None,
        page_end: Optional[int] = None,
        section: Optional[str] = None
    ) -> ChunkMetadata:
        """
        Constructs and validates a full ChunkMetadata instance, enforcing null-fallback rules
        for any unprovided or unresolvable attributes.
        """
        raw_metadata = raw_metadata or {}
        
        chunk_id = cls.generate_chunk_id(document_id, chunk_index)
        content_hash = cls.generate_content_hash(chunk_text)
        
        p_start = page_start or raw_metadata.get("page_start")
        p_end = page_end or raw_metadata.get("page_end") or p_start
        legacy_page = p_start or raw_metadata.get("page")

        return ChunkMetadata(
            document_id=document_id,
            chunk_id=chunk_id,
            chunk_index=chunk_index,
            content_hash=content_hash,
            title=raw_metadata.get("title"),
            source_url=raw_metadata.get("source_url"),
            language=language or raw_metadata.get("language"),
            language_confidence=language_confidence or raw_metadata.get("language_confidence"),
            publication_date=raw_metadata.get("publication_date"),
            document_type=raw_metadata.get("document_type"),
            organization=raw_metadata.get("organization"),
            location=raw_metadata.get("location"),
            disaster_type=raw_metadata.get("disaster_type"),
            version=raw_metadata.get("version", "v1.0"),
            page_start=p_start,
            page_end=p_end,
            page=legacy_page,
            section=section or raw_metadata.get("section")
        )