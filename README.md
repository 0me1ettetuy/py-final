# Kazakhstan OpenStreetMap POI Analytics

Streamlit dashboard for Topic 47, analyzing 126,778 mapped OpenStreetMap points of interest across Kazakhstan's 20 current ADM1 regions.

## Run

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python scripts/validate_outputs.py
streamlit run app.py
```

The supplied `outputs/` directory is used by default. To store it elsewhere, set `POI_OUTPUT_DIR` to that directory before running Streamlit.

## What is included

- Regional totals, per-100K and land-area-normalized POI comparisons.
- Astana, Almaty city, and Shymkent category comparisons.
- Filtered, sampled interactive OSM-base-map POI view.
- Precomputed geographic DBSCAN results, quality audit, hypothesis outputs, eight saved SQLite queries, and three-way benchmark.
- Precomputed unsupervised neighbourhood-profile embedding and its saved model metrics. It is not a classifier.

## Data and attribution

The processed artifacts in `outputs/` came from the Kazakhstan Geofabrik extract and the Kazakhstan Bureau of National Statistics regional population snapshot dated 2026-10-01. Original PBF: [Geofabrik Kazakhstan](https://download.geofabrik.de/asia/kazakhstan.html). Population source: [Kazakhstan BNS](https://stat.gov.kz/en/region/).

© OpenStreetMap contributors, [ODbL 1.0](https://www.openstreetmap.org/copyright); PBF extract by Geofabrik. The app reports mapped OSM features, not a complete inventory of real facilities. See `CODEX_CONTEXT.md` for methods, data limitations, and artifact contract.

## Development checks

```bash
python -m pytest -q
python -m compileall -q app.py src scripts
```

## Push to GitHub

After Git is initialized, create an empty GitHub repository, then run:

```bash
git add .
git commit -m "Initial Kazakhstan OSM POI dashboard"
git branch -M main
git remote add origin <YOUR-REPOSITORY-URL>
git push -u origin main
```

The processed `outputs/` artifacts are small enough for a normal GitHub repository; raw PBF and temporary extraction files are ignored. See `outputs/README.md` for provenance and redistribution obligations.

## Submission checklist

- [ ] GitHub repository link with source code, this README, and data files or a source-data link.
- [ ] Written report: data, methods, results, conclusions.
- [ ] Presentation (`.pptx` or `.pdf`).
