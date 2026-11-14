"""Validate the precomputed notebook artifacts before launching the dashboard."""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_loader import OutputDataError, output_paths, require_outputs  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"Validation failed: {message}")


def main() -> None:
    paths = output_paths()
    try:
        require_outputs(paths)
    except OutputDataError as error:
        fail(str(error))

    regions = pd.read_csv(paths.file("region_stats.csv"))
    if len(regions) != 20 or regions["region_code"].nunique() != 20:
        fail("region_stats.csv must contain exactly 20 unique regions")
    if int(regions["population"].sum()) != 20_633_529:
        fail("regional population total must equal 20,633,529")

    pois = pd.read_parquet(paths.file("poi_enriched.parquet"))
    required_columns = {"osm_key", "category", "region_code", "latitude", "longitude"}
    if not required_columns.issubset(pois.columns) or not pois["osm_key"].is_unique:
        fail("POI schema is incomplete or osm_key values are not unique")

    sql_files = list((paths.file("sql_results")).glob("*.sql"))
    if len(sql_files) < 8:
        fail("at least eight saved SQL queries are required")

    benchmark = pd.read_csv(paths.file("benchmark.csv"))
    if not benchmark["matches_baseline"].astype(str).str.lower().eq("true").all():
        fail("all benchmark implementations must match the SQLite baseline")

    with sqlite3.connect(paths.file("kazakhstan_poi.sqlite")) as connection:
        foreign_key_errors = connection.execute("PRAGMA foreign_key_check").fetchall()
    if foreign_key_errors:
        fail("SQLite foreign-key consistency check failed")
    print("Outputs validated: 20 regions, population total, unique POIs, SQL, benchmarks, and SQLite FK checks.")


if __name__ == "__main__":
    main()
