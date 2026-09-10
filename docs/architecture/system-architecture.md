# System Architecture: AtlasRAG

## 1. Architectural Overview
AtlasRAG is structured as a decoupled, multi-stage Retrieval-Augmented Generation (RAG) system designed for multilingual disaster knowledge management. The architecture isolates ingestion, indexing, query processing, retrieval, re-ranking, context construction, generation, citation mapping, evaluation, and telemetry into distinct, modular subsystems to support independent component ablation and empirical benchmarking.

## 2. Core Architectural Principles
* **Modularity:** Every pipeline stage communicates via standardized data interfaces, allowing drop-in component replacements (e.g., swapping dense vector indices or re-rankers) without breaking downstream logic.
* **Multilingual & Cross-Lingual Design:** Built to support multilingual and cross-lingual retrieval workflows, including languages with comparatively limited NLP resources. The baseline architecture prioritizes native multilingual representation and retrieval rather than requiring an external machine-translation pipeline.
* **Provenance Tracking:** End-to-end preservation of metadata and source attribution from raw document ingestion down to final generated citations.
* **Local Reproducibility:** Docker-based containerization is used to improve environment consistency and reproducibility across research setups using open-weights models (`Llama-3-8B-Instruct`, `BAAI/bge-m3`).

## 3. High-Level Subsystem Topology & Pipeline Flow
The end-to-end system topology is organized into the following functional layers:
1. **Ingestion & Parsing Subsystem:** Handles heterogeneous document formats (PDF, HTML, DOCX) and normalizes structural headers.
2. **Preprocessing & Metadata Subsystem:** Performs Unicode normalization, whitespace cleanup, and assigns persistent identifiers (`document_id`, `chunk_id`) along with structural metadata.
3. **Knowledge Representation Subsystem:** Manages hierarchical semantic chunking and dual indexing (Qdrant dense vector space + BM25 sparse lexical index).
4. **Query Processing Subsystem:** Handles query normalization, language identification, and optional metadata filtering.
5. **Retrieval & Re-Ranking Subsystem:** Executes hybrid candidate retrieval fused via Reciprocal Rank Fusion (RRF, baseline $k=60$, Top-$N=20$), followed by cross-encoder re-ranking (Top-$K=5$, model status: *Decision Pending*).
6. **Context Construction & Grounding Subsystem:** Evaluates evidence sufficiency, constructs provenance-aware contexts, and applies grounding constraints to prevent generation when evidence is insufficient.
7. **Generation & Citation Subsystem:** Generates grounded responses via local LLM generation (`Llama-3-8B-Instruct`) accompanied by traceable citation mapping.
8. **Evaluation & Operational Telemetry Subsystem:** Strictly separates offline research benchmarking (IR and generation metrics) from runtime operational monitoring.git 