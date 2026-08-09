"""BKWILDCARDS node definitions."""

import random

from . import library

# Scanned once at import. ComfyUI calls INPUT_TYPES at runtime, but the
# category list is cached here so a directory walk does not happen on every
# /object_info request. Adding a new wildcard file requires a ComfyUI restart
# or a "Refresh Node Definitions" to appear.
_CATEGORIES = library.scan()
_THEMES = library.themes(_CATEGORIES)
_THEME_TO_PACK = library.theme_to_pack(_CATEGORIES)


class BKWildcardSelector:
    """Pick a theme, toggle categories, emit one combined prompt string.

    Theme gating is enforced here in Python, not in the browser. A category
    belonging to a theme other than the selected one cannot contribute to the
    output no matter what its toggle says. The frontend extension only hides
    those toggles; if it fails to load, behaviour is unchanged and the node
    simply shows every toggle.
    """

    @classmethod
    def INPUT_TYPES(cls):
        required = {}

        if _THEMES:
            required["theme"] = (
                _THEMES,
                {
                    "default": _THEMES[0],
                    "tooltip": "Only this theme's categories contribute. Others are ignored.",
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
        required["separator"] = (
            "STRING",
            {
                "default": ", ",
                "multiline": False,
                "tooltip": "Placed between the selections from each enabled category.",
            },
        )

        # Global categories first, then each theme's block. Inputs for every
        # theme always exist, which is what lets toggle state survive switching
        # themes and switching back.
        ordered = [c for c in _CATEGORIES if c["is_global"]]
        for theme in _THEMES:
            pack = _THEME_TO_PACK[theme]
            ordered += [c for c in _CATEGORIES if c["pack"] == pack]

        for cat in ordered:
            scope = "always on" if cat["is_global"] else cat["pack_label"]
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
        return {"required": required}

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "breakdown")
    FUNCTION = "build"
    CATEGORY = "BKWILDCARDS"
    DESCRIPTION = (
        "Pick a theme, enable categories with toggles. Draws one line from each "
        "enabled category and returns them joined as a single prompt string. "
        "The second output lists what was drawn, for attribution."
    )

    def build(self, seed, separator, theme=None, **toggles):
        active_pack = _THEME_TO_PACK.get(theme)

        parts = []
        report = ["theme: {}".format(theme or "(none)"), "seed: {}".format(seed), ""]

        for cat in _CATEGORIES:
            in_scope = cat["is_global"] or cat["pack"] == active_pack
            enabled = bool(toggles.get(cat["key"], False))

            if not in_scope:
                continue
            if not enabled:
                continue

            entries = library.read_lines(cat["path"])
            if not entries:
                report.append("{}: SKIPPED (file empty)".format(cat["label"]))
                continue

            rng = random.Random(int(seed) + library.stable_offset(cat["key"]))
            pick = rng.choice(entries)
            parts.append(pick)
            report.append("{} [{}]: {}".format(cat["label"], cat["key"], pick))

        if not parts:
            report.append("(nothing enabled — output is empty)")

        return (separator.join(parts), "\n".join(report))


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
        if not _CATEGORIES:
            return ("No wildcard categories found under {}".format(library.WILDCARD_ROOT),)

        lines = ["Wildcard root: {}".format(library.WILDCARD_ROOT), ""]
        by_pack = {}
        for cat in _CATEGORIES:
            by_pack.setdefault((cat["pack"], cat["pack_label"], cat["is_global"]), []).append(cat)

        total = 0
        for (pack, label, is_global), cats in by_pack.items():
            lines.append("[{}]{}".format(label, "  (global — always active)" if is_global else ""))
            for cat in cats:
                lines.append(
                    "  {:<24} {:>5} entries   (input: {})".format(
                        cat["label"], cat["count"], cat["key"]
                    )
                )
                total += cat["count"]
        lines.append("")
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
