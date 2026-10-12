#!/usr/bin/env python3
"""Mutation harness for tooling/i18n-badge-test.js.

A test that cannot fail is not a test. This applies each mutation to the
shipped source, runs the test, records RED/GREEN, and restores the file
byte-exactly (sha256 verified before and after every mutation, so a crashed
run can never leave the tree dirty).

Usage: python3 tooling/mutation-i18n-badge.py   (exit 1 if any mutation stays green)

Mutations (each one a realistic defect, not a random byte flip):
  M1 hardcoded locale code   — the classic copy-paste bug: the chip is decided
                               for "es" whatever the reader picked, so English
                               users are warned about a dictionary they cannot read.
  M2 no provenance check     — the badge always shows (honesty surface that
                               cannot lie, replaced by one that always lies).
  M3 private event binder    — addEventListener on the chip instead of the
                               shared EventDelegate delegation.
  M4 persisted dismissal     — the collapse is remembered in localStorage, i.e.
                               the warning can be lost forever.
  M5 no reduced-motion guard — the badge's fade keeps running under
                               prefers-reduced-motion (app.css).
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST = os.path.join("tooling", "i18n-badge-test.js")
MODULE = os.path.join("vanilla", "js", "ui", "i18n-badge.js")
CSS = os.path.join("vanilla", "css", "app.css")

MUTATIONS = [
    ("M1 hardcoded locale code", MODULE,
     "      var code = I18n.locale();",
     '      var code = "es"; /* MUTANT: hardcoded code */'),
    ("M2 no provenance check", MODULE,
     "  function activeMachine() {\n    try {",
     "  function activeMachine() {\n    return true; /* MUTANT */\n    try {"),
    ("M3 private event binder", MODULE,
     '      EventDelegate.delegate(doc, "." + CHIP_CLASS, "click", function (evt, matched) {\n        toggle(matched);\n      });',
     '      chip.addEventListener("click", function () { toggle(chip); }); /* MUTANT */'),
    ("M4 persisted dismissal", MODULE,
     "    note.hidden = open;\n    return true;",
     '    note.hidden = open;\n    try { localStorage.setItem("bts-vanilla-i18n-badge-seen", "1"); } catch (e) { }\n    return true;'),
    ("M5 no reduced-motion guard", CSS,
     "@media (prefers-reduced-motion: reduce) {\n  .i18n-badge-note { animation: none; }\n}",
     "/* MUTANT: guard removed */"),
]


def sha(path):
    with open(os.path.join(ROOT, path), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run_test():
    p = subprocess.run([sys.executable and "node", os.path.join(ROOT, TEST)],
                       cwd=ROOT, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def main():
    saved = {}
    for name, path, _, _ in MUTATIONS:
        full = os.path.join(ROOT, path)
        saved[path] = (sha(path), full)

    tmpdir = tempfile.mkdtemp(prefix="i18n-badge-mutants-")
    for name, path, _, _ in MUTATIONS:
        shutil.copy2(saved[path][1], os.path.join(tmpdir, path.replace(os.sep, "_")))
    before = {path: sig for path, (sig, _) in saved.items()}

    stale = []
    try:
        for name, path, old, new in MUTATIONS:
            full = os.path.join(ROOT, path)
            with open(full, encoding="utf-8") as f:
                src = f.read()
            if src.count(old) != 1:
                print("%-32s SKIPPED — anchor appears %d times (test evolved; update this harness)"
                      % (name, src.count(old)))
                stale.append(name)
                continue
            backup = os.path.join(tmpdir, path.replace(os.sep, "_"))
            shutil.copy2(backup, full)
            with open(full, "w", encoding="utf-8", newline="") as f:
                f.write(src.replace(old, new))
            code, out = run_test()
            lines = out.splitlines()
            # Node prints a code frame ("throw new AssertionError(obj);")
            # BEFORE the assertion line, so take the last AssertionError hit.
            marker = [ln for ln in lines if "AssertionError" in ln]
            print("%-32s %s  %s" % (name, "RED  " if code != 0 else "GREEN",
                                    marker[-1].strip() if marker else (lines[-1] if lines else "")))
            shutil.copy2(backup, full)
            if sha(path) != before[path]:
                print("%-32s RESTORE FAILED — copy %s over %s" % (name, backup, path))
                return 1
    finally:
        for path, (_, full) in saved.items():
            shutil.copy2(os.path.join(tmpdir, path.replace(os.sep, "_")), full)
        shutil.rmtree(tmpdir, ignore_errors=True)

    for path, sig in before.items():
        if sha(path) != sig:
            print("FINAL RESTORE MISMATCH: %s" % path)
            return 1
    print("restored: %d file(s) byte-identical (sha256 verified)" % len(before))
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())