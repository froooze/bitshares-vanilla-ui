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
