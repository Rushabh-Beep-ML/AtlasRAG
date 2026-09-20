# AtlasRAG

### A Multilingual Retrieval-Augmented Intelligence System for Disaster Knowledge Management

> **Research Status:** 🧪 Research & Development — Milestones 1–3 Completed

AtlasRAG is a research-oriented multilingual Retrieval-Augmented Intelligence system for **disaster knowledge management**. The project investigates how information retrieval, multilingual representation, hybrid retrieval, re-ranking, and grounded generation can be combined to support evidence-based access to heterogeneous disaster-related knowledge.

The system is designed as a **modular research framework**, allowing individual components of the retrieval and generation pipeline to be implemented, isolated, evaluated, and iterated independently.

The project emphasizes:

- Multilingual and cross-lingual information retrieval
- Hybrid lexical and semantic retrieval
- Evidence-grounded generation
- Document and chunk-level provenance
- Reproducible experimentation
- Controlled evaluation and ablation studies
- Transparent research documentation

> **Research Integrity:** Architectural decisions described in this repository represent designed or planned components unless explicitly identified as implemented or experimentally validated. Performance claims will only be made after empirical evaluation.

---

## Research Motivation

Disaster-related knowledge is distributed across heterogeneous documents, organizations, formats, locations, and languages.

Traditional lexical retrieval methods can provide strong matching for terminology and named entities, while dense retrieval can capture semantic relationships beyond exact lexical overlap. However, their behavior can differ across domains, languages, query types, and document characteristics.

AtlasRAG therefore investigates a **hybrid retrieval architecture** that combines complementary retrieval signals and subsequently refines retrieved candidates through re-ranking.

The broader objective is to investigate whether a modular multilingual retrieval pipeline can provide more traceable and systematically evaluable access to disaster knowledge than treating retrieval and generation as a single black-box process.

---

# Research Objectives

AtlasRAG investigates the following objectives:

1. Develop a multilingual retrieval system for disaster-related knowledge.
2. Investigate dense, sparse, and hybrid information retrieval approaches.
3. Study multilingual semantic representations for disaster knowledge access.
4. Investigate cross-lingual query-document retrieval scenarios.
5. Combine semantic and lexical retrieval through rank fusion.
6. Investigate candidate refinement using cross-encoder re-ranking.
7. Maintain document- and chunk-level provenance for traceable evidence attribution.
8. Establish reproducible experimental configurations for retrieval research.
9. Evaluate retrieval and answer-grounding components using appropriate research metrics.
10. Provide a modular architecture suitable for controlled experimentation and ablation studies.

---

# Research Questions

The project is structured around questions such as:

- How does dense multilingual retrieval compare with lexical retrieval for disaster-domain queries?
- Does combining dense and sparse retrieval improve evidence retrieval compared with individual retrieval approaches?
- What effect does re-ranking have on the relevance of retrieved evidence?
- How does retrieval behavior change across languages and cross-lingual query-document pairs?
- How do chunking strategies and retrieval parameters affect retrieval effectiveness?
- How reliably can generated responses be traced back to their supporting evidence?

These questions will be investigated experimentally during the implementation and evaluation stages.

---

# System Architecture

The current high-level AtlasRAG pipeline is:

```text
                 ┌──────────────────────┐
                 │    Source Documents  │
                 │ PDF / HTML / TXT /   │
                 │ DOCX / Other Sources │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Document Ingestion   │
                 │ & Parsing             │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Text Normalization   │
                 │ Language Detection   │
                 │ Metadata Extraction  │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Configurable         │
                 │ Chunking             │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Multilingual         │
                 │ Representation      │
                 └──────────┬───────────┘
                            │
             ┌──────────────┴──────────────┐
             │                             │
             ▼                             ▼
   ┌─────────────────┐           ┌─────────────────┐
   │ Dense Retrieval │           │ Sparse Retrieval│
   │   BGE-M3        │           │      BM25       │
   └────────┬────────┘           └────────┬────────┘
            │                             │
            └──────────────┬──────────────┘
                           ▼
                ┌──────────────────────┐
                │ Reciprocal Rank     │
                │ Fusion (RRF)        │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Candidate Retrieval │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Cross-Encoder        │
                │ Re-ranking           │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Context Construction│
                │ & Provenance Mapping│
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Grounded Generation │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Response + Source   │
                │ Attribution         │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Evaluation &        │
                │ Experimental Analysis│
                └──────────────────────┘