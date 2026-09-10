# Retrieval & Re-Ranking Architecture: AtlasRAG

## 1. Subsystem Objective
The AtlasRAG retrieval subsystem is designed to provide robust, multilingual, and hybrid candidate retrieval for disaster knowledge management. To mitigate the semantic blindness of lexical search and the out-of-vocabulary failures of pure dense encoders, the system couples dense semantic vector search with sparse lexical matching, fused via Reciprocal Rank Fusion (RRF), and refined through cross-encoder re-ranking.

---

## 2. Complete Retrieval Pipeline Flow Diagram

```text
                                  USER QUERY
                                      ↓
                              Query Preprocessing
                                      ↓
                             Language Identification
                                      ↓
                             Metadata Filtering
                                      ↓
                     ┌────────────────┴────────────────┐
                     ↓                                 ↓
             Dense Retrieval                   Sparse Retrieval
           BAAI/bge-m3 + Qdrant                      BM25

             (Cosine Sim)                    (Lexical Term Match)
                     ↓                                 ↓
                     └────────────────┬────────────────┘
                                      ↓
                        Reciprocal Rank Fusion (RRF)
                            Baseline: k = 60
                                      ↓
                            Top-N Candidates (N = 20)
                                      ↓
                          Cross-Encoder Reranking
                           (Status: Decision Pending)
                                      ↓
                            Top-K Evidence Chunks (K = 5)
                                      ↓
                              Evidence Chunks
                                      ↓
                            Context Construction
                                      ↓
                            Grounded Generation

                            ## 3. Detailed Component Specifications

### A. Dense Retrieval Baseline
* **Embedding Model:** `BAAI/bge-m3` (Selected as an initial baseline because AtlasRAG requires multilingual and potentially cross-lingual semantic representation).
* **Vector Database:** Qdrant.
* **Similarity Metric:** Cosine similarity.
* **Research Status:** BAEI/bge-m3 is established strictly as a baseline model; it is not claimed to be optimal. The embedding model abstraction remains configurable and swappable to allow future comparative experiments against alternative multilingual embedding models.

### B. Sparse Lexical Retrieval Baseline
* **Engine:** Rank-BM25.
* **Technical Definition:** A probabilistic lexical retrieval model based on term frequency (TF), inverse document frequency (IDF), and document-length normalization ($k_1, b$ parameters).
* **Role:** Vital for recovering exact terms, technical disaster codes, acronyms, proper nouns, agency identifiers, and specific location names that semantic dense retrieval may fail to capture.

### C. Reciprocal Rank Fusion (RRF)
* **Mechanism:** Fuses dense and sparse rank lists without requiring normalized score calibration across disparate vector spaces:
  $$\text{RRF\_Score}(d \in D) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
* **Baseline Configuration:** $k = 60$.
* **Rationale:** Utilized instead of raw score combination due to differing score distributions across models, eliminating score calibration overhead while providing rank-based robustness. $k=60$ is an initial baseline configuration and remains fully configurable for future ablation experiments.

### D. Metadata Filtering
* **Capability:** Optional filtering or constraining of retrieval results using structured metadata fields: `language`, `disaster_type`, `location`, `document_type`, `organization`, `publication_date`, and `version`.
* **Usage:** Metadata filtering is not forced for every query. It serves as an optional constraint to reduce search space and improve domain-specific retrieval precision when queries contain explicit filtering constraints.

### E. Multilingual & Cross-Lingual Retrieval Scenarios
AtlasRAG is architected to support the following linguistic configurations:
1. English query → English documents
2. Hindi query → Hindi documents
3. Marathi query → Marathi documents
4. English query → Hindi documents
5. English query → Marathi documents
6. Hindi/Marathi query → English documents
7. Cross-language query → Multilingual document collection

* **Note:** The multilingual embedding layer is intended to enable semantic comparison across languages, but cross-lingual retrieval effectiveness has not yet been experimentally validated. It is formally designated for empirical evaluation in later milestones.

### F. Cross-Encoder Re-Ranking Stage
* **Model Status:** **Decision Pending**.
* **Rationale:** A definitive multilingual cross-encoder model with robust zero-shot cross-lingual capacity across low-resource Indic scripts (Hindi/Marathi) requires dedicated benchmarking. Rather than forcing an unverified English-only model, the reranker layer is implemented via a modular abstraction interface (`BaseReranker`), allowing a multilingual cross-encoder to be plugged in later.
* **Baseline Configuration (When Enabled):** Top-$N$ candidates ($N=20$) are retrieved via RRF, passed to the cross-encoder for deep scoring, and filtered down to Top-$K$ ($K=5$) high-precision evidence chunks. Both $N=20$ and $K=5$ are configurable baseline parameters subject to future ablation studies.

---

## 4. Subsystem Modularity & Interfaces
To support independent component substitution and ablation studies without rewriting downstream code, the retrieval architecture abstracts core components into decoupled interfaces:
* `EmbeddingModel`: Abstract base for generating dense/sparse vectors.
* `DenseRetriever`: Encapsulates Qdrant client interactions.
* `SparseRetriever`: Encapsulates Rank-BM25 indexing and scoring.
* `RankFusion`: Implements RRF and alternative fusion algorithms.
* `MetadataFilter`: Manages payload constraint extraction and application.
* `Reranker`: Decouples cross-encoder evaluation from initial candidate retrieval.

---

## 5. Planned Retrieval Experiments (Ablation Design)
The architecture supports the following prospective empirical experiments:
* **Experiment A:** Dense retrieval vs. BM25 sparse retrieval (Metric: MRR@K, Recall@K).
* **Experiment B:** Dense retrieval vs. Hybrid RRF retrieval.
* **Experiment C:** Hybrid retrieval without reranking vs. Hybrid + Cross-Encoder reranking.
* **Experiment D:** Comparative evaluation of alternative multilingual embedding models.
* **Experiment E:** Alternative chunking strategies and token sizes.
* **Experiment F:** Monolingual vs. Cross-lingual retrieval degradation analysis.
* **Experiment G:** Sensitivity analysis on RRF $k$ values ($k \in \{10, 60, 100\}$).
* **Experiment H:** Sensitivity analysis on candidate pool configurations ($N \in \{10, 20, 50\}$, $K \in \{3, 5, 10\}$).

---

## 6. Failure Mode Analysis & Fallback Behavior
* **Insufficient Evidence / Low Confidence:** If retrieval confidence falls below acceptance thresholds or no relevant chunks are retrieved, the system triggers a fallback state signaling insufficient evidence, preventing the generation layer from producing unsupported claims.
* **Metadata Filter Over-Constraint:** If strict metadata filtering returns zero results, the system logs a warning and falls back to unconstrained hybrid search with a query flag.
* **Retrieval Subsystem Failure:** Graceful exception handling catches vector database connection drops or BM25 index corruption, returning standardized error states to API telemetry logs.