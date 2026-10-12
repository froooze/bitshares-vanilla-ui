# Machine-Filled Translations, Honestly Labeled — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the binary translated/untranslated locale model with a three-state provenance model (verified / machine / stub), add the in-app honesty surfaces (dual-line signing text, header badge, limitations page), and fill the `es` locale to full coverage as the proven pilot.

**Architecture:** One new data module (`i18n/risk-keys.js`) owns the high-risk rule and is the single source of truth for views, tests, and gates. One new UI module (`ui/risk-text.js`) owns the dual-line widget; `ConfirmDialog` routes its title and row terms through it so all 78 operations get the treatment from one code path. One small module (`ui/i18n-badge.js`) owns the header badge. `i18n.js` gains `enFor()`, `provenance()` and v1/v2 `_meta` compatibility. Both gates learn `_meta` version 2.

**Tech Stack:** vanilla ES5-style JS (no framework, no build), plain CSS custom properties, Python 3 stdlib tooling, Node stdlib tests.

## Global Constraints

- **No runtime dependencies.** No `package.json`, `node_modules`, lockfile, CDN `<script src>`, or framework import inside `vanilla/`. `python3 tooling/check_rot.py` must pass.
- **No build step.** `python3 -m http.server` serves a working app. Every file added is referenced from `index.html` or required by an existing module.
- **Shared utilities are not re-created** (AGENTS.md §7 rule 9): use `DOM.el`, `DOM.attrs`, `DOM.text`, `DOM.clear`, `Forms.*`, `TableRenderer`, `Overlay`, `ConfirmDialog`, `Event.delegate`, `DOM.touchable`. No local `function el()`, no local touch-floor helper.
- **Money never round-trips through the locale file** (§3.5): locale strings are prose only; digits come from `Format`.
- **Placeholders byte-verbatim**: `%(name)s`, object IDs `1.2.x`, URLs, operation numbers, asset symbols, theme/network ids are never translated.
- **Every new user-visible string is keyed** and added to `en.json` + all 12 locale dicts; `t()` defaults must equal the `en.json` value (`check_i18n.py` enforces this across all call sites).
- **Types**: JSDoc + `checkJs`; `bash tooling/check_types.sh` passes with zero emit. No `any` leakage into public signatures.
- **Commits are small and independently runnable**; every task ends green on its own test.
- Spec: `docs/superpowers/specs/2026-10-12-i18n-machine-translation-design.md`.

---

### Task 1: High-risk key enumeration (single source of truth)

**Files:**
- Create: `vanilla/js/i18n/risk-keys.js`
- Test: `tooling/i18n-risk-keys-test.js`
- Modify: `vanilla/index.html` (script tag), `vanilla/js/globals.d.ts`

**Interfaces:**
- Consumes: nothing (pure data + pure functions).
- Produces: global `RiskKeys` with
  - `RiskKeys.MAX_RISK_LEN` → `120`
  - `RiskKeys.isHighRisk(key, enValue)` → `boolean`
  - `RiskKeys.listFor(dict, enDict)` → `string[]` (keys of `dict` that are high-risk, sorted).
    NOTE: this enumerates ALL keys, not just untranslated ones — 1118 for `es`.
    The 103 figure in the spec §6 table is a *fill bucket* (high-risk ∩ the 688
    stubs), not the total high-risk set. The rule keys off English wording, so
    danger is independent of whether a locale already has a translation.
  - `RiskKeys.HIGH_RISK_SECTIONS` → `Object<string, number>`

`ConfirmDialog`, `RiskText`, `ui/i18n-badge.js` and the tests all read the rule from here; nothing else re-implements it.

- [ ] **Step 1: Write the failing test**

`tooling/i18n-risk-keys-test.js`:

```js
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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `node tooling/i18n-risk-keys-test.js`
Expected: FAIL — `Cannot find module .../vanilla/js/i18n/risk-keys.js` (ENOENT).

- [ ] **Step 3: Write the minimal implementation**

`vanilla/js/i18n/risk-keys.js`:

```js
/* risk-keys: THE high-risk rule — which locale strings must render with an
 * English reference beside them, because misreading them can cost money.
 * Owns: the section set, the danger-word regex, the length bound, and the
 *   enumeration used by views, tests and gates.
 * Consumes: nothing (pure data + pure functions; takes dicts as arguments).
 * Side effects: none beyond defining the global RiskKeys. Never throws.
 * Created by: building-vanilla-slices skill, i18n-machine-translation plan
 *   (spec §2). Mirrors the spec constants EXACTLY — if the spec changes,
 *   this file and tooling/i18n-risk-keys-test.js change together.
 *
 * Why a rule and not a hand-written list: the signing path is the risk, and
 * a hand-maintained list silently rots (see i18n allowlist rot). A rule
 * derived from the English source cannot forget a new operation.
 */
var RiskKeys = (function () {
  "use strict";

  /* Sections whose every string is high-risk: auth, signing, irreversible
   * actions, recovery. Keyed by the top-level segment of the locale key.
   * Frozen: this object IS the rule, so no consumer may edit it mid-session.
   * `security` and `backup` are not top-level sections in the locale dicts
   * today — they stay as harmless defensive data (an old dict or a new
   * section may legitimately carry that name). */
  var HIGH_RISK_SECTIONS = Object.freeze({
    unlockconfirm: 1, auth: 1, createaccount: 1, createworker: 1,
    vesting: 1, proposal: 1, proposals_ticket: 1, confirm: 1,
    ticket: 1, tickets: 1, htlc: 1, transfer: 1, credit: 1,
    samet: 1, wallet: 1, security: 1, backup: 1, debit: 1,
    password: 1, approval: 1
  });

  /* Danger wording, matched against the ENGLISH value only. Matching a
   * translation would make the rule drift per locale.
   *
   * Two boundaries make this regex honest, and both are load-bearing:
   *  - The LEADING \b is why `sign` never fires inside `design` or `assign`:
   *    `e` and `s` are word characters, so there is no boundary before the
   *    `sign` inside those words.
   *  - Every alternative therefore carries its OWN inflection group before
   *    the trailing \b. A bare stem + trailing \b can never match its own
   *    inflections (the next character is a word character, so \b fails):
   *    `irreversib` missed "irreversible", `sign` missed "signed" — exactly
   *    the money words this rule exists to catch. */
  var DANGER_RE = /\b(sign(s|ed|ing|ature|atures)?|send(s|ing|er|ers)?|sent|irreversib(le|ly|ility)|permanent(ly)?|unrecover(able|ably|ed)?|passwords?|private keys?|brainkeys?|backups?|scam(s|mer|mers|ming)?|never share|withdraw(s|al|als|able|ables|ing|n|ne)??|delegat(e|ed|es|ing|ion|ions)|vest(ed|ing)?|memos?)\b/i;

  /* Above this, dual-line renders as two walls of text; those strings are
   * covered by the page-level limitations warning instead. */
  var MAX_RISK_LEN = 120;

  /* isHighRisk: true when key is high-risk for the given English value.
   * @param {string} key dotted locale key (top-level segment = section)
   * @param {string} [enValue] the en.json value for that key
   * @returns {boolean} never throws; empty/missing values are not high-risk */
  function isHighRisk(key, enValue) {
    if (typeof key !== "string" || !key) return false;
    if (typeof enValue !== "string" || !enValue) return false;
    if (enValue.length > MAX_RISK_LEN) return false;
    var section = key.split(".")[0];
    /* hasOwnProperty, not a plain read: inherited members ("constructor",
     * "toString", ...) are truthy, so "constructor.x" would be high-risk. */
    if (Object.prototype.hasOwnProperty.call(HIGH_RISK_SECTIONS, section) &&
        HIGH_RISK_SECTIONS[section]) return true;
    return DANGER_RE.test(enValue);
  }

  /* listFor: every key of dict that is high-risk, sorted ascending.
   * @param {Object<string,string>} dict flattened locale dict
   * @param {Object<string,string>} enDict flattened en.json dict
   * @returns {string[]} sorted, unique; empty when either input is absent */
  function listFor(dict, enDict) {
    if (!dict || !enDict) return [];
    var out = [], k;
    for (k in dict) {
      if (!Object.prototype.hasOwnProperty.call(dict, k)) continue;
      if (isHighRisk(k, enDict[k])) out.push(k);
    }
    return out.sort();
  }

  return {
    HIGH_RISK_SECTIONS: HIGH_RISK_SECTIONS,
    MAX_RISK_LEN: MAX_RISK_LEN,
    isHighRisk: isHighRisk,
    listFor: listFor
  };
}());

