"""Copy a canonical recipe.json into recipes.json as one entry (hub keys kept, everything else verbatim).

    python tools/vendor.py ormbg-android-gpu https://raw.githubusercontent.com/john-rocky/LiteRT-Models/main/ormbg/recipe.json --status verified
    python tools/vendor.py android-llm-chat android-llm-chat/recipe.json --status in_progress

The entry with that id keeps its hub-added keys (id, title, platform, status, question_page,
source); every other key is replaced by the canonical file's content, so tools/check_drift.py
passes by construction. --status and --source update those hub keys; when the canonical
argument is a URL and --source is not given, the URL becomes `source`. A new id appends an
entry and then needs --platform, --title and --question-page.
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

HUB_KEYS = ("id", "title", "platform", "status", "question_page", "source")


def load_canonical(ref: str) -> dict:
    if ref.startswith("http://") or ref.startswith("https://"):
        with urllib.request.urlopen(ref, timeout=30) as resp:  # noqa: S310
            return json.loads(resp.read().decode("utf-8"))
    return json.loads(Path(ref).read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("id")
    parser.add_argument("canonical", help="path or raw URL of the recipe.json to vendor")
    parser.add_argument("--status", choices=["verified", "in_progress", "planned"])
    parser.add_argument("--source", help="raw URL recorded as `source` (default: the canonical argument when it is a URL)")
    parser.add_argument("--platform")
    parser.add_argument("--title")
    parser.add_argument("--question-page")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)

    hub_path = args.root / "recipes.json"
    hub = json.loads(hub_path.read_text(encoding="utf-8"))
    canonical = load_canonical(args.canonical)
    entries = hub["recipes"]
    old = next((r for r in entries if r.get("id") == args.id), None)

    new: dict = {k: old[k] for k in HUB_KEYS if old and k in old} if old else {"id": args.id}
    if args.title:
        new["title"] = args.title
    if args.platform:
        new["platform"] = args.platform
    if args.status:
        new["status"] = args.status
    if args.question_page:
        new["question_page"] = args.question_page
    if args.source:
        new["source"] = args.source
    elif args.canonical.startswith("http") and "source" not in new:
        new["source"] = args.canonical
    # Hub keys first, then the canonical file verbatim (it never carries hub keys).
    ordered = {k: new[k] for k in HUB_KEYS if k in new}
    ordered.update(canonical)

    if old:
        hub["recipes"] = [ordered if r.get("id") == args.id else r for r in entries]
    else:
        missing = [k for k in ("title", "platform", "status", "question_page") if k not in ordered]
        if missing:
            parser.error(f"new id {args.id}: missing {', '.join(missing)}")
        entries.append(ordered)
    hub_path.write_text(json.dumps(hub, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"vendored {args.id} from {args.canonical} (status={ordered.get('status')}, source={ordered.get('source', '-')})")
    print("next: python tools/validate.py && python tools/check_drift.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
