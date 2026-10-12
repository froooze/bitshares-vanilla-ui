#!/usr/bin/env python3
"""One-shot sanitizer: drop false translation claims from the es allowlist
(issue follow-up).

check_i18n.py holds partially-translated dicts to two rules: identifiers
must NOT be allowlisted, and allowlisted values must DIFFER from English.
es.json allowlists 678 keys byte-identical to en — mostly never-translated
bulk content (account.op_*/sum_*, market_net.*, approval.*, older about.*
strings) plus recent-feature stubs and inherently-identical tokens. Every
one is an untranslated string wrongly claimed as translated.

This script drops exactly the allowlisted keys whose es value is
byte-identical to en (verified per key at runtime); keys that genuinely
differ stay claimed untouched.

This script drops exactly the allowlisted keys whose es value is
byte-identical to en (verified per key at runtime; anything differing
aborts instead of being touched). Values are untouched, so rendering is
unchanged; translators re-add a key to the allowlist if and when they
provide a real Spanish string (the add_*_i18n.py precedent runs the other
direction). check_i18n.py + validate_translations.py es verify afterward.

Safe to re-run (idempotent). Verify with: python3 tooling/check_i18n.py
"""
import io
import json
import sys

PATH = "vanilla/locales/es.json"

# Keys whose es value is byte-identical to en (verified 2026-10-12):
def main():
    with io.open(PATH, encoding="utf-8") as f:
        data = json.load(f)
    with io.open("vanilla/locales/en.json", encoding="utf-8") as f:
        en = json.load(f)

    def flat(d, prefix=""):
        out = {}
        for k, v in d.items():
            if k == "_meta":
                continue
            if isinstance(v, dict):
                out.update(flat(v, prefix + k + "."))
            else:
                out[prefix + k] = v
        return out

    en_flat = flat(en)
    es_flat = flat(data)
    inv = data["_meta"]["translated"]
    dropped = []
    for full in list(inv):
        if es_flat.get(full) != en_flat.get(full):
            continue  # genuine translation (differs from en): stays claimed
        # Byte-identical to en: not a translation. Drop the false claim.
        # (Values stay as-is, so rendering is unchanged.)
        inv.remove(full)
        dropped.append(full)
    data["_meta"]["translated"] = sorted(inv)
    if dropped:
        with io.open(PATH, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
    print("dropped %d false claims from %s" % (len(dropped), PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