if (typeof module !== "undefined" && module.exports) module.exports = RiskKeys;
```

Wire the script into `vanilla/index.html` immediately before `js/i18n.js`, and add to `vanilla/js/globals.d.ts`:

```ts
declare var RiskKeys: {
  HIGH_RISK_SECTIONS: { [section: string]: number };
  MAX_RISK_LEN: number;
  isHighRisk(key: string, enValue?: string): boolean;
  listFor(dict: { [key: string]: string }, enDict: { [key: string]: string }): string[];
};
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `node tooling/i18n-risk-keys-test.js`
Expected: PASS — `OK: i18n-risk-keys (1118 high-risk keys in es)`.

- [ ] **Step 5: Commit**

```bash
git add vanilla/js/i18n/risk-keys.js vanilla/index.html vanilla/js/globals.d.ts tooling/i18n-risk-keys-test.js
git commit -m "feat(i18n): high-risk key rule as one auditable source of truth

Section set + danger-word regex + 120-char bound, matching spec §2
exactly. Pure functions, no globals beyond RiskKeys, so the signing-path
rule cannot drift per locale the way a hand-written list would."
```

---

### Task 2: `i18n.js` — provenance, `enFor`, and v1/v2 `_meta`

**Files:**
- Modify: `vanilla/js/i18n.js` (`allowlisted` ~line 44, plus new exports)
- Test: `tooling/i18n-provenance-test.js`

**Interfaces:**
- Consumes: `RiskKeys` (not strictly — listed for ordering clarity; Task 1 is independent).
- Produces: three new `I18n` methods used by Tasks 3-6 —
  - `I18n.enFor(key)` → `string | undefined` (English source for `key`, always available)
  - `I18n.provenance(code)` → `"machine" | "human" | "none"` (`"none"` = not loaded, or `en`)
  - `I18n.isMachineLocale(code)` → `boolean` (true only when `provenance === "machine"`)

`allowlisted` becomes version-aware: v2 dicts are read from `_meta.coverage`, v1 from `_meta.translated`.

- [ ] **Step 1: Write the failing test**

`tooling/i18n-provenance-test.js`:

```js
/* i18n-provenance-test: the honesty surfaces all ask the same three
 * questions (is this locale machine-filled, what is the English source,
 * is this key verified). They must answer from the registry, never from
 * a re-read of the file, so all three are pinned here. */
"use strict";
var assert = require("assert");
var fs = require("fs");
var path = require("path");
var vm = require("vm");

var ROOT = path.join(__dirname, "..");
var sandbox = { console: console, fetch: function () { return Promise.reject(new Error("offline")); } };
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(path.join(ROOT, "vanilla/js/i18n.js"), "utf8"), sandbox);
var I18n = sandbox.I18n;

assert.strictEqual(typeof I18n.enFor, "function", "enFor exists");
assert.strictEqual(typeof I18n.provenance, "function", "provenance exists");
assert.strictEqual(typeof I18n.isMachineLocale, "function", "isMachineLocale exists");

/* en is never a machine locale and never needs a warning. */
assert.strictEqual(I18n.provenance("en"), "none");
assert.strictEqual(I18n.isMachineLocale("en"), false);

/* An unloaded or unknown locale reports "none" — never a false warning. */
assert.strictEqual(I18n.provenance("zz"), "none");
assert.strictEqual(I18n.isMachineLocale("zz"), false);

/* enFor resolves against the English master even before any locale loads:
 * the whole point is that the reference text is always available. */
var k = "menu.dashboard";
var en = I18n.enFor(k);
assert.strictEqual(typeof en, "string");
assert.ok(en.length > 0, "enFor resolves a real key");
assert.strictEqual(I18n.enFor("no.such.key"), undefined);

console.log("OK: i18n-provenance");
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `node tooling/i18n-provenance-test.js`
Expected: FAIL — `enFor is not a function`.

- [ ] **Step 3: Implement**

In `vanilla/js/i18n.js`, replace `allowlisted` and add the three methods:

```js
  /* Allowlist gate, version-aware. v2 dicts declare `coverage` ("this dict
   * has a value for every key"); v1 dicts declare `translated` ("these keys
   * are translated"). Reading the wrong one silently disables the fallback,
   * so the version decides which field is authoritative. */
  function allowlisted(code, key) {
    if (code === "en") return true;
    var dict = registry[code];
    if (!dict || !dict._meta) return false;
    var list = (dict._meta.version === 2) ? dict._meta.coverage : dict._meta.translated;
    if (!Array.isArray(list)) return false;
    return list.indexOf(key) !== -1;
  }

  /* enFor: the English source text for a key, from the en master seeded at
   * init. This is what makes dual-line possible without the view having to
   * thread a second string through every call site.
   * @param {string} key dotted locale key
   * @returns {string|undefined} undefined when unknown — callers render plain
   *   text rather than an empty English line. Never throws. */
  function enFor(key) {
    return lookup(registry.en, key);
  }

  /* provenance: review state of a dict, from _meta.provenance (v2).
   * @param {string} code locale code
   * @returns {"machine"|"human"|"none"} "none" for en, unloaded and unknown
   *   locales, so a missing dict can never render a false warning. */
  function provenance(code) {
    if (code === "en") return "none";
    var dict = registry[code];
    if (!dict || !dict._meta || dict._meta.version !== 2) return "none";
    return dict._meta.provenance === "machine" ? "machine" : "human";
  }

  /* isMachineLocale: true only when the active dict is machine-filled and
   * unverified — the single condition the badge and dual-line check. */
  function isMachineLocale(code) {
    return provenance(code) === "machine";
  }
```

Export all three on the module's public object (add to the existing `return { ... }`).

- [ ] **Step 4: Run the test to verify it passes**

Run: `node tooling/i18n-provenance-test.js`
Expected: PASS — `OK: i18n-provenance`.

- [ ] **Step 5: Commit**

```bash
git add vanilla/js/i18n.js tooling/i18n-provenance-test.js
git commit -m "feat(i18n): provenance + enFor + version-aware allowlist

enFor resolves the English source from the seeded master so dual-line
needs no second string threaded through call sites. provenance() returns
none for en/unloaded/unknown so a missing dict can never show a false
warning. allowlisted reads _meta.coverage on v2 dicts, _meta.translated
on v1."
```

---

### Task 3: `RiskText` — the dual-line widget

**Files:**
- Create: `vanilla/js/ui/risk-text.js`
- Test: `tooling/risk-text-test.js`
- Modify: `vanilla/index.html`, `vanilla/js/globals.d.ts`, `vanilla/css/app.css`

**Interfaces:**
- Consumes: `I18n.isMachineLocale`, `I18n.enFor`, `DOM.el`, `DOM.touchable`.
- Produces: `RiskText.render(doc, text, key)` → `Element` and `RiskText.wrap(doc, text, key)` → `Element` (alias for row use), plus `RiskText.isActive()` → `boolean`.

Behaviour contract: when the active locale is machine-filled, `key` is non-empty, and `I18n.enFor(key)` is a non-empty string **different** from `text`, return a `div.i18n-risk` containing the native `span`, a `button.i18n-risk-star` (`aria-expanded="false"`, `type="button"`), and a hidden `div.i18n-risk-en` holding the English. Otherwise return a plain text node wrapper (`span.i18n-risk-plain`) so callers never branch.

- [ ] **Step 1: Write the failing test**

`tooling/risk-text-test.js`:

```js
/* risk-text-test: dual-line is the honesty surface on the signing path,
 * so its three modes are pinned: dual-line when machine+key+english, plain
 * when english, and plain when verified/human. The asterisk must be a real
 * button (no hover-only affordance, AGENTS.md §3.6). */
