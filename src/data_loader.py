from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


REQUIRED_FILES = ("region_stats.csv", "region_category.csv", "city_stats.csv", "manifest.json")


class OutputDataError(RuntimeError):
    """Raised when the notebook output directory is incomplete or unreadable."""


@dataclass(frozen=True)
class OutputPaths:
    root: Path

    def file(self, name: str) -> Path:
        return self.root / name


def output_paths(value: str | Path | None = None) -> OutputPaths:
    """Resolve notebook outputs, allowing deployment-specific override."""
    root = Path(value or os.environ.get("POI_OUTPUT_DIR", "outputs")).expanduser()
    return OutputPaths(root)


def missing_required_files(paths: OutputPaths) -> list[str]:
    return [name for name in REQUIRED_FILES if not paths.file(name).is_file()]


def require_outputs(paths: OutputPaths) -> None:
    missing = missing_required_files(paths)
    if missing:
        raise OutputDataError(
            f"Output directory '{paths.root}' is incomplete. Missing: {', '.join(missing)}. "
            "Run the notebook first or set POI_OUTPUT_DIR to its outputs folder."
        )


def load_csv(paths: OutputPaths, name: str) -> pd.DataFrame:
    file_path = paths.file(name)
    if not file_path.is_file():
        raise OutputDataError(f"Required output is missing: {file_path}")
    return pd.read_csv(file_path)


def load_json(paths: OutputPaths, name: str) -> dict | list:
    file_path = paths.file(name)
    if not file_path.is_file():
        raise OutputDataError(f"Required output is missing: {file_path}")
    with file_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_parquet(paths: OutputPaths, name: str) -> pd.DataFrame:
    file_path = paths.file(name)
    if not file_path.is_file():
        raise OutputDataError(f"Required output is missing: {file_path}")
    return pd.read_parquet(file_path)


def load_geojson(paths: OutputPaths) -> dict:
    return load_json(paths, "regions.geojson")  # type: ignore[return-value]


def read_sql_query(paths: OutputPaths, filename: str) -> pd.DataFrame:
    query_path = paths.file("sql_results") / filename
    database = paths.file("kazakhstan_poi.sqlite")
    if not query_path.is_file() or not database.is_file():
        raise OutputDataError("SQLite database or saved query is missing from outputs.")
    with query_path.open(encoding="utf-8") as handle, sqlite3.connect(database) as connection:
        return pd.read_sql_query(handle.read(), connection)


def available_sql_queries(paths: OutputPaths) -> list[Path]:
    query_dir = paths.file("sql_results")
    return sorted(query_dir.glob("*.sql")) if query_dir.is_dir() else []
