/* xrate-ui.js — #/cross-rates cross-rate table (read-only pool price matrix).
 * Owns: page shell (h1, explainer, token input + column chips, status,
 *   table host, refresh, show-all expander), pool-list walk, BFS route
 *   selection, last-swap fetching for route pools only, progressive table
 *   paint, ?cols= hash sync, gen-guarded teardown. No signing, no storage
 *   writes (hash only), no broadcasts.
 * Consumes: XRate (pure matrix core), Pool.list (paged pool rows, symbols
 *   + precisions joined), PoolHistory.chainSwaps (newest op-63 per pool),
 *   Format (formatPrice + priceSig at render), DOM/TableRenderer/Forms
 *   shared globals, touchable floor. Reads MarketUI nothing; needs no
 *   account, no login.
 * Side effects: DOM under root only; WS reads (list + history batches);
 *   location hash replace on column change. Global XRateUI.
 * Created by: cross-rates slice, spec
 *   docs/superpowers/specs/2026-10-12-cross-rates-design.md.
 */
var XRateUI = (function () {
  "use strict";

  /* Batch-2d i18n: verbatim English default so file:// renders
   * identically; raw default returns unfilled without I18n. */
  function t(key, dflt, vars) {
    try {
      if (typeof I18n !== "undefined" && I18n && typeof I18n.t === "function") return I18n.t(key, dflt, vars);
    } catch (e) { /* default below */ }
    if (vars && typeof dflt === "string") {
      return dflt.replace(/%\(([^)]+)\)s/g, function (m, name) {
        return (vars && Object.prototype.hasOwnProperty.call(vars, name)) ? String(vars[name]) : m;
      });
    }
    return dflt;
  }

  var gen = 0;
  var _waitSub = false;
  /* Parallel history batches: wide enough to finish, narrow enough to be
   * polite to community nodes (candle-walk precedent). */
  var BATCH = 8;

  function touch(el) {
    try {
      if (typeof touchable === "function") { touchable(el); return el; }
    } catch (e) { /* cosmetic */ }
    return el;
  }

  /**
   * listPools: full pool walk (limit-100 pages, startId chaining; the
   * inclusive-paging duplicate is dropped pool-ui.js precedent).
   * @param {number} myGen Render token.
   * @returns {Promise<Array>} Joined pool rows (symbols + precisions).
   * Failure: rejects not-connected / upstream errors (caller renders them).
   */
  function listPools(myGen) {
    var all = [];
    function page(startId) {
      if (myGen !== gen) return Promise.reject(new Error("stale render"));
      return Pool.list({ limit: 100, startId: startId }).then(function (rows) {
        rows = rows || [];
        var fresh = rows;
        if (all.length && rows.length && String(rows[0].id) === String(all[all.length - 1].id)) {
          fresh = rows.slice(1);
        }
        all = all.concat(fresh);
        if (rows.length === 100) {
          var last = rows[rows.length - 1];
          return page(String(last.id));
        }
        return all;
      });
    }
    return page("1.19.0");
  }

  /**
   * fetchSwaps: newest op-63 per pool id, batched, failures counted.
   * @param {Array<string>} poolIds Route pools needing prices.
   * @param {number} myGen Render token.
   * @param {Function} onBatch Progress callback after each batch.
   * @returns {Promise<{byPool:Object,failures:number}>} Newest swap per pool + failure count.
   */
  function fetchSwaps(poolIds, myGen, onBatch) {
    var byPool = {}, failures = 0, i = 0;
    function batch() {
      if (myGen !== gen) return Promise.reject(new Error("stale render"));
      var slice = poolIds.slice(i, i + BATCH);
      if (!slice.length) return Promise.resolve({ byPool: byPool, failures: failures });
      i += BATCH;
      var jobs = slice.map(function (pid) {
        return PoolHistory.chainSwaps(pid, 10).then(function (res) {
          var swaps = (res && res.swaps) || [];
          for (var k = 0; k < swaps.length; k++) {
            if (swaps[k] && swaps[k].paid && swaps[k].received) { byPool[pid] = swaps[k]; break; }
          }
        }).catch(function () { failures++; });
      });
      return Promise.all(jobs).then(function () {
        try { if (typeof onBatch === "function") onBatch(); } catch (e) { /* paint stands */ }
        return batch();
      });
    }
    return batch();
  }

  /**
   * renderXRate: route entry — shell first (never blank), data progressively.
   * @param {HTMLElement} root Router mount element.
   * @returns {void} Never throws on routing (errors render inline).
   */
  function renderXRate(root) {
    if (!root) return;
    var doc = root.ownerDocument || (typeof document !== "undefined" ? document : null);
    if (!doc) return;
    var myGen = ++gen;
    var alive = function () { return myGen === gen; };
    DOM.clear(root);
    var wrap = doc.createElement("div");
    wrap.className = "wrap";
    root.appendChild(wrap);
    wrap.appendChild(DOM.pageHead(doc, t("xrate.title", "Cross Rates"), "swap"));
    wrap.appendChild(DOM.el(doc, "p",
      t("xrate.intro", "Every pool asset priced at its last swap, crossed through the pool graph. Nothing is signed and nothing is stored."),
      "muted"));

    var state = { pools: [], graph: null, bfs: null, bySym: {}, columns: ["BTS"], rows: [], shown: 40, swaps: {} };

    /* ---- controls: token input + datalist, add button, column chips ---- */
    var controls = DOM.el(doc, "div", null, "xrate-controls");
    var field = Forms.labeledInput(doc, t("xrate.token_label", "Add quote token"),
      { type: "text", placeholder: t("xrate.token_placeholder", "USD, CNY, BTC…"), autocomplete: "off", list: "xrate-syms" });
    var input = field.input;
    var list = doc.createElement("datalist");
    try { list.setAttribute("id", "xrate-syms"); } catch (e) { /* input stands alone */ }
    var addBtn = touch(DOM.el(doc, "button", t("xrate.add_btn", "Add column"), "subtle-btn"));
    try { addBtn.setAttribute("type", "button"); } catch (e2) { /* stands */ }
    var chips = DOM.el(doc, "div", null, "xrate-chips");
    controls.appendChild(field.row || input);
    controls.appendChild(list);
    controls.appendChild(addBtn);
    wrap.appendChild(controls);
    wrap.appendChild(chips);

    var status = DOM.el(doc, "p", t("xrate.loading", "Reading pools…"), "muted an-status");
    try { status.setAttribute("aria-live", "polite"); } catch (e3) { /* stands */ }
    wrap.appendChild(status);
    var host = DOM.el(doc, "div", null, "xrate-scroll");
    wrap.appendChild(host);
    var foot = DOM.el(doc, "div", null, "xrate-foot");
    var refreshBtn = touch(DOM.el(doc, "button", t("xrate.refresh_btn", "Refresh prices"), "subtle-btn"));
    try { refreshBtn.setAttribute("type", "button"); } catch (e4) { /* stands */ }
    var moreBtn = touch(DOM.el(doc, "button", t("xrate.show_all", "Show all assets"), "subtle-btn"));
    try { moreBtn.setAttribute("type", "button"); } catch (e5) { /* stands */ }
    moreBtn.style.display = "none";
    foot.appendChild(refreshBtn);
    foot.appendChild(moreBtn);
    wrap.appendChild(foot);

    function syncHash() {
      if (!alive()) return;
      try {
        var next = XRate.hashFor(state.columns);
        if (typeof location === "undefined") return;
        if (location.hash === next) return;
        if (typeof history !== "undefined" && history && typeof history.replaceState === "function") {
          history.replaceState(null, "", next);
          return;
        }
      } catch (e) { /* keep the current url */ }
      try { if (typeof location !== "undefined") location.hash = next; } catch (e2) { /* stands */ }
    }

    function paintChips() {
      if (!alive()) return;
      DOM.clear(chips);
      state.columns.forEach(function (sym) {
        var chip = DOM.el(doc, "span", sym, "xrate-chip");
        if (sym !== "BTS") {
          var x = DOM.el(doc, "button", t("xrate.remove_btn", "Remove ") + sym);
          try { x.setAttribute("type", "button"); } catch (e) { /* stands */ }
          touch(x);
          x.addEventListener("click", function () {
            state.columns = state.columns.filter(function (s) { return s !== sym; });
            syncHash();
            paintChips();
            paintTable();
          });
          chip.appendChild(x);
        } else {
          chip.title = t("xrate.base_pinned", "BTS is the base column and cannot be removed.");
        }
        chips.appendChild(chip);
      });
    }

    /* fracs: exact per-asset rationals (asset-per-BTS) from BTS-rooted
     * routes. A cell rate(row X, column C) = fracX / fracC — exact in raw
     * space, one shared anchor like forex crosses via USD. Diagonal falls
     * out as exactly 1 with no special case. */
    /* toLeg: chain swap row + pool-joined precisions -> XRate leg shape.
     * Precisions come from the pool list join (chainSwaps carries amounts
     * + ids only); a leg whose precision is unknown is unusable — the core
     * reports it unpriced, never assumed. */
    function toLeg(poolId, fromId, toId, sw) {
      if (!sw || !sw.paid || !sw.received) return null;
      var paidId = String(sw.paid.asset), recvId = String(sw.received.asset);
      var paidPrec = state.prec[paidId], recvPrec = state.prec[recvId];
      if (typeof paidPrec !== "number" || typeof recvPrec !== "number") return null;
      return { pool: poolId, from: fromId, to: toId, swap: {
        paidRaw: String(sw.paid.amount), paidId: paidId, paidPrec: paidPrec,
        recvRaw: String(sw.received.amount), recvId: recvId, recvPrec: recvPrec } };
    }

    function fracFor(assetId) {
      if (assetId === XRate.BTS_ID) return { num: "1", den: "1" };
      var legs = XRate.routeTo(state.graph, state.bfs, assetId) || [];
      if (!legs.length) return null;
      var withSwaps = [];
      for (var i = 0; i < legs.length; i++) {
        var leg = toLeg(legs[i].pool, legs[i].from, legs[i].to, state.swaps[legs[i].pool]);
        if (!leg) return null;
        withSwaps.push(leg);
      }
      return XRate.pathFraction(withSwaps);
    }

    /* cellFor: one matrix cell -> {text, pool, title}. rate(row X, col C)
     * = fracX / fracC, exact in raw space. Anything unresolvable reports
     * WHY (unpriced leg, out-of-scope column). */
    function cellFor(rowId, colSym, colId) {
      var fx = fracFor(rowId), fc = fracFor(colId);
      if (!fx || !fc) {
        var why = !fx
          ? t("xrate.unpriced", "A leg on this route has no recorded swap yet.")
          : t("xrate.no_route_col", "No route to %(sym)s within 6 pool hops.", { sym: colSym });
        return { text: "—", pool: null, title: why };
      }
      var num, den;
      try {
        num = (BigInt(fx.num) * BigInt(fc.den)).toString();
        den = (BigInt(fx.den) * BigInt(fc.num)).toString();
      } catch (e) {
        return { text: "—", pool: null, title: t("xrate.unpriced", "A leg on this route has no recorded swap yet.") };
      }
      var places = XRate.placesFor(num, den);
      var text;
      try {
        text = Format.priceSig(Format.formatPrice(num, 0, den, 0, places));
      } catch (e2) {
        return { text: "—", pool: null, title: t("xrate.unpriced", "A leg on this route has no recorded swap yet.") };
      }
      /* Click target: first pool on the BTS->row path (the actionable
       * start of a swap journey); the full both-sided route rides along. */
      var rowLegs = XRate.routeTo(state.graph, state.bfs, rowId) || [];
      var colLegs = (colId === XRate.BTS_ID) ? [] : (XRate.routeTo(state.graph, state.bfs, colId) || []);
      var routeTxt = "via " + rowLegs.map(function (l) { return l.pool + " " + l.from + "→" + l.to; }).join(" · ");
      if (colLegs.length) {
        routeTxt += " / " + colLegs.map(function (l) { return l.pool + " " + l.from + "→" + l.to; }).join(" · ");
      }
      return { text: text, pool: rowLegs.length ? rowLegs[0].pool : null, title: routeTxt };
    }

    function paintTable() {
      if (!alive()) return;
      DOM.clear(host);
      if (!state.rows.length) {
        host.appendChild(DOM.el(doc, "p",
          t("xrate.empty", "No pool assets within 3 hops of BTS on this chain."),
          "muted"));
        return;
      }
      var cols = [{ key: "asset", title: t("xrate.asset_col", "Asset") }];
      state.columns.forEach(function (sym) {
        cols.push({ key: "c_" + sym, title: sym, align: "right" });
      });
      var idOf = {};
      Object.keys(state.bySym).forEach(function (sym) { idOf[sym] = state.bySym[sym]; });
      var rows = state.rows.slice(0, state.shown).map(function (r) {
        var row = { asset: r.sym, id: r.id };
        state.columns.forEach(function (sym) {
          var cid = (sym === "BTS") ? XRate.BTS_ID : idOf[sym];
          var cell = (!cid) ? { text: "—", pool: null, title: "" } : cellFor(r.id, sym, cid);
          row["c_" + sym] = cell.text;
          row["c_" + sym + "__pool"] = cell.pool;
          row["c_" + sym + "__title"] = cell.title;
        });
        return row;
      });
      var table;
      try {
        table = TableRenderer.render({ columns: cols, rows: rows,
          keyExtractor: function (r) { return r.id || ""; },
          stickyFirstCol: true });
      } catch (e) { status.textContent = String((e && e.message) || e); return; }
      /* Cells link to their pool (keyboard + touch + mouse for free):
       * wrap priced text in anchors carrying the route in the title.
       * Self cells take the measured diagonal fill. */
      try {
        var trs = table.querySelectorAll("tbody tr");
        for (var i = 0; i < trs.length; i++) {
          var tds = trs[i].querySelectorAll("td");
          for (var j = 1; j < tds.length; j++) {
            var key = cols[j].key;
            if (rows[i].asset === key.slice(2)) {
              tds[j].className = (tds[j].className + " xrate-diag").trim();
              continue;
            }
            var pool = rows[i][key + "__pool"], title = rows[i][key + "__title"];
            if (pool) {
              var a = doc.createElement("a");
              a.setAttribute("href", "#/pools/" + pool);
              a.textContent = tds[j].textContent;
              if (title) a.title = title;
              DOM.clear(tds[j]);
              tds[j].appendChild(a);
            } else if (title) {
              tds[j].title = title;
            }
          }
          /* Row header links to the asset page. */
          (function () {
            var first = tds[0];
            var sym = rows[i].asset;
            var a0 = doc.createElement("a");
            a0.setAttribute("href", "#/asset/" + sym);
            a0.textContent = first.textContent;
            DOM.clear(first);
            first.appendChild(a0);
          })();
        }
        /* Hover crosshair (measured widget behavior): the hovered cell's
         * row header, column header, and cell share one tint. Mouse-only
         * enhancement — touch and keyboard never need it. */
        (function () {
          function clearHot() {
            var hot = table.querySelectorAll(".xrate-hot");
            for (var k = 0; k < hot.length; k++) {
              hot[k].className = hot[k].className.replace(/(^|\s)xrate-hot(\s|$)/, " ").trim();
            }
          }
          function mark(el) {
            if (!el) return;
            el.className = (el.className + " xrate-hot").trim();
          }
          table.addEventListener("mouseover", function (ev) {
            var t = null;
            try { t = ev && ev.target && ev.target.closest ? ev.target.closest("td,th") : null; } catch (e) { t = null; }
            if (!t || !table.contains(t)) { clearHot(); return; }
            clearHot();
            mark(t);
            var tr = t.parentNode;
            if (tr && tr.children && tr.children.length) mark(tr.children[0]);
            var cells = tr ? tr.children : [];
            var idx = -1;
            for (var c = 0; c < cells.length; c++) { if (cells[c] === t) { idx = c; break; } }
            if (idx < 0) return;
            try {
              var heads = table.querySelectorAll("thead th");
              if (heads[idx]) mark(heads[idx]);
            } catch (e2) { /* cell tint stands */ }
          });
          table.addEventListener("mouseleave", clearHot);
        })();
      } catch (e2) { /* plain-text table stands */ }
      host.appendChild(table);
      var total = state.rows.length;
      moreBtn.style.display = (state.shown < total) ? "" : "none";
      try {
        moreBtn.textContent = t("xrate.show_all", "Show all assets") + " (" + total + ")";
      } catch (e3) { /* stands */ }
    }

    function refreshStatus(done, total) {
      if (!alive()) return;
      DOM.text(status, t("xrate.status", "%(pools)s pools · %(assets)s assets within 3 hops · %(done)s of %(total)s pools hold a last swap",
        { pools: String(state.pools.length), assets: String(state.rows.length),
          done: String(done), total: String(total) }));
    }

    /* Route pools needing swaps: union over kept + expander rows AND
     * current columns (column routes run to 6 hops). */
    function routePoolUnion() {
      var need = {}, order = [];
      function needRoute(id) {
        if (!id || id === XRate.BTS_ID) return;
        var legs = XRate.routeTo(state.graph, state.bfs, id) || [];
        legs.forEach(function (l) {
          if (!need[l.pool]) { need[l.pool] = 1; order.push(l.pool); }
        });
      }
      state.rows.forEach(function (r) { needRoute(r.id); });
      state.columns.forEach(function (sym) {
        if (sym !== "BTS" && state.bySym[sym]) needRoute(state.bySym[sym]);
      });
      return order;
    }
    /* fetchMissing: swaps for route pools not yet attempted this draw
     * (success AND failure both count as attempted — a dead pool is not
     * retried every repaint). Progressive repaint per batch. */
    function fetchMissing() {
      var order = routePoolUnion().filter(function (pid) { return !state.fetched[pid]; });
      state.poolTotal = (state.poolTotal || 0) + order.length;
      var i = 0;
      function batch() {
        if (!alive()) return Promise.resolve();
        var slice = order.slice(i, i + BATCH);
        if (!slice.length) return Promise.resolve();
        i += BATCH;
          var jobs = slice.map(function (pid) {
            return PoolHistory.chainSwaps(pid, 10).then(function (res) {
              var swaps = (res && res.swaps) || [];
              for (var k = 0; k < swaps.length; k++) {
                if (swaps[k] && swaps[k].paid && swaps[k].received) {
                  state.swaps[pid] = swaps[k];
                  state.priced++;
                  break;
                }
              }
              state.fetched[pid] = 1;
            }).catch(function () { state.fetched[pid] = 1; });
          });
          return Promise.all(jobs).then(function () {
            if (!alive()) return;
            paintTable();
            refreshStatus(state.priced, state.poolTotal || 0);
            return batch();
          });
      }
      return batch();
    }

    function addColumn() {
      var raw = "";
      try { raw = String(input.value || "").trim().toUpperCase(); } catch (e) { raw = ""; }
      if (!raw) return;
      if (!state.bySym[raw]) {
        status.textContent = t("xrate.unknown_token", "No pool asset named %(sym)s.", { sym: raw });
        return;
      }
      state.columns = XRate.normalizeColumns(state.columns.concat([raw]), symSet());
      try { input.value = ""; } catch (e2) { /* stands */ }
      syncHash();
      paintChips();
      draw(false);
    }

    function symSet() {
      var s = {};
      Object.keys(state.bySym).forEach(function (k) { s[k] = 1; });
      s.BTS = 1;
      return s;
    }

    /* draw: full reload (pools -> routes -> swaps -> paint). refetch=false
     * repaints from cache, then fetches any route pools the new columns
     * still need (column add/remove path — never a full reload). */
    function draw(refetch) {
      if (!alive()) return;
      if (refetch === false && state.graph) {
        paintTable();
        refreshStatus(state.priced || 0, state.poolTotal || 0);
        fetchMissing();
        return;
      }
      status.textContent = t("xrate.loading", "Reading pools…");
      DOM.clear(host);
      listPools(gen).then(function (pools) {
        if (!alive()) return;
        state.pools = pools || [];
        var edges = state.pools.map(function (p) {
          return { id: p.id, a: p.asset_a_id, b: p.asset_b_id };
        });
        state.graph = XRate.buildGraph(edges);
        /* One BFS to depth 6 covers both rows (filtered to ≤3 below) and
         * user columns (any pool-network token, routes to 6 hops). */
        state.bfs = XRate.bfs(state.graph, XRate.BTS_ID, 6);
        /* Symbol + precision index from joined pool rows. */
        state.bySym = {};
        state.prec = {};
        state.pools.forEach(function (p) {
          [["sym_a", "asset_a_id", "prec_a"], ["sym_b", "asset_b_id", "prec_b"]].forEach(function (t3) {
            var sym = p[t3[0]], id = p[t3[1]], prec = p[t3[2]];
            if (sym && id && !state.bySym[sym]) state.bySym[sym] = id;
            if (id && typeof prec === "number" && state.prec[id] === undefined) state.prec[id] = prec;
          });
        });
        /* Datalist suggestions = every pool-network symbol. */
        try {
          DOM.clear(list);
          Object.keys(state.bySym).sort().forEach(function (sym) {
            var o = doc.createElement("option");
            o.value = sym;
            list.appendChild(o);
          });
        } catch (e) { /* input stands alone */ }
        /* Candidate rows: in-scope (≤3 hops) assets with a joined symbol. */
        var cands = [];
        Object.keys(state.bfs.depth || {}).forEach(function (id) {
          if (id === XRate.BTS_ID) return;
          if (state.bfs.depth[id] > XRate.MAX_DEPTH) return;
          var sym = null, found = null;
          Object.keys(state.bySym).forEach(function (s) {
            if (state.bySym[s] === id && !found) { sym = s; found = 1; }
          });
          if (!sym) return;
          cands.push({ id: id, sym: sym, hops: state.bfs.depth[id], newest: "" });
        });
        /* BTS leads the table; its diagonal computes to exactly one. */
        state.rows = [{ id: XRate.BTS_ID, sym: "BTS", hops: 0, newest: "" }].concat(
          XRate.rankRows(cands));
        state.columns = XRate.normalizeColumns(state.columns, symSet());
        paintChips();
        state.priced = 0;
        state.fetched = {};
        state.swaps = {};
        refreshStatus(0, state.poolTotal || 0);
        paintTable();
        return fetchMissing().then(function () {
          if (!alive()) return;
          /* One honest re-sort now that swap times exist: rows re-sort
           * once, then stay put (no reshuffling under the eye). */
          var head = state.rows[0];
          state.rows = [head].concat(XRate.rankRows(state.rows.slice(1).map(function (r) {
            var legs = XRate.routeTo(state.graph, state.bfs, r.id) || [];
            var newest = "";
            legs.forEach(function (l) {
              var sw = state.swaps[l.pool];
              if (sw && sw.time && (!newest || sw.time > newest)) newest = sw.time;
            });
            r.newest = newest;
            return r;
          })));
          paintTable();
          refreshStatus(state.priced, state.poolTotal || 0);
        });
      }).catch(function (e) {
        if (!alive()) return;
        /* Honest errors: only connectivity maps to the offline panel. Any
         * other failure shows its real message — calling a code bug
         * "network unavailable" would send the user fixing the wrong thing. */
        var msg = String((e && e.message) || e || "");
        if (msg.indexOf("not-connected") !== -1) {
          status.textContent = t("common.network_unavailable", "Network unavailable. Check Settings → Nodes and retry.");
        } else if (msg.indexOf("stale render") !== -1) {
          return;
        } else {
          status.textContent = t("xrate.load_failed", "Could not load cross rates: ") + msg;
        }
        var retry = touch(DOM.el(doc, "button", t("xrate.retry_btn", "Retry"), "subtle-btn"));
        try { retry.setAttribute("type", "button"); } catch (e2) { /* stands */ }
        retry.addEventListener("click", function () { draw(true); });
        host.appendChild(retry);
      });
    }

    /* ---- wire controls ---- */
    addBtn.addEventListener("click", addColumn);
    try {
      input.addEventListener("keydown", function (ev) {
        if (ev && ev.key === "Enter") { ev.preventDefault(); addColumn(); }
      });
    } catch (e) { /* button stands */ }
    refreshBtn.addEventListener("click", function () { draw(true); });
    moreBtn.addEventListener("click", function () {
      state.shown = state.rows.length;
      paintChips();
      paintTable();
      refreshStatus(state.priced || 0, state.poolTotal || 0);
    });

    /* ---- boot: ?cols= first, else BTS alone ---- */
    try {
      var h = (typeof location !== "undefined" && location.hash) || "";
      var parsed = XRate.parseColumns(h);
      if (parsed.length) state.columns = ["BTS"].concat(parsed.filter(function (s) { return s !== "BTS"; }));
    } catch (e) { /* BTS stands */ }
    paintChips();
    /* Connect gate (pool-ui routeReady precedent): the route can render
     * before the socket opens — drawing into a closed socket fails every
     * pool call with not-connected. Wait for open once, then draw. */
    (function drawWhenOpen() {
      var open = true;
      try {
        if (typeof Chain !== "undefined" && Chain && typeof Chain.status === "function") {
          var st = Chain.status();
          open = !st || st.state === "open";
        }
      } catch (e) { open = true; }
      if (open || _waitSub) { if (open) draw(true); return; }
      _waitSub = true;
      status.textContent = t("common.status_connecting", "Connecting to network…");
      try {
        if (typeof Store !== "undefined" && Store && typeof Store.subscribe === "function") {
          var off = Store.subscribe("connection", function (cst) {
            if (!cst || cst.state !== "open") return;
            _waitSub = false;
            try { if (typeof off === "function") off(); } catch (e2) { /* single-shot */ }
            if (alive()) draw(true);
          });
          return;
        }
      } catch (e3) { /* button path below covers */ }
      _waitSub = false;
      draw(true);
    })();
  }

  return { renderXRate: renderXRate };
})();

if (typeof globalThis !== "undefined" && typeof globalThis.XRateUI === "undefined") { globalThis.XRateUI = XRateUI; }
if (typeof module !== "undefined") { module.exports = XRateUI; }
