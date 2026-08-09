# CLAUDE.md — BKWILDCARDS

Guidance for Claude Code working in this repository.

---

## What this is

A ComfyUI custom node that turns a bundled wildcard library into scoped dropdowns and toggles and emits a finished prompt string. No wildcard syntax for the user to learn, no `__token__` to type.

**Owner:** Brian (`bkidderz`) · **Repo:** `BKWILDCARDS` · **Current version:** `0.6.5`
**Git:** initialised, ~12 local commits, **no remote yet** — GitHub is deliberately deferred until 1.0.
**Install path on owner's machine:**
`C:\Users\brian\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\custom_nodes\BKWILDCARDS`

The owner runs **ComfyUI Desktop (Electron)**. This matters — see the caching note under Open Bug.

## What it is NOT

- Not a workflow, subgraph, blueprint, or node template.
- Not a reimplementation of `ImpactWildcardProcessor`. **The syntax engine is out of scope**: no brace expansion, no nesting, no `$$`, no `::` weighting, no glob aggregation. Reading a file and picking a line is in scope; parsing `{a|b|c}` is not.

---

## Repo layout

```
BKWILDCARDS/
├── __init__.py                 NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, WEB_DIRECTORY
├── pyproject.toml              version, Registry metadata (license + PublisherId still TODO)
├── README.md                   user-facing
├── CLAUDE.md                   this file
├── .github/workflows/publish.yml   inert until Registry setup
├── bkwildcards/
│   ├── __init__.py             re-exports; wraps routes import in try/except
│   ├── library.py              pack/category scanning, section parsing, seeding, draw()
│   ├── nodes.py                node classes, scope gating, PNG metadata stamping
│   └── routes.py               GET /bkwildcards/layout · POST /bkwildcards/populate (cosmetic)
├── web/bkwildcards.js          scope hiding, relabelling, resolved-box population
└── wildcards/
    ├── common/    ancestry.txt · metatypes.txt            (global)
    ├── female/    builds.txt                              (global, gender: Female)
    ├── male/      _pack.json only, no files yet           (global, gender: Male)
    ├── cyberpunk/ tattoos outfits weapons accent_palette environments poses
    └── fantasy/   tattoos outfits weapons accent_palette
```

---

## Architecture — invariants that must not be traded away

**1. Python is authoritative. JavaScript is cosmetic.**
`nodes._in_scope()` decides what can contribute to a prompt. `web/bkwildcards.js` only *hides* out-of-scope widgets. If the extension fails to load, output stays correct and the node just looks cluttered. Never move gating into the browser.

**2. Never reorder `node.widgets` in JavaScript.**
`widgets_values` in a saved workflow is a positional array. Reordering the widget array desyncs it silently and permanently. Ordering changes go in `INPUT_TYPES` in Python, where at least a version bump warns the user.

**3. Input order is frozen at 1.0.**
Adding or moving an input shifts every `widgets_values` index after it. Pre-1.0 this has been broken several times deliberately. After publish, new inputs go on the END only.

**4. `{pack}_{id}` input names are permanent.**
That string is stored in every saved workflow. Moving a file between packs or changing its `id` breaks saved workflows. Display labels are safe to rename; `id` is not.

**5. Never use Python's `hash()` for seeding.**
It is salted per process, so the same seed would give different picks in different ComfyUI sessions. `library.stable_offset()` uses `zlib.crc32`.

**6. PNG persistence writes to `properties`, not `widgets_values`.**
`widgets_values` is positional and shifts when the frontend adds widgets such as `control_after_generate`.

**7. Metadata stamping must never break a render.**
`nodes._stamp_workflow()` is wrapped in a bare `except`. Keep it that way.

---

## Two orderings, and they are different

| Field | Controls | Default |
|---|---|---|
| `order` | position **in the emitted prompt** | 500 |
| `display` | position **on the node** | falls back to `order` |

Build sits at `display: 5` (directly under the scope dropdowns) but `order: 15` (emits after Ancestry). Do not conflate them.

Current prompt order: ancestry 10 → build 15 → metatype 20 → tattoos 30 → outfit 40 → weapons 50 → palette 60 → environment 70 → pose 80.

