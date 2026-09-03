# CLAUDE.md — BKWILDCARDS

Guidance for Claude Code working in this repository.

---

## What this is

A ComfyUI custom node that turns a bundled wildcard library into scoped dropdowns and toggles and emits a finished prompt string. No wildcard syntax for the user to learn, no `__token__` to type.

**Owner:** Brian (`bkidderz`) · **Repo:** `BKWILDCARDS` · **Current version:** `0.9.13` — shipped 2026-09-02, tag `v0.9.13` (0.9.13 = **Body Sliders**: the slider build lane — off/random/on/preset selector, five readout sliders, Gender-indexed register, preset snap, Mayhem coin, Physical → Physical - Body / Physical - Head regroup, bald scrubs hair from every pick; **forces a one-time node re-add**; see § Slider Build Control). Earlier: 0.9.12 = **Haunted Hallows** — 8th theme, Halloween costumes/environments/poses (`wildcards/halloween/`: 245 costumes incl. named-franchise costumes kept, `{a|b|c}` variants pre-expanded to individual lines; 26 environments; 30 poses) + **Compression / Zentai Suits** — a new `_ghost.runner` Wardrobe category (`cyberpunk/bodysuits.txt`, 144 full-coverage armored suits, 7 families, `order 45` between Outfits and Weapons, its own `suit:` label) + _ghost.runner **outfits reworded** (270 lines, every `bodysuit` swapped to a varied covering garment — undersuit/plugsuit/zentai/techsuit/leotard/…) + **gender word now explicitly adult** (`an adult woman` / `an adult man` / `an adult androgynous person`). Node is now **54 categories / 8 themes / 6 global packs / 5,277 entries**. Also a one-label library fix: `_VERBATIM_LABELS` gained `E.T.` and the verbatim check now runs before the trailing-punctuation strip so `E.T.` keeps its dot. 0.9.11 = **Bradhamel Style** + **Photorealism** art styles (→ 11 total); Art Style now **exempt from Mayhem** — mayhem honours the user's selection on its own seeded rng instead of rolling it, reversing the 0.9.8 core-slot change. 0.9.9–0.9.10 = **Cybernetics** — a new augment axis (17 species-neutral single + partial augments) in its own group between Physical and Hair, plus a **Cybernetics Color** axis whose pick is folded into the augment's finish word by a `resolve_prompt` cross-category rule; Android + Gynoid metatypes strengthened to 3 variants each; the augment-as-identity metatypes Cybernetic Augmented, Partial Cyborg and Cyber-Eyed removed. 0.9.8 = fix — Mayhem now includes the Art Style category, added to `_MAYHEM_SLOT` as a core slot; it had been skipped since the category shipped in 0.9.3; 0.9.7 = Anime + Anime Photo Realism art-style prompts rewritten from booru tags to natural-language KREA2 prose; 0.9.3 = **Art Style** global category — 2nd under the Theme header, leads the prompt; 0.9.4–0.9.6 = label polish: `BKSTYLE` kept verbatim, theme dropdown alphabetized, `Theme`/`Gender` selectors Title-Cased, `◆`/`·` label prefixes dropped. Earlier: 0.9.1/0.9.2 = _ghost.runner + Whimsical Woods environments 24/20→360, two-level subheader format). **PUBLIC on GitHub + live on Comfy Registry** (tag `v0.9.12`).
**Git:** committed on `main`, pushed to **https://github.com/bkidderz/BKWILDCARDS** — **public**. The Comfy Registry **auto-publishes** on every push to `main` that changes `pyproject.toml` (see `.github/workflows/publish.yml`). `gh` CLI is required for pushes/releases and must be installed + authed as `bkidderz` on each machine (current machine: v2.97.0, authed, scopes `repo`/`workflow`/`gist`/`read:org`). `SNIPPETS.md` is gitignored (local handoff note, not product).
**Install path (current machine, 2026-08-12):**
`C:\Users\Owner\Documents\ComfyUI\custom_nodes\bkwildcards` — a **Portable/manual ComfyUI** under `Documents` (the running copy, pulled from the repo; the dev loop copies changed files here). Paths differ per machine; see `instructions.md` in the workspace root.

