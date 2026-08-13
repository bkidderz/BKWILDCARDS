"""BKWILDCARDS node definitions."""

import random

from . import library

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


def _stamp_workflow(extra_pnginfo, unique_id, prompt_text):
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
_GENDER_TEXT = {"Female": "a woman", "Male": "a man"}
_GENDER_FLUID_TEXT = "an androgynous person"
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


def _drop_if_bald(raw):
    """raw is a list of (order, label, text, key). If the hair_type pick is
    bald, drop the hair colour/style picks. Returns (order, label, text) triples
    ready for _format_picks. Applies whether bald was chosen or randomly drawn.
    """
    bald = any(k == "hair_type" and _is_bald(t) for _, _, t, k in raw)
    if bald:
        raw = [r for r in raw if r[3] not in _HAIR_SUPPRESSED_BY_BALD]
    return [(o, l, t) for o, l, t, _k in raw]


# --- Mayhem mode -----------------------------------------------------------
# One-click, no-input, seeded, cross-theme composition. Maps each category id
# to the "slot" it competes in; mayhem picks at most one category per slot from
# a random source theme, so you get wild cross-theme mixing without stacking
# six outfits. Core slots always appear; extras roll in at _MAYHEM_EXTRA_PROB.
# These constants are tuning knobs, safe to adjust.
_MAYHEM_SLOT = {
    "art_style": "art_style",
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
_MAYHEM_CORE = {"art_style", "ancestry", "build", "hair_color", "hair_type",
                "hair_style", "outfit", "environment", "pose"}
_MAYHEM_EXTRA_PROB = 0.5


def _resolve_mayhem(seed, separator, labeled):
    """Seeded cross-theme random composition, ignoring every input.

    Rolls a gender, then for each slot picks one category from a random source
    theme and a random line from it. Fully determined by `seed`, so the
    queue-time preview still matches the render and a mayhem PNG reproduces.
    Core slots (via `or` short-circuit) never consume an extra-roll, keeping the
    rng sequence identical between preview and execution.
    """
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
    return _format_picks(_drop_if_bald(raw), separator, labeled)


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
        return _resolve_mayhem(seed, separator, labeled)
    choices = choices or {}
    # Random gender -> roll a concrete gender per seed (own rng stream, so the
    # per-category draws are unchanged). Fluid falls through to _in_scope, which
    # drops the gender gate. Deterministic, so preview still matches execution.
    if gender == GENDER_RANDOM and _GENDERS:
        gender = random.Random(
            int(seed) + library.stable_offset("__gender_roll__")
        ).choice(_GENDERS)
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
    return _format_picks(_drop_if_bald(raw), separator, labeled)


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
                    "tooltip": "The subject's gender, injected into the prompt (a woman / a man). "
                    "— off —: no gender word and no gendered categories. — random —: roll a gender "
                    "per seed. Fluid: both genders' physical options available and mixable "
                    "(an androgynous subject).",
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

        for cat in ordered:
            emit(cat)

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
        _stamp_workflow(extra_pnginfo, unique_id, prompt_text)

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
