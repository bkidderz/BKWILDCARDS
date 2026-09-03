"""BKWILDCARDS node definitions."""

import random
import re

from . import library
from . import sliders

# Scanned once at import. INPUT_TYPES is called on every /object_info request,
# so the walk is cached here. Adding a wildcard file needs a ComfyUI restart or
# "Refresh Node Definitions" before its toggle appears.
_PACKS = library.scan_packs()
_CATEGORIES = library.scan()
_THEMES = sorted(library.themes(_PACKS), key=str.lower)  # alphabetical dropdown
_THEME_TO_PACK = library.theme_to_pack(_PACKS)
_GENDERS = library.genders(_PACKS)

# Written into the workflow node's `properties` so the resolved text survives a
# save and, via extra_pnginfo, an embed into a generated PNG.
PROP_PROMPT = "bk_resolved"
PROP_SLIDERS = "bk_sliders"  # slider lane state (mode, values, register) per run


def _stamp_workflow(extra_pnginfo, unique_id, prompt_text, extra_props=None):
    """Write the resolved text into the workflow snapshot bound for the PNG.

    ComfyUI captures the workflow at queue time, before this node runs, so a
    widget written after execution would always be one generation stale in the
    saved image. Mutating the `extra_pnginfo` snapshot here — which SaveImage
    serialises into a PNG text chunk after we return — puts *this* run's text
    into *this* run's file.

    Written to `properties` rather than `widgets_values` because the latter is
    positional and its indices shift whenever a widget is added.
    """
    if not extra_pnginfo or unique_id is None:
        return
    try:
        workflow = extra_pnginfo.get("workflow")
        if not isinstance(workflow, dict):
            return
        for node in workflow.get("nodes", []) or []:
            if str(node.get("id")) != str(unique_id):
                continue
            props = node.get("properties")
            if not isinstance(props, dict):
                props = {}
                node["properties"] = props
            props[PROP_PROMPT] = prompt_text
            for key, value in (extra_props or {}).items():
                props[key] = value
            break
    except Exception as exc:  # never let metadata stamping break a render
        print("[BKWILDCARDS] could not stamp workflow metadata: {}".format(exc))


# Extra gender-dropdown options beyond the pack-derived genders (Female/Male),
# formatted to match the section dropdowns' reserved options.
GENDER_OFF = library.SECTION_OFF     # "— off —" — no gender, no gendered categories
GENDER_RANDOM = library.SECTION_ANY  # "— random —" — roll a concrete gender per seed
GENDER_FLUID = "Fluid"               # no gender gate — both genders' categories available

# The subject word each gender injects into the prompt so the render is actually
# directed toward a gender. Emitted at order 5, ahead of everything else.
_GENDER_TEXT = {"Female": "an adult woman", "Male": "an adult man"}
_GENDER_FLUID_TEXT = "an adult androgynous person"
_GENDER_ORDER = 5

# The Art Style category leads both the node (second, under the Theme header)
# and the prompt output. Its key is fixed by pack+id (common + art_style); its
# low `order` in _pack.json puts its text first, ahead of the gender word.
ART_STYLE_KEY = "common_art_style"


def _in_scope(cat, active_pack, active_gender):
    """Theme and gender gate. Enforced here, not in the browser.

    active_gender is already resolved to a concrete gender or GENDER_FLUID by
    the time this runs (resolve_prompt rolls GENDER_RANDOM -> a real gender).
    Under Fluid the gender axis is dropped entirely, so both genders'
    gender-scoped categories pass.
    """
    if not (cat["is_global"] or cat["pack"] == active_pack):
        return False
    if cat["gender"] and active_gender != GENDER_FLUID and cat["gender"] != active_gender:
        return False
    return True


