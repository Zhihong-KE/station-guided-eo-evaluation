from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from aggregate_station_year_predictions import aggregate
from build_protocol_splits import build_station_isolated, build_station_year
from compute_metrics import compute_metrics
from generate_synthetic_dataset import make_synthetic_dataset
from release_safety_audit import audit


def test_station_isolated_split_has_no_station_overlap() -> None:
    _, records = make_synthetic_dataset(seed=7)
    split = build_station_isolated(records, seed=42, train=0.7, validation=0.15)
    train_stations = set(split.loc[split["split"] == "train", "station_id"])
    test_stations = set(split.loc[split["split"] == "test", "station_id"])
    validation_stations = set(split.loc[split["split"] == "validation", "station_id"])
    assert train_stations.isdisjoint(test_stations)
    assert train_stations.isdisjoint(validation_stations)
    assert validation_stations.isdisjoint(test_stations)


def test_station_year_split_keeps_records_together() -> None:
    _, records = make_synthetic_dataset(seed=11)
    split = build_station_year(records, seed=42, train=0.7, validation=0.15)
    counts = split.groupby("station_year_id")["split"].nunique()
    assert counts.max() == 1


def test_aggregation_and_metrics_run() -> None:
    _, records = make_synthetic_dataset(seed=12)
    split = build_station_isolated(records, seed=42, train=0.7, validation=0.15)
    station_year_predictions = aggregate(records, split)
    metrics = compute_metrics(station_year_predictions)
    assert not station_year_predictions.empty
    assert set(metrics["metric_unit"]) == {"station_year"}
    assert metrics["crop_macro_f1"].between(0, 1).all()


def test_release_audit_catches_forbidden_coordinate_columns(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    pd.DataFrame({"station_id": ["SYN_ST001"], "latitude": [30.0]}).to_csv(path, index=False)
    issues = audit(tmp_path)
    assert any("forbidden public columns" in issue for issue in issues)
