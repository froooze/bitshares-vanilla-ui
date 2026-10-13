#!/usr/bin/env python3
"""Validate one translated locale dict against the English master.

Pre-merge gate: proves vanilla/locales/<code>.json is an honest, complete
translation of vanilla/locales/en.json before it may merge.

Usage:
  python3 tooling/validate_translations.py <code>             # e.g. ru
  python3 tooling/validate_translations.py --fix-meta <code>  # rewrite _meta only

Exit 0 = valid. Exit 1 = invalid (problems listed) or unreadable input.
Exit 2 = bad invocation.

Checks, in order (all must pass):
  1. Files parse: en.json loads as master, <code>.json parses.
  2. Key-completeness: flattened key set of <code>.json EQUALS en.json's
     set (same flatten rule as tooling/check_i18n.py: skip _meta, recurse
     dicts with "parent." prefixes, leaves are prefix+key).
  3. Placeholder preservation: for every key whose en value holds
     %(name)s-style placeholders, the translated value holds EXACTLY the
     same multiset of placeholders.
  4. Identifier preservation: any en value matching
     ^(1\.\d+\.\d+|#[#/][\w\-.?=&%/]*|https?://\S+|wss?://\S+)$ as a whole
     must be byte-verbatim equal in the translation; the same holds for
     the full keys settings.network_mainnet, settings.network_testnet,
     settings.custom_placeholder, settings.pending, settings.dash,
     settings.theme_original_blue, settings.theme_light,
     settings.theme_dark, shell.brand. (%(name)s-adjacent glue is
     covered by check 3, not here.)
  5. No-empty: every translated value is a string, and none is
     empty/whitespace-only unless en is.
  6. _meta, VERSION-AWARE. Two shapes are accepted, and both must stay
     accepted — every dict in the tree is v1 today, and the v1 rules are
     NOT replaced by the v2 rules:
     v1 (the original): version == 1, untranslated is false,
        sorted(translated) == sorted(en master key set), and no CLAIMED key's
        value equals en (outside the values check 4 requires verbatim). That
        last rule is what makes the old lie fatal: a v1 dict that lists a key
        in `translated` while shipping the English string is claiming a
        translation it does not have, and the claim is refutable from the
        bytes, so it is a failure.
     v2 (the three-state model): version == 2 with
        provenance in {machine, human}, coverage == the en key set exactly,
        and verified / high_risk naming only keys that are in en (hence in
        coverage). `coverage` is a COVERAGE claim ("this dict has a value for
        every key"); `provenance` is a TRUST claim ("a human reviewed this");
        `verified` lists the keys a human signed off. See check_meta_v2 for
        why a verified value equal to en is fatal while a non-verified one is
        merely a review note.
     A dict carrying `version: 2` but any v1 field (or the reverse) is
     rejected by the shape rules, and --fix-meta never rewrites one shape
     into the other.

--fix-meta rewrites only _meta, in whichever shape the file already is:
  v1 -> {"version": 1, "untranslated": false, "translated": sorted(keys)}
  v2 -> {"version": 2, "provenance": <kept, else "machine">,
         "coverage": sorted(keys), "verified": sorted(kept),
         "high_risk": sorted(kept)}
and writes the file back with json.dumps(indent=2, ensure_ascii=False)
plus a trailing newline. Round-trip fidelity was verified read-only
first: dumping an untouched en/de/es dict with those settings reproduces
the file byte-identically, so the rewrite touches _meta and nothing else.
`coverage` is recomputed from the dict's OWN keys rather than from en.json:
a coverage claim is the one field the tool can derive, and deriving it from
the file (instead of from the master) means --fix-meta can never manufacture
coverage a dict does not have. `verified` and `high_risk` are hand-curated
claims this tool has no authority to invent, so they are preserved verbatim.

Stdlib only. Never edits the reference checkouts.
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCALES = os.path.join(HERE, "..", "vanilla", "locales")

PLACEHOLDER_RE = re.compile(r"%\([^)]+\)s")
IDENTIFIER_RE = re.compile(r"^(1\.\d+\.\d+|#[#/][\w\-.?=&%/]*|https?://\S+|wss?://\S+)$")
CODE_RE = re.compile(r"[A-Za-z][\w-]*")

# Values identical in every language by design (network/theme ids,
# punctuation placeholders, brand). Same set as tooling/check_i18n.py.
VERBATIM_KEYS = {
    "settings.network_mainnet",
    "settings.network_testnet",
    "settings.custom_placeholder",
    "settings.pending",
    "settings.dash",
    "settings.theme_original_blue",
    "settings.theme_light",
    "settings.theme_dark",
    "shell.brand",
}

SHOW_MAX = 20

# Deliberate empties (see tooling/merge_translations.py EXCEPT_EMPTY): the
# translation is complete without this fragment; the sibling fragment carries
# the whole meaning. Exempt from check 5 only — all other checks still apply.
EXCEPT_EMPTY = {"gateway.coins_failed_prefix"}


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


def must_equal_en_keys(en_flat):
    """Keys whose value this gate REQUIRES to equal English byte-for-byte:
    the named verbatim keys, plus any value that is itself an object id, a
    route/anchor or a URL (check 4's two conditions, and only those).

    Computed once because two independent rules land on this exact set:
    check 4 demands the equality, and the v2 `verified` rule demands a
    difference. Re-spelling the predicate at each use site is how the two
    halves would drift apart — a key the gate would call identical in one
    place and translatable in the other, which is the whole failure mode
    this file exists to prevent."""
    out = set()
    for key, val in en_flat.items():
        if not isinstance(val, str):
            continue  # check 4 skips non-string English values; so do we
        if key in VERBATIM_KEYS or IDENTIFIER_RE.match(val):
            out.add(key)
    return out


def _key_list(meta, name, problems):
    """meta[name] as a list of strings, or None after reporting why it is not.

    A missing or wrongly-typed list is a shape failure, never a silently
    empty one: "coverage is absent" and "coverage is empty" mean the dict
    claims nothing, which is the machine-copying-English case the v2 model
    exists to surface, so it must be visible rather than inferred."""
    value = meta.get(name)
    if not isinstance(value, list) or any(not isinstance(v, str) for v in value):
        problems.append(
            "[6 _meta] %s must be a list of strings, got %s" % (name, _short(value, 40))
        )
        return None
    return value


def check_meta_v2(meta, flat, en_flat, en_keys):
    """Validate a `_meta` version-2 provenance dict. Returns problem lines.

    v2 exists because v1 conflated two different claims in one field.
    `_meta.translated` said both "this dict has a value for every key" (a
    COVERAGE claim, checkable from the file) and "a human translated these" (a
    TRUST claim, not checkable from the file at all). Nothing could test the
    second one, so 8,098 false translation claims accumulated in silence. v2
    splits them:

      coverage    "this dict has a value for every key" — checkable here.
      provenance  "machine" (filled by a machine, unreviewed) or "human".
      verified    the keys a human signed off.
      high_risk   the keys that must render with an English reference beside
                  them, because misreading them can cost money.

    Two rules carry the honesty, and the asymmetry between them is the point:

    * Every key in `verified` must DIFFER from en. A human signed it off, so
      an English value means the claim itself is wrong — refutable from the
      bytes, therefore fatal.
    * A value equal to en that is NOT verified is NOT fatal here. A machine
      string may legitimately coincide with English (loanwords: DEX, HTLC,
      URL, a brand), and no gate can tell a loanword from a machine that
      copied English. It can only queue the question for a human, which
      tooling/check_i18n.py does as a counted review note. Failing here
      instead would make every machine-filled locale unfalsifiable.
    * A verified key whose value must equal en BY DESIGN (identifier, brand,
      network/theme id) is rejected on a separate ground: it is not a
      translation, so "verified" is not a claim that can be made about it at
      all — the same reason v1 forbade identifiers in its allowlist.
    * `provenance: "human"` with an empty `verified` is a contradiction and
      is fatal. A human review that signed off nothing is exactly how a
      machine dict would silence the "machine translated" warning for good,
      so the cheap move has to be the loud one."""
    problems = []

    provenance = meta.get("provenance")
    if provenance not in ("machine", "human"):
        problems.append(
            '[6 _meta] provenance must be "machine" or "human", got %s'
            % _short(provenance, 24)
        )

    coverage = _key_list(meta, "coverage", problems)
    verified = _key_list(meta, "verified", problems)
    high_risk = _key_list(meta, "high_risk", problems)

    if coverage is not None and set(coverage) != en_keys:
        missing = sorted(en_keys - set(coverage))
        extra = sorted(set(coverage) - en_keys)
        problems.append(
            "[6 _meta] coverage drift: coverage lists %d key(s), en has %d "
            "(missing %d: %s; extra %d: %s)"
            % (len(coverage), len(en_keys), len(missing), _capped(missing),
               len(extra), _capped(extra))
        )

    # Subsets are tested against the EN key set, which is what `coverage` is
    # separately required to equal: the two rules cannot disagree, and when
    # coverage itself is broken the coverage message above is the accurate
    # diagnosis, so it should not be reported a second time per key.
    for name, keys in (("verified", verified), ("high_risk", high_risk)):
        if keys is None:
            continue
        unknown = sorted(set(keys) - en_keys)
        if unknown:
            problems.append(
                "[6 _meta] %s lists %d key(s) that are not in en.json, and so "
                "not in coverage either: %s" % (name, len(unknown), _capped(unknown))
            )

    verbatim = must_equal_en_keys(en_flat)
    if verified is not None:
        bad_ident = sorted(set(verified) & verbatim)
        if bad_ident:
            problems.append(
                "[6 _meta] verified must not claim keys whose value must equal "
                "en by design (identifier / verbatim), %d: %s — such a value is "
                "identical by construction, not untranslated"
                % (len(bad_ident), _capped(bad_ident))
            )
        same = [
            k for k in sorted(set(verified) - verbatim)
            if flat.get(k) == en_flat.get(k)
        ]
        for k in same[:SHOW_MAX]:
            problems.append(
                "[6 _meta] verified %s is identical to en — a human signed it "
                "off, so an English value means the claim is wrong" % k
            )
        if len(same) > SHOW_MAX:
            problems.append(
                "[6 _meta] (+%d more verified key(s) identical to en)"
                % (len(same) - SHOW_MAX)
            )

    if provenance == "human" and (verified is None or not verified):
        problems.append(
            '[6 _meta] provenance "human" requires at least one verified key: '
            "a human review that signed off nothing is a contradiction — the "
            'dict is machine-filled, so it must say "machine"'
        )

    return problems


def _short(value, width=64):
    text = value if isinstance(value, str) else repr(value)
    return text if len(text) <= width else text[: width - 1] + "\u2026"


def _capped(items):
    shown = list(items[:SHOW_MAX])
    if len(items) > SHOW_MAX:
        shown.append("(+%d more)" % (len(items) - SHOW_MAX))
    return ", ".join(shown)


def validate(code):
    problems = []

    # --- Check 1: files parse; en.json loads as master. ---
    try:
        with open(os.path.join(LOCALES, "en.json"), encoding="utf-8") as fh:
            en = json.load(fh)
    except (OSError, ValueError) as exc:
        print("FAIL: en.json unreadable: %s" % exc)
        return 1
    if not isinstance(en, dict):
        print("FAIL: en.json master is not an object")
        return 1
    try:
        with open(os.path.join(LOCALES, code + ".json"), encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        print("FAIL: %s.json unreadable: %s" % (code, exc))
        return 1
    if not isinstance(data, dict):
        print("FAIL: %s.json is not an object" % code)
        return 1

    en_flat = flatten(en)
    en_keys = set(en_flat)
    flat = flatten(data)
    keys = set(flat)
    common = en_keys & keys

    # --- Check 2: key-completeness against the en master set. ---
    missing = sorted(en_keys - keys)
    extra = sorted(keys - en_keys)
    if missing:
        problems.append(
            "[2 key-completeness] missing %d key(s): %s"
            % (len(missing), _capped(missing))
        )
    if extra:
        problems.append(
            "[2 key-completeness] extra %d key(s): %s" % (len(extra), _capped(extra))
        )

    # --- Check 3: placeholder preservation (exact multiset match). ---
    ph_bad = []
    for key in sorted(common):
        en_val = en_flat[key]
        if not isinstance(en_val, str):
            continue
        want = PLACEHOLDER_RE.findall(en_val)
        if not want:
            continue
        got_val = flat[key]
        if not isinstance(got_val, str):
            continue  # non-string values are reported once, under check 5
        got = PLACEHOLDER_RE.findall(got_val)
        if collections.Counter(got) != collections.Counter(want):
            ph_bad.append(
                "%s: en placeholders %s, %s has %s"
                % (key, sorted(want), code, sorted(got))
            )
    for line in ph_bad[:SHOW_MAX]:
        problems.append("[3 placeholders] " + line)
    if len(ph_bad) > SHOW_MAX:
        problems.append("[3 placeholders] (+%d more)" % (len(ph_bad) - SHOW_MAX))

    # --- Check 4: identifier preservation (byte-verbatim). ---
    id_bad = []
    for key in sorted(common):
        en_val = en_flat[key]
        if not isinstance(en_val, str):
            continue
        if key not in VERBATIM_KEYS and not IDENTIFIER_RE.match(en_val):
            continue
        got_val = flat[key]
        if not isinstance(got_val, str):
            continue  # reported once, under check 5
        if got_val != en_val:
            id_bad.append(
                "%s: must stay verbatim %r, %s has %r"
                % (key, en_val, code, _short(got_val))
            )
    for line in id_bad[:SHOW_MAX]:
        problems.append("[4 identifiers] " + line)
    if len(id_bad) > SHOW_MAX:
        problems.append("[4 identifiers] (+%d more)" % (len(id_bad) - SHOW_MAX))

    # --- Check 5: values are strings; no-empty unless en is. ---
    empty_bad = []
    for key in sorted(common):
        got_val = flat[key]
        if not isinstance(got_val, str):
            empty_bad.append(
                "%s: expected string value in %s, got %s"
                % (key, code, type(got_val).__name__)
            )
            continue
        if got_val.strip() == "":
            en_val = en_flat[key]
            en_empty = isinstance(en_val, str) and en_val.strip() == ""
            if not en_empty and key not in EXCEPT_EMPTY:
                empty_bad.append(
                    "%s: empty/whitespace-only in %s but en is %r"
                    % (key, code, _short(en_val))
                )
    for line in empty_bad[:SHOW_MAX]:
        problems.append("[5 no-empty] " + line)
    if len(empty_bad) > SHOW_MAX:
        problems.append("[5 no-empty] (+%d more)" % (len(empty_bad) - SHOW_MAX))

    # --- Check 6: _meta shape against the en master key set. ---
    # VERSION-AWARE, and deliberately not "the v2 rules replace the v1 ones":
    # every dict in the tree is v1 today, and each shape's rules are only
    # meaningful against its own shape's claims.
    meta = data.get("_meta")
    if not isinstance(meta, dict):
        problems.append("[6 _meta] _meta missing or not an object")
    elif meta.get("version") == 2:
        problems.extend(check_meta_v2(meta, flat, en_flat, en_keys))
    else:
        ver = meta.get("version")
        if type(ver) is not int or ver != 1:
            problems.append("[6 _meta] version must be 1, got %r" % (ver,))
        if meta.get("untranslated") is not False:
            problems.append(
                "[6 _meta] untranslated must be false, got %r"
                % (meta.get("untranslated"),)
            )
        translated = meta.get("translated")
        if not isinstance(translated, list) or any(
            not isinstance(t, str) for t in translated
        ):
            problems.append("[6 _meta] translated must be a list of strings")
            translated = None
        elif sorted(translated) != sorted(en_keys):
            miss = sorted(en_keys - set(translated))
            over = sorted(set(translated) - en_keys)
            if miss or over:
                problems.append(
                    "[6 _meta] translated lists %d key(s), en has %d "
                    "(missing %d: %s; extra %d: %s)"
                    % (
                        len(translated),
                        len(en_keys),
                        len(miss),
                        _capped(miss),
                        len(over),
                        _capped(over),
                    )
                )
            else:
                problems.append(
                    "[6 _meta] translated has the right key set but wrong "
                    "multiplicity (duplicates?), %d entries for %d keys"
                    % (len(translated), len(en_keys))
                )
        if translated is not None:
            # The v1 lie, kept fatal: `translated` IS the claim "these keys
            # are translated", so a claimed key whose value is the English
            # string is a false claim that the bytes themselves refute. v2
            # moves the identical-value rule onto `verified` (a real trust
            # claim) and downgrades the merely-covered case to a review note;
            # v1 has no such split, so "listed and identical" can only mean
            # one thing here. Checked even when the allowlist is ALSO
            # incomplete: the two are independent faults and a translator
            # needs to see both, not whichever one sorted first.
            verbatim = must_equal_en_keys(en_flat)
            same = [t for t in sorted(set(translated) - verbatim)
                    if flat.get(t) == en_flat.get(t)]
            for t in same[:SHOW_MAX]:
                problems.append(
                    "[6 _meta] translated %s is identical to en — the allowlist "
                    "claims it is translated (mistake, or a loanword left "
                    "claimed?)" % t
                )
            if len(same) > SHOW_MAX:
                problems.append(
                    "[6 _meta] (+%d more claimed key(s) identical to en)"
                    % (len(same) - SHOW_MAX)
                )

    if problems:
        noun = "problem" if len(problems) == 1 else "problems"
        print("FAIL: %s.json invalid (%d %s):" % (code, len(problems), noun))
        for line in problems:
            print(line)
        return 1
    identical = sum(1 for k in en_keys if flat.get(k) == en_flat[k])
    print(
        "OK: %s.json valid "
        "(%d keys; placeholders, identifiers, non-empty values, _meta v%d green; "
        "%d value(s) equal en — review candidates, not failures)."
        % (code, len(en_keys), meta.get("version"), identical)
    )
    return 0


def fix_meta(code):
    """Rewrite only `_meta`, preserving whichever shape the file already is.

    Rewriting a v2 dict into the v1 form would silently DEMOTE it: the
    provenance claim would vanish and `verified` (a human's sign-off) would be
    replaced by a blanket "these keys are translated" — the exact lie the v2
    model exists to stop, produced by the gate that is supposed to be
    enforcing it. So the shape is read first and kept."""
    path = os.path.join(LOCALES, code + ".json")
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        print("FAIL: %s.json unreadable: %s" % (code, exc))
        return 1
    if not isinstance(data, dict):
        print("FAIL: %s.json is not an object" % code)
        return 1
    flat = flatten(data)
    old = data.get("_meta") or {}
    if old.get("version") == 2:
        # coverage is the only field derived here, and it is derived from the
        # dict's OWN keys: --fix-meta must never manufacture a coverage claim
        # the file cannot support (that would be the lie, generated by the
        # tool meant to catch it). `provenance` degrades to "machine" when it
        # is not a legal value, because "machine" is the honest direction to
        # fail in: it lights the badge, it never hides a review. `verified` and
        # `high_risk` are hand-curated claims this tool has no authority to
        # invent, so they are preserved exactly.
        provenance = old.get("provenance")
        if provenance not in ("machine", "human"):
            provenance = "machine"
        data["_meta"] = {
            "version": 2,
            "provenance": provenance,
            "coverage": sorted(flat),
            "verified": sorted(old.get("verified") or []),
            "high_risk": sorted(old.get("high_risk") or []),
        }
        shape = ("version=2, provenance=%s, coverage=%d keys, verified=%d, "
                 "high_risk=%d"
                 % (provenance, len(flat), len(data["_meta"]["verified"]),
                    len(data["_meta"]["high_risk"])))
    else:
        data["_meta"] = {
            "version": 1,
            "untranslated": False,
            "translated": sorted(flat),
        }
        shape = "version=1, untranslated=false, translated=%d keys" % len(flat)
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    json.loads(text)  # sanity: output must stay parseable
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("FIXED: %s.json _meta rewritten (%s)." % (code, shape))
    return 0


def main(argv):
    fix = "--fix-meta" in argv
    rest = [a for a in argv if a != "--fix-meta"]
    if len(rest) != 1 or rest[0].startswith("-"):
        print(
            "usage: python3 tooling/validate_translations.py [--fix-meta] <code>",
            file=sys.stderr,
        )
        return 2
    code = rest[0]
    if CODE_RE.fullmatch(code) is None:
        print("invalid locale code: %r" % code, file=sys.stderr)
        return 2
    if fix:
        return fix_meta(code)
    return validate(code)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