def _format_picks(picks, separator, labeled):
    """Join (order, label, text) picks — plain, or as merged 'label: ...' lines.

    Stable sort by `order` matches the pre-existing behaviour (`_CATEGORIES` is
    already ordered by (order, pack, id), so equal-order picks keep their place).
    labeled=True merges adjacent same-label picks (the three hair categories ->
    one 'hair:' line).
    """
    picks = sorted(picks, key=lambda p: p[0])
    if not labeled:
        return separator.join(text for _, _, text in picks)
    groups = []
    for _, label, text in picks:
        if groups and groups[-1][0] == label:
            groups[-1][1].append(text)
        else:
            groups.append((label, [text]))
    return ",\n".join(
        "{}: {}".format(label, ", ".join(texts)) for label, texts in groups
    )


# Bald hair type suppresses hair colour and style (a bald head has neither).
_HAIR_SUPPRESSED_BY_BALD = {"hair_color", "hair_style"}


def _is_bald(text):
    return bool(text) and text.strip().lower().startswith("bald")


# "hair", "hairs", "haired", "long-haired" — but not "hairless"/"hairline".
_HAIR_WORD = re.compile(r"(?<![A-Za-z0-9_-])[A-Za-z0-9_-]*hair(?:ed|s)?(?![A-Za-z0-9_])", re.IGNORECASE)


def _scrub_hair(text):
    """Remove every comma-separated clause that mentions hair; inside a clause
    joined by ' and ', drop only the hair half. Other picks (art styles,
    ancestry, outfits, poses) describe hair in passing — 'layered anime hair',
    'long wavy hair' — and under a bald head those clauses must not reach the
    renderer or it grows hair anyway (owner-reported, 2026-09-01)."""
    if not _HAIR_WORD.search(text):
        return text
    out = []
    for clause in text.split(", "):
        if not _HAIR_WORD.search(clause):
            out.append(clause)
            continue
        keep = [p for p in clause.split(" and ") if not _HAIR_WORD.search(p)]
        if keep:
            out.append(" and ".join(keep))
    return ", ".join(out)


def _drop_if_bald(raw):
    """raw is a list of (order, label, text, key). If the hair_type pick is
    bald, drop the hair colour/style picks AND scrub hair clauses out of every
    other pick's text. Returns (order, label, text) triples ready for
    _format_picks. Applies whether bald was chosen or randomly drawn.
    """
    bald = any(k == "hair_type" and _is_bald(t) for _, _, t, k in raw)
    if bald:
        raw = [(o, l, t if k == "hair_type" else _scrub_hair(t), k)
               for o, l, t, k in raw if k not in _HAIR_SUPPRESSED_BY_BALD]
    return [(o, l, t) for o, l, t, _k in raw]


# Cybernetics finish colour: the Cybernetics Color pick replaces the "chrome"
# finish word inside the chosen Cybernetics augment (a cross-category rule, like
# the bald one). The colour never emits on its own, and vanishes if no augment
# is active. Keep exactly one "chrome" per augment line for a clean swap.
_CYBER_KEY = "common_cybernetics"
_CYBER_COLOR_KEY = "common_cyber_color"
_CYBER_FINISH = "chrome"


def _apply_cyber_color(raw):
    """raw is a list of (order, label, text, key). Fold the Cybernetics Color
    pick into the Cybernetics augment by swapping its finish word, then drop the
    colour entry so it is a modifier, not an emitter."""
    color = next((t for _o, _l, t, k in raw if k == _CYBER_COLOR_KEY), None)
    if color is None:
        return raw
    out = []
    for o, l, t, k in raw:
        if k == _CYBER_COLOR_KEY:
            continue
        if k == _CYBER_KEY and _CYBER_FINISH in t:
            t = t.replace(_CYBER_FINISH, color, 1)
        out.append((o, l, t, k))
    return out


