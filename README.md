# Meteor Impact Simulator

Desktop Tkinter app that estimates impact energy, a visual crater, city-level casualties, and emergency logistics for a strike on Turkey.

## Run

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python meteor_v12.py
```

Pillow is optional and only needed for the Turkey map in **Seismic Map**.

## NASA close-approach presets

`neo_fetch.py` downloads a few days of NASA NeoWs data into `neo_feed.csv`. The feed API allows at most 7 days per request. Defaults are **today → today + 3 days**.

```bash
# Rate-limited public demo key (fine for occasional use):
python neo_fetch.py

# Your own key and dates:
python neo_fetch.py --api-key YOUR_KEY --start 2026-09-07 --end 2026-09-10 --out neo_feed.csv
```

`NASA_API_KEY`, `NEO_START`, `NEO_END`, and `NEO_CSV_OUT` environment variables are also accepted. Then use **Load NASA CSV** in the app.

## Using the app

1. Enter diameter / velocity / density, or pick a preset, then **IMPACT**.
2. Click a column heading on the 81-city table to sort (default: highest casualties first). **Export table (CSV)** saves the current run.
3. **Seismic Map** — drag to pan, scroll to zoom, click a city (without dragging) to draw rings. Panning no longer selects a city.
4. **Needs Planner** estimates tents, water, calories, and kits; **CSV kaydet** writes the table.

Map files (`turkey_map.gif` / `Turkey_location_map.gif`) are optional and resolved next to the script or a packaged `.exe`.
