#!/usr/bin/env python3
"""Mutation harness for tooling/i18n-v2-meta-test.js.

A test that cannot fail is not a test. This applies each mutation to the
shipped gates, runs the test, records RED/GREEN, and restores the file
byte-exactly (sha256 verified before and after every mutation, so a crashed
run can never leave the tree dirty).

Usage: python3 tooling/mutation-i18n-v2-gate.py   (exit 1 if any mutation stays green)

Mutations (each one a realistic defect, not a random byte flip):
  M1 human/empty contradiction dropped (check_i18n) — provenance becomes a
     self-declared label again: the cheapest way to silence the
     machine-translated warning, which is the one lie the v2 model was built
     to make impossible.
  M2 human/empty contradiction dropped (validate_translations) — same defect
     in the pre-merge gate, so the two gates would disagree about one dict.
  M3 verified-must-differ dropped (check_i18n) — a verified key carrying the
     English string passes again: the trust claim is unenforceable.
  M4 --fix-meta demotes v2 to v1 — the gate that enforces the model silently
     rewrites a dict into the shape that cannot express it.
  M5 note promoted to failure — identical-to-en values go back to fatal for
     unverified keys, which would make every machine-filled locale
     unfalsifiable (and is the exact regression case 10 guards).
  M6 v1 lie re-allowed (validate_translations) — a v1 dict can claim an
     English-identical key again, i.e. the 8,098-claim rot.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST = os.path.join("tooling", "i18n-v2-meta-test.js")
CHECK = os.path.join("tooling", "check_i18n.py")
VALIDATE = os.path.join("tooling", "validate_translations.py")

MUTATIONS = [
    ("M1 human/empty contradiction dropped (check_i18n)", CHECK,
     """        if provenance == "human" and not verified:
            problems.append('%s _meta.provenance says human but verified is empty '
                            "— a human review that signed off nothing is a "
                            "contradiction; the dict is machine-filled, so it "
                            'must say machine' % code)
""",
     "        # MUTANT: contradiction rule removed\n"),
    ("M2 human/empty contradiction dropped (validate)", VALIDATE,
     """    if provenance == "human" and (verified is None or not verified):
        problems.append(
            '[6 _meta] provenance "human" requires at least one verified key: '
            "a human review that signed off nothing is a contradiction — the "
            'dict is machine-filled, so it must say "machine"'
        )
""",
     "    # MUTANT: contradiction rule removed\n"),
    ("M3 verified-must-differ dropped (check_i18n)", CHECK,
     """        for k in sorted(set(verified) - IDENTIFIERS):
            if flat.get(k) == en_flat.get(k):
                problems.append("%s _meta.verified %s is identical to en — a human "
                                "signed it off, so an English value means the "
                                "claim is wrong" % (code, k))
                break
""",
     "        # MUTANT: verified-must-differ removed\n"),
    ("M4 --fix-meta demotes v2 to v1", VALIDATE,
     "    if old.get(\"version\") == 2:",
     "    if False:  # MUTANT: v2 dicts silently demoted"),
    ("M5 note promoted to failure", CHECK,
     """        if same:
            notes.append("%s: %d machine value(s) equal en (review candidates)"
                         % (code, same))
""",
     """        if same:
            problems.append("%s: %d value(s) equal en" % (code, same))  # MUTANT
"""),
    ("M6 v1 lie re-allowed (validate)", VALIDATE,
     """            verbatim = must_equal_en_keys(en_flat)
            same = [t for t in sorted(set(translated) - verbatim)
                    if flat.get(t) == en_flat.get(t)]""",
     "            same = []  # MUTANT: v1 lie re-allowed"),
]


def sha(path):
    with open(os.path.join(ROOT, path), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run_test():
    p = subprocess.run(["node", os.path.join(ROOT, TEST)],
                       cwd=ROOT, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def main():
    paths = []
    for name, path, _, _ in MUTATIONS:
        if path not in paths:
            paths.append(path)

    tmpdir = tempfile.mkdtemp(prefix="i18n-v2-mutants-")
    backups = {}
    for path in paths:
        dest = os.path.join(tmpdir, path.replace(os.sep, "_"))
        shutil.copy2(os.path.join(ROOT, path), dest)
        backups[path] = (sha(path), dest)
    before = {path: sig for path, (sig, _) in backups.items()}

    stale = []
    try:
        for name, path, old, new in MUTATIONS:
            full = os.path.join(ROOT, path)
            with open(full, encoding="utf-8") as f:
                src = f.read()
            if src.count(old) != 1:
                print("%-52s SKIPPED — anchor appears %d times (test evolved; "
                      "update this harness)" % (name, src.count(old)))
                stale.append(name)
                continue
            backup = backups[path][1]
            shutil.copy2(backup, full)
            with open(full, "w", encoding="utf-8", newline="") as f:
                f.write(src.replace(old, new))
            code, out = run_test()
            lines = out.splitlines()
            marker = [ln for ln in lines if "AssertionError" in ln]
            print("%-52s %s  %s" % (name, "RED  " if code != 0 else "GREEN",
                                    marker[-1].strip() if marker
                                    else (lines[-1] if lines else "")))
            shutil.copy2(backup, full)
            if sha(path) != before[path]:
                print("%-52s RESTORE FAILED — copy %s over %s"
                      % (name, backup, path))
                return 1
    finally:
        for path, (_, full) in backups.items():
            shutil.copy2(full, os.path.join(ROOT, path))
        shutil.rmtree(tmpdir, ignore_errors=True)

    for path, sig in before.items():
        if sha(path) != sig:
            print("FINAL RESTORE MISMATCH: %s" % path)
            return 1
    print("restored: %d file(s) byte-identical (sha256 verified): %s"
          % (len(before), ", ".join(paths)))
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