"use strict";
var assert = require("assert");
var fs = require("fs");
var path = require("path");

var ROOT = path.join(__dirname, "..");
var riskSrc = fs.readFileSync(path.join(ROOT, "vanilla/js/ui/risk-text.js"), "utf8");

/* Minimal DOM good enough for the widget: exercises the real module code
 * without pulling in a browser. Anything richer is the browser probe's job
 * (tooling/visual/). */
function el(tag) {
  var node = {
    tagName: tag.toUpperCase(), children: [], attrs: {}, style: {},
    className: "", hidden: false, type: "", textContent: "",
    setAttribute: function (k, v) { this.attrs[k] = v; },
    getAttribute: function (k) { return this.attrs[k]; },
    appendChild: function (c) { this.children.push(c); return c; },
    addEventListener: function () {}
  };
  return node;
}
global.document = { createElement: el };
global.DOM = { el: function (d, tag, text, cls) {
  var n = d.createElement(tag);
  if (text) n.textContent = text;
  if (cls) n.className = cls;
  return n;
}, touchable: function (n) { n.attrs["data-touch"] = "1"; return n; } };
global.Event = { delegate: function () {} };

var machine = true;
global.I18n = {
  isMachineLocale: function () { return machine; },
  enFor: function (k) {
    if (k === "unlockconfirm.confirm") return "Unlock to sign";
    if (k === "menu.dashboard") return "Dashboard";
    return undefined;
  }
};

var sandbox = { document: global.document, DOM: global.DOM, I18n: global.I18n, Event: global.Event };
var vm = require("vm");
vm.createContext(sandbox);
vm.runInContext(riskSrc, sandbox);
var RiskText = sandbox.RiskText;

function find(node, cls) {
  if (node.className === cls) return node;
  for (var i = 0; i < (node.children || []).length; i++) {
    var hit = find(node.children[i], cls);
    if (hit) return hit;
  }
  return null;
}

/* 1. machine locale + high-risk key -> dual-line with asterisk. */
var node = RiskText.render(document, "Desbloquear para firmar", "unlockconfirm.confirm");
assert.strictEqual(node.className, "i18n-risk", "dual-line wrapper");
var star = find(node, "i18n-risk-star");
assert.ok(star, "asterisk exists");
assert.strictEqual(star.tagName, "BUTTON", "asterisk is a real button");
assert.strictEqual(star.attrs["aria-expanded"], "false", "starts collapsed");
assert.strictEqual(star.attrs.type, "button", "never submits a form");
var en = find(node, "i18n-risk-en");
assert.ok(en, "english line exists");
assert.strictEqual(en.hidden, true, "english starts hidden");
assert.ok(en.textContent.indexOf("Unlock to sign") !== -1, "english text is the reference");

/* 2. no key -> plain (dynamic values: amounts, ids, symbols). */
var plain = RiskText.render(document, "1.234,56 BTS", null);
assert.strictEqual(plain.className, "i18n-risk-plain", "dynamic values stay plain");

/* 3. english locale -> plain even for a high-risk key. */
var same = RiskText.render(document, "Unlock to sign", "unlockconfirm.confirm");
assert.strictEqual(same.className, "i18n-risk-plain", "no dual-line in english");

/* 4. machine locale OFF (human-reviewed) -> plain. */
machine = false;
var human = RiskText.render(document, "Desbloquear para firmar", "unlockconfirm.confirm");
assert.strictEqual(human.className, "i18n-risk-plain", "verified locales lose the asterisk");
machine = true;

console.log("OK: risk-text");
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `node tooling/risk-text-test.js`
Expected: FAIL — ENOENT on `vanilla/js/ui/risk-text.js`.

- [ ] **Step 3: Implement**

`vanilla/js/ui/risk-text.js`:

```js
/* risk-text: dual-line locale string — the native text with the English
 * reference one tap away. This is the honesty surface for strings where
 * misreading costs money (spec §4.1).
 * Owns: deciding dual-line vs plain, the asterisk disclosure, the
 *   back-link to the limitations article.
 * Consumes: I18n.isMachineLocale/enFor, DOM.el, DOM.touchable, Event.delegate.
 * Side effects: attaches one delegated click handler on first render.
 * Created by: building-vanilla-slices skill, i18n-machine-translation plan.
 * Failures: never throws — an unknown key or missing English degrades to
 *   plain text, which is the honest fallback (better a missing reference
 *   than a wrong one). */
var RiskText = (function () {
  "use strict";

  var ARTICLE = "#/help/translation-limitations";
  var bound = false;
  var uid = 0;

  /* shouldDual: the one decision, in one place so tests and views agree.
   * @param {string} [key] dotted locale key, or falsy for dynamic values
   * @param {string} text the already-translated text being displayed
   * @returns {boolean} true only when: machine locale, a key, an English
   *   source, and that source differing from what is displayed. */
  function shouldDual(key, text) {
    if (!key || typeof text !== "string" || !text) return false;
    if (typeof I18n === "undefined" || !I18n.isMachineLocale || !I18n.isMachineLocale()) return false;
    var src = I18n.enFor(key);
    return typeof src === "string" && !!src && src !== text;
  }

  /* render: the string, dual-line when warranted, plain otherwise.
   * @param {Document} doc owner document (callers pass theirs)
   * @param {string} text translated text to display
   * @param {string} [key] dotted locale key enabling the English reference
   * @returns {Element} span.i18n-risk-plain or div.i18n-risk; never a bare
   *   string, so callers can append unconditionally. Never throws. */
  function render(doc, text, key) {
    var str = (text === undefined || text === null) ? "" : String(text);
    if (!shouldDual(key, str)) {
      return DOM.el(doc, "span", str, "i18n-risk-plain");
    }
    uid += 1;
    var enId = "i18n-risk-en-" + uid;
    var wrap = DOM.el(doc, "div", null, "i18n-risk");
    wrap.appendChild(DOM.el(doc, "span", str, "i18n-risk-native"));

    var star = DOM.el(doc, "button", "*", "i18n-risk-star");
    star.type = "button";
    star.setAttribute("aria-expanded", "false");
    star.setAttribute("aria-controls", enId);
    star.setAttribute("aria-label", "Show the English reference for this line");
    DOM.touchable(star);
    wrap.appendChild(star);

    var en = DOM.el(doc, "div", I18n.enFor(key), "i18n-risk-en");
    en.id = enId;
    en.hidden = true;
    wrap.appendChild(en);

    /* The asterisk routes to the caveat, not just the disclosure — the
     * user should be able to reach the limitations page from the exact
     * line they did not trust. */
    var more = DOM.el(doc, "a", "About these translations", "i18n-risk-more");
    more.href = ARTICLE;
    wrap.appendChild(more);

    if (!bound && typeof Event !== "undefined" && Event.delegate) {
      bound = Event.delegate(document, ".i18n-risk-star", "click", function (ev) {
        var btn = (ev && ev.currentTarget) ? ev.currentTarget : null;
        if (!btn) return;
        var host = btn.closest ? btn.closest(".i18n-risk") : btn.parentNode;
        var panel = host ? host.querySelector(".i18n-risk-en") : null;
        if (!panel) return;
        var open = btn.getAttribute("aria-expanded") === "true";
        btn.setAttribute("aria-expanded", open ? "false" : "true");
        panel.hidden = open;
      }) !== false;
    }
    return wrap;
  }

  return { render: render, isActive: function () { return shouldDual("", "x"); } };
}());
```

Add to `vanilla/css/app.css` (theme-token based, no new raw HEX):

