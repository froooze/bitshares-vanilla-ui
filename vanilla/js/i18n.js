/* I18n: locale string resolution (registry + t() + locale->en->key fallback +
 * %(name)s interpolation + Intl wrappers + dict cache + Store-envelope pref).
 * Owns: locale registry (code -> nested dict), current-locale tag, dict
 *   fetch/cache/pref helpers, t()/setLocale()/loadCached() entry points, and
 *   the read-only honesty accessors the surfaces read (enFor /
 *   provenance / isMachineLocale).
 * Consumes locales/*.json + localStorage. Side effects: in-memory registry +
 *   localStorage pref/cache writes only; no view DOM (callers toast on
 * {ok:false}). Created by: building-vanilla-slices skill, slice-17-i18n plan.
 * Slice-17. Plurals deferred (batch-1 needs none). Failures are
 * {ok:false} ('bad-locale' | 'fetch-failed'), never throws. */
var I18n = (function () {
  "use strict";

  var VERSION = 1;
  var PREF_KEY = "bts-vanilla-locale-v1";
  var CACHE_KEY = "bts-vanilla-i18n-v1";
  var DICT_PATH = "locales/";

  /* Shipped locale codes (bitshares-ui/app/assets/locales.js:1-3 = 9 + en, plus hi + pt). */
  var CODES = ["en", "de", "es", "fr", "it", "ja", "ko", "ru", "tr", "zh", "hi", "pt"];

  /* Switcher display names, Reference #7 verbatim (identifiers, untranslated). */
  var NAMES = { de: "Deutsch", en: "English", es: "Español", fr: "Français", it: "Italiano",
    ja: "日本語", ko: "한국어", ru: "Русский", tr: "Türkçe", zh: "简体中文",
    hi: "हिन्दी", pt: "Português" };

  var registry = {}; /* code -> nested dict (sections); en loaded at boot by loadCached */
  var current = "en";

  /* English defaults handed to t(), keyed by locale key — the second,
   * always-present English source. loadCached() swallows a failed en
   * fetch and still resolves {ok:true}, and app.js boots on either
   * resolution, so registry.en can be empty while the active locale
   * renders fine: t() then answers from these defaults. Without them
   * the honesty surfaces lose their English reference exactly when the
   * en master failed to load. Bounded by the key space (one entry per
   * key, last write wins), never by call volume. */
  var enDefaults = {};

  /* Strict dotted-key lookup (=== per segment, never prefix/truthy). */
  function lookup(dict, key) {
    if (!dict || typeof key !== "string") return undefined;
    var node = dict;
    var parts = key.split(".");
    for (var i = 0; i < parts.length; i++) {
      if (node === null || typeof node !== "object") return undefined;
      if (!Object.prototype.hasOwnProperty.call(node, parts[i])) return undefined;
      node = node[parts[i]];
    }
    return (typeof node === "string") ? node : undefined;
  }

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

  /* %(name)s interpolation (ported verbatim from #1's counterpart syntax so
   * #1 strings stay reusable). Missing var: placeholder stays + warn, no throw. */
  function interpolate(s, vars) {
    if (!vars || typeof vars !== "object") return s;
    return String(s).replace(/%\(([^)]+)\)s/g, function (m, name) {
      if (Object.prototype.hasOwnProperty.call(vars, name)) return String(vars[name]);
      if (typeof console !== "undefined" && console.warn) console.warn("i18n: missing var " + name);
      return m;
    });
  }

  /* t(key, enDefault, vars?) -> string. Chain: current locale (allowlisted)
   * -> en registry -> enDefault (call-site copy, the file:// guarantee) ->
   * key id itself. Last resort is NEVER blank and NEVER throws.
   * Every non-empty enDefault is recorded for enFor() (see enDefaults), so
   * the English this call falls back to can still be shown as the
   * reference line when the en master never loaded. */
  function t(key, enDefault, vars) {
    if (typeof key !== "string" || !key) return "";
    /* Record only a real string: a missing or empty default must leave
     * enFor undefined rather than hand the honesty surfaces a blank
     * English line. The write is a plain data property on a private
     * object, and reads go through hasOwnProperty, so neither an
     * inherited member nor a "__proto__" key can pose as an entry. */
    if (typeof enDefault === "string" && enDefault) enDefaults[key] = enDefault;
    var hit;
    if (current !== "en" && allowlisted(current, key)) {
      hit = lookup(registry[current], key);
      if (hit !== undefined) return interpolate(hit, vars);
    }
    hit = lookup(registry.en, key);
    if (hit !== undefined) return interpolate(hit, vars);
    if (typeof enDefault === "string") return interpolate(enDefault, vars);
    return key;
  }

  /* Locale pref: an explicitly-stored envelope value wins (slice-17
   * architecture); else the standalone PREF_KEY (pre-migration users +
   * boot-order fallback — i18n.js loads before store.js); else "en".
   * Store access is lazy + guarded. */
  function readPref() {
    try {
      if (typeof Store !== "undefined" && Store && typeof Store.storedLocale === "function") {
        var env = Store.storedLocale();
        if (env && CODES.indexOf(env) !== -1) return env;
      }
    } catch (e) { /* fall through to standalone key */ }
    try {
      if (typeof localStorage === "undefined") return "en";
      var v = localStorage.getItem(PREF_KEY);
      return (CODES.indexOf(v) !== -1) ? v : "en";
    } catch (e) { return "en"; }
  }

  /* writePref: persist the locale choice (Store envelope + standalone key).
   * Params: code (shipped locale code string). Returns nothing. Fails: never
   * throws — blocked storage still leaves the in-memory locale applied. */
  function writePref(code) {
    try {
      if (typeof Store !== "undefined" && Store && typeof Store.saveSettings === "function") {
        Store.saveSettings({ locale: code });
      }
    } catch (e) { /* envelope unavailable: standalone key still applies */ }
    try {
      if (typeof localStorage !== "undefined") localStorage.setItem(PREF_KEY, code);
    } catch (e) { /* storage blocked: memory locale still applies */ }
  }

  /* readCache: validated cached dict for a locale (version + locale tag must
   * match). Params: code string. Returns the dict object or null on miss /
   * mismatch / bad JSON. Fails: never throws. */
  function readCache(code) {
    try {
      if (typeof localStorage === "undefined") return null;
      var raw = localStorage.getItem(CACHE_KEY + ":" + code);
      if (!raw) return null;
      var env = JSON.parse(raw);
      if (!env || env.v !== VERSION || env.locale !== code || !env.dict) return null;
      return env.dict; /* envelope mismatch -> drop, caller refetches */
    } catch (e) { return null; }
  }

  /* writeCache: store a fetched dict under the versioned cache key.
   * Params: code string, dict object. Returns nothing. Fails: never throws —
   * cache is optional (the memory registry still applies). */
  function writeCache(code, dict) {
    try {
      if (typeof localStorage !== "undefined") localStorage.setItem(CACHE_KEY + ":" + code, JSON.stringify({ v: VERSION, at: Date.now(), locale: code, dict: dict }));
    } catch (e) { /* cache optional: memory registry still applies */ }
  }

  /* THE single fetch call site in this file (grep-provable): dict loader.
   * no-store (not a ?v= token): dictionaries must never serve stale —
   * a cached dict shows yesterday's words with today's code (the stale
   * "Explore" incident). Same precedent as the version.json fetch in
   * app.js. Injected stub fetchers ignore the extra options arg. */
  function fetchDict(code, fetcher) {
    var f = fetcher || ((typeof fetch !== "undefined") ? fetch : null);
    if (!f) return Promise.resolve({ ok: false, reason: "fetch-failed" });
    var url = DICT_PATH + code + ".json";
    return f(url, { cache: "no-store" }).then(function (r) {
      if (!r || (typeof r.ok === "boolean" && !r.ok)) return { ok: false, reason: "fetch-failed" };
      return r.json().then(function (d) { return { ok: true, dict: d }; },
        function () { return { ok: false, reason: "fetch-failed" }; });
    }, function () { return { ok: false, reason: "fetch-failed" }; });
  }

  /* applyLang: mirror the active locale tag onto <html lang> (R-A-W6 html
   * lang: a11y/SEO hint for screen readers + search. Guarded try/catch —
   * never throws, even headless (no document) or on exotic DOMs. */
  function applyLang(code) {
    try {
      if (typeof document !== "undefined" && document && document.documentElement &&
          typeof document.documentElement.setAttribute === "function") {
        document.documentElement.setAttribute("lang", code);
      }
    } catch (e) { /* hint only: locale still applies in memory */ }
  }

  /* setLocale(code) -> Promise. 'bad-locale' unless shipped; memory+cache
   * first, fetch on miss (file://+uncached -> {ok:false}, caller toasts). */
  function setLocale(code, fetcher) {
    if (CODES.indexOf(code) === -1) return Promise.resolve({ ok: false, reason: "bad-locale" });
    var hit = (code === "en") ? registry.en : (code === current ? registry[code] : null);
    if (hit) { current = code; writePref(code); applyLang(code); return Promise.resolve({ ok: true, code: code }); }
    var cached = readCache(code);
    if (cached) {
      registry[code] = cached; current = code; writePref(code); applyLang(code);
      return Promise.resolve({ ok: true, code: code });
    }
    return fetchDict(code, fetcher).then(function (r) {
      if (!r.ok) return r;
      registry[code] = r.dict; writeCache(code, r.dict);
      current = code; writePref(code); applyLang(code);
      return { ok: true, code: code };
    });
  }

  function locale() { return current; }
  function names() {
    var out = {}, i;
    for (i = 0; i < CODES.length; i++) out[CODES[i]] = NAMES[CODES[i]];
    return out;
  }

  /* Intl wrappers, DISPLAY only. Prefs-locale tag; no Intl -> String(value). */
  function date(isoString) {
    var d = new Date(isoString);
    if (typeof Intl === "undefined" || typeof Intl.DateTimeFormat === "undefined") return String(isoString);
    return new Intl.DateTimeFormat(current, { dateStyle: "medium", timeStyle: "medium" }).format(d);
  }

  function num(n, opts) {
    if (typeof Intl === "undefined" || typeof Intl.NumberFormat === "undefined") return String(n);
    return new Intl.NumberFormat(current, opts).format(n);
  }

  /* Boot: pref + cache validate (mismatch drops, lazy refetch, never throw).
   * Write-back keeps the envelope reflecting the resolved choice. */
  function loadCached(fetcher) {
    current = readPref();
    writePref(current);
    applyLang(current); /* boot hint: <html lang> matches the pref immediately */
    var codes = (current === "en") ? ["en"] : ["en", current];
    var chain = Promise.resolve();
    codes.forEach(function (code) {
      chain = chain.then(function () {
        if (registry[code]) return null;
        var cached = readCache(code);
        if (cached) { registry[code] = cached; return null; }
        return fetchDict(code, fetcher).then(function (r) {
          if (r.ok) { registry[code] = r.dict; writeCache(code, r.dict); }
          return null;
        });
      });
    });
    return chain.then(function () { return { ok: true, code: current }; });
  }

  /* Test seam (headless vectors): seed registry without transport. */
  function _seed(code, dict) { registry[code] = dict; }
  function _setCurrent(code) { current = code; }

  return { t: t, setLocale: setLocale, locale: locale, names: names,
    date: date, num: num, loadCached: loadCached, CODES: CODES.slice(),
    enFor: enFor, provenance: provenance, isMachineLocale: isMachineLocale,
    _seed: _seed, _setCurrent: _setCurrent };
})();

if (typeof module !== "undefined") { module.exports = I18n; }
