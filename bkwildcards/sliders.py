"""Slider Build Control — EXPERIMENTAL (2026-09-01), may never ship.

An optional manual body-shaping lane parallel to the Build presets: five 0-10
sliders (mass, bust, waist, hips, muscle tone) and a mode selector (off /
random / on), synthesized into ONE figure-prose build phrase. This module owns
the value->prose rules; the phrase content is the owner's and lives in
`wildcards/_body_sliders.json` (a root-level file, so the pack scanner never
treats it as a wildcard pack).

Rules (locked with the owner 2026-09-01):

  * Each axis maps to five tiers and EVERY tier emits its phrase, the middle
    (4-6) included — the owner wants intentional control, not averages left to
    the model (the middle tier was silent in the first cut).
  * Per-axis-primary: each axis emits its tier phrase, so a slider crossing a
    tier boundary always changes the text (sliders must feel responsive). A
    silhouette label, derived from the bust/waist/hips ratios, leads when one
    of the ratio rules fires. EMITTING_TIERS is the one knob for a sparser
    model (drop "middle" for silent averages; extremes only = synthesis-primary).
  * The register comes from Gender (nodes._SLIDER_REGISTER): Female ->
    feminine, Male -> masculine, Fluid and Off -> androgynous, Random -> the
    per-seed rolled gender. A masculine..feminine blend slider existed briefly
    (2026-09-01) and was removed the same day: Gender guides the hard lock.
  * Mode `— random —` rolls the five values from the seed on their own rng
    streams (roll_values), so preview == execution and the PNG reproduces; the
    populate endpoint hands the roll back so the on-node sliders show it.
  * Mode `preset` hands the build back to the Build preset dropdowns (hidden
    in every other mode). The sliders snap to the section's vector (JSON
    `presets`, display only) and keep it when the mode flips to `on`, so a
    preset doubles as a starting point (owner, option 3, 2026-09-01).
  * Gender `— off —` suppresses the whole lane, as it already suppresses the
    gendered Build presets: no subject, no body (owner, 2026-09-01).
  * The register's `neutral` phrase is only a safety fallback if a bank phrase
    is missing, so the lane is never a silent no-op.

Mayhem (nodes._mayhem_slider_lane) flips a seeded coin for its build slot:
a preset line as before, or a rolled slider body in the rolled gender's
register (owner, option 2, 2026-09-01). Either way the sliders mirror the body
that rendered.
"""

import json
import os
import random

from . import library

BANKS_PATH = os.path.join(library.WILDCARD_ROOT, "_body_sliders.json")

# Axis order on the node. Emission order differs: mass, tone, silhouette, then
# bust/waist/hips — frame + musculature lead the line (owner's call).
AXES = ("mass", "bust", "waist", "hips", "tone")
REGISTERS = ("feminine", "masculine", "androgynous")
SILHOUETTES = ("hourglass", "pear", "inverted", "round", "straight")

# Input names are permanent once public (CLAUDE invariant #4): a pack directory
# named `body` is therefore reserved.
AXIS_INPUTS = {axis: "body_" + axis for axis in AXES}
TOGGLE_INPUT = "body_sliders"
# The on-node section the inputs share with the Build presets (_pack.json).
BODY_GROUP = "Physical - Body"
# Node order: the mode selector, then the Build preset dropdowns (emitted by
# nodes.INPUT_TYPES between these), then the five sliders (the JS hides the
# sliders while the mode is off).
INPUT_NAMES = [TOGGLE_INPUT] + [AXIS_INPUTS[a] for a in AXES]

# Mode selector options, formatted like every other section dropdown.
MODE_OFF = library.SECTION_OFF       # "— off —"
MODE_RANDOM = library.SECTION_ANY    # "— random —": roll the five values per seed
MODE_ON = "on"                       # use the slider values as set
MODE_PRESET = "preset"               # the Build preset dropdowns speak; sliders echo
MODES = [MODE_OFF, MODE_RANDOM, MODE_ON, MODE_PRESET]
# Not a selector option: the state a Mayhem run reports for the sliders to
# mirror (Mayhem rolls the lane itself; see nodes._mayhem_slider_lane).
MODE_MAYHEM = "mayhem"

