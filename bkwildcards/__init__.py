from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# Registers the /bkwildcards/layout endpoint used by the frontend extension.
# Wrapped because a failure here must never stop the nodes from loading.
try:
    from . import routes  # noqa: F401
except Exception as exc:  # pragma: no cover
    print("[BKWILDCARDS] layout endpoint unavailable: {}".format(exc))

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
