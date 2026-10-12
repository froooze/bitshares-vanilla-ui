/* i18n-risk-keys-test: the high-risk rule is the contract that decides
 * which strings get dual-line English. It must be mechanical and stable,
 * so it is tested as pure logic, not re-derived by hand in tests. */
"use strict";
var assert = require("assert");
var fs = require("fs");
var path = require("path");
var vm = require("vm");

var ROOT = path.join(__dirname, "..");
var MODULE_PATH = path.join(ROOT, "vanilla/js/i18n/risk-keys.js");
var src = fs.readFileSync(MODULE_PATH, "utf8");
var sandbox = {};
vm.createContext(sandbox);
vm.runInContext(src, sandbox);
var RiskKeys = sandbox.RiskKeys;

/* The constants ARE the rule, so pin them here: a silently widened bound or
 * a dropped section would otherwise leave this test green. */
assert.strictEqual(RiskKeys.MAX_RISK_LEN, 120,
  "MAX_RISK_LEN is 120 (the spec §2 bound)");
assert.deepStrictEqual(Object.keys(RiskKeys.HIGH_RISK_SECTIONS).sort(), [
  "approval", "auth", "backup", "confirm", "createaccount", "createworker",
  "credit", "debit", "htlc", "password", "proposal", "proposals_ticket",
  "samet", "security", "ticket", "tickets", "transfer", "unlockconfirm",
  "vesting", "wallet"
], "exactly the spec §2 high-risk sections — add nothing, drop nothing");
Object.keys(RiskKeys.HIGH_RISK_SECTIONS).forEach(function (s) {
  assert.strictEqual(RiskKeys.HIGH_RISK_SECTIONS[s], 1, "section flag is 1: " + s);
});
assert.strictEqual(Object.isFrozen(RiskKeys.HIGH_RISK_SECTIONS), true,
  "the exported rule is frozen — no consumer may mutate it");

/* Every section in the set really is high-risk (the set is not decorative),
 * checked through isHighRisk so a stray guard cannot hide a dead entry. */
Object.keys(RiskKeys.HIGH_RISK_SECTIONS).forEach(function (s) {
  assert.strictEqual(RiskKeys.isHighRisk(s + ".probe", "OK"), true,
    "named section is high-risk whatever it says: " + s);
});

/* The module's CommonJS branch: Node consumers get the same four members. */
var viaRequire = require(MODULE_PATH);
assert.deepStrictEqual(Object.keys(viaRequire).sort(),
  ["HIGH_RISK_SECTIONS", "MAX_RISK_LEN", "isHighRisk", "listFor"],
  "require() exposes the four members");
assert.strictEqual(viaRequire.MAX_RISK_LEN, 120);
assert.strictEqual(typeof viaRequire.isHighRisk, "function");
assert.strictEqual(typeof viaRequire.listFor, "function");
assert.strictEqual(viaRequire.isHighRisk("misc.probe", "This action is irreversible"),
  true, "require()'s copy applies the same rule");

/* Named sections are high-risk regardless of wording. */
assert.strictEqual(RiskKeys.isHighRisk("unlockconfirm.confirm", "OK"), true);
assert.strictEqual(RiskKeys.isHighRisk("vesting.vesting_note", "x"), true);

/* The word rule catches danger wording OUTSIDE the named sections — so the
 * keys here must be non-sections, or the section rule answers instead. */
assert.strictEqual(RiskKeys.isHighRisk("barter.uc_title", "Unlock to sign"), true);
assert.strictEqual(RiskKeys.isHighRisk("misc.probe", "Password"), true);

/* Ordinary chrome is NOT high-risk. */
assert.strictEqual(RiskKeys.isHighRisk("menu.dashboard", "Dashboard"), false);
assert.strictEqual(RiskKeys.isHighRisk("nav.explorer", "Explore"), false);

/* One positive per danger alternative, keyed from a non-section so a TRUE
 * result can only come from the word rule. Inflections matter more than the
 * bare stem: a stem that only matches itself misses the word as it is
 * actually written in a sentence. */
var DANGER_POSITIVES = [
  "sign", "Sign now",
  "signed", "This operation was signed",
  "signing", "Signing this broadcast is final",
  "signature", "A valid signature is required",
  "signatures", "Signatures are checked",
  "send", "Send BTS",
  "sending", "Sending to an exchange",
  "sent", "Transaction sent to the network",
  "irreversible", "This action is irreversible",
  "irreversibly", "funds are irreversibly transferred",
  "irreversibility", "the irreversibility of this choice",
  "permanent", "a permanent lock",
  "permanently", "permanently deleted",
  "Unrecoverable", "Unrecoverable",
  "unrecoverably", "unrecoverably lost",
  "unrecovered", "unrecovered funds",
  "Password", "Password",
  "passwords", "New passwords do not match",
  "private key", "Your private key",
  "private keys", "Your private keys",
  "brainkey", "Enter your brainkey",
  "brainkeys", "Your brainkeys",
  "Backup", "Backup",
  "Backups", "Backups",
  "scam", "a scam warning",
  "scams", "scams",
  "scammer", "never pay a scammer",
  "scamming", "scamming is illegal",
  "Never share", "Never share this with anyone",
  "Withdraw", "Withdraw",
  "withdraws", "The account withdraws funds",
  "withdrawal", "Pool withdrawal",
  "withdrawals", "Your withdrawals",
  "withdrawing", "withdrawing to an exchange",
  "Delegate", "Delegate votes",
  "delegates", "delegates",
  "delegated", "delegated",
  "delegating", "delegating voting power",
  "delegation", "delegation of votes",
  "vesting", "vesting balance",
  "vested", "vested",
  "memo", "memo",
  "memos", "memos"
];
for (var i = 0; i < DANGER_POSITIVES.length; i += 2) {
  assert.strictEqual(RiskKeys.isHighRisk("misc.probe", DANGER_POSITIVES[i + 1]), true,
    "danger word is caught: " + JSON.stringify(DANGER_POSITIVES[i + 1]));
}

