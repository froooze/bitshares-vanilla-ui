"use strict";
/* i18n-key-gate-test: gate 7 of tooling/check_i18n.py — "a keyed
 * signing-dialog line must name the string it actually shows".
 *
 * WHY THIS EXISTS. It was proven during the Task 4 fix wave that repointing
 * a ConfirmDialog/UnlockConfirm call site at a WRONG-but-existing key, or at
 * a key that does not exist at all, left every gate green. Both failures are
 * invisible from the outside: the t()-default drift check is equally happy
 * with either key, and a missing key simply degrades the line to plain text.
 * The damage is a confidently WRONG English reference disclosed — one tap
 * away — on the last dialog a user reads before signing a transaction. That
 * is worse than showing nothing, so the check is part of the gate, not a
 * lint.
 *
 * WHAT IS PROVEN HERE (each case is a mutation, so each fails without its
 * half of the gate):
 *   1. the unmodified tree is green;
 *   2. a titleKey repointed at a wrong-but-EXISTING key fails;
 *   3. a titleKey repointed at a MISSING key fails;
 *   4. a confirm row's 4th slot repointed at a wrong-but-EXISTING key fails;
 *   5. a confirm row's 4th slot repointed at a MISSING key fails;
 *   6. a feeTermKey repointed at a wrong key fails (the fee dt is a keyed
 *      signing line like any other);
 *   7. the ASSIGNMENT form (cfg.titleKey = "…", used by trade-panels.js)
 *      fails when it stops matching the preceding cfg.title = t("…");
 *   8. every failure names the file, so the message is actionable.
 *
 * ISOLATION. The real working tree is NEVER mutated. Each case copies
 * tooling/check_i18n.py + vanilla/{index.html,js,locales} into a fresh temp
 * directory and runs the copy, so the checker resolves its own ROOT from its
 * own __file__ exactly as it does in production. That costs a ~11 MB copy per
 * case and buys a test that cannot leave the tree dirty — the one thing a
 * mutating gate test must never do in a repo with other agents working in it.
 */
var assert = require("assert");
var fs = require("fs");
var os = require("os");
var path = require("path");
var cp = require("child_process");

var ROOT = path.join(__dirname, "..");
var passed = 0;
function ok(cond, msg) { assert.ok(cond, msg); passed += 1; }

/* copyTree: recursive copy of a file or directory into dst. */
function copyTree(src, dst) {
  var st = fs.statSync(src);
  if (st.isDirectory()) {
    fs.mkdirSync(dst, { recursive: true });
    fs.readdirSync(src).forEach(function (name) {
      copyTree(path.join(src, name), path.join(dst, name));
    });
    return;
  }
  fs.copyFileSync(src, dst);
}

/* sandbox: a throwaway copy of the tree the checker reads. Returns the dir. */
var seq = 0;
function sandbox() {
  var dir = fs.mkdtempSync(path.join(os.tmpdir(), "i18n-key-gate-" + (seq++) + "-"));
  fs.mkdirSync(path.join(dir, "tooling"), { recursive: true });
  fs.mkdirSync(path.join(dir, "vanilla"), { recursive: true });
  fs.copyFileSync(path.join(ROOT, "tooling", "check_i18n.py"),
    path.join(dir, "tooling", "check_i18n.py"));
  copyTree(path.join(ROOT, "vanilla", "js"), path.join(dir, "vanilla", "js"));
  copyTree(path.join(ROOT, "vanilla", "locales"), path.join(dir, "vanilla", "locales"));
  fs.copyFileSync(path.join(ROOT, "vanilla", "index.html"),
    path.join(dir, "vanilla", "index.html"));
  return dir;
}

/* run: the checker in a sandbox. Returns {code, out}. */
function run(dir) {
  var r = cp.spawnSync("python3", [path.join(dir, "tooling", "check_i18n.py")],
    { encoding: "utf8" });
  return { code: r.status, out: (r.stdout || "") + (r.stderr || "") };
}

/* mutate: exact string replacement in one file of a sandbox; fails loudly if
 * the anchor is not found exactly once, so a drifted test can never pass by
 * silently mutating nothing. */
function mutate(dir, rel, from, to, times) {
  var full = path.join(dir, rel);
  var src = fs.readFileSync(full, "utf8");
  var n = src.split(from).length - 1;
  assert.strictEqual(n, times === undefined ? 1 : times,
    "anchor not found exactly " + (times === undefined ? 1 : times) +
    " time(s) in " + rel + ": " + JSON.stringify(from));
  fs.writeFileSync(full, src.split(from).join(to));
}

/* expectFail: the mutation must be caught, with a message that names the file
 * and says something a reader can act on. */
function expectFail(dir, label, file, needle) {
  var r = run(dir);
  ok(r.code === 1, label + ": check_i18n.py exits non-zero (got " + r.code + ")");
  ok(r.out.indexOf(file) !== -1,
    label + ": the failure names " + file + " (output: " + r.out.split("\n")[1] + ")");
  ok(r.out.indexOf(needle) !== -1,
    label + ": the failure explains itself — expected " + JSON.stringify(needle) +
    ", got: " + r.out.split("\n").slice(1, 4).join(" | "));
}

