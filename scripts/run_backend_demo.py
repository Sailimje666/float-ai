# Note: v0 runs scripts in /scripts. Use console output for results.
import os
import json
import time
from backend import Config, DataIngestor, RagPipeline, detect_anomalies, ecosystem_health_index, educational_summary

def _ts() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")

def main():
    cfg = Config()
    print(f"[{_ts()}] [v0] Using DuckDB: {cfg.duckdb_path}")
    print(f"[{_ts()}] [v0] Data dir: {cfg.data_dir}")

    # 1) Ingest any *.nc files present in data/
    ing = DataIngestor(cfg)
    rows = ing.ingest_folder("*.nc")
    print(f"[{_ts()}] [v0] Ingested rows: {rows}")

    # 2) Build embeddings + FAISS (optional if deps unavailable)
    rag = RagPipeline(cfg)
    built, dim = rag.build_faiss()
    print(f"[{_ts()}] [v0] FAISS status: {built} vectors (dim={dim})")

    # 3) Sample query flows
    q1 = "Show salinity profiles near the equator in March 2023"
    ans1 = rag.ask(q1)
    print(f"[{_ts()}] [v0] Q1: {q1}")
    print(f"[{_ts()}] [v0] SQL1: {ans1['sql']}")
    print(f"[{_ts()}] [v0] Rows1: {ans1['rows']}")
    print(f"[{_ts()}] [v0] Summary1: {ans1['summary'][:300]}")

    q2 = "Compare BGC parameters in the Arabian Sea for the last 6 months"
    ans2 = rag.ask(q2)
    print(f"[{_ts()}] [v0] Q2: {q2}")
    print(f"[{_ts()}] [v0] SQL2: {ans2['sql']}")
    print(f"[{_ts()}] [v0] Rows2: {ans2['rows']}")
    print(f"[{_ts()}] [v0] Summary2: {ans2['summary'][:300]}")

    # 4) Social impact checks on a subset
    import duckdb
    con = duckdb.connect(cfg.duckdb_path if not cfg.in_memory_duckdb else ":memory:")
    try:
        df = con.execute("SELECT * FROM profiles ORDER BY time DESC LIMIT 200;").df()
    except Exception:
        df = con.execute("SELECT * FROM profiles LIMIT 200;").df()
    alerts = detect_anomalies(df)
    print(f"[{_ts()}] [v0] Alerts found: {len(alerts)}")
    if alerts:
        print(f"[{_ts()}] [v0] First alert: {json.dumps(alerts[0], default=str)[:300]}")

    # 5) Health index example (first row if present)
    if not df.empty:
        r = df.iloc[0]
        hi = ecosystem_health_index(
            (None if r.get('temp') is None else float(r['temp'])) if 'temp' in r else None,
            (None if r.get('salinity') is None else float(r['salinity'])) if 'salinity' in r else None,
        )
        print(f"[{_ts()}] [v0] Health index sample:", hi)

    # 6) Educational summary example
    edu = educational_summary("ocean salinity", data_hint="some locations show slightly lower salinity which can signal rainfall or freshwater input.")
    print(f"[{_ts()}] [v0] Educational summary:\n{edu}")

if __name__ == "__main__":
    main()
