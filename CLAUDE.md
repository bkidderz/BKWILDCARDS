# CLAUDE.md — BKWILDCARDS

Guidance for Claude Code working in this repository.

---

## What this is

A ComfyUI custom node that turns a bundled wildcard library into scoped dropdowns and toggles and emits a finished prompt string. No wildcard syntax for the user to learn, no `__token__` to type.

**Owner:** Brian (`bkidderz`) · **Repo:** `BKWILDCARDS` · **Current version:** `0.8.6` (committed and pushed)
**Git:** 14 commits on `main`, pushed to **https://github.com/bkidderz/BKWILDCARDS** — currently **PRIVATE** (flip to public when ready; required before the Comfy Registry can serve it). `gh` CLI is installed and authed as `bkidderz`. `SNIPPETS.md` is gitignored (local handoff note, not product).
**Install path on owner's machine:**
`C:\Users\brian\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\custom_nodes\BKWILDCARDS`

The owner runs **ComfyUI Desktop (Electron)**. This matters — see the caching note under Open Bug.

## Theme names

The dropdown labels are the owner's standalone wildcard-release names, kept true to
those releases. Pack **directory names** and **category keys** are unchanged, so the
shorthands below are safe to use in conversation — they map to the shipped labels.

| Pack (dir / key) | Theme label (in the node) | Shorthand |
|---|---|---|
| `cyberpunk` | **_ghost.runner** | Cyberpunk |
| `fantasy` | **Whimsical Woods** | Fantasy / Dark Fantasy |
| `dresses` | **All the Dresses** | Dresses / Gowns |
| `cassette_futurism` | **Cassette Futurism** | Cassette |
| `autumnal_oxidation` | **Autumnal Oxidation** | Autumnal / Goth |
| `lingerie` | **COZY SEXY LACY RACY Sleepwear** | Lingerie (adult) |

Globals (not themes): `common` (Identity: ancestry, metatype), `female` (Physical: build, face, nose, lips — gender: Female), `hair` (color/type/style), `shots` (Camera: angle, framing).

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
├── web/bkwildcards.js          scope hiding, section headers, queue-preview, connection colour, node title
└── wildcards/
    ├── common/     ancestry · metatypes                    (global — Identity)
    ├── female/     builds · face · nose · lips             (global, gender: Female — Physical)
    ├── male/       builds · face · nose · lips             (global, gender: Male — Physical, authored 0.8.1)
    ├── hair/       color · type · style                    (global — Hair)
    ├── shots/      angle · framing                         (global — Camera)
    ├── cyberpunk/  tattoos outfits weapons accent_palette environments poses
    ├── fantasy/    tattoos outfits weapons accent_palette environments poses spell_casting spell_effects
    ├── cassette_futurism/ outfits accent_palette environments poses
    ├── autumnal_oxidation/ outfits accent_palette environments poses   (granular pieces removed in 0.7.12)
    ├── dresses/    dresses · eastern · accent_palette · environments · poses
    └── lingerie/   sets                                    (adult)
