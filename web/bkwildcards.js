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

const BUILD = "0.9.12";
const NODE = "BKWildcardSelector";
const NODE_TITLE = "BKWILDCARDS Selector";
const HIDDEN_TYPE = "bkwildcards-hidden";
const RESOLVED_WIDGET = "resolved";
const PROP_PROMPT = "bk_resolved";
const PENDING_TEXT = "… generating …";
const HEADER_TYPE = "bkwildcards-header";
const RESOLVED_MIN_H = 150; // px — a taller default for the resolved box
const COLOR_CONNECTED = { color: "#2a4d2a", bgcolor: "#1c331c" }; // green
const COLOR_DISCONNECTED = { color: "#5a2020", bgcolor: "#331414" }; // red

// Non-category widgets that still belong in a titled UI section. Category
// widgets get their section from the layout's `group`; these are the fixed
// widgets ComfyUI/we declare. `control_after_generate` is the combo the
// frontend auto-adds next to a seed.
const SPECIAL_GROUPS = {
  theme: "Theme",
  gender: "Identity",
  separator: "Settings",
  seed: "Settings",
  control_after_generate: "Settings",
  label_output: "Settings",
  mayhem: "Settings",
};

// Display labels for the fixed (non-category) widgets. Only the on-node label is
// prettified; the widget NAME and its serialized value are unchanged.
const FIXED_LABELS = {
  theme: "Theme",
  gender: "Gender",
};

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
 * A non-interactive section-header row spliced into node.widgets.
 *
 * `serialize: false` alone is NOT sufficient to keep these out of
 * `widgets_values` — ComfyUI's serialize skips them but still writes at the
 * full-array index, punching null holes that the sequential reader then
 * misaligns against. See withoutHeaders(), which is what actually makes this
 * safe. Do not remove either mechanism.
 */
function makeHeader(group) {
  return {
    name: "__bkhdr__" + group,
    type: HEADER_TYPE,
    label: group,
    _bkHeader: true,
    _bkGroup: group,
    value: undefined,
    serialize: false,
    options: { serialize: false },
    computeSize() {
      return [0, 22];
    },
    // Click the header row to collapse/expand its section. Toggled on pointer
    // release; persisted in node.properties so a saved workflow remembers it.
    // Returning true consumes the event so the click never drags the node.
    mouse(event, pos, node) {
      try {
        if (((event && event.type) || "").endsWith("up")) {
          node.properties = node.properties || {};
          const c = (node.properties._bkCollapsed =
            node.properties._bkCollapsed || {});
          c[group] = !c[group];
          if (typeof node._bkApply === "function") node._bkApply();
        }
      } catch (_) {}
      return true;
    },
    draw(ctx, node, width, y, H) {
      try {
        const m = 6;
        const collapsed = !!(
          node.properties &&
          node.properties._bkCollapsed &&
          node.properties._bkCollapsed[group]
        );
        ctx.save();
        ctx.fillStyle = "rgba(96,128,168,0.30)";
        ctx.beginPath();
        if (ctx.roundRect) ctx.roundRect(m, y + 2, width - 2 * m, H - 4, 4);
        else ctx.rect(m, y + 2, width - 2 * m, H - 4);
        ctx.fill();
        ctx.fillStyle = "#e6eefa";
        ctx.font = "bold 11px sans-serif";
        ctx.textAlign = "left";
        ctx.textBaseline = "middle";
        ctx.fillText(
          (collapsed ? "▸  " : "▾  ") + String(group).toUpperCase(),
          m + 8,
          y + H / 2 + 1
        );
        ctx.restore();
      } catch (_) {}
    },
  };
}

/**
 * Run `fn` with the header rows temporarily spliced out of node.widgets.
 *
 * REQUIRED for correctness — this is not cosmetic. `widgets_values` is
 * positional, and ComfyUI's two halves disagree about what that position means:
 *
 *   serialize:  writes each value at its index in the FULL widgets array but
 *               SKIPS serialize:false widgets — leaving null holes where our
 *               headers sit.
 *   configure:  reads back SEQUENTIALLY, also skipping serialize:false.
 *
 * A compact reader against a hole-punched writer shifts every value by the
 * number of preceding headers. That corrupted every save/load round-trip and
 * every undo (v0.8.5-0.8.6). Hiding the headers for the duration of both calls
 * makes the array compact and the two halves agree.
 */
function withoutHeaders(node, fn) {
  const all = node?.widgets;
  if (!Array.isArray(all) || !all.some((w) => w && w._bkHeader)) return fn();
  const stripped = all.filter((w) => !w._bkHeader);
  node.widgets = stripped;
  try {
    return fn();
  } finally {
    // Only put them back if nothing else swapped the array out meanwhile.
    if (node.widgets === stripped) node.widgets = all;
  }
}

