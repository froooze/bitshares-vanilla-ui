/* credit-offer-confirm-test.js — the op-69 create confirm rows, driven by a
 * REAL operation built by the shipped Credit builder.
 *
 * WHY THIS FILE EXISTS. Task 4 added the locale key to each row term of
 * credit-ui.js's offer-create `rows` builder while it was editing it, and in
 * the same edit renamed two fields off the wire:
 *
 *   - `op.acceptable_borrowers.length`  ->  `op.accepted_borrowers.length`
 *   - `op.auto_disable_time`            ->  `op.auto_disable ? yes : no`
 *
 * The serializer (api/credit.js:352 buildOfferCreate, and the op-69 field
 * list) spells them acceptable_borrowers / auto_disable_time. The first threw
 * a TypeError inside the rows builder — swallowed by the .catch() at
 * credit-ui.js:339, which then reported "Fee lookup failed." for a crash. The
 * second silently rendered "no" for an offer the form REQUIRES an
 * auto-disable time for (credit-ui.js:793 rejects the form when it is unset),
 * i.e. a provably false string on a signing row — the exact failure this
 * whole honesty feature exists to prevent.
 *
 * Nothing caught either: the rows builder is a closure with no test. This file
 * builds the op with the real Credit API and calls the real rows builder, so
 * a renamed field fails HERE instead of in front of a user.
 *
 * HARNESS. vanilla/js/api/{credit,format}.js and vanilla/js/views/credit-ui.js
 * are the SHIPPED modules loaded as-is (require would pull in DOM globals the
 * view touches at load time). Only the two chain-reading seams the rows
 * builder never reaches are stubbed: nothing else — the builder under test is
 * the production function, verbatim.
 */
"use strict";
var assert = require("assert");
var fs = require("fs");
var path = require("path");
var vm = require("vm");

var ROOT = path.join(__dirname, "..");
function load(rel) { return fs.readFileSync(path.join(ROOT, rel), "utf8"); }

var sandbox = { console: console };
sandbox.window = sandbox;
vm.createContext(sandbox);
/* Script-tag order in index.html: utils/dom.js, utils/touchable.js, then the
 * api + view modules. The view resolves DOM/touchable/Format/Credit/I18n off
 * the shared global scope at load time — that is the real load order. */
vm.runInContext(load("vanilla/js/utils/dom.js"), sandbox);
vm.runInContext(load("vanilla/js/utils/touchable.js"), sandbox);
vm.runInContext(load("vanilla/js/api/format.js"), sandbox);
vm.runInContext(load("vanilla/js/api/credit.js"), sandbox);
vm.runInContext(load("vanilla/js/views/credit-ui.js"), sandbox);

var Credit = sandbox.Credit;
var CreditUI = sandbox.CreditUI;

var passed = 0;
function ok(cond, msg) { assert.ok(cond, msg); passed += 1; }
function eq(a, b, msg) { assert.strictEqual(a, b, msg); passed += 1; }

/* The ISO string the form produces (credit-ui.js:794 slices a datetime-local
 * value to 19 chars) — the shape _assertIso accepted, so the builder keeps it
 * byte-for-byte. */
var AUTO_ISO = "2031-06-01T12:00:00";

/* A REAL op-69: built by the shipped Credit.buildOfferCreate from the same
 * argument shape credit-ui.js:804 passes (one collateral leg, one borrower). */
var pair = Credit.buildOfferCreate({
  accountId: "1.2.5",
  assetId: "1.3.0",
  balanceRaw: "10000000",
  rateHuman: "0.5",
  maxDurSec: "259200",
  minDealRaw: "100000",
  enabled: true,
  autoDisableIso: AUTO_ISO,
  collateral: [{ assetId: "1.3.1", price: {
    base: { amount: "1000", asset_id: "1.3.0" },
    quote: { amount: "2000", asset_id: "1.3.1" } } }],
  borrowers: [{ accountId: "1.2.7", maxRaw: "5000000" }]
});

ok(Array.isArray(pair) && pair[0] === 69, "the fixture really is an op-69 credit offer create");
var op = pair[1];

/* What the dialog is shown: exactly what reviewPaid hands the rows builder
 * (credit-ui.js:330) — {pair, fee, me, a} — plus the fee object the builder
 * reads fee.text / fee.raw off. */
var R = {
  pair: pair,
  fee: { text: "0.10 BTS", raw: "10000" },
  me: { id: "1.2.5", name: "alice" },
  a: { id: "1.3.0", symbol: "BTS", precision: 5 }
};

var rows = CreditUI._ui.offerCreateRows(R, R.fee);
ok(Array.isArray(rows), "the offer-create rows builder answers an array");

function rowByKey(key) {
  for (var i = 0; i < rows.length; i++) if (rows[i][3] === key) return rows[i];
  return null;
}

/* ---- C1: the borrower-count row reads a field the op really has ---------- */
var bor = rowByKey("credit.borrowers");
ok(bor, "the Borrowers row carries its locale key (4th slot)");
eq(String(bor[1]), String(op.acceptable_borrowers.length),
  "Borrowers counts the op's acceptable_borrowers — the serializer's field name");
eq(String(bor[1]), "1", "and with one borrower row the count reads 1");
ok(!/NaN|undefined/.test(String(bor[1])),
  "the borrower count is a number, never NaN/undefined");

/* The whole builder must not throw for any op shape it can be handed: a
 * no-borrower offer is legal (the borrower list is empty). */
var emptyPair = Credit.buildOfferCreate({
  accountId: "1.2.5", assetId: "1.3.0", balanceRaw: "10000000",
  rateHuman: "0.5", maxDurSec: "259200", minDealRaw: "100000",
  enabled: true, autoDisableIso: AUTO_ISO, collateral: [], borrowers: []
});
var emptyRows = CreditUI._ui.offerCreateRows({ pair: emptyPair, fee: R.fee, me: R.me, a: R.a }, R.fee);
var emptyBor = null;
for (var j = 0; j < emptyRows.length; j++) if (emptyRows[j][3] === "credit.borrowers") emptyBor = emptyRows[j];
eq(String(emptyBor[1]), "0", "an offer with no acceptable borrowers reads 0, not a crash");

/* ---- C2: the Auto-disable row shows the real date ----------------------- */
var auto = rowByKey("credit.auto_disable");
ok(auto, "the Auto-disable row carries its locale key (4th slot)");
eq(auto[1], AUTO_ISO,
  "Auto-disable shows the op's auto_disable_time — the ISO string the serializer stores");
ok(!/^(yes|no)$/i.test(String(auto[1])),
  "Auto-disable is never reduced to yes/no: the form REQUIRES the time (credit-ui.js:793)");
eq(auto[1], op.auto_disable_time, "and it is byte-identical to the field the op carries");

/* Every static term is keyed, and every dynamic value is not (§3.5). */
var STATIC_KEYS = ["credit.owner", "credit.asset", "credit.balance", "credit.fee_rate",
  "credit.max_duration", "credit.min_deal", "credit.enabled", "credit.auto_disable",
  "credit.collateral_legs", "credit.borrowers", "credit.fee", "credit.network"];
STATIC_KEYS.forEach(function (k) {
  ok(rowByKey(k), "row keyed " + k);
});
rows.forEach(function (r) {
  ok(typeof r[3] === "string" && r[3].indexOf(".") !== -1, "every row term carries a dotted locale key");
});

console.log("credit offer-create confirm rows: " + passed + " passed, 0 failed");