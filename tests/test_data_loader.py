import json
from pathlib import Path

import pytest

from src.data_loader import OutputDataError, output_paths, require_outputs


def test_reports_missing_output_files(tmp_path: Path) -> None:
    with pytest.raises(OutputDataError, match="Missing"):
        require_outputs(output_paths(tmp_path))


def test_accepts_minimum_required_outputs(tmp_path: Path) -> None:
    for name, value in {
        "region_stats.csv": "region_code\nastana\n",
        "region_category.csv": "region_code,category\nastana,Retail\n",
        "city_stats.csv": "region_code\nastana\n",
    }.items():
        (tmp_path / name).write_text(value, encoding="utf-8")
    (tmp_path / "manifest.json").write_text(json.dumps({"population_total": 1}), encoding="utf-8")
    require_outputs(output_paths(tmp_path))