The earlier machine ran **ComfyUI Desktop (Electron)** under `%LOCALAPPDATA%\Comfy-Desktop\…`. Either way the dev-loop caching note in §Critical gotchas applies — restart ComfyUI to reload both Python and the cached JS.

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
| `steampunk` | **Nettie Necket** | Steampunk |
| `halloween` | **Haunted Hallows** | Halloween |
| `lingerie` | **COZY SEXY LACY RACY Sleepwear** | Lingerie (adult) |

`steampunk` (Nettie Necket) is Victorian brass/clockwork — **distinct from `cassette_futurism`** (1970s–90s analog "used future"); the two share the retrofuturism umbrella but no content. Nettie Necket has no accent_palette (outfits/environments/poses only).

Globals (not themes): `common` (Identity: ancestry, metatype; **Art Style**, rendered in the Theme section and leading the prompt; **Cybernetics** + **Cybernetics Color**, own group between Physical and Hair), `female` (Physical: build, face, nose, lips — gender: Female), `hair` (color/type/style), `eyes` (Physical: eyes — Natural/Cybernetic/Magical/Heterochromia), `shots` (Camera: angle, framing).

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
├── .github/workflows/publish.yml   auto-publishes to the Comfy Registry on push to main touching pyproject.toml
├── bkwildcards/
│   ├── __init__.py             re-exports; wraps routes import in try/except
│   ├── library.py              pack/category scanning, section parsing, seeding, draw()
│   ├── nodes.py                node classes, scope gating, PNG metadata stamping
│   ├── sliders.py              EXPERIMENTAL Slider Build Control — tiers, silhouette rules, synthesis
│   └── routes.py               GET /bkwildcards/layout · POST /bkwildcards/populate (cosmetic)
├── web/bkwildcards.js          scope hiding, section headers, queue-preview, connection colour, node title
└── wildcards/
    ├── _body_sliders.json      EXPERIMENTAL slider phrase banks (root-level file: not a pack; owner's prose)
    ├── common/     ancestry · metatypes · artstyles · cybernetics · cybernetics_color   (global — Identity; Art Style→Theme; Cybernetics own group)
    ├── female/     builds · face · nose · lips             (global, gender: Female — Physical)
    ├── male/       builds · face · nose · lips             (global, gender: Male — Physical, authored 0.8.1)
    ├── hair/       color · type · style                    (global — Hair)
    ├── eyes/       eyes (Natural/Cybernetic/Magical/Heterochromia) (global — Physical, 0.8.8)
    ├── shots/      angle · framing                         (global — Camera)
    ├── cyberpunk/  tattoos outfits bodysuits weapons accent_palette environments poses
    ├── fantasy/    tattoos outfits weapons accent_palette environments poses spell_casting spell_effects
    ├── halloween/  outfits(costumes) environments poses          (theme — Haunted Hallows, 0.9.12)
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
`widgets_values` in a saved workflow is a positional array. Reordering the real widgets desyncs it silently and permanently. Ordering changes go in `INPUT_TYPES` in Python, where at least a version bump warns the user.

**Exception (v0.7.x+): the JS inserts non-interactive section-header rows into `node.widgets`. Two mechanisms are required to make that safe — both are load-bearing.**

1. `serialize: false` on each header.
2. **`withoutHeaders()`** wrapping `nodeType.prototype.serialize` and `.configure`, which splices the headers out for the duration of the call.

**Why #2 is mandatory (the v0.8.7 bug):** ComfyUI's two halves disagree about what a position means. `serialize` skips `serialize:false` widgets **but writes each value at its index in the FULL widgets array**, leaving `null` holes where headers sit. `configure` reads back **sequentially**, also skipping headers. A compact reader against a hole-punched writer shifts every value by the number of preceding headers — so every save, load and Ctrl+Z corrupted the node (gender received the theme's value, etc.). Shipped broken in 0.7.1–0.8.6; fixed in 0.8.7. **Never conclude `serialize:false` alone is sufficient — verify BOTH the read and write paths in the installed frontend bundle before trusting any widget-array injection.**

**3. Changing input order costs users a node re-add — the owner's call, not a hard rule.**
Adding or moving an input shifts every `widgets_values` index after it, so existing users must delete and re-add the node. Pre-1.0 this was broken several times deliberately. The node's order is 100% Brian's choice: default to appending at the END, but insert or move mid-list on his direct instruction (as with the Slider Build Control, 2026-09-01), and call the re-add out in the release notes of whatever build ships it.

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

**On-node section order:** Theme (theme, **art style**) → Identity (gender, ancestry, metatype) → Physical - Body (the Body Sliders mode selector, then the Build preset dropdowns directly under it — shown only in preset mode — then the five body sliders, hidden while the mode is off) → Physical - Head (eyes, face, nose, lips) → **Cybernetics** (augment + colour) → Hair (type, style, color) → Wardrobe (theme outfits/tattoos/weapons) → Scene (palette, environment, poses, spell) → Camera (shot angle, framing) → Settings (separator, seed, control-after-generate) → output box. **Art Style is a `common`-pack category pinned into the Theme section** (`group: "Theme"`) and emitted right after `theme` in `INPUT_TYPES`, *before* gender, so it renders 2nd under the Theme header (0.9.3). **Camera is a global but is pinned *after* the theme block** — `INPUT_TYPES` emits `POST_THEME_GROUPS = {"Camera"}` globals after all theme blocks. `theme`/`gender`/`separator`/`seed`/`label_output` get their section from `SPECIAL_GROUPS` in the JS. The JS `relabel()` prettifies fixed-widget labels via `FIXED_LABELS` (theme→`Theme`, gender→`Gender`) and no longer prefixes category labels with `◆`/`·` (0.9.4–0.9.6). Label rule: **selectors Title Case, Settings widgets lowercase, section headers UPPERCASE.**

**Prompt order (`order`):** art style 1 (leads, ahead of the gender word at 5) → ancestry 10 → **cybernetics 14** → build 15 → metatype 20 → face/nose/lips 22/24/26 → hair 27–29 → tattoos 30 → outfit 40 → weapons 50 → palette 60 → environment 70 → pose 80 → spell 82/85 → shots 90/92. **Cybernetics Color** carries no order of its own — a cross-category rule (`_apply_cyber_color`, like `_drop_if_bald`) swaps the chosen colour into the cybernetics augment's `chrome` finish word and drops the colour entry, so it never emits separately.

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
  "group": "Physical - Body",
  "prompt_label": "build"
}
```

- `select: "section"` turns the file's `#` headers into dropdown options instead of a boolean toggle (off / random / each section). Reserved options are `library.SECTION_OFF` (`— off —`) and `library.SECTION_ANY` (`— random —`), em-dash-wrapped so a section literally named "off" cannot collide. **A `section` category with no usable headers silently falls back to a toggle** — that is why a flat file (e.g. the dresses "Gowns & Dresses" list) stays on/off. Most theme categories were converted to `section` across 0.7.8–0.7.11.
- `group` — the on-node section header the category renders under (Identity / Physical - Body / Physical - Head / Hair / Wardrobe / Scene / Camera). Cosmetic; drives display grouping only.
- `prompt_label` — the tag emitted when the node's **Labeled output** toggle is on (`build: …`, `hair: …`). Categories that share a `prompt_label` **and** are adjacent in `order` merge under one label (the three hair categories → one `hair:` line).