# --- Slider Build Control (EXPERIMENTAL, may never ship) --------------------
# A manual body-shaping lane parallel to the Build presets. Master toggle ON ->
# the slider-synthesized build emits under the Build slot and every Build
# preset pick is dropped for that run (one body description, never two).
# OFF -> the sliders are inert. Value->prose rules live in sliders.py; the
# gender->register mapping is here with the rest of the gender logic.
# Register = Gender (the owner's "hard lock", 2026-09-01): Female/Male -> the
# gendered banks; Fluid and Off -> the androgynous bank; Random never reaches
# here (resolve_prompt rolls it to a concrete gender first). A masculine..
# feminine blend slider stood in for this for part of 2026-09-01 and was
# removed the same day.
_SLIDER_REGISTER = {
    "Female": "feminine",
    "Male": "masculine",
    GENDER_FLUID: "androgynous",
    GENDER_OFF: "androgynous",
}
_SLIDER_DEFAULT_REGISTER = "androgynous"
# The Build preset picks the slider build replaces, and the slot it takes over.
_BUILD_KEYS = {c["key"] for c in _CATEGORIES if c["id"] == "build"}
_BUILD_CAT = next((c for c in _CATEGORIES if c["id"] == "build"), None)
_BUILD_ORDER = _BUILD_CAT["order"] if _BUILD_CAT else 15
_BUILD_LABEL = (_BUILD_CAT.get("prompt_label") or _BUILD_CAT["label"]) if _BUILD_CAT else "build"
_SLIDER_KEY = "__body_sliders__"


def _slider_register(gender):
    return _SLIDER_REGISTER.get(gender, _SLIDER_DEFAULT_REGISTER)


def _resolve_gender(seed, gender):
    """Random -> a concrete gender rolled per seed on its own rng stream (so
    the per-category draws are unchanged). Deterministic, so preview still
    matches execution. Everything else passes through."""
    if gender == GENDER_RANDOM and _GENDERS:
        return random.Random(
            int(seed) + library.stable_offset("__gender_roll__")
        ).choice(_GENDERS)
    return gender


def _preset_pick(seed, gender, choices):
    """(register, section) of the Build preset that will emit this run, or
    None. Mirrors the category loop's draw for the build categories so the
    section of a `— random —` preset is known at preview time."""
    gender = _resolve_gender(seed, gender)
    active = [c for c in _CATEGORIES if c["id"] == "build" and _in_scope(c, None, gender)]
    for cat in active:
        rng = random.Random(int(seed) + library.stable_offset(cat["key"]))
        pick = library.draw(cat, choices.get(cat["key"]), rng)
        if not pick:
            continue
        section = next((name for name, rows in library.read_sections(cat["path"]) if pick in rows), None)
        return _SLIDER_REGISTER.get(cat["gender"], _SLIDER_DEFAULT_REGISTER), section
    return None


def slider_state(seed, gender, choices):
    """What the slider lane will do for this run, or None when it is off.

    {"mode", "values": {axis: 0-10} | None, "register", "section"?} — under
    `— random —` the values are rolled from the seed (sliders.roll_values);
    under `on` they are read from the widgets; under `preset` they are the
    emitting preset section's vector (display only — the preset prose is what
    emits). Gender `— off —` -> None: the lane is suppressed like the gendered
    presets are. Shared by resolve_prompt (to build the text), build() (to
    stamp the state into the PNG workflow) and the populate endpoint (to hand
    the values back so the on-node sliders show them). Pure function of its
    arguments, so all three agree.
    """
    choices = choices or {}
    mode = sliders.mode_of(choices.get(sliders.TOGGLE_INPUT))
    if mode == sliders.MODE_OFF or sliders.BANKS is None or gender == GENDER_OFF:
        return None
    register = _slider_register(_resolve_gender(seed, gender))
    if mode == sliders.MODE_PRESET:
        pick = _preset_pick(seed, gender, choices)
        if pick is None:
            return {"mode": mode, "values": None, "register": register, "section": None}
        reg, section = pick
        return {"mode": mode, "values": sliders.preset_vector(reg, section),
                "register": reg, "section": section}
    if mode == sliders.MODE_RANDOM:
        values = sliders.roll_values(seed)
    else:
        values = {axis: sliders.clamp(choices.get(name))
                  for axis, name in sliders.AXIS_INPUTS.items()}
    return {"mode": mode, "values": values, "register": register}


