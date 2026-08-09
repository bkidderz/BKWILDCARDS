# BKWILDCARDS

A ComfyUI custom node that turns a bundled wildcard library into a panel of on/off toggles and emits a finished prompt string.

No wildcard syntax to learn. No `__token__` to type. Flip the categories you want, wire one output into your positive prompt, generate.

---

## Install

**Manual (until published):**

```
cd ComfyUI/custom_nodes
git clone https://github.com/bkidderz/BKWILDCARDS.git
```

Restart ComfyUI. No dependencies to install.

## Use

Add **BK Wildcard Selector** (category: `BKWILDCARDS`) to any workflow.

- Pick a **gender** and a **theme**. Only categories in scope for both contribute.
- Categories marked **◆** are global — they apply to every theme.
- Each toggle is one wildcard category. Set the ones you want to `yes`.
- Some categories are **section dropdowns** instead of on/off. Build, Ancestry and Metatype are section dropdowns: pick `Thick`, `European`, `Elves`, any other section from the file, `— random —` to draw from the whole file, or `— off —`.
- The node draws one line from each enabled category and joins them with `separator`.
- `seed` drives the draw. Set it to *randomize* for a new combination every run, or *fixed* to lock the result.
- Wire the `prompt` output into whatever feeds your CLIPTextEncode.

**In Gladas' workflow specifically:** wire `prompt` into `text_a` or `text_b` on the `StringFunction` node titled "Positive Prompt" (node 118). Those two slots are free; `text_c` already carries the ImpactWildcardProcessor. The two coexist — you do not have to remove anything.

After each run the node fills in its **`resolved`** box with the prompt it produced, so you can read it without wiring anything. That text is also stamped into the workflow saved inside generated PNGs — drag a finished image back into ComfyUI and the box still shows the prompt that made it.

Add **BK Wildcard Info** and wire its `report` output to a `Preview as Text` node to see every pack and category the loader found, with entry counts.

## Scope: gender and theme

Packs are scoped on two independent axes in `_pack.json`:

```json
{ "global": true, "gender": "Female" }
```

`"global": true` means the pack applies whatever theme is selected. `"gender"` means it only applies when that gender is chosen. They compose — the `female` pack is global *and* gender-scoped, so its Build category is available under every theme but only when Female is selected. A pack with no `gender` key is available to every gender. Every non-global pack becomes a theme in the dropdown; every distinct `gender` value becomes an option in the gender dropdown, even for a pack that holds no files yet.

Scope gating is enforced in Python. A category belonging to an inactive theme cannot contribute to the output, whatever its toggle says. The browser extension only *hides* those toggles; if it fails to load, the node shows every toggle and still produces correct output.

Selections are remembered per scope. Switching to Dark Fantasy and back leaves your Cyberpunk selections as you set them; the same holds for gender.

## Section dropdowns

A category can be declared `"select": "section"` in `_pack.json`. Its `#` headers then become dropdown options instead of a plain on/off toggle:

```json
{ "file": "builds.txt", "id": "build", "label": "Build", "order": 15, "display": 5, "select": "section" }
```

Header text is cleaned before it becomes an option: leading dashes stripped, a trailing parenthetical cut, then title-cased. So `# -- orks, trolls, dwarves (Shadowrun-style — come in every ancestry, skin unchanged)` becomes `Orks, Trolls, Dwarves`. Anything still over 40 characters after cleaning, plus `# ====` rule lines, is treated as prose and ignored, so a file's explanatory header block does not become a bogus section. Duplicate labels get a numeric suffix. If a file declared this way has no usable headers, the category falls back to an on/off toggle.

## Metatypes are shared, not per-theme

`common/metatypes.txt` holds every species, available under every theme. Merged from the former per-theme files, which had drifted: 20 of 28 identities existed in both, and 8 of those had diverged in wording. Where the two disagreed, both lines were kept as variants of one section rather than one being discarded.

A metatype and an ancestry combine freely. A Japanese werewolf or a Korean full-conversion cyborg is a supported result, not a conflict.

## Two orderings

`order` sets where a category lands **in the prompt**. `display` sets where it appears **on the node**, and defaults to `order` when omitted. They are separate so a category can be moved up the node without moving it in the sentence — Build sits directly under the scope dropdowns (`display: 5`) while still emitting after Ancestry (`order: 15`).

## Output order

Categories emit in a fixed order regardless of which are enabled, so the prompt reads sensibly:

```
ancestry → metatype → tattoos → outfit → weapons → accent palette → environment → pose
```

Order is set per entry in each pack's `_pack.json`.

## Adding wildcards

Drop a `.txt` into a pack directory under `wildcards/`. One entry per line. Blank lines and lines starting with `#` are ignored, so section headers and notes in your files are safe.

A new file becomes a new toggle automatically. Optionally add it to that pack's `_pack.json` to control its label, output position, and default state:

```json
{
  "file": "cyberdecks.txt",
  "id": "cyberdeck",
  "label": "Cyberdecks",
  "order": 45,
  "default": false
}
```

Node inputs are built when ComfyUI loads the module. After adding a file, restart ComfyUI or use **Refresh Node Definitions** for the new toggle to appear.

## Content

| Pack | Category | Entries |
|---|---|---|
| Common (global) | Ancestry — 16 sections | 44 |
| Common (global) | Metatype / Species — 32 sections | 49 |
| Female (global, Female) | Build — 5 sections | 61 |
| Cyberpunk | Tattoos | 75 |
| Cyberpunk | Outfits | 270 |
| Cyberpunk | Weapons / Carry | 28 |
| Cyberpunk | Accent Palette | 28 |
| Cyberpunk | Environments | 24 |
| Cyberpunk | Poses | 29 |
| Dark Fantasy | Tattoos | 75 |
| Dark Fantasy | Outfits | 360 |
| Dark Fantasy | Weapons / Carry | 30 |
| Dark Fantasy | Accent Palette | 31 |

Dark Fantasy has no Environments or Poses file yet, so those toggles do not appear when that theme is selected. The `male` pack exists so Male appears in the dropdown, but holds no files yet.

Wildcard content is written for KREA2-style natural-language prompting.

## Known limits (v0.6.0)

- Widget hiding uses a community pattern, not a supported API — [Comfy-Org/ComfyUI#12244](https://github.com/Comfy-Org/ComfyUI/issues/12244) requests an official one and is unanswered. A frontend update could break the hiding. It cannot break the output.
- One theme at a time. No cross-theme blending.
- Section selection is opt-in per category. Categories not declared `"select": "section"` still draw from the whole file.
- Files using inline `{a|b|c}` syntax are not supported — the braces are emitted literally. Split colour and style into separate files instead.
- One line per enabled category per run. No multi-draw.
- Adding wildcard files requires a ComfyUI refresh to surface new toggles.
- PNG embedding relies on your image saver writing `extra_pnginfo`. Core `SaveImage` does. Third-party savers may not.
- Input order is positional in a saved workflow's `widgets_values`. Adding or moving an input shifts every value after it, so ordering is frozen once this repo is published.

## License

Not yet chosen. All wildcard content is original work by the repository owner.
