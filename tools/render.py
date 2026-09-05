"""Render every generated surface of this hub from recipes.json and the cached litert-community listing.

Inputs
  recipes.json                          the hub index: each recipe.json vendored verbatim (tools/vendor.py)
  data/litert-community-litertlm.json   the Hugging Face listing of litert-community, reduced to the
                                        repositories that carry a .litertlm file (refresh with --fetch)

Outputs
  the text between `<!-- gen:<key>:start -->` and `<!-- gen:<key>:end -->` in README.md, llms.txt,
  AGENTS.md, docs/*.md and skills/**/*.md: the generator owns the inside of a region, people own
  everything outside it
  out/<id>/card-addendum.md          the line and the pull-request body for the model author's card
  out/<id>/page-block.md             the question-page block (answer, conditions, steps, limits,
                                     measurements, provenance), each part in its own marker region
  out/<id>/litert-side-addendum.md   one line for awesome-litert and one for an official sample list

    python tools/render.py             # render everything
    python tools/render.py --check     # render to memory, diff against the tree, exit 1 on drift (CI)
    python tools/render.py --fetch     # refresh the litert-community cache from the API, then render
    python tools/render.py --refresh   # re-vendor every entry from its `source` URL, then render

Keys: recipes-table, ungated-litertlm-list, llms-recipes, and per recipe recipe-answer:<id>,
recipe-conditions:<id>, recipe-steps:<id>, recipe-limits:<id>, recipe-measurements:<id>,
provenance:<id>. An unknown key or id is an error, never a silent skip.

The generator copies facts. It rounds nothing, computes no ratio and adds no adjective; a number
appears in its output only with the device and the date recipe.json gives it. The five provenance
items (converted and verified by, recipe, measurements, commit, maintained at) are in every output.

The Hugging Face listing endpoint returns cardData (license, base_model) only with
`expand[]=cardData`; `full=true` does not include it.
"""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vendor  # noqa: E402

CACHE = Path("data/litert-community-litertlm.json")
HF_LIST_URL = (
    "https://huggingface.co/api/models?author=litert-community&limit=400"
    "&expand[]=cardData&expand[]=gated&expand[]=lastModified&expand[]=siblings"
    "&expand[]=pipeline_tag&expand[]=tags&expand[]=library_name"
)
START_RE = re.compile(r"^(?P<indent>[ \t]*)<!-- gen:(?P<key>[A-Za-z0-9_.:-]+):start -->[ \t]*$")
TEXT_FILES = ("README.md", "llms.txt", "AGENTS.md")
TEXT_GLOBS = ("docs/*.md", "skills/**/*.md")
HUB_RAW = "https://raw.githubusercontent.com/john-rocky/on-device-recipes/main"
PLATFORM_LABEL = {"android": "Android", "ios": "iOS", "macos": "macOS", "linux": "Linux", "windows": "Windows", "web": "web"}
PIPELINE_ORDER = ["text-generation", "image-text-to-text", "automatic-speech-recognition", "translation"]
PIPELINE_LABEL = {
    "text-generation": "Text generation (chat and instruct models)",
    "image-text-to-text": "Image and text to text (vision-language models)",
    "automatic-speech-recognition": "Speech recognition",
    "translation": "Translation",
    None: "No pipeline tag on the card",
}
MEASUREMENT_COLUMNS = [
    ("name", "device"),
    ("os", "OS"),
    ("accelerator", "backend"),
    ("runtime_version", "runtime"),
    ("ms_per_frame", "model ms per frame"),
    ("process_ms_per_frame", "end-to-end ms per frame"),
    ("gpu_nodes", "ops on the accelerator"),
    ("partitions", "partitions"),
    ("load_ms", "load ms"),
    ("load_ms_warm", "reload ms"),
    ("tok_per_s", "decode tokens/s"),
    ("tok_per_s_runs", "decode tokens/s per run"),
    ("decode_tokens_per_run", "decode tokens per run"),
    ("prefill_tok_per_s", "prefill tokens/s"),
    ("ttft_s", "first token s"),
    ("first_turn_s", "first answer s"),
    ("footprint_mb", "footprint MB"),
    ("pss_loaded_kb", "PSS loaded kB"),
    ("pss_released_kb", "PSS after release kB"),
    ("cancel_cpu_ms_per_1500ms", "CPU ms in the 1.5 s after a cancel"),
    ("close_during_generation_ms", "close() during a reply ms"),
    ("thermal_status", "thermal status"),
    ("parity", "parity"),
    ("output", "output"),
    ("date", "date"),
]
CONDITION_ROWS = [
    ("model", "hf_repo", "model repository"),
    ("model", "file", "model file"),
    ("model", "url", "download URL"),
    ("model", "sha256", "sha256"),
    ("model", "bytes", "size, bytes"),
    ("model", "license", "license"),
    ("model", "base_model", "base model"),
    ("model", "source_repo", "converted from"),
    ("model", "source_revision", "source revision"),
    ("model", "source_license_note", "license note"),
    ("model", "params", "parameters"),
    ("model", "variant", "variant"),
    ("model", "published_by", "published by"),
    ("model", "input", "input"),
    ("model", "output", "output"),
    ("runtime", "name", "runtime"),
    ("runtime", "version", "runtime version"),
    ("runtime", "maven", "Maven artifact"),
    ("runtime", "spm", "Swift package"),
    ("runtime", "swift_package_ref", "Swift package tag"),
    ("runtime", "pip", "pip package"),
    ("runtime", "accelerator", "accelerator"),
    ("convert", "tool", "converter"),
    ("convert", "version", "converter version"),
    ("convert", "script", "conversion script"),
    ("convert", "command", "conversion command"),
    ("convert", "patches", "graph patches"),
    ("convert", "reproduced", "conversion reproduced"),
    ("convert", "note", "conversion note"),
    ("integrate", "min_sdk", "minimum Android SDK"),
    ("integrate", "min_os", "minimum OS"),
    ("integrate", "abi", "ABI"),
    ("integrate", "toolchain", "toolchain"),
]


