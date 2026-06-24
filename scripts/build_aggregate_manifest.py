#!/usr/bin/env python3
"""Create a release-safe aggregate manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--diagnostics", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    metrics = pd.read_csv(args.metrics)
    diagnostics = pd.read_csv(args.diagnostics)
    manifest = {
        "release_scope": "synthetic aggregate demonstration",
        "privacy_boundary": {
            "row_level_real_data": "excluded",
            "real_station_identifiers": "excluded",
            "real_coordinates": "excluded",
            "real_split_assignments": "excluded",
        },
        "tables": {
            "metrics": {
                "path": str(args.metrics),
                "rows": int(len(metrics)),
                "grain": "protocol x split x metric_unit",
            },
            "diagnostics": {
                "path": str(args.diagnostics),
                "rows": int(len(diagnostics)),
                "grain": "protocol x split x diagnostic_bin",
            },
        },
        "protocols": sorted(metrics["protocol"].dropna().unique().tolist()),
        "splits": sorted(metrics["split"].dropna().unique().tolist()),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
        handle.write("\n")
    print(f"wrote aggregate manifest to {args.out}")


if __name__ == "__main__":
    main()
