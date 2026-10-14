#!/usr/bin/env python3
"""Apply a review agent's JSON corrections to the locale dicts — mechanically.

Usage:
    python3 tooling/apply_review_answers.py <answers.json> [--apply]

The answers file MUST follow the REVIEW.md contract exactly:
    {"<lang>": {"<dotted.key>": {"original": "...", "replacement": "..."}}}

Rules, in order:
  1. `original` must equal the dict's current value BYTE-FOR-BYTE. A mismatch
     means the fix is SKIPPED and reported loudly — never guessed, never
     fuzzy-matched. (This is the load-bearing rule: a sloppy copy from the
     reviewer must not land in the wrong string.)
  2. `replacement` must preserve every placeholder, id, URL, path, number,
     symbol, link hash and line count the English source requires. A
     correction that breaks structure is rejected, not applied.
  3. Keys must exist in en.json. Unknown keys are rejected.
  4. `_meta` is never touched: no `verified` changes, no provenance changes.
     Corrections change string values only.
  5. Key order and file formatting (indent=2, ensure_ascii=False, trailing
     newline) are preserved exactly.

Without --apply this is a dry run: it reports what WOULD change and every
skip/reject with its reason, and writes nothing. With --apply it writes the
dicts and prints the same report.

Exit 0 = all corrections applied (or dry run clean). Exit 1 = at least one
skip or reject. Stdlib only.
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCALES_DIR = os.path.join(HERE, "..", "vanilla", "locales")

PLACEHOLDER_RE = re.compile(r"%\([^)]+\)s")
PATH_RE = re.compile(r"\b[\w-]+\.(?:js|py|json|html|css)\b")
URL_RE = re.compile(r"(?:https?://|wss?://|#/)[^\s)\]]+")
OPNUM_RE = re.compile(r"\bop-\d+\b")


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


def load(code):
    with io.open(os.path.join(LOCALES_DIR, code + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


def structure_of(text):
    """The structural fingerprint a replacement must preserve."""
    return (
        sorted(PLACEHOLDER_RE.findall(text)),
        sorted(PATH_RE.findall(text)),
        sorted(URL_RE.findall(text)),
        sorted(OPNUM_RE.findall(text)),
        sorted(re.findall(r"\]\(([^)]+)\)", text)),
        text.count("\n"),
    )


def main(argv):
    if len(argv) < 2 or len(argv) > 3:
        print(__doc__)
        return 2
    apply = (len(argv) == 3 and argv[2] == "--apply")
    with io.open(argv[1], encoding="utf-8") as fh:
        answers = json.load(fh)

    en = flat(load("en"))
    applied, skipped, rejected = [], [], []

    # Stage everything in memory first; write only at the end.
    staged = {}
    for lang in sorted(answers):
        if lang == "en":
            rejected.append((lang, "*", "refusing to touch the English master"))
            continue
        try:
            staged[lang] = load(lang)
        except (OSError, ValueError):
            rejected.append((lang, "*", "no such locale dict"))
            continue
        loc = flat(staged[lang])
        for key in sorted(answers[lang]):
            entry = answers[lang][key]
            if not isinstance(entry, dict) or "original" not in entry or "replacement" not in entry:
                rejected.append((lang, key, "entry is not {original, replacement}"))
                continue
            if key not in en:
                rejected.append((lang, key, "unknown key (not in en.json)"))
                continue
            current = loc.get(key)
            if current is None:
                rejected.append((lang, key, "key missing from dict"))
                continue
            if current != entry["original"]:
                skipped.append((lang, key,
                                "original does not match byte-for-byte "
                                "(dict has %r)" % current[:60]))
                continue
            new = entry["replacement"]
            if not isinstance(new, str) or not new.strip():
                rejected.append((lang, key, "replacement is empty"))
                continue
            if structure_of(en[key]) != structure_of(new):
                # The replacement must carry the ENGLISH source's structure,
                # not merely the old value's: a correction that drops a
                # placeholder the source requires is a bug, not a fix.
                rejected.append((lang, key,
                                 "replacement breaks required structure "
                                 "(placeholders/paths/urls/hashes/lines differ from en)"))
                continue
            # Write into the nested position, preserving order.
            node = staged[lang]
            parts = key.split(".")
            for p in parts[:-1]:
                node = node[p]
            node[parts[-1]] = new
            applied.append((lang, key))

    print("review answers: %d applied, %d skipped, %d rejected%s"
          % (len(applied), len(skipped), len(rejected),
             " (DRY RUN — nothing written)" if not apply else ""))
    for lang, key in applied:
        print("  APPLIED %s:%s" % (lang, key))
    for lang, key, why in skipped:
        print("  SKIPPED %s:%s — %s" % (lang, key, why))
    for lang, key, why in rejected:
        print("  REJECTED %s:%s — %s" % (lang, key, why))

    if apply and applied:
        for lang in sorted({a[0] for a in applied}):
            path = os.path.join(LOCALES_DIR, lang + ".json")
            with io.open(path, "w", encoding="utf-8") as fh:
                json.dump(staged[lang], fh, ensure_ascii=False, indent=2)
                fh.write("\n")
        print("wrote %d dict(s)" % len({a[0] for a in applied}))
    return 1 if (skipped or rejected) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
