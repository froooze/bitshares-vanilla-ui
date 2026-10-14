#!/usr/bin/env python3
"""Build vanilla/locales/REVIEW.md — the single-file review bundle.

Concatenates all 11 non-English locale dicts against the English master so a
review agent that only accepts one file can audit every machine-filled string.
Only keys whose value DIFFERS from English are expanded (those are the
translations to review); keys deliberately left English are listed compactly
per locale so the reviewer can spot-check them without paying for 42k repeats.

Run from the repo root:  python3 tooling/build_locale_review.py
Output: vanilla/locales/REVIEW.md (regenerate it whenever a dict changes).
Stdlib only. Reads the dicts, writes nothing else.
"""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LOCALES_DIR = os.path.join(HERE, "..", "vanilla", "locales")
OUT = os.path.join(LOCALES_DIR, "REVIEW.md")

LANG = {
    "de": ("German", "formal Sie, standard for German financial software"),
    "es": ("Spanish", "informal tú, standard for Spanish wallet UIs"),
    "fr": ("French", "formal vous, standard for French financial software"),
    "it": ("Italian", "formal standard Italian UI voice"),
    "ja": ("Japanese", "polite です/ます; 「」 for button-like labels, … for loaders, 和欧間 space around Latin runs"),
    "ko": ("Korean", "polite split: ~습니다 statements, ~십시오 instructions, bare nouns for labels; glued middle dots; dual placeholder particles %(name)s은(는) / …을(를) / …(으)로"),
    "pt": ("Portuguese (Brazilian)", "informal você; carteira, painel, cota, nó, emissor, acordo spellings"),
    "ru": ("Russian", "formal вы; watch postposition-equivalents and case agreement"),
    "tr": ("Turkish (Türkiye)", "formal siz; WATCH vowel harmony on every suffix and case stacking — a dropped suffix changes meaning, not just formality"),
    "zh": ("Chinese (Simplified)", "no spaces between words; watch terseness dropping a qualifier — an amount, a direction, an irreversibility, a permission"),
    "hi": ("Hindi", "formal आप; WATCH postpositions में/से/को — a dropped postposition loses the meaning with it"),
}


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


