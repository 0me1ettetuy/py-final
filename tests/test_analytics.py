import pandas as pd
import pytest

from src.analytics import category_counts, filter_pois, map_sample


@pytest.fixture
def pois() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "region_code": ["astana", "astana", "abay"],
            "category": ["Retail", "Healthcare", "Retail"],
            "osm_key": ["node:1", "node:2", "node:3"],
        }
    )


def test_filters_by_region_and_category(pois: pd.DataFrame) -> None:
    result = filter_pois(pois, "astana", ["Healthcare"])
    assert result["osm_key"].tolist() == ["node:2"]


def test_category_counts_and_map_sampling(pois: pd.DataFrame) -> None:
    counts = category_counts(pois)
    sample, sampled = map_sample(pois, 2)
    assert counts.iloc[0].to_dict() == {"category": "Retail", "poi_count": 2}
    assert sampled is True
    assert len(sample) == 2


def test_rejects_invalid_sample_limit(pois: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="at least 1"):
        map_sample(pois, 0)
