// probe-i18n-badge.mjs — DEV ONLY (never shipped, never required to run the
// wallet). Browser proof for the Task 5 header honesty chip, at both ends of
// the range (principle #7): a 1440px desk and a 360px phone, in all three
// themes, with the console watched.
//
// The shipped dicts are still v1 (no _meta.provenance), so the chip correctly
// shows for NOTHING yet — that IS the first assertion. To reach the machine
// path we use the shipped test seams (I18n._seed/_setCurrent, App.localizeShell)
// rather than faking storage, so the probe drives the real code path.
//
// Usage: python3 -m http.server 8099 --directory vanilla &
//   node tooling/visual/probe-i18n-badge.mjs --url http://localhost:8099
import { chromium } from "playwright-core";
import fs from "node:fs";

const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, cur, i, arr) => {
    if (cur.startsWith("--")) acc.push([cur.slice(2), arr[i + 1] && !arr[i + 1].startsWith("--") ? arr[i + 1] : "1"]);
    return acc;
  }, [])
);
const URL = args.url || "http://localhost:8099";
const OUT = args.out || "/tmp/i18n-badge";
fs.mkdirSync(OUT, { recursive: true });

let pass = 0, fail = 0;
function check(name, cond, extra) {
  if (cond) { pass++; console.log("ok   " + name); }
  else { fail++; console.log("FAIL " + name + " " + (extra === undefined ? "" : JSON.stringify(extra).slice(0, 300))); }
}

const errors = [];
const browser = await chromium.launch();

/* The machine-filled dict the probe seeds. Only _meta matters to
 * I18n.provenance(): version 2 + provenance "machine" (i18n.js:95-100). */
/* Playwright only forwards an argument to a REAL function, not to a string
 * expression (a string arg is evaluated as-is and the arg is silently
 * dropped — which reads as "the seed did nothing"). */
async function seed(page, code, prov) {
  await page.evaluate(({ code, prov }) => {
    I18n._seed(code, { _meta: { version: 2, provenance: prov, coverage: [] } });
    I18n._setCurrent(code);
    App.localizeShell();
  }, { code, prov });
}

async function open(width, height, theme) {
  const page = await browser.newPage({ viewport: { width, height } });
  page.on("console", (m) => { if (m.type() === "error") errors.push("console: " + m.text().slice(0, 200)); });
  page.on("pageerror", (e) => errors.push("pageerror: " + String(e).slice(0, 200)));
  try { page.on("unhandledrejection", (r) => errors.push("unhandled: " + String(r).slice(0, 200))); } catch (e) {}
  if (theme) {
    await page.addInitScript((t) => {
      try {
        const raw = localStorage.getItem("bts-vanilla-settings-v1");
        const s = raw ? JSON.parse(raw) : {};
        s.theme = t;
        localStorage.setItem("bts-vanilla-settings-v1", JSON.stringify(s));
        localStorage.setItem("bts-vanilla-tour-dismissed-v1", "1");
      } catch {}
    }, theme);
  }
  await page.goto(URL + "/#/settings", { waitUntil: "load" });
  await page.waitForTimeout(2500);
  return page;
}

const state = (page) => page.evaluate(() => {
  const slot = document.getElementById("i18n-badge-slot");
  const chip = document.querySelector(".i18n-badge");
  const note = document.querySelector(".i18n-badge-note");
  const r = (el) => { if (!el) return null; const b = el.getBoundingClientRect();
    return { x: Math.round(b.x), y: Math.round(b.y), w: Math.round(b.width), h: Math.round(b.height),
             right: Math.round(b.right), bottom: Math.round(b.bottom) }; };
  return {
    slotChildren: slot ? slot.children.length : -1,
    chip: r(chip),
    note: r(note),
    noteHidden: note ? !!note.hidden : null,
    expanded: chip ? chip.getAttribute("aria-expanded") : null,
    chipText: chip ? chip.textContent : null,
    chipLabel: chip ? chip.getAttribute("aria-label") : null,
    chipMin: chip ? getComputedStyle(chip).minHeight : null,
    noteText: note ? note.innerText : null,
    noteWidth: note ? getComputedStyle(note).maxWidth : null,
    nav: r(document.getElementById("nav")),
    view: r(document.getElementById("view")),
    scrollW: document.documentElement.scrollWidth,
    innerW: window.innerWidth,
    links: Array.from(document.querySelectorAll(".i18n-badge-link")).map((a) => a.getAttribute("href")),
    lang: document.documentElement.getAttribute("lang"),
    /* the honesty surface the chip must agree with */
    riskActive: typeof RiskText !== "undefined" ? RiskText.isActive() : null
  };
});

/* 1. English: nothing in the DOM at all. */
const desk = await open(1440, 900, "ref-ui-theme");
let s = await state(desk);
check("en: the slot has no children", s.slotChildren === 0, s);
check("en: no chip element exists", s.chip === null, s);
check("en: visible() is false", await desk.evaluate(() => I18nBadge.visible()) === false);
await desk.screenshot({ path: OUT + "/desk-en.png" });
await desk.close();

