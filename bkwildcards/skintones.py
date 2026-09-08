"""Metatype-driven skin tone — a resolve-time coloration axis (0.9.16, EXPERIMENTAL).

Decouples coloration from metatype identity: the metatype line carries the surface
TYPE + features (flesh / panels / fur / scales) and this axis supplies the COLOUR,
rolled from a palette appropriate to the metatype's skin-GROUP. Mirrors the Body
Sliders pattern — a bank + a metatype->group map + a resolve-time seeded roll, so
preview == execution and a PNG reproduces.

Authoring source AND runtime bank is `wildcards/_skin_tones.txt`
(GROUP: / MEMBERS: / NOTE: + family headers + '* ' tone lines), parsed here. The
leading underscore keeps the pack scanner from treating it as a wildcard category.
"""

import os
import random

from . import library

BANK_PATH = os.path.join(library.WILDCARD_ROOT, "_skin_tones.txt")

INPUT = "skin_tone"                  # widget key (permanent once shipped)
TONE_OFF = library.SECTION_OFF      # "— off —"
TONE_RANDOM = library.SECTION_ANY   # "— random —": roll within the metatype's group
PROMPT_LABEL = "coloration"         # neutral: reads for skin / fur / finish / colour
ORDER = 20                          # ties metatype (20); _apply_skin_tone inserts the
                                    # pick directly after the metatype line so the stable
                                    # sort keeps metatype -> coloration -> eyes (eyes is 20 too)
KEY = "__skin_tone__"               # raw-pick key; not a category, not bald/cyber
DEFAULT_GROUP = "human"             # fallback when no metatype is active


def _parse(path):
    """-> (groups, metatype_group) or (None, {}) on failure. Fails soft.

    groups = {group: {family: [lines]}}; metatype_group = {metatype: group}.
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        print("[BKWILDCARDS] skin tone bank unavailable ({}): {}".format(path, exc))
        return None, {}
    groups, mt_group = {}, {}
    group = family = None
    in_note = False
    for raw in lines:
        s = raw.strip()
        if not s or set(s) <= set("="):          # blank or "====" divider ends a NOTE block
            in_note = False
            continue
        if in_note:                               # a NOTE: may wrap over several lines;
            continue                              # skip until the blank line that ends it
        if s.startswith("GROUP:"):
            group = s[len("GROUP:"):].strip()
            groups.setdefault(group, {})
            family = None
        elif s.startswith("MEMBERS:"):
            for m in s[len("MEMBERS:"):].split(","):
                m = m.strip()
                if m and group:
                    mt_group[m] = group
        elif s.startswith("NOTE:"):
            in_note = True                        # skip this line and any wrapped continuation
        elif s.startswith("*"):
            line = s[1:].strip()
            if line and group and family:
                groups[group].setdefault(family, []).append(line)
        elif group:                               # a family header
            family = s
            groups[group].setdefault(family, [])
    if not groups:
        return None, {}
    return groups, mt_group


GROUPS, METATYPE_GROUP = _parse(BANK_PATH)


def _group_lines(group):
    """Every tone line across a group's families."""
    fams = (GROUPS or {}).get(group) or {}
    return [ln for lines in fams.values() for ln in lines]


def family_options():
    """Dropdown options: off / random / the union of family names (case-insensitive
    dedupe, first-seen display form). Flat list; the resolver keeps a pick coherent
    with the active metatype's group (v1 — metatype-conditioned options are v2)."""
    seen, fams = set(), []
    for g in (GROUPS or {}).values():
        for fam in g:
            k = fam.lower()
            if k not in seen:
                seen.add(k)
                fams.append(fam)
    return [TONE_OFF, TONE_RANDOM] + fams


def frontend_map():
    """Data the frontend uses to LIMIT the Skin Tone dropdown to the active
    metatype's families. Derived from the parsed (current) bank — never hardcoded.

    {off, random, metatype_families: {section: [family...]}, default_families: [...]}
    A metatype maps to its group's families; no/off metatype -> the default
    (human) group's families; — random — metatype -> only off/random (group
    varies per seed). The full flat family list stays the server-side validation
    superset (family_options); the JS just narrows what is shown/selectable.
    """
    if GROUPS is None:
        return {"off": TONE_OFF, "random": TONE_RANDOM,
                "metatype_families": {}, "default_families": []}
    group_fams = {g: list(fams.keys()) for g, fams in GROUPS.items()}
    mt_fams = {mt: group_fams.get(grp, []) for mt, grp in METATYPE_GROUP.items()}
    default_group = next((g for g in GROUPS if g.lower() == DEFAULT_GROUP), None)
    return {
        "off": TONE_OFF,
        "random": TONE_RANDOM,
        "metatype_families": mt_fams,
        "default_families": group_fams.get(default_group, []) if default_group else [],
    }


def roll(seed, metatype_section, choice):
    """One coloration line for this run, or None.

    metatype_section: active metatype section name (e.g. 'Android'), or None.
    choice: the skin_tone widget value (off / random / a family name).
    Own seeded rng stream (stable_offset), so preview == execution.
    """
    if GROUPS is None or not choice or choice == TONE_OFF:
        return None
    group = METATYPE_GROUP.get(metatype_section) if metatype_section else None
    if group is None:                             # no/unknown metatype -> default group
        group = next((g for g in GROUPS if g.lower() == DEFAULT_GROUP), None)
    if group is None:
        return None
    fams = GROUPS.get(group) or {}
    if choice == TONE_RANDOM:
        pool = _group_lines(group)
    else:
        match = next((f for f in fams if f.lower() == choice.lower()), None)
        pool = fams.get(match) if match else _group_lines(group)  # out-of-group -> group roll
    if not pool:
        return None
    return random.Random(int(seed) + library.stable_offset(KEY)).choice(pool)
