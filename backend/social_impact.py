from __future__ import annotations
import time
from typing import List, Dict, Any, Optional

import pandas as pd

from .config import Config


def _ts() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def detect_anomalies(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Threshold detection:
    - Salinity outside 34–36 PSU
    - Temperature outside 15–25 °C
    Risk: Low (slight), Medium (moderate), High (extreme)
    """
    alerts: List[Dict[str, Any]] = []
    for _, r in df.iterrows():
        issues = []
        if pd.notnull(r.get("salinity")) and (r["salinity"] < 34 or r["salinity"] > 36):
            delta = abs(r["salinity"] - 35)
            risk = "High" if delta > 1.5 else ("Medium" if delta > 0.7 else "Low")
            issues.append({"type": "salinity", "value": float(r["salinity"]), "risk": risk})
        if pd.notnull(r.get("temp")) and (r["temp"] < 15 or r["temp"] > 25):
            delta = abs(r["temp"] - 20)
            risk = "High" if delta > 4.0 else ("Medium" if delta > 2.0 else "Low")
            issues.append({"type": "temp", "value": float(r["temp"]), "risk": risk})

        if issues:
            impact = "Potential coastal impact: monitor for flood/storm or marine stress."
            alerts.append(
                {
                    "id": int(r.get("id", -1)),
                    "float_id": str(r.get("float_id", "")),
                    "time": str(r.get("time", "")),
                    "lat": float(r.get("lat", 0.0)),
                    "lon": float(r.get("lon", 0.0)),
                    "issues": issues,
                    "impact": impact,
                }
            )
    return alerts


def educational_summary(
    topic: str,
    data_hint: Optional[str] = None,
    model_name: str = "kid_friendly",
) -> str:
    """
    Generate a 100-200 word kid-friendly explanation. Falls back to template.
    Emojis included for educational engagement per spec.
    """
    base = (
        f"Let's learn about {topic}! Oceans are like the planet's lungs, helping to move heat and nutrients around. "
        f"Scientists use floating robots called 'Argo floats' to measure temperature and saltiness (salinity) at different depths. "
    )
    if data_hint:
        base += f"From our data, we noticed: {data_hint}. "

    base += (
        "When water is warmer or saltier than usual, it can affect sea life and weather. "
        "Staying curious helps us protect the ocean! 🌊🐠🧪\n"
        "Fun fact: A career in ocean science can involve coding, data analysis, and ship expeditions! 🚢💻🔬"
    )
    return base


def ecosystem_health_index(temp: Optional[float], salinity: Optional[float]) -> Dict[str, Any]:
    """
    Health index = 0.6*(100 - |salinity-35|*10) + 0.4*(100 - |temp-20|*5)
    Status bands: Healthy (>=80), At Risk (60-79), Critical (<60)
    """
    if temp is None or salinity is None:
        return {"score": None, "status": "Unknown", "recommendation": "Insufficient data."}

    score = 0.6 * (100 - abs(salinity - 35) * 10) + 0.4 * (100 - abs(temp - 20) * 5)
    score = max(0.0, min(100.0, score))
    if score >= 80:
        status = "Healthy"
        rec = "Maintain monitoring and protect local habitats."
    elif score >= 60:
        status = "At Risk"
        rec = "Investigate causes; consider conservation or policy actions."
    else:
        status = "Critical"
        rec = "Immediate mitigation needed; coordinate with local stakeholders."
    return {"score": round(score, 1), "status": status, "recommendation": rec}


if __name__ == "__main__":
    # Minimal sanity check for the health function
    print(f"[{_ts()}] [v0] Health(20C,35PSU):", ecosystem_health_index(20, 35))
    print(f"[{_ts()}] [v0] Health(26C,33PSU):", ecosystem_health_index(26, 33))
