/* i18n-risk-keys-test: the high-risk rule is the contract that decides
 * which strings get dual-line English. It must be mechanical and stable,
 * so it is tested as pure logic, not re-derived by hand in tests. */
"use strict";
var assert = require("assert");
var fs = require("fs");
var path = require("path");
var vm = require("vm");

var ROOT = path.join(__dirname, "..");
var src = fs.readFileSync(path.join(ROOT, "vanilla/js/i18n/risk-keys.js"), "utf8");
var sandbox = {};
vm.createContext(sandbox);
vm.runInContext(src, sandbox);
var RiskKeys = sandbox.RiskKeys;

/* Named sections are high-risk regardless of wording. */
assert.strictEqual(RiskKeys.isHighRisk("unlockconfirm.confirm", "OK"), true);
assert.strictEqual(RiskKeys.isHighRisk("vesting.vesting_note", "x"), true);

/* The word rule catches danger wording OUTSIDE the named sections. */
assert.strictEqual(RiskKeys.isHighRisk("barter.uc_title", "Unlock to sign"), true);
assert.strictEqual(RiskKeys.isHighRisk("approval.password", "Password"), true);

/* Ordinary chrome is NOT high-risk. */
assert.strictEqual(RiskKeys.isHighRisk("menu.dashboard", "Dashboard"), false);
assert.strictEqual(RiskKeys.isHighRisk("nav.explorer", "Explore"), false);

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
   * exists to prevent — and rejects the 13 keys whose Spanish rendering is
   * longer than its English source. */
  assert.ok(String(enFlat[k]).length <= RiskKeys.MAX_RISK_LEN, "listed key's EN value is short: " + k);
});

/* The printed count is the WHOLE es enumeration — every key in the dict the
 * rule flags, which is what _meta.high_risk and the views consume. It is NOT
 * the spec §6 pilot bucket (69): that figure is high-risk INTERSECTED with the
 * 688 untranslated es stubs (empty or identical to English), i.e. the strings
 * the es fill has to cover, not the strings the rule flags. Asserting 69 here
 * would bake a pre-fill locale snapshot into a pure rule test. */
console.log("OK: i18n-risk-keys (" + list.length + " high-risk keys in es)");