/* Negative controls: near-misses the leading \b has to keep out. */
var DANGER_NEGATIVES = [
  "design", "The design is fixed",
  "designing", "designing a policy",
  "assign", "Assign this asset",
  "assignment", "assignment of voting power",
  "unsigned", "an unsigned blob",
  "resign", "resign the slate",
  "sentence", "One sentence is all",
  "consent", "consent form",
  "sensitive", "sensitive field",
  "investing", "investing your stake",
  "harvest", "harvest the plot",
  "manifest", "the manifest is clear",
  "memory", "memory usage",
  "memoize", "memoize the query",
  "best", "best price",
  "Navigation", "Navigation",
  "Dashboard", "Dashboard",
  "Back up early", "Back up early"
];
for (var j = 0; j < DANGER_NEGATIVES.length; j += 2) {
  assert.strictEqual(RiskKeys.isHighRisk("misc.probe", DANGER_NEGATIVES[j + 1]), false,
    "NOT a danger word: " + JSON.stringify(DANGER_NEGATIVES[j + 1]));
}

/* A prototype-chain key is not a section: reading HIGH_RISK_SECTIONS
 * without hasOwnProperty makes "constructor.x" and "toString.x" truthy. */
assert.strictEqual(RiskKeys.isHighRisk("constructor.x", "Hi"), false);
assert.strictEqual(RiskKeys.isHighRisk("toString.x", "Hi"), false);
assert.strictEqual(RiskKeys.isHighRisk("hasOwnProperty.x", "Hi"), false);

/* Length bound: long help prose is page-level-warning territory, never
 * two unreadable paragraphs. */
var long = new Array(130).join("sign "); /* 129 x "sign " */
assert.ok(long.length > RiskKeys.MAX_RISK_LEN, "fixture really is over the bound");
assert.strictEqual(RiskKeys.isHighRisk("help.topic_backups_body", long), false);

/* A short string in the SAME section is still dual-lined: the bound cuts
 * prose, it does not disable the section rule. */
var shortProse = "Back up early";
assert.ok(shortProse.length <= RiskKeys.MAX_RISK_LEN);
assert.strictEqual(RiskKeys.isHighRisk("help.topic_backups_body", shortProse), false,
  "help is not a named section and carries no danger word");
assert.strictEqual(RiskKeys.isHighRisk("wallet.backup_body", shortProse), true,
  "but wallet IS a named section, so its short strings are dual-lined");

/* Missing/short values must not throw. */
assert.strictEqual(RiskKeys.isHighRisk("x.y", ""), false);
assert.strictEqual(RiskKeys.isHighRisk("x.y", undefined), false);

/* listFor enumerates a real dict against en and is sorted + unique. */
function flat(d, p) {
  var out = {}, k, v;
  p = p || "";
  for (k in d) {
    if (!Object.prototype.hasOwnProperty.call(d, k) || k === "_meta") continue;
    v = d[k];
    if (v && typeof v === "object") { Object.assign(out, flat(v, p + k + ".")); }
    else { out[p + k] = v; }
  }
  return out;
}
var en = JSON.parse(fs.readFileSync(path.join(ROOT, "vanilla/locales/en.json"), "utf8"));
var es = JSON.parse(fs.readFileSync(path.join(ROOT, "vanilla/locales/es.json"), "utf8"));
var enFlat = flat(en), esFlat = flat(es);
var list = RiskKeys.listFor(esFlat, enFlat);
assert.ok(Array.isArray(list) && list.length > 0, "es has high-risk keys");
var sorted = list.slice().sort();
assert.deepStrictEqual(list, sorted, "listFor output is sorted");
assert.strictEqual(new Set(list).size, list.length, "no duplicates");
list.forEach(function (k) {
  assert.ok(enFlat[k] !== undefined, "listed key exists in en: " + k);
  /* The bound is on the ENGLISH value (spec §2: "its English value is <=120
   * characters"), and isHighRisk() only ever sees the English value, so this
   * must assert against enFlat. Asserting against esFlat would apply an
   * English-only rule to a translation — the per-locale drift the rule
   * exists to prevent — and rejects the 15 keys whose Spanish rendering is
   * longer than its English source. */
  assert.ok(String(enFlat[k]).length <= RiskKeys.MAX_RISK_LEN, "listed key's EN value is short: " + k);
});

/* The printed count is the WHOLE es enumeration — every key in the dict the
 * rule flags, which is what _meta.high_risk and the views consume. It is NOT
 * the spec §6 pilot bucket: that figure is high-risk INTERSECTED with the
 * 688 untranslated es stubs (empty or identical to English), i.e. the strings
 * the es fill has to cover, not the strings the rule flags. It moves whenever
 * the rule or the dict moves, so pinning it here would bake a pre-fill
 * locale snapshot into a pure rule test. */
console.log("OK: i18n-risk-keys (" + list.length + " high-risk keys in es)");