/**
 * Splice one header row in above the first category of each group, once. The
 * category widgets are already in contiguous group order (driven by `display`
 * in Python), so a header appears wherever the group changes. Non-category
 * widgets (gender/theme/separator/seed/resolved) reset the group so a header
 * reappears at the next category run.
 */
/**
 * The section a widget belongs to. Category widgets carry `group` from the
 * layout; fixed widgets come from SPECIAL_GROUPS. The resolved box gets none
 * (it sits below Settings with no header). `undefined` means "inherit the
 * previous section" — e.g. the auto-added control-after-generate combo.
 */
function groupOf(w, byKey) {
  if (!w) return null;
  if (w.name === RESOLVED_WIDGET) return null;
  const cat = byKey.get(w.name);
  if (cat) return cat.group || null;
  if (SPECIAL_GROUPS[w.name]) return SPECIAL_GROUPS[w.name];
  return undefined;
}

function insertHeaders(node, layout) {
  if (!node || node._bkHeadersDone) return;
  try {
    const byKey = new Map();
    for (const cat of layout.categories || []) byKey.set(cat.key, cat);
    const out = [];
    let prevGroup = null;
    for (const w of node.widgets || []) {
      let group = groupOf(w, byKey);
      if (group === undefined) group = prevGroup; // inherit
      if (group && group !== prevGroup) out.push(makeHeader(group));
      out.push(w);
      prevGroup = group;
    }
    node.widgets = out;
    node._bkHeadersDone = true;
  } catch (err) {
    console.warn("[BKWILDCARDS] header insert failed:", err);
  }
}

/**
 * Show the build number in the node's title so it is obvious which version is
 * running when troubleshooting. Refreshes our own default title (including an
 * old build number, or the pre-0.7 "BK Wildcard" branding) but leaves a title
 * the user has deliberately customised alone.
 */
function setNodeTitle(node) {
  try {
    const t = node.title;
    if (!t || t.startsWith(NODE_TITLE) || t.startsWith("BK Wildcard")) {
      node.title = NODE_TITLE + " " + BUILD;
    }
  } catch (_) {}
}

/** Is the node's prompt output wired to anything downstream? */
function isConnected(node) {
  try {
    const out = node.outputs && node.outputs[0];
    return !!(out && out.links && out.links.length);
  } catch (_) {
    return true; // fail-open: assume wired so we never falsely warn
  }
}

/** A box value that is a status line (safe to overwrite), not a real prompt. */
function isStatusText(v) {
  return (
    typeof v !== "string" ||
    v === "" ||
    v === PENDING_TEXT ||
    v.indexOf("[BKWILDCARDS build") === 0
  );
}

/**
 * Reflect whether the prompt output is wired: green + "ready" when connected,
 * red + "NOT ready…" when not. Only a status line is swapped — a real generated
 * prompt already in the box is left in place (the colour still signals state).
 * Colours are recomputed on load and on every connection change, so the value
 * saved into a workflow can never go stale.
 */
function refreshConnectionState(node) {
  try {
    const connected = isConnected(node);
    const c = connected ? COLOR_CONNECTED : COLOR_DISCONNECTED;
    node.color = c.color;
    node.bgcolor = c.bgcolor;

    const w = node.widgets?.find((x) => x.name === RESOLVED_WIDGET);
    if (isStatusText(w?.value)) {
      const msg =
        "[BKWILDCARDS build " +
        BUILD +
        "]" +
        (connected
          ? " ready — press Run"
          : " NOT ready, please wire the node to your prompt block.");
      setResolved(node, msg, { persist: false });
    }
    node.setDirtyCanvas?.(true, true);
  } catch (_) {}
}

/** Give the resolved box a taller default height so it needs no resizing. */
function ensureResolvedHeight(node) {
  const w = node?.widgets?.find((x) => x.name === RESOLVED_WIDGET);
  if (!w || w._bkHeightPatched) return;
  w._bkHeightPatched = true;
  const orig = typeof w.computeSize === "function" ? w.computeSize.bind(w) : null;
  w.computeSize = function (width) {
    const base = orig ? orig(width) : [width, 20];
    return [base[0], Math.max(base[1] || 0, RESOLVED_MIN_H)];
  };
}

/**
 * Recompute widget visibility for the current theme/gender AND per-section
 * collapse. Mirrors the Python gate in nodes._in_scope (Python stays
 * authoritative); collapse is a second, cosmetic reason to hide a section's
 * widgets. Each non-header widget belongs to the most recent header's section.
 */
