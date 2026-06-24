#!/usr/bin/env python3
"""Audit the repository for common public-release leakage risks."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


TEXT_SUFFIXES = {".py", ".md", ".json", ".toml", ".csv", ".txt", ".yml", ".yaml", ".gitignore"}
FORBIDDEN_PATH_PARTS = {
    "data/raw",
    "data/restricted",
    "data/private",
    "restricted",
    "private",
    "raw",
}
FORBIDDEN_FIELD_NAMES = {
    "latitude",
    "longitude",
    "lat",
    "lon",
    "station_name",
    "site_name",
    "admin_code",
    "county",
    "province",
}
FORBIDDEN_TEXT_PATTERNS = [
    re.compile("/" + "New" + "Disk" + "/"),
    re.compile("/" + "home" + r"/[^\s]+/"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY-----"),
]


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name == ".gitignore"


def audit_csv_header(path: Path) -> list[str]:
    issues: list[str] = []
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader, [])
    except UnicodeDecodeError:
        return [f"{path}: cannot decode as UTF-8"]
    lower = {col.strip().lower() for col in header}
    leaked = sorted(lower & FORBIDDEN_FIELD_NAMES)
    if leaked:
        issues.append(f"{path}: forbidden public columns {leaked}")
    if path.name.startswith("protocol_") and "synthetic" not in str(path):
        issues.append(f"{path}: protocol split file is not under a synthetic example path")
    return issues


def audit_text(path: Path) -> list[str]:
    issues: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"{path}: cannot decode as UTF-8"]
    for pattern in FORBIDDEN_TEXT_PATTERNS:
        if pattern.search(text):
            issues.append(f"{path}: matched forbidden text pattern {pattern.pattern}")
    return issues


def audit(root: Path) -> list[str]:
    issues: list[str] = []
    for path in root.rglob("*"):
        if ".git" in path.parts or "invalid_files" in path.parts or path.is_dir():
            continue
        rel = path.relative_to(root).as_posix()
        lower_rel = rel.lower()
        if any(part in lower_rel for part in FORBIDDEN_PATH_PARTS):
            issues.append(f"{rel}: path suggests restricted/raw/private data")
        if path.suffix.lower() == ".csv":
            issues.extend(audit_csv_header(path))
        if is_text_file(path):
            issues.extend(audit_text(path))
    return issues


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()

    issues = audit(args.root)
    if issues:
        print("release safety audit failed:")
        for issue in issues:
            print(f"- {issue}")
        raise SystemExit(1)
    print("release safety audit passed")


if __name__ == "__main__":
    main()