```css
/* i18n dual-line: native text with the English reference one tap away.
   Tokens only — the three themes come free (principle #5). */
.i18n-risk { display: inline; }
.i18n-risk-native { }
.i18n-risk-star {
  background: none; border: 0; color: var(--link, #3d6d9e);
  cursor: pointer; font-size: 0.9em; padding: 0 0.2em; min-width: 44px;
  min-height: 44px; vertical-align: middle;
}
.i18n-risk-star:focus-visible { outline: 2px solid var(--focus, #3d6d9e); }
.i18n-risk-en {
  display: block; margin: 0.15em 0 0.35em; padding-left: 0.5em;
  border-left: 3px solid var(--rule, #d5d8dc); opacity: 0.85;
  font-size: 0.92em;
}
.i18n-risk-en[hidden] { display: none; }
.i18n-risk-more { display: none; }
.i18n-risk-plain { }
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `node tooling/risk-text-test.js`
Expected: PASS — `OK: risk-text`.

- [ ] **Step 5: Commit**

```bash
git add vanilla/js/ui/risk-text.js vanilla/css/app.css vanilla/index.html vanilla/js/globals.d.ts tooling/risk-text-test.js
git commit -m "feat(i18n): dual-line RiskText widget with asterisk disclosure

Native text plus English reference, the asterisk a real 44px button
with aria-expanded and aria-controls (no hover-only affordance). Degrades
to plain text when the locale is verified, the value is dynamic, or the
English source is unknown — a missing reference beats a wrong one."
```

---

### Task 4: Wire the signing path — `ConfirmDialog` + risk surfaces

**Files:**
- Modify: `vanilla/js/ui/confirm.js` (title + rows loop, lines ~98-127)
- Modify: the 16 `ConfirmDialog.show` call sites: add `titleKey` / `rows[i][3]` where the string is a static keyed label
- Test: `tooling/confirm-risk-test.js`

**Interfaces:**
- Consumes: `RiskText.render`, `I18n.enFor` (Task 2, 3).
- Produces: `ConfirmDialog.show` accepts two new optional fields — `cfg.titleKey` (string) and `rows[i][3]` (`termKey`, string) — and routes both through `RiskText.render`. Absent keys render exactly as before (plain), so no existing call site changes behaviour until it opts in.

- [ ] **Step 1: Write the failing test**

`tooling/confirm-risk-test.js`:

```js
/* confirm-risk-test: the signing dialog is where a misread string costs
 * money, so every row must be able to carry its locale key. This test
 * pins the row/title contract on the real module via the same tiny DOM
 * shim risk-text-test uses. */
"use strict";
var assert = require("assert");
var fs = require("fs");
var path = require("path");
var vm = require("vm");

var ROOT = path.join(__dirname, "..");

function el(tag) {
  return {
    tagName: tag.toUpperCase(), children: [], attrs: {}, style: {}, className: "",
    hidden: false, textContent: "", innerHTML: "", disabled: false,
    setAttribute: function (k, v) { this.attrs[k] = v; },
    getAttribute: function (k) { return this.attrs[k]; },
    appendChild: function (c) { this.children.push(c); return c; },
    removeChild: function (c) { this.children = this.children.filter(function (x) { return x !== c; }); },
    addEventListener: function () {}, removeEventListener: function () {},
    querySelector: function () { return null; }, focus: function () {}
  };
}
var doc = { createElement: el, body: el("body") };

var duals = [];
global.DOM = {
  el: function (d, tag, text, cls) { var n = d.createElement(tag); if (text) n.textContent = text; if (cls) n.className = cls; return n; },
  append: function (w) { (w.children || []).forEach(function () {}); },
  status: function () {}, error: function () {}, clear: function () {}, text: function () {}, attrs: function () {},
  touchable: function (n) { return n; }
};
global.I18n = { isMachineLocale: function () { return true; }, enFor: function (k) { return k === "confirm.sign" ? "Sign & Send" : undefined; } };
global.Event = { delegate: function () { return true; } };

var sandbox = { document: doc, DOM: global.DOM, I18n: global.I18n, Event: global.Event };
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(path.join(ROOT, "vanilla/js/ui/risk-text.js"), "utf8"), sandbox);
sandbox.RiskText.render = function (d, text, key) {
  duals.push({ text: text, key: key });
  var n = d.createElement("span"); n.className = key ? "i18n-risk" : "i18n-risk-plain"; return n;
};
sandbox.global = sandbox;
vm.runInContext(fs.readFileSync(path.join(ROOT, "vanilla/js/ui/confirm.js"), "utf8"), sandbox);
var ConfirmDialog = sandbox.ConfirmDialog;

duals.length = 0;
ConfirmDialog.show({
  title: "¿Firmar y enviar?",
  titleKey: "confirm.sign",
  rows: [["Firmar", "1.234,56 BTS", null, "confirm.sign"]],
  doc: doc
});

var keys = duals.map(function (d) { return d.key; });
assert.ok(keys.indexOf("confirm.sign") !== -1, "title key reached RiskText");
assert.ok(keys.indexOf("confirm.sign") !== -1, "row term key reached RiskText");
assert.ok(keys.indexOf(undefined) === -1, "every rendered text is keyed in this dialog");

/* Absent keys must still work — backwards compatibility for the 16
 * existing call sites until they opt in. */
duals.length = 0;
var box = ConfirmDialog.show({ title: "Cancel order?", rows: [["Amount", "12.0 BTS"]], doc: doc });
assert.ok(box, "dialog renders without any keys");
assert.deepStrictEqual(duals.map(function (d) { return d.key; }), [null, undefined]);

console.log("OK: confirm-risk");
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `node tooling/confirm-risk-test.js`
Expected: FAIL — keys never reach `RiskText` (`keys.indexOf("confirm.sign") === -1`).

- [ ] **Step 3: Implement**

In `vanilla/js/ui/confirm.js`, replace the title and row rendering:

```js
    box = mk(doc, "div", null, "confirm-dialog");
    /* Title and row terms go through RiskText so a machine-translated
     * signing dialog shows its English reference inline. No key = plain
     * text, which is why un-migrated call sites keep working untouched. */
    box.appendChild((typeof RiskText !== "undefined" && RiskText.render)
      ? RiskText.render(doc, title, cfg.titleKey || null)
      : mk(doc, "h3", title));
    list = mk(doc, "dl", null, "confirm");
    for (i = 0; i < rows.length; i++) {
      list.appendChild((typeof RiskText !== "undefined" && RiskText.render)
        ? RiskText.render(doc, rows[i][0], rows[i][3] || null)
        : mk(doc, "dt", rows[i][0]));
      dd = mk(doc, "dd", rows[i][1]);
      if (rows[i][2]) dd.title = rows[i][2];
      list.appendChild(dd);
    }
```

Then opt in the static-keyed call sites. For each `ConfirmDialog.show` whose `title` or a row term is a literal translated string, add the key — e.g. in `vanilla/js/ui/unlock-confirm.js` pass `titleKey: cfg.titleKey` through from `cfg`, and in `vanilla/js/builders/trade-cancel.js`:

```js
      dlg = ConfirmDialog.show({ title: "Cancel order " + id + "?", titleKey: "tradecancel.confirm_title",
```

Rule for the migration pass: **a row term gets `rows[i][3]` only when the term is a static keyed string.** Dynamic values (formatted amounts, asset symbols, object ids) get no key — they are locale-independent by §3.5 and must not be wrapped. Record the migrated keys in `docs/parity/i18n-machine-translation.md`.

- [ ] **Step 4: Run the test to verify it passes**

Run: `node tooling/confirm-risk-test.js`
Expected: PASS — `OK: confirm-risk`.

- [ ] **Step 5: Commit**

