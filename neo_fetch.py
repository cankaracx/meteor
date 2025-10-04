import sys, json, csv, os, time
from datetime import datetime
import requests

API_KEY = "njGUd5KQp3qvKmRseVn2wR3kmeqGKMg3r9WlM07g"  # senin key
START = "2025-10-01"
END   = "2025-10-04"
URL   = "https://api.nasa.gov/neo/rest/v1/feed"
CSV_OUT = "neo_feed.csv"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def main():
    log("Başlıyorum…")
    log(f"Tarih aralığı: {START} → {END}")
    log("İstek atılıyor…")

    try:
        r = requests.get(URL, params={
            "start_date": START,
            "end_date": END,
            "api_key": API_KEY
        }, timeout=30)
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

    # Ekrana kısa özet
    for date, neos in sorted(neos_by_date.items()):
        log(f"{date} → {len(neos)} adet")

    # CSV yaz
    log(f"CSV yazılıyor: {CSV_OUT}")
    with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "date", "neo_id", "name", 
            "estimated_diameter_m_min", "estimated_diameter_m_max",
            "is_potentially_hazardous",
            "close_approach_date", "rel_velocity_km_h", "miss_distance_km"
        ])

        for date, neos in sorted(neos_by_date.items()):
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
                        date, neo.get("id",""), neo.get("name",""),
                        f"{dmin:.3f}", f"{dmax:.3f}",
                        hazard,
                        ca_date, vel, miss
                    ])
                except Exception as e:
                    log(f"Uyarı: bir NEO satırı yazılamadı -> {e}")

    log("Bitti ✅")
    log(f"CSV dosyası konum: {os.path.abspath(CSV_OUT)}")

if __name__ == "__main__":
    main()
