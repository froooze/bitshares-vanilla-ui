// probe-i18n-badge-nodom.mjs — DEV ONLY (never shipped, never required to run
// the wallet). Real-browser proof for review wave 1 / Important 1, in the one
// environment that matters: a live HTMLCollection.
//
// The Node probes model the collection with a getter-only `length`, which is
// right but is still a model. This probe runs the SHIPPED page in Chromium,
// deletes the utils/dom.js global at runtime (`window.DOM = undefined` — the
// same condition the review used), and then forces the header to repaint, so
// clearHost() takes its raw-platform fallback against a REAL node. Before the
// fix that fallback ended with `node.children.length = 0`, which throws
// TypeError on a real HTMLCollection, and the throw escaped mount() and left
// the header with no chip at all.
//
// It also asserts the precondition rather than assuming it: that the slot's
// `children` really is an HTMLCollection whose `length` cannot be written, and
// that a strict-mode write really does throw there.
//
// Usage:
//   python3 -m http.server 8099 --directory vanilla &
//   PLAYWRIGHT_BROWSERS_PATH=.browsers node tooling/visual/probe-i18n-badge-nodom.mjs \
//     --url http://localhost:8099
import { chromium } from "playwright-core";

const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, cur, i, arr) => {
    if (cur.startsWith("--")) acc.push([cur.slice(2), arr[i + 1] && !arr[i + 1].startsWith("--") ? arr[i + 1] : "1"]);
    return acc;
  }, [])
);
const URL = args.url || "http://localhost:8099";

let pass = 0, fail = 0;
function check(name, cond, extra) {
  if (cond) { pass++; console.log("ok   " + name); }
  else { fail++; console.log("FAIL " + name + " " + (extra === undefined ? "" : JSON.stringify(extra))); }
}

const errors = [];
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1024, height: 800 } });
page.on("console", (m) => { if (m.type() === "error") errors.push("console: " + m.text().slice(0, 200)); });
page.on("pageerror", (e) => errors.push("pageerror: " + String(e).slice(0, 200)));
await page.addInitScript(() => {
  try { localStorage.setItem("bts-vanilla-tour-dismissed-v1", "1"); } catch (e) {}
});
await page.goto(URL + "/#/settings/display", { waitUntil: "load" });
await page.waitForFunction(() => typeof I18n !== "undefined" && typeof I18nBadge !== "undefined" && typeof App !== "undefined");

/* Precondition: prove the page really does hand the module a live
 * HTMLCollection whose `length` is getter-only — the thing the old fallback
 * wrote to. A "use strict" directive only counts as the FIRST statement of a
 * function body, so the throw has to come from a function built with
 * new Function: a sloppy call site would silently succeed, exactly as it does
 * in utils/dom.js today. */
const pre = await page.evaluate(() => {
  const slot = document.getElementById("i18n-badge-slot");
  const probe = document.createElement("div");
  slot.appendChild(probe);
  const coll = slot.children;
  const shape = Object.prototype.toString.call(coll);
  const strictWrite = new Function("c", "'use strict'; c.length = 0;");
  let writeErr = null;
  try { strictWrite(coll); } catch (e) { writeErr = String(e && e.name); }
  slot.removeChild(probe);
  const desc = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(coll), "length");
  return { shape, writeErr, hasSetter: !!(desc && desc.set), len: coll.length };
});
console.log("     slot.children = " + pre.shape + "  length setter? " + pre.hasSetter +
  "  strict write -> " + (pre.writeErr || "NO THROW") + "  (children=" + pre.len + ")");
check("the slot's children really is a live HTMLCollection", pre.shape === "[object HTMLCollection]", pre);
check("writing HTMLCollection.length throws TypeError — the old fallback's write was fatal",
  pre.writeErr === "TypeError" && !pre.hasSetter, pre);

/* The condition: the shared DOM helper is gone. */
await page.evaluate(() => { window.DOM = undefined; });
check("window.DOM is undefined — utils/dom.js is out of the way",
  await page.evaluate(() => typeof DOM === "undefined"));

/* Machine locale + a repaint, so refresh()/clearHost() take the raw path. */
const r = await page.evaluate(() => {
  I18n._seed("es", { _meta: { version: 2, provenance: "machine", coverage: [
    "i18n.badge_chip", "i18n.badge_label", "i18n.badge_body",
    "i18n.badge_details", "i18n.badge_improve"] } });
  I18n._setCurrent("es");
  let mountThrew = null, refreshThrew = null;
  try { App.localizeShell(); } catch (e) { mountThrew = String((e && e.message) || e); }
  try { I18nBadge.refresh(); } catch (e) { refreshThrew = String((e && e.message) || e); }
  const slot = document.getElementById("i18n-badge-slot");
  const chip = slot.querySelector(".i18n-badge");
  const note = slot.querySelector(".i18n-badge-note");
  return {
    mountThrew, refreshThrew,
    visible: I18nBadge.visible(),
    children: slot.children.length,
    chipClass: chip ? chip.className : null,
    chipFace: chip ? chip.textContent : null,
    noteHidden: note ? note.hidden : null,
    chipBox: chip ? Math.round(chip.getBoundingClientRect().height) : null
  };
});
console.log("     " + JSON.stringify(r));
check("mount() (via App.localizeShell) does not throw without the DOM helper", r.mountThrew === null, r);
check("refresh() does not throw without the DOM helper", r.refreshThrew === null, r);
check("visible() is true — the chip was painted, not skipped", r.visible === true, r);
check("the slot holds exactly chip + note", r.children === 2, r);
check("the chip is the chip", r.chipClass === "i18n-badge", r);
check("the chip keeps its 44px touch floor in a real layout", r.chipBox >= 44, r);
check("and its panel starts collapsed", r.noteHidden === true, r);

/* Repaint again over the populated slot: the fallback clearHost runs for real
 * on a node that already has children. */
const again = await page.evaluate(() => {
  let threw = null;
  try { App.localizeShell(); } catch (e) { threw = String((e && e.message) || e); }
  const slot = document.getElementById("i18n-badge-slot");
  return { threw, children: slot.children.length };
});
check("re-painting over a populated slot clears and rebuilds without throwing",
  again.threw === null && again.children === 2, again);

/* And the honest inverse in the same session: English removes both nodes. */
const en = await page.evaluate(() => {
  let threw = null;
  try { I18n._setCurrent("en"); App.localizeShell(); } catch (e) { threw = String((e && e.message) || e); }
  const slot = document.getElementById("i18n-badge-slot");
  return { threw, children: slot.children.length, visible: I18nBadge.visible() };
});
check("switching to English empties the slot without throwing",
  en.threw === null && en.children === 0 && en.visible === false, en);

await browser.close();
check("no console/page errors", errors.length === 0, errors.slice(0, 6));
console.log("\ni18n-badge-nodom: " + pass + " passed, " + fail + " failed");
process.exit(fail === 0 ? 0 : 1);