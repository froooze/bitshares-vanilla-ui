// probe-i18n-honesty-live.mjs — DEV ONLY (never shipped, never required to run the
// wallet). End-to-end audit: with every locale now _meta v2 + provenance machine,
// the chip must be VISIBLE by default and a signing dialog must render dual-line.
// Drives the real code paths in a real Chromium; asserts DOM truth, not transcripts.
import { chromium } from "playwright-core";
import fs from "node:fs";

const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, cur, i, arr) => {
    if (cur.startsWith("--")) acc.push([cur.slice(2), arr[i + 1] && !arr[i + 1].startsWith("--") ? arr[i + 1] : "1"]);
    return acc;
  }, [])
);
const URL = args.url || "http://localhost:8099";
const OUT = args.out || "/tmp/i18n-honesty-live";
fs.mkdirSync(OUT, { recursive: true });

let pass = 0, fail = 0;
function check(name, cond, extra) {
  if (cond) { pass++; console.log("ok   " + name); }
  else { fail++; console.log("FAIL " + name + " " + (extra === undefined ? "" : JSON.stringify(extra).slice(0, 400))); }
}

const errors = [];
const browser = await chromium.launch();

async function pageFor(width, theme, locale) {
  const page = await browser.newPage({ viewport: { width: width, height: 800 } });
  page.on("pageerror", function (e) { errors.push(String(e && e.message || e)); });
  page.on("console", function (m) { if (m.type() === "error") errors.push(m.text()); });
  await page.goto(URL + "/#/explorer", { waitUntil: "networkidle" });
  /* Switch locale through the app's real setLocale() — the same function
   * the settings UI calls — rather than fighting boot-order storage. This
   * exercises the genuine user path: fetch dict, set current, write pref,
   * repaint the shell (which is where the badge mounts). */
  const switched = await page.evaluate(async function (args) {
    try {
      var r = await I18n.setLocale(args[0]);
      try { document.documentElement.setAttribute("data-theme", args[1]); } catch (e2) {}
      try { if (typeof App !== "undefined" && App.localizeShell) App.localizeShell(); } catch (e3) {}
      return { ok: !!(r && r.ok), locale: I18n.locale() };
    } catch (e) { return { ok: false, error: String(e && e.message || e) }; }
  }, [locale, theme]);
  if (!switched.ok) console.log("WARN setLocale(" + locale + ") failed: " + JSON.stringify(switched));
  return page;
}

for (const theme of ["ref-ui-theme", "dex-ux-theme", "vanilla-ui-theme"]) {
  for (const width of [360, 1440]) {
    for (const locale of ["en", "es"]) {
      const page = await pageFor(width, theme, locale);
      const state = await page.evaluate(function () {
        var doc = document;
        var chip = doc.querySelector(".i18n-badge");
        var slot = doc.getElementById("i18n-badge-slot");
        // Exercise the real signing dialog path with a keyed title and row.
        var duel = null;
        try {
          var box = ConfirmDialog.show({
            title: "Cancelar orden", titleKey: "tradecancel.confirm_title",
            rows: [["Cantidad", "12.0 BTS", null, "transfer.amount_label"]],
            feeHuman: "0.01 BTS", backLabel: "Atras", sendLabel: "Firmar",
            doc: document
          });
          doc.body.appendChild(box);
          var star = box.querySelector(".i18n-risk-star");
          var h3 = box.querySelector("h3");
          var dts = box.querySelectorAll("dt");
          duel = {
            starTag: star ? star.tagName : null,
            ariaExpanded: star ? star.getAttribute("aria-expanded") : null,
            h3Kept: !!h3,
            dtCount: dts.length,
            enHidden: !!(box.querySelector(".i18n-risk-en") || {}).hidden,
            backId: !!(box.querySelector("#confirm-back") || box.querySelector(".confirm-actions button")),
            dualCount: box.querySelectorAll(".i18n-risk").length
          };
          // Expand the asterisk and confirm the English appears.
          if (star) {
            var before = (box.querySelector(".i18n-risk-en") || {}).hidden;
            star.click();
            var after = (box.querySelector(".i18n-risk-en") || {}).hidden;
            duel.expandWorks = (before === true && after === false);
            duel.ariaFlipped = star.getAttribute("aria-expanded") === "true";
          }
          box.remove();
        } catch (e) { duel = { error: String(e && e.message || e) }; }
        return { chipVisible: !!chip, slotChildren: slot ? slot.children.length : -1, duel: duel };
      });
      const tag = "[" + theme + " " + width + "px " + locale + "]";
      if (locale === "en") {
        check(tag + " no chip in English", state.chipVisible === false);
      } else {
        check(tag + " chip visible for es", state.chipVisible === true, state);
        check(tag + " asterisk is a BUTTON", state.duel && state.duel.starTag === "BUTTON", state.duel);
        check(tag + " h3 kept", state.duel && state.duel.h3Kept === true, state.duel);
        check(tag + " English starts hidden", state.duel && state.duel.enHidden === true, state.duel);
        check(tag + " tap reveals English", state.duel && state.duel.expandWorks === true, state.duel);
        check(tag + " aria-expanded flips", state.duel && state.duel.ariaFlipped === true, state.duel);
        check(tag + " Back/Send stable hooks", state.duel && state.duel.backId === true, state.duel);
      }
      await page.screenshot({ path: OUT + "/honesty-" + theme + "-" + width + "-" + locale + ".png" });
      await page.close();
    }
  }
}

check("zero console/page errors", errors.length === 0, errors.slice(0, 5));
await browser.close();
console.log("\n" + pass + " passed, " + fail + " failed");
process.exit(fail ? 1 : 0);
