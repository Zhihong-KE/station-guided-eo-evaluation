#!/usr/bin/env python3
"""Validate and standardize a station-year-record table."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


DEFAULT_SCHEMA = Path("schemas/record_predictions_schema.json")


def load_schema(path: Path = DEFAULT_SCHEMA) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_public_schema(frame: pd.DataFrame, schema: dict[str, object]) -> None:
    required = list(schema["required_columns"])
    missing = [col for col in required if col not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    forbidden = {str(col).lower() for col in schema["forbidden_public_columns"]}
    leaked = [col for col in frame.columns if col.lower() in forbidden]
    if leaked:
        raise ValueError(f"Forbidden public columns are present: {leaked}")

    key_cols = ["record_id", "station_id", "station_year_id"]
    for col in key_cols:
        if frame[col].isna().any():
            raise ValueError(f"Null values are not allowed in {col}")
        if frame[col].duplicated().any() and col == "record_id":
            raise ValueError("record_id must be unique")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    args = parser.parse_args()

    records = pd.read_csv(args.records)
    schema = load_schema(args.schema)
    validate_public_schema(records, schema)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    records.sort_values(["station_id", "year", "station_year_id", "record_id"]).to_csv(
        args.out, index=False
    )
    print(f"validated and wrote {len(records)} rows to {args.out}")


if __name__ == "__main__":
    main()