**Removing a category = delete its `.txt` file, not just its `entries` row.** `library._load_pack` scans *every* `.txt` in the pack dir and loads undeclared files with a filename-derived label. (This is how the goth granular pieces were removed in 0.7.12 — files deleted, not just de-listed.)

### Section header parsing

`library.clean_section_name()` strips leading `#` and dashes, cuts at the first `(` or `[`, trims, and title-cases. **Cleaning happens before the 40-character length test** — deliberately. A raw header like `# -- orks, trolls, dwarves (Shadowrun-style — come in every ancestry, skin unchanged)` is 80+ chars and would fail a raw length test, but cleans to `Orks, Trolls, Dwarves`. Lines starting `=` and all-punctuation rules are rejected as prose. Duplicate labels get a numeric suffix. **Exception:** labels in `library._VERBATIM_LABELS` (e.g. `BKSTYLE`) skip title-casing so a creator's all-caps branding is preserved; because `clean_section_name` is the single source for both the dropdown option and the draw-match, the verbatim label stays consistent end-to-end (0.9.4).

### Wildcard file format

One entry per line. Blank lines ignored. `#` lines are section headers (used only by `select: "section"` categories, ignored otherwise).

---

## Content inventory

54 categories across 8 themes + 6 global packs. Almost everything with usable `#`
headers is now **section-select**; the exceptions are noted.