```bash
git add vanilla/js/ui/confirm.js vanilla/js/ui/unlock-confirm.js vanilla/js/builders/trade-cancel.js tooling/confirm-risk-test.js
git commit -m "feat(i18n): route ConfirmDialog title + row terms through RiskText

One code path gives all 78 operations the English reference. Rows gain an
optional 4th element (termKey) and the dialog an optional titleKey; both
absent means plain text, so existing call sites are unchanged until they
opt in. Dynamic values (amounts, symbols, ids) stay unwrapped per §3.5."
```

---

### Task 5: Header badge — machine locales only

**Files:**
- Create: `vanilla/js/ui/i18n-badge.js`
- Modify: `vanilla/index.html` (topbar slot), `vanilla/js/app.js` (mount + locale-change refresh), `vanilla/css/app.css`, `vanilla/js/globals.d.ts`
- Test: `tooling/i18n-badge-test.js`

**Interfaces:**
- Consumes: `I18n.provenance`, `I18n.locale()` (existing accessor, `vanilla/js/i18n.js:179`), `DOM.el`, `DOM.touchable`, `Event.delegate`.
- Produces: `I18nBadge.mount(doc, host)` → `void`, `I18nBadge.refresh()` → `void`, `I18nBadge.visible()` → `boolean`.

Behaviour: hidden (element removed) unless the active locale's provenance is `"machine"`. Collapsed shows a `button.i18n-badge` labelled `i18n`. Tapping sets `#i18n-badge-note` visible with `aria-live="polite"`, containing the warning sentence, a *Details* link to `#/help/translation-limitations`, and a *Help improve* link to the GitHub issues URL. Collapse is an explicit second tap; state persists in the session via a module-level boolean, not localStorage (no persistence of a warning dismissal).

- [ ] **Step 1: Write the failing test**

`tooling/i18n-badge-test.js`:

```js
/* i18n-badge-test: the badge must cost English and human-reviewed users
 * exactly zero pixels, and must never lie: an unloaded locale shows
 * nothing rather than a warning about a dict we cannot read. */
"use strict";
var assert = require("assert");
var fs = require("fs");
var path = require("path");
var vm = require("vm");

var ROOT = path.join(__dirname, "..");
function el(tag) {
  return { tagName: tag.toUpperCase(), children: [], attrs: {}, style: {}, className: "",
    hidden: false, textContent: "", href: "",
    setAttribute: function (k, v) { this.attrs[k] = v; },
    getAttribute: function (k) { return this.attrs[k]; },
    appendChild: function (c) { this.children.push(c); return c; },
    removeChild: function () {}, addEventListener: function () {},
    querySelector: function () { return null; }, closest: function () { return null; } };
}
var host = el("div");
var prov = "none";
global.DOM = {
  el: function (d, tag, text, cls) { var n = d.createElement(tag); if (text) n.textContent = text; if (cls) n.className = cls; return n; },
  clear: function (n) { n.children = []; }, text: function (n, t) { n.textContent = t; },
  attrs: function () {}, append: function () {}, touchable: function (n) { return n; }
};
global.I18n = { provenance: function () { return prov; }, locale: function () { return "es"; } };
global.Event = { delegate: function () { return true; } };

var sandbox = { document: { createElement: el }, DOM: global.DOM, I18n: global.I18n, Event: global.Event };
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(path.join(ROOT, "vanilla/js/ui/i18n-badge.js"), "utf8"), sandbox);
var B = sandbox.I18nBadge;

prov = "none";
B.mount(document, host);
assert.strictEqual(host.children.length, 0, "en / unloaded locales pay zero pixels");
assert.strictEqual(B.visible(), false);

prov = "human";
B.mount(document, host);
assert.strictEqual(host.children.length, 0, "human-reviewed locales pay zero pixels");

prov = "machine";
B.mount(document, host);
/* Two nodes: the chip, then the hidden note it expands. The chip itself
 * stays one 44px target. */
assert.strictEqual(host.children.length, 2, "machine locale shows chip + note");
assert.strictEqual(B.visible(), true);
assert.strictEqual(host.children[0].className, "i18n-badge", "collapsed by default");
assert.strictEqual(host.children[0].tagName, "BUTTON", "the badge is a real control");
assert.ok(host.children[0].attrs["aria-expanded"] === "false", "starts collapsed");
assert.strictEqual(host.children[1].hidden, true, "note starts hidden");

/* Both links the warning promises must exist in the module source. */
var src = fs.readFileSync(path.join(ROOT, "vanilla/js/ui/i18n-badge.js"), "utf8");
assert.ok(src.indexOf("#/help/translation-limitations") !== -1, "details link present");
assert.ok(src.indexOf("issues/new?labels=translation") !== -1, "help-improve link present");
assert.ok(src.indexOf("aria-live") !== -1, "expansion is announced");

console.log("OK: i18n-badge");
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `node tooling/i18n-badge-test.js`
Expected: FAIL — ENOENT on `vanilla/js/ui/i18n-badge.js`.

- [ ] **Step 3: Implement**

`vanilla/js/ui/i18n-badge.js`:

```js
/* i18n-badge: the one persistent honesty signal — a collapsed "i18n" chip
 * in the header that exists only while the active locale is machine-filled
 * and unverified (spec §4.3).
 * Owns: mount/refresh/visible and the collapsed↔expanded toggle.
 * Consumes: I18n.provenance, I18n.locale(), DOM.el/clear/touchable,
 *   Event.delegate. Uses the shared module-level i18n keys.
 * Side effects: replaces the contents of the host element on every mount.
 * Created by: building-vanilla-slices skill, i18n-machine-translation plan.
 * Mirrors the extension shield-badge precedent: hidden means truly hidden,
 * so English and human-reviewed locales pay zero pixels (principle #7).
 * Failures: never throws — a host that cannot be written leaves the bar as
 * it was rather than breaking the header. */
var I18nBadge = (function () {
  "use strict";

  var ISSUES = "https://github.com/litepresence/bitshares-vanilla-ui/issues/new?labels=translation";
  var ARTICLE = "#/help/translation-limitations";
  var host = null;
  var shown = false;

  /* note: the expanded explanation. Built as a sibling of the chip so the
   * chip itself stays a single 44px target and the panel is the only thing
   * that appears on expansion. */
  function buildNote(doc) {
    var note = DOM.el(doc, "div", null, "i18n-badge-note");
    note.id = "i18n-badge-note";
    note.setAttribute("role", "note");
    note.setAttribute("aria-live", "polite");
    note.hidden = true;
    var text = DOM.el(doc, "p", t("i18n.badge_body",
      "These translations were written by a machine and have not been checked by a human. The English text is always one tap away on any line marked with *."),
      "i18n-badge-text");
    note.appendChild(text);
    var links = DOM.el(doc, "p", null, "i18n-badge-links");
    var more = DOM.el(doc, "a", t("i18n.badge_details", "What this means"), "i18n-badge-link");
    more.href = ARTICLE;
    var help = DOM.el(doc, "a", t("i18n.badge_improve", "Help improve this translation"), "i18n-badge-link");
    help.href = ISSUES;
    help.target = "_blank";
    help.rel = "noopener noreferrer";
    DOM.touchable(more);
    DOM.touchable(help);
    links.appendChild(more);
    links.appendChild(help);
    note.appendChild(links);
    return note;
  }

  /* mount: (re)build the badge into host for the current locale.
   * @param {Document} doc owner document
   * @param {Element|null} hostEl container in the header
   * @returns {void} never throws. */
  function mount(doc, hostEl) {
    if (!hostEl) return;
    host = hostEl;
    refresh();
  }

  /* refresh: re-evaluate visibility for the active locale. Called on boot
   * and on every locale change.
   * @returns {void} never throws. */
  function refresh() {
    if (!host) return;
    var doc = host.ownerDocument || document;
    var machine = (typeof I18n !== "undefined" && I18n.provenance)
      ? (I18n.provenance(I18n.locale()) === "machine") : false;
    DOM.clear(host);
    if (!machine) { shown = false; return; }
    var btn = DOM.el(doc, "button", "i18n", "i18n-badge");
    btn.type = "button";
    btn.setAttribute("aria-expanded", "false");
    btn.setAttribute("aria-controls", "i18n-badge-note");
    btn.setAttribute("aria-label", t("i18n.badge_label", "Translation status: machine translated, not human verified"));
    DOM.touchable(btn);
    var note = buildNote(doc);
    btn.addEventListener("click", function () {
      var open = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", open ? "false" : "true");
      note.hidden = open;
    });
    host.appendChild(btn);
    host.appendChild(note);
    shown = true;
  }

  /* visible: whether the badge is currently mounted. English and
   * human-reviewed locales return false, which is the zero-pixel promise.
   * @returns {boolean} */
  function visible() { return shown === true; }

  return { mount: mount, refresh: refresh, visible: visible };
}());
```

In `vanilla/index.html` add the slot inside `header.topbar`, before the nav toggle:

```html
  <span id="i18n-badge-slot" class="i18n-badge-slot"></span>
