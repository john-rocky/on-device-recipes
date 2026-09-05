# Provenance block

Every recipe, model card and question page in this ecosystem ends with the same five lines. A model author, an official sample list or an AI answer can then point at one place that says who converted and verified the model, where the recipe is, where the numbers come from, which commit they were taken at, and where to report breakage.

## The five lines

```markdown
## Provenance

- Converted and verified by: john-rocky
- Recipe: https://github.com/john-rocky/LiteRT-Models/blob/main/ormbg/INTEGRATION.md
- Measurements: https://github.com/john-rocky/LiteRT-Models/blob/main/ormbg/README.md#gpu-conversion (Pixel 8a, GPU)
- Commit: john-rocky/LiteRT-Models@47c4ccc5041fa9ccaa0d5b8a6856c67fa4060ea3
- Maintained at: https://github.com/john-rocky/LiteRT-Models/issues
```

Rules:

1. Handles only: john-rocky on GitHub, mlboydaisuke on Hugging Face. No real names.
2. The Measurements line names the device and links a report that carries a date. When there is no dated report yet, the line says `none yet`; it never carries a number without one.
3. Commit is the commit of the repository that holds the recipe, at the time the numbers were taken. It changes when the numbers are re-taken, not when unrelated files change.
4. Maintained at is an issue tracker, not a person.
5. The same five keys live in `recipe.json` under `provenance`: `converted_by`, `recipe_origin`, `measurement_report`, `commit`, `maintainer`. The Markdown block and the JSON say the same thing; `tools/check_drift.py` catches the JSON side when it drifts from its source.

## Where it goes

### recipe.json

```json
"provenance": {
  "converted_by": "john-rocky",
  "recipe_origin": "https://github.com/john-rocky/LiteRT-Models/blob/main/ormbg/INTEGRATION.md",
  "measurement_report": "https://github.com/john-rocky/LiteRT-Models/blob/main/ormbg/README.md#gpu-conversion",
  "commit": "john-rocky/LiteRT-Models@47c4ccc5041fa9ccaa0d5b8a6856c67fa4060ea3",
  "maintainer": "https://github.com/john-rocky/LiteRT-Models/issues"
}
```

### The recipe (INTEGRATION.md)

The last section of the file, `## Provenance`, with the five lines verbatim. Only a `Last verified: YYYY-MM-DD` line may follow it.

### Hugging Face model card

A `## Provenance` section after the "How to run" or "Add to your app" section and before the license section. The card's YAML front matter keeps `base_model`, `license`, `pipeline_tag` and `library_name`; the provenance block is Markdown, not YAML, so it renders and gets quoted as-is. On a card in an organization you do not own (litert-community), the line still names the handle; the organization is the publisher, the handle is who converted and verified.

### Pull request to a model author's README or an official sample list

The PR body keeps its one-line form: the line being added, the evidence that it works, and who fixes it if it breaks. The five items fold into that body as bullets; they are not pasted as a block, because the maintainer reads a request, not a record.

```markdown
Thanks for the Implementations list. This adds one line to it for an Android build of <model>:
the <weights> converted to LiteRT (.tflite) and running on the phone GPU through the LiteRT
CompiledModel API, with a Kotlin sample.

- Pixel 8a: <n> ms per frame, <k>/<k> ops on the GPU, measured <YYYY-MM-DD> (report: <url>).
- Output matches PyTorch at <parity> on <inputs>.
- Recipe and conversion script: <recipe url>, at <repo>@<sha>. If it breaks on a newer runtime, file it at <issues url> and I will fix it.

Happy to shorten the line or drop it if you would rather keep the list to official implementations. Thanks again.
```

### Question pages (this site)

The last section, `## Provenance`, with the five lines, followed by one sentence saying that the page is the canonical text and that article copies are snapshots.
