"""Serves the node layout to the frontend extension.

The browser needs to know which toggle belongs to which theme in order to hide
off-theme toggles. This endpoint is the only channel for that. It is read-only
and purely cosmetic — if it is unreachable the extension does nothing and the
node still behaves correctly, because theme gating is enforced in Python.
"""

from . import library
from . import nodes

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

    @PromptServer.instance.routes.post("/bkwildcards/populate")
    async def bkwildcards_populate(request):
        """Queue-time preview of the prompt this node will emit.

        The frontend posts the node's current widget values here just before a
        run is queued and shows the result in the on-node box, so the box
        visibly changes every queue instead of only after execution. This is a
        cosmetic preview: the authoritative draw still happens in the node's
        build() during execution. Both call nodes.resolve_prompt over the same
        cached category scan, so the previewed text and the generated image's
        prompt are byte-identical for the same seed. Fails soft — on any error
        the box simply is not previewed and output is unaffected.
        """
        try:
            data = await request.json()
        except Exception:
            data = {}
        if not isinstance(data, dict):
            data = {}
        try:
            text = nodes.resolve_prompt(
                data.get("seed", 0),
                data.get("separator", ", "),
                data.get("gender"),
                data.get("theme"),
                data.get("choices") or {},
            )
        except Exception as exc:
            return web.json_response({"error": str(exc)}, status=400)
        return web.json_response({"text": text})
