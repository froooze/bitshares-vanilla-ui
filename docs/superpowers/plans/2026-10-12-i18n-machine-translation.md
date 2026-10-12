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
  - `I18n.enFor(key)` → `string | undefined` (English source for `key`: the en master when loaded, otherwise the English default `t()` was handed for that key — `loadCached()` resolves `{ok:true}` even when the en fetch fails, so the master can be absent on a running app)
  - `I18n.provenance(code)` → `"machine" | "human" | "none"` (`"none"` = not loaded, or `en`)
  - `I18n.isMachineLocale(code)` → `boolean` (true only when `provenance === "machine"`)

`allowlisted` becomes version-aware: v2 dicts are read from `_meta.coverage`, v1 from `_meta.translated`. A v2 dict whose `coverage` is missing or is not an array claims nothing, so every key falls back to English.

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

  /* enFor: the English source text for a key. Two sources, in order:
   * the en master that loadCached() loads at boot, then the English
   * default t() was handed for that key. The fallback exists because
   * loadCached() resolves {ok:true} even when the en fetch FAILS — it
   * swallows the error and app.js boots on either resolution — so the
   * whole active locale can render with registry.en empty. t() answers
   * in that boot from the call-site default, and the honesty surfaces
   * need the same string: a machine-labelled locale whose lines have no
   * English reference is the exact dishonesty this exists to prevent.
   * The master always wins, so a stale recorded default can never
   * displace the dict every other surface reads.
   * @param {string} key dotted locale key
   * @returns {string|undefined} undefined when neither source knows the
   *   key — callers render plain text rather than an empty English line.
   *   The raw template, `%(name)s` intact, exactly as the master stores
   *   it. Never throws. */
  function enFor(key) {
    var hit = lookup(registry.en, key);
    if (hit !== undefined) return hit;
    if (typeof key !== "string" || !key) return undefined;
    if (Object.prototype.hasOwnProperty.call(enDefaults, key)) return enDefaults[key];
    return undefined;
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
   * unverified — the single condition the badge and dual-line check.
   * @param {string} code locale code
   * @returns {boolean} false for en, unloaded, unknown and v1 locales;
   *   never throws. */
  function isMachineLocale(code) {
    return provenance(code) === "machine";
  }
```

`t()` gains one line (no signature change, no return change): every non-empty
`enDefault` is recorded in a private `enDefaults` map for `enFor()` to fall
back on.

```js
  var enDefaults = {}; /* English defaults handed to t(), keyed by locale key */
```

```js
  function t(key, enDefault, vars) {
    if (typeof key !== "string" || !key) return "";
    if (typeof enDefault === "string" && enDefault) enDefaults[key] = enDefault;
    var hit;
    /* …unchanged chain below… */
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
- Consumes: `I18n.locale`, `I18n.isMachineLocale(code)`, `I18n.enFor`, `DOM.el` (element creation), the global `touchable()` (44px floor), `EventDelegate.delegate` (one delegated listener).
- Produces: `RiskText.render(doc, text, key)` → `Element` and `RiskText.wrap(doc, text, key)` → `Element` (alias for row use), plus `RiskText.isActive()` → `boolean`.

Behaviour contract: when the active locale (from `I18n.locale()`) is machine-filled, `key` is non-empty, and `I18n.enFor(key)` is a non-empty string **different** from `text`, return a `div.i18n-risk` containing the native `span`, a `button.i18n-risk-star` (`aria-expanded="false"`, `type="button"`), a hidden `div.i18n-risk-en` holding the English, and an `a.i18n-risk-more` link to the limitations article. Otherwise return a plain text wrapper (`span.i18n-risk-plain`) so callers never branch. `render` never returns null and never throws — callers append the result unconditionally. Each tap flips `is-open` on the wrapper, the class `.i18n-risk.is-open .i18n-risk-more` needs to reveal the article link.

- [ ] **Step 1: Write the failing test**

`tooling/risk-text-test.js`:

```js
/* risk-text-test: the dual-line honesty surface on the signing path, so its
 * three modes are pinned — dual-line when machine + key + a differing English
 * source, plain when there is no English reference or none that differs, and
 * plain when the locale is verified/human. The asterisk must be a real button
 * with a 44px touch floor and aria-expanded/aria-controls (no hover-only
 * affordance, AGENTS.md §3.6), and the disclosure must actually toggle.
 *
 * Two notes on the harness, both loadings rather than fakes:
 *   1. utils/dom.js, utils/touchable.js and utils/event.js are the SHIPPED
 *      modules, loaded as-is. The brief's draft stubbed DOM.el/touchable and
 *      a global `Event`; the real globals are `touchable` and `EventDelegate`
 *      (Event is reserved for the DOM constructor), and the delegated handler
 *      receives the matched element as its SECOND argument. Stubbing them
 *      would have hidden exactly the wiring Task 4 depends on.
 *   2. The fake document supplies only createElement + addEventListener, and
 *      reflects `type`/`hidden` to attributes the way real elements do, so
 *      `[hidden]` CSS and getAttribute assertions see the same truth.
 *   3. Sections 8-9 stand up two more sandboxes with parts of that harness
 *      MISSING on purpose (no DOM global; no document at all) — the module
 *      claims it never throws and never answers null, and that claim is only
 *      testable away from the fully-loaded sandbox.
 * Anything richer than this is the browser probe's job (tooling/visual/). */
"use strict";
var assert = require("assert");
var fs = require("fs");
var path = require("path");
var vm = require("vm");

var ROOT = path.join(__dirname, "..");
function load(rel) { return fs.readFileSync(path.join(ROOT, rel), "utf8"); }

var clickListeners = [];
function el(tag) {
  var node = {
    tagName: String(tag).toUpperCase(),
    children: [], attrs: {}, style: {},
    className: "", textContent: "", parentNode: null,
    setAttribute: function (k, v) { this.attrs[k] = String(v); },
    getAttribute: function (k) {
      return Object.prototype.hasOwnProperty.call(this.attrs, k) ? this.attrs[k] : null;
    },
    hasAttribute: function (k) { return Object.prototype.hasOwnProperty.call(this.attrs, k); },
    removeAttribute: function (k) { delete this.attrs[k]; },
    appendChild: function (c) { if (c) c.parentNode = this; this.children.push(c); return c; },
    addEventListener: function () {}
  };
  var hiddenFlag = false;
  Object.defineProperty(node, "type", {
    get: function () { return this.attrs.type === undefined ? "" : this.attrs.type; },
    set: function (v) { this.attrs.type = String(v); }
  });
  Object.defineProperty(node, "hidden", {
    get: function () { return hiddenFlag; },
    set: function (v) { hiddenFlag = !!v; if (v) { this.attrs.hidden = ""; } else { delete this.attrs.hidden; } }
  });
  return node;
}

var document = {
  createElement: el,
  addEventListener: function (type, fn) { if (type === "click") clickListeners.push(fn); },
  removeEventListener: function (type, fn) {
    if (type !== "click") return;
    var i = clickListeners.indexOf(fn);
    if (i !== -1) clickListeners.splice(i, 1);
  }
};
function click(node) {
  clickListeners.forEach(function (fn) { fn({ target: node, currentTarget: document }); });
}

var sandbox = { document: document };
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(load("vanilla/js/utils/touchable.js"), sandbox);
vm.runInContext(load("vanilla/js/utils/dom.js"), sandbox);
vm.runInContext(load("vanilla/js/utils/event.js"), sandbox);

/* Fake I18n mirroring the shipped Task 2 contract (i18n.js:95-109) EXACTLY:
 * locale() names the active code, isMachineLocale(code) takes that code, and
 * enFor(key) may be undefined when neither the en master nor a recorded t()
 * default knows the key.
 *
 * The isMachineLocale fake is deliberately STRICT, because a permissive one
 * hides the bug this widget exists to be careful about: the real function is
 * provenance(code) === "machine", and provenance answers "none" for anything
 * that is not a loaded non-en locale — a non-string code included. A fake
 * written as `machine && code !== "en"` says true for undefined, so calling
 * isMachineLocale() with no argument (the mistake this module must not make)
 * still renders dual-line and the suite stays GREEN over the real defect.
 * Faithful terms, therefore: a non-empty string code that is not "en". */
var localeCode = "es";
var machine = true;
var enForCalls = 0;
/* One factory, so the degraded sandboxes below get the SAME contract instead
 * of a second, laxer copy. */
function fakeI18n() {
  return {
    locale: function () { return localeCode; },
    isMachineLocale: function (code) {
      return machine && typeof code === "string" && !!code && code !== "en";
    },
    enFor: function (k) {
      enForCalls += 1;
      if (k === "unlockconfirm.confirm") return "Unlock to sign";
      if (k === "menu.dashboard") return "Dashboard";
      return undefined;
    }
  };
}
sandbox.I18n = fakeI18n();

vm.runInContext(load("vanilla/js/ui/risk-text.js"), sandbox);
var RiskText = sandbox.RiskText;

function find(node, cls) {
  if (!node) return null;
  if (node.className === cls) return node;
  var kids = node.children || [];
  for (var i = 0; i < kids.length; i++) {
    var hit = find(kids[i], cls);
    if (hit) return hit;
  }
  return null;
}

/* 1. machine locale + high-risk key -> dual-line with asterisk. */
var node = RiskText.render(document, "Desbloquear para firmar", "unlockconfirm.confirm");
assert.strictEqual(node.className, "i18n-risk", "dual-line wrapper");
var native = find(node, "i18n-risk-native");
assert.ok(native, "native line exists");
assert.strictEqual(native.textContent, "Desbloquear para firmar", "native text is what was passed");
var star = find(node, "i18n-risk-star");
assert.ok(star, "asterisk exists");
assert.strictEqual(star.tagName, "BUTTON", "asterisk is a real button");
assert.strictEqual(star.attrs["aria-expanded"], "false", "starts collapsed");
assert.strictEqual(star.attrs.type, "button", "never submits a form");
assert.ok(star.getAttribute("aria-controls"), "aria-controls names the panel");
assert.ok(star.style.minHeight === "44px" && star.style.minWidth === "44px",
  "touch floor applied by the shared touchable()");
var en = find(node, "i18n-risk-en");
assert.ok(en, "english line exists");
assert.strictEqual(en.hidden, true, "english starts hidden");
assert.strictEqual(en.id, star.getAttribute("aria-controls"), "aria-controls points at the english line");
/* The en reference is byte-exact, not "contains the words": the panel shows
 * the en master string and nothing else (the limitations link is a SIBLING of
 * the panel, asserted below). */
assert.strictEqual(en.textContent, "Unlock to sign", "english text is the reference, byte-exact");
var more = find(node, "i18n-risk-more");
assert.ok(more, "the limitations link is reachable from the line itself");
assert.strictEqual(more.tagName, "A", "limitations link is an anchor");
assert.ok(String(more.href).indexOf("#/help/translation-limitations") !== -1,
  "limitations link points at the article");
assert.strictEqual(more.parentNode, node, "link lives on the wrapper, not inside the english text");

/* 2. no key -> plain (dynamic values: amounts, ids, symbols). */
var plain = RiskText.render(document, "1.234,56 BTS", null);
assert.strictEqual(plain.className, "i18n-risk-plain", "dynamic values stay plain");
assert.strictEqual(plain.textContent, "1.234,56 BTS", "plain keeps the text");

/* 3. the displayed text IS the english -> plain (nothing to disclose). */
var same = RiskText.render(document, "Unlock to sign", "unlockconfirm.confirm");
assert.strictEqual(same.className, "i18n-risk-plain", "no dual-line when text already is the english");

/* 4. human/verified locale -> plain even for a high-risk key. */
machine = false;
var human = RiskText.render(document, "Desbloquear para firmar", "unlockconfirm.confirm");
assert.strictEqual(human.className, "i18n-risk-plain", "verified locales lose the asterisk");
assert.strictEqual(RiskText.isActive(), false, "isActive is false off a machine locale");

/* en is never machine-filled: an active en locale must never double up. */
machine = true;
localeCode = "en";
var enLocale = RiskText.render(document, "Unlock to sign", "unlockconfirm.confirm");
assert.strictEqual(enLocale.className, "i18n-risk-plain", "the english locale needs no reference line");
/* The ACTIVE LOCALE has to be what decides, so prove it with a pair where the
 * text is NOT the english source. The assertion above passes on the "text
 * already is the english" short-circuit, which holds whatever locale the
 * module reads; this one cannot. Same key, same differing text, plain here
 * and dual-line one step below — the locale is the only variable, so a module
 * that hardcoded a code (or ignored I18n.locale() entirely) fails both. */
var enSamePair = RiskText.render(document, "Desbloquear para firmar", "unlockconfirm.confirm");
assert.strictEqual(enSamePair.className, "i18n-risk-plain",
  "under en, a high-risk key whose text differs from the en master stays plain");
assert.strictEqual(RiskText.isActive(), false, "isActive is false when the active locale is en");
localeCode = "es";
var esSamePair = RiskText.render(document, "Desbloquear para firmar", "unlockconfirm.confirm");
assert.strictEqual(esSamePair.className, "i18n-risk",
  "the identical pair dual-lines once the active locale is machine-filled");
assert.strictEqual(RiskText.isActive(), true, "isActive is true on a machine locale");

/* 5. unknown english source -> plain, never an empty english line
 *    (I18n.enFor returns undefined when the master and the recorded t()
 *    default both miss — a missing reference beats a wrong one). */
var unknown = RiskText.render(document, "Texte dynamique", "some.key.nobody.knows");
assert.strictEqual(unknown.className, "i18n-risk-plain", "no english source degrades to plain");
assert.strictEqual(unknown.textContent, "Texte dynamique", "the degraded text is untouched");

/* 6. the disclosure toggles through the shared delegated listener. */
var t1 = RiskText.render(document, "Desbloquear para firma", "unlockconfirm.confirm");
var s1 = find(t1, "i18n-risk-star");
var e1 = find(t1, "i18n-risk-en");
var id1 = e1.id;
/* The class IS the CSS: `.i18n-risk.is-open .i18n-risk-more { display:inline }`
 * in app.css is the only thing that reveals the "About these translations"
 * link, so a module that stopped toggling it would leave that link as
 * permanently invisible markup while aria/hidden assertions still passed. */
assert.ok(String(t1.className).indexOf("is-open") === -1, "wrapper starts without the open class");
click(s1);
assert.strictEqual(s1.getAttribute("aria-expanded"), "true", "first tap expands");
assert.strictEqual(e1.hidden, false, "first tap reveals the english");
assert.ok(String(t1.className).split(/\s+/).indexOf("is-open") !== -1,
  "first tap puts is-open on the wrapper — the class app.css needs for .i18n-risk-more");
click(s1);
assert.strictEqual(s1.getAttribute("aria-expanded"), "false", "second tap collapses");
assert.strictEqual(e1.hidden, true, "second tap hides it again");
assert.ok(String(t1.className).split(/\s+/).indexOf("is-open") === -1,
  "second tap removes is-open, and never leaves the class behind twice");

/* ids are unique, so one disclosure never drives another's panel. */
var t2 = RiskText.render(document, "Desbloquear para firmar", "unlockconfirm.confirm");
var e2 = find(t2, "i18n-risk-en");
assert.notStrictEqual(e2.id, id1, "each dual-line gets its own panel id");
click(find(t2, "i18n-risk-star"));
assert.strictEqual(e1.hidden, true, "opening the second panel leaves the first closed");

/* exactly one delegated listener for the whole app, however many renders. */
assert.strictEqual(clickListeners.length, 1, "the disclosure binds one delegated click listener");

/* 7. wrap is the render alias for row/cell use, and odd input never throws. */
assert.strictEqual(RiskText.wrap, RiskText.render, "wrap is the render alias");
assert.strictEqual(typeof RiskText.isActive, "function", "isActive exists");
assert.strictEqual(RiskText.render(document, "", "unlockconfirm.confirm").className,
  "i18n-risk-plain", "empty text degrades to plain");
assert.strictEqual(RiskText.render(document, null, null).textContent, "", "null text renders empty");
assert.strictEqual(RiskText.render(document, 42, null).textContent, "42", "non-string text is stringified");
assert.strictEqual(RiskText.render(document, "x", 42).className, "i18n-risk-plain",
  "a non-string key is not a key");

/* 8. ONE English lookup per dual-line line. The decision compares the en
 *    source against the text, and the panel then renders that same source; two
 *    lookups can disagree (the master could be re-read between them), which
 *    would put a line's panel out of sync with the reason it was rendered. */
enForCalls = 0;
var once = RiskText.render(document, "Desbloquear para firmar", "unlockconfirm.confirm");
assert.strictEqual(once.className, "i18n-risk", "the counted render dual-lined");
assert.strictEqual(enForCalls, 1, "the English source is resolved once and reused for the panel");
assert.strictEqual(find(once, "i18n-risk-en").textContent, "Unlock to sign",
  "the panel shows the source the decision compared against");

/* 9. a missing helper degrades instead of throwing. Two harnesses, neither of
 *    which any real page can be: (a) no DOM global (utils/dom.js not loaded)
 *    with a document present, and (b) no document at all. The module header
 *    claims "never throws", so both must answer a node. */

/* (a) document present, DOM absent. */
var bareDoc = { createElement: el, addEventListener: function () {} };
var bare = { document: bareDoc, I18n: fakeI18n() };
bare.window = bare;
vm.createContext(bare);
vm.runInContext(load("vanilla/js/ui/risk-text.js"), bare);
var bareOut = bare.RiskText.render(bareDoc, "Desbloquear para firma", "unlockconfirm.confirm");
assert.ok(bareOut, "no DOM global must not throw and must still answer a node");
assert.strictEqual(bareOut.className, "i18n-risk",
  "without the DOM helper the dual-line line still renders (raw createElement)");
assert.ok(find(bareOut, "i18n-risk-star"), "the asterisk survives a missing DOM helper");
assert.ok(find(bareOut, "i18n-risk-en"), "the english panel survives a missing DOM helper");
assert.strictEqual(bare.RiskText.render(bareDoc, "Unlock to sign", "unlockconfirm.confirm").className,
  "i18n-risk-plain", "and the plain path survives a missing DOM helper too");

/* (b) no document at all. Task 4 mounts this straight into ConfirmDialog with
 *     appendChild, which stringifies a null return into the dialog as the
 *     visible text "null" — so the degraded answer is an EMPTY plain wrapper,
 *     never null. */
var headless = {};
headless.window = headless;
vm.createContext(headless);
vm.runInContext(load("vanilla/js/ui/risk-text.js"), headless);
var noDoc = headless.RiskText.render(undefined, "Desbloquear para firmar", "unlockconfirm.confirm");
assert.ok(noDoc, "no document must not throw and must not answer null");
assert.strictEqual(noDoc.className, "i18n-risk-plain", "the no-document floor is a plain wrapper");
assert.strictEqual(noDoc.textContent, "", "and it is empty — nothing is rendered, rather than \"null\"");
assert.ok(headless.RiskText.isActive() === false, "isActive is false without I18n");

console.log("OK: risk-text");
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `node tooling/risk-text-test.js`
Expected: FAIL — ENOENT on `vanilla/js/ui/risk-text.js`.

- [ ] **Step 3: Implement**

`vanilla/js/ui/risk-text.js`:

```js
/* ui/risk-text.js — the dual-line honesty surface for high-risk locale strings.
 * Owns: the one decision (dual-line vs plain, see dualEnglish), the asterisk
 *   disclosure button (real <button type="button">, aria-expanded +
 *   aria-controls, 44px touch floor — never a hover-only affordance, AGENTS.md
 *   §3.6), the English reference panel it toggles, and the link to the
 *   translation-limitations article from the exact line the user doubted.
 * Consumes: I18n.locale/isMachineLocale/enFor, DOM.el (element creation — never
 *   reimplemented here), the global touchable() (44px floor, same guard shape
 *   as ui/confirm.js so Node harnesses without it still render), EventDelegate
 *   (ONE delegated click listener, the shared helper — not a private one).
 * Side effects: creates detached elements; adds at most one delegated
 *   document-level "click" listener, on the first dual-line render only.
 *   No storage, no network, no signing.
 * Created by: building-vanilla-slices skill,
 *   docs/superpowers/plans/2026-10-12-i18n-machine-translation.md Task 3.
 * Failures: never throws. An unknown key, a missing English source (I18n.enFor
 *   returns undefined when the en master never loaded and no t() default was
 *   recorded), a non-machine locale, a verified locale, or a missing doc all
 *   degrade to the plain text wrapper — a missing reference beats a wrong one.
 *
 * Two UI strings below are still English literals (the asterisk's accessible
 * name and the article link's label). They cannot be keyed in this task: the
 * locale dictionaries and their _meta allowlists are not in this task's write
 * set, and an unkeyed t() call site fails the drift gate
 * (tooling/check_i18n.py). Task 6 adds the `i18n.risk_*` keys to all 12
 * dicts; these two literals are the exact strings reserved for them. */
var RiskText = (function () {
  "use strict";

  var ARTICLE = "#/help/translation-limitations";
  var EN_CLASS = "i18n-risk-en";
  var STAR_CLASS = "i18n-risk-star";
  var WRAP_CLASS = "i18n-risk";
  var OPEN_CLASS = "is-open";
  /* Reserved keys for the two literals above (Task 6 owns the dictionaries). */
  var SHOW_EN_LABEL = "Show the English reference for this line";
  var ABOUT_LABEL = "About these translations";

  var bound = false;
  var uid = 0;

  /* activeMachine: is the ACTIVE locale machine-filled and unverified?
   * I18n.isMachineLocale(code) takes the code (calling it bare answers
   * "not machine" for every locale — see i18n.js:107), so the code comes from
   * I18n.locale(). Failures: false when I18n is absent, incomplete, or
   * throws — a surface that cannot prove machine provenance must stay silent. */
  function activeMachine() {
    try {
      if (typeof I18n === "undefined" || !I18n || typeof I18n.isMachineLocale !== "function") return false;
      if (typeof I18n.locale !== "function") return false;
      var code = I18n.locale();
      if (typeof code !== "string" || !code) return false;
      return I18n.isMachineLocale(code) === true;
    } catch (e) {
      return false;
    }
  }

  /* englishSource: the English master text for a key, or null.
   * @param {string} key dotted locale key.
   * @returns {string|null} null when neither source knows the key.
   * Failure: never throws — a throwing enFor degrades to no reference. */
  function englishSource(key) {
    try {
      if (typeof I18n === "undefined" || !I18n || typeof I18n.enFor !== "function") return null;
      var src = I18n.enFor(key);
      return (typeof src === "string" && src) ? src : null;
    } catch (e) {
      return null;
    }
  }

  /* isVerified: has a human reviewed THIS key in the active locale?
   * SEAM — deliberately always false in this task. Task 5 reads the locale's
   * _meta.verified list (per-key human review) and answers true there, which
   * drops the asterisk from that line while leaving every unverified key of
   * the same machine-filled locale labelled. Kept as its own function so that
   * addition is one return statement, not a rewrite of dualEnglish.
   * @param {string} key dotted locale key (unused until Task 5 wires it).
   * @returns {boolean} always false today. */
  function isVerified(key) {
    return false;
  }

  /* mk: ONE element through the SHARED DOM helper — never reimplemented here.
   * Falls back to the raw owner.createElement only when the DOM global is
   * absent (a harness that did not load utils/dom.js), the same guard shape
   * ui/confirm.js uses, so a missing helper degrades the widget instead of
   * throwing a ReferenceError out of a signing dialog.
   * @param {Document} owner owner document (createElement known good — render
   *   resolves it before calling).
   * @param {string} tag tag name.
   * @param {string|null} text textContent; null leaves the element empty.
   * @param {string} [cls] optional className.
   * @returns {HTMLElement} new detached element. */
  function mk(owner, tag, text, cls) {
    if (typeof DOM !== "undefined" && DOM && typeof DOM.el === "function") {
      return DOM.el(owner, tag, text, cls);
    }
    var n = owner.createElement(tag);
    if (text !== undefined && text !== null) n.textContent = text;
    if (cls) n.className = cls;
    return n;
  }

  /* degraded: the no-document floor for render(). With no document there is
   * no element to build, but the answer must still NOT be null: Task 4 mounts
   * this straight into ConfirmDialog with appendChild, and appendChild(null)
   * inserts the visible text "null" into the dialog. An empty plain wrapper is
   * the honest floor — nothing is rendered rather than something wrong.
   * Unreachable in a page: every caller resolves a document first (and
   * ConfirmDialog.show throws "confirm: no document" without one). */
  function degraded() {
    return { className: "i18n-risk-plain", textContent: "", children: [] };
  }

  /* dualEnglish: the ONE decision about dual-line rendering, in one place so
   * views (Task 4 mounts every signing row through this) and this test agree.
   * Returns the English source to DISCLOSE, not a boolean, so the decision
   * and the panel share one lookup: a second I18n.enFor call could read a
   * different value and leave a line's panel disagreeing with the reason the
   * line was rendered dual-line.
   * @param {string} [key] dotted locale key; falsy for dynamic values
   *   (amounts, ids, symbols) which have no English source by construction.
   * @param {string} text the already-translated text about to be displayed.
   * @returns {string|null} the English reference to show, or null for the
   *   plain path — returned only when: the value is a real string, the key
   *   is a non-empty string, the key is not verified, the active locale is
   *   machine-filled, an English source exists, and that source differs from
   *   the text on screen. Never throws. */
  function dualEnglish(key, text) {
    if (typeof key !== "string" || !key) return null;
    if (typeof text !== "string" || !text) return null;
    if (isVerified(key)) return null;
    if (!activeMachine()) return null;
    var src = englishSource(key);
    return (src && src !== text) ? src : null;
  }

  /* setOpen: add/remove the open-state class on the wrapper.
   * @param {Element} host the div.i18n-risk wrapper.
   * @param {boolean} on desired state.
   * @returns {Element} host, mutated. Failure: no-op on a missing host. */
  function setOpen(host, on) {
    if (!host) return host;
    var names = String(host.className || "").split(/\s+/);
    var out = [], i;
    for (i = 0; i < names.length; i++) {
      if (names[i] && names[i] !== OPEN_CLASS) out.push(names[i]);
    }
    if (on) out.push(OPEN_CLASS);
    host.className = out.join(" ");
    return host;
  }

  /* panelIn: the English panel inside a dual-line wrapper. The wrapper's
   * children are flat and created here in a known order, so a direct-child
   * scan is exact and needs no selector engine; it also keeps the disclosure
   * working where querySelector is absent.
   * @param {any} host wrapper element (the button's parentNode).
   * @returns {any} the panel, or null when absent. Never throws. */
  function panelIn(host) {
    if (!host || !host.children) return null;
    var kids = host.children, i;
    for (i = 0; i < kids.length; i++) {
      if (kids[i] && kids[i].className === EN_CLASS) return kids[i];
    }
    return null;
  }

  /* toggle: flip one line's disclosure.
   * @param {any} btn the matched asterisk button (EventDelegate's second arg).
   * @returns {boolean} true when a panel was toggled. Failure: false (and no
   *   DOM change) when the button has no wrapper or the wrapper has no panel. */
  function toggle(btn) {
    if (!btn) return false;
    var host = btn.parentNode;
    var panel = panelIn(host);
    if (!panel) return false;
    var open = btn.getAttribute && btn.getAttribute("aria-expanded") === "true";
    if (btn.setAttribute) btn.setAttribute("aria-expanded", open ? "false" : "true");
    panel.hidden = open;
    setOpen(host, !open);
    return true;
  }

  /* bindDisclosure: attach the ONE delegated click listener for the app.
   * Delegation (not a listener per row) keeps the cost flat on a signing
   * dialog that renders dozens of lines, and re-renders after a locale switch
   * keep working because the listener lives on document. Failure: never
   * throws — a missing delegate helper or a missing document just leaves the
   * asterisk visible but inert rather than taking the confirm dialog down. */
  function bindDisclosure() {
    if (bound) return;
    if (typeof EventDelegate === "undefined" || !EventDelegate || typeof EventDelegate.delegate !== "function") return;
    if (typeof document === "undefined" || !document) return;
    try {
      EventDelegate.delegate(document, "." + STAR_CLASS, "click", function (evt, matched) {
        toggle(matched);
      });
      bound = true;
    } catch (e) {
      /* Disclosure stays inert; the line still renders plain text + asterisk. */
    }
  }

  /* render: the string, dual-line when warranted, plain otherwise. Callers
   * append the result unconditionally — the answer is always an element,
   * never a bare string and never null (Task 4 mounts this with appendChild,
   * and appendChild(null) would insert the text "null").
   * @param {Document} doc owner document (callers pass theirs).
   * @param {string|number|null|undefined} text the already-translated text to
   *   display; non-strings are stringified, null/undefined render empty.
   * @param {string} [key] dotted locale key enabling the English reference.
   * @returns {HTMLElement} span.i18n-risk-plain or div.i18n-risk — never a
   *   bare string, so callers can append unconditionally. Never throws. */
  function render(doc, text, key) {
    var str = (text === undefined || text === null) ? "" : String(text);
    var owner = (doc && typeof doc.createElement === "function") ? doc
      : ((typeof document !== "undefined" && document && typeof document.createElement === "function") ? document : null);
    if (!owner) return degraded();
    var enText = dualEnglish(key, str);
    if (enText === null) return mk(owner, "span", str, "i18n-risk-plain");

    uid += 1;
    var enId = "i18n-risk-en-" + uid;
    var wrap = mk(owner, "div", null, WRAP_CLASS);
    wrap.appendChild(mk(owner, "span", str, "i18n-risk-native"));

    var star = mk(owner, "button", "*", STAR_CLASS);
    star.type = "button";
    star.setAttribute("aria-expanded", "false");
    star.setAttribute("aria-controls", enId);
    star.setAttribute("aria-label", SHOW_EN_LABEL);
    if (typeof touchable === "function") touchable(star);
    wrap.appendChild(star);

    /* enText is the SAME string the decision compared against — one lookup. */
    var en = mk(owner, "div", enText, EN_CLASS);
    en.id = enId;
    en.hidden = true;
    wrap.appendChild(en);

    /* The link sits on the wrapper, not inside the panel, so the English
     * reference stays byte-for-byte the en master string with nothing appended
     * to it. CSS (.i18n-risk.is-open .i18n-risk-more) keeps it out of sight
     * until the line is open — which is why toggle() owns that class. */
    var more = mk(owner, "a", ABOUT_LABEL, "i18n-risk-more");
    more.href = ARTICLE;
    wrap.appendChild(more);

    bindDisclosure();
    return wrap;
  }

  /* isActive: is the honesty surface live at all? Views use it to decide
   * whether a legend or a page-level caveat is worth rendering at all.
   * @returns {boolean} true only on a machine-filled active locale. */
  function isActive() {
    return activeMachine();
  }

  return { render: render, wrap: render, isActive: isActive };
}());

if (typeof window !== "undefined") window.RiskText = RiskText;
```

Add to `vanilla/css/app.css` (theme-token based, no new raw HEX):

```css
/* i18n dual-line honesty surface (ui/risk-text.js): the machine-filled string
 * with its English reference one tap away, for lines where misreading costs
 * money. Tokens only, so all three themes get it free (principle #5) — no new
 * HEX. The 44px star box is declared here as well as applied by the shared
 * touchable() so the affordance survives a page that loads this stylesheet
 * without the helper. */
.i18n-risk { display: inline; }
.i18n-risk-star {
  background: none; border: 0; margin: 0; padding: 0 0.15em;
  min-width: 44px; min-height: 44px; vertical-align: middle;
  color: var(--accent); cursor: pointer; font-size: 0.9em; line-height: 1;
}
.i18n-risk-star:hover { color: var(--text); }
.i18n-risk-star:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }
.i18n-risk-en {
  display: block; margin: 0.15em 0 0.35em; padding-left: 0.55em;
  border-left: 3px solid var(--border); color: var(--muted); font-size: 0.92em;
}
/* Author display:block would otherwise beat the UA [hidden] rule. */
.i18n-risk-en[hidden] { display: none; }
.i18n-risk-more { display: none; margin-left: 0.35em; font-size: 0.92em; }
.i18n-risk.is-open .i18n-risk-more { display: inline; }
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

Run: `python3 tooling/check_i18n.py && python3 tooling/validate_translations.py es && bash tooling/check_types.sh && python3 tooling/check_rot.py && node tooling/risk-text-test.js && node tooling/i18n-risk-keys-test.js && node tooling/i18n-provenance-test.js && node tooling/i18n-badge-test.js && node tooling/confirm-risk-test.js && node tooling/i18n-v2-meta-test.js`
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