SLIDER_MIN = 0
SLIDER_MAX = 10
SLIDER_DEFAULT = 5  # middle tier: "average" — and it emits, like every tier

# (tier name, low, high) inclusive bands over the 0-10 scale.
TIERS = (
    ("lowest", 0, 1),
    ("low", 2, 3),
    ("middle", 4, 6),
    ("high", 7, 8),
    ("highest", 9, 10),
)
MIDDLE_TIER = "middle"
# Every tier emits (owner's call). Silent averages would drop "middle";
# synthesis-primary would be {"lowest", "highest"}.
EMITTING_TIERS = {"lowest", "low", "middle", "high", "highest"}

# --- silhouette thresholds (tuning knobs) ----------------------------------
PROPORTION_TOLERANCE = 2   # |bust - hips| <= this reads as "in proportion"
HOURGLASS_WAIST_DROP = 3   # waist at least this far below both bust and hips
DOMINANT_GAP = 3           # bust-hips (or hips-bust) >= this = top/bottom heavy
DOMINANT_WAIST_GAP = 2     # ...and the dominant axis clears the waist by this
ROUND_WAIST_EXCESS = 2     # waist exceeds both bust and hips by this = round
STRAIGHT_WAIST_SLACK = 1   # waist within this of the smaller of bust/hips