/* ---- 1. baseline ------------------------------------------------------- */
var base = sandbox();
var baseRun = run(base);
ok(baseRun.code === 0, "the unmodified tree is green: " + baseRun.out.split("\n")[0]);
ok(/keyed dialog titles/.test(baseRun.out) &&
   /confirm-row term keys/.test(baseRun.out),
  "the gate reports its own coverage (titles/fee terms + row slots), so a "
  + "silently-empty gate would be visible in the output");
var gated = baseRun.out.match(/(\d+) keyed dialog titles \/ fee terms and (\d+) confirm-row term keys/);
ok(gated && Number(gated[1]) > 0 && Number(gated[2]) > 0,
  "and the reported coverage is non-zero (" + (gated ? gated[1] + "/" + gated[2] : "none") + ")");

/* ---- 2/3. titleKey: wrong-but-existing, and missing ------------------- */
var t1 = sandbox();
mutate(t1, "vanilla/js/views/asset-ui.js",
  'title: t("asset.confirm_create", "Confirm asset create"), titleKey: "asset.confirm_create",',
  'title: t("asset.confirm_create", "Confirm asset create"), titleKey: "asset.confirm_update",');
expectFail(t1, "wrong-but-existing titleKey", "asset-ui.js", "WRONG English reference");

var t2 = sandbox();
mutate(t2, "vanilla/js/views/asset-ui.js",
  'titleKey: "asset.confirm_create",',
  'titleKey: "asset.confirm_create_typo",');
expectFail(t2, "missing titleKey", "asset-ui.js", "does not exist in en.json");

/* ---- 4/5. confirm row 4th slot: wrong-but-existing, and missing -------- */
var r1 = sandbox();
mutate(r1, "vanilla/js/views/credit-ui.js",
  '[t("credit.owner", "Owner"), who(R.me), null, "credit.owner"]',
  '[t("credit.owner", "Owner"), who(R.me), null, "credit.asset"]');
expectFail(r1, "wrong-but-existing row term key", "credit-ui.js", "WRONG English reference");

var r2 = sandbox();
mutate(r2, "vanilla/js/views/credit-ui.js",
  '[t("credit.owner", "Owner"), who(R.me), null, "credit.owner"]',
  '[t("credit.owner", "Owner"), who(R.me), null, "credit.owner_typo"]');
expectFail(r2, "missing row term key", "credit-ui.js", "does not exist in en.json");

/* The key-shape filter that decides "is this a confirm row" must accept
 * HYPHENS: help.topic_accounts-permissions_title is a real signing row, and
 * an over-narrow shape silently skips gated rows — the exact hole the gate
 * exists to close. Mutation: point that row at a wrong-but-existing key. */
var r3 = sandbox();
mutate(r3, "vanilla/js/views/asset-ui.js",
  'null, "help.topic_accounts-permissions_title"]',
  'null, "asset.flags_title"]');
expectFail(r3, "hyphenated row term key", "asset-ui.js", "WRONG English reference");

/* ---- 6. feeTermKey (the fee dt is a keyed signing line too) ------------ */
var f1 = sandbox();
mutate(f1, "vanilla/js/views/asset-manage-ui.js",
  'feeHuman: updFee, feeTerm: t("borrow.fee", "Fee"), feeTermKey: "borrow.fee",',
  'feeHuman: updFee, feeTerm: t("borrow.fee", "Fee"), feeTermKey: "confirm.fee",');
expectFail(f1, "wrong feeTermKey", "asset-manage-ui.js", "WRONG English reference");

/* ---- 7. the ASSIGNMENT form (cfg.titleKey = "…") ---------------------- */
var a1 = sandbox();
mutate(a1, "vanilla/js/views/trade-panels.js",
  'cfg.titleKey = "trade.uc_title";',
  'cfg.titleKey = "trade.uc_orders";');
expectFail(a1, "wrong assignment-form titleKey", "trade-panels.js", "WRONG English reference");

/* ---- 8. an UNKEYED dialog is unaffected (no false alarm) --------------- */
var n1 = sandbox();
mutate(n1, "vanilla/js/views/asset-ui.js",
  'title: t("asset.confirm_create", "Confirm asset create"), titleKey: "asset.confirm_create",',
  'title: t("asset.confirm_create", "Confirm asset create"),');
ok(run(n1).code === 0,
  "dropping the key (back to the unkeyed opt-out) is still green — the gate " +
  "demands correctness of what IS keyed, never keys");

/* ---- cleanup ---------------------------------------------------------- */
[base, t1, t2, r1, r2, r3, f1, a1, n1].forEach(function (dir) {
  try { fs.rmSync(dir, { recursive: true, force: true }); } catch (e) { /* tmp is disposable */ }
});

console.log("i18n keyed-dialog key gate: " + passed + " passed, 0 failed");