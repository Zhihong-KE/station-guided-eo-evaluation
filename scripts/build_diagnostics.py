#!/usr/bin/env python3
"""Build aggregate support-density and synthetic-distance diagnostics."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from compute_metrics import macro_f1


def nearest_train_distance(test: pd.DataFrame, train: pd.DataFrame) -> pd.Series:
    train_xy = train[["synthetic_x", "synthetic_y"]].drop_duplicates().to_numpy(dtype=float)
    if len(train_xy) == 0:
        return pd.Series(np.nan, index=test.index)
    test_xy = test[["synthetic_x", "synthetic_y"]].to_numpy(dtype=float)
    distances = []
    for row in test_xy:
        diff = train_xy - row
        distances.append(float(np.sqrt((diff * diff).sum(axis=1)).min()))
    return pd.Series(distances, index=test.index)


def summarize_group(protocol: str, split: str, diagnostic: str, bin_label: str, group: pd.DataFrame) -> dict[str, object]:
    sowing_mae = (group["sowing_pred"] - group["sowing_doy"]).abs().mean()
    maturity_mae = (group["maturity_pred"] - group["maturity_doy"]).abs().mean()
    return {
        "protocol": protocol,
        "split": split,
        "diagnostic": diagnostic,
        "bin": bin_label,
        "n_station_years": int(group["station_year_id"].nunique()),
        "crop_macro_f1": round(macro_f1(group["crop_label"], group["crop_pred"]), 6),
        "phenology_mae": round(float((sowing_mae + maturity_mae) / 2), 6),
    }


def build_diagnostics(station_years: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (protocol, split), split_group in station_years.groupby(["protocol", "split"]):
        density_bins = pd.cut(
            split_group["n_records"],
            bins=[0, 5, 10, 20, 1_000_000],
            labels=["1-5", "6-10", "11-20", "20+"],
            include_lowest=True,
        )
        for bin_label, group in split_group.groupby(density_bins, observed=True):
            rows.append(summarize_group(protocol, split, "support_density", str(bin_label), group))

    for protocol, protocol_group in station_years.groupby("protocol"):
        train = protocol_group[protocol_group["split"] == "train"]
        test = protocol_group[protocol_group["split"] == "test"].copy()
        if test.empty:
            continue
        test["nearest_train_distance"] = nearest_train_distance(test, train)
        distance_bins = pd.cut(
            test["nearest_train_distance"],
            bins=[0, 10, 25, 50, 1_000_000],
            labels=["0-10", "10-25", "25-50", "50+"],
            include_lowest=True,
        )
        for bin_label, group in test.groupby(distance_bins, observed=True):
            rows.append(summarize_group(protocol, "test", "synthetic_distance", str(bin_label), group))

    return pd.DataFrame(rows).sort_values(["protocol", "split", "diagnostic", "bin"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--splits", type=Path, required=True)
    parser.add_argument("--station-year-predictions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    station_years = pd.read_csv(args.station_year_predictions)
    diagnostics = build_diagnostics(station_years)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    diagnostics.to_csv(args.out, index=False)
    print(f"wrote {len(diagnostics)} diagnostic rows to {args.out}")


if __name__ == "__main__":
    main()
