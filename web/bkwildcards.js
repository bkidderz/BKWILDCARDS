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
import { api } from "../../scripts/api.js";

const BUILD = "0.6.4";
const NODE = "BKWildcardSelector";
const HIDDEN_TYPE = "bkwildcards-hidden";
const RESOLVED_WIDGET = "resolved";
const PROP_PROMPT = "bk_resolved";
const PENDING_TEXT = "… generating …";

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

/**
 * Hide every category widget out of scope for the current gender + theme.
 * Mirrors the Python gate in nodes._in_scope; Python remains authoritative.
 */
function applyTheme(node, layout) {
  if (!node || !layout) return;
  try {
    const activeTheme = node.widgets?.find((w) => w.name === "theme")?.value;
    const activeGender = node.widgets?.find((w) => w.name === "gender")?.value;
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
      const themeOk = cat.is_global || cat.pack === activePack;
      const genderOk = !cat.gender || cat.gender === activeGender;
      setHidden(widget, !(themeOk && genderOk));
    }

    resize(node);
  } catch (err) {
    console.warn("[BKWILDCARDS] scope apply failed, showing all widgets:", err);
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

/**
 * Write the resolved prompt into the on-node display box.
 *
 * Also mirrored into node.properties so a normally-saved workflow carries it.
 * The PNG path is handled server-side instead: ComfyUI snapshots the workflow
 * at queue time, before this node executes, so Python stamps the same property
 * into extra_pnginfo during the run.
 */
function setResolved(node, text, { persist = true } = {}) {
  if (!node || typeof text !== "string") return;
  try {
    const widget = node.widgets?.find((w) => w.name === RESOLVED_WIDGET);
    if (!widget) return;

    // A multiline STRING widget is backed by a real DOM <textarea>. On the very
    // first execution the element gets initialised from widget.value during the
    // node's initial layout pass, so a plain property assignment appears to
    // work. It never syncs again — which is why the box froze on run 1 while
    // the real prompt kept changing. Every known sync path is tried below.
    try {
      widget.value = text;
    } catch (_) {}

    const el =
      widget.inputEl ||
      widget.element ||
      widget.options?.inputEl ||
      (typeof widget.element === "object" ? widget.element : null);

    if (el && "value" in el) {
      if (el.value !== text) {
        el.value = text;
        // Some widget implementations mirror the element back into state only
        // when the element reports a change.
        try {
          el.dispatchEvent(new Event("input", { bubbles: true }));
        } catch (_) {}
      }
      el.readOnly = true;
      el.style.opacity = "0.75";
      el.scrollTop = 0;
    }

    // Widgets built with a setter or callback pathway rather than a raw
    // property. Guarded because calling a callback can re-enter.
    if (!node._bkSyncing) {
      node._bkSyncing = true;
      try {
        if (typeof widget.setValue === "function") widget.setValue(text);
        else if (typeof widget.callback === "function") widget.callback(text, app.canvas, node);
      } catch (_) {
      } finally {
        node._bkSyncing = false;
      }
    }

    if (persist) {
      node.properties = node.properties || {};
      node.properties[PROP_PROMPT] = text;
    }
    node.setDirtyCanvas(true, true);
  } catch (err) {
    console.warn("[BKWILDCARDS] could not write resolved text:", err);
  }
}

/** Every BKWildcardSelector currently on the canvas. */
function selectorNodes() {
  try {
    return (app.graph?._nodes || []).filter((n) => n?.comfyClass === NODE);
  } catch (_) {
    return [];
  }
}

function restoreResolved(node) {
  try {
    const stored = node?.properties?.[PROP_PROMPT];
    if (typeof stored === "string" && stored.length) setResolved(node, stored);
    const widget = node?.widgets?.find((w) => w.name === RESOLVED_WIDGET);
    if (widget?.inputEl) {
      widget.inputEl.readOnly = true;
      widget.inputEl.style.opacity = "0.75";
    }
  } catch (_) {
    /* cosmetic only */
  }
}

function attach(node, layout) {
  if (!node || !layout || node._bkAttached) return;
  node._bkAttached = true;

  relabel(node, layout);

  // Both scope dropdowns re-apply hiding when changed.
  for (const name of ["theme", "gender"]) {
    const widget = node.widgets?.find((w) => w.name === name);
    if (!widget) continue;
    const original = widget.callback;
    widget.callback = function (...args) {
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

// Loud on purpose. If this line is absent from the console, the browser is
// serving a cached copy of this file and no amount of fixing here will show up.
console.log(
  "%c[BKWILDCARDS]%c extension loaded, build " + BUILD,
  "color:#7dd3fc;font-weight:bold", "color:inherit"
);
try {
  window.BKWILDCARDS_BUILD = BUILD;
} catch (_) {}

app.registerExtension({
  name: "bkwildcards.themeSelector",

  async setup() {
    await loadLayout();

    // Visible feedback at queue time. The resolved text cannot be known until
    // Python runs, so the box is marked pending rather than left showing the
    // previous run's prompt. Not persisted — a stale placeholder must never be
    // what gets saved into a workflow or a PNG.
    api.addEventListener("execution_start", () => {
      const nodes = selectorNodes();
      console.debug("[BKWILDCARDS] execution_start ->", nodes.length, "selector node(s)");
      for (const node of nodes) {
        setResolved(node, PENDING_TEXT, { persist: false });
      }
    });

    // Backstop for the per-node onExecuted hook.
    api.addEventListener("executed", (event) => {
      try {
        const detail = event?.detail;
        const text = detail?.output?.bk_resolved?.[0];
        console.debug("[BKWILDCARDS] executed event, node", detail?.node,
                      "resolved:", typeof text === "string" ? text.length + " chars" : "none");
        if (typeof text !== "string") return;
        const node = app.graph?.getNodeById?.(Number(detail.node) || detail.node);
        if (node?.comfyClass === NODE) setResolved(node, text);
      } catch (err) {
        console.warn("[BKWILDCARDS] executed listener failed:", err);
      }
    });

    // If a run dies before this node executes, clear the placeholder rather
    // than leaving it stuck on screen.
    const clearPending = () => {
      for (const node of selectorNodes()) {
        const w = node.widgets?.find((x) => x.name === RESOLVED_WIDGET);
        if (w && w.value === PENDING_TEXT) {
          setResolved(node, node.properties?.[PROP_PROMPT] || "", { persist: false });
        }
      }
    };
    api.addEventListener("execution_error", clearPending);
    api.addEventListener("execution_interrupted", clearPending);
  },

  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData?.name !== NODE) return;
    const onExecuted = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function (message) {
      const r = onExecuted?.apply(this, arguments);
      try {
        const text = message?.bk_resolved?.[0];
        if (typeof text === "string") setResolved(this, text);
      } catch (err) {
        console.warn("[BKWILDCARDS] onExecuted handler failed:", err);
      }
      return r;
    };
  },

  async nodeCreated(node) {
    if (node?.comfyClass !== NODE) return;
    const layout = await loadLayout();
    if (!layout) return;
    attach(node, layout);
    restoreResolved(node);
    // Visible build marker. If the box does not say this build number on a
    // freshly added node, the browser is serving a cached script and no fix
    // in this file has reached the user.
    const w = node.widgets?.find((x) => x.name === RESOLVED_WIDGET);
    if (w && !w.value) {
      setResolved(node, "[BKWILDCARDS build " + BUILD + "] ready — press Run", { persist: false });
    }
    applyNowAndNextFrame(node, layout);
  },

  async loadedGraphNode(node) {
    if (node?.comfyClass !== NODE) return;
    const layout = await loadLayout();
    if (!layout) return;
    attach(node, layout);
    restoreResolved(node);
    applyNowAndNextFrame(node, layout);
  },
});