class RenderError(Exception):
    pass


# ---------------------------------------------------------------- formatting helpers


def num(value) -> str:
    """A number as recipe.json wrote it; integers get thousands separators, nothing is rounded."""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        return repr(value)
    return str(value)


def cell(value) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "; ".join(cell(v) for v in value)
    return num(value).replace("|", "\\|").replace("\n", " ")


def hf_url(repo: str) -> str:
    return f"https://huggingface.co/{repo}"


def blob_base(recipe: dict) -> str | None:
    """The GitHub blob root of the repository that ships the recipe, from provenance.recipe_origin."""
    origin = recipe.get("provenance", {}).get("recipe_origin", "")
    m = re.match(r"^(https://github\.com/[^/]+/[^/]+/blob/[^/]+/)", origin)
    return m.group(1) if m else None


def runtime_text(recipe: dict) -> str:
    rt = recipe.get("runtime", {})
    text = f"{rt.get('name', '')} {rt.get('version', '')}".strip()
    coord = rt.get("maven") or rt.get("pip")
    if coord:
        text += f" (`{coord}`)"
    if rt.get("accelerator"):
        text += f", {rt['accelerator']}"
    return text


def pinned_rows(recipe: dict) -> list[dict]:
    """Device rows taken on the runtime version the recipe pins (the version string appears in the row)."""
    version = str(recipe.get("runtime", {}).get("version", "")).split(" ")[0]
    rows = recipe.get("devices", [])
    if not version:
        return rows
    return [r for r in rows if version in str(r.get("runtime_version", version))]


def row_metrics(row: dict) -> str:
    parts = []
    if "ms_per_frame" in row:
        parts.append(f"{num(row['ms_per_frame'])} ms per frame for the model")
    if "process_ms_per_frame" in row:
        parts.append(f"{num(row['process_ms_per_frame'])} ms end to end")
    if "gpu_nodes" in row:
        parts.append(f"{row['gpu_nodes']} ops on the {str(row.get('accelerator', 'accelerator')).upper()}")
    if "tok_per_s" in row:
        parts.append(f"{num(row['tok_per_s'])} tokens/s decode")
    if "prefill_tok_per_s" in row:
        parts.append(f"{num(row['prefill_tok_per_s'])} tokens/s prefill")
    if "ttft_s" in row:
        parts.append(f"{num(row['ttft_s'])} s to the first token")
    if "first_turn_s" in row:
        parts.append(f"{num(row['first_turn_s'])} s to the first answer")
    if "footprint_mb" in row:
        parts.append(f"{num(row['footprint_mb'])} MB footprint")
    acc = row.get("accelerator")
    text = ", ".join(parts)
    return f"{str(acc).upper()}: {text}" if acc and text else text or "(no throughput fields)"