```

---

## Architecture — invariants that must not be traded away

**1. Python is authoritative. JavaScript is cosmetic.**
`nodes._in_scope()` decides what can contribute to a prompt. `web/bkwildcards.js` only *hides* out-of-scope widgets. If the extension fails to load, output stays correct and the node just looks cluttered. Never move gating into the browser.

**2. Never reorder the *serializable* `node.widgets` in JavaScript.**
`widgets_values` in a saved workflow is a positional array. Reordering the real widgets desyncs it silently and permanently. Ordering changes go in `INPUT_TYPES` in Python, where at least a version bump warns the user. **Exception (v0.7.x):** the JS inserts non-interactive **section-header** rows into `node.widgets`, but each is marked `serialize: false`. This ComfyUI version's serialize loop skips them on *both* save and load (`if (r.serialize === false) continue`), so they consume **no** `widgets_values` slot and never shift the real widgets' indices. That `serialize: false` is load-bearing — do not remove it, and do not add serialized widgets in JS.

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

## Two orderings + on-node sections

| Field | Controls | Default |
|---|---|---|
| `order` | position **in the emitted prompt** | 500 |
| `display` | position **on the node** | falls back to `order` |
| `group` | which **titled section** the category sits under on the node | none |

Do not conflate `order` and `display`. `display` is set so each `group`'s categories are **contiguous** on the node; the JS draws a header row at each group boundary.

**On-node section order (v0.7.x):** Theme → Identity (gender, ancestry, metatype) → Physical (build, face, nose, lips) → Hair (type, style, color) → Wardrobe (theme outfits/tattoos/weapons) → Scene (palette, environment, poses, spell) → Camera (shot angle, framing) → Settings (separator, seed, control-after-generate) → output box. **Camera is a global but is pinned *after* the theme block** — `INPUT_TYPES` emits `POST_THEME_GROUPS = {"Camera"}` globals after all theme blocks. `theme`/`gender`/`separator`/`seed`/`label_output` get their section from `SPECIAL_GROUPS` in the JS (they carry no `group` in the layout).

**Prompt order (`order`):** ancestry 10 → build 15 → face/nose/lips 22/24/26 → hair 27–29 → metatype 20 → tattoos 30 → outfit 40 → weapons 50 → palette 60 → environment 70 → pose 80 → spell 82/85 → shots 90/92.

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
  "display": 20,
  "select": "section",
  "default": false,
  "group": "Physical",
  "prompt_label": "build"
}
```

- `select: "section"` turns the file's `#` headers into dropdown options instead of a boolean toggle (off / random / each section). Reserved options are `library.SECTION_OFF` (`— off —`) and `library.SECTION_ANY` (`— random —`), em-dash-wrapped so a section literally named "off" cannot collide. **A `section` category with no usable headers silently falls back to a toggle** — that is why a flat file (e.g. the dresses "Gowns & Dresses" list) stays on/off. Most theme categories were converted to `section` across 0.7.8–0.7.11.
- `group` — the on-node section header the category renders under (Identity / Physical / Hair / Wardrobe / Scene / Camera). Cosmetic; drives display grouping only.
- `prompt_label` — the tag emitted when the node's **Labeled output** toggle is on (`build: …`, `hair: …`). Categories that share a `prompt_label` **and** are adjacent in `order` merge under one label (the three hair categories → one `hair:` line).

**Removing a category = delete its `.txt` file, not just its `entries` row.** `library._load_pack` scans *every* `.txt` in the pack dir and loads undeclared files with a filename-derived label. (This is how the goth granular pieces were removed in 0.7.12 — files deleted, not just de-listed.)

### Section header parsing

`library.clean_section_name()` strips leading `#` and dashes, cuts at the first `(` or `[`, trims, and title-cases. **Cleaning happens before the 40-character length test** — deliberately. A raw header like `# -- orks, trolls, dwarves (Shadowrun-style — come in every ancestry, skin unchanged)` is 80+ chars and would fail a raw length test, but cleans to `Orks, Trolls, Dwarves`. Lines starting `=` and all-punctuation rules are rejected as prose. Duplicate labels get a numeric suffix.

### Wildcard file format

One entry per line. Blank lines ignored. `#` lines are section headers (used only by `select: "section"` categories, ignored otherwise).

---

## Content inventory

~44 categories across 6 themes + 4 global packs. Almost everything with usable `#`
headers is now **section-select**; the exceptions are noted.

**Globals**

