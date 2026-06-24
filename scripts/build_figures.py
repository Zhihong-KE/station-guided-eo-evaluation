#!/usr/bin/env python3
"""Build release-safe Nature-style figures from aggregate manifests."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROTOCOL_LABELS = {
    "random_record_seed42": "Random record",
    "station_year_seed42": "Station-year",
    "station_isolated_seed42": "Station isolated",
    "temporal_holdout_2021": "Temporal holdout",
}

PALETTE = {
    "Random record": "#0072B2",
    "Station-year": "#009E73",
    "Station isolated": "#D55E00",
    "Temporal holdout": "#CC79A7",
}


def set_nature_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 8,
            "axes.labelsize": 8,
            "axes.titlesize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.8,
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
            "legend.frameon": False,
        }
    )


def protocol_label(value: str) -> str:
    return PROTOCOL_LABELS.get(value, value.replace("_", " ").title())


def plot_protocol_audit(metrics: pd.DataFrame, diagnostics: pd.DataFrame, out_dir: Path) -> None:
    set_nature_style()
    test_metrics = metrics[metrics["split"] == "test"].copy()
    if test_metrics.empty:
        return
    test_metrics["protocol_label"] = test_metrics["protocol"].map(protocol_label)
    order = [
        "Random record",
        "Station-year",
        "Station isolated",
        "Temporal holdout",
    ]
    test_metrics["protocol_label"] = pd.Categorical(
        test_metrics["protocol_label"], categories=order, ordered=True
    )
    test_metrics = test_metrics.sort_values("protocol_label")
    colors = [PALETTE[str(label)] for label in test_metrics["protocol_label"]]

    fig = plt.figure(figsize=(7.1, 3.8), constrained_layout=True)
    grid = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 1.35])
    ax_f1 = fig.add_subplot(grid[0, 0])
    ax_mae = fig.add_subplot(grid[0, 1])
    ax_diag = fig.add_subplot(grid[0, 2])

    y = range(len(test_metrics))
    ax_f1.hlines(y, 0, test_metrics["crop_macro_f1"], color="#D9D9D9", linewidth=1.2)
    ax_f1.scatter(test_metrics["crop_macro_f1"], y, s=36, color=colors, edgecolor="black", linewidth=0.35)
    ax_f1.set_yticks(list(y))
    ax_f1.set_yticklabels(test_metrics["protocol_label"])
    f1_min = float(test_metrics["crop_macro_f1"].min())
    ax_f1.set_xlim(max(0.0, f1_min - 0.08), 1.02)
    ax_f1.set_xlabel("Crop Macro-F1")
    ax_f1.set_title("Crop classification")
    ax_f1.grid(axis="x", color="#E6E6E6", linewidth=0.6)

    ax_mae.hlines(y, 0, test_metrics["phenology_mae"], color="#D9D9D9", linewidth=1.2)
    ax_mae.scatter(test_metrics["phenology_mae"], y, s=36, color=colors, edgecolor="black", linewidth=0.35)
    ax_mae.set_yticks(list(y))
    ax_mae.set_yticklabels([])
    ax_mae.set_xlabel("Phenology MAE (days)")
    ax_mae.set_title("Phenology date error")
    ax_mae.grid(axis="x", color="#E6E6E6", linewidth=0.6)

    support = diagnostics[
        (diagnostics["split"] == "test") & (diagnostics["diagnostic"] == "support_density")
    ].copy()
    if not support.empty:
        support["protocol_label"] = support["protocol"].map(protocol_label)
        support["bin"] = pd.Categorical(
            support["bin"], categories=["1-5", "6-10", "11-20", "20+"], ordered=True
        )
        for label, group in support.sort_values("bin").groupby("protocol_label", observed=True):
            ax_diag.plot(
                group["bin"].astype(str),
                group["phenology_mae"],
                marker="o",
                linewidth=1.4,
                markersize=4,
                color=PALETTE.get(label, "#4D4D4D"),
                label=label,
            )
        ax_diag.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), borderaxespad=0.0)
    ax_diag.set_xlabel("Records per station-year")
    ax_diag.set_ylabel("Phenology MAE (days)")
    ax_diag.set_title("Support-density diagnostic")
    ax_diag.grid(axis="y", color="#E6E6E6", linewidth=0.6)

    for label, ax in zip(["a", "b", "c"], [ax_f1, ax_mae, ax_diag], strict=True):
        ax.text(
            -0.18,
            1.08,
            label,
            transform=ax.transAxes,
            fontsize=10,
            fontweight="bold",
            va="top",
            ha="left",
        )

    for suffix in ["png", "pdf", "svg"]:
        fig.savefig(out_dir / f"synthetic_protocol_audit_figure.{suffix}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_metrics(metrics: pd.DataFrame, out_dir: Path) -> None:
    set_nature_style()
    test_metrics = metrics[metrics["split"] == "test"].copy()
    if test_metrics.empty:
        return
    test_metrics["protocol_label"] = test_metrics["protocol"].map(protocol_label)
    test_metrics = test_metrics.sort_values("protocol_label")
    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.6), constrained_layout=True)
    axes[0].barh(
        test_metrics["protocol_label"],
        test_metrics["crop_macro_f1"],
        color=[PALETTE.get(label, "#4D4D4D") for label in test_metrics["protocol_label"]],
    )
    axes[0].set_xlabel("Macro-F1")
    axes[0].set_title("Synthetic crop classification")
    axes[0].set_xlim(0, 1.05)

    axes[1].barh(
        test_metrics["protocol_label"],
        test_metrics["phenology_mae"],
        color=[PALETTE.get(label, "#4D4D4D") for label in test_metrics["protocol_label"]],
    )
    axes[1].set_xlabel("MAE (days)")
    axes[1].set_yticklabels([])
    axes[1].set_title("Synthetic phenology")
    fig.savefig(out_dir / "synthetic_protocol_metrics.png", dpi=300)
    plt.close(fig)


def plot_diagnostics(diagnostics: pd.DataFrame, out_dir: Path) -> None:
    set_nature_style()
    subset = diagnostics[(diagnostics["split"] == "test") & (diagnostics["diagnostic"] == "support_density")]
    if subset.empty:
        return
    subset = subset.copy()
    subset["protocol_label"] = subset["protocol"].map(protocol_label)
    pivot = subset.pivot_table(
        index="bin", columns="protocol_label", values="phenology_mae", aggfunc="mean", observed=True
    )
    fig, ax = plt.subplots(figsize=(4.8, 3.0), constrained_layout=True)
    for column in pivot.columns:
        ax.plot(pivot.index.astype(str), pivot[column], marker="o", linewidth=1.5, label=column)
    ax.set_ylabel("MAE (days)")
    ax.set_xlabel("Support-density bin")
    ax.set_title("Synthetic support-density diagnostic")
    ax.legend()
    fig.savefig(out_dir / "synthetic_support_density.png", dpi=300)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--diagnostics", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    metrics = pd.read_csv(args.metrics)
    diagnostics = pd.read_csv(args.diagnostics)
    plot_protocol_audit(metrics, diagnostics, args.out_dir)
    plot_metrics(metrics, args.out_dir)
    plot_diagnostics(diagnostics, args.out_dir)
    print(f"wrote figures to {args.out_dir}")


if __name__ == "__main__":
    main()
