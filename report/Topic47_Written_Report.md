# OpenStreetMap Kazakhstan: Points of Interest Analytics

**Course:** AAI-2605M  
**Topic:** 47 — OpenStreetMap Kazakhstan: Points of Interest Analytics  
**Student:** _[add your name and student ID]_  
**Date:** _[add submission date]_  
**Source repository:** _[add your GitHub repository URL before submission]_

## Abstract

This project analyzes the geographic distribution and composition of mapped points of interest (POIs) in Kazakhstan using OpenStreetMap (OSM). The delivered processing run retained 126,778 uniquely identified OSM entities across 20 current first-level administrative regions. Regional totals, rates per 100,000 residents, land-area-normalized rates, city-region category mixes, exploratory statistical tests, geographic DBSCAN clusters, SQLite queries, and an unsupervised neighbourhood-profile model are exposed through a Streamlit dashboard. The results describe OSM mapping coverage rather than a complete census of real-world facilities.

## 1. Data

### 1.1 Sources

- **POIs and boundaries:** Kazakhstan extract from [Geofabrik](https://download.geofabrik.de/asia/kazakhstan.html), derived from OpenStreetMap.
- **Population:** Kazakhstan Bureau of National Statistics regional data, snapshot **2026-10-01**: [stat.gov.kz/en/region](https://stat.gov.kz/en/region/).
- **License and attribution:** © OpenStreetMap contributors, ODbL 1.0; PBF extract by Geofabrik.

The original PBF was 226.3 MB. The app uses preprocessed files in `outputs/`, so it does not download the raw extract or train a model on startup.

### 1.2 Unit of analysis and coverage

Each row represents one retained OSM node, way, or relation. When an entity was a polygon or line, its representative point was used for point-based analysis. Entity keys preserve OSM type and ID, for example `node:12345`; this avoids collisions between object types. The broad category priority was `amenity`, then `shop`, `tourism`, and `leisure`.

| Measure | Value |
|---|---:|
| Retained POI entities | 126,778 |
| Unique OSM keys | 126,778 |
| Current ADM1 regions matched | 20 / 20 |
| Population denominator | 20,633,529 |
| Population snapshot | 2026-10-01 |
| Broad POI categories | 10 |
| POIs without a matched region | 1,243 |
| POIs without a name | 70,431 |
| Invalid coordinates | 0 |
| Duplicate OSM keys | 0 |

The 1,243 spatially unmatched POIs remain in national totals; they are not silently deleted.

## 2. Methods

### 2.1 Processing and quality checks

The notebook streams the Geofabrik PBF with Osmium, filters relevant tags and ADM1 relations, converts output to Parquet, and optimizes data types. Current OSM administrative-level-4 polygons are explicitly matched to 20 official region codes. A spatial `within` join assigns each POI to a region. The quality audit checks missing names and regions, invalid coordinates, duplicate OSM keys, and IQR density outliers. Outliers are reported, not automatically removed.

### 2.2 Regional and city-region measures

For every region, the analysis calculates total mapped POIs, POIs per 100,000 population, and POIs per 100 km². City-region comparisons are limited to Astana, Almaty city, and Shymkent because they are standalone first-level regions with compatible population denominators. The project does not relabel oblast-wide totals as counts for their namesake municipalities.

### 2.3 Database and performance comparison

The normalized SQLite database contains `region`, `category`, and `poi` tables. Eight saved SQL queries demonstrate joins, grouped queries, a CTE, subqueries, and window functions; their results are read into Pandas. The same regional-category aggregation is compared using SQLite, Pandas, and Polars.

| Method | Runtime (s) | Peak process RSS (MiB) | Matches SQLite baseline |
|---|---:|---:|---|
| SQLite | 0.124 | 17.6 | Yes |
| Pandas | 0.942 | 131.1 | Yes |
| Polars | 0.449 | 74.4 | Yes |

These are single-run measurements in this processing environment, not universal speed rankings.

### 2.4 Exploratory inference and clustering

H1 tests whether the category distribution is the same in the three city-regions, using a chi-square test and Cramér's V. H2 compares nearest-neighbour healthcare distances between Astana and Almaty city with a Mann–Whitney U test. Geographic DBSCAN uses haversine distance, ε = 0.5 km, and `min_samples = 8`.

| Test | Result | Interpretation |
|---|---:|---|
| H1: city-region category distributions are equal | χ²(18) = 1163.80, p = 6.37 × 10⁻²³⁶, Cramér's V = 0.127 | Reject equal distributions; association is small by this effect size. |
| H2: Astana and Almaty healthcare nearest-neighbour distances are equal | U = 188,605, p = 0.00345 | Reject equal distributions; medians are 0.1269 km (Astana, n=408) and 0.1034 km (Almaty, n=839). |

Both tests are exploratory: POIs are spatially dependent and should not be treated as random independent observations.

### 2.5 Neighbourhood profile model

The project includes a GPU-trained autoencoder for unsupervised reconstruction of category-count profiles in 2 km urban grid cells. The input has ten categories, uses `log1p` counts and a training-fitted scaler, and is compressed to a four-dimensional latent vector. The split uses 10 km spatial blocks: 2,478 train cells, 606 validation cells, and 721 test cells (3,805 total). It is not a classifier and is separate from DBSCAN.

| Method | Test MSE | Test MAE |
|---|---:|---:|
| Train-mean baseline | 1.08332 | 0.79297 |
| PCA baseline | 0.17093 | 0.30338 |
| GPU autoencoder | 0.12963 | 0.24350 |

The autoencoder improves MSE by 24.2% over PCA in standardized log-count reconstruction space.

## 3. Results

### 3.1 National POI composition

Retail is the largest mapped category (31,767 POIs), followed by Other amenities (20,424), Recreation (17,139), and Transport (16,582). The smallest broad categories are Finance (5,439) and Healthcare (5,711). These are counts of OSM features, not a statement that one category has more real facilities nationwide.

### 3.2 Regional comparison

Almaty city has the highest total mapped POIs (23,460) and the highest population-normalized rate (980.7 per 100,000 people). Astana city has 9,411 mapped POIs (551.3 per 100,000), while Shymkent has 3,256 (246.5 per 100,000). Almaty city's compact administrative area also produces the highest area-normalized value (3,333.2 POIs per 100 km²). The dashboard permits switching between all three metrics because each describes a different aspect of mapping concentration.

### 3.3 City-region composition and DBSCAN

The city-region category distributions visibly differ, consistent with H1. DBSCAN found 25 clusters in Astana (9,411 points; 2.1% noise), 45 in Almaty city (12,000-point sample; 4.3% noise), and 20 in Shymkent (3,256 points; 10.9% noise). Almaty has more mapped POIs than the sample used for DBSCAN, so its result must be labelled exploratory.

### 3.4 Dashboard outcome

The Streamlit application provides an overview, regional rankings and choropleth, city-region composition, sampled interactive POI map, DBSCAN maps, quality/method/SQL results, and the precomputed autoencoder embedding. It reads only the processed outputs and gives a clear setup error if they are absent.

## 4. Conclusions

1. OpenStreetMap supports reproducible regional POI comparison when feature identity, current boundaries, and population denominators are handled explicitly.
2. Almaty city leads the supplied mapping-based total and per-capita indicators, but this should be interpreted as mapped coverage rather than a service census.
3. The three standalone city-regions have statistically distinguishable category mixes, though the measured association is small and inference is exploratory.
4. The autoencoder reconstructs neighbourhood category profiles better than the PCA and mean baselines, but it does not predict facilities or replace geographic clustering.
5. The SQLite baseline, Pandas, and Polars produce equal aggregation results; SQLite was fastest and used the least measured RSS in this run.

## 5. Limitations and future work

- OSM completeness varies geographically and over time.
- OSM entities can represent the same real establishment more than once (for example, node and area tagging).
- Population data and OSM extract dates are not identical.
- Only the three standalone city-regions have valid city-level denominators in this project.
- Spatial autocorrelation weakens conventional independent-observation interpretations of p-values.
- Additional verified municipal polygons and municipal populations would be needed for sound comparisons of other cities.

## References

1. Geofabrik. *Kazakhstan OSM extract*. https://download.geofabrik.de/asia/kazakhstan.html
2. OpenStreetMap contributors. *OpenStreetMap copyright and ODbL*. https://www.openstreetmap.org/copyright
3. Kazakhstan Bureau of National Statistics. *Regional population statistics*. https://stat.gov.kz/en/region/
4. Osmium Tool. *Osmium export documentation*. https://docs.osmcode.org/osmium/latest/osmium-export.html
5. GeoPandas. *GeoDataFrame.sjoin*. https://geopandas.org/en/latest/docs/reference/api/geopandas.GeoDataFrame.sjoin.html

## Reproducibility

Run `python scripts/validate_outputs.py` to validate the delivered outputs, then `streamlit run app.py` to launch the dashboard. The repository README has the complete setup and GitHub push instructions.
