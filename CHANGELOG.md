Add a concise, factual entry at the top of your **`CHANGELOG.md`**:

```markdown
## [0.4.0] - 2026-09-20
### Added
- Milestone 4 core ingestion pipeline (`src/ingestion/`): document loader (PDF, TXT, MD, HTML), NFC normalizer, 18-field Pydantic metadata schema with SHA-256 deterministic hashing, language detector (`langdetect`), and configurable word-level chunker.
- Comprehensive unit test suite (`tests/test_ingestion.py`) validating normalization, hashing, language fallback, loading edge cases, and provenance inheritance.
- Root `pyproject.toml` configuration and milestone reporting documentation.