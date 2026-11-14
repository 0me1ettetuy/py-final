from __future__ import annotations

import pandas as pd
import streamlit as st

from src.analytics import CITY_CODES, category_counts, city_category_shares, filter_pois, map_sample
from src.data_loader import (
    OutputDataError,
    available_sql_queries,
    load_csv,
    load_geojson,
    load_json,
    load_parquet,
    output_paths,
    read_sql_query,
    require_outputs,
)
from src.plots import (
    category_bar,
    city_mix,
    cluster_map,
    poi_map,
    profile_embedding,
    regional_choropleth,
    regional_ranking,
)


st.set_page_config(page_title="Kazakhstan OSM POI Analytics", page_icon="🗺️", layout="wide")


@st.cache_data(show_spinner=False)
def csv_data(root: str, name: str) -> pd.DataFrame:
    return load_csv(output_paths(root), name)


@st.cache_data(show_spinner=False)
def json_data(root: str, name: str) -> dict | list:
    return load_json(output_paths(root), name)


@st.cache_data(show_spinner=False)
def parquet_data(root: str, name: str) -> pd.DataFrame:
    return load_parquet(output_paths(root), name)


def fmt_number(value: int | float) -> str:
    return f"{value:,.0f}"


def main() -> None:
    paths = output_paths()
    try:
        require_outputs(paths)
        root = str(paths.root.resolve())
        manifest = json_data(root, "manifest.json")
        regions = csv_data(root, "region_stats.csv")
        region_categories = csv_data(root, "region_category.csv")
        cities = csv_data(root, "city_stats.csv")
    except OutputDataError as error:
        st.title("Kazakhstan OSM POI Analytics")
        st.error(str(error))
        st.code("POI_OUTPUT_DIR=/path/to/outputs streamlit run app.py")
        return

    st.title("Kazakhstan OpenStreetMap POI Analytics")
    st.caption(
        f"OSM snapshot via Geofabrik · population snapshot {manifest['population_date']} · "
        "© OpenStreetMap contributors, ODbL 1.0; extract by Geofabrik"
    )
    tabs = st.tabs(["Overview", "Regional analysis", "Cities", "Map", "Clustering", "Methods & SQL", "AI profiles"])

    with tabs[0]:
        quality = json_data(root, "quality_report.json")
        categories = len(quality["category_counts"])
        cards = st.columns(4)
        cards[0].metric("Mapped POIs", fmt_number(quality["rows"]))
        cards[1].metric("Current ADM1 regions", len(regions))
        cards[2].metric("Population denominator", fmt_number(manifest["population_total"]))
        cards[3].metric("Broad categories", categories)
        st.plotly_chart(category_bar(pd.DataFrame(quality["category_counts"].items(), columns=["category", "poi_count"])), use_container_width=True)
        st.subheader("Standalone city-regions")
        st.dataframe(cities[["region_name", "population", "poi_count", "per_100k"]], hide_index=True, use_container_width=True, column_config={"population": st.column_config.NumberColumn(format="%,d"), "poi_count": st.column_config.NumberColumn(format="%,d"), "per_100k": st.column_config.NumberColumn("POIs / 100K", format="%.1f")})
        st.info("Counts describe mapped OSM features, not a real-world inventory. Only Astana, Almaty city, and Shymkent are city-region comparisons.")

    with tabs[1]:
        metric = st.radio("Metric", ["poi_count", "per_100k", "per_100km2"], format_func={"poi_count": "Total mapped POIs", "per_100k": "Per 100K residents", "per_100km2": "Per 100 km²"}.get, horizontal=True)
        chart_col, map_col = st.columns(2)
        with chart_col:
            st.plotly_chart(regional_ranking(regions, metric), use_container_width=True)
        with map_col:
            try:
                st.plotly_chart(regional_choropleth(regions, load_geojson(output_paths(root)), metric), use_container_width=True)
            except OutputDataError as error:
                st.warning(str(error))

    with tabs[2]:
        shares = city_category_shares(region_categories, cities)
        st.plotly_chart(city_mix(shares), use_container_width=True)
        city_table = cities[["region_name", "poi_count", "population", "per_100k", "per_100km2"]].copy()
        st.dataframe(city_table, hide_index=True, use_container_width=True)
        st.caption("Different denominators answer different questions: population normalizes access proxies; land area emphasizes mapped concentration.")

    with tabs[3]:
        try:
            pois = parquet_data(root, "poi_enriched.parquet")
            labels = dict(zip(regions["region_code"], regions["region_name"]))
            region = st.selectbox("Region", ["All regions", *regions["region_code"].tolist()], format_func=lambda code: labels.get(code, code))
            chosen_categories = st.multiselect("Categories", sorted(pois["category"].dropna().unique()))
            limit = st.slider("Maximum displayed points", 100, 2500, 1500, 100)
            filtered = filter_pois(pois, region, chosen_categories)
            sample, was_sampled = map_sample(filtered, limit)
            st.write(f"{fmt_number(len(filtered))} matching POIs")
            if was_sampled:
                st.warning(f"Map shows a reproducible sample of {fmt_number(len(sample))} points to keep the dashboard responsive.")
            if sample.empty:
                st.info("No POIs match these filters.")
            else:
                st.plotly_chart(poi_map(sample), use_container_width=True)
        except OutputDataError as error:
            st.warning(str(error))

    with tabs[4]:
        try:
            report = json_data(root, "clustering_report.json")
            clusters = parquet_data(root, "clusters.parquet")
            code = st.selectbox("City-region", list(CITY_CODES), format_func=lambda value: labels.get(value, value), key="cluster_city")
            details = report[code]
            st.write(f"DBSCAN: ε = 0.5 km · min samples = 8 · {details['clusters']} clusters · {details['noise_fraction']:.1%} noise")
            if details["sampled"]:
                st.warning("Almaty city clustering uses a capped 12,000-point sample; treat it as exploratory.")
            st.plotly_chart(cluster_map(clusters[clusters["cluster_city"] == code], labels.get(code, code)), use_container_width=True)
        except OutputDataError as error:
            st.warning(str(error))

    with tabs[5]:
        quality = json_data(root, "quality_report.json")
        hypotheses = json_data(root, "hypotheses.json")
        benchmark = csv_data(root, "benchmark.csv")
        st.subheader("Data quality")
        st.json({key: quality[key] for key in ("rows", "missing_region_count", "missing_name_count", "invalid_coordinates", "duplicate_osm_keys")})
        st.subheader("Exploratory hypotheses")
        st.dataframe(pd.DataFrame(hypotheses), hide_index=True, use_container_width=True)
        st.caption("Spatial observations are not independent, so p-values are exploratory rather than causal claims.")
        st.subheader("Same-task benchmark")
        st.dataframe(benchmark, hide_index=True, use_container_width=True)
        queries = available_sql_queries(output_paths(root))
        if queries:
            selected = st.selectbox("Saved SQLite query", queries, format_func=lambda path: path.name)
            st.code(selected.read_text(encoding="utf-8"), language="sql")
            try:
                st.dataframe(read_sql_query(output_paths(root), selected.name), hide_index=True, use_container_width=True)
            except OutputDataError as error:
                st.warning(str(error))

    with tabs[6]:
        try:
            profiles = parquet_data(root, "urban_grid_profiles.parquet")
            metrics = csv_data(root, "gpu_model_metrics.csv")
            st.dataframe(metrics, hide_index=True, use_container_width=True)
            st.plotly_chart(profile_embedding(profiles), use_container_width=True)
            st.info("These are precomputed unsupervised POI-category reconstruction profiles. They are neither geographic DBSCAN labels nor supervised predictions.")
        except OutputDataError as error:
            st.warning(str(error))


if __name__ == "__main__":
    main()
