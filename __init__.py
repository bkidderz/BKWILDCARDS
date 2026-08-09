"""BKWILDCARDS — toggle-driven wildcard selector for ComfyUI."""

from .bkwildcards import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# Frontend extension. Cosmetic only — hides off-theme toggles.
# Theme gating itself is enforced in Python, so this is safe to lose.
WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
