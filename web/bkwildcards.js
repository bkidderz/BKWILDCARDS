/**
 * BKWILDCARDS frontend extension.
 *
 * PURELY COSMETIC. It hides toggles belonging to a theme other than the one
 * selected and gives them readable labels. It never adds, removes, reorders or
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
let LAYOUT_PROMISE = null;

function loadLayout() {
  if (LAYOUT) return Promise.resolve(LAYOUT);
  if (LAYOUT_PROMISE) return LAYOUT_PROMISE;
  LAYOUT_PROMISE = fetch("/bkwildcards/layout")
    .then((res) => {
      if (!res.ok) throw new Error("HTTP " + res.status);
      return res.json();
    })
    .then((json) => {
      LAYOUT = json;
      return LAYOUT;
    })
    .catch((err) => {
      console.warn("[BKWILDCARDS] layout unavailable, leaving node as-is:", err);
      return null;
    });
  return LAYOUT_PROMISE;
}

/**
 * Hide or show a widget.
 *
 * The restore path is the part that broke in 0.2.0. Most widgets have no own
 * `computeSize`, so the saved value was `undefined` and `undefined ?? current`
 * resolved back to the zero-height override — widgets could hide but never
 * reappear. We now record whether an own property existed and delete rather
 * than reassign when it did not.
 */
function setHidden(widget, hidden) {
  if (!widget) return;

  if (hidden) {
    if (widget._bkHidden) return;
    widget._bkHidden = true;
    widget._bkType = widget.type;
    widget._bkOwnComputeSize = Object.prototype.hasOwnProperty.call(widget, "computeSize");
    if (widget._bkOwnComputeSize) widget._bkComputeSize = widget.computeSize;

    widget.type = HIDDEN_TYPE;
    widget.computeSize = () => [0, -4];
    widget.hidden = true; // honoured by some frontend versions; harmless otherwise
  } else {
    if (!widget._bkHidden) return;

    widget.type = widget._bkType;
    if (widget._bkOwnComputeSize) {
      widget.computeSize = widget._bkComputeSize;
    } else {
      delete widget.computeSize;
    }
    widget.hidden = false;

    delete widget._bkHidden;
    delete widget._bkType;
    delete widget._bkComputeSize;
    delete widget._bkOwnComputeSize;
  }
}

function showAll(node) {
  try {
    for (const widget of node?.widgets || []) setHidden(widget, false);
    resize(node);
  } catch (_) {
    /* give up quietly */
  }
}

function resize(node) {
  if (!node) return;
  const computed = node.computeSize();
  // Keep whatever width the user dragged to; recompute height only.
  node.setSize([Math.max(node.size[0], computed[0]), computed[1]]);
  node.setDirtyCanvas(true, true);
}

function applyTheme(node, layout) {
  if (!node || !layout) return;
  try {
    const themeWidget = node.widgets?.find((w) => w.name === "theme");
    const activeTheme = themeWidget?.value;
    const activePack = layout.theme_to_pack?.[activeTheme];

    // Unknown theme: don't guess, show everything.
    if (!activePack) {
      showAll(node);
      return;
    }

    const byKey = new Map();
    for (const cat of layout.categories || []) byKey.set(cat.key, cat);

    for (const widget of node.widgets || []) {
      const cat = byKey.get(widget.name);
      if (!cat) continue;
      setHidden(widget, !(cat.is_global || cat.pack === activePack));
    }

    resize(node);
  } catch (err) {
    console.warn("[BKWILDCARDS] theme apply failed, showing all toggles:", err);
    showAll(node);
  }
}

function relabel(node, layout) {
  try {
    const byKey = new Map();
    for (const cat of layout.categories || []) byKey.set(cat.key, cat);
    for (const widget of node.widgets || []) {
      const cat = byKey.get(widget.name);
      if (!cat) continue;
      widget.label = `${cat.is_global ? "◆" : "·"} ${cat.label}`;
    }
  } catch (err) {
    console.warn("[BKWILDCARDS] relabel failed:", err);
  }
}

function attach(node, layout) {
  if (!node || !layout || node._bkAttached) return;
  node._bkAttached = true;

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
}

/**
 * Apply once now and once on the next animation frame. The second pass is what
 * catches the initial-load overflow: on first placement the node is sized
 * before widget values from a saved workflow are restored, so a single early
 * pass computes the wrong height.
 */
function applyNowAndNextFrame(node, layout) {
  applyTheme(node, layout);
  requestAnimationFrame(() => applyTheme(node, layout));
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
    attach(node, layout);
    applyNowAndNextFrame(node, layout);
  },

  async loadedGraphNode(node) {
    if (node?.comfyClass !== NODE) return;
    const layout = await loadLayout();
    if (!layout) return;
    attach(node, layout);
    applyNowAndNextFrame(node, layout);
  },
});
