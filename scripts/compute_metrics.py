#!/usr/bin/env python3
"""Compute station-year equal-weighted metrics."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def macro_f1(y_true: pd.Series, y_pred: pd.Series) -> float:
    labels = sorted(set(y_true.dropna()) | set(y_pred.dropna()))
    f1_values: list[float] = []
    for label in labels:
        true_pos = int(((y_true == label) & (y_pred == label)).sum())
        false_pos = int(((y_true != label) & (y_pred == label)).sum())
        false_neg = int(((y_true == label) & (y_pred != label)).sum())
        precision = true_pos / (true_pos + false_pos) if true_pos + false_pos else 0.0
        recall = true_pos / (true_pos + false_neg) if true_pos + false_neg else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        f1_values.append(f1)
    return float(np.mean(f1_values)) if f1_values else float("nan")


def compute_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (protocol, split), group in frame.groupby(["protocol", "split"]):
        sowing_mae = (group["sowing_pred"] - group["sowing_doy"]).abs().mean()
        maturity_mae = (group["maturity_pred"] - group["maturity_doy"]).abs().mean()
        rows.append(
            {
                "protocol": protocol,
                "split": split,
                "metric_unit": "station_year",
                "n_station_years": int(group["station_year_id"].nunique()),
                "crop_macro_f1": round(macro_f1(group["crop_label"], group["crop_pred"]), 6),
                "sowing_mae": round(float(sowing_mae), 6),
                "maturity_mae": round(float(maturity_mae), 6),
                "phenology_mae": round(float((sowing_mae + maturity_mae) / 2), 6),
            }
        )
    return pd.DataFrame(rows).sort_values(["protocol", "split"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--station-year-predictions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    frame = pd.read_csv(args.station_year_predictions)
    metrics = compute_metrics(frame)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(args.out, index=False)
    print(f"wrote {len(metrics)} metric rows to {args.out}")


if __name__ == "__main__":
    main()
