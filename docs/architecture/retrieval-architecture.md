## 1. Subsystem Objective
To achieve high recall and precision across multilingual disaster texts, AtlasRAG rejects pure dense-only vector search in favor of a robust **Hybrid Retrieval and Cross-Encoder Re-Ranking Pipeline**.

## 2. Dense Semantic Retrieval
* **Model:** `BAAI/bge-m3`
* **Mechanism:** Projects queries and document chunks into a unified high-dimensional vector space. Similarity is computed using cosine distance inside the Qdrant vector database.
* **Role:** Captures deep semantic intent, conceptual synonyms, and cross-lingual semantic equivalents.

## 3. Sparse Lexical Retrieval
* **Engine:** Rank-BM25
* **Mechanism:** Probabilistic term-matching based on TF-IDF weighting with document length normalization.
* **Role:** Vital for capturing exact keyword matches, official crisis codes, proper nouns, and technical acronyms that dense encoders occasionally miss.

## 4. Reciprocal Rank Fusion (RRF)
To combine dense and sparse outputs without requiring sensitive score calibration across disparate vector spaces, AtlasRAG utilizes Reciprocal Rank Fusion:
$$\text{RRF\_Score}(d \in D) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
*(where $k=60$ is a standard smoothing constant, and $r_m(d)$ is the rank of document $d$ in retrieval method $m$).*

## 5. Cross-Encoder Re-Ranking Stage
* **Mechanism:** Top-$N$ candidates ($N=20$) retrieved via hybrid RRF are passed through a cross-encoder model to compute joint attention scores between the query and each chunk simultaneously.
* **Role:** Dramatically filters out false positives, retaining only the top-$K$ ($K=5$) high-precision evidence chunks for final LLM context construction.