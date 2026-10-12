#!/usr/bin/env python3
"""Sanitizer: drop false translation claims from every locale allowlist.

check_i18n.py holds ALL dicts to one honesty rule now (generalized from the
old es-only branch): an allowlisted ("translated") key must DIFFER from
English; unclaimed non-identifier keys must EQUAL English (honest stubs).
History: only es was ever audited, so the other ten locales accumulated
750-930 allowlisted-but-identical keys each (never-translated bulk content
plus recent-feature stubs) that the old coverage-only check waved through.

This script drops exactly the allowlisted keys whose value is byte-identical
to en (verified per key at runtime, per locale). Values are untouched, so
rendering is byte-identical; translators re-add a key to the allowlist if
and when they provide a real string (the add_*_i18n.py scripts run the other
direction — note they re-append, so re-running one re-pollutes; check_i18n
will go red again by design if that happens).

Supersedes fix_es_allowlist.py (es-only predecessor, same method).
Safe to re-run (idempotent). Verify with: python3 tooling/check_i18n.py
"""
import json
import sys

LOCALES = ["de", "es", "fr", "it", "ja", "ko", "ru", "tr", "zh", "hi", "pt"]


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


def main():
    en_flat = flat(json.load(open("vanilla/locales/en.json", encoding="utf-8")))
    en_keys = set(en_flat)
    total_dropped = 0
    for code in LOCALES:
        path = "vanilla/locales/%s.json" % code
        d = json.load(open(path, encoding="utf-8"))
        f = flat(d)
        if set(f) != en_keys:
            print("ABORT %s: key drift, fix keys before sanitizing" % code)
            return 1
        inv = d["_meta"]["translated"]
        # Guard: an unclaimed key differing from en is a dishonest stub in
        # the other direction — abort instead of touching anything.
        for k in sorted(en_keys - set(inv)):
            if k in ("settings.network_mainnet", "settings.network_testnet",
                      "settings.custom_placeholder", "settings.pending",
                      "settings.dash", "settings.theme_original_blue",
                      "settings.theme_light", "settings.theme_dark",
                      "shell.brand"):
                continue
            if f.get(k) != en_flat.get(k):
                print("ABORT %s: non-allowlisted %s differs from en" % (code, k))
                return 1
        drop = sorted(k for k in inv if f.get(k) == en_flat.get(k))
        if drop:
            d["_meta"]["translated"] = sorted(set(inv) - set(drop))
            json.dump(d, open(path, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=2)
            open(path, "a", encoding="utf-8").write("\n")
        total_dropped += len(drop)
        print("%s: dropped %4d false claims, %4d genuinely translated, %4d honest stubs"
              % (code, len(drop), len(d["_meta"]["translated"]),
                 len(en_keys) - len(d["_meta"]["translated"])))
    print("total dropped: %d" % total_dropped)
    return 0


if __name__ == "__main__":
    sys.exit(main())
