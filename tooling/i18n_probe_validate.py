#!/usr/bin/env python3
"""Score a model's answers to the i18n probe against the structural rules.

Usage:
    python3 tooling/i18n_probe_validate.py hi  tooling/probe_runs/hi-model-a.json
    python3 tooling/i18n_probe_validate.py tr  tooling/probe_runs/tr-model-a.json

This checks what can be checked MECHANICALLY, and deliberately nothing more:

  1. every item in the fixture is answered, and nothing extra is invented
  2. %(name)s placeholder multiset is identical to the English source
  3. object ids, URLs and file paths survive byte-verbatim
  4. multi-line values keep their line count
  5. markdown link HASHES survive byte-verbatim (labels are translated)
  6. script contamination: hi must be Devanagari, tr must be Latin - a run of
     the wrong script is almost always an untranslated leftover or a model
     answering in the wrong language
  7. Latin tokens are limited to the declared loanword allowlist

A PASS here does NOT mean the translation is good. Meaning, register, aspect
and morphology are exactly what this script cannot see - that is what the
side-by-side comparison between two models is for. This script exists only to
stop a model from quietly dropping a placeholder or mangling a hash and having
that read as fluency.

Exit 0 = all structural checks pass. Exit 1 = one or more violations.
Stdlib only; reads the fixture and the answers file, writes nothing.
"""
import json
import re
import sys
import unicodedata

HERE = "tooling/i18n_probe_fixture.json"
PLACEHOLDER_RE = re.compile(r"%\([^)]+\)s")
PATH_RE = re.compile(r"\b[\w-]+\.(?:js|py|json|html|css)\b")
URL_RE = re.compile(r"(?:https?://|wss?://|#/)[^\s)\]]+")
OPNUM_RE = re.compile(r"\bop-\d+\b")

DEVANAGARI = re.compile(r"[ऀ-ॿ]")
# Unicode-aware word runs. A plain [A-Za-z] class silently shreds Turkish
# ("parolanızı" -> "parolan", "z", "zdan") because ı/ş/ğ/ü/ö/ç are not ASCII
# letters, which produced 100+ bogus violations on a correct Turkish answer.
WORD_RE = re.compile(r"[^\W\d_]+(?:[.\-][^\W\d_]+)*", re.UNICODE)
CYRILLIC = re.compile(r"[Ѐ-ӿ]")
CJK = re.compile(r"[一-鿿぀-ヿ가-힯]")


