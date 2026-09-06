# Meteor Impact Simulator

Desktop (Tkinter) classroom tool for exploring “what if this asteroid hit Turkey?” scenarios. It is a demonstration model, not a scientific impact forecast.

## What it does

1. Enter meteor diameter (m), velocity (km/s), and density (kg/m³), or pick a preset (Chelyabinsk, Chicxulub, NASA NEOs from CSV).
2. **IMPACT** estimates kinetic energy (Mt TNT), a demo-scale crater, Hiroshima equivalent, and a damage label.
3. Fills an 81-province table with estimated casualties, **sorted by severity** (highest first) and capped by 2024 population.
4. **Seismic Map** — Turkey map with damage rings, zoom, and pan.
5. **Needs Planner** — water, tents, medkits, and other supplies over N days.

Crater size and casualty numbers are simplified teaching formulas, not real physics.

## Run

Python 3.10+ with Tkinter (included on most desktop Python installs).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python meteor_v12.py
```

Optional files in this folder:

- `neo_feed.csv` — NASA near-Earth object presets (create with `neo_fetch.py`)
- `turkey_map.gif` — background for the Seismic Map

## Refresh NASA asteroid data

Get a free key at [api.nasa.gov](https://api.nasa.gov). The NASA feed endpoint accepts at most a 7-day window.

```bash
export NASA_API_KEY=your_key
# optional: NEO_START=2026-09-06 NEO_END=2026-09-09
python neo_fetch.py
```

Then use **Load NASA CSV** in the app (or restart). Without `NASA_API_KEY` the script uses `DEMO_KEY`, which is rate-limited.

## Build a Windows exe

```bash
pip install pyinstaller
pyinstaller meteor_v12.spec
```

`resource_path()` looks next to the script in development and next to the exe / PyInstaller bundle when frozen.

## Requirements

- `requests` — NASA fetch script
- `pillow` — optional map image in Seismic Map
- `tkinter` — standard library (not listed)