def _apply_body_sliders(raw, seed, gender, choices):
    """raw is a list of (order, label, text, key). With the slider lane on or
    random, replace the Build preset picks with the synthesized slider build.
    Fails soft: no banks -> presets untouched."""
    state = slider_state(seed, gender, choices)
    if state is None or state["mode"] == sliders.MODE_PRESET:
        return raw  # off, Gender off, or the presets' turn to speak
    text = sliders.synthesize(state["register"], state["values"])
    raw = [r for r in raw if r[3] not in _BUILD_KEYS]
    if text:
        raw.append((_BUILD_ORDER, _BUILD_LABEL, text, _SLIDER_KEY))
    return raw


# --- Mayhem mode -----------------------------------------------------------
# One-click, no-input, seeded, cross-theme composition. Maps each category id
# to the "slot" it competes in; mayhem picks at most one category per slot from
# a random source theme, so you get wild cross-theme mixing without stacking
# six outfits. Core slots always appear; extras roll in at _MAYHEM_EXTRA_PROB.
# These constants are tuning knobs, safe to adjust.
_MAYHEM_SLOT = {
    "ancestry": "ancestry", "metatype": "metatype", "build": "build",
    "face": "face", "nose": "nose", "lips": "lips",
    "color": "hair_color", "type": "hair_type", "style": "hair_style",
    "outfit": "outfit", "dress": "outfit", "eastern": "outfit", "set": "outfit",
    "tattoo": "tattoos", "weapon": "weapons",
    "accent_palette": "palette", "environment": "environment",
    "pose": "pose", "spell_casting": "pose",
    "spell_effects": "effect",
    "angle": "shot_angle", "framing": "shot_framing",
}
_MAYHEM_CORE = {"ancestry", "build", "hair_color", "hair_type",
                "hair_style", "outfit", "environment", "pose"}
_MAYHEM_EXTRA_PROB = 0.5


def _mayhem_compose(seed, choices=None):
    """Seeded cross-theme random composition, ignoring every input EXCEPT the
    Art Style selection. Returns (raw picks, slider-lane state).

    Rolls a gender, then for each slot picks one category from a random source
    theme and a random line from it. Fully determined by `seed`, so the
    queue-time preview still matches the render and a mayhem PNG reproduces.
    Core slots (via `or` short-circuit) never consume an extra-roll, keeping the
    rng sequence identical between preview and execution.

    Art Style is exempt from the randomisation: mayhem honours the user's Art
    Style pick on its own seeded rng stream (independent of the mayhem rolls), so
    the look stays consistent while everything else goes wild. Off contributes
    nothing; a specific style stays put; — random — still rolls per seed.
    """
    choices = choices or {}
    rng = random.Random(int(seed))
    gender = rng.choice([None] + list(_GENDERS))
    slots = {}
    for cat in _CATEGORIES:
        if cat["gender"] and cat["gender"] != gender:
            continue
        slot = _MAYHEM_SLOT.get(cat["id"])
        if slot:
            slots.setdefault(slot, []).append(cat)
    raw = []  # (order, label, text, key)
    # Art Style is honoured from the user's selection, not randomised by mayhem.
    art_cat = next((c for c in _CATEGORIES if c["key"] == ART_STYLE_KEY), None)
    if art_cat:
        art_rng = random.Random(int(seed) + library.stable_offset(art_cat["key"]))
        pick = library.draw(art_cat, choices.get(art_cat["key"]), art_rng)
        if pick:
            raw.append((art_cat["order"],
                        art_cat.get("prompt_label") or art_cat["label"],
                        pick, art_cat["key"]))
    gtext = _GENDER_TEXT.get(gender)
    if gtext:
        raw.append((_GENDER_ORDER, "gender", gtext, None))
    for slot, cats in slots.items():
        if slot not in _MAYHEM_CORE and rng.random() >= _MAYHEM_EXTRA_PROB:
            continue
        cat = rng.choice(cats)
        pool = library.read_lines(cat["path"])
        if not pool:
            continue
        raw.append((cat["order"], cat.get("prompt_label") or cat["label"],
                    rng.choice(pool), cat["key"]))
    return _mayhem_slider_lane(seed, gender, raw)