def device_summary(recipe: dict, rows: list[dict] | None = None) -> str:
    """One sentence per device: name (OS), date: backend metrics; backend metrics."""
    rows = recipe.get("devices", []) if rows is None else rows
    groups: dict[tuple, list[dict]] = {}
    for r in rows:
        groups.setdefault((r.get("name", "?"), r.get("os", ""), r.get("date", "")), []).append(r)
    out = []
    for (name, os_, date), rs in groups.items():
        head = f"{name}, {os_}" if os_ else name
        out.append(f"{head}, {date}: " + "; ".join(row_metrics(r) for r in rs))
    return " ".join(out)


def status_word(status: str) -> str:
    return status.replace("_", " ")


def first_sentence(text: str) -> str:
    m = re.match(r"(.+?\.)(\s|$)", text)
    return m.group(1) if m else text


def provenance_lines(recipe: dict) -> list[str]:
    p = recipe.get("provenance", {})
    commit = p.get("commit", "none yet")
    if p.get("commit_note"):
        commit += f" ({p['commit_note']})"
    return [
        f"- Converted and verified by: {p.get('converted_by', 'none yet')}",
        f"- Recipe: {p.get('recipe_origin', 'none yet')}",
        f"- Measurements: {p.get('measurement_report', 'none yet')}",
        f"- Commit: {commit}",
        f"- Maintained at: {p.get('maintainer', 'none yet')}",
    ]


# ---------------------------------------------------------------- context


class Context:
    def __init__(self, root: Path, hub: dict, listing: dict | None):
        self.root = root
        self.hub = hub
        self.recipes: list[dict] = hub.get("recipes", [])
        self.listing = listing
        self.by_id = {r["id"]: r for r in self.recipes}
        self._h1: dict[str, str] = {}

    def recipe(self, rid: str) -> dict:
        if rid not in self.by_id:
            raise RenderError(f"unknown recipe id {rid!r} (ids: {', '.join(self.by_id)})")
        return self.by_id[rid]

    def question(self, recipe: dict) -> tuple[str, str] | None:
        """(H1 text, repo-relative path) of the recipe's question page."""
        page = recipe.get("question_page")
        if not page:
            return None
        if page not in self._h1:
            text = (self.root / page).read_text(encoding="utf-8")
            h1 = next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), page)
            self._h1[page] = h1
        return self._h1[page], page


def page_link(ctx: Context, recipe: dict, where: Path) -> str:
    q = ctx.question(recipe)
    if not q:
        return ""
    h1, page = q
    if where.parent.name == "docs":
        target = Path(page).name
    elif where.name == "llms.txt":
        target = f"{HUB_RAW}/{page}"
    else:
        target = page
    return f"[{h1}]({target})"


# ---------------------------------------------------------------- templates


def tpl_recipes_table(ctx: Context, where: Path) -> str:
    lines = ["| Recipe | Question it answers | Runtime | Verified on | Status |", "|---|---|---|---|---|"]
    for r in ctx.recipes:
        guide = r.get("provenance", {}).get("recipe_origin")
        title = r.get("title") or r.get("task", r["id"])
        name = f"[{title}]({guide}) (`{r['id']}`)" if guide else f"{title} (`{r['id']}`)"
        verified = device_summary(r, pinned_rows(r)) or "none yet"
        lines.append(f"| {name} | {page_link(ctx, r, where)} | {runtime_text(r)} | {verified} | {status_word(r['status'])} |")
    return "\n".join(lines)


def tpl_llms_recipes(ctx: Context, where: Path) -> str:
    lines = []
    for r in ctx.recipes:
        p = r.get("provenance", {})
        title = r.get("title") or r.get("task", r["id"])
        guide = p.get("recipe_origin", "")
        verified = device_summary(r, pinned_rows(r)) or "none yet"
        verify = r.get("verify", {}).get("command")
        parts = [f"- [{title}]({guide}): {runtime_text(r)}; {verified}"]
        if verify:
            parts.append(f" Verify: `{verify.split('   #')[0].strip()}`.")
        if r.get("source"):
            parts.append(f" Machine-readable: [recipe.json]({r['source']}).")
        parts.append(
            f" Converted and verified by {p.get('converted_by', 'none yet')}; measurements {p.get('measurement_report', 'none yet')};"
            f" commit {p.get('commit', 'none yet')}; issues {p.get('maintainer', 'none yet')}. Status: {status_word(r['status'])}."
        )
        lines.append("".join(parts))
    return "\n".join(lines)


