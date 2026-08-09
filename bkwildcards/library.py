"""
Wildcard library loader for BKWILDCARDS.

Scans the bundled `wildcards/` directory. Each subdirectory is a "pack".
Each .txt file inside a pack is a "category" that becomes one toggle on the
selector node.

An optional `_pack.json` in a pack directory controls display labels, output
ordering, and default toggle state. Files not listed in `_pack.json` are still
picked up automatically with derived labels and a default order.

File format for wildcard .txt files:
  - one entry per line
  - blank lines ignored
  - lines beginning with '#' ignored (used as section headers / notes)
"""

import json
import os
import re
import zlib

# repo_root/bkwildcards/library.py -> repo_root/wildcards
_HERE = os.path.dirname(os.path.abspath(__file__))
WILDCARD_ROOT = os.path.normpath(os.path.join(_HERE, os.pardir, "wildcards"))

DEFAULT_ORDER = 500

# A pack marked "global": true in its _pack.json is always active regardless of
# the selected theme. By convention the directory named below is global even if
# it has no manifest.
GLOBAL_PACK = "common"


def _prettify(stem: str) -> str:
    """derive a human label from a filename stem"""
    s = re.sub(r"^krea2bk[_-]", "", stem)
    s = re.sub(r"[_-]\d+$", "", s)
    s = s.replace("_", " ").replace("-", " ").strip()
    return s.title() if s else stem


def read_lines(path: str):
    """Return usable entries from a wildcard file, comments and blanks stripped."""
    out = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                out.append(line)
    except OSError:
        return []
    return out


def _load_pack(pack_dir: str, pack_name: str):
    manifest = {}
    manifest_path = os.path.join(pack_dir, "_pack.json")
    if os.path.isfile(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as fh:
                manifest = json.load(fh)
        except (OSError, ValueError):
            manifest = {}

    pack_label = manifest.get("label") or _prettify(pack_name)
    is_global = bool(manifest.get("global", pack_name == GLOBAL_PACK))
    declared = {}
    for entry in manifest.get("entries", []) or []:
        fname = entry.get("file")
        if fname:
            declared[fname] = entry

    categories = []
    for fname in sorted(os.listdir(pack_dir)):
        if not fname.lower().endswith(".txt"):
            continue
        path = os.path.join(pack_dir, fname)
        if not os.path.isfile(path):
            continue

        entry = declared.get(fname, {})
        stem = os.path.splitext(fname)[0]
        cid = entry.get("id") or re.sub(r"[^a-z0-9]+", "_", stem.lower()).strip("_")
        entries = read_lines(path)

        categories.append(
            {
                "key": "{}_{}".format(pack_name, cid),
                "pack": pack_name,
                "pack_label": pack_label,
                "is_global": is_global,
                "id": cid,
                "label": entry.get("label") or _prettify(stem),
                "path": path,
                "order": entry.get("order", DEFAULT_ORDER),
                "default": bool(entry.get("default", False)),
                "count": len(entries),
            }
        )
    return categories


def scan():
    """Return every category across every pack, sorted by output order."""
    cats = []
    if not os.path.isdir(WILDCARD_ROOT):
        return cats
    for pack_name in sorted(os.listdir(WILDCARD_ROOT)):
        pack_dir = os.path.join(WILDCARD_ROOT, pack_name)
        if not os.path.isdir(pack_dir) or pack_name.startswith((".", "_")):
            continue
        cats.extend(_load_pack(pack_dir, pack_name))
    cats.sort(key=lambda c: (c["order"], c["pack"], c["id"]))
    return cats


def stable_offset(key: str) -> int:
    """Deterministic per-category seed offset. Stable across runs and platforms.

    Python's built-in hash() is salted per process, so it cannot be used here —
    the same seed would produce different picks in different ComfyUI sessions.
    """
    return zlib.crc32(key.encode("utf-8")) & 0x7FFFFFFF


def themes(categories):
    """Selectable theme labels, in pack order. Global packs are excluded."""
    seen = []
    for cat in categories:
        if cat["is_global"]:
            continue
        if cat["pack_label"] not in seen:
            seen.append(cat["pack_label"])
    return seen


def theme_to_pack(categories):
    """Map a theme label back to its pack directory name."""
    return {c["pack_label"]: c["pack"] for c in categories if not c["is_global"]}
