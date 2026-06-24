#!/usr/bin/env python3
"""Generate a small synthetic station-year-record dataset.

The output is invented and contains no real station identifiers, coordinates,
labels, or split assignments.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


CROPS = np.array(["wheat", "maize", "rice"])


def make_synthetic_dataset(seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    station_rows: list[dict[str, object]] = []
    record_rows: list[dict[str, object]] = []
    record_idx = 1

    for station_idx in range(1, 13):
        station_id = f"SYN_ST{station_idx:03d}"
        base_x = float((station_idx % 4) * 12 + rng.normal(0, 1))
        base_y = float((station_idx // 4) * 10 + rng.normal(0, 1))
        preferred_crop = CROPS[station_idx % len(CROPS)]

        for year in [2019, 2020, 2021]:
            station_year_id = f"{station_id}_{year}"
            crop_label = str(rng.choice(CROPS, p=[0.5, 0.3, 0.2]))
            if rng.random() < 0.55:
                crop_label = str(preferred_crop)
            sowing_doy = int(rng.normal({"wheat": 102, "maize": 125, "rice": 148}[crop_label], 5))
            maturity_doy = int(sowing_doy + rng.normal({"wheat": 128, "maize": 118, "rice": 110}[crop_label], 6))
            station_rows.append(
                {
                    "station_id": station_id,
                    "station_year_id": station_year_id,
                    "year": year,
                    "crop_label": crop_label,
                    "sowing_doy": sowing_doy,
                    "maturity_doy": maturity_doy,
                    "synthetic_x": round(base_x, 3),
                    "synthetic_y": round(base_y, 3),
                }
            )

            n_records = int(rng.integers(4, 16))
            for _ in range(n_records):
                is_correct = rng.random() < 0.78
                crop_pred = crop_label if is_correct else str(rng.choice(CROPS[CROPS != crop_label]))
                record_rows.append(
                    {
                        "record_id": f"SYN_REC{record_idx:05d}",
                        "station_id": station_id,
                        "station_year_id": station_year_id,
                        "year": year,
                        "crop_label": crop_label,
                        "sowing_doy": sowing_doy,
                        "maturity_doy": maturity_doy,
                        "crop_pred": crop_pred,
                        "sowing_pred": round(float(sowing_doy + rng.normal(0, 7)), 2),
                        "maturity_pred": round(float(maturity_doy + rng.normal(0, 8)), 2),
                        "synthetic_x": round(float(base_x + rng.normal(0, 1.2)), 3),
                        "synthetic_y": round(float(base_y + rng.normal(0, 1.2)), 3),
                    }
                )
                record_idx += 1

    return pd.DataFrame(station_rows), pd.DataFrame(record_rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("examples/synthetic_toy_dataset"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    station_years, records = make_synthetic_dataset(seed=args.seed)
    station_years.to_csv(args.out_dir / "station_year_labels.csv", index=False)
    records.to_csv(args.out_dir / "record_predictions.csv", index=False)
    print(f"wrote {len(station_years)} station-year rows and {len(records)} record rows")


if __name__ == "__main__":
    main()
