from __future__ import annotations
import os
import glob
import math
import time
from typing import List, Dict, Any, Optional

import duckdb
import pandas as pd
import numpy as np
import xarray as xr

from .config import Config, get_duckdb_connection


def _ts() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _first_existing(ds: xr.Dataset, candidates: List[str]) -> Optional[str]:
    for k in candidates:
        if k in ds.variables:
            return k
        if k in ds.coords:
            return k
    return None


def _coerce_numpy(a) -> np.ndarray:
    if isinstance(a, xr.DataArray):
        return a.values
    return np.asarray(a)


class DataIngestor:
    """
    Ingest NetCDF (Argo) profiles → DuckDB 'profiles' table with optional spatial geometry.
    """

    def __init__(self, cfg: Optional[Config] = None):
        self.cfg = cfg or Config()
        self.con = get_duckdb_connection(self.cfg)
        os.makedirs(self.cfg.data_dir, exist_ok=True)
        self._ensure_schema()

    def _ensure_schema(self):
        print(f"[{_ts()}] [v0] Ensuring DuckDB schema...")
        self.con.execute(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                id BIGINT PRIMARY KEY,
                float_id VARCHAR,
                time TIMESTAMP,
                lat DOUBLE,
                lon DOUBLE,
                depth DOUBLE,
                temp DOUBLE,
                salinity DOUBLE,
                bgc JSON,
                geom GEOMETRY
            );
            """
        )
        # Query logging table for RAG interactions
        self.con.execute(
            """
            CREATE TABLE IF NOT EXISTS queries (
                ts TIMESTAMP DEFAULT current_timestamp,
                question VARCHAR,
                sql VARCHAR,
                rows BIGINT
            );
            """
        )
        # Lightweight indexes; spatial index may be a no-op depending on build
        try:
            self.con.execute("CREATE INDEX IF NOT EXISTS idx_profiles_time ON profiles(time);")
            self.con.execute("CREATE INDEX IF NOT EXISTS idx_profiles_lat ON profiles(lat);")
            self.con.execute("CREATE INDEX IF NOT EXISTS idx_profiles_lon ON profiles(lon);")
            self.con.execute("CREATE INDEX IF NOT EXISTS idx_profiles_geom ON profiles(geom);")
        except Exception as e:
            print(f"[{_ts()}] [v0] Index creation warning: {e}")

    def _parse_netcdf(self, nc_path: str) -> pd.DataFrame:
        print(f"[{_ts()}] [v0] Parsing NetCDF: {nc_path}")
        ds = xr.open_dataset(nc_path)

        # Candidate variable names across Argo variants
        var_lat = _first_existing(ds, ["LATITUDE", "lat", "latitude"])
        var_lon = _first_existing(ds, ["LONGITUDE", "lon", "longitude"])
        var_time = _first_existing(ds, ["JULD", "time", "TIME"])
        var_temp = _first_existing(ds, ["TEMP_ADJUSTED", "TEMP", "temperature"])
        var_sal = _first_existing(ds, ["PSAL_ADJUSTED", "PSAL", "salinity"])
        var_depth = _first_existing(ds, ["DEPTH", "PRES_ADJUSTED", "PRES", "depth"])

        # Float/platform id
        float_id = None
        for cand in ["PLATFORM_NUMBER", "platform", "platform_number", "float_id"]:
            if cand in ds.variables:
                v = ds[cand].values
                if np.ndim(v) == 0:
                    float_id = str(v)
                else:
                    float_id = str(v[0])
                break
        if float_id is None:
            float_id = str(ds.attrs.get("platform_number", "unknown"))

        # Coerce arrays safely; flatten if needed
        lat = _coerce_numpy(ds[var_lat]) if var_lat else np.array([])
        lon = _coerce_numpy(ds[var_lon]) if var_lon else np.array([])
        time_var = _coerce_numpy(ds[var_time]) if var_time else np.array([])
        temp = _coerce_numpy(ds[var_temp]) if var_temp else np.array([])
        sal = _coerce_numpy(ds[var_sal]) if var_sal else np.array([])
        depth = _coerce_numpy(ds[var_depth]) if var_depth else np.array([])

        # Broadcast to 1D rows; many Argo files have profile x level shapes.
        # We build profiles by taking per-profile means as a simple MVP.
        def safe_flat_mean(a, axis=None):
            try:
                if a.size == 0:
                    return np.array([])
                if a.ndim > 1 and axis is not None and axis < a.ndim:
                    return np.nanmean(a, axis=axis)
                return a
            except Exception:
                return a

        # Try to reduce 2D (profile x level) to 1D (profile)
        for name, arr in [("temp", temp), ("sal", sal), ("depth", depth)]:
            if arr.size and arr.ndim > 1:
                # mean over levels
                red = safe_flat_mean(arr, axis=1)
                if name == "temp":
                    temp = red
                elif name == "sal":
                    sal = red
                else:
                    depth = red

        # Ensure equal length by trimming to shortest
        lengths = [len(x) for x in [lat, lon, time_var, temp, sal, depth] if hasattr(x, "__len__")]
        n = min(lengths) if lengths else 0

        df = pd.DataFrame(
            {
                "float_id": [float_id] * n,
                "lat": lat[:n],
                "lon": lon[:n],
                "time": pd.to_datetime(time_var[:n], errors="coerce", unit="D", origin="1950-01-01", utc=True)
                if str(var_time).upper() == "JULD"
                else pd.to_datetime(time_var[:n], errors="coerce", utc=True),
                "depth": depth[:n] if np.ndim(depth) else np.full(n, np.nan),
                "temp": temp[:n] if np.ndim(temp) else np.full(n, np.nan),
                "salinity": sal[:n] if np.ndim(sal) else np.full(n, np.nan),
            }
        )

        # Build simple BGC JSON if present (collect extra vars)
        bgc_vars = ["CHLA", "DOXY", "BBP", "NITRATE", "PH_IN_SITU_TOTAL", "O2SAT", "CDOM"]
        bgc: List[Dict[str, Any]] = []
        for v in bgc_vars:
            if v in ds.variables:
                arr = _coerce_numpy(ds[v])
                if arr.ndim > 1:
                    arr = np.nanmean(arr, axis=1)
                bgc.append({v: np.asarray(arr[:n]).tolist()})
        df["bgc"] = [bgc[i] if i < len(bgc) else {} for i in range(n)] if bgc else [{} for _ in range(n)]

        # Add surrogate id
        df.insert(0, "id", pd.Series(range(int(self._next_id()), int(self._next_id() + n)), dtype="int64"))
        return df

    def _next_id(self) -> int:
        try:
            cur = self.con.execute("SELECT COALESCE(MAX(id)+1, 1) FROM profiles;").fetchone()
            return int(cur[0] or 1)
        except Exception:
            return 1

    def ingest_folder(self, pattern: str = "*.nc") -> int:
        """
        Ingest all NetCDF files in cfg.data_dir matching pattern. Returns rows inserted.
        """
        path_glob = os.path.join(self.cfg.data_dir, pattern)
        files = sorted(glob.glob(path_glob))
        print(f"[{_ts()}] [v0] Found {len(files)} NetCDF files under {self.cfg.data_dir}")
        total = 0
        for fp in files:
            try:
                df = self._parse_netcdf(fp)
                if df.empty:
                    print(f"[{_ts()}] [v0] No rows parsed from {fp}")
                    continue
                # Insert via parameterized COPY for performance
                # Create geometry via ST_Point if spatial available; else NULL
                self.con.execute(
                    """
                    INSERT INTO profiles
                    SELECT
                        id::BIGINT,
                        float_id::VARCHAR,
                        time::TIMESTAMP,
                        lat::DOUBLE,
                        lon::DOUBLE,
                        depth::DOUBLE,
                        temp::DOUBLE,
                        salinity::DOUBLE,
                        to_json(bgc) AS bgc,
                        CASE
                          WHEN try_create('geometry', 1) IS NOT NULL THEN ST_Point(lon, lat)
                          ELSE NULL
                        END AS geom
                    FROM df
                    """,
                )
                total += len(df)
                print(f"[{_ts()}] [v0] Inserted {len(df)} rows from {os.path.basename(fp)}")
            except Exception as e:
                print(f"[{_ts()}] [v0] Error ingesting {fp}: {e}")
        return total

    def query_within_radius(
        self,
        lat: float,
        lon: float,
        radius_km: float,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Geospatial-temporal query with ST_DWithin if available, else Haversine fallback.
        """
        print(f"[{_ts()}] [v0] Radius query lat={lat} lon={lon} r={radius_km}km start={start} end={end}")
        params: Dict[str, Any] = {
            "lat": lat,
            "lon": lon,
            "radius_km": radius_km,
            "limit": limit,
        }

        date_clause = ""
        if start:
            date_clause += " AND time >= TIMESTAMP '" + start + "'"
        if end:
            date_clause += " AND time <= TIMESTAMP '" + end + "'"

        try:
            # Prefer spatial if available
            q = f"""
                SELECT *
                FROM profiles
                WHERE geom IS NOT NULL
                  AND ST_DWithin(geom, ST_Point({lon}, {lat}), {radius_km * 1000})
                  {date_clause}
                ORDER BY time DESC
                LIMIT {limit}
            """
            return self.con.execute(q).df()
        except Exception:
            # Fallback: Haversine distance
            q = f"""
                WITH base AS (
                  SELECT *,
                    2 * 6371 * asin(
                      sqrt(
                        sin(radians((lat - {lat})/2)) * sin(radians((lat - {lat})/2)) +
                        cos(radians({lat})) * cos(radians(lat)) *
                        sin(radians((lon - {lon})/2)) * sin(radians((lon - {lon})/2))
                      )
                    ) AS dist_km
                  FROM profiles
                  WHERE TRUE {date_clause}
                )
                SELECT * FROM base WHERE dist_km <= {radius_km}
                ORDER BY time DESC
                LIMIT {limit}
            """
            return self.con.execute(q).df()