function applyTheme(node, layout) {
  if (!node || !layout) return;
  try {
    const activeTheme = node.widgets?.find((w) => w.name === "theme")?.value;
    const activeGender = node.widgets?.find((w) => w.name === "gender")?.value;
    const activePack = layout.theme_to_pack?.[activeTheme];
    const byKey = new Map();
    for (const cat of layout.categories || []) byKey.set(cat.key, cat);
    const collapsed = node.properties?._bkCollapsed || {};
    // Random/Fluid show both genders' physical categories.
    const showBoth =
      activeGender === layout.gender_random ||
      activeGender === layout.gender_fluid;

    // Pass 1: category widgets gate on theme+gender; fixed widgets are always in
    // scope. Visible = in scope AND its section isn't collapsed. The output box
    // never collapses. Record `_bkInScope` on each widget for the header pass.
    let currentGroup = null;
    for (const w of node.widgets || []) {
      if (w._bkHeader) {
        currentGroup = w._bkGroup;
        continue;
      }
      if (w.name === RESOLVED_WIDGET) {
        w._bkInScope = false; // the output box is never a section member
        setHidden(w, false);
        continue;
      }
      const cat = byKey.get(w.name);
      let inScope = true;
      if (cat) {
        const themeOk = !activePack || cat.is_global || cat.pack === activePack;
        const genderOk = !cat.gender || cat.gender === activeGender || showBoth;
        inScope = themeOk && genderOk;
      }
      w._bkInScope = inScope;
      setHidden(w, !(inScope && !(currentGroup && collapsed[currentGroup])));
    }

    // Pass 2: a header shows only when ITS OWN members (up to the next header)
    // have an in-scope one — so the per-theme Wardrobe/Scene headers of inactive
    // themes stay hidden. Uses _bkInScope (not visibility) so a collapsed
    // section's header stays visible and re-expandable.
    const widgets = node.widgets || [];
    for (let i = 0; i < widgets.length; i++) {
      if (!widgets[i]._bkHeader) continue;
      let anyInScope = false;
      for (let j = i + 1; j < widgets.length; j++) {
        if (widgets[j]._bkHeader) break;
        if (widgets[j]._bkInScope) { anyInScope = true; break; }
      }
      setHidden(widgets[i], !anyInScope);
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
      if (cat) {
        widget.label = cat.label;
      } else if (FIXED_LABELS[widget.name]) {
        widget.label = FIXED_LABELS[widget.name];
      }
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

    // The resolved box is a multiline STRING widget: a DOM-widget wrapper around
    // a real <textarea>. In the ComfyUI frontend its value setter only updates
    // the widget's stored state (this._state.value) — it does NOT write the
    // element. So widget.value keeps the serialized/saved value correct, while
    // el.value is what actually changes the text on screen. Both are required;
    // setting only widget.value is exactly what made the box look frozen.
    try {
      widget.value = text; // stored / serialized value
    } catch (_) {}

    const el = widget.inputEl || widget.element || null;
    if (el && "value" in el) {
      if (el.value !== text) {
        el.value = text; // the visible update
        // Mirror the direct element write back into widget state.
        try {
          el.dispatchEvent(new Event("input", { bubbles: true }));
        } catch (_) {}
      }
      el.readOnly = true;
      el.style.opacity = "0.75";
      el.scrollTop = 0;
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

/**
 * Queue-time preview — the mechanism that makes the box change on every Run,
 * the way ImpactWildcardProcessor's populated_text does.
 *
 * Wraps the serialized prompt ComfyUI is about to send. For each selector node
 * in it, it asks the backend to resolve the SAME seed and choices and writes the
 * result into the box before generation starts. The seed is read from the
 * outgoing payload — not recomputed here — so it is the exact seed the backend
 * will run with after control_after_generate has advanced it once. The preview
 * therefore cannot show a different seed than the image uses.
 *
 * This stays cosmetic: the authoritative draw is still nodes.build() during
 * execution. If the endpoint is unreachable the box simply is not previewed and
 * the generated prompt is unaffected. The `executed` handler below cross-checks
 * that the previewed text equals what execution produced.
 */
function previewFromPrompt(promptData) {
  const output = promptData?.output;
  if (!output || typeof output !== "object") return;
  for (const id of Object.keys(output)) {
    const entry = output[id];
    if (!entry || entry.class_type !== NODE) continue;
    const inputs = entry.inputs || {};
    const seed = inputs.seed;
    // Skip if the seed was converted to a linked input (an array), not a value.
    if (typeof seed !== "number") continue;
    const node = app.graph?.getNodeById?.(Number(id));
    if (!node) continue;

    node._bkPreviewedThisCycle = true;
    setResolved(node, PENDING_TEXT, { persist: false });

    fetch("/bkwildcards/populate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        seed,
        separator: typeof inputs.separator === "string" ? inputs.separator : ", ",
        gender: inputs.gender ?? null,
        theme: inputs.theme ?? null,
        // resolve_prompt only reads the category keys out of this; extra keys
        // (seed, separator, resolved, ...) are ignored.
        choices: inputs,
      }),
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((json) => {
        if (!json || typeof json.text !== "string") return;
        node._bkPreview = json.text; // cross-checked against execution below
        setResolved(node, json.text);
        console.debug("[BKWILDCARDS] queue preview, node", id, "seed", seed,
                      "->", json.text.length, "chars");
      })
      .catch((err) => console.warn("[BKWILDCARDS] populate failed:", err));
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
  // Header clicks call this to recompute visibility (collapse/expand).
  node._bkApply = () => applyTheme(node, layout);

  relabel(node, layout);
  insertHeaders(node, layout);
  ensureResolvedHeight(node);

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

    // The live-update mechanism. Intercept the serialized prompt on its way to
    // the server and preview each selector node from the exact seed being sent,
    // so the box changes on every queue — before generation, like Impact's
    // populated_text. Fire-and-forget so queueing is never delayed.
    const origQueuePrompt = api.queuePrompt.bind(api);
    api.queuePrompt = async function (number, data) {
      try {
        previewFromPrompt(data);
      } catch (err) {
        console.warn("[BKWILDCARDS] queue preview hook failed:", err);
      }
      return origQueuePrompt(number, data);
    };

    // Fallback feedback for any node the queue preview did not fill (endpoint
    // down, seed linked as an input). Not persisted — a placeholder must never
    // be saved into a workflow or PNG.
    api.addEventListener("execution_start", () => {
      for (const node of selectorNodes()) {
        if (node._bkPreviewedThisCycle) continue; // preview already showed the text
        setResolved(node, PENDING_TEXT, { persist: false });
      }
    });

    // Authoritative text from execution. Also the acceptance check: it must
    // equal the queue-time preview. A mismatch means the preview read the wrong
    // seed — the one thing that could make the box lie — and is logged loudly.
    api.addEventListener("executed", (event) => {
      try {
        const detail = event?.detail;
        const text = detail?.output?.bk_resolved?.[0];
        if (typeof text !== "string") return;
        const node = app.graph?.getNodeById?.(Number(detail.node) || detail.node);
        if (node?.comfyClass !== NODE) return;

        if (typeof node._bkPreview === "string") {
          if (node._bkPreview === text) {
            console.debug("[BKWILDCARDS] preview matched execution ✓ (" +
                          text.length + " chars)");
          } else {
            console.warn("[BKWILDCARDS] PREVIEW ≠ EXECUTION — seed timing is wrong.\n" +
                         " preview : " + node._bkPreview.slice(0, 120) + "\n" +
                         " executed: " + text.slice(0, 120));
          }
          node._bkPreview = undefined;
        }
        node._bkPreviewedThisCycle = false;
        setResolved(node, text);
      } catch (err) {
        console.warn("[BKWILDCARDS] executed listener failed:", err);
      }
    });

    // If a run dies before this node executes, clear the placeholder rather
    // than leaving it stuck on screen.
    const clearPending = () => {
      for (const node of selectorNodes()) {
        node._bkPreviewedThisCycle = false;
        node._bkPreview = undefined;
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

    // Keep our injected header rows out of every positional widgets_values
    // read/write. Without this, saving, loading or undoing shifts every widget
    // value by the number of preceding headers. See withoutHeaders().
    for (const method of ["serialize", "configure"]) {
      const original = nodeType.prototype[method];
      if (typeof original !== "function") continue;
      nodeType.prototype[method] = function (...args) {
        return withoutHeaders(this, () => original.apply(this, args));
      };
    }

    // Red/green node + box message reflecting whether the prompt output is
    // wired. Fires on every wire add/remove (ComfyUI guards it during graph
    // load, so the explicit calls in the lifecycle hooks cover the load case).
    const onConnectionsChange = nodeType.prototype.onConnectionsChange;
    nodeType.prototype.onConnectionsChange = function (...args) {
      const r = onConnectionsChange?.apply(this, args);
      try {
        refreshConnectionState(this);
      } catch (_) {}
      return r;
    };
  },

  async nodeCreated(node) {
    if (node?.comfyClass !== NODE) return;
    setNodeTitle(node); // layout-independent — set even if the fetch fails
    refreshConnectionState(node); // colour + build-stamped ready/NOT-ready line
    const layout = await loadLayout();
    if (!layout) return;
    attach(node, layout);
    restoreResolved(node); // a stored prompt takes the box back from the status line
    applyNowAndNextFrame(node, layout);
    requestAnimationFrame(() => refreshConnectionState(node)); // after connections settle
  },

  async loadedGraphNode(node) {
    if (node?.comfyClass !== NODE) return;
    setNodeTitle(node);
    refreshConnectionState(node);
    const layout = await loadLayout();
    if (!layout) return;
    attach(node, layout);
    restoreResolved(node);
    applyNowAndNextFrame(node, layout);
    requestAnimationFrame(() => refreshConnectionState(node));
  },
});
