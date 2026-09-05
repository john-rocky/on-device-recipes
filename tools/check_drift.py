"""Fail (exit 1) when a vendored recipe in recipes.json drifts from its canonical recipe.json.

Each entry may carry `source`: the raw URL of the recipe.json that lives next to the
recipe's INTEGRATION guide in the repository that ships the code. That file is the
source of truth. This script fetches it and compares every key it defines with the
hub entry; keys the hub adds on top (id, title, platform, status, question_page,
source) are ignored. Entries without `source` are reported as skipped, not failed,
so a recipe can be listed before its canonical file exists.

    python tools/check_drift.py             # fetch and compare
    python tools/check_drift.py --offline   # only report which entries would be checked
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

HUB_KEYS = {"id", "title", "platform", "status", "question_page", "source"}


def fetch_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310 (raw GitHub URL from recipes.json)
        return json.loads(resp.read().decode("utf-8"))


def diff(canonical: dict, entry: dict, prefix: str = "") -> list[str]:
    out: list[str] = []
    for key, want in canonical.items():
        path = f"{prefix}{key}"
        if key not in entry:
            out.append(f"missing in hub: {path}")
        elif isinstance(want, dict) and isinstance(entry[key], dict):
            out.extend(diff(want, entry[key], path + "."))
        elif entry[key] != want:
            out.append(f"differs: {path}: hub={entry[key]!r} canonical={want!r}")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--offline", action="store_true", help="do not fetch; list what would be checked")
    args = parser.parse_args(argv)
    index = json.loads((args.root / "recipes.json").read_text(encoding="utf-8"))

    failed = 0
    checked = 0
    for entry in index.get("recipes", []):
        rid = entry.get("id", "?")
        source = entry.get("source")
        if not source:
            print(f"drift: {rid}: skipped (no canonical recipe.json yet)")
            continue
        if args.offline:
            print(f"drift: {rid}: would fetch {source}")
            continue
        try:
            canonical = fetch_json(source)
        except (urllib.error.URLError, ValueError) as err:
            print(f"drift: {rid}: FAILED to fetch {source}: {err}")
            failed += 1
            continue
        hub_view = {k: v for k, v in entry.items() if k not in HUB_KEYS}
        problems = diff(canonical, hub_view)
        checked += 1
        if problems:
            failed += 1
            print(f"drift: {rid}: FAILED against {source}")
            for p in problems:
                print(f"  - {p}")
        else:
            print(f"drift: {rid}: OK")
    if failed:
        print("fix: re-vendor the entry from its canonical recipe.json and commit the result")
        return 1
    print(f"drift check: OK ({checked} checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
