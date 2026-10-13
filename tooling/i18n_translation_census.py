#!/usr/bin/env python3
"""Read-only per-locale translation census — the record `_meta.translated` used
to store, recomputed from the shipped bytes instead of kept as a claim.

WHY THIS EXISTS. Under `_meta` v1 every non-English dict carried a `translated`
list naming the keys a human had translated; `i18n.js`'s `allowlisted()` read
it, and check_i18n.py / validate_translations.py refuted it ("this key claims to
be translated but ships the English string"). `_meta` v2 (gate 8) has no such
field — it declares `coverage` (a value exists for every key), `provenance`
(machine or human) and `verified` (human sign-offs) — because the old field
conflated a COVERAGE claim with a TRUST claim and nothing could test the second
half, which is how thousands of false claims accumulated in silence.

Dropping the list therefore loses nothing that the two files cannot reproduce:
`{k : value(locale, k) != value(en, k)}` IS the v1 `translated` set, exactly,
because v1's own rule required a listed key to differ from English. This tool
prints that set (and its count) on demand, plus a stable hash of a locale's
non-`_meta` payload so a metadata-only rewrite can be proven value-neutral.

Usage:
  python3 tooling/i18n_translation_census.py            # one line per locale
  python3 tooling/i18n_translation_census.py --keys es  # the differing keys
  python3 tooling/i18n_translation_census.py --hash es  # payload sha256
  python3 tooling/i18n_translation_census.py --json     # machine-readable

Stdlib only. Writes nothing; reads vanilla/locales/*.json only.
"""
import glob
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCALES = os.path.join(HERE, "..", "vanilla", "locales")
CODE_RE = re.compile(r"[A-Za-z][\w-]*")


def flatten(d, prefix=""):
    """Flatten a locale dict to {"dotted.key": value}, skipping `_meta`.

    Same rule as tooling/check_i18n.py: recurse into nested dicts with a
    "parent." prefix, leaves become prefix+key. `d` must be a dict (the caller
    has already checked); a malformed one raises and the caller reports it."""
    out = {}
    for key, value in d.items():
        if key == "_meta":
            continue
        if isinstance(value, dict):
            out.update(flatten(value, prefix + key + "."))
        else:
            out[prefix + key] = value
    return out


def payload_hash(flat):
    """sha256 of a locale's non-`_meta` payload, canonical and key-order free.

    Params: flat — the flattened dict from flatten().
    Returns: a 64-char hex digest. Hashes a canonical JSON encoding of every
    key/value pair sorted by key, so a reordering of the file cannot change the
    digest while a single changed character in a single string does. Never
    raises for string values; non-JSON-serialisable leaves raise, which the
    caller surfaces."""
    canonical = json.dumps(flat, sort_keys=True, ensure_ascii=False,
                           separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def census(code, en_flat):
    """Every census figure for one locale, all derived from the shipped files.

    Params: code — locale code string ("es"); en_flat — flattened en.json.
    Returns: a dict with the locale code, its `_meta` shape, the three v2
    counters, the number of values differing from en ("differs"), the number
    equal to en ("identical"), and whether the v1 `translated` list, when the
    dict still carries one, equals the differs set.
    Returns None when the locale file is missing or unparseable; the caller
    prints the reason. Never raises for a readable dict."""
    path = os.path.join(LOCALES, code + ".json")
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    flat = flatten(data)
    meta = data.get("_meta") if isinstance(data.get("_meta"), dict) else {}
    differs = sorted(k for k, v in flat.items() if en_flat.get(k) != v)
    row = {
        "code": code,
        "meta_version": meta.get("version"),
        "coverage": len(meta["coverage"]) if isinstance(meta.get("coverage"), list) else None,
        "verified": len(meta["verified"]) if isinstance(meta.get("verified"), list) else None,
        "high_risk": len(meta["high_risk"]) if isinstance(meta.get("high_risk"), list) else None,
        "translated": len(meta["translated"]) if isinstance(meta.get("translated"), list) else None,
        "keys": len(flat),
        "differs": differs,
        "identical": len(flat) - len(differs),
    }
    claimed = meta.get("translated")
    # Only meaningful while a dict still carries the v1 field: it is the claim
    # this tool recomputes, so equality is the proof that nothing was lost.
    row["translated_equals_differs"] = (sorted(claimed) == differs
                                        if isinstance(claimed, list) else None)
    return row


def main(argv):
    """Print the census for every locale, or the detail for one locale.

    Params: argv — sys.argv[1:]. `--keys <code>` prints the differing keys one
    per line; `--hash <code>` prints the payload digest; `--json` switches the
    default listing to a JSON array. Returns: a POSIX exit status (0 ok,
    1 unreadable input, 2 bad invocation)."""
    as_json = "--json" in argv
    detail = [a for a in argv if a not in ("--json", "--keys", "--hash")]
    want_keys = "--keys" in argv
    want_hash = "--hash" in argv

    try:
        with open(os.path.join(LOCALES, "en.json"), encoding="utf-8") as fh:
            en_flat = flatten(json.load(fh))
    except (OSError, ValueError) as exc:
        print("FAIL: en.json unreadable: %s" % exc)
        return 1

    if len(detail) > 1:
        print("usage: i18n_translation_census.py [--json] [--keys <code> | --hash <code>]",
              file=sys.stderr)
        return 2
    codes = ([detail[0]] if detail else
             sorted(os.path.splitext(os.path.basename(p))[0]
                    for p in glob.glob(os.path.join(LOCALES, "*.json"))))

    rows = []
    for code in codes:
        if CODE_RE.fullmatch(code) is None:
            print("invalid locale code: %r" % code, file=sys.stderr)
            return 2
        row = census(code, en_flat)
        if row is None:
            print("FAIL: %s.json unreadable or not an object" % code)
            return 1
        rows.append(row)

        if want_keys:
            print("\n".join(row["differs"]) or "(no key differs from en)")
            continue
        if want_hash:
            print("%s  %s" % (row["code"], payload_hash(
                {k: v for k, v in
                 flatten(json.load(open(os.path.join(LOCALES, code + ".json"),
                                       encoding="utf-8"))).items()})))
            continue
        if not as_json:
            print("%-3s _meta v%-4s keys %-5d differs %-5d identical %-5d "
                  "coverage %-5s verified %-5s high_risk %-5s v1-translated %-5s "
                  "== differs: %s"
                  % (row["code"], row["meta_version"], row["keys"], len(row["differs"]),
                     row["identical"], row["coverage"], row["verified"], row["high_risk"],
                     row["translated"], row["translated_equals_differs"]))

    if as_json and not (want_keys or want_hash):
        print(json.dumps([{k: v for k, v in row.items() if k != "differs"}
                          for row in rows], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))