| Pack | Categories (selector) |
|---|---|
| common (Identity) | Ancestry (section, 16) · Metatype/Species (section, 32) |
| female (Physical, gender: Female) | Build (section, 6 — incl. Brian's LITHE) · Face · Nose · Lips (toggles, flat lists) |
| male (Physical, gender: Male) | Build (section, 7 — incl. Muscular) · Face · Nose · Lips (toggles) — authored 0.8.1 to mirror female (frame/chest/shoulders, not breasts). Claude-authored; review the prose. |
| hair (Hair) | Color (section: Natural/Vivid/Multi-Tone) · Type (Straight/Wavy/Curly/Coily) · Style (Short/Medium/Long/…) |
| shots (Camera) | Shot Angle (section, 20 — direct pick) · Shot Framing (section, 50 — direct pick) |

**Themes** (each with a Scene block: accent_palette / environments / poses, all section-select with cleaned labels)

| Theme (label) | Wardrobe categories |
|---|---|
| _ghost.runner | Tattoos (by body-placement) · Outfits (18 archetypes) · Weapons (Sidearms/Long Guns/…) |
| Whimsical Woods | Tattoos · Outfits (24 archetypes) · Weapons · **Spell Casting** · **Spell Effects** (by element) |
| Cassette Futurism | Outfits (14 archetypes) |
| Autumnal Oxidation | Outfits (12 goth substyles; granular pieces removed 0.7.12) |
| All the Dresses | "Gowns & Dresses" (**toggle** — 530 flat, no headers) · Eastern Attire (section, garments) |
| COZY SEXY LACY RACY Sleepwear | Lingerie Sets (section, 12 — adult) |

All content is Brian's original work, from his standalone wildcard releases (see Theme names). The TrashAI `totalChaosRandomizer` workflow was a **UX reference only** — none of its data is used. Content is also published on Civitai; which source is canonical is undecided.

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

## Features shipped in the 0.7.x–0.8.0 line (all uncommitted, on the live install for testing)

- **Collapsible section headers (0.8.5–0.8.6).** The header rows are clickable (litegraph calls `widget.mouse` on custom widgets). Clicking toggles `node.properties._bkCollapsed[group]` — persisted, so a saved workflow remembers collapsed sections — and draws a ▸/▾ arrow. `applyTheme` folds collapse into the scope pass: visible = in-scope AND section not collapsed; the output box never collapses. **Header visibility must be judged per header instance against ITS OWN members (widgets until the next header), not by group name** — Wardrobe/Scene headers repeat once per theme, and keying on the name showed every theme's header when any one was in scope (the 0.8.5 duplicate-headers bug, fixed 0.8.6 via `_bkInScope` markers).
- **Bald hair + Feminine/Masculine labels (0.8.4).** Hair Type gained a **Bald** section (all lines start with "bald"). `_drop_if_bald()` — run by both `resolve_prompt` and `_resolve_mayhem` over a `(order,label,text,key)` list — detects a bald `hair_type` pick and removes the `hair_color`/`hair_style` picks (a bald head has neither), whether bald was chosen or randomly drawn. This is the one **cross-category rule**; keep it in the shared helper. The female/male Physical categories are labelled **Feminine/Masculine** Build/Face/Nose/Lips so they're distinguishable when both show under Fluid/Random.
- **Gender emitted + Random / Fluid (0.8.2–0.8.3).** The gender dropdown options are `— off — · — random — · Female · Male · Fluid` — `GENDER_OFF`/`GENDER_RANDOM` reuse `library.SECTION_OFF`/`SECTION_ANY` so they read like the section dropdowns. **The gender is now injected into the prompt as a subject word** (`_GENDER_TEXT`: a woman / a man; Fluid → "an androgynous person"; Off → nothing), at `order 5` so it leads — previously gender was scope-only and never reached the text, so the render wasn't directed toward a gender at all. **Random** rolls a concrete gender per seed (own rng stream via `stable_offset("__gender_roll__")`, deterministic → preview matches; also rolled in mayhem). **Fluid** drops the gender gate in `_in_scope` so both genders' physical categories contribute. The JS reads the sentinels (`gender_off`/`gender_random`/`gender_fluid`) from the layout payload rather than hardcoding the em-dash strings, and shows both genders' categories under Random/Fluid.
- **Male Physical content (0.8.1).** `male` pack authored (build/face/nose/lips) mirroring female — Claude-authored, pending Brian's prose review.
- **Mayhem mode (0.8.0).** A `mayhem` toggle (Settings). When on, `resolve_prompt` calls `_resolve_mayhem(seed, …)` — ignores every category widget and the theme/gender gate and composes a **seeded cross-theme** image: rolls a gender, then picks one category per *slot* (`_MAYHEM_SLOT`) from a random source theme + a random line. Core slots always appear; extras roll in at `_MAYHEM_EXTRA_PROB` (0.5). Includes all themes + adult content. Still a pure function of `seed` (core slots use `or` short-circuit so they never consume an extra-roll) → preview matches render, PNG reproduces. `resolve_prompt` shares a `_format_picks` helper with the normal path; the normal path is byte-identical to before the refactor.

- **Content build-out.** 6 themes fleshed out to _ghost.runner depth (each with theme-true environments / poses / accent palettes); new global `hair` pack (color/type/style split — resolved the old `{a|b|c}` brace blocker mechanically); `shots` pack (angle/framing direct-select); face/nose/lips; Whimsical Woods spell casting + effects; the COZY SEXY LACY RACY Sleepwear theme.
- **Section-select conversion.** Most theme categories moved off boolean toggles to off/random/section dropdowns (0.7.8–0.7.11). Verbose internal section headers were cleaned to short labels (poses, palettes). Files with no headers stay toggles.
- **Labeled output** (`label_output` toggle, default on). When on, each selection is tagged (`build: …`, `hair: …`, `scene/background: …`) and same-`prompt_label` adjacent picks merge. `resolve_prompt(..., labeled=)` builds it; the populate endpoint honours it so the preview matches. When off, the old comma-joined string.
- **On-node sections + layout.** Category `group` field + a JS-drawn header row per section; contiguous `display` ordering; Camera pinned below Scene; a Settings section for the run controls; taller default height for the resolved box.
- **Connection state.** Node turns **green + "ready — press Run"** when the prompt output is wired, **red + "NOT ready…"** when not — via an `api.queuePrompt`-independent `onConnectionsChange` hook + `node.outputs[0].links` check. Cosmetic; recomputed on load so a saved colour can't go stale.
- **Build number surfaced.** Node title shows `BKWILDCARDS Selector <build>` and the box shows the build on a fresh node — so a stale title/box is the tell-tale of a cached JS load. Branding standardised to **BKWILDCARDS** (all caps, plural).

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

Done in 0.7.x: resolved-live-update (0.6.5), hair `{a|b|c}` split, `group`/grouped-panels, physical attributes (face/nose/lips), Dark Fantasy env/poses. Still open:

| Item | Notes |
|---|---|
| **Eye color** | No source file exists (colours live only inside `bk_characters.txt` prose). Owner to provide a file or approve a drafted starter list. Would slot into the Physical group. |
| **Cyberpunk outfit structure** | Uses monolithic 270. Available: 183, 530, and a granular decomposition (`_ghost.runner 1.a`). Owner's call whether to keep/expand/granularise. |
| **"Gowns & Dresses" flat list** | 530 lines, no headers → stays a toggle. To section-select it, headers would need adding (by silhouette/fabric). |
| **Character presets** | `bk_characters.txt` — 12 whole-subject presets. A different feature shape (not a per-attribute category). Build or ignore? |
| Art Style | Planned global tier; no file exists. |
| Vampire variants 1 and 3 | Near-identical merge residue (`visible subtle fangs` vs `visible fangs`). One is redundant. |
| License | ✅ Dual: MIT for code, CC BY-SA 4.0 for `wildcards/`. `pyproject.toml` points at `LICENSE`. |
| GitHub publish | ✅ Pushed to `bkidderz/BKWILDCARDS` at v0.8.6. **Private** — flip to public when ready. Remaining: add `REGISTRY_ACCESS_TOKEN` secret for the Registry workflow. |
| Canonical source | Node package vs Civitai collection. Undecided. |
| Phase 2 | Module listed as a resource on image outputs. Surface unidentified. Partially anticipated by the PNG stamping. |

## Planned hierarchy

```
gender → ancestry (optional) → metatype (optional)
→ physical attributes (hair ✓, eyes ✗, build ✓, face/nose/lips ✓) → outfits ✓ → environments ✓ → art style ✗
```

Built: gender, ancestry, metatype, build, face/nose/lips (**both genders** — male authored 0.8.1), hair, outfits, environments, poses, palettes, weapons, tattoos, shots. Unbuilt: **eyes** (no source), **art style**.
