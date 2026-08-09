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

- Each toggle is one wildcard category. Set the ones you want to `yes`.
- The node draws one line from each enabled category and joins them with `separator`.
- `seed` drives the draw. Set it to *randomize* for a new combination every run, or *fixed* to lock the result.
- Wire the `prompt` output into whatever feeds your CLIPTextEncode.

**In Gladas' workflow specifically:** wire `prompt` into `text_a` or `text_b` on the `StringFunction` node titled "Positive Prompt" (node 118). Those two slots are free; `text_c` already carries the ImpactWildcardProcessor. The two coexist — you do not have to remove anything.

Add **BK Wildcard Info** and run it to see every pack and category the node loaded, with entry counts. Use it to confirm your install picked up the content.

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
| Common | Ancestry | 44 |
| Cyberpunk | Metatype / Species | 35 |
| Cyberpunk | Tattoos | 75 |
| Cyberpunk | Outfits | 270 |
| Cyberpunk | Weapons / Carry | 28 |
| Cyberpunk | Accent Palette | 28 |
| Cyberpunk | Environments | 24 |
| Cyberpunk | Poses | 29 |

Wildcard content is written for KREA2-style natural-language prompting.

## Known limits (v0.1.0)

- Toggles render as a flat list, not the grouped visual panels shown in the design target. Panel grouping needs a frontend extension; not in this version.
- No section-level selection. A file's `#` headers are organizational only — a draw can come from any section.
- One line per enabled category per run. No multi-draw.
- Adding wildcard files requires a ComfyUI refresh to surface new toggles.

## License

Not yet chosen. All wildcard content is original work by the repository owner.
