# BKWILDCARDS — Content Expansion Plan

Working document for growing the bundled library. Survey source:
`comfyui-impact-pack/custom_wildcards/` (Brian's collected/authored wildcard files).

**Status: 2026-08-31 — build `0.9.12`, staged to the live install, public on
GitHub, live on the Comfy Registry, tag `v0.9.12` (pending push).** Node is **54 categories / 8 themes / 6
global packs** (from 13), plus **Mayhem mode**, **Eyes** (0.8.8), the **Nettie
Necket** steampunk theme (0.9.0) and the **Haunted Hallows** Halloween theme (0.9.12).
Repo: https://github.com/bkidderz/BKWILDCARDS —
**public**; the Comfy Registry auto-publishes on every version bump touching
`pyproject.toml`.

> This revision marks answered items **✅ DONE** and keeps only the genuinely
> open items in §2. Skim §2 for what still needs you.

### Theme names

Dropdown labels are the owner's standalone wildcard-release names; this doc uses
the shorthands for brevity. Pack dirs and category keys are unchanged.

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

---

## 1. Done & shipped (0.6.5 → 0.7.12)

- **Themes fleshed out to _ghost.runner depth** — every theme now has Environments,
  Poses, and Accent Palette, authored theme-true (not noun-swapped): Whimsical Woods
  (+ **Spell Casting** & **Spell Effects**), Cassette Futurism, Autumnal Oxidation,
  All the Dresses (dance-forward poses).
- **Hair** — new global `hair` pack (Color / Type / Style), section-select. Resolved
  the old `{color}` brace blocker via the mechanical split.
- **Physical attributes** — Face / Nose / Lips in `female`; Brian's **LITHE** build.
- **Shots** — new global `shots` pack: Angle (20) and Framing (50), direct-select.
- **Section-select everywhere** (0.7.8–0.7.11) — environments, poses, outfits, weapons,
  tattoos, palettes, spell effects converted from toggles to off/random/section
  dropdowns. Verbose internal headers cleaned to short labels; goth outfits regrouped
  by 12 substyles. Files with no headers stay toggles (the flat "Gowns & Dresses" list).
- **New theme: COZY SEXY LACY RACY Sleepwear** (0.7.12) — Lingerie Sets only (12
  sections), granular lingerie pieces intentionally excluded. Goth granular pieces
  removed the same run (Outfits only).
- **Labeled output** toggle — tags each selection (`build:`, `hair:`, `scene/background:`);
  same-label adjacent picks merge. Preview honours it.
- **UI: sections + layout** — `group` field, JS header rows, contiguous ordering
  (Ancestry no longer splits Hair), Camera pinned below Scene, a Settings section,
  taller resolved box.
- **Connection state** — green/"ready" when the output is wired, red/"NOT ready" when
  not. **Build number** in the node title + box; branding standardised to BKWILDCARDS.
- **Theme renames** — Cyberpunk→_ghost.runner, Dark Fantasy→Whimsical Woods,
  Gowns & Dresses→All the Dresses.

---

## 2. OUTSTANDING — decisions & actions still needed

**PRIORITY ORDER (per Brian, 2026-08-09):**

1. ~~**Eyes**~~ — ✅ **DONE (0.8.8).** Source files existed after all
   (`bk_cyberpunk_eyes.txt` + `bk_fantasy_eyes.txt`, found 2026-08-10 in the
   updated source pull). Built as a **global** pack `wildcards/eyes/` (one Eyes
   dropdown, section-select off/random/header, Physical group, order 20 →
   after Build/before Face), per Brian's decision to mirror hair. 29 lines, 4
   sections: Natural / Cybernetic / Magical / Heterochromia. Validated
   headlessly (discovery, sections, seeded draws, end-to-end resolve across
   themes incl. a theme with no eyes file). **Tested in-app, pushed to git
   (0.8.8), and live on the Comfy Registry.**
   - Spelling: source lines originally read "heterocromia" (missing h);
     **fixed to "heterochromia" in 0.8.9.**
2. ~~**README.md for GitHub**~~ — ✅ **DONE.** Rewritten from the stale v0.6.0
   version against verified state (then 43 categories / 3,779 entries / 6
   themes; **now 47 categories / 4,790 entries / 7 themes**, and the live README
   reflects those counts plus Eyes and the Comfy Registry install). Has Install (git + ZIP + `custom_nodes` paths + verify), How to Use
   with a GitHub `> [!IMPORTANT]` callout to **wire `prompt` into a prompt
   block**, node-at-a-glance, theme/content tables, features (labeled output,
   Mayhem, live preview, bald), adding-your-own-wildcards, scoping, limits.
   Re-verify the content tables whenever content changes.
3. ~~**pyproject.toml for the ComfyUI Registry**~~ — ✅ **DONE**, validated
   against the official spec (docs.comfy.org/registry/specifications). Now has:
   `license = { file = "LICENSE" }`, `requires-python = ">=3.9"`, classifiers,
   Repository/Documentation/Bug Tracker URLs, `PublisherId = "bkidderz"`,
   `DisplayName`, and `includes = ["wildcards", "web"]` so a registry package
   can never ship without the content or the UI script. TOML parses; node still
   loads. **License is DUAL** — MIT for code (`LICENSE`), CC BY-SA 4.0 for
   `wildcards/` (`LICENSE-CONTENT`), per Brian's prepared files + `SNIPPETS.md`.
   The `REGISTRY_ACCESS_TOKEN` secret is now configured and the Registry workflow
   (`.github/workflows/publish.yml`) auto-publishes on every version bump —
   **live on the Comfy Registry** (registry.comfy.org/nodes/bkwildcards).
4. ~~**GitHub publish**~~ — ✅ **DONE (2026-08-09).** v0.8.6 committed (`bdb2329`,
   57 files, +4,851) and pushed to **https://github.com/bkidderz/BKWILDCARDS**,
   now **PUBLIC** (repo has since advanced to v0.9.2). `SNIPPETS.md` gitignored.
   GitHub reports the license as "Other" (not "MIT") because our `LICENSE` opens
   with the dual-license preamble — arguably the right outcome, since a bare MIT
   badge would misstate the content licence. **Completed since:** ✅ repo flipped
   to public · ✅ `REGISTRY_ACCESS_TOKEN` secret added and the Registry workflow
   auto-publishes on every version bump · **live on the Comfy Registry**
   (registry.comfy.org/nodes/bkwildcards). **Git tagging initialized at `v0.9.6`**
   (first tag, 2026-08-12) — annotate + push a `vX.Y.Z` tag on each release from
   here on. (Full GitHub Releases with notes are still optional.)
   Original notes:
   **`gh` CLI is now installed (v2.97.0) and authenticated as `bkidderz`**
   (scopes: repo, workflow, gist, read:org) — so Claude CAN create the repo and
   push on Brian's explicit go-ahead. Remaining pre-publish chores:
   - Set the repo git identity to match `bkidderz` (currently the machine global
     is "The SundanceRP <thesundancerp@…>"); existing 13 commits are authored as
     `bk <b@x>` — decide whether to rewrite history before it goes public.
   - **Commit the 0.7.x/0.8.x line** (everything since `0.6.5` is uncommitted).
   - Decide public vs private, and whether the adult Lingerie theme needs a
     content note in the repo description.
   - ⚠️ **When creating the repo, leave GitHub's "Add a license" dropdown set to
     None.** Picking MIT there makes GitHub write its own `LICENSE`, which would
     conflict on first push or silently clobber the dual-license file. The two
     license files go in via our commit. (From Brian's `SNIPPETS.md`.)
   - `SNIPPETS.md` is a scratch/handoff note, not part of the product — decide
     whether to delete it or keep it out of the published repo.

**New source material pulled 2026-08-10:**
- ~~**Steam Punk theme**~~ — ✅ **DONE (0.9.0).** Built as the **Nettie Necket**
  theme (`wildcards/steampunk/`, label "Nettie Necket" — its standalone release
  name). Outfits (235, 23 archetypes) · Environments (41, Interiors/Exteriors) ·
  Poses (30, 7 groups); no accent_palette. Confirmed **net-new** vs Cassette
  Futurism (Victorian brass vs 1970s analog — disjoint content). Validated:
  theme registers, 32 sections clean (no prose leak), seeded draws, end-to-end
  resolve, scope gating, UTF-8 (moiré/piqué intact). Shipped + pushed.
- ~~**Halloween theme**~~ — ✅ **DONE (0.9.12), built as the Haunted Hallows theme**
  (`wildcards/halloween/`, label "Haunted Hallows"). Costumes (245, 36 costume
  sections — classic monsters, cute/glam, + named-franchise) · environments (26,
  Interiors/Exteriors) · poses (30, 8 groups); no accent_palette/tattoos/weapons.
  The 18 source `{a|b|c}` outfit lines were **pre-expanded to individual lines**
  (192 → 245) since the node can't parse braces — every colour/option variant
  preserved. **IP decision (owner, 2026-08-31): franchise costumes KEPT**
  (Darth Vader, Pikachu, E.T., Wonder Woman, TMNT, Harry Potter, Ghostface…) — the
  owner accepts the exposure knowingly for a public/Registry release. Label fixes:
  `Frankenstein's Monster` (mixed-case header) and `E.T.` (via `_VERBATIM_LABELS`
  + a verbatim-before-rstrip tweak so the dot survives). Validated: theme
  registers, 36/2/8 sections clean, in-section draws, preview == execution,
  Mayhem pulls Halloween content. **⚠️ Known interaction:** costumes are written
  as "a costumed person, not the creature," so pairing with **Metatype =
  Werewolf/Vampire/etc.** contradicts ("a vampire … in a vampire costume").
  Metatype is off by default; the theme reads best with Metatype off.
- **`krea2-bk_hair.txt` (Aug 5)** — newer hair authoring, but every line leads
  with an inline `{color|…}` brace array. **Unusable as-is** — the node emits
  braces literally. Bundled hair is already the mechanically-split version, so
  this is a no-op unless Brian wants it split the same way.

**Environment expansions (two-level subheader format, 0.9.1):**
- ~~**_ghost.runner (cyberpunk) environments**~~ — ✅ **DONE (0.9.1).** Expanded
  24 → **360** (180 interiors + 180 exteriors, 20 subheader sections). File uses
  `# -- Subheader` under cosmetic `# === INTERIORS/EXTERIORS ===`; loader already
  treats subheaders as the selectable sections (no code change). Verified: 20
  unique sections, no dupes, no divider leak, both int/ext draw.
- ~~**Whimsical Woods (fantasy) environments**~~ — ✅ **DONE (0.9.2).** Expanded
  20 → **360** (180 interiors + 180 exteriors, 20 subheader sections). The first
  export was interiors-only; Brian force-refreshed the OneDrive file and the
  complete 419-line / 64 KB version arrived. Verified: 20 unique sections, no
  dupes, no leak, UTF-8 clean, both int/ext draw. Exterior subheaders: Castles &
  Ruins, Ancient Forests, Villages & Markets, Graveyards & Barrows, Mountains &
  Passes, Battlefields & War Camps, Swamps & Moors, Coast & Harbor, Ruined
  Temples & Monoliths, Wastes & Blighted Lands.

**Known content conflicts (to resolve):**
- **Ancestry hair vs. Bald / Hair Type — double-ownership of hair texture**
  *(parked 2026-08-11).* Nearly all 44 ancestry lines carry a hair TEXTURE/length
  phrase ("straight hair", "long straight hair"). The `hair` pack's **Hair Type**
  dropdown *also* owns texture (Straight/Wavy/Curly/Coily) **and Bald**. So two
  sources describe hair at once. Worst case: Ancestry=random lands hair guidance
  + Hair Type=random lands **Bald** → images with a bald scalp but hair on the
  back/half the head. Subtler clashes happen non-bald too (ancestry "straight"
  vs type "coily"). Note: the ancestry header comment claims "they never
  conflict" (it assumed the hair pack owned only COLOR) — that comment is wrong
  and must be updated with whatever fix we choose. Metatype/species is clean
  (0 hair mentions), so ancestry is the only other hair source. `_drop_if_bald`
  can't help here — it drops the hair_color/style *picks*, but ancestry hair is
  embedded in prose and can't be surgically removed at runtime.
  Options (Brian raised 1 & 2):
  1. **Mutual toggle** — ancestry and hair disable each other by selection.
     *Not recommended:* overbroad (ancestry also owns skin/eyes/face/nose/lips,
     all lost if toggled off), kills independent hair control, and needs fragile
     dynamic cross-widget UI logic.
  2. **Strip hair from ancestry prose (recommended)** — make the hair pack the
     SOLE owner of all hair. Remove texture/length phrases from the 44 ancestry
     lines; ancestry keeps skin tone, eye shape, face structure, nose, lips.
     Content-only, deterministic, no code; fixes bald AND all texture clashes.
     Tradeoff: ancestry-only (hair all off) leaves hair unspecified → model
     free-picks (acceptable; turn hair on for control). Ethnic hair textures are
     largely already covered by Hair Type; optionally enrich the hair pack if any
     are missed.
  3. **Strengthen Bald lines** ("completely bald, hairless, smooth scalp") to
     out-weight ancestry hair tokens. *Weak:* prompt-engineering mitigation only,
     unreliable, ignores non-bald texture clashes. At best a stopgap.
  4. **Hair-free ancestry variants** selected when Bald is active (metatype
     multi-variant pattern). *Overkill* vs. option 2; doubles ancestry authoring
     and adds resolver complexity.
  Recommendation: **option 2** — it's the single-owner fix the design already
  implies (Hair Type owns texture), and it resolves the general conflict, not
  just the bald symptom.

**Content decisions (blocking new content):**
- **Cyberpunk outfits / structure** — current pack uses monolithic **270**.
  Available: 183, 530, and a full granular decomposition (`_ghost.runner 1.a`:
  tops/bottoms/footwear/headgear/outerwear/accessories). Keep 270, bump to 530,
  or adopt the granular model (as done for goth)? This is your primary theme.
  **0.9.12 progress (structure question still open):** (a) added a *separate*
  **Compression / Zentai Suits** category (`cyberpunk/bodysuits.txt`, 144
  full-coverage armored suits, 7 families, `order 45`, own `suit:` label) as a
  coverage alternative to Outfits — pick one or the other; (b) reworded the 270 —
  every `bodysuit` garment swapped to a varied covering garment
  (undersuit/plugsuit/zentai/techsuit/leotard/skinsuit/jumpsuit) since the plain
  "bodysuit" rendered under-covered. 8 `catsuit`/`undersuit` lines remain as an
  optional later pass (worksheet: `ghost-runner_bodysuit_rewrites.md`, workspace root).
- ~~**Character presets**~~ — **Dropped (owner, 0.9.7):** some are Brian's own
  personal characters and are not for public release. Prompt them manually or use
  existing wildcard options instead.
- **Extra global candidate** — `bk_gaze.txt` (23 gaze/expression lines) is a
  plausible always-on category. Include it? (`bk_heritage.txt` **dropped** — too
  similar to Ancestry, which is already built.)
- **Unused pose sources** — `bk_poses_action` (25) and `bk_poses_suggestive`
  (62) aren't wired anywhere yet. Want them in fantasy/global poses?
- **"Gowns & Dresses" flat list** — 530 lines, no headers, so it stays a toggle.
  To make it a section dropdown I'd add headers (by silhouette/fabric). Do it?

**Confirmations (currently shipped one way; change if you disagree):**

- **Shot Framing near-duplicates** — I removed only exact dupes; terms like
  "Close-Up" vs "Close Up Portrait Shot" remain as distinct options. Prune?

**Enhancements (scoped, deferred — awaiting Brian):**

- **Slider Build Control** — ✅ **SHIPPED IN 0.9.13** (built 2026-09-01, shipped
  2026-09-02; the owner evaluated it and kept it). Seed phrase banks (93, Claude-drafted at
  the owner's request) are in `wildcards/_body_sliders.json`; Brian keeps revising them —
  content-only edits need no re-add. **The 0.9.13 release notes carry the one-time node
  re-add callout.**
  An optional manual body-shaping lane: five 0–10 sliders (**mass, bust, waist, hips,
  muscle tone**) synthesized into coherent figure prose, **independent** of the existing
  Build presets. Architecture notes live in `CLAUDE.md` (§ Experimental — Slider Build
  Control).
  - **Two independent lanes, no coupling.** Existing Build category stays exactly as-is
    (presets are category-level only, so tying them to slider vectors was judged wasted
    effort). A **"Body Sliders" master toggle** (default off): ON → the slider-synthesized
    build emits and the preset Build output is **suppressed** that run; OFF → sliders inert,
    Build unchanged. One body description, never two.
  - **Node regroup:** `Physical` → **Physical - Body** (the Body Sliders off/random/on/preset
    selector, the Build preset dropdowns directly under it — shown in preset mode — then the
    five body sliders, hidden while off) and new **Physical - Head** (Eyes, Face, Nose,
    Lips). Cosmetic (`group`/`display`); rides the same re-add the sliders force.
  - **Register = Gender** (owner, 2026-09-01, final): Female/Male → gendered banks, Fluid
    and — off — → androgynous, — random — → the rolled gender. The Body Sliders selector is
    **off / random / on / preset**; random rolls the five values per seed and the node's
    sliders show the roll after each queue; **preset** (Option 3, 2026-09-01) shows the Build
    preset dropdowns again and lets them emit while the sliders snap to the section's vector
    (JSON `presets`, 13 owner-editable entries, display only) and keep it when flipped to
    on — one build line, never two. Gender — off — silences the lane (no subject, no body).
    The preset dropdowns are **hidden, not removed**, in the other modes. **Mayhem** flips a
    seeded 50/50 coin on its build slot between a preset line and a rolled slider body
    (option 2, 2026-09-01); the sliders mirror whichever rendered. *Superseded same-day design, kept for the record:* a sixth slider,
    `body_blend` (masculine 0 .. feminine 10), picked the register per axis under every gender: the ends
    are the gendered banks, 4–6 is the androgynous bank, and 2–3 / 7–8 mix a frame register
    (mass, tone, waist) with the other register's chest and hips — chest and hips flip first
    because they read most gendered. The mixed bands are the gender-fluid bodies; 4–6 is
    androgyny (owner, 2026-09-01, replacing the first cut's single androgynous body, which
    made fluidity a midpoint the model rendered feminine). The androgynous bust/hips bank
    was rewritten the same day to describe chest breadth and squared hips on a straight
    torso, never fullness; **— random —**
    → the per-seed rolled gender picks the register (deterministic); **— off —** →
    the slider build **still emits and the blend supplies the subject word** (JSON `subject`
    table, 5 bands — the sliders can replace the Gender selector; a set Gender keeps its own
    word; the Gender-scoped head categories still key on Gender — the earlier "suppress under Off" rule emptied the build line in practice and was
    dropped 2026-09-01).
  - **Prose model:** owner-authored per-axis phrase banks × 3 registers; each slider maps
    to 5 tiers and **every tier emits, the middle (4–6) included** — the owner wants
    intentional control, not averages left to the model (2026-09-01; the first cut had a
    silent middle tier).
    Synthesis (code) derives a leading **silhouette** from hip/waist/bust ratios, a
    **muscle-tone** modifier, and **overall scale** from mass. *Sub-model (locked 2026-09-01):*
    **per-axis-primary** — every axis emits its own phrase, and the silhouette
    label leads whenever a ratio rule fires. Chosen because sliders must feel responsive:
    under synthesis-primary a slider could move without changing the text. Fragments are
    chained corpus-style ("a slender frame with an hourglass figure, …") so it reads as a
    figure, not a spec sheet. Synthesis-primary remains one constant away
    (`sliders.EMITTING_TIERS`). Boundary (agreement #7): the silhouette/tier **rules**
    are code, and the **final** wording is the owner's — but the **owner has asked for a
    seed draft to edit** (2026-09-01), so producing a first-pass of the phrase banks (3
    registers) IS authorized as an editable starting point (the #7 "unless he asks"
    carve-out); the owner then revises and owns it.
  - **Authoring scope (the number):** 5 axes × 5 tiers × 3 registers = 75 tier phrases,
    + 5 silhouette labels × 3 + 3 fallbacks → **93 short phrases** first cut (was ~80–90 with
    a silent middle tier), owner-authored.
  - **Forces a one-time node re-add** (the six inputs are inserted mid-list, directly after
    the Build presets, shifting `widgets_values`) — accepted by the owner as the cost of
    innovation; **requires a clear re-add callout in the release notes** for whatever build
    it lands on, *if* it ships at all.
  - ~~**Open micro-items**~~ — resolved 2026-09-01: (1) `— off —` → suppress;
    (2) per-axis-primary; (3) placement → mid-list under the Build presets.

- **Cross-theme via a Theme option** (design agreed; not built). Add an "any"
  sentinel option to the Theme dropdown that **drops the theme gate** — every
  theme's categories become in-scope at once, so a user can manually mix a
  cyberpunk outfit with a fantasy environment, all seed-random where set to
  `— random —`. This is the clean decomposition of "locking": randomize is
  already per-option, cross-theme is the only missing primitive, and **Mayhem
  stays as-is (no lock system needed)**. Mirrors gender **Fluid** exactly.
  - Python: `_in_scope` drops the pack check when theme == the sentinel (like
    Fluid drops the gender check). Frontend: `applyTheme` already shows all when
    the theme isn't a real one — make that intentional.
  - Open details: (a) name it `— any —`/`— cross-theme —`, NOT `— random —`
    (it's "all available for manual mixing", not "roll one theme"); a separate
    "roll one theme per seed" could be added later. (b) The node ~triples in
    height in this mode (all themes' Wardrobe/Scene shown). (c) Nothing stops two
    same-slot picks (two outfits) — intended, "manually managed" like Fluid.

- **Update-without-re-add (widget-value survival across updates)** — *deferred,
  not started (discussed 2026-08-11).* Today a structural update (new
  category/theme, changed section options) can force users to delete & re-add
  the node. Root cause is two mechanisms:
  1. **Positional `widgets_values`.** `INPUT_TYPES` sorts categories by `display`
     ([nodes.py:263](bkwildcards/nodes.py:263)), so inserting a category
     mid-list (e.g. Eyes at display 21) shifts every later widget → old saved
     values misalign.
  2. **Combo option changes.** A section-select's saved value (e.g.
     `environment = "Interiors"`) becomes invalid when the file's sections
     change → ComfyUI throws "invalid input".
  Planned fixes, ship as **separate** versions with in-app round-trip testing:
  - **C — tolerant combo restore (small, do first):** on load, coerce a
    saved dropdown value that's no longer a valid option to its default instead
    of erroring. Turns a hard error into a silent per-widget reset.
  - **B — name-keyed value persistence (moderate, the real fix):** store values
    keyed by widget `key` and restore by name in the existing `configure` hook,
    so adding/reordering categories no longer misaligns. **Forward-fixing only**
    (pre-B saves lack the map). Must ship *with* C. Negatives logged 2026-08-11:
    deepens dependency on the fragile serialize/configure path (0.8.7 territory),
    **silent** failure mode if wrong, two-sources-of-truth drift risk, permanent
    dual-path complexity, and it can't be validated headlessly (JS-only path).
  - Cheaper alternative considered: **C only + let the library stabilize** —
    content-only updates already don't require re-adds; most churn was our own
    structural changes. Re-add should be a *troubleshooting* step, not routine.

- ~~**Art Style option (rests with Theme)**~~ — ✅ **BUILT (0.9.3, polished
  0.9.4–0.9.6).** A global section-select category `common/artstyles.txt`
  (`id: art_style`), `group: "Theme"` so it sits **2nd, directly under the Theme
  selector**, and `order: 1` so its text **leads the prompt** ahead of the gender
  word. Off/random like every other section dropdown. The open questions
  resolved: it's a **category in the `common` global pack** (not a separate
  selector or `wildcards/style/`), off/random/section like the others, and
  **Mayhem ignores it** (mayhem composes its own image). 9 styles: **BKSTYLE** and
  **GLADAS STYLE** (creator styles, kept verbatim via `_VERBATIM_LABELS`), Anime,
  Anime Photo Realism, Painterly, Pixel Art 16-Bit, Surreal, Semi-Realism, Western
  Comics. Source: `bk_art_styles.txt` + Brian's KREA2 prose. ⚠️ Inserting it as
  widget #2 **shifts `widgets_values`**, so workflows saved before 0.9.3 need the
  node re-added.

**Housekeeping:**

- ~~**Commit the 0.7.x/0.8.x milestone to git**~~ — ✅ done; every shipped version
  through 0.9.2 is committed and pushed to `main` (working tree clean).

---

## 3. Scope map — every source, and its disposition (updated)

| Source dir / file | Content | Disposition |
|---|---|---|
| `cassetteFuturism_v1A` | outfits, environments, poses, hair | ✅ Built (hair → global split) |
| `autumnalOxidation_v1B` | 6 goth files | ✅ Built |
| `allTheDressesDresses…` / `…Eastern…` | dresses / eastern 530 | ✅ Built |
| `bk_female_face/lips/nose` | flat lists | ✅ Built into `female` |
| `krea2-bk_hair.txt` | 45 lines, `{color}` braces | ✅ Built — split into Color/Type/Style |
| `bk_shots_angle/framing.txt` | 20 / 52 camera lines | ✅ Built → global `shots` |
| `bk_art_styles.txt` + KREA2 prose | art-style directives | ✅ Built (0.9.3) → global `common/art_style`, 2nd under Theme, leads prompt |
| `bk_poses_dancing` | 20 dance lines | ✅ Reference for Dresses poses |
| `bk_poses_casting` / `bk_poses_spell_effects` | 15 / 15 | ✅ → Dark Fantasy Spell Casting / Effects |
| `whimsicalWoods_v1B` | fantasy set | ✅ Env/Poses now authored (were missing) |
| `bk_gaze.txt` | 23 gaze lines | ⏳ Candidate global — §2 |
| `bk_heritage.txt` | 24 (8 sections) | ✋ Dropped — overlaps Ancestry (built) |
| `bk_poses_action` / `bk_poses_suggestive` | 25 / 62 | ⏳ Unwired — §2 |
| `bk_characters.txt` | 12 character presets | ✋ Dropped — owner's personal characters, not for public release |
| `_ghost.runner 1.a` | cyberpunk granular (13 files) | ⏳ Cyberpunk restructure — §2 |
| `bk_cyberpunk_outfits_183/530` | outfit supersets | ⏳ Cyberpunk decision — §2 |
| `krea2-bk_female_builds(_small)` | build variants | ✅ Resolved (61 + LITHE) |
| `GhostRunner_v1B` | cyberpunk set | Already the node's `cyberpunk` source |
| `cozySEXYLACYRACY_v1B/bk_lingerie_sets.txt` | 530 lingerie sets | ✅ Built → Lingerie theme (sets only) |
| `Steam Punk` / `halloween` | theme dirs | ✅ Built — Nettie Necket (0.9.0) / Haunted Hallows (0.9.12) |
| `krea2-bk_cyberpunk_bodysuits.txt` | 152 armored suits (`{a|b|c}` colour rows) | ✅ Built (0.9.12) → `cyberpunk/bodysuits.txt` (Compression/Zentai Suits, 144; transparent dropped, braces expanded) |
| `*.zip` | archives | Ignore (extracted copies present) |

---

## 4. Future themes (planned, not built — awaiting your go)

Both `Steam Punk` (→ Nettie Necket, 0.9.0) and `halloween` (→ Haunted Hallows,
0.9.12) are now built. `nettie_necket` (zip) remains unopened — likely redundant
with the built Nettie Necket theme. The `cozySEXYLACYRACY` **sets** are now built (the
Lingerie theme); its 7 other granular lingerie files (tops/bottoms/hosiery/…) are
intentionally left out — available if you ever want them.

---

## 5. Redundancy — status

| Redundancy | Status |
|---|---|
| `ancestry` duplicated across theme dirs | ✅ merged to `common/ancestry` |
| cyberpunk + fantasy metatypes | ✅ merged to `common/metatypes` (both variants kept) |
| hair identical (root == cassette) | ✅ resolved — one global hair pack, split |
| Female builds ×3 (61/61/39) | ✅ resolved — 61 canonical + LITHE |
| Cyberpunk outfits 183/270/530 + granular | ⏳ open — see §2 (cyberpunk structure) |

---

## Changelog (0.7.x — all uncommitted on `0.6.5`)

- **0.7.0** content build-out: hair pack, all-theme env/poses/palettes, spell casting/effects, shots, face/nose/lips
- **0.7.1** `group`/section-header UI, contiguous ordering, taller resolved box
- **0.7.2** section order reflow: Theme→Identity→Physical→Hair→Wardrobe→Scene→Camera→Settings
- **0.7.3** labeled output (`label_output` toggle, `prompt_label`)
- **0.7.4** build number in node title; BKWILDCARDS branding
- **0.7.5** connection state (green ready / red not-wired)
- **0.7.6** rename Cyberpunk→_ghost.runner, Dark Fantasy→Whimsical Woods
- **0.7.7** rename Gowns & Dresses→All the Dresses; doc glossary
- **0.7.8** section-select: environments, poses, outfits (3 themes), eastern
- **0.7.9** section-select: goth outfit (12 substyles), spell effects, all palettes
- **0.7.10** section-select: weapons · **0.7.11** section-select: tattoos
- **0.7.12** goth granular removed; COZY SEXY LACY RACY Sleepwear theme (sets)
- **0.8.0** **Mayhem mode** — one-click seeded cross-theme random image (coherent chaos, one-per-slot, all themes incl. adult, random gender; deterministic/reproducible)
- **0.8.1** **Male Physical content** — authored `male` build/face/nose/lips mirroring the female pack (frame/chest/shoulders; Build has 7 sections incl. Muscular). Claude-authored — pending Brian's prose review.
- **0.8.2** **Gender Random / Fluid** — Random rolls a gender per seed (deterministic); Fluid makes both genders' physical options available and mixable.
- **0.8.3** **Gender reaches the prompt** — emit a subject word (a woman / a man / androgynous), leading. Options reformatted to `— off — / — random — / Female / Male / Fluid`.
- **0.8.4** **Bald hair type** (suppresses hair color + style) + **Feminine/Masculine** Physical labels (readable under Fluid/Random).
- **0.8.5** **Collapsible section headers** — click a header (▸/▾) to collapse/expand its section; persisted per saved workflow.
- **0.8.6** fix: duplicate Wardrobe/Scene headers from inactive themes (per-header member check, not group name). **Confirmed working by Brian** — collapse/expand clean, no bleed-through.

Earlier (committed 0.6.5): resolved-text live-update fix + `setResolved` cleanup (validated).
- **0.8.7** **CRITICAL FIX** — section headers corrupted `widgets_values` on every save/load/undo (serialize wrote at full-array index leaving null holes; configure read sequentially). Headers now spliced out during serialize/configure. Workflows saved with 0.7.1–0.8.6 may have shifted widget values — re-set them.
- **0.8.8** **Eyes** global category · **0.8.9** heterochromia spelling fix · **0.9.0** **Nettie Necket** steampunk theme · **0.9.1 / 0.9.2** _ghost.runner + Whimsical Woods environments expanded to 360 (two-level `# --` subheader format)
- **0.9.3** **Art Style** — new global section-select category (`common/artstyles.txt`), pinned **2nd under the Theme header** (`group: Theme`) and **leading the prompt** (`order 1`, ahead of the gender word). Off/random + 9 styles incl. creator styles **BKSTYLE** / **GLADAS STYLE**. Emitted right after `theme` in `INPUT_TYPES` via an extracted `emit()` closure. ⚠️ Shifts `widgets_values` → re-add nodes in pre-0.9.3 saved workflows.
- **0.9.4** label polish — `BKSTYLE` kept verbatim (`library._VERBATIM_LABELS`, no regression to the other 242 all-caps labels), `ANIME Photorealism` → `Anime Photo Realism`, **theme dropdown alphabetized** (`_THEMES` sorted), `Theme` selector Title-Cased (JS `FIXED_LABELS`)
- **0.9.5** dropped the `◆`/`·` category-label prefixes (JS `relabel()`)
- **0.9.6** `Gender` selector Title-Cased. Standing label rule: **selectors Title Case, Settings widgets lowercase, section headers UPPERCASE.**
- **0.9.7** **Anime** + **Anime Photo Realism** art-style prompts rewritten from Danbooru-tag strings to natural-language KREA2 prose (matching the other Art Style entries; the tag-based versions weren't producing anime). Content-only, no widget shift. Also dropped from the plan: **Character presets** (owner's personal characters) and **`bk_heritage`** (overlaps built Ancestry); **Halloween** flagged not-ready.
- **0.9.8** **Fix:** Mayhem ignored the Art Style category — it was never added to `_MAYHEM_SLOT` when the category shipped in 0.9.3. Added `art_style` as a **core** mayhem slot, so every mayhem image now rolls a random art style, leading the prompt. Determinism preserved (preview == execution); mayhem seeds re-roll vs pre-0.9.8. No widget shift.
- **0.9.9** **Cybernetics as an axis.** Split augmentation from identity: new global `common/cybernetics.txt` (17 species-neutral augments — single/both Arm·Hand·Leg·Foot·Ear, Jaw, Torso, Neural Jack, + Partial Cyborg Four Limbs/Upper/Lower/Extensive) in its **own group between Physical and Hair** (`order 14`), composing onto any metatype (orc + cyber arm). Metatypes restructured: **Android + Gynoid strengthened to 3 variants each**; **Cybernetic Augmented, Partial Cyborg and Cyber-Eyed removed** (augments-as-identity; cyber-eyes already live in the Eyes category). Metatype set 32 → 29 sections. New widget → re-add.
- **0.9.10** **Cybernetics Color.** New `common/cybernetics_color.txt` (`— off —` = chrome / `— random —` / 14 colours drawn from the _ghost.runner + Cassette Futurism hue vocabulary). Cross-category rule `_apply_cyber_color` swaps the chosen colour into the augment's `chrome` finish word and drops the colour entry — the colour binds to the metal instead of floating, and vanishes when no augment is active. Preview == execution preserved. Replaced the chrome/matte-black augment variants with this single colour axis.
- **0.9.11** Two art styles added — **Bradhamel Style** (painterly oil-realism, distinct from BKSTYLE's blend) and **Photorealism** (clean 8K-sharp photo, the missing straight-photoreal option); 9 → 11 styles. **Art Style exempted from Mayhem**: mayhem now honours the selected style on its own seeded rng (independent of the mayhem rolls) instead of randomising it — reverses the 0.9.8 core-slot change. Mayhem RNG shifts, so pre-0.9.11 mayhem seeds re-roll. No widget change → no re-add.
- **0.9.12** **Haunted Hallows** theme (8th) — Halloween Costumes (245, 36 sections incl. named-franchise, kept per owner), Environments (26), Poses (30); `{a|b|c}` source rows pre-expanded (192 → 245). **Compression / Zentai Suits** — new `_ghost.runner` Wardrobe category (144 full-coverage armored suits, 7 families, `order 45`, own `suit:` label; transparent variants dropped). **_ghost.runner outfits reworded** — every `bodysuit` (48 lines) swapped to varied covering garments; 270 count unchanged. **Gender word now explicitly adult** — `an adult woman` / `an adult man` / `an adult androgynous person`. Library: `_VERBATIM_LABELS` += `E.T.` with a verbatim-before-rstrip tweak (keeps the dot); no regression to existing labels. Node 50→**54 categories**, 7→**8 themes**, 4,832→**5,277 entries**. New categories/theme → re-add nodes in pre-0.9.12 saved workflows.
