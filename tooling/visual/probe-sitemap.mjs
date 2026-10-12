/* probe-sitemap.mjs — visual + behavioral gate for the #/help/sitemap page.
 *
 * WHY: the sitemap is the "every page listed and reachable" contract made
 * visible — a unit test can assert links exist, but only a browser proves
 * the buttons scroll, the links navigate, and the layout holds at both
 * ends of the screen. Exercises: 8-button subsection nav (scroll position
 * moves, hash untouched), a page-link click-through, theme trio, phone.
 *
 * DEV-ONLY: playwright lives in tooling/visual/node_modules; never shipped,
 * never required to run the wallet. Run from /workspace:
 *   PLAYWRIGHT_BROWSERS_PATH=tooling/visual/.browsers node tooling/visual/probe-sitemap.mjs */
import { chromium } from "playwright";
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";

const ROOT = "/workspace/vanilla";
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png" };
const server = createServer(async (req, res) => {
  try {
    const p = normalize(decodeURIComponent(req.url.split("?")[0])).replace(/^(\.\.[/\\])+/, "");
    const file = join(ROOT, p === "/" ? "index.html" : p);
    const body = await readFile(file);
    res.writeHead(200, { "content-type": TYPES[extname(file)] || "application/octet-stream" });
    res.end(body);
  } catch (e) { res.writeHead(404).end("x"); }
});
await new Promise((r) => server.listen(8234, r));

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const errs = [];
page.on("console", (m) => { if (m.type() === "error") errs.push(m.text()); });
page.on("pageerror", (e) => errs.push("PAGEERROR " + String(e)));
await page.addInitScript(() => {
  try { localStorage.setItem("bts-vanilla-tour-dismissed-v1", "1"); } catch (e) { /* storage-less run */ }
});

let fails = 0;
const check = (name, ok, detail) => {
  if (!ok) fails++;
  console.log((ok ? "PASS " : "FAIL ") + name + (detail ? "  " + detail : ""));
};

await page.goto("http://localhost:8234/#/help/sitemap", { waitUntil: "load" });
await page.waitForTimeout(1500);
const nav = await page.evaluate(() => {
  const view = document.getElementById("view");
  const btns = Array.from(view.querySelectorAll(".help-sitemap-nav button"));
  const heads = Array.from(view.querySelectorAll("#view h2"));
  return {
    h1: ((view.querySelector("h1") || {}).textContent || "").trim(),
    buttons: btns.map((b) => b.textContent),
    headIds: heads.map((h) => h.getAttribute("id")),
    links: view.querySelectorAll("#view li a[href^='#/']").length,
  };
});
check("h1 Site map", /site map/i.test(nav.h1), JSON.stringify(nav.h1));
check("8 subsection buttons", nav.buttons.length === 8, JSON.stringify(nav.buttons));
check("markers carry ids", nav.headIds.every((id, i) => id === "sitemap-sec-" + i), JSON.stringify(nav.headIds));
check("granular links present", nav.links >= 60, "links=" + nav.links);

/* Subsection button scrolls without touching the hash. */
const y0 = await page.evaluate(() => window.scrollY);
await page.locator(".help-sitemap-nav button").nth(5).click();
await page.waitForTimeout(700);
const scrolled = await page.evaluate(() => ({ y: window.scrollY, hash: location.hash }));
check("button scrolls to marker", scrolled.y > y0, "y " + y0 + " -> " + scrolled.y);
check("button leaves hash alone", scrolled.hash === "#/help/sitemap", scrolled.hash);

/* Page link navigates to a real desk. */
await page.goto("http://localhost:8234/#/help/sitemap", { waitUntil: "load" });
await page.waitForTimeout(1000);
await page.locator("#view li a[href='#/cross-rates']").first().click();
await page.waitForTimeout(1500);
const dest = await page.evaluate(() => ({
  hash: location.hash,
  h1: ((document.querySelector("#view h1") || {}).textContent || "").trim(),
}));
check("sitemap link reaches Cross Rates", dest.hash === "#/cross-rates", JSON.stringify(dest));

/* Theme trio + phone end. */
for (const theme of ["ref-ui-theme", "dex-ux-theme", "vanilla-ui-theme"]) {
  await page.evaluate((th) => document.documentElement.setAttribute("data-theme", th), theme);
  await page.goto("http://localhost:8234/#/help/sitemap", { waitUntil: "load" });
  await page.waitForTimeout(1000);
  const t = await page.evaluate(() => {
    const view = document.getElementById("view");
    return {
      h1: ((view.querySelector("h1") || {}).textContent || "").trim(),
      btns: view.querySelectorAll(".help-sitemap-nav button").length,
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    };
  });
  check(theme + ": renders clean", /site map/i.test(t.h1) && t.btns === 8 && t.overflow <= 1, JSON.stringify(t));
  await page.screenshot({ path: "/tmp/opencode/sitemap-" + theme + "-desk.png" });
}
await page.setViewportSize({ width: 360, height: 780 });
await page.goto("http://localhost:8234/#/help/sitemap", { waitUntil: "load" });
await page.waitForTimeout(1000);
const phone = await page.evaluate(() => {
  const btns = document.querySelectorAll("#view .help-sitemap-nav button");
  const small = Array.from(btns).filter((b) => {
    const r = b.getBoundingClientRect();
    return r.width >= 44 || r.height >= 44;
  }).length;
  return { btns: btns.length, touchOk: small };
});
check("360px: buttons keep touch floor", phone.btns === 8 && phone.touchOk === 8, JSON.stringify(phone));
await page.screenshot({ path: "/tmp/opencode/sitemap-phone.png" });

console.log("console errors:", errs.length ? errs : "none");
check("no console errors", errs.length === 0);
await browser.close();
server.close();
console.log(fails ? "sitemap: " + fails + " FAILURE(S)" : "sitemap: PASS");
process.exit(fails ? 1 : 0);
