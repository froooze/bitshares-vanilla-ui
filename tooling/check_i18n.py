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
  7. KEYED SIGNING-DIALOG LINES (gate 7). Task 4 routed the ConfirmDialog /
     UnlockConfirm title, row term and fee term through RiskText, so a
     keyed line can disclose its English master one tap away. A key that
     does not exist, or that names a DIFFERENT string than the line
     actually shows, is WORSE than no key at all: the widget then
     discloses a confidently wrong English reference on the one dialog a
     user reads before signing — and nothing else in this file can see
     it, because check 6 is equally happy with either key and a missing
     key simply degrades to plain text. So:
       7a. every titleKey/feeTermKey literal exists in en.json;
       7b. every titleKey/feeTermKey that has a sibling title/feeTerm in
           the SAME object literal names exactly the key that sibling's
           t() call uses (and that t() default is the en value);
       7c. every 4-slot confirm row [t("k", d), value, raw, "rk"] has
           k == rk.
     Scans are bracket-aware (strings, comments and nesting respected), so
     a value like Format.formatAmount(a, b) never splits the row it is in.
     Not reimplemented per call site: this is the one gate for the whole
     tree, and tooling/i18n-key-gate-test.js proves it fails on a wrong
     key and on a missing key.

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

# --- gate 7: keyed signing-dialog lines -------------------------------------
# A property whose value is a bare string literal (titleKey: "x.y"), and the
# t() call a labelled line is expected to be built from. Both are matched on
# the SOURCE TEXT of one element/property, so they are safe to run over
# bracketed spans.
STR_LITERAL_RE = re.compile(r'^\s*"(?P<v>(?:\\.|[^"\\])*)"\s*$')
T_HEAD_RE = re.compile(r'^\s*t\(\s*"(?P<key>(?:\\.|[^"\\])*)"\s*,')
KEYED_PROP_RE = re.compile(r'^\s*(?P<prop>titleKey|feeTermKey)\s*:\s*"'
                           r'(?P<v>(?:\\.|[^"\\])*)"\s*$')
LABEL_PROP_RE = re.compile(r'^\s*(?P<prop>title|feeTerm)\s*:\s*(?P<rest>.*)$', re.S)
ASSIGN_KEY_RE = re.compile(r'\.(?P<prop>titleKey|feeTermKey)\s*=\s*"'
                           r'(?P<v>(?:\\.|[^"\\])*)"')
ASSIGN_LABEL_RE = re.compile(r'\.(?P<prop>title|feeTerm)\s*=\s*t\(\s*'
                             r'"(?P<v>(?:\\.|[^"\\])*)"')
# Shape of a dotted locale key ("credit.owner", "help.topic_accounts-permissions_title").
# Used to tell a confirm row's 4th slot (a locale key) from an unrelated
# 4-element array whose 4th element happens to be a string — e.g. the
# dashboard tile row [label, description, "#/route", badge] in debit-ui.js,
# which is the same shape with a completely different meaning. Hyphens are
# legal inside a key (help.topic_accounts-permissions_title), so they must be
# accepted: an over-narrow shape silently SKIPS gated rows, which is the exact
# "the gate could not see it" hole this gate exists to close.
LOCALE_KEY_SHAPE_RE = re.compile(r"^[a-z][a-z0-9_-]*(?:\.[a-z0-9_-]+)+$")

# Files whose `titleKey:` fields are NOT signing-dialog keys. Both are
# pre-existing tables from the slice-17 menu/SEO work, they pair the key with a
# PLAIN STRING title (not a t() call), and no RiskText widget ever reads them —
# including them would either flag 13 correct SEO rows or, worse, tempt someone
# into weakening the rule for every future file. Kept as an explicit list (not a
# shape test) so a THIRD file that pairs a hardcoded title with a key FAILS
# loudly instead of inheriting a silent exemption.
NON_DIALOG_TITLEKEY_FILES = {
    "router.js": "SEO meta table — titles are plain strings consumed by t(key, title)",
    "menu-ui.js": "burger-menu nav table — pairs titleKey with titleDefault, not title",
}


