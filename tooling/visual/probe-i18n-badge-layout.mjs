// probe-i18n-badge-layout.mjs — DEV ONLY (never shipped, never required to run
// the wallet). Browser proof for review wave 1 / Minor 5: moving
// #i18n-badge-slot after #nav-toggle and deleting the note's `order: 9` must
// (a) add NO header row and no overflow, and (b) leave DOM order == visual
// order at every width, note closed and open — including where the bar WRAPS.
//
// Why a browser and not the Node harness: the property under test is flex
// layout — wrapping, `display: contents` participation, and whether removing
// `order: 9` actually keeps the note where it belongs. None of that exists
// outside a layout engine.
//
// Usage:
//   python3 -m http.server 8099 --directory vanilla &
//   PLAYWRIGHT_BROWSERS_PATH=.browsers node tooling/visual/probe-i18n-badge-layout.mjs \
//     --url http://localhost:8099
import { chromium } from "playwright-core";

const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, cur, i, arr) => {
    if (cur.startsWith("--")) acc.push([cur.slice(2), arr[i + 1] && !arr[i + 1].startsWith("--") ? arr[i + 1] : "1"]);
    return acc;
  }, [])
);
const URL = args.url || "http://localhost:8099";
const WIDTHS = [360, 768, 1440, 2560];

/* coverage is seeded so the chip's own five strings are allowlisted (v2 gate,
 * i18n.js:58-65) — otherwise the panel would render the key ids, which is a
 * different (already pinned) concern than layout. See paint() below. */

let pass = 0, fail = 0;
function check(name, cond, extra) {
  if (cond) { pass++; console.log("ok   " + name); }
  else { fail++; console.log("FAIL " + name + " " + (extra === undefined ? "" : JSON.stringify(extra))); }
}

const errors = [];
const browser = await chromium.launch();

/* The rendered flex items of .topbar in DOM order. The slot is
 * display:contents, so it is not a flex item itself — its children (the chip,
 * and the note once expanded) join the bar in its place. display:none items
 * (a JS-added hidden link) are skipped: they have no box and no place in a
 * reading order.
 *
 * Reading order is computed by ROW, not by raw `top`: the bar is align-items
 * :center, so a tall panel and a 44px chip on the SAME flex line have very
 * different top edges. Items are clustered by their vertical CENTER (flex
 * centres every line item on the line's middle) and each line is read
 * left-to-right. Sorting on `top` alone would report a one-line bar as two
 * rows — which is exactly the kind of false signal this probe exists to avoid. */
const MEASURE = `(() => {
  const bar = document.querySelector("header.topbar");
  const out = [];
  bar.childNodes.forEach((node) => {
    if (node.nodeType !== 1) return;
    if (node.id === "i18n-badge-slot") {
      node.childNodes.forEach((kid) => {
        if (kid.nodeType !== 1) return;
        const r = kid.getBoundingClientRect();
        out.push({ label: kid.className || kid.tagName, rendered: r.width > 0, mid: Math.round((r.top + r.bottom) / 2), left: Math.round(r.left) });
      });
    } else {
      const r = node.getBoundingClientRect();
      out.push({ label: node.id || node.className || node.tagName, rendered: r.width > 0, mid: Math.round((r.top + r.bottom) / 2), left: Math.round(r.left) });
    }
  });
  const shown = out.filter((x) => x.rendered);
  const lines = [];
  shown.slice().sort((a, b) => a.mid - b.mid).forEach((x) => {
    const line = lines[lines.length - 1];
    if (line && Math.abs(x.mid - line.mid) <= 4) { line.items.push(x); line.mid = (line.mid * (line.items.length - 1) + x.mid) / line.items.length; }
    else lines.push({ mid: x.mid, items: [x] });
  });
  const byVisual = [];
  lines.forEach((l) => l.items.sort((a, b) => a.left - b.left).forEach((x) => byVisual.push(x)));
  const note = document.querySelector(".i18n-badge-note");
  const chip = document.querySelector(".i18n-badge");
  return {
    domSeq: shown.map((x) => x.label),
    visual: byVisual.map((x) => x.label),
    rows: lines.length,
    barHeight: Math.round(bar.getBoundingClientRect().height),
    barOverflow: bar.scrollWidth - bar.clientWidth,
    pageOverflow: document.documentElement.scrollWidth - window.innerWidth,
    chip: !!chip,
    noteVisible: !!note && !note.hidden,
    noteLine: byVisual.findIndex((x) => x.label === "i18n-badge-note"),
    chipLine: byVisual.findIndex((x) => x.label === "i18n-badge")
  };
})()`;

