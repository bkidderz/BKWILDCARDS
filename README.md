# BKWILDCARDS

**A ComfyUI custom node that turns a bundled wildcard library into scoped dropdowns and emits a finished prompt string.**

No wildcard syntax to learn. No `__token__` to type. Pick a theme, choose the categories you want, wire one output into your prompt, and generate.

Ships with **5,244 hand-written entries** across **54 categories** and **8 themes** — plus a **192-tone, metatype-driven coloration bank** — art styles, cybernetics, outfits, Halloween costumes, environments, poses, ancestry, species, hair, eyes, physical features, skin tone, camera framing and more, all written for natural-language prompting.

---

## Contents

- [Install](#install)
- [How to use](#how-to-use)
- [The node at a glance](#the-node-at-a-glance)
- [Themes and content](#themes-and-content)
- [Features](#features)
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

The node title shows the build number (e.g. `BKWILDCARDS Selector 0.9.18`), so you can confirm the update took.

**Updating to 0.9.16 or later from an older version: delete the BKWILDCARDS Selector node and add it again once.** Version 0.9.16 added a Skin Tone control in the middle of the node, which shifts the saved widget positions below it, so a node carried over from an older workflow can show wrong values until it's re-added. (The same is true when updating from a pre–Body Sliders version.) One-time step; your other nodes and wiring are unaffected.

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

---

## How to use

Add **BKWILDCARDS Selector** to your workflow (right-click → Add Node → **BKWILDCARDS**).

> [!IMPORTANT]
> **You must wire the node's `prompt` output into a prompt block.**
>
> The node does not talk to your model on its own — it only *produces text*. Connect its **`prompt`** output to whatever feeds your positive prompt: a **`CLIPTextEncode`** node's `text` input, or a string node (such as `StringFunction`) that is already feeding your prompt.
>
> **The node tells you if you forgot:** it turns 🔴 **red** and displays
> `NOT ready, please wire the node to your prompt block.`
> Once wired, it turns 🟢 **green** and reads `ready — press Run`.

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

---

## The node at a glance

Widgets are grouped into labelled sections. **Click any section header to collapse or expand it** (▾ / ▸) — collapsed sections are remembered when you save the workflow.

| Section | Contains |
|---|---|
| **Theme** | Theme selector, **Art Style** (leads the prompt) |
| **Identity** | Gender, Ancestry, Metatype / Species |
| **Physical - Body** | **Body Sliders** mode (off / random / on / preset), the Build presets (shown in preset mode), the five body sliders — Mass, Bust, Waist, Hips, Muscle Tone — and **Skin Tone** (a coloration that fits the selected Metatype) |
| **Physical - Head** | Eyes, Face, Nose, Lips (Eyes always available; the rest feminine and/or masculine) |
| **Cybernetics** | The augment (arm, leg, torso, …) and its finish color |
| **Hair** | Hair Type, Hair Style, Hair Color |
| **Wardrobe** | The active theme's tattoos, outfits, weapons / carry (in _ghost.runner, also a full-coverage Compression / Zentai Suits category) |
| **Scene** | Accent palette, environments, poses (plus spell casting/effects in Whimsical Woods) |
| **Camera** | Shot angle, shot framing |
| **Settings** | Separator, seed, labeled output, Mayhem — then the output box |

---

## Themes and content

Each theme is one of the owner's standalone wildcard releases, kept true to that release.

| Theme | Categories |
|---|---|
| **_ghost.runner** *(cyberpunk)* | Outfits (270, 18 sections) · **Compression / Zentai Suits (144, 7 families — full-coverage armored suits)** · Tattoos (75) · Weapons / Carry (28) · Accent Palette (28) · Environments (360, 20 sections — interiors + exteriors) · Poses (29) |
| **Whimsical Woods** *(dark fantasy)* | Outfits (360, 24 sections) · Tattoos (75) · Weapons / Carry (30) · Accent Palette (31) · Environments (360, 20 sections — interiors + exteriors) · Poses (28) · **Spell Casting** (15) · **Spell Effects** (20) |
| **Autumnal Oxidation** *(gothic autumn)* | Outfits (337, 12 goth substyles) · Accent Palette (23) · Environments (13) · Poses (23) |
| **Cassette Futurism** *(retro analog sci-fi)* | Outfits (139, 14 sections) · Accent Palette (23) · Environments (24) · Poses (24) |
| **All the Dresses** | Gowns & Dresses (530) · Eastern Attire (530, 11 sections) · Accent Palette (24) · Environments (13) · Poses (24, dance-forward) |
| **Nettie Necket** *(steampunk)* | Outfits (235, 23 archetypes) · Environments (41, Interiors / Exteriors) · Poses (30, 7 groups) |
| **Haunted Hallows** *(Halloween)* | Costumes (245, 36 sections — classic monsters, cute/glam, franchise costumes) · Environments (26, Interiors / Exteriors) · Poses (30, 8 groups) |
| **COZY SEXY LACY RACY Sleepwear** ⚠️ *adult* | Lingerie Sets (530, 12 sections) |

### Always available (every theme)

| Pack | Categories |
|---|---|
| **Art Style** | 11 styles — Anime, Anime Photo Realism, BKSTYLE, Gladas Style, Painterly, Painterly Photorealism, Photorealism, Pixel Art 16-Bit, Semi-Realism, Surreal, Western Comics (alphabetical; leads the prompt; sits under Theme) |
| **Common** | Ancestry (44, 16 sections — facial structure only) · Metatype / Species (40, 30 sections) |
| **Cybernetics** | 17 augments — single/both limbs, jaw, torso, neural jack, + Partial Cyborg presets · 14 finish colors (— off — = chrome) |
| **Hair** | Hair Color (49) · Hair Type (24, incl. **Bald**) · Hair Style (53) |
| **Eyes** | Eyes (29) — Natural · Cybernetic · Magical · Heterochromia |
| **Shots** | Shot Angle (17) · Shot Framing (33) |
| **Body Sliders** | Five 0–10 sliders (Mass, Bust, Waist, Hips, Muscle Tone) synthesized into one build phrase in the feminine, masculine or androgynous register, chosen by Gender |
| **Skin Tone** | Metatype-driven coloration (192 tones, 12 groups) — human skin tones, tiefling reds/violets, dragonborn scales, android synthetic skin, beast-form fur, vampire pallor, hologram glow. The dropdown offers only the palette that fits the selected Metatype. |
| **Female** *(when Female/Fluid)* | Feminine Build (61, 6 sections — Body Sliders **preset** mode) · Face (26) · Nose (9) · Lips (11) |
| **Male** *(when Male/Fluid)* | Masculine Build (43, 7 sections — Body Sliders **preset** mode) · Face (26) · Nose (10) · Lips (10) |

Ancestry (facial structure) and Metatype combine freely — a Japanese werewolf or a Korean full-conversion cyborg is a supported result — and the separate Skin Tone control colors it to match.

---

## Features

### Labeled output

By default the node tags each selection so the renderer reads structured attributes instead of one run-on sentence:

```
gender: a feminine adult,
ancestry: Korean, warm-toned East Asian features, monolid eyes, …,
coloration: warm caramel-brown skin,
hair: soft black hair, with loose open S-shaped waves, half-up …,
outfit: a sleeveless heavy canvas coverall unzipped low over …,
color palette: muted olive-drab and warm-tan accents …,
scene/background: an exterior landing pad, a boxy retrofuturist craft …,
pose: the subject holds one wrist up close to check a strapped readout …
```

**`label_output`** offers three formats: **`labeled`** (the default, shown above), **`comma-separated`** for a single comma-joined string, and **`JSON`** for the same labeled selections as a JSON object — same keys and values, e.g. `{"gender": "a feminine adult", "ancestry": "Korean, …", "hair": "…"}`.

### Body sliders

**Body Sliders** in the Physical - Body section replaces the single Build dropdown with a shaped body you control. Set the selector to:

- **on** — the five sliders (Mass, Bust, Waist, Hips, Muscle Tone; 0–10, every value is described) are synthesized into one build phrase. Each slider shows the phrase its position selects, live, as you drag it: `Hips: 8 | wide, curvy hips and thick thighs`.
- **— random —** — the five values are rolled from the seed on every run, and the sliders move to show the body that rendered.
- **preset** — the Feminine / Masculine Build presets come back and speak instead. The sliders snap to the chosen preset and keep those values if you then switch to **on**, so a preset works as a starting point you can adjust.
- **— off —** — the lane is silent and the sliders are hidden.

The wording follows **Gender**: Female and Male use their own vocabulary, Fluid uses an androgynous one, and — random — follows the gender rolled for the run. Setting Gender to — off — turns Body Sliders off as well, since a prompt with no subject has no body. Only one build description is ever emitted — the sliders or a preset, never both — and the sliders always show the body that was used, in the preview, in the render and in the saved PNG.

### Skin tone (metatype-driven coloration)

**Skin Tone**, in the Physical - Body section, rolls a coloration that fits your **Metatype** and emits it right after the metatype in the prompt. Every metatype has its own palette — human skin tones for people and same-skin species, reds / violets / golds for tieflings, colored scales for dragonborn, matte and chrome **synthetic skin** for androids, coat colors for full beast-forms, a drained pallor across every skin depth for vampires, and a glow color for holograms. The dropdown only offers the families that belong to the selected Metatype, so you can't pick a green tone for a human or an undead tone for an android. Set it to **— off —** for none, **— random —** to roll within the metatype's palette, or pick a specific family. **Mayhem** keeps the coloration coherent with a selected Metatype. Like everything else it is seed-deterministic and reproduces from the saved PNG.

### Mayhem mode

Flip **`mayhem`** on in Settings for one-click chaos: the node ignores your category selections, the theme and the gender (but keeps your chosen Art Style), and composes a fully random **cross-theme** image — a cyberpunk outfit in a fantasy shrine with a goth pose, and so on. Queue again for a new one. It stays seed-deterministic, so any result you like can be reproduced or recovered from its PNG. For the build, Mayhem flips a seeded coin between one of the Build presets and a body rolled on the sliders, and the sliders show whichever it used.

### Live output preview

The output box updates **at queue time**, before generation starts, so you can see exactly what the run will use. The previewed text is guaranteed identical to what the image is generated from.

---

## License

BKWILDCARDS is licensed in two parts.

**Software** — everything except `wildcards/` — is [MIT](LICENSE). Use it, fork it, ship it, no strings.

**Wildcard content** — everything inside `wildcards/` — is [CC BY-SA 4.0](LICENSE-CONTENT). You may use, adapt and redistribute it, including commercially, provided you credit the author and release any modified or extended version of the library under the same terms.

**Images you generate are yours.** No attribution requested, ShareAlike not asserted against output. The ShareAlike term exists to keep the wildcard library itself open, not to reach into your renders.

All wildcard content is original work by the repository owner and is also published on Civitai.
