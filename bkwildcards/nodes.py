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

# Keys written into the workflow node's `properties` dict so the resolved text
# survives a save and, via extra_pnginfo, an embed into a saved PNG.
PROP_PROMPT = "bk_resolved"
PROP_BREAKDOWN = "bk_breakdown"


def _stamp_workflow(extra_pnginfo, unique_id, prompt_text, breakdown_text):
    """Write the resolved text into the workflow snapshot bound for the PNG.

    ComfyUI captures the workflow at queue time, before this node runs, so a
    widget written after execution would always be one generation stale in the
    saved image. Mutating the `extra_pnginfo` snapshot here — which SaveImage
    serialises into a PNG text chunk after we return — puts *this* run's text
    into *this* run's file.

    We write into the node's `properties` dict rather than `widgets_values`
    because widgets_values is positional, and its indices shift with frontend
    additions such as the control_after_generate widget.
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
            props[PROP_BREAKDOWN] = breakdown_text
            break
    except Exception as exc:  # never let metadata stamping break a render
        print("[BKWILDCARDS] could not stamp workflow metadata: {}".format(exc))


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

        # Display box, declared LAST so it renders below every toggle instead of
        # splitting them. Filled in after execution by the frontend extension and
        # stamped into saved PNGs by _stamp_workflow. Whatever it contains on the
        # way in is ignored.
        #
        # NOTE: widget order is positional in a saved workflow's widgets_values
        # array. Moving an input after a public release shifts every value after
        # it. Treat this ordering as frozen once the repo is published.
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

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "breakdown")
    FUNCTION = "build"
    CATEGORY = "BKWILDCARDS"
    DESCRIPTION = (
        "Pick a theme, enable categories with toggles. Draws one line from each "
        "enabled category and returns them joined as a single prompt string. "
        "The resolved text is shown on the node and saved into generated PNGs."
    )

    def build(
        self,
        seed,
        separator,
        resolved="",
        theme=None,
        extra_pnginfo=None,
        unique_id=None,
        **toggles
    ):
        active_pack = _THEME_TO_PACK.get(theme)

        parts = []
        report = ["theme: {}".format(theme or "(none)"), "seed: {}".format(seed), ""]

        for cat in _CATEGORIES:
            if not (cat["is_global"] or cat["pack"] == active_pack):
                continue
            if not toggles.get(cat["key"], False):
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

        prompt_text = separator.join(parts)
        breakdown_text = "\n".join(report)

        _stamp_workflow(extra_pnginfo, unique_id, prompt_text, breakdown_text)

        return {
            # Picked up by the frontend extension and written into the
            # `resolved` box so you can read it without a preview node.
            "ui": {
                "bk_resolved": [prompt_text],
                "bk_breakdown": [breakdown_text],
            },
            "result": (prompt_text, breakdown_text),
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