def load_banks(path=BANKS_PATH):
    """Read the phrase banks. Fails soft: a missing or malformed file logs a
    warning and returns None, and nodes.py then leaves the Build preset alone
    (the sliders become inert rather than breaking a render)."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        print("[BKWILDCARDS] body slider banks unavailable ({}): {}".format(path, exc))
        return None
    if not isinstance(data, dict) or not all(r in data for r in REGISTERS):
        print("[BKWILDCARDS] body slider banks malformed: missing a register")
        return None
    return data


# Loaded once at import, like the category scan (restart ComfyUI or refresh
# node definitions after editing the JSON).
BANKS = load_banks()


def mode_of(value):
    """Normalise the mode widget's value. Accepts the dropdown strings and, for
    tolerance, the booleans the first cut used (True -> on, False -> off)."""
    if value is True:
        return MODE_ON
    if not value or value == MODE_OFF:
        return MODE_OFF
    if value == MODE_RANDOM:
        return MODE_RANDOM
    if value == MODE_PRESET:
        return MODE_PRESET
    return MODE_ON


def clamp(value, default=SLIDER_DEFAULT):
    """Coerce a widget value (int, float, numeric string) onto 0-10."""
    try:
        v = int(round(float(value)))
    except (TypeError, ValueError):
        return default
    return max(SLIDER_MIN, min(SLIDER_MAX, v))


def tier_of(value):
    v = clamp(value)
    for name, lo, hi in TIERS:
        if lo <= v <= hi:
            return name
    return MIDDLE_TIER  # unreachable while TIERS covers 0-10


def roll_values(seed):
    """{axis: value} rolled from the seed, one rng stream per axis (keyed by the
    input name via library.stable_offset, so it is stable across processes
    and independent of every category's draw)."""
    out = {}
    for axis in AXES:
        rng = random.Random(int(seed) + library.stable_offset(AXIS_INPUTS[axis]))
        out[axis] = rng.randint(SLIDER_MIN, SLIDER_MAX)
    return out


def preset_vector(register, section):
    """The slider vector a Build preset section maps to (the JSON `presets`
    table), or None. Display only: under `preset` mode the preset prose emits
    and the sliders just show where it sits."""
    table = ((BANKS or {}).get("presets") or {}).get(register) or {}
    vec = table.get(section)
    if not isinstance(vec, dict):
        return None
    return {axis: clamp(vec.get(axis)) for axis in AXES}


def silhouette(bust, waist, hips):
    """Which silhouette label (if any) the three torso axes describe.

    Rules are checked in order; the first that fires wins. None means the
    ratios are unremarkable and the per-axis phrases carry the figure alone.
    """
    b, w, h = clamp(bust), clamp(waist), clamp(hips)
    lo, hi = min(b, h), max(b, h)
    in_proportion = abs(b - h) <= PROPORTION_TOLERANCE
    if in_proportion and lo - w >= HOURGLASS_WAIST_DROP:
        return "hourglass"
    if h - b >= DOMINANT_GAP and h - w >= DOMINANT_WAIST_GAP:
        return "pear"
    if b - h >= DOMINANT_GAP and b - w >= DOMINANT_WAIST_GAP:
        return "inverted"
    if w - hi >= ROUND_WAIST_EXCESS:
        return "round"
    all_middle = all(tier_of(x) == MIDDLE_TIER for x in (b, w, h))
    if in_proportion and w >= lo - STRAIGHT_WAIST_SLACK and not all_middle:
        return "straight"
    return None


def ui_tables():
    """Lookup tables the frontend uses to label each slider live with the
    phrase its current value selects ("Mass: 0 | a gaunt, frail frame").

    Precomputed per value 0-10 so the JS does no tier logic of its own — it
    only indexes these tables, and the phrases are the same objects
    synthesize() uses. Cosmetic: the prompt is still built in Python.
    """
    values = list(range(SLIDER_MIN, SLIDER_MAX + 1))
    phrases = {}
    for reg in REGISTERS:
        bank = (BANKS or {}).get(reg) or {}
        phrases[reg] = {
            axis: [((bank.get(axis) or {}).get(tier_of(v)) or "") for v in values]
            for axis in AXES
        }
    return {
        "axis_of": {name: axis for axis, name in AXIS_INPUTS.items()},
        "toggle_input": TOGGLE_INPUT,
        "mode_off": MODE_OFF,
        "mode_random": MODE_RANDOM,
        "mode_on": MODE_ON,
        "mode_preset": MODE_PRESET,
        "mode_mayhem": MODE_MAYHEM,
        "phrases": phrases,
        # Build preset section -> slider vector, so the sliders can snap the
        # moment a section is chosen (a random preset snaps after the preview).
        "presets": (BANKS or {}).get("presets") or {},
    }


def join_fragments(fragments):
    """Corpus-style chain: 'a slender frame with an hourglass figure, large
    breasts, a narrow waist, toned, defined muscle'. A plain comma list after
    "with" — no closing "and", because fragments may contain "and" themselves
    ("wide hips and thick thighs")."""
    fragments = [f for f in fragments if f]
    if not fragments:
        return ""
    if len(fragments) == 1:
        return fragments[0]
    return "{} with {}".format(fragments[0], ", ".join(fragments[1:]))


def synthesize(register, values, banks=None):
    """One build phrase for a register and a {axis: value} dict.

    Returns None only when the register's bank is missing. Any axis absent
    from `values` counts as the middle value.
    """
    banks = BANKS if banks is None else banks
    bank = (banks or {}).get(register)
    if not isinstance(bank, dict):
        return None
    vals = {axis: clamp(values.get(axis) if values else None) for axis in AXES}

    def phrase(axis):
        tier = tier_of(vals[axis])
        if tier not in EMITTING_TIERS:
            return None
        return (bank.get(axis) or {}).get(tier)

    fragments = [phrase("mass"), phrase("tone")]
    shape = silhouette(vals["bust"], vals["waist"], vals["hips"])
    if shape:
        fragments.append((bank.get("silhouette") or {}).get(shape))
    fragments += [phrase("bust"), phrase("waist"), phrase("hips")]
    text = join_fragments(fragments)
    return text or bank.get("neutral") or None
