"""Download NASA NeoWs close-approach data into neo_feed.csv."""
import argparse
import csv
import os
import sys
import time
from datetime import date, timedelta

import requests

URL = "https://api.nasa.gov/neo/rest/v1/feed"
MAX_SPAN_DAYS = 7


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def parse_args() -> argparse.Namespace:
    today = date.today()
    parser = argparse.ArgumentParser(
        description="Fetch NASA NEO close approaches into a CSV the simulator can load."
    )
    parser.add_argument(
        "--start",
        default=os.environ.get("NEO_START", today.isoformat()),
        help="Start date YYYY-MM-DD (default: today)",
    )
    parser.add_argument(
        "--end",
        default=os.environ.get("NEO_END", (today + timedelta(days=3)).isoformat()),
        help="End date YYYY-MM-DD (default: today + 3 days, max 7-day span)",
    )
    parser.add_argument(
        "--out",
        default=os.environ.get("NEO_CSV_OUT", "neo_feed.csv"),
        help="Output CSV path",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("NASA_API_KEY", "DEMO_KEY"),
        help="NASA API key. Set NASA_API_KEY, or pass --api-key. DEMO_KEY is rate-limited.",
    )
    return parser.parse_args()


def clamp_end(start: str, end: str) -> str:
    try:
        start_d = date.fromisoformat(start)
        end_d = date.fromisoformat(end)
    except ValueError:
        log("HATA: Dates must be YYYY-MM-DD.")
        sys.exit(1)
    if end_d < start_d:
        log("HATA: End date is before start date.")
        sys.exit(1)
    max_end = start_d + timedelta(days=MAX_SPAN_DAYS)
    if end_d > max_end:
        log(f"NeoWs allows at most {MAX_SPAN_DAYS} days; clamping end to {max_end.isoformat()}.")
        return max_end.isoformat()
    return end


def main() -> None:
    args = parse_args()
    start, end, out, api_key = args.start, clamp_end(args.start, args.end), args.out, args.api_key

    log("Başlıyorum…")
    log(f"Tarih aralığı: {start} → {end}")
    log("İstek atılıyor…")

    try:
        r = requests.get(
            URL,
            params={"start_date": start, "end_date": end, "api_key": api_key},
            timeout=30,
        )
    except Exception as e:
        log(f"HATA: İstek atılamadı -> {e}")
        sys.exit(1)

    log(f"HTTP durum kodu: {r.status_code}")
    if r.status_code != 200:
        log(f"HATA: Beklenmeyen durum kodu. Gövde: {r.text[:400]} ...")
        sys.exit(1)

    try:
        data = r.json()
    except Exception as e:
        log(f"HATA: JSON parse edilemedi -> {e}\nİlk 400 karakter: {r.text[:400]} ...")
        sys.exit(1)

    if "near_earth_objects" not in data:
        log("HATA: 'near_earth_objects' alanı yok. Yanıt biçimi beklenenden farklı.")
        sys.exit(1)

    neos_by_date = data["near_earth_objects"]
    total = sum(len(v) for v in neos_by_date.values())
    log(f"Toplam NEO sayısı: {total}")

    for day, neos in sorted(neos_by_date.items()):
        log(f"{day} → {len(neos)} adet")

    log(f"CSV yazılıyor: {out}")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "date", "neo_id", "name",
            "estimated_diameter_m_min", "estimated_diameter_m_max",
            "is_potentially_hazardous",
            "close_approach_date", "rel_velocity_km_h", "miss_distance_km",
        ])

        for day, neos in sorted(neos_by_date.items()):
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
                        day, neo.get("id", ""), neo.get("name", ""),
                        f"{dmin:.3f}", f"{dmax:.3f}",
                        hazard,
                        ca_date, vel, miss,
                    ])
                except Exception as e:
                    log(f"Uyarı: bir NEO satırı yazılamadı -> {e}")

    log("Bitti")
    log(f"CSV dosyası konum: {os.path.abspath(out)}")


if __name__ == "__main__":
    main()