**Globals**

| Pack | Categories (selector) |
|---|---|
| common (Identity + Art Style + Cybernetics) | Ancestry (section, 16) · Metatype/Species (section, 29) · **Art Style** (section, 11; `group: Theme`, `order 1` → leads the prompt; exempt from Mayhem in 0.9.11; 0.9.3) · **Cybernetics** (section, 17 — species-neutral single + partial augments; own group between Physical and Hair, `order 14`; 0.9.9) · **Cybernetics Color** (section, 14 — off=chrome/random/colour; folded into the augment's finish word by `_apply_cyber_color`, never emits alone; 0.9.10) |
| female (Physical, gender: Female) | Build (section, 6 — incl. Brian's LITHE) · Face · Nose · Lips (toggles, flat lists) |
| male (Physical, gender: Male) | Build (section, 7 — incl. Muscular) · Face · Nose · Lips (toggles) — authored 0.8.1 to mirror female (frame/chest/shoulders, not breasts). Claude-authored; review the prose. |
| hair (Hair) | Color (section: Natural/Vivid/Multi-Tone) · Type (Straight/Wavy/Curly/Coily) · Style (Short/Medium/Long/…) |
| eyes (Physical) | Eyes (section, 29 — Natural/Cybernetic/Magical/Heterochromia). Global like hair: exotic eyes are drawable under any theme by design. `order 20/display 21` → sits after Build, before Face. Sourced from `bk_cyberpunk_eyes`+`bk_fantasy_eyes` (0.8.8). |
| shots (Camera) | Shot Angle (section, 20 — direct pick) · Shot Framing (section, 50 — direct pick) |

**Two-level environment format (0.9.1+):** an env file may nest `# -- Subheader` lines under cosmetic `# === INTERIORS/EXTERIORS ===` dividers. `read_sections` already treats the `# --` subheaders as the selectable sections and **ignores the `# ===` dividers** — no code change was needed. Requirement: subheader names must be **unique across the whole file** (section-select keys by name), so an interior and an exterior subheader must not share a name or their lines silently merge. `_ghost.runner` environments use this (20 sections → 22 dropdown options incl. off/random). Verify uniqueness + no INTERIORS/EXTERIORS leak whenever a two-level env file is added.

**Themes** (each with a Scene block: accent_palette / environments / poses, all section-select with cleaned labels)

| Theme (label) | Wardrobe categories |
|---|---|
| _ghost.runner | Tattoos (by body-placement) · Outfits (18 archetypes, 270) · **Compression / Zentai Suits (144, 7 families — full-coverage armored suits, `order 45`; 0.9.12)** · Weapons (Sidearms/Long Guns/…) · **Environments (360, 20 subheader sections — 0.9.1)** |
| Whimsical Woods | Tattoos · Outfits (24 archetypes) · Weapons · **Spell Casting** · **Spell Effects** (by element) · **Environments (360, 20 subheader sections — 0.9.2)** |
| Cassette Futurism | Outfits (14 archetypes) |
| Autumnal Oxidation | Outfits (12 goth substyles; granular pieces removed 0.7.12) |
| All the Dresses | "Gowns & Dresses" (**toggle** — 530 flat, no headers) · Eastern Attire (section, garments) |
| Nettie Necket | Outfits (23 archetypes — airship/aristocrat/occult/nautical/sultry). Scene: environments (Interiors/Exteriors) + poses (7 groups). **No accent_palette.** (0.9.0) |
| Haunted Hallows | **Costumes** (245, 36 costume sections — classic monsters, cute/glam, + named-franchise costumes; braces pre-expanded). Scene: environments (Interiors/Exteriors, 26) + poses (8 groups, 30). **No accent_palette/tattoos/weapons** (same shape as Nettie Necket). Costumes are a *costumed person, not the creature* — reads best with Metatype off (Metatype=Werewolf + a werewolf costume contradicts). (0.9.12) |
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
- **Bald hair + Feminine/Masculine labels (0.8.4).** Hair Type gained a **Bald** section (all lines start with "bald"). `_drop_if_bald()` — run by both `resolve_prompt` and `_resolve_mayhem` over a `(order,label,text,key)` list — detects a bald `hair_type` pick and removes the `hair_color`/`hair_style` picks (a bald head has neither), whether bald was chosen or randomly drawn. This is one of **two cross-category rules** (the other is `_apply_cyber_color`, 0.9.10, which folds the Cybernetics Color pick into the cybernetics augment); keep both in the shared post-process helpers. The female/male Physical categories are labelled **Feminine/Masculine** Build/Face/Nose/Lips so they're distinguishable when both show under Fluid/Random. **Extended 2026-09-01:** it also runs `_scrub_hair()` over every other pick's text, dropping comma-separated clauses (or the `and`-joined half of one) that mention hair — art styles ("layered anime hair", "realistic hair with individual strands"), ancestry ("long wavy hair"), outfits and poses all describe hair in passing, and the renderer grew hair on a bald subject from those clauses alone. This is the one **cross-category rule**; keep it in the shared helper. The female/male Physical categories are labelled **Feminine/Masculine** Build/Face/Nose/Lips so they're distinguishable when both show under Fluid/Random.
- **Gender emitted + Random / Fluid (0.8.2–0.8.3).** The gender dropdown options are `— off — · — random — · Female · Male · Fluid` — `GENDER_OFF`/`GENDER_RANDOM` reuse `library.SECTION_OFF`/`SECTION_ANY` so they read like the section dropdowns. **The gender is now injected into the prompt as a subject word** (`_GENDER_TEXT`: a woman / a man; Fluid → "an androgynous person"; Off → nothing), at `order 5` so it leads — previously gender was scope-only and never reached the text, so the render wasn't directed toward a gender at all. **Random** rolls a concrete gender per seed (own rng stream via `stable_offset("__gender_roll__")`, deterministic → preview matches; also rolled in mayhem). **Fluid** drops the gender gate in `_in_scope` so both genders' physical categories contribute. The JS reads the sentinels (`gender_off`/`gender_random`/`gender_fluid`) from the layout payload rather than hardcoding the em-dash strings, and shows both genders' categories under Random/Fluid.
- **Male Physical content (0.8.1).** `male` pack authored (build/face/nose/lips) mirroring female — Claude-authored, pending Brian's prose review.
- **Mayhem mode (0.8.0).** A `mayhem` toggle (Settings). When on, `resolve_prompt` calls `_resolve_mayhem(seed, …)` — ignores every category widget and the theme/gender gate, **except Art Style, which mayhem honours from the user's selection** (its own seeded rng stream, so changing the style on a fixed seed leaves the rest identical; 0.9.11) — and composes a **seeded cross-theme** image: rolls a gender, then picks one category per *slot* (`_MAYHEM_SLOT`) from a random source theme + a random line. Core slots always appear; extras roll in at `_MAYHEM_EXTRA_PROB` (0.5). Includes all themes + adult content. Still a pure function of `seed` (core slots use `or` short-circuit so they never consume an extra-roll) → preview matches render, PNG reproduces. `resolve_prompt` shares a `_format_picks` helper with the normal path; the normal path is byte-identical to before the refactor.

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

Done in 0.7.x–0.9.x: resolved-live-update (0.6.5), hair `{a|b|c}` split, `group`/grouped-panels, physical attributes (face/nose/lips), Dark Fantasy env/poses, **eyes (0.8.8)**, **Nettie Necket steampunk theme (0.9.0)**, **environment expansions to 360 (0.9.1–0.9.2)**, **public + live on the Comfy Registry**, **Art Style global category (0.9.3, + label polish 0.9.4–0.9.6)**, and **Cybernetics augment axis + Cybernetics Color (0.9.9–0.9.10; metatypes restructured — Android/Gynoid strengthened, 3 augment-metatypes relocated to Cybernetics)**, and **Haunted Hallows theme + Compression/Zentai Suits category + adult gender wording (0.9.12)**. Still open:

| Item | Notes |
|---|---|
| **Cyberpunk outfit structure** | Outfits still monolithic 270 (available: 183, 530, granular `_ghost.runner 1.a`). Owner's call whether to keep/expand/granularise. **0.9.12** added a *separate* Compression/Zentai Suits category (144) as a coverage alternative and reworded the 270's `bodysuit` garments — the 270-vs-530 structure question itself is still open. |
| **"Gowns & Dresses" flat list** | 530 lines, no headers → stays a toggle. To section-select it, headers would need adding (by silhouette/fabric). |
| Art Style | ✅ **Built (0.9.3).** Global `common/artstyles.txt`, section-select, 2nd under the Theme header, leads the prompt (`order 1`). 9 styles incl. creator styles **BKSTYLE** / **GLADAS STYLE**. |
| Vampire variants 1 and 3 | Near-identical merge residue (`visible subtle fangs` vs `visible fangs`). One is redundant. |
| License | ✅ Dual: MIT for code, CC BY-SA 4.0 for `wildcards/`. `pyproject.toml` points at `LICENSE`. |
| GitHub publish | ✅ **Public** on GitHub + **live on the Comfy Registry** (auto-publishes on version bump touching `pyproject.toml`; `REGISTRY_ACCESS_TOKEN` secret configured). **Git tagging initialized at `v0.9.6`** (first tag, 2026-08-12) — annotate + push a `vX.Y.Z` tag on each release going forward. |
| Canonical source | Node package vs Civitai collection. Undecided. |
| Phase 2 | Module listed as a resource on image outputs. Surface unidentified. Partially anticipated by the PNG stamping. |
| **Slider Build Control** | ✅ **Shipped in 0.9.13** (2026-09-02). Body sliders (mass/bust/waist/hips/muscle tone) synthesized to figure prose; off/random/on/preset modes; Mayhem coin. Phrase banks are the owner's to keep revising (`wildcards/_body_sliders.json`). See the section below + `CONTENT_PLAN.md` §2. |

## Slider Build Control (0.9.13)

**Built 2026-09-01, shipped 2026-09-02 in 0.9.13** (`bkwildcards/sliders.py`,
`wildcards/_body_sliders.json`, six inputs in `nodes.INPUT_TYPES`, JS group/label entries,
readouts and mirrors). The release notes MUST carry the one-time re-add callout. Full content-facing scope is in
`CONTENT_PLAN.md` §2 (Enhancements). Decisions locked with the owner 2026-09-01: gender
`— off —` → **suppressed**; prose sub-model → **per-axis-primary** (every non-middle axis
emits, silhouette label leads when a ratio rule fires — sliders must feel responsive;
`sliders.EMITTING_TIERS` is the one knob for sparser models); **every tier emits, 4–6
included** (no silent averages, 2026-09-01); inputs placed **mid-list
directly after the Build presets** (the re-add is accepted). Architecture:

- **What it is.** An optional manual body-shaping lane *parallel to* the existing Build
  category: five 0–10 sliders (**mass, bust, waist, hips, muscle tone**) + a **"Body
  Sliders" master toggle**, synthesized in Python into one figure-prose build phrase.
  Independent of the Build presets; the two never both emit — master toggle **ON
  suppresses the preset Build output** for that run.
- **Inputs (invariants #3, #4).** Six new inputs — a `body_sliders` mode dropdown (`— off —` /
  `— random —` / `on` / `preset`, reusing the section sentinels) + 5 `INT` (`min:0, max:10, step:1,
  display:"slider"`) named `body_mass`/`body_bust`/`body_waist`/`body_hips`/`body_tone` (so a
  pack dir named `body` is reserved). A `body_blend` slider existed for part of 2026-09-01
  and was removed the same day. Emitted by
  `INPUT_TYPES` **directly after the last `Physical - Body` category** (the Build presets),
  so they render under the presets with no JS reordering (invariant #2 intact). This shifts
  `widgets_values` → **one-time node re-add**; call it out in the release notes. Order on
  the node: the `body_sliders` mode, the Build presets under it, then the five body sliders
  (owner, 2026-09-01). The JS adds
  `SPECIAL_GROUPS`/`FIXED_LABELS` entries for the six names, **hides the sliders while the
  mode is off**, greys them under `— random —` (`options.disabled`), **shows the preset Build dropdowns only in `preset` mode** (`PRESET_WIDGETS` — hidden, not
  removed, otherwise; Python still honours a saved value), greys the sliders in `preset`
  mode and under Gender `— off —` (the selector too — and **Gender `— off —` writes the
  selector to `— off —`**, one-way, owner's call 2026-09-01: a live `preset` selection with no
  presets showing would confuse), and **snaps the sliders to the chosen
  preset section's vector** (`snapToPreset`, from `slider_ui.presets`; a random preset snaps
  after the preview), and after each queue-time preview **mirrors the rolled values** onto the
  sliders (`applySliderState`, from the populate response's `sliders` state), and draws a **live readout on each slider** (`installSliderReadouts`:
  "Mass: 0 | a gaunt, frail frame", left-aligned, truncated to the bar) from per-value phrase
  tables the layout endpoint ships (`sliders.ui_tables`) — cosmetic, no tier/blend logic in JS;
  the six sliders carry **no tooltip** (the hover pop-up got in the way — owner, 2026-09-01) (`applyTheme`, re-applied on the toggle's callback like
  theme/gender) — cosmetic, Python ignores them when off regardless.
- **Python authoritative (invariant #1).** `sliders.py` owns tiers (0–1 / 2–3 / 4–6 / 7–8 /
  9–10 — **every tier emits**, the middle included, since 2026-09-01: the owner wants
  intentional control, not averages left to the model), the silhouette rules (hourglass / pear / inverted / round /
  straight, thresholds are module constants) and `synthesize()`; `nodes._apply_body_sliders`
  runs after the category loop in `resolve_prompt` (so the populate endpoint shares it),
  drops every `id == "build"` pick and appends the slider build at the Build `order`/
  `prompt_label`. Fails soft: banks missing → presets untouched. A pure function of
  (register, five values) → **preview == execution** holds (400-trial headless check, incl.
  string-typed values from the JSON payload). The register's `neutral` phrase is only a
  fallback for a missing bank phrase.
- **Register = Gender** (the owner's "hard lock", 2026-09-01, after a blend-slider detour the
  same day): `nodes._SLIDER_REGISTER` — Female/Male → the gendered banks, Fluid and Off →
  androgynous, Random → the rolled gender. `— random —` mode rolls the five values per seed
  (`sliders.roll_values`, one stream per input name); **`preset` mode** lets the Build preset
  dropdowns emit (Option 3, 2026-09-01): `nodes._preset_pick` re-derives which preset line
  will emit (same rng as the category loop) and its section, `sliders.preset_vector` maps
  the section to a five-value vector (JSON `presets`, owner-editable, display only) that the
  sliders snap to and keep when the mode flips to `on` — a preset is a starting point, never
  a second build line; **Gender `— off —` silences the lane** (state None) as it does the
  gendered presets — landscapes have no body; `nodes.slider_state()` is the one pure
  function `resolve_prompt`, `build()` (stamps `properties.bk_sliders`) and the populate
  endpoint share, so the on-node sliders, the box, the render and the PNG all agree. Earlier
  same-day design, superseded: **the `body_blend` slider picked the register per axis
  under every gender** (`sliders.blend_registers`:
  0–1 masculine, 2–3 masculine frame + androgynous chest/hips, 4–6 androgynous, 7–8
  androgynous frame + feminine bust/hips, 9–10 feminine — chest and hips flip first because
  they read most gendered; the mixed bands are the gender-fluid bodies, 4–6 is androgyny.
  Replaced the first cut's "Fluid collapses to one androgynous body", which turned fluidity
  into a midpoint the model kept rendering feminine — owner, 2026-09-01); **Random →
  per-seed rolled gender** (existing `stable_offset("__gender_roll__")`, deterministic);
  **Off → the slider build still emits, and the blend supplies the subject word** from the
  JSON `subject` table (`sliders.blend_subject`, 5 blend bands: an adult man / … / an adult
  woman), so the sliders can stand in for the Gender selector; a set Gender keeps its own word
  (owner, 2026-09-01 — with Off and no subject word the masculine body text alone did not
  anchor the render). An earlier cut suppressed it under Off, which silently emptied the build
  line for the owner's Off-gender runs — dropped 2026-09-01.
- **Mayhem rolls the lane itself** (owner, option 2, 2026-09-01): it still ignores the
  selector and slider widgets, but `_mayhem_slider_lane` flips a seeded coin
  (`_MAYHEM_SLIDER_PROB`, 0.5) on its build slot — heads replaces the preset line with a
  slider body rolled in the rolled gender's register, tails keeps the preset and reports its
  section's vector. Own rng stream (`__mayhem_sliders__`), so every other Mayhem pick for a
  seed is unchanged. `nodes.mayhem_slider_state` feeds the populate mirror and the PNG stamp,
  so the sliders always show the body Mayhem rendered. No gender rolled → no body. Still no
  slider slot in `_MAYHEM_SLOT`.
- **Regroup.** `group` `Physical` → `Physical - Body` + `Physical - Head` (Eyes/Face/Nose/
  Lips move to Head). Cosmetic (JS header + `display`); collapse state re-keys on the new
  group names.
- **Content boundary (agreement #7).** Silhouette/tier **rules** are code; the phrase
  content is the owner's. The owner asked for a seed draft (2026-09-01) — the #7 "unless he
  asks" carve-out — so `wildcards/_body_sliders.json` holds a Claude-authored **93-phrase
  first pass** (3 registers × (5 axes × 5 tiers + 5 silhouette labels + 1 neutral fallback))
  that Brian revises and owns. Edit the JSON, restart ComfyUI (loaded once at import).
  Emission order: mass → tone → silhouette → bust → waist → hips (frame + musculature lead,
  2026-09-01). Phrases are noun-phrase fragments; code joins them corpus-style ("a slender frame with a
  toned, athletic, visibly muscular physique, an hourglass figure, large breasts, a narrow waist").

## Planned hierarchy

```
gender → ancestry (optional) → metatype (optional)
→ physical attributes (hair ✓, eyes ✓, build ✓, face/nose/lips ✓) → outfits ✓ → environments ✓ → art style ✓
```

Built: gender, ancestry, metatype, build, face/nose/lips (**both genders** — male authored 0.8.1), hair, **eyes** (0.8.8), outfits, environments, poses, palettes, weapons, tattoos, shots, **art style** (0.9.3). Unbuilt: — (the planned hierarchy is now feature-complete).