---

## Data model — `_pack.json`

Pack level:

```json
{
  "pack": "female",
  "label": "Female",
  "global": true,
  "gender": "Female",
  "entries": [ ... ]
}
```

- `global: true` — active under every theme. Every non-global pack becomes a **theme** in the dropdown.
- `gender` — active only when that gender is selected. Every distinct value becomes a **gender** option, including for a pack with no files (that is why `wildcards/male/` exists).
- The two axes compose independently.

Entry level:

```json
{
  "file": "builds.txt",
  "id": "build",
  "label": "Build",
  "order": 15,
  "display": 5,
  "select": "section",
  "default": false
}
```

`select: "section"` turns the file's `#` headers into dropdown options instead of a boolean toggle. Reserved options are `library.SECTION_OFF` (`— off —`) and `library.SECTION_ANY` (`— random —`), both em-dash-wrapped so a section literally named "off" cannot collide.

Files not listed in `entries` still load, with labels derived from the filename.

### Section header parsing

`library.clean_section_name()` strips leading `#` and dashes, cuts at the first `(` or `[`, trims, and title-cases. **Cleaning happens before the 40-character length test** — deliberately. A raw header like `# -- orks, trolls, dwarves (Shadowrun-style — come in every ancestry, skin unchanged)` is 80+ chars and would fail a raw length test, but cleans to `Orks, Trolls, Dwarves`. Lines starting `=` and all-punctuation rules are rejected as prose. Duplicate labels get a numeric suffix.

### Wildcard file format

One entry per line. Blank lines ignored. `#` lines are section headers (used only by `select: "section"` categories, ignored otherwise).

---

## Content inventory

| Pack | Category | Entries | Selector |
|---|---|---|---|
| common (global) | Ancestry | 44 | 16 sections |
| common (global) | Metatype / Species | 53 | 32 sections |
| female (global, Female) | Build | 61 | 5 sections |
| cyberpunk | Tattoos / Outfits / Weapons / Accent Palette / Environments / Poses | 75 / 270 / 28 / 28 / 24 / 29 | toggles |
| fantasy | Tattoos / Outfits / Weapons / Accent Palette | 75 / 360 / 30 / 31 | toggles |

All content is Brian's original work. The TrashAI `totalChaosRandomizer` workflow was a **UX reference only** — none of its data is used. Content is also published on Civitai; which source is canonical is undecided.

Metatypes were merged from two drifted per-theme files into one shared `common/metatypes.txt`. Where wording differed, **both lines were kept as variants** rather than one being discarded. Nine sections have multiple variants (Tiefling 6, Dark Elf 4, Vampire 8, …).

---

## RESOLVED (v0.6.5) — resolved-text box now updates every queue

**Was (owner-reported):** the `resolved` textarea did not visibly change per run — it appeared to update only when the whole generation finished. Randomisation and the PNG round-trip were always correct; the problem was purely visible feedback, and users read "box didn't change" as "wildcards didn't re-roll." The reference behaviour was ImpactWildcardProcessor, whose text box changes on every queue.

**Root cause was architectural, not a bug in the display code.** BK computed the prompt server-side during execution and pushed it to the box *after* the node ran, via `{"ui": {"bk_resolved": [...]}}` + `onExecuted`. Impact does the opposite: it populates `populated_text` at **queue time, before execution**. Confirmed from the installed Impact source — `ImpactWildcardProcessor.doit()` returns `(populated_text,)` with **no `ui` channel**; a `POST /impact/wildcards` endpoint resolves the text (impact_server.py); its own DESCRIPTION says *"Before the workflow is executed … is displayed in populated_text."* No amount of post-execution DOM-writing could move BK's update to queue time, which is why the v0.6.2–v0.6.4 display fixes never satisfied the symptom.

**The v0.6.3 cache hypothesis was disproven.** A fresh node reported `build 0.6.4` before any run, so the new JS was live on the owner's machine. It was never a cached-ES-module problem; the earlier "hard-refresh" theory was a dead end.

### The fix — Impact's timing, but Python stays authoritative

