"""BKWILDCARDS node definitions."""

import random

from . import library

# Scanned once at import. ComfyUI calls INPUT_TYPES at runtime, but the
# category list is cached here so a directory walk does not happen on every
# /object_info request. Adding a new wildcard file requires a ComfyUI restart
# or a "Refresh Node Definitions" to appear.
_CATEGORIES = library.scan()


class BKWildcardSelector:
    """Toggle wildcard categories on and off; emit one combined prompt string."""

    @classmethod
    def INPUT_TYPES(cls):
        required = {
            "seed": (
                "INT",
                {
                    "default": 0,
                    "min": 0,
                    "max": 0xFFFFFFFFFFFFFFFF,
                    "control_after_generate": True,
                    "tooltip": "Drives which line is drawn from each enabled category.",
                },
            ),
            "separator": (
                "STRING",
                {
                    "default": ", ",
                    "multiline": False,
                    "tooltip": "Placed between the selections from each enabled category.",
                },
            ),
        }
        for cat in _CATEGORIES:
            required[cat["key"]] = (
                "BOOLEAN",
                {
                    "default": cat["default"],
                    "label_on": "yes",
                    "label_off": "no",
                    "tooltip": "{} → {} ({} entries)".format(
                        cat["pack_label"], cat["label"], cat["count"]
                    ),
                },
            )
        return {"required": required}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "build"
    CATEGORY = "BKWILDCARDS"
    DESCRIPTION = (
        "Enable wildcard categories with toggles. Draws one line from each "
        "enabled category and returns them joined as a single prompt string."
    )

    def build(self, seed, separator, **toggles):
        parts = []
        for cat in _CATEGORIES:
            if not toggles.get(cat["key"], False):
                continue
            entries = library.read_lines(cat["path"])
            if not entries:
                continue
            rng = random.Random(int(seed) + library.stable_offset(cat["key"]))
            parts.append(rng.choice(entries))

        return (separator.join(parts),)


class BKWildcardInfo:
    """Diagnostic: list every category the loader found, with entry counts."""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("report",)
    FUNCTION = "report"
    CATEGORY = "BKWILDCARDS"
    OUTPUT_NODE = True
    DESCRIPTION = "Lists the wildcard packs and categories BKWILDCARDS loaded."

    def report(self):
        if not _CATEGORIES:
            return ("No wildcard categories found under {}".format(library.WILDCARD_ROOT),)
        lines = ["Wildcard root: {}".format(library.WILDCARD_ROOT), ""]
        current = None
        total = 0
        for cat in _CATEGORIES:
            if cat["pack"] != current:
                current = cat["pack"]
                lines.append("[{}]".format(cat["pack_label"]))
            lines.append(
                "  {:<24} {:>5} entries   (input: {})".format(
                    cat["label"], cat["count"], cat["key"]
                )
            )
            total += cat["count"]
        lines.append("")
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
