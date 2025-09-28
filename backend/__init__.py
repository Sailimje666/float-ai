"""
Argo AI Ocean Assistant - Backend Package

Modules:
- config: paths, tokens, and shared helpers
- data_processing: NetCDF ingestion to DuckDB with spatial helpers
- rag_pipeline: FAISS embeddings + NL2SQL + summarization
- social_impact: anomaly detection, educational summaries, ecosystem health index
"""

from .config import Config, get_duckdb_connection
from .data_processing import DataIngestor
from .rag_pipeline import RagPipeline
from .social_impact import (
    detect_anomalies,
    educational_summary,
    ecosystem_health_index,
)

__all__ = [
    "Config",
    "get_duckdb_connection",
    "DataIngestor",
    "RagPipeline",
    "detect_anomalies",
    "educational_summary",
    "ecosystem_health_index",
]
