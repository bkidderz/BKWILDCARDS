/**
 * BKWILDCARDS frontend extension.
 *
 * PURELY COSMETIC. It hides toggles that belong to a theme other than the one
 * selected, and gives them readable labels. It never adds, removes, reorders or
 * recreates widgets, so the values ComfyUI sends to Python are untouched.
 *
 * Theme gating is enforced in Python. If this file throws, fails to fetch, or
 * is broken by a future frontend change, every guard below fails open: the node
 * shows all toggles and still produces correct output.
 *
 * There is no official ComfyUI API for hiding widgets
 * (Comfy-Org/ComfyUI issue #12244 is open with no maintainer reply), so the
 * type-swap below is a community pattern, not a supported interface. That is
 * exactly why nothing correctness-critical depends on it.
 */

import { app } from "../../scripts/app.js";

const NODE = "BKWildcardSelector";
const HIDDEN_TYPE = "bkwildcards-hidden";

let LAYOUT = null;

async function loadLayout() {
  if (LAYOUT) return LAYOUT;
  try {
    const res = await fetch("/bkwildcards/layout");
    if (!res.ok) throw new Error("HTTP " + res.status);
    LAYOUT = await res.json();
  } catch (err) {
    console.warn("[BKWILDCARDS] layout unavailable, leaving node as-is:", err);
    LAYOUT = null;
  }
  return LAYOUT;
}

function setHidden(widget, hidden) {
  if (!widget) return;
  if (hidden) {
    if (widget.type === HIDDEN_TYPE) return;
    widget._bkType = widget.type;
    widget._bkComputeSize = widget.computeSize;
    widget.type = HIDDEN_TYPE;
    widget.computeSize = () => [0, -4];
  } else {
    if (widget.type !== HIDDEN_TYPE) return;
    widget.type = widget._bkType ?? widget.type;
    widget.computeSize = widget._bkComputeSize ?? widget.computeSize;
    delete widget._bkType;
    delete widget._bkComputeSize;
  }
}

function applyTheme(node, layout) {
  if (!node || !layout) return;
  try {
    const themeWidget = node.widgets?.find((w) => w.name === "theme");
    const activeTheme = themeWidget?.value;
    const activePack = layout.theme_to_pack?.[activeTheme];

    const byKey = new Map();
    for (const cat of layout.categories || []) byKey.set(cat.key, cat);

    for (const widget of node.widgets || []) {
      const cat = byKey.get(widget.name);
      if (!cat) continue;
      const inScope = cat.is_global || cat.pack === activePack;
      setHidden(widget, !inScope);
    }

    const size = node.computeSize();
    // Never shrink narrower than the user has dragged it.
    node.setSize([Math.max(node.size[0], size[0]), size[1]]);
    node.setDirtyCanvas(true, true);
  } catch (err) {
    console.warn("[BKWILDCARDS] theme apply failed, showing all toggles:", err);
    try {
      for (const widget of node.widgets || []) setHidden(widget, false);
    } catch (_) {
      /* give up quietly */
    }
  }
}

function relabel(node, layout) {
  try {
    const byKey = new Map();
    for (const cat of layout.categories || []) byKey.set(cat.key, cat);
    for (const widget of node.widgets || []) {
      const cat = byKey.get(widget.name);
      if (!cat) continue;
      const scope = cat.is_global ? "◆" : "·";
      widget.label = `${scope} ${cat.label}`;
    }
  } catch (err) {
    console.warn("[BKWILDCARDS] relabel failed:", err);
  }
}

app.registerExtension({
  name: "bkwildcards.themeSelector",

  async setup() {
    await loadLayout();
  },

  async nodeCreated(node) {
    if (node?.comfyClass !== NODE) return;
    const layout = await loadLayout();
    if (!layout) return;

    relabel(node, layout);

    const themeWidget = node.widgets?.find((w) => w.name === "theme");
    if (themeWidget) {
      const original = themeWidget.callback;
      themeWidget.callback = function (...args) {
        const result = original?.apply(this, args);
        applyTheme(node, layout);
        return result;
      };
    }

    // Deferred so widget values restored from a saved workflow are in place.
    setTimeout(() => applyTheme(node, layout), 0);
  },

  async loadedGraphNode(node) {
    if (node?.comfyClass !== NODE) return;
    const layout = await loadLayout();
    if (!layout) return;
    relabel(node, layout);
    applyTheme(node, layout);
  },
});
