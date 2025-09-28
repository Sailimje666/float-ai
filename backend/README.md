# Argo AI Ocean Assistant - Backend

This backend package ingests Argo NetCDF profiles into DuckDB (with spatial functions), builds FAISS embeddings for semantic retrieval, and provides a lightweight RAG pipeline (semantic hints → NL2SQL → execute → summarize). It also includes social impact features: anomaly alerts, kid-friendly educational summaries, and an ecosystem health index.

## Features
- Data ingestion from NetCDF (`xarray`) → DuckDB table `profiles`
- Spatial queries via DuckDB spatial extension (fallback to Haversine)
- Embeddings with `sentence-transformers` + FAISS index
- RAG pipeline:
  - Semantic search (k=5)
  - NL2SQL with Mistral-7B via HuggingFace (safe heuristic fallback)
  - Result summarization (LLM or rule-based)
- Social Impact: anomaly detection, educational summaries, health index (0–100)

## Quick Start
1. Place your `.nc` NetCDF files in `data/`.
2. (Optional) Set env vars:
   - `ARGO_DUCKDB_PATH` (default: `data/argo.duckdb`)
   - `ARGO_DATA_DIR` (default: `data`)
   - `HUGGINGFACEHUB_API_TOKEN` (optional for Mistral-7B)
   - `MISTRAL_MODEL_ID` (default: `mistralai/Mistral-7B-Instruct-v0.2`)
3. Run the demo:
   - From v0, execute `scripts/run_backend_demo.py`.

## Notes
- If the spatial extension isn’t available, queries fall back to Haversine distance.
- Large models may be replaced by heuristics automatically if not available.
- Designed to handle 10k+ records with simple indexes and vectorized ingestion.
