"""Serves the node layout to the frontend extension.

The browser needs to know which toggle belongs to which theme in order to hide
off-theme toggles. This endpoint is the only channel for that. It is read-only
and purely cosmetic — if it is unreachable the extension does nothing and the
node still behaves correctly, because theme gating is enforced in Python.
"""

from . import library

try:
    from server import PromptServer
    from aiohttp import web
except ImportError:  # pragma: no cover - not running inside ComfyUI
    PromptServer = None
    web = None


def _payload():
    packs = library.scan_packs()
    cats = library.scan()
    return {
        "themes": library.themes(packs),
        "theme_to_pack": library.theme_to_pack(packs),
        "genders": library.genders(packs),
        "categories": [
            {
                "key": c["key"],
                "pack": c["pack"],
                "pack_label": c["pack_label"],
                "is_global": c["is_global"],
                "gender": c["gender"],
                "label": c["label"],
                "count": c["count"],
                "order": c["order"],
                "select": c["select"],
            }
            for c in cats
        ],
    }


if PromptServer is not None and web is not None:

    @PromptServer.instance.routes.get("/bkwildcards/layout")
    async def bkwildcards_layout(request):
        return web.json_response(_payload())
