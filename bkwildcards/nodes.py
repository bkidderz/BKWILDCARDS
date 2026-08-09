"""BKWILDCARDS node definitions."""

import random

from . import library

# Scanned once at import. INPUT_TYPES is called on every /object_info request,
# so the walk is cached here. Adding a wildcard file needs a ComfyUI restart or
# "Refresh Node Definitions" before its toggle appears.
_PACKS = library.scan_packs()
_CATEGORIES = library.scan()
_THEMES = library.themes(_PACKS)
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


def _in_scope(cat, active_pack, active_gender):
    """Theme and gender gate. Enforced here, not in the browser."""
    if not (cat["is_global"] or cat["pack"] == active_pack):
        return False
    if cat["gender"] and cat["gender"] != active_gender:
        return False
    return True


def resolve_prompt(seed, separator, gender=None, theme=None, choices=None):
    """Draw one line from each in-scope, enabled category and join them.

    The single source of truth for the emitted prompt. Both build() (during
    graph execution) and the POST /bkwildcards/populate endpoint (at queue
    time, for the on-node preview) call this, so the preview cannot drift from
    the generated image: identical seed + choices give a byte-identical string,
    because per-category seeding is deterministic across processes
    (library.stable_offset uses zlib.crc32, never the salted built-in hash()).
    """
    choices = choices or {}
    active_pack = _THEME_TO_PACK.get(theme)
    parts = []
    for cat in _CATEGORIES:
        if not _in_scope(cat, active_pack, gender):
            continue
        rng = random.Random(int(seed) + library.stable_offset(cat["key"]))
        pick = library.draw(cat, choices.get(cat["key"]), rng)
        if pick:
            parts.append(pick)
    return separator.join(parts)


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

        # --- scope selectors, top of the node ---
        if _GENDERS:
            required["gender"] = (
                _GENDERS,
                {
                    "default": _GENDERS[0],
                    "tooltip": "Gender-scoped categories only contribute when their gender is selected.",
                },
            )
        if _THEMES:
            required["theme"] = (
                _THEMES,
                {
                    "default": _THEMES[0],
                    "tooltip": "Only this theme's categories contribute. Others are ignored.",
                },
            )

        # --- category selectors ---
        # Global packs first, then each theme's block, each sorted by `display`
        # so a category can be moved on the node without moving it in the
        # prompt. Inputs for every theme and gender always exist, which is what
        # lets settings survive switching away and back.
        def by_display(cats):
            return sorted(cats, key=lambda c: (c["display"], c["pack"], c["id"]))

        ordered = by_display([c for c in _CATEGORIES if c["is_global"]])
        for theme in _THEMES:
            pack = _THEME_TO_PACK[theme]
            ordered += by_display([c for c in _CATEGORIES if c["pack"] == pack])

        for cat in ordered:
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
        extra_pnginfo=None,
        unique_id=None,
        **choices
    ):
        prompt_text = resolve_prompt(seed, separator, gender, theme, choices)
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
    "BKWildcardSelector": "BK Wildcard Selector",
    "BKWildcardInfo": "BK Wildcard Info",
}