```

In `vanilla/js/app.js` `buildNav` (after the directory is appended) call:

```js
    /* Machine-locale honesty chip; a no-op for en and reviewed locales. */
    try {
      var slot = document.getElementById("i18n-badge-slot");
      if (slot && typeof I18nBadge !== "undefined") I18nBadge.mount(document, slot);
    } catch (e) { /* header stands without the chip */ }
```

and on locale change (wherever the existing locale switch re-renders the shell) call `I18nBadge.refresh()`.

CSS appended to `vanilla/css/app.css`:

```css
/* i18n honesty chip: zero pixels unless the locale is machine-filled. */
.i18n-badge-slot { display: inline-flex; align-items: center; }
.i18n-badge {
  font-size: 12px; padding: 0 8px; min-height: 44px; cursor: pointer;
  border: 1px solid var(--rule, #d5d8dc); border-radius: 3px;
  background: var(--panel, #fff); color: var(--text, #333);
}
.i18n-badge:focus-visible { outline: 2px solid var(--focus, #3d6d9e); }
.i18n-badge-note {
  position: absolute; right: 8px; top: 100%; max-width: 340px; z-index: 60;
  padding: 10px 12px; font-size: 13px; line-height: 1.45;
  background: var(--panel, #fff); border: 1px solid var(--rule, #d5d8dc);
  border-radius: 3px;
}
.i18n-badge-note[hidden] { display: none; }
.i18n-badge-links { margin: 6px 0 0; display: flex; gap: 12px; flex-wrap: wrap; }
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `node tooling/i18n-badge-test.js`
Expected: PASS — `OK: i18n-badge`.

- [ ] **Step 5: Commit**

```bash
git add vanilla/js/ui/i18n-badge.js vanilla/index.html vanilla/js/app.js vanilla/css/app.css vanilla/js/globals.d.ts tooling/i18n-badge-test.js
git commit -m "feat(i18n): header honesty chip for machine-filled locales

Mounts only when the active dict is provenance=machine, so English and
human-reviewed locales pay zero pixels (extension-badge precedent). One
44px chip, tap expands an aria-live note with the limitations link and
the GitHub issues correction route. No localStorage: a warning must not
be permanently dismissible."
```

---

### Task 6: Limitations article + sitemap + glossary

**Files:**
- Modify: `vanilla/js/views/help-ui.js` (`TOPICS` array ~line 43, `BODY_DEFAULTS` ~line 116, sitemap array)
- Modify: `vanilla/locales/en.json` + all 11 non-en dicts (new `help.topic_translation_limitations_*` and `i18n.*` keys)
- Create: `docs/i18n-glossary/es.md`
- Test: `tooling/help-test.js` (extend), `tooling/i18n-glossary-test.js`

**Interfaces:**
- Consumes: `TOPICS` entry `[slug, titleKey-ish title, blurb, href]`; the article slug is `translation-limitations`; `I18n` keys are shared module-level `i18n.badge_*`.
- Produces: route `#/help/translation-limitations` reachable from the badge and listed in `BODY_DEFAULTS["sitemap"]`.

- [ ] **Step 1: Write the failing test**

Extend `tooling/help-test.js` with a case asserting the new slug is present in both `TOPICS` and the sitemap array, and that its i18n keys exist in `en.json` and all 11 other dicts. Create `tooling/i18n-glossary-test.js` asserting the glossary lists every term used by es high-risk keys:

```js
/* i18n-glossary-test: the glossary is the artifact external auditors read,
 * so it must actually cover the dangerous vocabulary, not just exist. */
"use strict";
var assert = require("assert");
var fs = require("fs");
var path = require("path");

var ROOT = path.join(__dirname, "..");
var glossary = fs.readFileSync(path.join(ROOT, "docs/i18n-glossary/es.md"), "utf8");
var REQUIRED = ["brainkey", "witness", "committee", "worker", "proxy", "vesting",
  "HTLC", "swap", "slate", "liquidity pool", "credit offer", "ticket",
  "proposal", "precision", "orderbook", "limit order", "fee"];
var missing = REQUIRED.filter(function (t) {
  return glossary.toLowerCase().indexOf(t.toLowerCase()) === -1;
});
assert.deepStrictEqual(missing, [], "glossary covers the BitShares term list");
console.log("OK: i18n-glossary (" + REQUIRED.length + " terms)");
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `node tooling/i18n-glossary-test.js`
Expected: FAIL — ENOENT on `docs/i18n-glossary/es.md`.

- [ ] **Step 3: Implement**

Add to `TOPICS` in `vanilla/js/views/help-ui.js`:

```js
    ["translation-limitations", "Translation limitations", "Machine-filled translations are labeled; the English reference is always one tap away. Help us fix a line.", "#/"],
```

Add to `BODY_DEFAULTS` a `translation-limitations` array whose first element is the caveat paragraph and which renders a per-language confidence table. Add the slug to the `sitemap` array under a new `# Wallet` sibling section. Add keys `help.topic_translation_limitations_title` / `_body` plus `help.confidence_high` / `_good` / `_moderate` to `en.json` and the other 11 dicts (Phase C fills the Spanish values; other locales get them in Phase D).

Write `docs/i18n-glossary/es.md` with a table: English term | Spanish term | note — covering at minimum the 17 REQUIRED terms plus `precision`, `share`, `balance`, `orderbook`, `limit order`, `market`, `block`, `transaction`, `asset`, `smartcoin`, `collateral`, `proposal`, `account`.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `node tooling/i18n-glossary-test.js && node tooling/help-test.js && python3 tooling/check_i18n.py`
Expected: all PASS. (`check_i18n` must already pass because the new keys are English stubs in non-en dicts — honest, and the gate accepts that.)

- [ ] **Step 5: Commit**

```bash
git add vanilla/js/views/help-ui.js vanilla/locales/ docs/i18n-glossary/es.md tooling/help-test.js tooling/i18n-glossary-test.js
git commit -m "feat(i18n): translation-limitations article, sitemap entry, es glossary

New help article reachable from the badge and listed in the sitemap
(AGENTS.md rule 10). Carries the per-language confidence table
(hi/tr moderate, flagged for review). Glossary covers the BitShares term
list so external audits correct a term once."
```

---

### Task 7: Gates learn `_meta` version 2

**Files:**
- Modify: `tooling/check_i18n.py` (locale loop ~lines 97-140)
- Modify: `tooling/validate_translations.py` (check 6)
- Test: `tooling/i18n-v2-meta-test.js`

**Interfaces:**
- Consumes: nothing from earlier tasks (pure tooling).
- Produces: `check_i18n.py` accepts a v2 dict when `coverage` == the en key set, `verified ⊆ coverage`, `high_risk ⊆ coverage`, every `verified` key differs from en; identical-to-en **claimed** keys are reported as a review note (not a failure) for v2, while a **v1** dict claiming an identical key still fails. `validate_translations.py <code>` accepts the v2 `_meta` in check 6.

- [ ] **Step 1: Write the failing test**

`tooling/i18n-v2-meta-test.js` builds temporary v1/v2 dicts in a scratch dir and runs both tools against them. Simpler and equally strong: a Python-free shell assertion inside the test using `child_process`:

```js
/* i18n-v2-meta-test: the gate must accept a well-formed v2 dict, reject a
 * v2 dict that claims an English value as verified, and still reject the
 * old v1 lie. This is the guard that stops the rot from coming back. */
"use strict";
var assert = require("assert");
var fs = require("fs");
var path = require("path");
var cp = require("child_process");

var ROOT = path.join(__dirname, "..");
var LOCALES = path.join(ROOT, "vanilla/locales");
var en = JSON.parse(fs.readFileSync(path.join(LOCALES, "en.json"), "utf8"));

function keys(d, p) {
  var out = [], k;
  p = p || "";
  for (k in d) {
    if (k === "_meta") continue;
    if (typeof d[k] === "object") out = out.concat(keys(d[k], p + k + "."));
    else out.push(p + k);
  }
  return out.sort();
}
var enKeys = keys(en);

function run(args) {
  try { return { code: 0, out: cp.execSync("python3 " + args.map(function (a) { return JSON.stringify(a); }).join(" "), { cwd: ROOT, stdio: ["ignore", "pipe", "pipe"] }).toString() }; }
  catch (e) { return { code: e.status || 1, out: (e.stdout || "").toString() + (e.stderr || "").toString() }; }
}

/* A well-formed v2 dict validates. */
var good = { _meta: { version: 2, provenance: "machine", coverage: enKeys, verified: [], high_risk: ["unlockconfirm.confirm"] } };
(function fill(o, src) {
  for (var i = 0; i < enKeys.length; i++) {
    var parts = enKeys[i].split(".");
    var node = o;
    for (var p = 0; p < parts.length - 1; p++) { node[parts[p]] = node[parts[p]] || {}; node = node[parts[p]]; }
    node[parts[parts.length - 1]] = src[enKeys[i]]; /* en is flat: index by the full dotted key */
  }
})(good, en);
var backup = fs.readFileSync(path.join(LOCALES, "es.json"), "utf8");
fs.writeFileSync(path.join(LOCALES, "es.json"), JSON.stringify(good, null, 2));
var r1 = run(["tooling/validate_translations.py", "es"]);
assert.strictEqual(r1.code, 0, "well-formed v2 dict validates: " + r1.out);

/* A v2 dict claiming an English value as verified is rejected. */
var bad = JSON.parse(JSON.stringify(good));
bad._meta.verified = ["menu.dashboard"]; /* menu.dashboard === "Dashboard" in en */
fs.writeFileSync(path.join(LOCALES, "es.json"), JSON.stringify(bad, null, 2));
var r2 = run(["tooling/validate_translations.py", "es"]);
assert.strictEqual(r2.code, 1, "verified-but-English is rejected");
assert.ok(/identical|verified/i.test(r2.out), "error names the problem: " + r2.out);

/* Restore. */
fs.writeFileSync(path.join(LOCALES, "es.json"), backup);
console.log("OK: i18n-v2-meta");
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `node tooling/i18n-v2-meta-test.js`
Expected: FAIL — `validate_translations.py` rejects the v2 `_meta` (check 6 requires `translated`).

- [ ] **Step 3: Implement**

In `tooling/validate_translations.py`, replace check 6 (lines 212-232) with a version-aware version and add the verified-differ rule. `en` is already loaded in `main()` (line 109) and `flatten(d, prefix="")` is the existing helper (line 79) — both are passed in rather than re-read:

```python
def check_meta_v2(data, en, en_keys):
    """Validate a _meta version-2 provenance dict.

    A v2 dict declares `coverage` ("this dict has a value for every key"),
    `provenance` (machine-filled vs human-reviewed) and two subsets,
    `verified` and `high_risk`. A key in `verified` whose value equals
    English is rejected: a human verified it, so an English value means the
    claim itself is wrong. Machine strings that merely coincide with
    English are fine here (loanwords); check_i18n reports those as a review
    note instead of failing them.
    """
    m = data.get("_meta") or {}
    problems = []
    if m.get("provenance") not in ("machine", "human"):
        problems.append("[6 _meta] provenance must be machine or human")
    if set(m.get("coverage") or []) != en_keys:
        only = sorted(set(m.get("coverage") or []) - en_keys)[:5]
        miss = sorted(en_keys - set(m.get("coverage") or []))[:5]
        problems.append("[6 _meta] coverage drift (extra=%s missing=%s)" % (only, miss))
    verified = set(m.get("verified") or [])
    if not verified <= en_keys:
        problems.append("[6 _meta] verified unknown keys: %s" % sorted(verified - en_keys)[:5])
    if not set(m.get("high_risk") or []) <= en_keys:
        problems.append("[6 _meta] high_risk unknown keys: %s"
                        % sorted(set(m.get("high_risk") or []) - en_keys)[:5])
    flat = flatten(data)
    en_flat = flatten(en)
    for k in sorted(verified):
        if flat.get(k) == en_flat.get(k):
            problems.append("[6 _meta] verified %s is identical to en" % k)
    return problems
```

Then at the check-6 call site:

```python
    meta = data.get("_meta")
    if not isinstance(meta, dict):
        problems.append("[6 _meta] _meta missing or not an object")
    elif meta.get("version") == 2:
        problems.extend(check_meta_v2(data, en, en_keys))
    else:
        ... the existing version-1 checks, unchanged ...
```

`--fix-meta` must also learn the v2 shape (it currently rewrites `_meta` to the v1 form, which would silently demote a v2 dict):

```python
    if (data.get("_meta") or {}).get("version") == 2:
        data["_meta"] = {"version": 2, "provenance": (data["_meta"].get("provenance") or "machine"),
                         "coverage": sorted(en_keys),
                         "verified": sorted(data["_meta"].get("verified") or []),
                         "high_risk": sorted(data["_meta"].get("high_risk") or [])}
    else:
        data["_meta"] = {"version": 1, "untranslated": False, "translated": sorted(en_keys)}
```

In `tooling/check_i18n.py`, add a v2 branch before the existing v1 checks so a v2 dict is validated by `coverage` completeness plus `verified` honesty, and identical-to-en values become a reported note rather than a failure:

```python
        if m.get("version") == 2:
            if m.get("provenance") not in ("machine", "human"):
                problems.append("%s _meta.provenance must be machine|human" % code)
            if set(m.get("coverage") or []) != en_keys:
                problems.append("%s _meta.coverage drift" % code)
            verified = set(m.get("verified") or [])
            if not verified <= en_keys:
                problems.append("%s _meta.verified unknown keys" % code)
            if not set(m.get("high_risk") or []) <= en_keys:
                problems.append("%s _meta.high_risk unknown keys" % code)
            for k in sorted(verified):
                if flat.get(k) == en_flat.get(k):
                    problems.append("%s _meta.verified %s identical to en" % (code, k))
                    break
            # machine strings may legitimately equal en (loanwords): note, don't fail
            notes.append("%s: %d machine value(s) equal en (review candidates)"
                         % (code, sum(1 for k in en_keys if flat.get(k) == en_flat.get(k))))
        elif code == "en":
            pass
        elif not is_full and m.get("untranslated") is not True:
            ... existing honesty branch ...
```

(`notes` is a new list the reporter prints after `problems`.)

- [ ] **Step 4: Run the test to verify it passes**

Run: `node tooling/i18n-v2-meta-test.js && python3 tooling/check_i18n.py`
Expected: PASS — `OK: i18n-v2-meta` and `OK: 12 dicts key-complete ...`.

- [ ] **Step 5: Commit**

```bash
git add tooling/check_i18n.py tooling/validate_translations.py tooling/i18n-v2-meta-test.js
git commit -m "feat(i18n): gates learn _meta version 2

check_i18n validates coverage/verified/high_risk for v2 dicts, keeps the
v1 lie fatal, and downgrades identical-value to a review note (loanwords
are legitimate in machine text). validate_translations accepts the v2
shape and rejects a verified key whose value equals English."
```

---

### Task 8: Convert `es.json` to v2 (structure only, values untouched)

**Files:**
- Modify: `vanilla/locales/es.json`
- Test: `tooling/check_i18n.py`, `tooling/validate_translations.py es`

**Interfaces:**
- Consumes: `RiskKeys.listFor` (via a Node one-liner that prints the sorted list).
- Produces: `es.json._meta = {version:2, provenance:"machine", coverage:[...3921 en keys...], verified:[], high_risk:[...69 keys...]}`.

- [ ] **Step 1: Confirm the pre-state fails**

Run: `python3 tooling/validate_translations.py es`
Expected: FAIL — 688 missing keys (the honest gap Phase C closes).

- [ ] **Step 2: Rewrite `_meta` only, via a Node one-liner** (values untouched)

```bash
node -e '
const fs=require("fs"),vm=require("vm");
const ROOT="/workspace";
const sandbox={};vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(ROOT+"/vanilla/js/i18n/risk-keys.js","utf8"),sandbox);
const flat=(d,p="")=>{const o={};for(const k in d){if(k==="_meta")continue;const v=d[k];
  if(v&&typeof v==="object")Object.assign(o,flat(v,p+k+"."));else o[p+k]=v;}return o;};
const en=JSON.parse(fs.readFileSync(ROOT+"/vanilla/locales/en.json","utf8"));
const es=JSON.parse(fs.readFileSync(ROOT+"/vanilla/locales/es.json","utf8"));
const enFlat=flat(en), esFlat=flat(es);
es._meta={version:2,provenance:"machine",
  coverage:Object.keys(enFlat).sort(),
  verified:[],
  high_risk:sandbox.RiskKeys.listFor(esFlat,enFlat)};
fs.writeFileSync(ROOT+"/vanilla/locales/es.json",JSON.stringify(es,null,2)+"\n");
console.log("coverage",es._meta.coverage.length,"high_risk",es._meta.high_risk.length);
'
```

Expected output: `coverage 3921 high_risk 1118`.

- [ ] **Step 3: Verify**

Run: `python3 tooling/check_i18n.py && node tooling/i18n-v2-meta-test.js`
Expected: both PASS.

- [ ] **Step 4: Commit**

```bash
git add vanilla/locales/es.json
git commit -m "refactor(i18n): es.json to _meta v2 (coverage 3921, high_risk 69)

Structure only; no value changed. coverage declares 'every key has a
value', high_risk is enumerated from the shared rule rather than typed by
hand, verified starts empty because no human has reviewed anything."
```

---

### Task 9: Fill the es locale (688 strings) and prove the pilot

**Files:**
- Modify: `vanilla/locales/es.json` (688 values + `high_risk` stays as enumerated)
- Modify: `docs/i18n-glossary/es.md` (fill the Spanish column)
- Test: every gate in §8 of the spec

**Interfaces:**
- Consumes: the glossary from Task 6, the `RiskKeys` rule, `Format` (§3.5 — digits are never touched here).
- Produces: `es.json` with no English stub values, `provenance:"machine"` (never `"human"`), and every en key present.

- [ ] **Step 1: Capture the red state**

Run: `python3 tooling/validate_translations.py es`
Expected: FAIL listing the 688 missing keys (v2 `coverage` is declared but values are still English — the tool reports the honest gap).

- [ ] **Step 2: Fill the 688 values, section by section**

For each key in `coverage` whose current value equals the English value, write the Spanish translation into the existing nested position. Rules, in this precedence (spec §6):

1. **Byte-verbatim, never translated**: `%(name)s` placeholders (exact multiset), `1.2.x` object IDs, URLs, operation numbers, asset symbols, `settings.network_mainnet`/`network_testnet`/`custom_placeholder`/`pending`/`dash`/`theme_*`, `shell.brand`.
2. **Glossary wins** — one Spanish term per concept, reused at every occurrence (`docs/i18n-glossary/es.md`).
3. **Register**: informal *tú* for Spanish (wallet UI convention).
4. **Numbers**: Spanish decimal comma (`1.234,56`) **only** inside prose sentences that quote a figure; a bare value line is left alone because `Format` owns rendering (§3.5). Never re-format a chain integer by hand.
5. **Identical-to-English is allowed** for true loanwords (`DEX`, `HTLC`, `BitShares`, `BTS`); those stay English and are recorded in the review-note list from `check_i18n.py`, not faked.

Translate the **103 high-risk** strings with the most care (they render dual-line, so both the Spanish and the fact that an English reference exists are user-visible), then the **574** ordinary strings, then the **11** long help-prose bodies.

- [ ] **Step 3: Verify the fill**

Run: `python3 tooling/check_i18n.py && python3 tooling/validate_translations.py es && bash tooling/check_types.sh && python3 tooling/check_rot.py && node tooling/risk-text-test.js && node tooling/i18n-risk-keys-test.js && node tooling/i18n-badge-test.js && node tooling/confirm-risk-test.js && node tooling/i18n-v2-meta-test.js`
Expected: every command PASS; `validate_translations.py es` exits 0 **for the first time**.

- [ ] **Step 4: Fill the glossary's Spanish column**

For each of the 17 REQUIRED terms plus the account/asset/market nouns, write the Spanish term actually used in `es.json` (cross-check with grep so the glossary cannot drift from the strings).

Run: `node tooling/i18n-glossary-test.js`
Expected: PASS.

- [ ] **Step 5: Browser probe (three themes, 360px + desktop)**

Using `tooling/visual/` (Playwright, dev-only): capture, in `es` with `es.json` v2 —
  1. a normal page with the `i18n` chip visible,
  2. the chip expanded,
  3. a `ConfirmDialog` with dual-line rows and one asterisk revealed,
  4. `#/help/translation-limitations`.
Each in `ref-ui-theme`, `dex-ux-theme`, `vanilla-ui-theme`, at 360px and 1440px. Assert zero console errors from the screenshots' capture log.

- [ ] **Step 6: Commit**

```bash
git add vanilla/locales/es.json docs/i18n-glossary/es.md
git commit -m "feat(i18n): fill es locale to full coverage (machine, unverified)

688 strings: 103 high-risk dual-line, 11 long prose, 574 ordinary. Glossary
-constrained, placeholders/ids/URLs byte-verbatim, informal tú register,
decimal comma only inside prose. provenance stays machine — filling
strings is not verification. validate_translations es now exits 0."
```

---

## Self-Review

- **Spec coverage**: §3 data model → Task 2 + 8. §4.1 dual-line → Task 3. §4.2 mount points → Task 4. §4.3 badge → Task 5. §4.4 confidence + limitations page → Task 6. §5 glossary → Task 6 + 9. §6 fill rules → Task 9. §7 gates → Task 7. §8 verification → Task 9 Steps 3/5. §9 out-of-scope (no Crowdin, no scaling) → global constraints + this plan's boundary. RiskKeys rule (§2) → Task 1. Every section has a task.
- **Placeholder scan**: no TBD/TODO; every code block is complete; every command has an expected output; `en.json`-derived key lists are generated, not typed.
- **Type consistency**: `RiskKeys.isHighRisk(key, enValue)` / `listFor(dict, enDict)` used identically in Tasks 1, 4, 8; `I18n.enFor/provenance/isMachineLocale` defined in Task 2 and consumed in 3, 4, 5; `RiskText.render(doc, text, key)` defined in Task 3, consumed in Task 4; `rows[i][3]`/`titleKey` defined in Task 4 only; `_meta v2` field names (`version/provenance/coverage/verified/high_risk`) identical in Tasks 2, 7, 8, 9. No orphan references.
- **Ordering**: Task 1 and 2 are independent and both precede 3-5; 6-8 depend only on 1-2; 9 depends on all. No task references a name defined later.
