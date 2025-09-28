from __future__ import annotations
import os
import json
import time
from typing import List, Dict, Any, Optional, Tuple

import duckdb
import numpy as np
import pandas as pd

from .config import Config, get_duckdb_connection

# Embeddings
try:
    from sentence_transformers import SentenceTransformer
    _HAS_ST = True
except Exception as _e:
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [v0] sentence-transformers unavailable: {_e}")
    _HAS_ST = False

# FAISS
try:
    import faiss
    _HAS_FAISS = True
except Exception as _e:
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [v0] FAISS unavailable: {_e}")
    _HAS_FAISS = False

# LLM via HF (Mistral-7B)
try:
    from transformers import pipeline
    _HAS_HF = True
except Exception as _e:
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [v0] transformers unavailable: {_e}")
    _HAS_HF = False


def _ts() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _ensure_paths(cfg: Config):
    os.makedirs(os.path.dirname(cfg.faiss_index_path), exist_ok=True)
    os.makedirs(os.path.dirname(cfg.faiss_meta_path), exist_ok=True)


class RagPipeline:
    """
    - Build embeddings for profile metadata and store in FAISS
    - Semantic search → NL2SQL (LLM or heuristic) → Execute on DuckDB → Summarize
    """

    def __init__(self, cfg: Optional[Config] = None):
        self.cfg = cfg or Config()
        self.con = get_duckdb_connection(self.cfg)
        _ensure_paths(self.cfg)
        self.embedder = None
        if _HAS_ST:
            try:
                self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
                print(f"[{_ts()}] [v0] Loaded sentence-transformers model.")
            except Exception as e:
                print(f"[{_ts()}] [v0] Failed to load embedder: {e}")
        self.index = None
        self.meta: List[Dict[str, Any]] = []

    def _metadata_rows(self) -> List[Dict[str, Any]]:
        df = self.con.execute(
            """
            SELECT id, float_id, time, lat, lon, depth, temp, salinity
            FROM profiles
            ORDER BY time DESC
            """
        ).df()
        rows: List[Dict[str, Any]] = []
        for _, r in df.iterrows():
            text = (
                f"Float {r['float_id']} at ({r['lat']:.3f},{r['lon']:.3f}) on {r['time']}: "
                f"depth {r['depth'] if pd.notnull(r['depth']) else 'NA'} m, "
                f"temp {r['temp'] if pd.notnull(r['temp']) else 'NA'} C, "
                f"salinity {r['salinity'] if pd.notnull(r['salinity']) else 'NA'} PSU"
            )
            rows.append(
                {
                    "id": int(r["id"]),
                    "float_id": str(r["float_id"]),
                    "time": str(r["time"]),
                    "lat": float(r["lat"]),
                    "lon": float(r["lon"]),
                    "depth": float(r["depth"]) if pd.notnull(r["depth"]) else None,
                    "temp": float(r["temp"]) if pd.notnull(r["temp"]) else None,
                    "salinity": float(r["salinity"]) if pd.notnull(r["salinity"]) else None,
                    "text": text,
                }
            )
        return rows

    def build_faiss(self) -> Tuple[int, int]:
        if not (_HAS_ST and _HAS_FAISS and self.embedder):
            print(f"[{_ts()}] [v0] Build skipped: dependencies missing (ST={_HAS_ST}, FAISS={_HAS_FAISS}).")
            return (0, 0)
        self.meta = self._metadata_rows()
        if not self.meta:
            print(f"[{_ts()}] [v0] No metadata to index.")
            return (0, 0)

        texts = [m["text"] for m in self.meta]
        embs = self.embedder.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        dim = embs.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embs)
        faiss.write_index(index, self.cfg.faiss_index_path)
        with open(self.cfg.faiss_meta_path, "w", encoding="utf-8") as f:
            for m in self.meta:
                f.write(json.dumps(m) + "\n")
        self.index = index
        print(f"[{_ts()}] [v0] FAISS built with {index.ntotal} vectors (dim={dim}).")
        return (index.ntotal, dim)

    def _load_index(self) -> bool:
        if self.index is not None and self.meta:
            return True
        try:
            self.index = faiss.read_index(self.cfg.faiss_index_path) if _HAS_FAISS else None
            self.meta = []
            with open(self.cfg.faiss_meta_path, "r", encoding="utf-8") as f:
                for line in f:
                    self.meta.append(json.loads(line))
            return self.index is not None and len(self.meta) > 0
        except Exception as e:
            print(f"[{_ts()}] [v0] Unable to load FAISS index: {e}")
            return False

    def semantic_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        if not self._load_index():
            print(f"[{_ts()}] [v0] No FAISS index; rebuilding.")
            self.build_faiss()
            if not self._load_index():
                return []

        if not self.embedder:
            print(f"[{_ts()}] [v0] Embedder not available; returning metadata head.")
            return self.meta[:k]

        q_emb = self.embedder.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        D, I = self.index.search(q_emb, k)
        results = []
        for idx, score in zip(I[0].tolist(), D[0].tolist()):
            if 0 <= idx < len(self.meta):
                m = dict(self.meta[idx])
                m["score"] = float(score)
                results.append(m)
        return results

    def _llm(self):
        if not _HAS_HF:
            return None
        try:
            return pipeline(
                "text-generation",
                model=self.cfg.mistral_model_id,
                token=self.cfg.hf_token,
                trust_remote_code=True,
                max_new_tokens=384,
            )
        except Exception as e:
            print(f"[{_ts()}] [v0] HF pipeline unavailable: {e}")
            return None

    def nl2sql(self, question: str) -> str:
        """
        Produce DuckDB SQL. Prefers LLM; falls back to heuristics that parse basic
        geospatial and temporal concepts.
        """
        schema = """
        Table profiles(id BIGINT, float_id VARCHAR, time TIMESTAMP, lat DOUBLE, lon DOUBLE,
                       depth DOUBLE, temp DOUBLE, salinity DOUBLE, bgc JSON, geom GEOMETRY)
        """
        examples = [
            (
                "Show salinity profiles near the equator in March 2023",
                "SELECT id, float_id, time, lat, lon, depth, temp, salinity FROM profiles "
                "WHERE abs(lat) <= 5 AND time >= '2023-03-01' AND time < '2023-04-01' "
                "ORDER BY time DESC LIMIT 200;"
            ),
            (
                "Compare BGC parameters in the Arabian Sea for the last 6 months",
                "SELECT time::DATE AS date, avg(temp) AS avg_temp, avg(salinity) AS avg_salinity "
                "FROM profiles WHERE lon BETWEEN 40 AND 75 AND lat BETWEEN 5 AND 25 "
                "AND time >= now() - INTERVAL 6 MONTH GROUP BY date ORDER BY date;"
            ),
        ]
        instr = (
            "Write a single DuckDB SQL query. Use ST_DWithin if distance/radius is implied and geom is available. "
            "Use standard DuckDB functions, avoid CTEs unless needed. Output only SQL."
        )

        llm = self._llm()
        if llm:
            prompt = (
                f"Schema:\n{schema}\n\nInstruction: {instr}\n\n"
                f"Examples:\n"
                + "\n".join([f"Q: {q}\nSQL: {s}" for q, s in examples])
                + f"\n\nQ: {question}\nSQL:"
            )
            try:
                out = llm(prompt)[0]["generated_text"]
                # Extract SQL after last 'SQL:'
                if "SQL:" in out:
                    out = out.split("SQL:")[-1].strip()
                # Basic sanity guard
                if "SELECT" not in out.upper():
                    raise ValueError("LLM did not return SQL; using fallback.")
                return out
            except Exception as e:
                print(f"[{_ts()}] [v0] nl2sql LLM error: {e}")

        # Heuristic fallback
        ql = question.lower()
        date_filter = ""
        if "march 2023" in ql:
            date_filter = " AND time >= '2023-03-01' AND time < '2023-04-01'"
        elif "last 6 months" in ql:
            date_filter = " AND time >= now() - INTERVAL 6 MONTH"

        geo_filter = ""
        if "equator" in ql:
            geo_filter = " AND abs(lat) <= 5"
        if "arabian sea" in ql:
            # Approx bounding box
            geo_filter += " AND lon BETWEEN 40 AND 75 AND lat BETWEEN 5 AND 25"

        cols = "id, float_id, time, lat, lon, depth, temp, salinity"
        sql = f"SELECT {cols} FROM profiles WHERE 1=1{geo_filter}{date_filter} ORDER BY time DESC LIMIT 200;"
        return sql

    def execute_sql(self, sql: str) -> pd.DataFrame:
        try:
            return self.con.execute(sql).df()
        except Exception as e:
            print(f"[{_ts()}] [v0] SQL error: {e}\n-- SQL --\n{sql}")
            return pd.DataFrame()

    def summarize(self, question: str, df: pd.DataFrame) -> str:
        """
        Summarize results. Prefer LLM; fallback to rule-based summary.
        """
        if df.empty:
            return "No matching profiles were found for your query."

        llm = self._llm()
        if llm:
            preview = df.head(20).to_csv(index=False)
            prompt = (
                "Provide a concise scientific summary (4-6 sentences) for the oceanography results below. "
                "Focus on location, time, temperature, salinity, and depth trends.\n\n"
                f"Question: {question}\n\nData (CSV head):\n{preview}\n\nSummary:"
            )
            try:
                out = llm(prompt)[0]["generated_text"]
                return out.split("Summary:", 1)[-1].strip()
            except Exception as e:
                print(f"[{_ts()}] [v0] Summarization LLM error: {e}")

        # Fallback summary
        s = []
        s.append(f"Found {len(df)} matching records.")
        if "temp" in df.columns:
            s.append(f"Average temperature: {df['temp'].dropna().mean():.2f}°C.")
        if "salinity" in df.columns:
            s.append(f"Average salinity: {df['salinity'].dropna().mean():.2f} PSU.")
        if "depth" in df.columns:
            s.append(f"Median depth: {df['depth'].dropna().median():.0f} m.")
        return " ".join(s)

    def ask(self, question: str, k: int = 5) -> Dict[str, Any]:
        """
        Full RAG flow: semantic hinting, NL2SQL, execute, summarize
        """
        hints = self.semantic_search(question, k=k)
        sql = self.nl2sql(question)
        df = self.execute_sql(sql)
        summary = self.summarize(question, df)
        return {
            "question": question,
            "hints": hints,
            "sql": sql,
            "rows": len(df),
            "summary": summary,
        }