def size_in_name(repo_id: str) -> str:
    """The parameter figure written in the repository name, as written; blank when the name has none."""
    name = repo_id.split("/")[-1]
    m = re.search(r"(?<![A-Za-z0-9.])(\d+(?:\.\d+)?[BbMm])(?![A-Za-z])", name)
    return m.group(1) if m else ""


def tpl_ungated_list(ctx: Context, where: Path) -> str:
    if not ctx.listing:
        raise RenderError(f"{CACHE} is missing; run `python tools/render.py --fetch` once")
    repos = ctx.listing["repos"]
    fetched = ctx.listing["fetched"]

    def is_gemma(r):
        return "gemma" in r["id"].lower() or "gemma" in (r.get("base_model") or "").lower()

    ungated = [r for r in repos if r["gated"] is False and not is_gemma(r)]
    gemma_open = [r for r in repos if r["gated"] is False and is_gemma(r)]
    gated = [r for r in repos if r["gated"] is not False]
    lines = [
        f"Read from the Hugging Face API on {fetched}: {len(repos)} repositories under "
        f"[litert-community](https://huggingface.co/litert-community) carry a `.litertlm` file, and "
        f"{len(ungated)} of them are neither gated nor a Gemma model. They are listed below by the task on "
        f"their card, with the base model and the license exactly as the card metadata gives them. "
        f"The size column is the figure written in the repository name, not a count of the weights; "
        f"repositories whose name carries none are left blank. Not listed: {len(gemma_open)} ungated Gemma "
        f"repositories and {len(gated)} gated ones ("
        + ", ".join(f"[{r['id'].split('/')[-1]}]({hf_url(r['id'])})" for r in gated)
        + ")."
    ]
    tags = [t for t in PIPELINE_ORDER if any(r.get("pipeline_tag") == t for r in ungated)]
    tags += sorted({r.get("pipeline_tag") for r in ungated if r.get("pipeline_tag") not in PIPELINE_ORDER and r.get("pipeline_tag")})
    if any(r.get("pipeline_tag") is None for r in ungated):
        tags.append(None)
    for tag in tags:
        group = [r for r in ungated if r.get("pipeline_tag") == tag]
        lines.append("")
        lines.append(f"**{PIPELINE_LABEL.get(tag, tag)}** ({len(group)})")
        lines.append("")
        lines.append("| repository | base model | license | size in name | `.litertlm` files | last updated |")
        lines.append("|---|---|---|---|---|---|")
        for r in sorted(group, key=lambda r: ((r.get("base_model") or "").lower(), r["id"].lower())):
            base = r.get("base_model") or ""
            base_cell = f"[{base}]({hf_url(base)})" if base and "/" in base else base
            lic = r.get("license") or ""
            if r.get("license_name") and lic == "other":
                lic = f"other ({r['license_name']})"
            files = "<br>".join(f"`{f}`" for f in r["files"])
            lines.append(
                f"| [{r['id'].split('/')[-1]}]({hf_url(r['id'])}) | {base_cell} | {lic} | {size_in_name(r['id'])} | {files} | {r['last_modified']} |"
            )
    return "\n".join(lines)


def tpl_recipe_answer(ctx: Context, where: Path, recipe: dict) -> str:
    m = recipe.get("model", {})
    p = recipe.get("provenance", {})
    model = f"[{m.get('hf_repo')}]({hf_url(m['hf_repo'])})" if m.get("hf_repo") else "none yet"
    if m.get("file"):
        model += f" `{m['file']}`"
    facts = []
    if m.get("bytes"):
        facts.append(f"{num(m['bytes'])} bytes")
    if m.get("license"):
        facts.append(m["license"])
    if m.get("base_model"):
        facts.append(f"from [{m['base_model']}]({hf_url(m['base_model'])})")
    if facts:
        model += f" ({', '.join(facts)})"
    verified = device_summary(recipe, pinned_rows(recipe)) or "none yet"
    return (
        f"**{recipe.get('task', '')}.** Model: {model}. Runtime: {runtime_text(recipe)}. "
        f"Verified: {verified}. Status: {status_word(recipe['status'])}. "
        f"Guide: {p.get('recipe_origin', 'none yet')}"
        + (f"; machine-readable: {recipe['source']}." if recipe.get("source") else ".")
    )


