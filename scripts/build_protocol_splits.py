#!/usr/bin/env python3
"""Build protocol split masks for station-guided EO evaluation."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


SPLIT_COLUMNS = ["record_id", "station_id", "station_year_id", "year", "split", "protocol"]


def assign_groups(groups: pd.Series, seed: int, train: float, validation: float) -> pd.Series:
    rng = np.random.default_rng(seed)
    unique = np.array(sorted(groups.dropna().unique()))
    shuffled = unique.copy()
    rng.shuffle(shuffled)
    n = len(shuffled)
    n_train = max(1, int(round(n * train)))
    n_val = max(1, int(round(n * validation)))
    train_groups = set(shuffled[:n_train])
    val_groups = set(shuffled[n_train : n_train + n_val])

    def label(value: object) -> str:
        if value in train_groups:
            return "train"
        if value in val_groups:
            return "validation"
        return "test"

    return groups.map(label)


def build_random_record(records: pd.DataFrame, seed: int, train: float, validation: float) -> pd.DataFrame:
    out = records[["record_id", "station_id", "station_year_id", "year"]].copy()
    out["split"] = assign_groups(out["record_id"], seed, train, validation)
    out["protocol"] = f"random_record_seed{seed}"
    return out[SPLIT_COLUMNS]


def build_station_year(records: pd.DataFrame, seed: int, train: float, validation: float) -> pd.DataFrame:
    out = records[["record_id", "station_id", "station_year_id", "year"]].copy()
    out["split"] = assign_groups(out["station_year_id"], seed, train, validation)
    out["protocol"] = f"station_year_seed{seed}"
    return out[SPLIT_COLUMNS]


def build_station_isolated(records: pd.DataFrame, seed: int, train: float, validation: float) -> pd.DataFrame:
    out = records[["record_id", "station_id", "station_year_id", "year"]].copy()
    out["split"] = assign_groups(out["station_id"], seed, train, validation)
    out["protocol"] = f"station_isolated_seed{seed}"
    return out[SPLIT_COLUMNS]


def build_temporal_holdout(
    records: pd.DataFrame, test_year: int | None = None, validation_year: int | None = None
) -> pd.DataFrame:
    out = records[["record_id", "station_id", "station_year_id", "year"]].copy()
    years = sorted(int(year) for year in out["year"].dropna().unique())
    if test_year is None:
        test_year = years[-1]
    if validation_year is None:
        earlier = [year for year in years if year < test_year]
        validation_year = earlier[-1] if earlier else test_year
    out["split"] = np.where(
        out["year"].eq(test_year),
        "test",
        np.where(out["year"].eq(validation_year), "validation", "train"),
    )
    out["protocol"] = f"temporal_holdout_{test_year}"
    return out[SPLIT_COLUMNS]


def write_split(frame: pd.DataFrame, out_dir: Path, name: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"protocol_{name}.csv"
    frame.to_csv(path, index=False)
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train-fraction", type=float, default=0.7)
    parser.add_argument("--validation-fraction", type=float, default=0.15)
    parser.add_argument("--temporal-test-year", type=int, default=None)
    parser.add_argument("--temporal-validation-year", type=int, default=None)
    args = parser.parse_args()

    records = pd.read_csv(args.records)
    outputs = {
        f"random_record_seed{args.seed}": build_random_record(
            records, args.seed, args.train_fraction, args.validation_fraction
        ),
        f"station_year_seed{args.seed}": build_station_year(
            records, args.seed, args.train_fraction, args.validation_fraction
        ),
        f"station_isolated_seed{args.seed}": build_station_isolated(
            records, args.seed, args.train_fraction, args.validation_fraction
        ),
    }
    temporal = build_temporal_holdout(
        records, args.temporal_test_year, args.temporal_validation_year
    )
    outputs[str(temporal["protocol"].iloc[0])] = temporal

    manifest_rows = []
    for name, split in outputs.items():
        path = write_split(split, args.out_dir, name)
        manifest_rows.append(
            {
                "protocol": name,
                "path": str(path),
                "n_records": len(split),
                "n_station_years": split["station_year_id"].nunique(),
                "n_stations": split["station_id"].nunique(),
            }
        )
    pd.DataFrame(manifest_rows).to_csv(args.out_dir / "split_manifest.csv", index=False)
    print(f"wrote {len(outputs)} protocol masks to {args.out_dir}")


if __name__ == "__main__":
    main()
