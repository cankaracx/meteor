import argparse
import csv
import os
import sys
import tempfile
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import requests

URL = "https://api.nasa.gov/neo/rest/v1/feed"
CSV_FIELDS = [
    "date",
    "neo_id",
    "name",
    "estimated_diameter_m_min",
    "estimated_diameter_m_max",
    "is_potentially_hazardous",
    "close_approach_date",
    "rel_velocity_km_h",
    "miss_distance_km",
]

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as error:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD") from error

def fetch_feed(start, end, api_key, session=requests):
    try:
        response = session.get(
            URL,
            params={
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "api_key": api_key,
            },
            timeout=(5, 30),
        )
        response.raise_for_status()
    except requests.RequestException as error:
        raise RuntimeError(f"NASA request failed: {error}") from error

    try:
        payload = response.json()
    except requests.JSONDecodeError as error:
        raise RuntimeError("NASA returned an unreadable response") from error
    if not isinstance(payload.get("near_earth_objects"), dict):
        raise RuntimeError("NASA response is missing near_earth_objects")
    return payload

def rows_from_feed(payload):
    rows = []
    skipped = 0
    for feed_date, objects in sorted(payload["near_earth_objects"].items()):
        for neo in objects:
            try:
                diameter = neo["estimated_diameter"]["meters"]
                approaches = neo.get("close_approach_data") or []
                approach = next(
                    (
                        item
                        for item in approaches
                        if item.get("close_approach_date") == feed_date
                    ),
                    approaches[0] if approaches else {},
                )
                rows.append(
                    {
                        "date": feed_date,
                        "neo_id": neo.get("id", ""),
                        "name": neo.get("name", ""),
                        "estimated_diameter_m_min": f"{float(diameter['estimated_diameter_min']):.3f}",
                        "estimated_diameter_m_max": f"{float(diameter['estimated_diameter_max']):.3f}",
                        "is_potentially_hazardous": bool(
                            neo.get("is_potentially_hazardous_asteroid", False)
                        ),
                        "close_approach_date": approach.get(
                            "close_approach_date_full",
                            approach.get("close_approach_date", ""),
                        ),
                        "rel_velocity_km_h": approach.get(
                            "relative_velocity", {}
                        ).get("kilometers_per_hour", ""),
                        "miss_distance_km": approach.get("miss_distance", {}).get(
                            "kilometers", ""
                        ),
                    }
                )
            except (KeyError, TypeError, ValueError):
                skipped += 1
    return rows, skipped

def write_csv(rows, output_path):
    output_path = Path(output_path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            newline="",
            encoding="utf-8",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as output:
            temp_name = output.name
            writer = csv.DictWriter(output, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temp_name, output_path)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)
    return output_path

def build_parser():
    parser = argparse.ArgumentParser(
        description="Download NASA near-Earth object data for the simulator."
    )
    parser.add_argument(
        "--start",
        type=parse_date,
        default=date.today(),
        help="first feed date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--days",
        type=int,
        choices=range(1, 8),
        default=4,
        metavar="1-7",
        help="number of feed days to request (default: 4)",
    )
    parser.add_argument(
        "--output",
        default=Path(__file__).resolve().with_name("neo_feed.csv"),
        help="CSV destination (default: next to this script)",
    )
    return parser

def main(argv=None):
    args = build_parser().parse_args(argv)
    end = args.start + timedelta(days=args.days - 1)
    api_key = os.environ.get("NASA_API_KEY", "DEMO_KEY").strip() or "DEMO_KEY"

    log(f"Fetching NASA NEOs: {args.start} → {end}")
    if api_key == "DEMO_KEY":
        log("NASA_API_KEY is not set; using NASA's rate-limited DEMO_KEY")
    try:
        payload = fetch_feed(args.start, end, api_key)
        for feed_date, objects in sorted(payload["near_earth_objects"].items()):
            log(f"{feed_date}: {len(objects)} objects")
        rows, skipped = rows_from_feed(payload)
        output_path = write_csv(rows, args.output)
    except RuntimeError as error:
        log(f"ERROR: {error}")
        return 1
    except OSError as error:
        log(f"ERROR: could not write CSV: {error}")
        return 1

    log(f"Saved {len(rows)} objects to {output_path}")
    if skipped:
        log(f"Skipped {skipped} malformed objects")
    return 0

if __name__ == "__main__":
    sys.exit(main())