def is_latin_script(token):
    """True when every letter in the token belongs to the Latin script.

    Uses Unicode character names so Turkish, Vietnamese and Polish letters
    count as Latin, while Devanagari/Cyrillic/CJK tokens do not.
    """
    for ch in token:
        if ch in ".-":
            continue
        try:
            if "LATIN" not in unicodedata.name(ch):
                return False
        except ValueError:
            return False
    return True


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def script_profile(text):
    """Count script families present, ignoring punctuation/whitespace/digits."""
    counts = {"deva": 0, "latin": 0, "cyr": 0, "cjk": 0}
    for ch in text:
        if DEVANAGARI.match(ch):
            counts["deva"] += 1
        elif CYRILLIC.match(ch):
            counts["cyr"] += 1
        elif CJK.match(ch):
            counts["cjk"] += 1
        elif ch.isalpha() and ord(ch) < 128:
            counts["latin"] += 1
    return counts


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    lang, answers_path = argv[1], argv[2]
    if lang not in ("hi", "tr"):
        print("lang must be hi or tr")
        return 2

    fixture = load(HERE)
    answers = load(answers_path)
    items = fixture["items"]
    allowed_loan = set(fixture["loanwords_allowed"].get(lang, []))

    got = answers.get("answers", answers)
    problems = []

    expected_ids = [i["id"] for i in items]
    for extra in sorted(set(got) - set(expected_ids)):
        problems.append("[%s] invented an item not in the fixture: %s" % (lang, extra))
    for missing in sorted(set(expected_ids) - set(got)):
        problems.append("[%s] did not answer: %s" % (lang, missing))

    checked = 0
    for item in items:
        iid = item["id"]
        if iid not in got:
            continue
        checked += 1
        src, out = item["en"], got[iid]
        if not isinstance(out, str) or not out.strip():
            problems.append("[%s] %s: empty or non-string answer" % (lang, iid))
            continue

        # 2. placeholders
        if sorted(PLACEHOLDER_RE.findall(src)) != sorted(PLACEHOLDER_RE.findall(out)):
            problems.append("[%s] %s: placeholder multiset changed\n    en: %s\n    %s: %s"
                            % (lang, iid, PLACEHOLDER_RE.findall(src), lang, out))

        # 3. ids / urls / paths / op numbers survive byte-verbatim
        for label, rx in (("path", PATH_RE), ("url", URL_RE), ("op-number", OPNUM_RE)):
            s_tok, o_tok = rx.findall(src), rx.findall(out)
            missing_tok = [t for t in s_tok if t not in o_tok]
            if missing_tok:
                problems.append("[%s] %s: %s not preserved byte-verbatim: %s"
                                % (lang, iid, label, missing_tok))

        # 4. line count
        if src.count("\n") != out.count("\n"):
            problems.append("[%s] %s: line count changed (en %d, %s %d)"
                            % (lang, iid, src.count("\n"), lang, out.count("\n")))

        # 5. markdown link hashes survive
        for h in re.findall(r"\]\(([^)]+)\)", src):
            if h not in out:
                problems.append("[%s] %s: link hash %s lost" % (lang, iid, h))

        # 6. script contamination
        prof = script_profile(out)
        if lang == "hi":
            if prof["deva"] == 0:
                problems.append("[%s] %s: no Devanagari at all - answer is not Hindi\n    %s"
                                % (lang, iid, out))
            for fam in ("cyr", "cjk"):
                if prof[fam]:
                    problems.append("[%s] %s: %d unexpected %s character(s)"
                                    % (lang, iid, prof[fam], fam))
        else:
            if prof["latin"] == 0:
                problems.append("[%s] %s: no Latin script at all - answer is not Turkish\n    %s"
                                % (lang, iid, out))
            for fam in ("deva", "cyr", "cjk"):
                if prof[fam]:
                    problems.append("[%s] %s: %d unexpected %s character(s)"
                                    % (lang, iid, prof[fam], fam))

        # 7. untranslated leftovers — HINDI ONLY.
        #    Two failure modes, both classic: a wholly untranslated answer
        #    (Latin words absent from the source) and a HALF-translated one
        #    (some Devanagari, the rest still English). The first is caught
        #    by allowlist membership; the second by flagging any multi-word
        #    Latin run embedded in a string that also has Devanagari.
        #    Meaningless for Turkish, which IS Latin script.
        if lang == "hi":
            for tok in sorted(set(WORD_RE.findall(out))):
                if not is_latin_script(tok):
                    continue
                if tok in allowed_loan or tok in src:
                    continue
                problems.append("[%s] %s: undeclared Latin token %r (untranslated leftover, "
                                "or add it to loanwords_allowed if it is an intentional loanword)"
                                % (lang, iid, tok))
            if DEVANAGARI.search(out):
                for run in re.findall(r"[A-Za-z][A-Za-z0-9.\-]*(?:[ ][A-Za-z][A-Za-z0-9.\-]*)+", out):
                    leftover = [w for w in run.split()
                                if w not in allowed_loan]
                    if leftover:
                        problems.append("[%s] %s: mixed-script run %r inside an otherwise "
                                        "Hindi answer — looks HALF-translated"
                                        % (lang, iid, run))

    print("i18n probe [%s] — %d/%d items checked against %s"
          % (lang, checked, len(items), answers_path))
    if problems:
        print("FAIL — %d structural violation(s):" % len(problems))
        for p in problems:
            print("  " + p)
        print("\nReminder: passing this does NOT mean the translation reads well.")
        return 1
    print("PASS — all structural checks clean.")
    print("Reminder: this says nothing about meaning, register, aspect or "
          "morphology. Judge those by reading the side-by-side.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
