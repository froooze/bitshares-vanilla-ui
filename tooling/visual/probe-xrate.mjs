/* probe-xrate.mjs — visual + behavioral gate for the #/cross-rates page.
 * Asserts the matrix renders with live data, cells link to their pools,
 * the theme trio + phone/desktop all render, and the console stays clean.
 * Run: PLAYWRIGHT_BROWSERS_PATH=.browsers node tooling/visual/probe-xrate.mjs
 * (server must NOT already run on 8256 — the probe serves vanilla/ itself).
 * DEV-ONLY probe, never shipped, never required to run the wallet. */
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
await new Promise((r) => server.listen(8256, r));

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const errs = [];
page.on("console", (m) => { if (m.type() === "error") errs.push(m.text()); });
page.on("pageerror", (e) => errs.push("PAGEERROR " + String(e)));
await page.addInitScript(() => {
  try { localStorage.setItem("bts-vanilla-tour-dismissed-v1", "1"); } catch (e) { /* probe stands */ }
});
let fails = 0;
const check = (name, ok, detail) => {
  if (!ok) fails++;
  console.log((ok ? "PASS " : "FAIL ") + name + (detail ? "  " + detail : ""));
};

await page.goto("http://localhost:8256/#/cross-rates", { waitUntil: "load", timeout: 60000 });
await page.waitForFunction(
  () => document.querySelectorAll("#view .xrate-scroll tbody tr").length > 1,
  null, { timeout: 120000 });
await page.waitForTimeout(3000);
const snap = await page.evaluate(() => {
  const view = document.getElementById("view");
  const h1 = view.querySelector("h1");
  const rows = view.querySelectorAll(".xrate-scroll tbody tr");
  const firstLink = view.querySelector(".xrate-scroll tbody td a[href^='#/pools/']");
  const diag = view.querySelectorAll(".xrate-scroll td.xrate-diag").length;
  const status = (view.querySelector(".an-status") || view.querySelector(".muted") || {}).textContent || "";
  return {
    h1: h1 ? h1.textContent.trim() : "",
    rows: rows.length,
    firstHref: firstLink ? firstLink.getAttribute("href") : "",
    diag,
    status: status.slice(0, 120),
  };
});
check("h1 Cross Rates", snap.h1.indexOf("Cross Rates") === 0, JSON.stringify(snap.h1));
check("matrix has rows", snap.rows > 5, "rows=" + snap.rows);
check("cells link to pools", /^#\/pools\/1\.19\.\d+$/.test(snap.firstHref), snap.firstHref);
check("diagonal cells marked", snap.diag > 0, "diag=" + snap.diag);
console.log("     status:", JSON.stringify(snap.status));

/* Click-through: first pool link lands on a pool desk. */
await page.locator(".xrate-scroll tbody td a[href^='#/pools/']").first().click();
await page.waitForTimeout(2500);
const nav = await page.evaluate(() => location.hash);
check("cell click opens its pool", /^#\/pools\/1\.19\.\d+$/.test(nav), nav);
await page.evaluate(() => { location.hash = "#/cross-rates"; });
await page.waitForTimeout(1500);

/* Theme trio + phone width. */
for (const theme of ["ref-ui-theme", "dex-ux-theme", "vanilla-ui-theme"]) {
  await page.evaluate((th) => document.documentElement.setAttribute("data-theme", th), theme);
  await page.waitForTimeout(900);
  const t = await page.evaluate(() => {
    const view = document.getElementById("view");
    return {
      h1: (view.querySelector("h1") || {}).textContent || "",
      rows: view.querySelectorAll(".xrate-scroll tbody tr").length,
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    };
  });
  check(theme + "/desk renders", t.h1.indexOf("Cross Rates") === 0 && t.rows > 5 && t.overflow <= 1,
    "rows=" + t.rows + " overflow=" + t.overflow);
  await page.screenshot({ path: "/tmp/opencode/xrate-" + theme + "-desk.png" });
}
await page.setViewportSize({ width: 360, height: 780 });
await page.evaluate(() => document.documentElement.setAttribute("data-theme", "dex-ux-theme"));
await page.waitForTimeout(900);
const phone = await page.evaluate(() => {
  const view = document.getElementById("view");
  const table = view.querySelector(".xrate-scroll table");
  const style = table ? getComputedStyle(table).display : "?";
  return {
    rows: view.querySelectorAll(".xrate-scroll tbody tr").length,
    tableDisplay: style,
    scrolls: view.querySelector(".xrate-scroll").scrollWidth >= view.querySelector(".xrate-scroll").clientWidth,
  };
});
check("360px keeps the table (no card swap)", phone.rows > 5 && phone.tableDisplay === "table", JSON.stringify(phone));
await page.screenshot({ path: "/tmp/opencode/xrate-dex-phone.png" });

console.log("console errors:", errs.length ? errs : "none");
check("no console errors", errs.length === 0);
await browser.close();
server.close();
console.log(fails ? "xrate: " + fails + " FAILURE(S)" : "xrate: PASS");
process.exit(fails ? 1 : 0);
