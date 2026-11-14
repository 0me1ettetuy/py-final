# Codex CLI context — Topic 47, Kazakhstan OpenStreetMap POI Analytics

## Your role

Build the **finished, locally runnable Python Streamlit analytics application** and a clean GitHub-ready repository from the attached executed Jupyter notebook `Topic47_Colab_GPU_Executed.ipynb`, `TRAINING_RESULTS.md`, the included `outputs/` directory, and this context. **Do not redo the full analytical investigation, fabricate numeric results, or retrain the saved AI model on every app startup.** First inspect notebook source and outputs (if provided); adapt gracefully if the notebook was not yet executed.

The user's assigned topic is **#47: “OpenStreetMap Kazakhstan: Points of Interest Analytics”** (AAI-2605M), from **Cluster 8: Large-Scale Data Processing**. Goal: analyze types/densities of mapped amenities across Kazakhstan, compare Astana, Almaty, Shymkent and regions, calculate POIs per 100K residents, and demonstrate geographic DBSCAN clusters. Original data source: <https://download.geofabrik.de/asia/kazakhstan.html>.

## Mandatory university rubric — implement/retain all

1. Python 3 application split into modules with **at least 5 meaningful functions** beyond `main`, `list`/`dict`, `if/elif/else`, loops, file reading/writing, `try/except`.
2. A working UI: Streamlit dashboard with user-selectable filters (region, city, POI category, DBSCAN settings). Must show nonempty results with processed data and understandable errors without it.
3. Large data: PBF streaming via Osmium, Parquet conversion and dtype optimization, data-quality audit, missing/invalid/duplicates, **outliers evaluated but not automatically deleted**.
4. Three-way same-task comparison: **SQLite GROUP BY baseline**, **Pandas**, **Polars**; report wall time, peak process RSS, equality of aggregate results.
5. EDA plus **at least 4–5 charts**, with at least one interactive Plotly chart/map; >=2 data-backed hypotheses, with methods, p-values, effect sizes and limitations.
6. SQLite (or PostgreSQL), a normalized relational **ER diagram** and **at least eight SQL queries**, including `JOIN`, `GROUP BY/HAVING`, CTE/subqueries and window functions; results read into Pandas.
7. A README with one-command startup, `requirements.txt`, runnable tests, citations, report guidance, GitHub-ready layout. Written report and slide deck are separate required final university deliverables (do not claim they are created merely by building this app).

## Already implemented by the notebook

The notebook is intended to do the **data and analysis layer**:

