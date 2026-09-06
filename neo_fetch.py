import csv
import os
import sys
import time
from datetime import date, timedelta

import requests

API_KEY = os.environ.get("NASA_API_KEY", "DEMO_KEY")
TODAY = date.today()
START = os.environ.get("NEO_START", TODAY.isoformat())
END = os.environ.get("NEO_END", (TODAY + timedelta(days=3)).isoformat())
URL = "https://api.nasa.gov/neo/rest/v1/feed"
CSV_OUT = os.environ.get(
    "NEO_OUT",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "neo_feed.csv"),
)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def main():
    if API_KEY == "DEMO_KEY":
        log("NASA_API_KEY is not set; using DEMO_KEY (strict rate limits). Get a key at api.nasa.gov")
    log(f"Date range: {START} → {END}")
    log("Requesting NASA NeoWs feed…")

    try:
        r = requests.get(
            URL,
            params={"start_date": START, "end_date": END, "api_key": API_KEY},
            timeout=30,
        )
    except Exception as e:
        log(f"ERROR: request failed -> {e}")
        sys.exit(1)

    log(f"HTTP status: {r.status_code}")
    if r.status_code != 200:
        log(f"ERROR: unexpected status. Body: {r.text[:400]} ...")
        sys.exit(1)

    try:
        data = r.json()
    except Exception as e:
        log(f"ERROR: JSON parse failed -> {e}\nFirst 400 chars: {r.text[:400]} ...")
        sys.exit(1)

    if "near_earth_objects" not in data:
        log("ERROR: 'near_earth_objects' missing from the response.")
        sys.exit(1)

    neos_by_date = data["near_earth_objects"]
    total = sum(len(v) for v in neos_by_date.values())
    log(f"Total NEOs: {total}")

    for neo_date, neos in sorted(neos_by_date.items()):
        log(f"{neo_date} → {len(neos)}")

    log(f"Writing CSV: {CSV_OUT}")
    with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "date", "neo_id", "name",
            "estimated_diameter_m_min", "estimated_diameter_m_max",
            "is_potentially_hazardous",
            "close_approach_date", "rel_velocity_km_h", "miss_distance_km",
        ])

        for neo_date, neos in sorted(neos_by_date.items()):
            for neo in neos:
                try:
                    diam = neo["estimated_diameter"]["meters"]
                    dmin = diam["estimated_diameter_min"]
                    dmax = diam["estimated_diameter_max"]
                    hazard = neo.get("is_potentially_hazardous_asteroid", False)

                    cad = neo.get("close_approach_data", [])
                    if cad:
                        ca = cad[0]
                        ca_date = ca.get("close_approach_date_full") or ca.get("close_approach_date")
                        vel = ca["relative_velocity"]["kilometers_per_hour"]
                        miss = ca["miss_distance"]["kilometers"]
                    else:
                        ca_date, vel, miss = "", "", ""

                    w.writerow([
                        neo_date, neo.get("id", ""), neo.get("name", ""),
                        f"{dmin:.3f}", f"{dmax:.3f}",
                        hazard,
                        ca_date, vel, miss,
                    ])
                except Exception as e:
                    log(f"Warning: skipped one NEO row -> {e}")

    log(f"Done. CSV path: {os.path.abspath(CSV_OUT)}")


if __name__ == "__main__":
    main()
