#!/usr/bin/env python3
"""Inspect a locale's untranslated keys and its already-translated voice.

Read-only companion to the apply_i18n_*_chunk*.py scripts: it prints the keys
whose value is still byte-equal to the en master (grouped by section) and, for
each, the already-translated SIBLING strings of the same section, so a fill pass
can match the shipped dictionary's voice instead of inventing one.

Usage:
  python3 tooling/inspect_untranslated_locale.py ru
  python3 tooling/inspect_untranslated_locale.py ru --section account
  python3 tooling/inspect_untranslated_locale.py ru --translated 40
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "vanilla", "locales")


def flat(d, prefix=""):
    """Flatten a locale dict to dotted leaf keys, skipping _meta."""
    out = collections.OrderedDict()
    for k, v in d.items():
        if k == "_meta":
            continue
        if isinstance(v, dict):
            out.update(flat(v, prefix + k + "."))
        else:
            out[prefix + k] = v
    return out


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh, object_pairs_hook=collections.OrderedDict)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lang")
    ap.add_argument("--section", default=None)
    ap.add_argument("--translated", type=int, default=0,
                    help="show N already-translated keys of the section too")
    args = ap.parse_args()

    en = flat(load(os.path.join(BASE, "en.json")))
    loc = flat(load(os.path.join(BASE, "%s.json" % args.lang)))
    todo = [k for k in en if loc.get(k) == en[k]]
    done = [k for k in en if loc.get(k) != en[k]]

    counts = collections.Counter(k.split(".")[0] for k in todo)
    print("# %s: %d keys total, %d untranslated, %d translated"
          % (args.lang, len(en), len(todo), len(done)))
    print("# sections (untranslated):")
    for sec, c in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        print("#   %-20s %d" % (sec, c))

    secs = [args.section] if args.section else sorted(counts)
    for sec in secs:
        keys = [k for k in todo if k.split(".")[0] == sec]
        if not keys and args.section is None:
            continue
        print("\n===== %s (%d untranslated) =====" % (sec, len(keys)))
        for k in keys:
            en_v = en[k]
            multi = "\n" in en_v
            print("%s  EN: %s" % (k, repr(en_v)))
            if multi:
                for line in en_v.split("\n"):
                    print("      | %s" % line)
            if loc.get(k) != en_v:
                print("   RU: %s" % repr(loc.get(k)))
        if args.translated:
            shown = [k for k in done if k.split(".")[0] == sec][:args.translated]
            print("  --- already-translated siblings (%d) ---" % len(shown))
            for k in shown:
                print("%s  RU: %s" % (k, repr(loc[k])))
    return 0


if __name__ == "__main__":
    sys.exit(main())