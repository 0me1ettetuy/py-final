from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .analytics import metric_label


def regional_ranking(regions: pd.DataFrame, metric: str) -> go.Figure:
    data = regions.sort_values(metric)
    return px.bar(data, x=metric, y="region_name", orientation="h", color=metric, color_continuous_scale="Blues", labels={metric: metric_label(metric), "region_name": "Region"})


def regional_choropleth(regions: pd.DataFrame, geojson: dict, metric: str) -> go.Figure:
    figure = px.choropleth_map(
        regions,
        geojson=geojson,
        locations="region_code",
        featureidkey="properties.region_code",
        color=metric,
        hover_name="region_name",
        hover_data={"population": ":,", "poi_count": ":,", "per_100k": ".1f", "per_100km2": ".1f"},
        color_continuous_scale="Viridis",
        map_style="open-street-map",
        center={"lat": 48.0, "lon": 67.0},
        zoom=3.3,
        opacity=0.65,
        labels={metric: metric_label(metric)},
    )
    figure.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    return figure


def category_bar(counts: pd.DataFrame, title: str = "POIs by category") -> go.Figure:
    return px.bar(counts, x="category", y="poi_count", color="category", title=title, labels={"category": "Category", "poi_count": "Mapped POIs"})


def poi_map(pois: pd.DataFrame) -> go.Figure:
    figure = px.scatter_map(
        pois,
        lat="latitude",
        lon="longitude",
        color="category",
        hover_name="name",
        hover_data={"subcategory": True, "region_code": True, "latitude": ".4f", "longitude": ".4f"},
        map_style="open-street-map",
        zoom=3.5,
        height=650,
    )
    figure.update_layout(margin=dict(l=0, r=0, t=30, b=0))
    return figure


def city_mix(city_categories: pd.DataFrame) -> go.Figure:
    return px.bar(city_categories, x="category", y="share", color="region_name", barmode="group", labels={"share": "Share of city-region POIs", "region_name": "City-region"})


def cluster_map(clusters: pd.DataFrame, city_name: str) -> go.Figure:
    visible = clusters.assign(cluster_label=clusters["cluster_id"].astype(str).replace("-1", "Noise"))
    return px.scatter_map(visible, lat="latitude", lon="longitude", color="cluster_label", hover_data=["category"], map_style="open-street-map", zoom=9, height=650, title=f"DBSCAN clusters: {city_name}")


def profile_embedding(profiles: pd.DataFrame) -> go.Figure:
    return px.scatter(profiles, x="embedding_00", y="embedding_01", color="profile_cluster", size="total_pois", hover_data=["latitude", "longitude", "embedding_02", "embedding_03"], title="Precomputed neighbourhood-profile embedding")