# Mayhem's build slot: a preset line (as always) or a rolled slider body, on a
# seeded coin. Its own rng stream, so every other Mayhem pick for a seed is
# unchanged by this feature. Tuning knob (owner: 50/50, 2026-09-01).
_MAYHEM_SLIDER_PROB = 0.5


def _mayhem_slider_lane(seed, gender, raw):
    """raw is a list of (order, label, text, key). With a preset build in the
    composition, flip the coin: heads -> replace it with a slider body rolled
    from the seed in the rolled gender's register; tails -> keep the preset and
    report its section's vector. Returns (raw, state) where state is what the
    sliders mirror ({"mode": "mayhem", "values", "register", "section"?}) or
    None when Mayhem rolled no gender (no body, as with Gender off)."""
    build = next((r for r in raw if r[3] in _BUILD_KEYS), None)
    if gender is None or build is None or sliders.BANKS is None:
        return raw, None
    rng = random.Random(int(seed) + library.stable_offset("__mayhem_sliders__"))
    register = _SLIDER_REGISTER.get(gender, _SLIDER_DEFAULT_REGISTER)
    if rng.random() < _MAYHEM_SLIDER_PROB:
        values = {axis: rng.randint(sliders.SLIDER_MIN, sliders.SLIDER_MAX)
                  for axis in sliders.AXES}
        text = sliders.synthesize(register, values)
        if text:
            raw = [r for r in raw if r[3] not in _BUILD_KEYS]
            raw.append((_BUILD_ORDER, _BUILD_LABEL, text, _SLIDER_KEY))
            return raw, {"mode": sliders.MODE_MAYHEM, "values": values, "register": register}
    cat = next((c for c in _CATEGORIES if c["key"] == build[3]), None)
    section = None
    if cat:
        section = next((name for name, rows in library.read_sections(cat["path"])
                        if build[2] in rows), None)
    return raw, {"mode": sliders.MODE_MAYHEM, "values": sliders.preset_vector(register, section),
                 "register": register, "section": section}


def _resolve_mayhem(seed, separator, labeled, choices=None):
    raw, _state = _mayhem_compose(seed, choices)
    return _format_picks(_drop_if_bald(_apply_cyber_color(raw)), separator, labeled)


def mayhem_slider_state(seed, choices=None):
    """The slider-lane state of a Mayhem run (for the populate endpoint and the
    PNG stamp), from the same seeded composition build() emits."""
    return _mayhem_compose(seed, choices)[1]


def resolve_prompt(seed, separator, gender=None, theme=None, choices=None,
                   labeled=False, mayhem=False):
    """Draw one line from each in-scope, enabled category and join them.

    The single source of truth for the emitted prompt. Both build() (during
    graph execution) and the POST /bkwildcards/populate endpoint (at queue
    time, for the on-node preview) call this, so the preview cannot drift from
    the generated image: identical seed + choices give a byte-identical string,
    because per-category seeding is deterministic across processes
    (library.stable_offset uses zlib.crc32, never the salted built-in hash()).

    labeled=True tags each selection with what it is ("build: ...", "hair: ...").
    mayhem=True ignores the inputs entirely and returns a seeded cross-theme
    random composition (see _resolve_mayhem) — still a pure function of `seed`.
    """
    if mayhem:
        return _resolve_mayhem(seed, separator, labeled, choices)
    choices = choices or {}
    # Random gender -> roll a concrete gender per seed (own rng stream, so the
    # per-category draws are unchanged). Fluid falls through to _in_scope, which
    # drops the gender gate. Deterministic, so preview still matches execution.
    gender = _resolve_gender(seed, gender)
    active_pack = _THEME_TO_PACK.get(theme)
    raw = []  # (order, label, text, key)
    # Lead with the gender subject word so the prompt is directed toward a gender
    # (Off emits nothing; Fluid an androgynous subject).
    gtext = _GENDER_TEXT.get(gender) or (
        _GENDER_FLUID_TEXT if gender == GENDER_FLUID else None
    )
    if gtext:
        raw.append((_GENDER_ORDER, "gender", gtext, None))
    for cat in _CATEGORIES:
        if not _in_scope(cat, active_pack, gender):
            continue
        rng = random.Random(int(seed) + library.stable_offset(cat["key"]))
        pick = library.draw(cat, choices.get(cat["key"]), rng)
        if pick:
            raw.append((cat["order"], cat.get("prompt_label") or cat["label"],
                        pick, cat["key"]))
    raw = _apply_body_sliders(raw, seed, gender, choices)
    return _format_picks(_drop_if_bald(_apply_cyber_color(raw)), separator, labeled)