def _skip_string(src, i):
    """i points at a quote character; return the index just past its match."""
    q = src[i]
    i += 1
    while i < len(src):
        c = src[i]
        if c == "\\":
            i += 2
            continue
        if c == q:
            return i + 1
        i += 1
    return i


def _skip_trivia(src, i):
    """Advance past whitespace and // / /* */ comments. Never leaves src."""
    n = len(src)
    while i < n:
        c = src[i]
        if c in " \t\r\n":
            i += 1
        elif c == "/" and i + 1 < n and src[i + 1] in "/*":
            if src[i + 1] == "/":
                j = src.find("\n", i)
                i = n if j == -1 else j + 1
            else:
                j = src.find("*/", i + 2)
                i = n if j == -1 else j + 2
        else:
            break
    return i


def _split_top(src, start, end):
    """Split src[start:end] on TOP-LEVEL commas -> [(begin, end), ...] spans.
    Strings, comments and nested ()/[]/{} are respected, so a value such as
    Format.formatAmount(a, b) never splits the confirm row it sits in.
    Empty trailing elements are dropped; the input span is caller-bracketed."""
    out = []
    depth = 0
    i = start
    elem = start
    while i < end:
        c = src[i]
        if c in "\"'":
            i = _skip_string(src, i)
            continue
        if c == "/" and i + 1 < end and src[i + 1] in "/*":
            i = _skip_trivia(src, i)
            continue
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif c == "," and depth == 0:
            out.append((elem, i))
            elem = i + 1
        i += 1
    if src[elem:end].strip():
        out.append((elem, end))
    return out


def _brackets(src):
    """Every balanced ()/[]/{} pair -> [((open, close), ...)].
    Strings and comments are skipped, so braces inside prose do not pair up."""
    pairs = []
    stack = []
    i = 0
    n = len(src)
    while i < n:
        c = src[i]
        if c in "\"'":
            i = _skip_string(src, i)
            continue
        if c == "/" and i + 1 < n and src[i + 1] in "/*":
            i = _skip_trivia(src, i)
            continue
        if c in "([{":
            stack.append((c, i))
        elif c in ")]}":
            want = {")": "(", "]": "[", "}": "{"}[c]
            if stack and stack[-1][0] == want:
                pairs.append((stack[-1][1], i))
                stack.pop()
        i += 1
    return pairs


def _inner_spans(src, pairs, opener):
    """Body spans (just inside) of every bracket pair opened by `opener`."""
    return [(o + 1, c) for (o, c) in pairs if src[o] == opener]


