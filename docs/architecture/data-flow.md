## 1. Architectural Status & Scope
* **Design Status:** Designed / Proposed (Milestone 3 Baseline Architecture).
* **Scope:** This document defines the formal data flow pathways for the AtlasRAG system, separating the **Offline Ingestion Pipeline** from the **Online Query Execution Pipeline**, and defining independent tracks for operational telemetry and offline research evaluation.

---

## 2. Complete End-to-End System Data Flow Diagram

### A. Offline Ingestion Pipeline
```text
Raw Documents (PDF, HTML, TXT, DOCX)
        ↓
[Document Loader & Parser] (Extracts raw text & section hierarchies)
        ↓
[Text Preprocessor] (Unicode NFC normalization & whitespace cleanup)
        ↓
[Metadata Extractor] (Assigns persistent document_id, title, source_url, language, disaster_type, version, publication_date)
        ↓
[Hierarchical Semantic Chunker] (Baseline configuration: 512-token chunks with 64-token overlap; configurable for future ablation)
        ↓
        ├─────────────────────────────────────────┐
        ↓                                         ↓
[Dense Embedding Path]                    [Sparse Lexical Path]
BAAI/bge-m3 Encoder                       Lexical Preprocessing / Tokenization
        ↓                                         ↓
Qdrant Vector Database                    BM25 Lexical Index
(Dense Vectors + Payload Metadata)        (Inverted Index / Term Frequencies)






User Query Input
        ↓
[Query Preprocessing & Sanitization]
        ↓
[Language Identification]
        ↓
[Optional Metadata Filtering] (Constrains payload search space by language, disaster_type, location, etc.)
        ↓
        ├─────────────────────────────────────────┐
        ↓                                         ↓
Dense Retrieval                           Sparse Retrieval
BAAI/bge-m3 + Qdrant                      Rank-BM25 Lexical Search
(Cosine Similarity)                       (Term Frequency Match)
        ↓                                         ↓
        └───────────────────┬──────────────────────┘
                            ↓
               [Reciprocal Rank Fusion (RRF)]
                     Baseline: k = 60
                            ↓
               [Top-N Candidate Pool]
                     Baseline: N = 20
                            ↓
             [Cross-Encoder Reranking Engine]
                   (Status: Decision Pending)
                            ↓
               [Top-K Evidence Chunks]
                     Baseline: K = 5
                            ↓
              [Evidence Sufficiency Check]
                     ├── Insufficient → [Fallback / Abstention] ("Sufficient verified evidence was not found...")
                     └── Sufficient   → [Context Builder & Provenance Injector] (Packages chunks with [Source ID], [Page], [Section])
                            ↓
              [Grounded Generation (Llama-3-8B-Instruct)] (Constrained prompt generation)
                            ↓
              [Citation Mapping & Source Attribution Engine] (Binds generated claims to source chunk IDs)
                            ↓
              [Final Grounded Answer + Traceable Citations]
                            ↓
        ┌───────────────────┴───────────────────┐
        ↓                                       ↓
[Operational Telemetry]                [Research Evaluation Pipeline]
Record request_id, latency,            Offline benchmarking via Ragas
token usage, component timings,        (Faithfulness, Answer Relevance, Context Precision,
retrieval scores, errors               Recall@K, MRR, nDCG)



## 3. Pipeline Stage Specifications

### Phase 1: Offline Ingestion & Provenance Preservation
1. **Document Ingestion & Parsing:** Raw multi-format crisis documents are ingested while preserving structural headers, page numbers, and section hierarchies.
2. **Preprocessing & Normalization:** Text undergoes Unicode NFC normalization and whitespace sanitation.
3. **Metadata Schema Assignment:** Each document and resulting chunk is bound to a persistent identifier and structured dictionary (`document_id`, `title`, `source_url`, `language`, `publication_date`, `document_type`, `organization`, `location`, `disaster_type`, `version`, `page`, `section`, `chunk_id`, `ingestion_timestamp`).
4. **Chunking Strategy:** The baseline chunking strategy utilizes recursive character token splitting configured to a target size of 512 tokens with a 64-token overlap. This is an initial baseline configuration designed to be swappable for alternative chunking strategies during future ablation experiments. Provenance metadata is explicitly inherited by every chunk to guarantee end-to-end traceability back to the source document, page, and section.
5. **Dual Indexing (Decoupled Paths):**
   * **Dense Path:** Chunks are processed through the `BAAI/bge-m3` embedding encoder to generate dense vector representations stored in Qdrant with associated payload metadata.
   * **Sparse Path:** Chunks undergo lexical preprocessing and are indexed into the Rank-BM25 sparse search index independently.

### Phase 2: Online Query Execution
1. **Query Preprocessing & Language ID:** Incoming user queries are cleaned, normalized, and evaluated for language identification to assist cross-lingual routing.
2. **Metadata Filtering (Optional):** Structured query filters may be applied to constrain Qdrant payload search space by specific disaster types, languages, or geographic locations.
3. **Hybrid Candidate Retrieval:** Queries are evaluated simultaneously against Qdrant (dense cosine similarity) and BM25 (sparse lexical term matching).
4. **Reciprocal Rank Fusion (RRF):** Dense and sparse rank lists are merged using Reciprocal Rank Fusion with baseline smoothing parameter $k=60$, producing a unified Top-$N$ candidate pool ($N=20$). Both parameters are initial baselines and remain fully configurable.
5. **Cross-Encoder Re-Ranking:** Top-$N$ candidates are passed to a cross-encoder re-ranking stage (model status: *Decision Pending*) to produce high-precision Top-$K$ evidence chunks ($K=5$).
6. **Evidence Sufficiency Check:** Retrieved chunks are evaluated for relevance and confidence. If evidence is deemed insufficient, the system bypasses generation and triggers a fallback/abstention protocol (*"Sufficient verified evidence was not found in the ingested knowledge base to answer this query safely"*).
7. **Context Construction & Grounded Generation:** Sufficient evidence is packaged with explicit provenance markers (`[Source ID], [Page], [Section]`) and passed to `Llama-3-8B-Instruct` under strict system prompts prohibiting extrapolation beyond provided evidence.
8. **Citation Mapping:** Generated response claims are programmatically bound to source chunk metadata to deliver auditable citations.

---

## 4. Separation of Telemetry and Research Evaluation
To maintain rigorous research standards, operational runtime execution is strictly decoupled from offline evaluation:
* **Operational Telemetry:** Records production metadata per request (query ID, timestamp, component latency, token count, selected configuration versions, and error states) without executing heavy evaluation benchmarks on every live call.
* **Research Evaluation Pipeline:** Executed asynchronously or in experimental sandboxes using frameworks like **Ragas** alongside traditional IR metrics (Recall@K, Precision@K, MRR, nDCG) to evaluate retrieval precision, context relevance, answer faithfulness, and citation correctness.git add docs/architecture/data-flow.md
