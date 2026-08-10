# BKWILDCARDS — Content Expansion Plan

Working document for growing the bundled library. Survey source:
`comfyui-impact-pack/custom_wildcards/` (Brian's collected/authored wildcard files).

**Status: 2026-08-09 — build `0.8.6`, shipped to the live install for testing,
verified headlessly.** Everything since `0.6.5` is **uncommitted**; committed
`0.6.5` remains the rollback. Node is now **~48 categories / 6 themes** (from 13),
plus **Mayhem mode** and both-gender Physical content.

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

1. **Eyes** — top priority. Still no source file (colours live only inside
   `bk_characters.txt` prose). Needs either Brian's file or his approval for a
   Claude-drafted starter list (colour + natural/unnatural sections; would slot
   into the Physical group and compose like hair does).
2. ~~**README.md for GitHub**~~ — ✅ **DONE.** Rewritten from the stale v0.6.0
   version against verified current state (43 categories, 3,779 entries, 6
   themes). Has Install (git + ZIP + `custom_nodes` paths + verify), How to Use
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
   Only remaining Registry step: add the `REGISTRY_ACCESS_TOKEN` secret to the
   GitHub repo (see `.github/workflows/publish.yml`).
4. ~~**GitHub publish**~~ — ✅ **DONE (2026-08-09).** v0.8.6 committed (`bdb2329`,
   57 files, +4,851) and pushed to **https://github.com/bkidderz/BKWILDCARDS**,
   currently **PRIVATE**. `SNIPPETS.md` gitignored. GitHub reports the license as
   "Other" (not "MIT") because our `LICENSE` opens with the dual-license
   preamble — arguably the right outcome, since a bare MIT badge would misstate
   the content licence. Remaining before it's installable by others:
   **(a) flip the repo to public**, **(b) add the `REGISTRY_ACCESS_TOKEN`
   secret** if publishing to the Comfy Registry, **(c)** optionally tag `v0.8.6`
   / cut a Release.
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

**Content decisions (blocking new content):**
- **Cyberpunk outfits / structure** — current pack uses monolithic **270**.
  Available: 183, 530, and a full granular decomposition (`_ghost.runner 1.a`:
  tops/bottoms/footwear/headgear/outerwear/accessories). Keep 270, bump to 530,
  or adopt the granular model (as done for goth)? This is your primary theme.
- **Character presets (`bk_characters.txt`)** — 12 complete character
  descriptions; a whole-subject preset, not a per-attribute category. Build a
  "Character Preset" picker, or leave it?
- **Extra global candidates** — `bk_gaze.txt` (23 gaze/expression lines) and
  `bk_heritage.txt` (24) are plausible always-on categories. Include either?
- **Unused pose sources** — `bk_poses_action` (25) and `bk_poses_suggestive`
  (62) aren't wired anywhere yet. Want them in fantasy/global poses?
- **"Gowns & Dresses" flat list** — 530 lines, no headers, so it stays a toggle.
  To make it a section dropdown I'd add headers (by silhouette/fabric). Do it?

**Confirmations (currently shipped one way; change if you disagree):**

- **Shot Framing near-duplicates** — I removed only exact dupes; terms like
  "Close-Up" vs "Close Up Portrait Shot" remain as distinct options. Prune?

**Enhancements (scoped, deferred — awaiting Brian):**

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

**Housekeeping:**

- **Commit the 0.7.x/0.8.x milestone to git** once it tests clean (still uncommitted).

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
| `bk_poses_dancing` | 20 dance lines | ✅ Reference for Dresses poses |
| `bk_poses_casting` / `bk_poses_spell_effects` | 15 / 15 | ✅ → Dark Fantasy Spell Casting / Effects |
| `whimsicalWoods_v1B` | fantasy set | ✅ Env/Poses now authored (were missing) |
| `bk_gaze.txt` | 23 gaze lines | ⏳ Candidate global — §2 |
| `bk_heritage.txt` | 24 (8 sections) | ⏳ Candidate global — §2 |
| `bk_poses_action` / `bk_poses_suggestive` | 25 / 62 | ⏳ Unwired — §2 |
| `bk_characters.txt` | 12 character presets | ⏳ Feature? — §2 |
| `_ghost.runner 1.a` | cyberpunk granular (13 files) | ⏳ Cyberpunk restructure — §2 |
| `bk_cyberpunk_outfits_183/530` | outfit supersets | ⏳ Cyberpunk decision — §2 |
| `krea2-bk_female_builds(_small)` | build variants | ✅ Resolved (61 + LITHE) |
| `GhostRunner_v1B` | cyberpunk set | Already the node's `cyberpunk` source |
| `cozySEXYLACYRACY_v1B/bk_lingerie_sets.txt` | 530 lingerie sets | ✅ Built → Lingerie theme (sets only) |
| `Steam Punk` / `halloween` / `nettie_necket` | theme dirs | ⏳ Future themes — §4 |
| `*.zip` | archives | Ignore (extracted copies present) |

---

## 4. Future themes (planned, not built — awaiting your go)

Self-contained theme dirs ready to build the same way when you want them:
`Steam Punk` (env/outfits/poses), `halloween` (env/outfits/poses),
`nettie_necket` (zip, unopened). The `cozySEXYLACYRACY` **sets** are now built (the
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