def check_keyed_signing_lines(path, src, en_flat, problems):
    """Gate 7 — every keyed ConfirmDialog/UnlockConfirm line names the string
    it actually shows. Returns (title_like, row_slots) counts for the report.
    Failure modes are deliberately LOUD: an unverifiable keyed line (a sibling
    label that is not a t() call, or none at all) is reported, not skipped —
    'the gate could not see it' is how a wrong key reaches production."""
    base = os.path.basename(path)
    pairs = _brackets(src)
    title_like = 0
    row_slots = 0

    # 7a/7b — titleKey / feeTermKey inside an object literal, paired with the
    # sibling title / feeTerm property of the SAME literal.
    for ob, cb in _inner_spans(src, pairs, "{"):
        props = {}
        keyed = []
        for b, e in _split_top(src, ob, cb):
            text = src[b:e]
            km = KEYED_PROP_RE.match(text)
            if km:
                keyed.append((km.group("prop"), js_unescape(km.group("v")), b))
                continue
            lm = LABEL_PROP_RE.match(text)
            if lm and lm.group("prop") not in props:
                props[lm.group("prop")] = lm.group("rest")
        for prop, key, _pos in keyed:
            if base in NON_DIALOG_TITLEKEY_FILES:
                # Exempt from 7b, still gated by 7a below.
                if key not in en_flat:
                    problems.append("%s: %s %r does not exist in en.json" % (base, prop, key))
                continue
            title_like += 1
            label_prop = "title" if prop == "titleKey" else "feeTerm"
            if key not in en_flat:
                problems.append("%s: %s %r does not exist in en.json" % (base, prop, key))
                continue
            label = props.get(label_prop)
            if label is None:
                # Not a confirm-dialog literal (menu-ui.js pairs titleKey with
                # titleDefault, router.js titles are SEO meta): only the
                # existence rule applies, and 7a already checked it.
                continue
            tm = T_HEAD_RE.match(label)
            if not tm:
                if base not in NON_DIALOG_TITLEKEY_FILES:
                    problems.append("%s: %s %r is not built from a t() call — its English "
                                    "reference cannot be verified (label is %r)"
                                    % (base, prop, key, " ".join(label.split())[:60]))
                continue
            tkey = js_unescape(tm.group("key"))
            if tkey != key:
                problems.append("%s: %s %r labels %s t(%r) — the dialog would disclose "
                                "the WRONG English reference" % (base, prop, key, label_prop, tkey))

    # 7a/7b (assignment form) — cfg.title = t("k"); cfg.titleKey = "k".
    for m in ASSIGN_KEY_RE.finditer(src):
        prop = m.group("prop")
        key = js_unescape(m.group("v"))
        title_like += 1
        if key not in en_flat:
            problems.append("%s: .%s %r does not exist in en.json" % (base, prop, key))
            continue
        label_prop = "title" if prop == "titleKey" else "feeTerm"
        prior = [x for x in ASSIGN_LABEL_RE.finditer(src, 0, m.start())
                 if x.group("prop") == label_prop]
        if not prior:
            problems.append("%s: .%s = %r has no preceding .%s = t(...) assignment to "
                            "verify against" % (base, prop, key, label_prop))
            continue
        if prior[-1].group("v") != key:
            problems.append("%s: .%s = %r labels .%s = t(%r) — the dialog would disclose "
                            "the WRONG English reference"
                            % (base, prop, key, label_prop, prior[-1].group("v")))

    # 7c — 4-slot confirm rows: [t("k", d), value, rawTitle, "rk"].
    for ab, cb in _inner_spans(src, pairs, "["):
        elems = _split_top(src, ab, cb)
        if len(elems) != 4:
            continue
        tm = T_HEAD_RE.match(src[elems[0][0]:elems[0][1]])
        sm = STR_LITERAL_RE.match(src[elems[3][0]:elems[3][1]])
        if not (tm and sm):
            continue
        rkey = js_unescape(sm.group("v"))
        if not LOCALE_KEY_SHAPE_RE.match(rkey):
            continue  # not a locale key: not a confirm row (see the shape note)
        row_slots += 1
        tkey = js_unescape(tm.group("key"))
        if tkey != rkey:
            if rkey not in en_flat:
                problems.append("%s: confirm row term %r has key %r, which does not exist "
                                "in en.json" % (base, tkey, rkey))
            else:
                problems.append("%s: confirm row t(%r) carries term key %r — the row would "
                                "disclose the WRONG English reference" % (base, tkey, rkey))
    return title_like, row_slots


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
    title_like = 0
    row_slots = 0
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
        if path.endswith(".js"):
            tl, rs = check_keyed_signing_lines(path, src, en_flat, problems)
            title_like += tl
            row_slots += rs

    if problems:
        print("FAIL (%d call sites scanned):" % calls)
        print("\n".join(problems))
        return 1
    print("OK: 12 dicts key-complete (%d keys); allowlists exact; "
          "stubs honest; %d t() call sites drift-free; %d keyed dialog titles / "
          "fee terms and %d confirm-row term keys all name the string they label."
          % (len(en_keys), calls, title_like, row_slots))
    return 0


if __name__ == "__main__":
    sys.exit(main())
