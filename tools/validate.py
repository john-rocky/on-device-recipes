"""Validate recipes.json against schemas/recipe.schema.json and check the docs it points at.

Exit 1 with a readable report on any problem. Run from anywhere:

    python tools/validate.py            # this repo
    python tools/validate.py --root X   # another checkout

Checks: every entry is valid against the schema; ids are unique; question_page files
exist; every published question page starts with a question H1 and carries a
"Last verified" line near the top.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover
    print("validate: pip install jsonschema", file=sys.stderr)
    raise SystemExit(2)

SKIP_PAGES = {"index.md", "provenance.md"}


def load(root: Path):
    index = json.loads((root / "recipes.json").read_text(encoding="utf-8"))
    schema = json.loads((root / index["schema"]).read_text(encoding="utf-8"))
    return index, schema


def check_recipes(root: Path, index: dict, schema: dict) -> list[str]:
    problems: list[str] = []
    validator = Draft202012Validator(schema)
    seen: set[str] = set()
    for i, recipe in enumerate(index.get("recipes", [])):
        rid = recipe.get("id", f"<entry {i}>")
        for err in sorted(validator.iter_errors(recipe), key=lambda e: list(e.path)):
            where = "/".join(str(p) for p in err.path) or "(root)"
            problems.append(f"{rid}: {where}: {err.message}")
        if rid in seen:
            problems.append(f"{rid}: duplicate id")
        seen.add(rid)
        page = recipe.get("question_page")
        if page and not (root / page).is_file():
            problems.append(f"{rid}: question_page {page} does not exist")
    return problems


def front_matter(text: str) -> dict:
    """Minimal front matter reader: only `key: value` lines between the first two --- lines."""
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    out = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def check_pages(root: Path) -> list[str]:
    problems: list[str] = []
    for page in sorted((root / "docs").glob("*.md")):
        if page.name in SKIP_PAGES:
            continue
        text = page.read_text(encoding="utf-8")
        fm = front_matter(text)
        published = fm.get("published", "true").lower() != "false"
        body = text[text.find("\n---", 4) + 4 :] if fm else text
        h1 = next((line for line in body.splitlines() if line.startswith("# ")), "")
        if not h1.rstrip().endswith("?"):
            problems.append(f"docs/{page.name}: H1 must be the question (end with '?'), got: {h1!r}")
        head = "\n".join(body.splitlines()[:12])
        if published and "Last verified" not in head:
            problems.append(f"docs/{page.name}: published page has no 'Last verified' line in its first lines")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    index, schema = load(root)
    Draft202012Validator.check_schema(schema)
    problems = check_recipes(root, index, schema) + check_pages(root)
    if problems:
        print("validate: FAILED")
        for p in problems:
            print(f"  - {p}")
        return 1
    n = len(index.get("recipes", []))
    print(f"validate: OK ({n} recipes, schema and docs consistent)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