def tpl_recipe_conditions(ctx: Context, where: Path, recipe: dict) -> str:
    lines = ["| | |", "|---|---|"]
    for section, key, label in CONDITION_ROWS:
        value = recipe.get(section, {}).get(key)
        if value in (None, "", []):
            continue
        if key in ("url", "spm"):
            value = f"<{value}>"
        elif key == "hf_repo" or key == "base_model" or key == "source_repo":
            value = f"[{value}]({hf_url(value)})"
        elif key in ("file", "sha256", "maven", "pip", "command", "script"):
            value = f"`{value}`"
        elif key == "patches":
            value = "; ".join(value) if isinstance(value, list) else value
        lines.append(f"| {label} | {cell(value)} |")
    return "\n".join(lines)


def tpl_recipe_steps(ctx: Context, where: Path, recipe: dict) -> str:
    i = recipe.get("integrate", {})
    v = recipe.get("verify", {})
    base = blob_base(recipe)
    out: list[str] = []
    n = 0
    if i.get("deps"):
        n += 1
        out += [f"{n}. Dependency lines, exactly as they go into the build file:", "", "   ```"]
        out += [f"   {d}" for d in i["deps"]]
        out += ["   ```"]
        extra = []
        if i.get("min_sdk"):
            extra.append(f"minSdk {i['min_sdk']}")
        if i.get("min_os"):
            extra.append(f"minimum OS {i['min_os']}")
        if i.get("pins"):
            extra.append("pins " + ", ".join(f"`{k}` {val}" for k, val in i["pins"].items()))
        if i.get("gradle"):
            extra.append("Gradle: " + "; ".join(i["gradle"]))
        if i.get("manifest"):
            extra.append("manifest: " + "; ".join(i["manifest"]))
        if extra:
            out += ["", "   " + ". ".join(extra) + "."]
        out.append("")
    if i.get("files"):
        n += 1
        out.append(f"{n}. Files to copy into the app:")
        for f in i["files"]:
            out.append(f"   - [`{Path(f).name}`]({base}{f})" if base else f"   - `{f}`")
        out.append("")
    if i.get("swift"):
        n += 1
        out += [f"{n}. Code:", "", "   ```swift", f"   {i['swift']}", "   ```", ""]
    if i.get("model_delivery"):
        n += 1
        out += [f"{n}. Model delivery: {i['model_delivery']}", ""]
    for key, label in (("stop", "Stop"), ("release", "Release"), ("second_turn", "Second turn")):
        if i.get(key):
            n += 1
            out += [f"{n}. {label}: {i[key]}", ""]
    if v.get("command"):
        n += 1
        out += [f"{n}. Verify:", "", "   ```sh", f"   {v['command']}", "   ```", ""]
        if v.get("expected"):
            out += [f"   Expected, from the run recorded in recipe.json: {v['expected']}", ""]
        if v.get("host_parity"):
            out += [f"   Host parity: {v['host_parity']}", ""]
        if v.get("device_command"):
            out += [f"   Device command: {v['device_command']}", ""]
    if i.get("test_files"):
        out.append("   Test files: " + ", ".join(f"[`{Path(f).name}`]({base}{f})" if base else f"`{f}`" for f in i["test_files"]))
        out.append("")
    if not out:
        return "No integration steps recorded yet."
    return "\n".join(out).rstrip()


def tpl_recipe_limits(ctx: Context, where: Path, recipe: dict) -> str:
    items = recipe.get("unverified", [])
    dates = sorted({r.get("date", "") for r in recipe.get("devices", []) if r.get("date")})
    head = f"Not verified as of {dates[-1]}:" if dates else "Not verified:"
    lines = [head, ""] + [f"- {u}" for u in items] if items else ["Nothing recorded as unverified yet."]
    regate = recipe.get("regate")
    if isinstance(regate, dict) and regate:
        lines += ["", "Re-gate notes:", ""] + [f"- {k}: {val}" for k, val in regate.items()]
    return "\n".join(lines)