- Download `kazakhstan-latest.osm.pbf` from Geofabrik; filter `amenity`, `shop`, `tourism`, `leisure` tags and ADM1 `admin_level=4` boundary relations with the `osmium` CLI; export streaming GeoJSONSeq.
- Preserve OSM entity keys `node:id`, `way:id`, `relation:id`; collapse polygon/line geometries to representative points; output raw POI Parquet.
- Load official **20-region population snapshot dated 2026-10-01** from Kazakhstan's Bureau of National Statistics (`stat.gov.kz/en/region/`, nationwide population **20,633,529**), and construct current region polygons from **the same OSM PBF**. **Do not use geoBoundaries Kazakhstan ADM1 as a substitute:** that source reports **2017 boundaries with only 16 units**, incompatible with 2026 Kazakhstan.
- Explicitly map region aliases and **fail** if some of the 20 regions do not match; `GeoPandas.sjoin(..., predicate="within")` assigns POIs; unmatched points remain null and are reported.
- Save regional total/count-per-100K/count-per-100-km² and category tables; compute Astana, Almaty, Shymkent comparisons; plot regional bar charts, category distributions, heatmap and interactive map.
- Test (H1) independence of city and POI category (chi-square / Cramér's V), (H2) Astana vs Almaty healthcare nearest-neighbor distances (haversine BallTree / Mann–Whitney U). Interpret p-values only as exploratory because OSM points are spatially dependent/nonrandom.
- DBSCAN per city using haversine, `eps=0.5 km`, `min_samples=8`; a city exceeding 12,000 points is sampled, and this **must be labelled as exploratory**.
- Create normalized SQLite dimension tables `region`, `category` and fact table `poi`, execute eight SQL queries, save SQL texts and query results.
- Benchmark SQLite baseline, Pandas and Polars; write `manifest.json`, QA report, figures and optional ZIP of processed outputs.

The **uploaded notebook was executed in Colab**, and all 27 original code cells have execution outputs, no recorded exceptions. Reported real outputs: 126,778 POIs, 20/20 regions matched, Tesla T4 training, 3,805 grid cells. The exported The exported `outputs/` directory is INCLUDED in this handoff. All model weights, Parquet, SQLite, and visualizations are present; do not request the data again. See `TRAINING_RESULTS.md` for measured outputs and interpretation caveats.

## Exact notebook output contract

The notebook creates `kazakhstan_poi_47/` under the working directory, with:

```text
kazakhstan_poi_47/
  data/raw/                        # huge and temporary: NOT for GitHub
    kazakhstan-latest.osm.pbf
    poi-filtered.osm.pbf
    adm1-filtered.osm.pbf
    poi.geojsonseq
    adm1.geojsonseq
    osmium-export-config.json
  outputs/
    poi_raw.parquet
    poi_enriched.parquet            # primary map/point dataset
    regions.geojson                # twenty OSM ADM1 geometries, EPSG:4326
    regions.csv                    # region dimension with population and area
    population_2026_10_01.csv
    region_stats.csv
    region_category.csv
    city_stats.csv
    regional_outliers_iqr.csv
    quality_report.json
    hypotheses.json
    hypothesis1_contingency.csv
    clusters.parquet
    clustering_report.json
    benchmark.csv
    kazakhstan_poi.sqlite
    manifest.json
    urban_autoencoder.pt            # fitted GPU model state + metadata
    urban_autoencoder_scaler.joblib # fitted StandardScaler
    pca_baseline.joblib             # comparison model
    urban_profile_kmeans.joblib     # fitted embedding clusters
    urban_grid_profiles.parquet     # cell-level features, latent vectors, labels
    gpu_model_report.json
    gpu_model_metrics.csv
    figures/*.html                 # nine-plus interactive Plotly files
    sql_results/*.sql              # exactly eight SQL scripts
    sql_results/*.csv              # query results
```

### Primary data schemas

**`outputs/poi_enriched.parquet`** (one row per retained OSM feature, not one row per amenity tag):

- `osm_key`: string unique PK, e.g. `node:123456` or `relation:125`, not just numeric ID.
- `osm_type`: string, one of `node`, `way`, `relation`.
- `osm_id`: int64.
- `name`: nullable string.
- `main_tag`: string `amenity|shop|tourism|leisure` (priority in this order).
- `subcategory`: string raw OSM tag value (`restaurant`, `school`, `supermarket`…).
- `category`: string broad group (`Food & drink`, `Healthcare`, `Education`, `Finance`, `Transport`, `Public services`, `Retail`, `Tourism`, `Recreation`, `Other amenities`).
- `latitude`, `longitude`: float64 EPSG:4326 representative coordinates.
- `geometry_type`: string OSM geometry shape before point conversion.
- `region_code`: nullable string one of the 20 official keys listed below.

**`outputs/region_stats.csv`**: `region_code`, `region_name`, `population`, `population_date`, `area_km2`, `poi_count`, `per_100k`, `per_100km2`, `density_iqr_outlier`.

**`outputs/region_category.csv`**: `region_code`, `category`, `poi_count`.

**`outputs/regions.geojson`**: FeatureCollection, CRS WGS84, properties `region_code`, `region_name`, `population`, `population_date`, `area_km2`, and Polygon/MultiPolygon geometry.

**`outputs/clusters.parquet`**: `osm_key`, `cluster_city`, `cluster_id` (`-1` means DBSCAN noise), `latitude`, `longitude`, `category`. `cluster_city` is a region code.

**`outputs/benchmark.csv`**: `approach`, `time_seconds`, `peak_process_rss_mib`, `matches_baseline`.

**`outputs/quality_report.json`**: quality metrics including counts of missing names, absent region assignments, invalid coordinates and duplicate OSM keys.

**`outputs/manifest.json`**: sources, file availability/sizes, methodology, provenance, limitations.

**SQLite schema**:

```sql
CREATE TABLE region(region_code TEXT PRIMARY KEY, region_name TEXT UNIQUE,
  population INTEGER, population_date TEXT, area_km2 REAL);
CREATE TABLE category(category_name TEXT PRIMARY KEY);
CREATE TABLE poi(osm_key TEXT PRIMARY KEY, osm_type TEXT, osm_id INTEGER, name TEXT,
  main_tag TEXT, subcategory TEXT, category_name TEXT REFERENCES category(category_name),
  region_code TEXT REFERENCES region(region_code), latitude REAL, longitude REAL,
  geometry_type TEXT);
```

Canonical 20 region codes: `astana`, `almaty_city`, `shymkent`, `almaty_region`, `aktobe`, `atyrau`, `akmola`, `west_kazakhstan`, `east_kazakhstan`, `zhambyl`, `karaganda`, `kostanay`, `kyzylorda`, `mangystau`, `north_kazakhstan`, `pavlodar`, `turkistan`, `abay`, `zhetisu`, `ulytau`.

**Important scope:** Other non-capital cities must have separate verified municipal polygons and separate city population data to support city-specific per-capita comparisons. **Do not relabel entire oblast counts as counts for Karaganda city, Aktobe city, etc.** Simple nearest-radius estimates are allowed only if explicitly labelled, without per-100k denominators.

## Streamlit app requirements

Build polished but light UI, no dependence on external map tokens, use Plotly MapLibre/open OSM-based view, sensible markers and fast filters. Use `st.cache_data` / `st.cache_resource` appropriately, and avoid loading 200MB PBF in app.

Suggested navigation (can be tabs/pages):

- **Overview:** dataset snapshot / source attribution, total mapped POIs, 20 regions, 3 city-region comparisons, category coverage. KPI cards are derived from data, not hardcoded.
- **Regional analysis:** Plotly rankings by total count, per 100k residents, per 100 km², regional choropleth built from `regions.geojson`. Switch between normalized metrics.
- **Cities:** Astana/Almaty/Shymkent category comparisons, totals, per 100k, relative shares; demonstrate effect of different denominators.
- **Interactive map:** select region/city and one/multiple categories; show sampled POI points (limit 2,500 or configurable) to avoid UI memory exhaustion; label sampling in the UI and avoid claiming map displays all points.
- **Clustering:** visualize precomputed DBSCAN points for one city and read the report; show `eps`, `min_samples`, sample warning; optional live rerun only on a capped subset.
- **Quality, Methods & SQL:** show missingness, outliers, test results, benchmark table, query results and downloadable CSVs; ER diagram as image/Markdown/Mermaid if supported.
- **AI neighbourhood profiles:** visualize `urban_grid_profiles.parquet` cells colored by `profile_cluster`, show a four-dimensional embedding and its source POI category counts. Display GPU Autoencoder vs PCA vs train-mean baseline test MSE/MAE from saved CSV. Clarify that this is unsupervised feature reconstruction, not geographic DBSCAN or supervised classification. Inference should reuse the saved category order, `log1p` transform, train-fitted scaler, and encoder weights.

Required behavior: high-quality empty-state messages, exception handling when output files are missing; graceful handling of no matches; caching; filter validation; no misleading absolute claims. List exact data snapshot date/region version and OSM/ODbL credit in UI.

## Implementation plan for Codex

1. Inspect and understand the entire supplied executed notebook first. Use the already-extracted `outputs/` directory. Confirm its schema matches the contract and reconcile differences if necessary.
2. Create `app.py`, `src/` modules (`data_loader.py`, `analytics.py`, `plots.py`, `map_view.py`, `db.py`, `utils.py` or similar), `tests/`, `requirements.txt`, `README.md`, `.gitignore`, `docs/er_diagram.md`.
3. Implement robust app pages with efficient data loading; read all numbers from real notebook outputs or SQL, never fabricate.
4. Add unit tests that create **tiny synthetic temporary CSV/SQLite/Parquet fixtures** (do not pretend these are real findings). Test region filtering, rate-per-100K, category aggregations, missing file errors, SQL equivalence and mapping/cluster IDs.
5. Add a `scripts/validate_outputs.py` that checks schemas, 20 regions, FK consistency, unique IDs, population total, SQL query count, and that all benchmark modes match.
6. Document `python -m venv .venv && pip install -r requirements.txt`, followed by `streamlit run app.py`; document how to run notebook and copy or unzip `outputs/` into `outputs/` (or configure `POI_OUTPUT_DIR`).
7. Run `python -m pytest -q`, `python -m compileall -q .`, and start Streamlit locally if outputs are available; fix failures. Do not claim national results without output files.
8. Make the repo GitHub-ready, with `.gitignore` excluding `.osm.pbf`, `.geojsonseq`, large raw archives, `.venv`, `__pycache__`; decide and document a reproducible data distribution strategy for the 24 MB SQLite database, 4 MB processed Parquet, 3 MB regions GeoJSON, and small trained checkpoint (all already available in `outputs/`), including ODbL obligations. The GitHub clone should start with bundled data if you commit it, or have a clearly documented download step; include attribution and a small sample fixture so tests run in CI.
9. If asked to push to GitHub, do so only through authorized user repo access/CLI configuration. Do not make up a repository URL or assert a push occurred without confirmation.

## Acceptance criteria

- `streamlit run app.py` loads real `outputs/` and lets me filter regions, categories and three city-regions, view charts and maps, query SQL, inspect clusters/quality/benchmarks.
- App shows an actionable “run notebook first / point to output folder” message if datasets are absent (not a crash).
- SQL query count >=8 and demonstrated joins, CTE/window functions; app is modular, documented, and testable.
- All chart/data values are computed from notebook outputs and remain traceable to source snapshot.
- 20-region coverage is checked and **population 20,633,529 (2026-10-01)** is referenced accurately; no outdated 16-region polygons.
- Attribution: “© OpenStreetMap contributors, ODbL 1.0; PBF extract by Geofabrik”, and Kazakhstan Bureau of National Statistics for population.

## One-message instruction to paste into Codex CLI

> Read `CODEX_CONTEXT.md`, `TRAINING_RESULTS.md` and the executed `Topic47_Colab_GPU_Executed.ipynb`. Use the already-extracted `outputs/` directory. Build a GitHub-ready modular Streamlit app with regional analytics, maps, SQL, geographic DBSCAN, and the trained autoencoder neighbourhood profile visualization. Implement tests, README, dependencies, ER diagram, attribution and validation; run tests and fix failures. Never fabricate data or retrain on each app launch.

## Sources to cite in README/report

- Course PDF supplied by the user: *Темы_финальных_проектов_AI.pdf*, Topic 47 p.24, Cluster 8 p.21–22, general requirements pp.29–34.
- Geofabrik Kazakhstan: https://download.geofabrik.de/asia/kazakhstan.html
- Geofabrik/OpenStreetMap download/license: https://www.geofabrik.de/en/data/download.html
- Kazakhstan BNS regional population: https://stat.gov.kz/en/region/ (as of October 1, 2026).
- Osmium CLI docs: https://docs.osmcode.org/osmium/latest/osmium-export.html and https://github.com/osmcode/osmium-tool/blob/master/man/osmium-tags-filter.md
- GeoPandas spatial join: https://geopandas.org/en/latest/docs/reference/api/geopandas.GeoDataFrame.sjoin.html
- Note: geoBoundaries KAZ ADM1 available at https://www.geoboundaries.org/api/current/gbOpen/KAZ/ADM1/ reports 16 units for 2017, so avoid it for current comparative rates.


## This handoff has been verified (2026-11-14)

- All 52 ZIP members extracted successfully, and archive integrity passed.
- `outputs/kazakhstan_poi.sqlite` opens and contains `region=20`, `category=10`, `poi=126778`; `PRAGMA foreign_key_check` returned no violations.
- `outputs/urban_autoencoder.pt` loads via `torch.load(..., map_location="cpu", weights_only=True)`; state dictionary has 12 tensors, `input_dim=10`, `latent_dim=4`.
- `outputs/benchmark.csv` ACTUAL results for this run: SQLite **0.124 s / 17.6 MiB**, Pandas **0.942 s / 131.1 MiB**, Polars **0.449 s / 74.4 MiB**. Earlier note(s) had different measured values from a previous run; prefer files inside `outputs/`.
- The three DBSCAN city counts are Astana=25, Almaty city=45 (sampled at 12,000), Shymkent=20; cluster IDs are specific to each city and are distinct from KMeans neighbourhood profile labels.
- This environment did not have a Parquet reader installed for an independent read, though the notebook execution and ZIP export contain the Parquet datasets. The app should validate schemas when it runs with `pyarrow`.

### Be careful with model inference

`urban_autoencoder.pt` stores a PyTorch `state_dict`, not a pickled `torch.nn.Module`. Recreate the `AmenityAutoencoder` class from notebook cell 16, with encoder `Linear(10,64)->ReLU->Linear(64,32)->ReLU->Linear(32,4)` and matching symmetric decoder; then load `state_dict` with `weights_only=True` and `map_location="cpu"`. The model expects inputs ordered according to `categories` in its checkpoint, transformed via `np.log1p(counts)` followed by the saved `StandardScaler`. Do not fit a new scaler on app data. For the first dashboard implementation, plot the precomputed `urban_grid_profiles.parquet` rather than forcing the checkpoint to run inference on every page load.

## Final submission deliverables

- [ ] GitHub repository link containing the source code, `README.md` run instructions, and either the data files or a link to the data source.
- [ ] Written report covering the data, methods, results, and conclusions.
- [ ] Presentation submitted as `.pptx` or `.pdf`.
