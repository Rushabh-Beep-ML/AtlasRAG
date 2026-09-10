# AtlasRAG: Milestone 3 — Official System Architecture & Completion Report

**Author:** Lead Research Architect & Senior ML/RAG Engineer, AtlasRAG Research Lab  
**Status:** Approved for Implementation  
**Classification:** Research Lab Architecture Specification  

---

## 1. Milestone Objective
Milestone 3 establishes the rigorous scientific, structural, and operational system architecture required to transform the theoretical frameworks of Milestones 1 and 2 into an implementable, modular, and empirically testable Retrieval-Augmented Generation (RAG) system. This specification governs all subsequent engineering design in Milestone 4 and beyond.

---

## 2. Starting State Audit
Prior to this milestone, the repository contained:
* **Milestone 1:** Project Vision, Research Proposal, Research Gap Analysis, and Repository Planning structure (`docs/00_Project_Vision.md` – `03_Repository_Planning.md`).
* **Milestone 2:** Comprehensive Literature Review, Technology Selection, Competitive Analysis, and Research Methodology Planning (`docs/03_Literature_Review.md` – `06_Research_Methodology.md`).
* **Repository Baseline:** Unstructured package skeletons under `src/` (`ingestion`, `retrieval`, `reranking`, `generation`, `evaluation`) and version-controlled Git infrastructure on the `dev` branch.

---

## 3. Comprehensive System Architecture Design
AtlasRAG is structured as a decoupled, multi-stage pipeline designed for low-resource multilingual disaster knowledge management. The system transitions from raw multi-format heterogeneous inputs to fully attributed, grounded, and verified text outputs.

### High-Level End-to-End Pipeline Flow
```text
[Heterogeneous Data Sources] 
        ↓ (Batch Ingestion)
[Document Parsing & OCR Engine] 
        ↓ (Text Normalization & Unicode Cleanup)
[Persistent Metadata Schema Assignment] 
        ↓ (Hierarchical Semantic Chunking)
[Multi-Vector Multilingual Embedding (BAAI/bge-m3)] 
        ↓ (Dual-Index Storage: Qdrant Dense Vector Store + BM25 Lexical Index)
------------------- [OFFLINE INDEXING BOUNDARY] -------------------
------------------- [ONLINE QUERY EXECUTION BOUNDARY] -------------------
[User Query Input] 
        ↓ (Query Preprocessing & Language Detection)
[Hybrid Retrieval Engine (Dense Qdrant + Sparse BM25 via RRF)] 
        ↓ (Top-N Candidate Pool)
[Cross-Encoder Re-Ranking Engine] 
        ↓ (Top-K High-Precision Evidence Chunks)
[Context Construction & Provenance Injector] 
        ↓ (Grounded Generation via Llama-3-8B-Instruct with Guardrails)
[Citation Mapping & Source Attribution Engine] 
        ↓ (Final Verified Answer + Traceable Citations)
[Automated Evaluation Framework (Ragas) & Structured Telemetry Logging]

### 4. Detailed Component Specifications

### Layer 1 to 4: Ingestion & Preprocessing Pipeline
* **Inputs:** Raw PDFs, HTML bulletins, plain text government protocols, and DOCX crisis logs.
* **Processing:** Multi-format loaders parse raw files while maintaining section hierarchies. Text undergoes Unicode normalization (NFC) and whitespace sanitization.
* **Persistent Identity Schema:** Every ingested chunk receives a deterministic unique identifier and standardized metadata dictionary:
### Layer 5: Chunking Strategy (Research Baseline)
* **Strategy:** Recursive Character Text Splitting with semantic boundary awareness, targeting a chunk size of 512 tokens with a 64-token overlap.
* **Rationale:** Balances context window availability with granular snippet attribution, avoiding the complete loss of relational context common in fixed-size character slicing.

### Layer 6 & 7: Multilingual Embedding & Indexing
* **Embedding Model:** `BAAI/bge-m3` selected for its native capacity to output dense representations, sparse lexical weights, and multi-vector alignments simultaneously.
* **Storage Backend:** Qdrant Vector Database configured with payload indexing on `language`, `disaster_type`, and `publication_date` to support rapid metadata filtering alongside vector similarity matching.

### Layer 8 & 9: Hybrid Retrieval Subsystem
* **Architecture:** Combines Dense Vector Search (Qdrant) and Sparse Lexical Search (BM25).
* **Fusion Algorithm:** Reciprocal Rank Fusion (RRF) to merge disparate rank lists without requiring normalized score calibration across models:
  $$\text{RRF\_Score}(d \in D) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
  *(where $k=60$ is a standard smoothing constant, and $r_m(d)$ is the rank of document $d$ in retrieval method $m$)*.

### Layer 10 & 11: Cross-Encoder Re-Ranking & Context Construction
* **Re-ranking:** Top-$N$ candidates ($N=20$) fetched via hybrid search are passed through a cross-encoder model to compute deep token-level interaction scores, reducing the set to top-$K$ ($K=5$) high-precision evidence chunks.
* **Context Builder:** Packages retrieved chunks with explicit provenance markers (`[Source ID], [Page], [Section]`) to ensure the downstream generator retains structural traceability.

### Layer 12 & 13: Grounded Generation & Citation Architecture
* **Generator:** `Llama-3-8B-Instruct` configured with strict system prompts prohibiting extrapolation beyond provided evidence.
* **Fallback Behavior:** If retrieval confidence falls below a set similarity threshold or no relevant documents are found, the system explicitly outputs a designated state: *"Sufficient verified evidence was not found in the ingested knowledge base to answer this query safely."*
* **Citation Mapping:** Generated response claims are programmatically bound to source chunk IDs, producing auditable footnotes.