from __future__ import annotations

import pandas as pd


CITY_CODES = ("astana", "almaty_city", "shymkent")


def filter_pois(
    pois: pd.DataFrame, region_code: str | None = None, categories: list[str] | None = None
) -> pd.DataFrame:
    """Return a copy constrained by region and broad categories."""
    result = pois
    if region_code and region_code != "All regions":
        result = result[result["region_code"] == region_code]
    if categories:
        result = result[result["category"].isin(categories)]
    return result.copy()


def category_counts(pois: pd.DataFrame) -> pd.DataFrame:
    return (
        pois.groupby("category", dropna=False)
        .size()
        .rename("poi_count")
        .reset_index()
        .sort_values("poi_count", ascending=False)
    )


def city_category_shares(region_category: pd.DataFrame, city_stats: pd.DataFrame) -> pd.DataFrame:
    cities = region_category[region_category["region_code"].isin(CITY_CODES)].merge(
        city_stats[["region_code", "region_name", "poi_count", "per_100k"]], on="region_code", how="left"
    )
    totals = cities.groupby("region_code")["poi_count_x"].transform("sum")
    cities["share"] = cities["poi_count_x"] / totals
    return cities.rename(columns={"poi_count_x": "category_poi_count", "poi_count_y": "total_poi_count"})


def metric_label(metric: str) -> str:
    return {
        "poi_count": "Mapped POIs",
        "per_100k": "POIs per 100K residents",
        "per_100km2": "POIs per 100 km²",
    }[metric]


def map_sample(pois: pd.DataFrame, maximum: int, seed: int = 47) -> tuple[pd.DataFrame, bool]:
    if maximum < 1:
        raise ValueError("Map sample limit must be at least 1.")
    sampled = len(pois) > maximum
    return (pois.sample(maximum, random_state=seed) if sampled else pois), sampled
