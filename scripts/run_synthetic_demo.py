#!/usr/bin/env python3
"""Run the complete synthetic demonstration pipeline."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run(args: list[str]) -> None:
    subprocess.run([PYTHON, *args], cwd=ROOT, check=True)


def main() -> None:
    toy = Path("examples/synthetic_toy_dataset")
    splits = toy / "splits"
    aggregate = Path("aggregate_manifests")
    run(["scripts/generate_synthetic_dataset.py", "--out-dir", str(toy)])
    run(["scripts/preprocess_samples.py", "--records", str(toy / "record_predictions.csv"), "--out", str(toy / "record_predictions_validated.csv")])
    run(["scripts/build_protocol_splits.py", "--records", str(toy / "record_predictions_validated.csv"), "--out-dir", str(splits)])
    sy_predictions = aggregate / "synthetic_station_year_predictions.csv"
    metrics = aggregate / "synthetic_metrics.csv"
    diagnostics = aggregate / "synthetic_diagnostics.csv"
    aggregate.mkdir(parents=True, exist_ok=True)
    partial_prediction_paths = []
    for split_path in sorted(splits.glob("protocol_*.csv")):
        if split_path.name == "split_manifest.csv":
            continue
        protocol_name = split_path.stem.replace("protocol_", "")
        partial_path = aggregate / f"synthetic_station_year_predictions_{protocol_name}.csv"
        run([
            "scripts/aggregate_station_year_predictions.py",
            "--records",
            str(toy / "record_predictions_validated.csv"),
            "--splits",
            str(split_path),
            "--out",
            str(partial_path),
        ])
        partial_prediction_paths.append(partial_path)
    pd.concat((pd.read_csv(path) for path in partial_prediction_paths), ignore_index=True).to_csv(
        sy_predictions, index=False
    )
    run(["scripts/compute_metrics.py", "--station-year-predictions", str(sy_predictions), "--out", str(metrics)])
    run([
        "scripts/build_diagnostics.py",
        "--records",
        str(toy / "record_predictions_validated.csv"),
        "--splits",
        str(split_path),
        "--station-year-predictions",
        str(sy_predictions),
        "--out",
        str(diagnostics),
    ])
    run(["scripts/build_aggregate_manifest.py", "--metrics", str(metrics), "--diagnostics", str(diagnostics), "--out", str(aggregate / "synthetic_manifest.json")])
    run(["scripts/build_figures.py", "--metrics", str(metrics), "--diagnostics", str(diagnostics), "--out-dir", str(aggregate / "figures")])
    run(["scripts/release_safety_audit.py", "."])


if __name__ == "__main__":
    main()