/* 2. Human-reviewed v2 dict: still nothing (the chip is not "not English",
 * it is "machine-filled"). */
const human = await open(1440, 900, "ref-ui-theme");
await seed(human, "es", "human");
s = await state(human);
check("human v2: the slot stays empty", s.slotChildren === 0, s);
await human.close();

/* 3. Machine dict: the chip appears and expands, on all three themes. */
for (const theme of ["ref-ui-theme", "dex-ux-theme", "vanilla-ui-theme"]) {
  const page = await open(1440, 900, theme);
  await seed(page, "es", "machine");
  s = await state(page);
  check(theme + ": slot holds chip + note", s.slotChildren === 2, s);
  check(theme + ": chip is collapsed", s.expanded === "false" && s.noteHidden === true, s);
  check(theme + ": chip text is the keyed label", s.chipText === "i18n", s);
  check(theme + ": chip has an accessible name", !!s.chipLabel && s.chipLabel.length > 10, s);
  check(theme + ": chip meets the 44px touch floor", s.chipMin === "44px", s);
  check(theme + ": the two routes are real hrefs",
    s.links.length === 2 && s.links[0] === "#/help/translation-limitations"
    && /issues\/new\?labels=translation/.test(s.links[1]), s);
  check(theme + ": RiskText agrees the locale is machine", s.riskActive === true, s);
  /* expand by tap (a real click, through the delegated binder) */
  await page.click(".i18n-badge");
  await page.waitForTimeout(250);
  const openState = await state(page);
  check(theme + ": tap expands the note", openState.expanded === "true" && openState.noteHidden === false, openState);
  check(theme + ": note text is the keyed warning",
    /machine/i.test(openState.noteText || "") && /English/i.test(openState.noteText || ""), openState.noteText);
  check(theme + ": the expanded note covers NEITHER the nav NOR the page",
    openState.note.bottom <= openState.nav.y + 1 && openState.note.bottom <= openState.view.y + 1,
    { note: openState.note, nav: openState.nav, view: openState.view });
  check(theme + ": no horizontal overflow", openState.scrollW <= openState.innerW, openState);
  await page.screenshot({ path: OUT + "/desk-machine-" + theme + ".png", fullPage: false });
  await page.click(".i18n-badge");
  await page.waitForTimeout(150);
  const closed = await state(page);
  check(theme + ": second tap collapses (chip remains — not dismissible)",
    closed.expanded === "false" && closed.noteHidden === true && closed.slotChildren === 2, closed);
  await page.close();
}

/* 4. 360px phone: the note takes its own row, covers nothing, stays in frame. */
const phone = await open(360, 740, "ref-ui-theme");
await seed(phone, "es", "machine");
s = await state(phone);
check("360px: chip present", s.slotChildren === 2, s);
check("360px: no horizontal overflow with the chip", s.scrollW <= s.innerW, s);
await phone.click(".i18n-badge");
await phone.waitForTimeout(250);
const p2 = await state(phone);
check("360px: tap expands", p2.expanded === "true" && p2.noteHidden === false, p2);
check("360px: the note fits the viewport", p2.note.x >= 0 && p2.note.right <= p2.innerW, p2);
check("360px: the note does not cover the nav", p2.note.bottom <= p2.nav.y + 1, { note: p2.note, nav: p2.nav });
check("360px: the note does not cover the page", p2.note.bottom <= p2.view.y + 1, { note: p2.note, view: p2.view });
check("360px: the note is not wider than the bar", p2.note.w <= p2.innerW, p2);
await phone.screenshot({ path: OUT + "/phone-machine.png" });
await phone.close();

/* 5. Locale switch back to English empties it again (the paint path app.js
 *    uses — App.localizeShell on every locale change). */
const back = await open(1440, 900, "ref-ui-theme");
await seed(back, "es", "machine");
await back.evaluate(() => { I18n._setCurrent("en"); App.localizeShell(); });
s = await state(back);
check("switch back to en: slot empty again", s.slotChildren === 0, s);
check("switch back to en: lang tag follows", s.lang === "en", s);
await back.close();

/* This sandbox has no route to the chain, so the node socket fails to connect
 * and Chromium logs THAT as a console error. Chain connectivity is not what
 * this probe tests, so those lines are filtered; everything else (including
 * every error the badge itself could cause) is still held to zero. */
const realErrors = errors.filter((e) => !/WebSocket connection|net::ERR_|Failed to load resource/.test(e));
check("no console errors / page errors during the whole probe", realErrors.length === 0, realErrors);
console.log("(" + (errors.length - realErrors.length) + " network-only console lines ignored: chain socket unreachable in this sandbox)");
await browser.close();
console.log((fail === 0 ? "OK" : "FAIL") + ": i18n-badge browser probe — " + pass + " passed, " + fail + " failed");
console.log("screenshots: " + OUT);
process.exit(fail === 0 ? 0 : 1);