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

- Pick a **theme** from the dropdown. Only that theme's categories contribute.
- Categories marked **◆** are global — they apply to every theme.
- Each toggle is one wildcard category. Set the ones you want to `yes`.
- The node draws one line from each enabled category and joins them with `separator`.
- `seed` drives the draw. Set it to *randomize* for a new combination every run, or *fixed* to lock the result.
- Wire the `prompt` output into whatever feeds your CLIPTextEncode.

**In Gladas' workflow specifically:** wire `prompt` into `text_a` or `text_b` on the `StringFunction` node titled "Positive Prompt" (node 118). Those two slots are free; `text_c` already carries the ImpactWildcardProcessor. The two coexist — you do not have to remove anything.

The second output, `breakdown`, lists exactly which line was drawn from which category. Wire it to a `Preview as Text` node when you want to attribute a result back to the content that produced it.

Add **BK Wildcard Info** and wire its `report` output to a `Preview as Text` node to see every pack and category the loader found, with entry counts.

## Themes

Themes come from the pack directories under `wildcards/`. A pack whose `_pack.json` sets `"global": true` — currently `common` — is always active regardless of the selected theme. Every other pack becomes a theme in the dropdown.

Theme gating is enforced in Python. A category belonging to an inactive theme cannot contribute to the output, whatever its toggle says. The browser extension only *hides* those toggles; if it fails to load, the node shows every toggle and still produces correct output.

Toggle state is remembered per theme. Switching to Dark Fantasy and back leaves your Cyberpunk toggles as you set them.

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
| Common (global) | Ancestry | 44 |
| Cyberpunk | Metatype / Species | 35 |
| Cyberpunk | Tattoos | 75 |
| Cyberpunk | Outfits | 270 |
| Cyberpunk | Weapons / Carry | 28 |
| Cyberpunk | Accent Palette | 28 |
| Cyberpunk | Environments | 24 |
| Cyberpunk | Poses | 29 |
| Dark Fantasy | Metatype / Species | 28 |
| Dark Fantasy | Tattoos | 75 |
| Dark Fantasy | Outfits | 360 |
| Dark Fantasy | Weapons / Carry | 30 |
| Dark Fantasy | Accent Palette | 31 |

Dark Fantasy has no Environments or Poses file yet, so those toggles do not appear when that theme is selected.

Wildcard content is written for KREA2-style natural-language prompting.

## Known limits (v0.2.0)

- Widget hiding uses a community pattern, not a supported API — [Comfy-Org/ComfyUI#12244](https://github.com/Comfy-Org/ComfyUI/issues/12244) requests an official one and is unanswered. A frontend update could break the hiding. It cannot break the output.
- One theme at a time. No cross-theme blending.
- No section-level selection. A file's `#` headers are organizational only — a draw can come from any section.
- One line per enabled category per run. No multi-draw.
- Adding wildcard files requires a ComfyUI refresh to surface new toggles.
- Full-replacement metatypes (`full kitsune`, `full zombie`, `android`) can still stack on top of an enabled Ancestry line. The node has no mutual-exclusion logic yet.

## License

Not yet chosen. All wildcard content is original work by the repository owner.
