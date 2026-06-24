#!/usr/bin/env python3
"""Aggregate record-level predictions to station-year support."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def mode_or_first(values: pd.Series) -> object:
    modes = values.mode(dropna=True)
    if not modes.empty:
        return modes.iloc[0]
    return values.dropna().iloc[0]


def aggregate(records: pd.DataFrame, splits: pd.DataFrame) -> pd.DataFrame:
    merged = records.merge(splits[["record_id", "split", "protocol"]], on="record_id", how="inner")
    group_cols = ["protocol", "split", "station_id", "station_year_id", "year"]
    grouped = merged.groupby(group_cols, as_index=False)
    out = grouped.agg(
        crop_label=("crop_label", mode_or_first),
        sowing_doy=("sowing_doy", "median"),
        maturity_doy=("maturity_doy", "median"),
        crop_pred=("crop_pred", mode_or_first),
        sowing_pred=("sowing_pred", "median"),
        maturity_pred=("maturity_pred", "median"),
        n_records=("record_id", "count"),
        synthetic_x=("synthetic_x", "mean"),
        synthetic_y=("synthetic_y", "mean"),
    )
    out["phenology_abs_error"] = (
        (out["sowing_pred"] - out["sowing_doy"]).abs()
        + (out["maturity_pred"] - out["maturity_doy"]).abs()
    ) / 2
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--splits", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    records = pd.read_csv(args.records)
    splits = pd.read_csv(args.splits)
    out = aggregate(records, splits)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)
    print(f"wrote {len(out)} station-year predictions to {args.out}")


if __name__ == "__main__":
    main()
