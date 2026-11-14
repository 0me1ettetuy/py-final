# Verified training and analytics results — Topic 47

These numbers are transcribed directly from the **uploaded** Colab output archive `topic47_app_data.zip`, rechecked on 2026-11-14. They are **not fabricated**, but the full nationwide notebook was **not rerun** in this local environment.

## Model

- GPU used in uploaded run: **Tesla T4** (`cuda`)
- Task: **unsupervised neighbourhood POI-category profile reconstruction**; unsupervised reconstruction, not a supervised prediction.
- 10 input categories, 4-dimensional latent space, **5,838** trained parameters.
- Grid cells: **3,805** (train 2,478, validation 606, test 721); spatial-block grouping rather than random cell split.
- Best validation epoch: **70**; validation MSE 0.12640.

| Approach | Test MSE | Test MAE |
|---|---:|---:|
| Train-mean baseline | 1.08332 | 0.79297 |
| PCA baseline | 0.17093 | 0.30338 |
| **GPU Autoencoder** | **0.12963** | **0.24350** |

MSE improvement over PCA: **24.2%** in standardized log-transformed POI-count reconstruction space. Not classification accuracy and not DBSCAN performance.

## Dataset and quality

- POI entities: **126,778** (unique OSM keys 126,778).
- Region boundaries matched: **20/20**; unassigned POIs: **1,243** (do not silently drop from national totals).
- Missing POI names: **70,431**; invalid coordinates: **0**; duplicate OSM keys: **0**.
- Preprocessing memory: **57.44 MiB** baseline → **17.37 MiB** optimized.
- Official population snapshot in manifest: **2026-10-01**, total **20,633,529** people.

## DBSCAN (haversine, eps 0.5 km, min_samples 8)

| City region | Points clustered | Clusters | Sampled? | Noise share |
|---|---:|---:|---|---:|
| Astana | 9,411 | 25 | No | 2.1% |
| Almaty city | 12,000 | 45 | Yes | 4.3% |
| Shymkent | 3,256 | 20 | No | 10.9% |

Almaty city contains more mapped POIs than the 12,000 sampled for this clustering exercise; label all maps using the sampled result accordingly.

## Three-way processing benchmark (same regional-category grouping)

| Method | Runtime (s) | Peak process RSS (MiB) | Agrees with SQLite baseline? |
|---|---:|---:|---|
| sqlite | 0.124 | 17.6 | True |
| pandas | 0.942 | 131.1 | True |
| polars | 0.449 | 74.4 | True |

These are single-run measurements; do not overinterpret timings as universal speed rankings. The ZIP also contains H1/H2 hypothesis results, eight SQL scripts + outputs, regional CSV metrics, and Plotly HTML figures.

## Interpretation warnings

1. OpenStreetMap is crowdsourced. Mapped POI counts are not a complete real-world facility census.
2. The geographies here are 20 current first-level Kazakhstan administrative units; only Astana, Almaty and Shymkent are standalone city-regions. Do not label oblast totals as their namesake cities.
3. Nearest-neighbour and category-distribution tests assume independence in ways spatial data can violate; findings are exploratory, not causal.
4. OSM attribution / ODbL obligations apply to redistributed extracts and derivative datasets.
