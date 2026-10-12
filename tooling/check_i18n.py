#!/usr/bin/env python3
"""Drift check for slice-17 i18n (durable gate, runs in Task 2/3 + audits).

Verifies:
  1. All 10 vanilla/locales/*.json parse and carry _meta {version:1}.
  2. Key-completeness: every dict's flattened key set == en.json's set.
  3. Allowlist exactness: stubs (8) have untranslated=true + translated==[];
     es has untranslated=false + translated==32 batch-1 keys; en lists all.
  4. Stub honesty: every non-allowlisted value in a non-en dict EQUALS the
     en value (unverified strings never masquerade as translations).
  5. Translated es values differ from en (a "translation" identical to en
     is either an identifier -- allowlisted below -- or a mistake).
  6. Call-site drift: every t("key", "default") literal in vanilla/js/*.js
     and vanilla/index.html has default == en.json's value (ambiguity A).
     Zero call sites in Task 1 -> vacuously green; load-bearing in Task 2.

Usage: python3 tooling/check_i18n.py  (exit 0 green, 1 with problems)
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCALES = os.path.join(HERE, "..", "vanilla", "locales")
JS_DIRS = [os.path.join(HERE, "..", "vanilla", "js")]
INDEX_HTML = os.path.join(HERE, "..", "vanilla", "index.html")
STUB_CODES = ["de", "fr", "it", "ja", "ko", "ru", "tr", "zh", "hi", "pt"]

# Values identical in every language by design (proper nouns, URL schemes,
# symbols, theme/network ids). May appear in _meta.translated nowhere and
# must equal en everywhere.
IDENTIFIERS = {
    "settings.network_mainnet", "settings.network_testnet",
    "settings.custom_placeholder", "settings.pending", "settings.dash",
    "settings.theme_original_blue", "settings.theme_light",
    "settings.theme_dark", "shell.brand",
}

T_CALL_RE = re.compile(
    r"""\bt\(\s*"(?P<key>(?:\\.|[^"\\])*)"\s*,\s*"(?P<dflt>(?:\\.|[^"\\])*)"\s*(?:,\s*\{[^}]*\})?\s*\)"""
)


def js_unescape(s):
    """Decode a JS double-quoted literal to its runtime value (\\n, \\t,
    \\uXXXX, \\" — the old two-replace chain missed \\n, which hid the
    literal-\\n vs real-newline drift class, see misc.invoice_lines_placeholder).
    Falls back to the legacy replaces for JS-only escapes like \\'."""
    try:
        return json.loads('"' + s + '"')
    except ValueError:
        return s.replace('\\"', '"').replace("\\\\", "\\")


def flatten(d, prefix=""):
    out = {}
    for k, v in d.items():
        if k == "_meta":
            continue
        if isinstance(v, dict):
            out.update(flatten(v, prefix + k + "."))
        else:
            out[prefix + k] = v
    return out


def main():
    problems = []
    try:
        en = json.load(open(os.path.join(LOCALES, "en.json"), encoding="utf-8"))
    except (OSError, ValueError) as e:
        print("en.json unreadable: %s" % e)
        return 1
    en_flat = flatten(en)
    en_keys = set(en_flat)

    meta = en.get("_meta") or {}
    if meta.get("version") != 1 or meta.get("untranslated") is not False:
        problems.append("en.json _meta must be {version:1, untranslated:false}")
    if set(meta.get("translated") or []) != en_keys:
        problems.append("en.json _meta.translated must list all %d keys" % len(en_keys))

    for code in ["es"] + STUB_CODES:
        path = os.path.join(LOCALES, code + ".json")
        try:
            d = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError) as e:
            problems.append("%s unreadable: %s" % (code, e))
            continue
        flat = flatten(d)
        if set(flat) != en_keys:
            only = sorted(set(flat) - en_keys)
            miss = sorted(en_keys - set(flat))
            problems.append("%s key drift (extra=%s missing=%s)" % (code, only[:5], miss[:5]))
        m = d.get("_meta") or {}
        if m.get("version") != 1:
            problems.append("%s _meta.version != 1" % code)
        allow = m.get("translated") or []
        is_full = (set(allow) == en_keys)
        if not is_full and m.get("untranslated") is not True:
            # Partial translation in any language: honesty rules. Claimed
            # keys must differ from en (no false translation claims);
            # unclaimed non-identifier keys must equal en (honest stubs).
            # (Historically only es could be partial, so this branch was
            # es-gated; the rule itself is language-independent.)
            if m.get("untranslated") is not False:
                problems.append("%s _meta.untranslated must be false" % code)
            if set(allow) - en_keys:
                problems.append("%s allowlist has unknown keys: %s"
                                % (code, sorted(set(allow) - en_keys)))
            if set(allow) & IDENTIFIERS:
                problems.append("%s allowlist must not contain identifiers: %s"
                                % (code, sorted(set(allow) & IDENTIFIERS)))
            for k in sorted(en_keys - set(allow) - IDENTIFIERS):
                if flat.get(k) != en_flat[k]:
                    problems.append("%s: non-allowlisted %s != en value (dishonest stub)" % (code, k))
                    break
            for k in sorted(set(allow)):
                if flat.get(k) == en_flat.get(k):
                    problems.append("%s: translated %s identical to en (mistake or identifier?)" % (code, k))
                    break
        else:
            if m.get("untranslated") is True:
                if allow != []:
                    problems.append("%s stub _meta.translated must be []" % code)
                for k in sorted(en_keys):
                    if flat.get(k) != en_flat[k]:
                        problems.append("%s stub: %s != en value" % (code, k))
                        break
            else:
                # Fully translated dict (wave-1+): allowlist must cover every
                # key, identifiers included (validate_translations enforces
                # their byte-verbatim values pre-merge). The identical-value
                # check below also applies here (identifiers excepted, whose
                # values must equal en): a "full" dict with English strings
                # claimed as translated is the same lie as a partial one.
                # Quality (meaning, placeholders) is the auditors' job.
                if set(allow) != en_keys:
                    only = sorted(set(flat) - en_keys)
                    miss = sorted(en_keys - set(allow))
                    problems.append("%s allowlist drift (extra=%s missing=%s)"
                                    % (code, only[:5], miss[:5]))
                for k in sorted(en_keys - IDENTIFIERS):
                    if flat.get(k) == en_flat.get(k):
                        problems.append("%s: translated %s identical to en (mistake or loanword? leave it unclaimed)" % (code, k))
                        break

    # Call-site drift (ambiguity A): t() defaults must equal en.json values.
    calls = 0
    sources = glob.glob(os.path.join(JS_DIRS[0], "**", "*.js"), recursive=True) + [INDEX_HTML]
    for path in sources:
        try:
            src = open(path, encoding="utf-8").read()
        except OSError:
            continue
        for m in T_CALL_RE.finditer(src):
            calls += 1
            key = js_unescape(m.group("key"))
            dflt = js_unescape(m.group("dflt"))
            if key not in en_flat:
                problems.append("%s: t() key %r not in en.json" % (os.path.basename(path), key))
            elif dflt != en_flat[key]:
                problems.append("%s: t() default for %s != en.json value" % (os.path.basename(path), key))

    if problems:
        print("FAIL (%d call sites scanned):" % calls)
        print("\n".join(problems))
        return 1
    print("OK: 12 dicts key-complete (%d keys); allowlists exact; "
          "stubs honest; %d t() call sites drift-free." % (len(en_keys), calls))
    return 0


if __name__ == "__main__":
    sys.exit(main())
