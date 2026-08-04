# Repository Planning & Architectural Standards: AtlasRAG

## 1. Folder Structure
```text
atlasrag/
├── .github/workflows/       # CI/CD pipelines (linting, testing)
├── assets/                  # Diagrams, architectural schemas
├── data/                    # Raw, processed, and evaluation datasets (git-ignored large files)
├── docs/                    # Research documentation (Vision, Proposal, Gaps)
├── notebooks/               # Exploratory data analysis and prototyping notebooks
├── src/                     # Core source code package
│   ├── ingestion/           # Document parsing, cleaning, and semantic chunking
│   ├── retrieval/           # Hybrid search (Dense FAISS + Sparse BM25 + RRF)
│   ├── reranking/           # Cross-encoder re-ranking modules
│   ├── generation/          # LLM orchestration and prompt templates
│   └── evaluation/          # Retrieval and generation metrics evaluation scripts
├── tests/                   # Unit and integration test suites
├── pyproject.toml           # Dependency management and project metadata
├── README.md                # Project landing page and overview
└── LICENSE                  # Open-source license (MIT)