def tpl_recipe_measurements(ctx: Context, where: Path, recipe: dict) -> str:
    rows = recipe.get("devices", [])
    if not rows:
        return "No device row yet."
    cols = [(k, label) for k, label in MEASUREMENT_COLUMNS if any(k in r for r in rows)]
    lines = ["| " + " | ".join(label for _, label in cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        lines.append("| " + " | ".join(cell(r.get(k)) for k, _ in cols) + " |")
    notes = []
    for r in rows:
        who = f"{r.get('name', '?')}, {r.get('accelerator', '')}, {r.get('date', '')}".replace(", ,", ",")
        bits = []
        if r.get("soc"):
            bits.append(f"SoC {r['soc']}")
        if r.get("conditions"):
            bits.append(r["conditions"])
        if r.get("model_provisioned_via"):
            bits.append(f"model provisioned via {r['model_provisioned_via']}")
        if r.get("source"):
            bits.append(f"Source: {r['source']}")
        if bits:
            notes.append(f"- {who}: " + ". ".join(bits) + ".")
    if notes:
        lines += ["", "Conditions:", ""] + notes
    return "\n".join(lines)


def tpl_provenance(ctx: Context, where: Path, recipe: dict) -> str:
    return "\n".join(provenance_lines(recipe))


TEMPLATES = {
    "recipes-table": tpl_recipes_table,
    "ungated-litertlm-list": tpl_ungated_list,
    "llms-recipes": tpl_llms_recipes,
}
RECIPE_TEMPLATES = {
    "recipe-answer": tpl_recipe_answer,
    "recipe-conditions": tpl_recipe_conditions,
    "recipe-steps": tpl_recipe_steps,
    "recipe-limits": tpl_recipe_limits,
    "recipe-measurements": tpl_recipe_measurements,
    "provenance": tpl_provenance,
}


def render_key(ctx: Context, key: str, where: Path) -> str:
    if key in TEMPLATES:
        return TEMPLATES[key](ctx, where)
    name, sep, rid = key.partition(":")
    if sep and name in RECIPE_TEMPLATES:
        return RECIPE_TEMPLATES[name](ctx, where, ctx.recipe(rid))
    raise RenderError(f"{where}: unknown gen key {key!r}")


# ---------------------------------------------------------------- marker injection


def inject(ctx: Context, where: Path, text: str) -> str:
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        m = START_RE.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        key, indent = m.group("key"), m.group("indent")
        end = f"<!-- gen:{key}:end -->"
        try:
            j = next(k for k in range(i + 1, len(lines)) if lines[k].strip() == end)
        except StopIteration:
            raise RenderError(f"{where}: `{key}` has a start marker at line {i + 1} but no end marker") from None
        body = render_key(ctx, key, where)
        out.append(lines[i])
        out += [(indent + line) if line else "" for line in body.split("\n")]
        out.append(lines[j])
        i = j + 1
    return "\n".join(out)


def text_targets(root: Path) -> list[Path]:
    found = [root / f for f in TEXT_FILES if (root / f).is_file()]
    for pattern in TEXT_GLOBS:
        found += sorted(p for p in root.glob(pattern) if p.is_file())
    return [p for p in found if "gen:" in p.read_text(encoding="utf-8")]


# ---------------------------------------------------------------- out/<id>/ files


def card_addendum(ctx: Context, recipe: dict) -> str:
    m = recipe.get("model", {})
    p = recipe.get("provenance", {})
    rt = recipe.get("runtime", {})
    target = m.get("source_repo") or m.get("base_model") or "(no base model recorded)"
    platform = PLATFORM_LABEL.get(recipe.get("platform", ""), recipe.get("platform", ""))
    acc = str(rt.get("accelerator", "")).upper()
    label = f"{platform} ({rt.get('name', '')}{', ' + acc if acc else ''})"
    converted = f"[{m.get('hf_repo')}]({hf_url(m['hf_repo'])})" if m.get("hf_repo") else "none yet"
    summary = device_summary(recipe, pinned_rows(recipe)) or "no device row yet"
    verify = recipe.get("verify", {})
    if verify.get("host_parity"):
        evidence = f"Output against the reference: {verify['host_parity']}."
    elif any(r.get("parity") for r in recipe.get("devices", [])):
        evidence = "Output against the reference: " + "; ".join(r["parity"] for r in recipe["devices"] if r.get("parity")) + "."
    elif verify.get("command"):
        evidence = f"The recipe's verify command (`{verify['command'].split('   #')[0].strip()}`) passed: {first_sentence(verify.get('expected', ''))}"
    else:
        evidence = "No verify command recorded yet."
    lines = [
        f"# Card addendum for {target} (recipe `{recipe['id']}`)",
        "",
        f"Target: the author's card, <{hf_url(target)}>. The converted file lives in {converted}; the line below goes",
        "under the card's own \"how to run\" or implementations list. Form: docs/provenance.md, \"Pull request to a",
        "model author's README\". The opening in [brackets] is written by hand for the card it goes to.",
        "",
        "## The line to add",
        "",
        f"- **{label}**: {converted} — {summary}; recipe for an app that already exists: {p.get('recipe_origin', 'none yet')}",
        "",
        "## Pull request body (the line, the evidence, who fixes it)",
        "",
        f"[Thanks for <what the card does well>.] This adds one line for an {platform} build of "
        f"{target.split('/')[-1]}: the weights as `{m.get('file', '')}` running through {rt.get('name', '')} "
        f"{rt.get('version', '')}{' on the ' + acc if acc else ''}, with the recipe for an app that already exists.",
        "",
        f"- {summary} (report: {p.get('measurement_report', 'none yet')}).",
        f"- {evidence}",
        f"- Recipe: {p.get('recipe_origin', 'none yet')}, at {p.get('commit', 'none yet')}. If it breaks on a newer runtime, file it at {p.get('maintainer', 'none yet')} and I will fix it.",
        "",
        "Happy to shorten the line or drop it if you would rather keep the card to your own implementations. Thanks again.",
        "",
        "## Provenance",
        "",
    ] + provenance_lines(recipe)
    return "\n".join(lines) + "\n"


def page_block(ctx: Context, recipe: dict) -> str:
    rid = recipe["id"]
    where = ctx.root / "docs" / "page-block.md"
    parts = [
        ("Direct answer", "recipe-answer"),
        ("Conditions", "recipe-conditions"),
        ("Steps", "recipe-steps"),
        ("Limits", "recipe-limits"),
        ("Real-device measurements", "recipe-measurements"),
        ("Provenance", "provenance"),
    ]
    lines = [
        f"# Page block for `{rid}`",
        "",
        "Paste any region into a question page; `tools/render.py` keeps the text between the markers current.",
        "",
    ]
    for heading, key in parts:
        full = f"{key}:{rid}"
        lines += [f"## {heading}", "", f"<!-- gen:{full}:start -->", render_key(ctx, full, where), f"<!-- gen:{full}:end -->", ""]
    return "\n".join(lines)


def litert_side_addendum(ctx: Context, recipe: dict) -> str:
    m = recipe.get("model", {})
    p = recipe.get("provenance", {})
    title = recipe.get("title") or recipe.get("task", recipe["id"])
    platform = PLATFORM_LABEL.get(recipe.get("platform", ""), recipe.get("platform", ""))
    rows = pinned_rows(recipe)
    summary = device_summary(recipe, rows) or "no device row yet"
    devices = "; ".join(sorted({f"{r.get('name', '?')}, {r.get('os', '')}" for r in rows})) or "no device yet"
    dates = sorted({r.get("date", "") for r in rows if r.get("date")})
    lines = [
        f"# LiteRT-side lines for `{recipe['id']}`",
        "",
        "## awesome-litert (Running models in your app › Recipes)",
        "",
        f"- [{title}]({p.get('recipe_origin', '')}) — {runtime_text(recipe)}; {summary}; verify command and machine-readable recipe.json"
        + (f" ({recipe['source']})." if recipe.get("source") else "."),
        "",
        "## Official sample list, one line (offered through the FYI, never as a cold PR)",
        "",
        f"* **{title}** (community recipe): [{m.get('hf_repo', '')}]({hf_url(m.get('hf_repo', ''))}) on {runtime_text(recipe)}, "
        f"added to an existing {platform} app; {status_word(recipe['status'])} on {devices}"
        + (f", {dates[-1]}" if dates else "")
        + f"; {p.get('recipe_origin', '')}",
        "",
        "## Provenance",
        "",
    ] + provenance_lines(recipe)
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- driver


def fetch_listing() -> dict:
    with urllib.request.urlopen(HF_LIST_URL, timeout=60) as resp:  # noqa: S310
        models = json.loads(resp.read().decode("utf-8"))
    repos = []
    for m in models:
        files = sorted(s["rfilename"] for s in m.get("siblings", []) if s["rfilename"].endswith(".litertlm"))
        if not files:
            continue
        card = m.get("cardData") or {}
        tags = m.get("tags") or []
        base = card.get("base_model")
        if isinstance(base, list):
            base = ", ".join(base)
        if not base:
            base = next((t.split(":", 2)[2] for t in tags if re.match(r"^base_model:(finetune|quantized|merge|adapter):", t)), None)
        lic = card.get("license") or next((t.split(":", 1)[1] for t in tags if t.startswith("license:")), None)
        repos.append(
            {
                "id": m["id"],
                "gated": m.get("gated", False),
                "license": lic,
                "license_name": card.get("license_name"),
                "base_model": base,
                "pipeline_tag": m.get("pipeline_tag"),
                "last_modified": m["lastModified"][:10],
                "files": files,
            }
        )
    repos.sort(key=lambda r: r["id"].lower())
    return {
        "source": HF_LIST_URL,
        "fetched": dt.date.today().isoformat(),
        "note": "Every litert-community repository that carries a .litertlm file, with gated, license, base_model, pipeline_tag and lastModified as the API returned them. Refresh: python tools/render.py --fetch.",
        "repositories_listed": len(models),
        "repos": repos,
    }


def render_all(ctx: Context) -> dict[Path, str]:
    """Every file the generator writes, with its new content (repo-relative path -> text)."""
    result: dict[Path, str] = {}
    for path in text_targets(ctx.root):
        result[path.relative_to(ctx.root)] = inject(ctx, path, path.read_text(encoding="utf-8"))
    for r in ctx.recipes:
        d = Path("out") / r["id"]
        result[d / "card-addendum.md"] = card_addendum(ctx, r)
        result[d / "page-block.md"] = page_block(ctx, r)
        result[d / "litert-side-addendum.md"] = litert_side_addendum(ctx, r)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--check", action="store_true", help="diff the tree against a fresh render; exit 1 on drift")
    parser.add_argument("--fetch", action="store_true", help=f"refresh {CACHE} from the Hugging Face API first")
    parser.add_argument("--refresh", action="store_true", help="re-vendor every entry of recipes.json from its source URL first")
    args = parser.parse_args(argv)
    root = args.root.resolve()

    hub_path = root / "recipes.json"
    hub = json.loads(hub_path.read_text(encoding="utf-8"))
    if args.refresh:
        for entry in list(hub.get("recipes", [])):
            if entry.get("source"):
                vendor.vendor(hub, entry["id"], vendor.load_canonical(entry["source"]))
                print(f"render: re-vendored {entry['id']} from {entry['source']}")
        hub["updated"] = dt.date.today().isoformat()
        hub_path.write_text(json.dumps(hub, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    cache_path = root / CACHE
    if args.fetch:
        listing = fetch_listing()
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(listing, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"render: fetched {listing['repositories_listed']} repositories, {len(listing['repos'])} with a .litertlm file -> {CACHE}")
    listing = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.is_file() else None

    ctx = Context(root, hub, listing)
    try:
        rendered = render_all(ctx)
    except RenderError as err:
        print(f"render: ERROR: {err}", file=sys.stderr)
        return 2

    if args.check:
        drift = 0
        for rel, new in rendered.items():
            if rel.parts[0] == "out":
                continue  # out/ is not tracked; the regions it mirrors are checked through the pages
            old = (root / rel).read_text(encoding="utf-8")
            if old != new:
                drift += 1
                sys.stdout.writelines(
                    difflib.unified_diff(old.splitlines(keepends=True), new.splitlines(keepends=True), fromfile=f"{rel} (tree)", tofile=f"{rel} (render)")
                )
                print()
        if drift:
            print(f"render --check: FAILED ({drift} file(s) drift from recipes.json / {CACHE}); fix: python tools/render.py, then commit")
            return 1
        print(f"render --check: OK ({len([r for r in rendered if r.parts[0] != 'out'])} files, no drift)")
        return 0

    changed = []
    for rel, new in rendered.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.is_file() or path.read_text(encoding="utf-8") != new:
            path.write_text(new, encoding="utf-8")
            changed.append(rel)
    print(f"render: {len(rendered)} files rendered, {len(changed)} changed" + (": " + ", ".join(str(c) for c in changed) if changed else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