async function paint(width, { machine, openNote }) {
  const page = await browser.newPage({ viewport: { width, height: 900 } });
  page.on("console", (m) => { if (m.type() === "error") errors.push(width + "px console: " + m.text().slice(0, 200)); });
  page.on("pageerror", (e) => errors.push(width + "px pageerror: " + String(e).slice(0, 200)));
  try { page.on("unhandledrejection", (r) => errors.push(width + "px unhandled: " + String(r).slice(0, 200))); } catch (e) {}
  await page.addInitScript(() => {
    try { localStorage.setItem("bts-vanilla-tour-dismissed-v1", "1"); } catch (e) {}
  });
  await page.goto(URL + "/#/settings/display", { waitUntil: "load" });
  await page.waitForFunction(() => typeof I18n !== "undefined" && typeof I18nBadge !== "undefined" && typeof App !== "undefined");
  /* Reach the machine path through the SHIPPED test seams (i18n.js:291-292),
   * the same way probe-i18n-badge.mjs does — no storage rewriting. Note the
   * argument is a BOOLEAN, not the dict as a string: Playwright evaluates a
   * string argument as an expression, which is how the seed silently vanishes. */
  await page.evaluate((wantMachine) => {
    if (wantMachine) {
      I18n._seed("es", { _meta: { version: 2, provenance: "machine", coverage: [
        "i18n.badge_chip", "i18n.badge_label", "i18n.badge_body",
        "i18n.badge_details", "i18n.badge_improve"] } });
    }
    I18n._setCurrent("es");
    App.localizeShell();
  }, machine);
  if (openNote) {
    await page.click(".i18n-badge");
    await page.waitForFunction(() => { const n = document.querySelector(".i18n-badge-note"); return n && !n.hidden; });
  }
  const m = await page.evaluate(MEASURE);
  await page.close();
  return m;
}

for (const width of WIDTHS) {
  /* Baseline: the same header in a locale with NO chip (the shipped v1 dicts
   * are all human/unreadable, which is the zero-pixel promise). Whatever row
   * count this bar needs is pre-existing — the slot move must not add to it. */
  const bare = await paint(width, { machine: false, openNote: false });
  const closed = await paint(width, { machine: true, openNote: false });
  const opened = await paint(width, { machine: true, openNote: true });

  check(width + "px machine locale paints the chip", closed.chip === true, closed);
  check(width + "px CLOSED: no chip in the baseline (zero-pixel promise)", bare.chip === false, bare);
  check(width + "px CLOSED: the chip adds NO header row",
    closed.rows === bare.rows && closed.barHeight === bare.barHeight,
    { bare: { rows: bare.rows, h: bare.barHeight }, chip: { rows: closed.rows, h: closed.barHeight } });
  check(width + "px CLOSED: no overflow", closed.barOverflow <= 0 && closed.pageOverflow <= 0,
    { barOverflow: closed.barOverflow, pageOverflow: closed.pageOverflow });
  check(width + "px OPEN: note visible", opened.noteVisible === true, opened);
  check(width + "px OPEN: no overflow", opened.barOverflow <= 0 && opened.pageOverflow <= 0,
    { barOverflow: opened.barOverflow, pageOverflow: opened.pageOverflow });
  /* The point of Minor 5: with the slot LAST and no `order:`, flex lays the
   * items out in DOM sequence across however many rows it wraps to. */
  check(width + "px OPEN: visual order === DOM order",
    JSON.stringify(opened.visual) === JSON.stringify(opened.domSeq),
    { domSeq: opened.domSeq, visual: opened.visual });
  check(width + "px OPEN: the note reads after the chip (never above it)",
    opened.noteLine > opened.chipLine, { visual: opened.visual });
  console.log("     " + width + "px rows=" + bare.rows + "/" + closed.rows + "/" + opened.rows +
    "  barH=" + bare.barHeight + "/" + closed.barHeight + "/" + opened.barHeight +
    "  order=" + opened.visual.join(" > "));
}

await browser.close();
check("no console/page errors at any width", errors.length === 0, errors.slice(0, 6));
console.log("\ni18n-badge-layout: " + pass + " passed, " + fail + " failed");
process.exit(fail === 0 ? 0 : 1);