class BKWildcardSelector:
    """Pick a gender and a theme, choose categories, emit one prompt string.

    Scoping is enforced in Python. A category belonging to another theme or
    another gender cannot contribute no matter what its widget says. The frontend
    extension only hides those widgets; if it fails to load, behaviour is
    unchanged and the node simply shows everything.
    """

    @classmethod
    def INPUT_TYPES(cls):
        required = {}

        # Emit one category's widget (section dropdown or boolean toggle) into
        # `required`. A closure so the Art Style category can be placed at the
        # top (before gender) while every other category flows through the loop.
        def emit(cat):
            scope_bits = []
            if cat["gender"]:
                scope_bits.append(cat["gender"])
            scope_bits.append("always on" if cat["is_global"] else cat["pack_label"])
            scope = " / ".join(scope_bits)
            if cat["select"] == library.SELECT_SECTION:
                options = library.section_options(cat)
                required[cat["key"]] = (
                    options,
                    {
                        "default": options[0],
                        "tooltip": "{} — {}. Pick a section, or random to draw from all {} entries.".format(
                            scope, cat["label"], cat["count"]
                        ),
                    },
                )
            else:
                required[cat["key"]] = (
                    "BOOLEAN",
                    {
                        "default": cat["default"],
                        "label_on": "yes",
                        "label_off": "no",
                        "tooltip": "{} — {} ({} entries)".format(
                            scope, cat["label"], cat["count"]
                        ),
                    },
                )

        # --- scope selectors, top of the node ---
        # Theme is its own UI section; gender leads the Identity section. The JS
        # assigns their section headers (theme -> "Theme", gender -> "Identity").
        if _THEMES:
            required["theme"] = (
                _THEMES,
                {
                    "default": _THEMES[0],
                    "tooltip": "Only this theme's categories contribute. Others are ignored.",
                },
            )

        # Art Style: second option under the Theme header (emitted here, right
        # after the theme selector and before gender) and first in the output
        # (its low `order` in _pack.json leads the prompt text).
        art_style_cat = next(
            (c for c in _CATEGORIES if c["key"] == ART_STYLE_KEY), None
        )
        if art_style_cat:
            emit(art_style_cat)

        if _GENDERS:
            required["gender"] = (
                [GENDER_OFF, GENDER_RANDOM] + _GENDERS + [GENDER_FLUID],
                {
                    "default": _GENDERS[0],
                    "tooltip": "The subject's gender, injected into the prompt (an adult woman / an adult man). "
                    "— off —: no gender word and no gendered categories. — random —: roll a gender "
                    "per seed. Fluid: both genders' physical options available and mixable "
                    "(an adult androgynous subject).",
                },
            )

        # --- category selectors ---
        # Global packs first, then each theme's block, each sorted by `display`
        # so a category can be moved on the node without moving it in the
        # prompt. Inputs for every theme and gender always exist, which is what
        # lets settings survive switching away and back.
        def by_display(cats):
            return sorted(cats, key=lambda c: (c["display"], c["pack"], c["id"]))

        # Most globals (Identity, Physical, Hair) render above the theme block.
        # The Camera section is pinned BELOW the theme's Scene, so its globals
        # are emitted after all theme blocks.
        POST_THEME_GROUPS = {"Camera"}
        globals_all = [c for c in _CATEGORIES if c["is_global"] and c["key"] != ART_STYLE_KEY]
        pre_globals = by_display(
            [c for c in globals_all if c.get("group") not in POST_THEME_GROUPS]
        )
        post_globals = by_display(
            [c for c in globals_all if c.get("group") in POST_THEME_GROUPS]
        )

        ordered = list(pre_globals)
        for theme in _THEMES:
            pack = _THEME_TO_PACK[theme]
            ordered += by_display([c for c in _CATEGORIES if c["pack"] == pack])
        ordered += post_globals

        # Slider Build Control (experimental): six fixed inputs emitted directly
        # after the last Build-preset category so they render inside the
        # Physical - Body section: the mode selector, the Build presets under
        # it, then the five body sliders (the JS hides them while the mode is off).
        # Inserting mid-list shifts widgets_values (a one-time node re-add) —
        # the owner's explicit call.
        def emit_body_mode():
            required[sliders.TOGGLE_INPUT] = (
                list(sliders.MODES),
                {
                    "default": sliders.MODE_OFF,
                    "tooltip": "Experimental. on: the five sliders below are synthesized into one "
                    "build phrase (register follows Gender) and the Build preset is ignored. "
                    "— random —: the five values are rolled from the seed each run and shown "
                    "on the sliders. preset: the Build preset dropdown speaks and the sliders "
                    "snap to its section as a starting point. — off —: sliders hidden and "
                    "inert. Gender — off — silences the lane. Mayhem ignores it.",
                },
            )
        def emit_body_axes():
            # No tooltips on the five body sliders: each slider's own label reads
            # out its value and the phrase it selects, live, as it moves (owner,
            # 2026-09-01 — the hover pop-up got in the way of the slider).
            for axis in sliders.AXES:
                required[sliders.AXIS_INPUTS[axis]] = (
                    "INT",
                    {
                        "default": sliders.SLIDER_DEFAULT,
                        "min": sliders.SLIDER_MIN,
                        "max": sliders.SLIDER_MAX,
                        "step": 1,
                        "display": "slider",
                    },
                )

        # Physical - Body order (owner, 2026-09-01): the Body Sliders selector,
        # then the Build preset dropdowns directly under it, then the five
        # sliders. The selector goes out just before the first Physical - Body
        # category and the sliders right after the last.
        body_cats = [c for c in ordered if c.get("group") == sliders.BODY_GROUP]
        body_first = body_cats[0] if body_cats else None
        body_last = body_cats[-1] if body_cats else None
        for cat in ordered:
            if cat is body_first:
                emit_body_mode()
            emit(cat)
            if cat is body_last:
                emit_body_axes()
        if not body_cats:  # no Build categories found: still expose the lane
            emit_body_mode()
            emit_body_axes()

        # --- run controls, below the selectors ---
        required["separator"] = (
            "STRING",
            {
                "default": ", ",
                "multiline": False,
                "tooltip": "Placed between the selections from each enabled category.",
            },
        )
        required["seed"] = (
            "INT",
            {
                "default": 0,
                "min": 0,
                "max": 0xFFFFFFFFFFFFFFFF,
                "control_after_generate": True,
                "tooltip": "Drives which line is drawn from each enabled category.",
            },
        )
        required["label_output"] = (
            "BOOLEAN",
            {
                "default": True,
                "label_on": "labeled",
                "label_off": "plain",
                "tooltip": "Labeled: tag each selection (build:, hair:, scene/background:, …) "
                "so the renderer reads structured attributes. Plain: one comma-joined string.",
            },
        )
        required["mayhem"] = (
            "BOOLEAN",
            {
                "default": False,
                "label_on": "MAYHEM",
                "label_off": "off",
                "tooltip": "One-click chaos: ignore every selection and the theme/gender, and "
                "build a fully random CROSS-THEME image seeded by seed. Queue again "
                "(advance the seed) for a new one. Includes all themes and adult content.",
            },
        )

        # Display box, declared LAST so it renders below everything else.
        #
        # NOTE: widget order is positional in a saved workflow's widgets_values
        # array. Moving or inserting an input shifts every value after it.
        # Treat this ordering as frozen once the repo is published.
        required["resolved"] = (
            "STRING",
            {
                "default": "",
                "multiline": True,
                "tooltip": "The prompt this node produced. Filled in automatically; edits are ignored.",
            },
        )

        return {
            "required": required,
            "hidden": {
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "build"
    CATEGORY = "BKWILDCARDS"
    DESCRIPTION = (
        "Pick a gender and theme, then choose categories. Draws one line from each "
        "and returns them joined as a single prompt string. The resolved text is "
        "shown on the node and saved into generated PNGs."
    )

    def build(
        self,
        seed,
        separator,
        resolved="",
        gender=None,
        theme=None,
        label_output=True,
        mayhem=False,
        extra_pnginfo=None,
        unique_id=None,
        **choices
    ):
        prompt_text = resolve_prompt(
            seed, separator, gender, theme, choices,
            labeled=bool(label_output), mayhem=bool(mayhem),
        )
        # The slider lane's effective values (rolled under — random —) ride
        # along in `properties` so the saved workflow and the PNG carry them.
        state = (mayhem_slider_state(seed, choices) if mayhem
                 else slider_state(seed, gender, choices))
        _stamp_workflow(extra_pnginfo, unique_id, prompt_text,
                        {PROP_SLIDERS: state} if state else None)

        # Printed to the ComfyUI server log every run. If a new line appears
        # here on each queue while the on-node box stays frozen, the backend is
        # fine and the frontend script is stale.
        print(
            "[BKWILDCARDS] node {} seed {} -> {} chars: {}".format(
                unique_id, seed, len(prompt_text), prompt_text[:70].replace("\n", " ")
            )
        )

        return {
            "ui": {"bk_resolved": [prompt_text]},
            "result": (prompt_text,),
        }


class BKWildcardInfo:
    """Diagnostic: list every category the loader found, with entry counts."""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("report",)
    FUNCTION = "report"
    CATEGORY = "BKWILDCARDS"
    DESCRIPTION = "Lists the wildcard packs and categories BKWILDCARDS loaded."

    def report(self):
        lines = ["Wildcard root: {}".format(library.WILDCARD_ROOT), ""]
        total = 0

        for pack in _PACKS:
            flags = []
            if pack["is_global"]:
                flags.append("global")
            if pack["gender"]:
                flags.append(pack["gender"])
            lines.append(
                "[{}]{}".format(pack["label"], "  ({})".format(", ".join(flags)) if flags else "")
            )
            cats = [c for c in _CATEGORIES if c["pack"] == pack["pack"]]
            if not cats:
                lines.append("  (no wildcard files yet)")
            for cat in cats:
                style = (
                    "sections: " + ", ".join(cat["sections"])
                    if cat["select"] == library.SELECT_SECTION
                    else "on/off"
                )
                lines.append(
                    "  {:<20} {:>5} entries   {}".format(cat["label"], cat["count"], style)
                )
                lines.append("  {:<20} input: {}".format("", cat["key"]))
                total += cat["count"]

        lines.append("")
        lines.append("Genders: {}".format(", ".join(_GENDERS) or "(none)"))
        lines.append("Themes: {}".format(", ".join(_THEMES) or "(none)"))
        lines.append("{} categories, {} total entries".format(len(_CATEGORIES), total))
        return ("\n".join(lines),)


NODE_CLASS_MAPPINGS = {
    "BKWildcardSelector": BKWildcardSelector,
    "BKWildcardInfo": BKWildcardInfo,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BKWildcardSelector": "BKWILDCARDS Selector",
    "BKWildcardInfo": "BKWILDCARDS Info",
}
