"""
Wildcard library loader for BKWILDCARDS.

Layout
------
`wildcards/<pack>/*.txt` — each subdirectory is a pack, each .txt a category.
`wildcards/<pack>/_pack.json` — optional manifest controlling labels, ordering,
defaults, scope and selection style. Files absent from it still load.

Pack scope
----------
A pack can be scoped on two independent axes:

  "global": true   always active, whatever theme is selected
  "sex": "Female"  only active when that sex is selected

They compose. The `female` pack is global *and* sex-scoped: its categories
apply to every theme, but only when Female is the chosen sex. A theme pack with
no `sex` key is available to every sex.

Orderings
---------
Two, and they are not the same thing:

  display order — the order toggles appear on the node, grouped by pack.
  output order  — the order selections are joined into the prompt, driven by
                  each category's `order` across all packs, so a goth outfit
                  and a cyberpunk outfit land in the same slot of the sentence.

File format
-----------
One entry per line. Blank lines ignored. Lines beginning with '#' are section
headers: ignored for plain categories, but a category declared
`"select": "section"` turns them into a dropdown so you can draw from one
section rather than the whole file.
"""

import json
import os
import re
import zlib

# repo_root/bkwildcards/library.py -> repo_root/wildcards
_HERE = os.path.dirname(os.path.abspath(__file__))
WILDCARD_ROOT = os.path.normpath(os.path.join(_HERE, os.pardir, "wildcards"))

DEFAULT_ORDER = 500
GLOBAL_PACK = "common"

# Reserved options on a section dropdown. Prefixed so a section literally named
# "off" or "any" cannot collide with them.
SECTION_OFF = "— off —"
SECTION_ANY = "— any section —"

SELECT_TOGGLE = "toggle"
SELECT_SECTION = "section"


def _prettify(stem):
    s = re.sub(r"^(krea2bk|krea2-bk|bk)[_-]", "", stem)
    s = re.sub(r"[_-]\d+$", "", s)
    s = s.replace("_", " ").replace("-", " ").strip()
    return s.title() if s else stem


def read_lines(path):
    """Every usable entry in a file, comments and blanks stripped."""
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


def read_sections(path):
    """Entries grouped by their preceding '#' header, in file order.

    Returns a list of (section_name, [lines]). Entries appearing before any
    header are grouped under None. Sections with no entries are dropped.
    """
    sections = []
    current = None
    bucket = []

    def flush():
        if bucket:
            sections.append((current, list(bucket)))

    try:
        with open(path, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    header = line.lstrip("#").strip()
                    # Long rule lines and prose notes are not section headers.
                    if not header or len(header) > 40 or header.startswith("="):
                        continue
                    flush()
                    bucket = []
                    current = header
                    continue
                bucket.append(line)
        flush()
    except OSError:
        return []
    return sections


def _load_pack(pack_dir, pack_name):
    manifest = {}
    manifest_path = os.path.join(pack_dir, "_pack.json")
    if os.path.isfile(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as fh:
                manifest = json.load(fh)
        except (OSError, ValueError):
            manifest = {}

    pack = {
        "pack": pack_name,
        "label": manifest.get("label") or _prettify(pack_name),
        "is_global": bool(manifest.get("global", pack_name == GLOBAL_PACK)),
        "sex": manifest.get("sex") or None,
    }

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

        select = entry.get("select", SELECT_TOGGLE)
        section_names = []
        if select == SELECT_SECTION:
            section_names = [name for name, rows in read_sections(path) if name and rows]
            if not section_names:
                # Declared section-select but the file has no usable headers.
                select = SELECT_TOGGLE

        categories.append(
            {
                "key": "{}_{}".format(pack_name, cid),
                "pack": pack_name,
                "pack_label": pack["label"],
                "is_global": pack["is_global"],
                "sex": pack["sex"],
                "id": cid,
                "label": entry.get("label") or _prettify(stem),
                "path": path,
                "order": entry.get("order", DEFAULT_ORDER),
                "default": bool(entry.get("default", False)),
                "select": select,
                "sections": section_names,
                "count": len(read_lines(path)),
            }
        )
    return pack, categories


def _walk():
    packs, cats = [], []
    if not os.path.isdir(WILDCARD_ROOT):
        return packs, cats
    for pack_name in sorted(os.listdir(WILDCARD_ROOT)):
        pack_dir = os.path.join(WILDCARD_ROOT, pack_name)
        if not os.path.isdir(pack_dir) or pack_name.startswith((".", "_")):
            continue
        pack, pack_cats = _load_pack(pack_dir, pack_name)
        packs.append(pack)
        cats.extend(pack_cats)
    return packs, cats


def scan():
    """Every category, in output order."""
    _, cats = _walk()
    cats.sort(key=lambda c: (c["order"], c["pack"], c["id"]))
    return cats


def scan_packs():
    """Every pack, including packs that currently hold no wildcard files.

    Needed so a sex or theme can appear in its dropdown before any content has
    been written for it.
    """
    packs, _ = _walk()
    return packs


def themes(packs):
    """Selectable theme labels. Global packs are not themes."""
    out = []
    for pack in packs:
        if pack["is_global"]:
            continue
        if pack["label"] not in out:
            out.append(pack["label"])
    return out


def theme_to_pack(packs):
    return {p["label"]: p["pack"] for p in packs if not p["is_global"]}


def sexes(packs):
    """Distinct sex values declared by packs, in pack order."""
    out = []
    for pack in packs:
        s = pack["sex"]
        if s and s not in out:
            out.append(s)
    return out


def section_options(category):
    """Dropdown options for a section-select category."""
    return [SECTION_OFF, SECTION_ANY] + list(category["sections"])


def draw(category, choice, rng):
    """Pick one entry from a category, honouring its selection style.

    Returns None when the category should not contribute.
    """
    if category["select"] == SELECT_SECTION:
        if not choice or choice == SECTION_OFF:
            return None
        if choice == SECTION_ANY:
            pool = read_lines(category["path"])
        else:
            pool = []
            for name, rows in read_sections(category["path"]):
                if name == choice:
                    pool = rows
                    break
    else:
        if not choice:
            return None
        pool = read_lines(category["path"])

    return rng.choice(pool) if pool else None


def stable_offset(key):
    """Deterministic per-category seed offset, stable across processes.

    Python's built-in hash() is salted per process, so the same seed would
    otherwise produce different picks in different ComfyUI sessions.
    """
    return zlib.crc32(key.encode("utf-8")) & 0x7FFFFFFF