- **`nodes.resolve_prompt(seed, separator, gender, theme, choices)`** — the draw loop extracted from `build()`. Single source of truth; `build()` calls it, behaviour unchanged.
- **`POST /bkwildcards/populate`** (routes.py) calls the **same** function over the **same** module-cached category scan, so a preview cannot drift from the generated image.
- **`web/bkwildcards.js`** wraps `api.queuePrompt(number, {output, workflow})`, reads our node's final `inputs` from the outgoing payload — including the seed *already advanced once* by `control_after_generate` — POSTs them, and writes the result into the box before generation starts.
- Still cosmetic (invariant #1 intact): if the endpoint is unreachable the box simply is not previewed and the generated prompt is unaffected. No widget was added, so no `widgets_values` shift (invariant #3 intact).

### Why it's correct, and how that's checked

Reading the seed **from the serialized payload** (not by re-calling `graphToPrompt`) is what makes the preview seed identical to the execution seed — calling `graphToPrompt` again would advance `control_after_generate` a second time and the box would show a different seed than the image used.

The `executed` handler cross-checks: it compares the queue-time preview against the executed text and logs `preview matched execution ✓` or, on any regression, `PREVIEW ≠ EXECUTION`. **Confirmed ✓ on the owner's machine (v0.6.5).** Headless: 400 randomised trials plus an exact-payload test, all byte-identical (see Verification).

---

## Verification

No test suite exists. Verification has been ad-hoc scripts. Worth formalising.

The headless harness runs under ComfyUI's own venv Python — no separate install needed. On the owner's machine:
`...\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe`. (There is no standalone `node` on that machine, so `node --check` is unavailable there; JS is validated by review + a real browser load.)

Import the package outside ComfyUI (`routes.py` degrades gracefully when `server`/`aiohttp` are absent):

```python
import sys; sys.path.insert(0, "<parent of BKWILDCARDS>")
from BKWILDCARDS import NODE_CLASS_MAPPINGS
from BKWILDCARDS.bkwildcards import library as L, nodes
```

Checks that have caught real bugs and should be kept:

- **Section correctness** — for every section of every `select: "section"` category, draw over N seeds and assert every result is in that section. Isolate: set all other categories off, or you will get false failures from other categories' output. *(This produced a false 100% failure rate once because the harness left booleans on.)*
- **Scope gating** — assert a gender- or theme-scoped category contributes 0/N when out of scope and N/N when in scope.
- **Cross-theme leakage** — compare against pack-**exclusive** lines only. 17 lines legitimately exist in more than one pack; naive set intersection reports false leaks.
- **Widget order** — assert `resolved` is last and the scope dropdowns are first.
- **Metadata stamping** — pass a fake `extra_pnginfo` workflow dict and assert the stamped property matches the returned prompt, survives `json.dumps`, and leaves other nodes untouched. Also pass malformed shapes (`None`, `{}`, `{"workflow": None}`, a bare string) and assert no raise.
- **JS widget hide/show round-trip** — simulate a widget with and without an own `computeSize` (see the regression note below).
- **Preview == execution** — for many seeds/choices, assert `nodes.resolve_prompt(...)` equals `BKWildcardSelector.build(...)["result"][0]` byte-for-byte, including a JSON round-trip with seed as a string and with the whole `inputs` dict passed as `choices` (extra non-category keys must be ignored). Guards the queue preview against ever drifting from the generated prompt.

Syntax gates: `python3 -m compileall bkwildcards` and `node --check web/bkwildcards.js`.

---

## Regression notes — bugs already fixed, do not reintroduce

**v0.2.0 → v0.2.1, widget restore.**
`widget.computeSize = widget._bkComputeSize ?? widget.computeSize`. Most widgets have no *own* `computeSize`, so the saved value was `undefined` and `??` resolved back to the zero-height override. Widgets could hide but never reappear. The fix records whether an own property existed (`Object.prototype.hasOwnProperty.call`) and **deletes** rather than reassigns.

**Section headers.** An early version applied a 40-character limit to the *raw* header, silently dropping over half the real sections in the metatype files. Clean first, then test length.

**Fantasy metatype `Lycanthrope`.** Before the merge, the four full-replacement forms had no `# --` header of their own and were absorbed into the section above. Resolved by the merge into `common/metatypes.txt`.

**v0.6.5, queue preview.** The box updates at queue time via `POST /bkwildcards/populate`, not by post-execution DOM writes. Two things must not be "simplified" away: (1) the preview seed is read from the serialized payload inside the `api.queuePrompt` wrapper — never re-derive it or call `graphToPrompt`, which advances `control_after_generate` a second time and makes the box show a different seed than the image uses; (2) the draw stays in `nodes.resolve_prompt` (Python), shared by `build()` and the endpoint — do not reimplement the draw in JS. The `executed` handler's `PREVIEW ≠ EXECUTION` warning exists to catch a violation of either.

---

## Reference workflow

`gladasWorkflowFor_v2.json` — the owner's daily driver, by a friend, updated frequently.

- Bolt-on target: node **118**, `StringFunction|pysssss` "Positive Prompt", `action: append`
- `text_a` holds a fixed ~799-char style block; `text_b` takes our `prompt` output; `text_c` was a now-bypassed `ImpactWildcardProcessor` (node 116)
- Output fans to `Lora Prompt Concatenation` (52) and `CLIPTextEncode` 73 (base) / 191 (upscale)

The owner's whole motivation is that this workflow updates often. Anything requiring a rebuild per workflow release defeats the point.

---

## Working agreements

These exist because they were violated.

1. **Lock scope before solutioning.** No architectures, no files, until scope is understood and output is expressly requested.
2. **Do not build unrequested features.** The `breakdown` output was offered, not accepted, built anyway, and later removed. Wasted work on both ends.
3. **Do not argue the owner toward a simpler alternative he did not ask for** — including when a learning goal is part of the ask.
4. **"Start small" means a number.** Get the number.
5. **State the basis for factual claims** — source consulted, or explicitly labelled inference. Never present inference as fact.
6. **Reproduce before fixing.** Three speculative fixes shipped for the open bug because there was no local test loop. There is one now. Use it.
7. **Content is the owner's.** Structural edits (headers, file splits) are fine to propose and execute; writing or choosing his prose is not, unless he asks. When two of his variants conflict, keep both rather than picking.

---

## Open items

| Item | Notes |
|---|---|
| ~~Resolved-text live update~~ | **Done in v0.6.5.** See the Resolved section. |
| Hair file | `krea2bk_hair.txt` uses inline `{a\|b\|c}` for colour on all 45 lines. Unsupported — emitted literally. Owner to decide: split into `hair_style` + `hair_color`, add single-level brace picking, or pre-flatten to 720 lines. Recommended: split. |
| `group` field | Schema for sub-panels within a tier. Not built. Must land before the physical-attributes tier or manifests get rewritten. |
| Physical attributes | `bk_female_face.txt` (26 lines, 1 dupe, 2 trailing commas), `bk_female_lips.txt` (11), `bk_female_nose.txt` (9) supplied but not packed. All female-scoped — `wildcards/female/` is their home. |
| Male content | `wildcards/male/` is an empty shell. |
| Dark Fantasy gaps | No `environments.txt`, no `poses.txt`. Owner is writing them. |
| Art Style | In the planned global tier; no file exists. |
| Vampire variants 1 and 3 | Near-identical merge residue (`visible subtle fangs` vs `visible fangs`). One is redundant. |
| License | `pyproject.toml` placeholder. Blocks Registry publish, not GitHub install. |
| GitHub remote | Deferred to 1.0 by owner. Learning GitHub publishing is one of his stated goals for this project. |
| Grouped panels | Frontend rendering of `group`. Deferred; the theme + gender dropdowns solved most of the clutter. |
| Canonical source | Node package vs Civitai collection. Undecided. |
| Phase 2 | Module listed as a resource on image outputs. Surface unidentified. Partially anticipated by the PNG stamping. |

## Planned hierarchy

```
gender → ancestry (optional) → metatype (optional)
→ physical attributes (hair, eyes, build) → outfits → environments → art style
```

Gender exists. Ancestry, metatype and build exist. The rest is unbuilt.
