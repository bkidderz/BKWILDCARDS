# BKWILDCARDS

**A ComfyUI custom node that turns a bundled wildcard library into scoped dropdowns and emits a finished prompt string.**

No wildcard syntax to learn. No `__token__` to type. Pick a theme, choose the categories you want, wire one output into your prompt, and generate.

Ships with **4,799 hand-written entries** across **48 categories** and **7 themes** — art styles, outfits, environments, poses, ancestry, species, hair, eyes, physical features, camera framing and more, all written for natural-language prompting.

---

## Contents

- [Install](#install)
- [How to use](#how-to-use)
- [The node at a glance](#the-node-at-a-glance)
- [Themes and content](#themes-and-content)
- [Features](#features)
- [Adding your own wildcards](#adding-your-own-wildcards)
- [How scoping works](#how-scoping-works)
- [Known limits](#known-limits)
- [License](#license)

---

## Install

### Install via ComfyUI-Manager (recommended)

The easiest way. BKWILDCARDS is published on the [Comfy Registry](https://registry.comfy.org/nodes/bkwildcards), so [ComfyUI-Manager](https://github.com/Comfy-Org/ComfyUI-Manager) can install it for you — no git, no manual file copying.

1. Open **Manager → Custom Nodes Manager**.
2. Search for **BKWILDCARDS**.
3. Click **Install**.
4. **Restart ComfyUI** when prompted.

**There are no dependencies to install** — the node uses only the Python standard library.

### Updating

- **Via ComfyUI-Manager:** open **Manager → Custom Nodes Manager**, find **BKWILDCARDS**, and click **Update** (or use **Update All**). Restart ComfyUI to load the new version. Manager pulls the latest release from the Comfy Registry.
- **Via git** (if you installed with `git clone`): run `git pull` inside the `BKWILDCARDS` folder, then restart ComfyUI.

The node title shows the build number (e.g. `BKWILDCARDS Selector 0.9.7`), so you can confirm the update took.

### Manual install (git)

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/bkidderz/BKWILDCARDS.git
```

Restart ComfyUI. **There are no dependencies to install** — the node uses only the Python standard library.

### Manual install (ZIP)

1. Download this repository as a ZIP (**Code → Download ZIP**).
2. Extract it into `ComfyUI/custom_nodes/`.
3. Make sure the folder is named `BKWILDCARDS` and contains `__init__.py` directly inside it.
4. Restart ComfyUI.

### Where is `custom_nodes`?

| Install type | Path |
|---|---|
| ComfyUI Desktop (Windows) | `%LOCALAPPDATA%\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\custom_nodes` |
| Portable / manual | `<your ComfyUI folder>\ComfyUI\custom_nodes` |

### Verify it loaded

Add the **BKWILDCARDS Selector** node (right-click canvas → Add Node → **BKWILDCARDS**). The node title shows the build number, e.g. `BKWILDCARDS Selector 0.9.7`.

---

## How to use

Add **BKWILDCARDS Selector** to your workflow (right-click → Add Node → **BKWILDCARDS**).

> [!IMPORTANT]
> **You must wire the node's `prompt` output into a prompt block.**
>
> The node does not talk to your model on its own — it only *produces text*. Connect its **`prompt`** output to whatever feeds your positive prompt: a **`CLIPTextEncode`** node's `text` input, or a string node (such as `StringFunction`) that is already feeding your prompt.
>
> **The node tells you if you forgot:** it turns **red** and displays
> `NOT ready, please wire the node to your prompt block.`
> Once wired, it turns **green** and reads `ready — press Run`.

### Basic workflow

1. **Pick a theme** (top of the node) — e.g. `_ghost.runner`, `Whimsical Woods`, `All the Dresses`. Only that theme's categories are shown and can contribute.
2. **Pick a gender** — `Female`, `Male`, `— random —` (rolls per image), `Fluid` (both sets available), or `— off —`.
3. **Choose your categories.** Most are dropdowns with three kinds of choice:
   - `— off —` — this category contributes nothing
   - `— random —` — draw from the whole file
   - a **named section** (e.g. `Netrunner / Decker`, `Interiors`, `Cybergoth`) — draw only from that section
4. **Wire `prompt`** into your prompt block (see the callout above).
5. **Press Run.** The node draws one line from each active category and joins them into a single prompt.

### Getting a new result each run

Set the **`seed`** widget's control to **`randomize`** for a fresh combination every queue, or **`fixed`** to lock a result you like. The `seed` fully determines the output — the same seed always reproduces the same prompt.

### Reading what it produced

The **output box** at the bottom of the node fills in with the exact prompt, **updating the moment you press Run** — before the image renders. That same text is embedded in generated PNGs, so dragging a finished image back into ComfyUI restores the prompt that made it.

### Seeing what's installed

Add the **BKWILDCARDS Info** node and wire its `report` output to a **Preview as Text** node to list every pack and category the loader found, with entry counts.

---

## The node at a glance

Widgets are grouped into labelled sections. **Click any section header to collapse or expand it** (▾ / ▸) — collapsed sections are remembered when you save the workflow.

| Section | Contains |
|---|---|
| **Theme** | Which theme's content is active, plus **Art Style** (leads the prompt) |
| **Identity** | Gender, Ancestry, Metatype / Species |
| **Physical** | Build, Eyes, Face, Nose, Lips (Eyes always available; the rest feminine and/or masculine) |
| **Hair** | Hair Type, Hair Style, Hair Color |
| **Wardrobe** | The active theme's outfits, tattoos, weapons |
| **Scene** | Accent palette, environments, poses (plus spell casting/effects in Whimsical Woods) |
| **Camera** | Shot angle, shot framing |
| **Settings** | Separator, seed, labeled output, Mayhem — then the output box |

---

## Themes and content

Each theme is one of the owner's standalone wildcard releases, kept true to that release.

| Theme | Categories |
|---|---|
| **_ghost.runner** *(cyberpunk)* | Outfits (270, 18 sections) · Tattoos (75) · Weapons / Carry (28) · Accent Palette (28) · Environments (360, 20 sections — interiors + exteriors) · Poses (29) |
| **Whimsical Woods** *(dark fantasy)* | Outfits (360, 24 sections) · Tattoos (75) · Weapons / Carry (30) · Accent Palette (31) · Environments (360, 20 sections — interiors + exteriors) · Poses (28) · **Spell Casting** (15) · **Spell Effects** (20) |
| **Autumnal Oxidation** *(gothic autumn)* | Outfits (337, 12 goth substyles) · Accent Palette (23) · Environments (13) · Poses (23) |
| **Cassette Futurism** *(retro analog sci-fi)* | Outfits (139, 14 sections) · Accent Palette (23) · Environments (24) · Poses (24) |
| **All the Dresses** | Gowns & Dresses (530) · Eastern Attire (530, 11 sections) · Accent Palette (24) · Environments (13) · Poses (24, dance-forward) |
| **Nettie Necket** *(steampunk)* | Outfits (235, 23 archetypes) · Environments (41, Interiors / Exteriors) · Poses (30, 7 groups) |
| **COZY SEXY LACY RACY Sleepwear** ⚠️ *adult* | Lingerie Sets (530, 12 sections) |

### Always available (every theme)

| Pack | Categories |
|---|---|
| **Art Style** | 9 styles — BKSTYLE, GLADAS STYLE, Anime, Anime Photo Realism, Painterly, Pixel Art 16-Bit, Surreal, Semi-Realism, Western Comics (leads the prompt; sits under Theme) |
| **Common** | Ancestry (44, 16 sections) · Metatype / Species (53, 32 sections) |
| **Hair** | Hair Color (49) · Hair Type (24, incl. **Bald**) · Hair Style (53) |
| **Eyes** | Eyes (29) — Natural · Cybernetic · Magical · Heterochromia |
| **Shots** | Shot Angle (20) · Shot Framing (50) |
| **Female** *(when Female/Fluid)* | Feminine Build (61, 6 sections) · Face (26) · Nose (9) · Lips (11) |
| **Male** *(when Male/Fluid)* | Masculine Build (43, 7 sections) · Face (26) · Nose (10) · Lips (10) |

Ancestry and Metatype combine freely — a Japanese werewolf or a Korean full-conversion cyborg is a supported result, not a conflict.

---

## Features

### Labeled output

By default the node tags each selection so the renderer reads structured attributes instead of one run-on sentence:

```
gender: a woman,
ancestry: korean, warm-toned East Asian features, monolid eyes, …,
hair: soft black hair, with loose open S-shaped waves, half-up …,
outfit: a sleeveless heavy canvas coverall unzipped low over …,
color palette: muted olive-drab and warm-tan accents …,
scene/background: an exterior landing pad, a boxy retrofuturist craft …,
pose: the subject holds one wrist up close to check a strapped readout …
```

Flip **`label_output`** to `plain` for a single comma-joined string instead.

### Mayhem mode

Flip **`mayhem`** on in Settings for one-click chaos: the node ignores every selection, the theme and the gender, and composes a fully random **cross-theme** image — a cyberpunk outfit in a fantasy shrine with a goth pose, and so on. Queue again for a new one. It stays seed-deterministic, so any result you like can be reproduced or recovered from its PNG.

### Live output preview

The output box updates **at queue time**, before generation starts, so you can see exactly what the run will use. The previewed text is guaranteed identical to what the image is generated from.

### Bald

Choosing (or randomly drawing) a **Bald** hair type automatically suppresses hair colour and style — no "blonde bald head".

---

## Adding your own wildcards

Drop a `.txt` file into any pack directory under `wildcards/`. One entry per line. Blank lines are ignored; `#` lines are section headers.

```
# Sidearms
a compact polymer-framed pistol holstered at the hip
a heavy revolver worn in a shoulder rig

# Long Guns
a bullpup carbine slung across the chest
```

A new file becomes a new category automatically. Optionally declare it in that pack's `_pack.json` to control its label, prompt position and behaviour:

```json
{
  "file": "cyberdecks.txt",
  "id": "cyberdeck",
  "label": "Cyberdecks",
  "order": 45,
  "group": "Wardrobe",
  "prompt_label": "gear",
  "select": "section",
  "default": false
}
```

| Field | Meaning |
|---|---|
| `order` | Position **in the emitted prompt** |
| `display` | Position **on the node** (defaults to `order`) |
| `group` | Which on-node section it appears under |
| `prompt_label` | The tag used in labeled output (`gear: …`) |
| `select` | `"section"` for an off/random/section dropdown; omit for a plain on/off toggle |
| `default` | Whether it starts enabled |

> [!NOTE]
> Node inputs are built when ComfyUI loads the module. After adding a file, **restart ComfyUI** (or use *Refresh Node Definitions*) for the new category to appear.

Section headers are cleaned before becoming dropdown options: leading dashes stripped, a trailing parenthetical cut, then title-cased. Anything still over 40 characters, plus `# ====` rule lines, is treated as prose and ignored — so an explanatory header block at the top of your file won't become a bogus section. If a file declared `"select": "section"` has no usable headers, it falls back to an on/off toggle.

---

## How scoping works

Packs are scoped on two independent axes in `_pack.json`:

```json
{ "pack": "female", "label": "Female", "global": true, "gender": "Female" }
```

- **`"global": true`** — the pack applies under every theme. Every **non-global** pack becomes a **theme** in the dropdown.
- **`"gender"`** — the pack only applies when that gender is selected. Every distinct value becomes a gender option.

The two compose: the `female` pack is global *and* gender-scoped, so its categories are available under every theme, but only when Female (or Fluid) is selected.

**Scope gating is enforced in Python.** A category belonging to an inactive theme cannot contribute to the output, whatever its widget says. The browser extension only *hides* those widgets — if it fails to load, the node shows everything and still produces correct output.

Selections are remembered per scope: switching theme and back leaves your previous choices intact.

---

## Known limits

- **One theme at a time.** No manual cross-theme blending yet (Mayhem mode does it randomly).
- **Widget hiding uses a community pattern, not a supported API** — [Comfy-Org/ComfyUI#12244](https://github.com/Comfy-Org/ComfyUI/issues/12244) requests an official one and is unanswered. A frontend update could break the hiding; it cannot break the output.
- **One line per active category per run.** No multi-draw.
- **Inline `{a|b|c}` syntax is not supported** — braces are emitted literally. Split alternatives into separate files or sections instead.
- **Adding wildcard files requires a ComfyUI refresh** to surface new categories.
- **PNG embedding relies on your image saver writing `extra_pnginfo`.** Core `SaveImage` does; third-party savers may not.
- **Input order is positional** in a saved workflow's `widgets_values`. Adding or moving an input shifts every value after it, so ordering is frozen at 1.0.

---

## License

BKWILDCARDS is licensed in two parts.

**Software** — everything except `wildcards/` — is [MIT](LICENSE). Use it, fork it, ship it, no strings.

**Wildcard content** — everything inside `wildcards/` — is [CC BY-SA 4.0](LICENSE-CONTENT). You may use, adapt and redistribute it, including commercially, provided you credit the author and release any modified or extended version of the library under the same terms.

**Images you generate are yours.** No attribution requested, ShareAlike not asserted against output. The ShareAlike term exists to keep the wildcard library itself open, not to reach into your renders.

All wildcard content is original work by the repository owner and is also published on Civitai.