PROMPT = """# REVIEW PROMPT — read this first, then review the sections below

## What you are looking at

This file concatenates all 11 non-English locale dictionaries of a
**BitShares cryptocurrency wallet** (a web app where users hold real funds,
sign transactions, and manage cryptographic keys). Each section holds ONE
locale. Inside a section, every translated key is shown as a triple:
the dotted key, the `EN:` English source string, and the `<CODE>:` current
translation. After the triples, a compact `IDENTICAL:` list names the keys
deliberately left in English.

**Every non-English string in this file was written by a machine and has
never been reviewed by a human.** Your job is to find where the machine is
wrong. A fluent, confident, grammatical translation that says the wrong
thing is the failure mode — it is worse than a clumsy one, because a user
will trust it.

## Why this matters (the risks)

1. **Money and signing strings.** Keys under `transfer`, `auth`,
   `unlockconfirm`, `vesting`, `createworker`, `createaccount`, `htlc`,
   `samet`, `credit`, `debit`, `ticket`, `vote`, `txbuilder`, `confirm`,
   `approval`, `proposals_ticket`, `wallet`, `gateway` render inside
   **signing confirmation dialogs**, each beside an English reference line.
   If your correction changes what the user believes they are authorizing —
   an amount, a destination, an irreversible action, a permission — say so
   explicitly. An inverted comparison ("greater than" rendered as "less
   than") tells the user the opposite of the truth.
2. **Placeholders, ids, code and structure MUST survive byte-verbatim.**
   `%(name)s` placeholders (same multiset, same spelling), object ids like
   `1.2.x`, URLs, file paths (`tx.js`), operation numbers (`op-34`), asset
   symbols (`BTS`, `USD`), markdown link targets (`#/assets/feed`), and line
   counts of multi-line values. A translation that breaks any of these is a
   bug, not a translation — flag it even if the prose is beautiful.
3. **Some English is deliberate.** The `IDENTICAL:` lists are loanwords the
   target language's crypto UIs actually use (`DEX`, `HTLC`, `Swap`,
   `Proxy`, `Memo`), indicator tickers (`BB`, `EMA`, `PSAR`, `SMA`),
   brands, pinned network/theme ids, and data glue. Do NOT invent a
   translation for these to "complete" the file. If you believe one of them
   SHOULD have been translated, say which key and why — that is a finding,
   not a correction.
4. **Register must match the locale's stated convention** (listed per
   section). A correct word in the wrong register reads as untrustworthy in
   financial software.
5. **Do not touch metadata.** There is no `_meta` in this file and there
   must be none in your answer. You are not marking anything verified;
   a separate human process does that. Your corrections change string
   values only.
6. **Loanword disputes.** Where a locale splits on one concept (two spellings
   for one English term), prefer the form the file already uses most, and say
   which keys use the minority form. One term, one spelling — that is what
   makes a future correction propagate instead of fork.

## How to answer

**Respond in JSON only, no prose, no markdown fences.** Shape:

```json
{
  "<lang>": {
    "<dotted.key>": {
      "original": "<the exact current string, byte-for-byte>",
      "replacement": "<your corrected string>"
    }
  }
}
```

Rules for the answer object:

- Include **only the keys you are correcting**. Do not repeat the 42,000
  keys you approve of. An empty object `{}` for a language means you reviewed
  it and found nothing — that is a valid and useful answer.
- `original` must equal the current string **byte-for-byte**, copied exactly
  (placeholders, punctuation, trailing spaces included). It is how the fix
  is applied mechanically; a mismatch means the fix is skipped, not guessed.
- `replacement` must preserve every placeholder, id, URL, path, number,
  symbol, link hash and line break the original's English source requires.
- `"<lang>"` is the two-letter code from the section header (`hi`, `tr`,
  ...), never the language name.
- If you find a key that was wrongly left English (in an `IDENTICAL:` list
  but clearly needing translation), include it with the English string as
  `original` and your translation as `replacement`.
- If you find a structural break (placeholder dropped, hash mangled, line
  count changed) in a string you otherwise approve of, include it with a
  `replacement` that restores the structure. Structure beats style.

You are the last reader before these strings meet users who trust them with
money. Be strict, be specific, and prefer flagging a doubt over silently
accepting it.

---
"""


def main():
    en = flat(load("en"))
    en_keys = sorted(en)
    parts = [PROMPT]
    parts.append("# Coverage — what is and is not in this file\n")
    parts.append("`en.json` is the master (%d keys). Per locale: translated keys are "
                 "expanded below; identical keys are listed compactly.\n" % len(en_keys))
    for code in ["de", "es", "fr", "it", "ja", "ko", "pt", "ru", "tr", "zh", "hi"]:
        name, register = LANG[code]
        loc = flat(load(code))
        diff = [(k, en[k], loc[k]) for k in en_keys if loc.get(k) != en[k]]
        same = [k for k in en_keys if loc.get(k) == en[k]]
        parts.append("## %s — %s (%d translated, %d deliberately English)\n" % (code, name, len(diff), len(same)))
        parts.append("Register: %s.\n" % register)
        for k, e, v in diff:
            parts.append("### %s\nEN: %s\n%s: %s\n" % (k, e, code.upper(), v))
        parts.append("IDENTICAL (deliberately English — loanwords, tickers, brands, "
                     "pinned ids, data glue; challenge individual keys per the prompt, "
                     "do not translate the list):\n%s\n" % ", ".join(same))
    with io.open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))
    print("wrote %s (%d bytes)" % (OUT, os.path.getsize(OUT)))


if __name__ == "__main__":
    main()
