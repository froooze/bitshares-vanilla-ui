# Machine-Filled Translations, Honestly Labeled — Design

Date: 2026-10-12. Status: approved by owner (trust model, surface
tiers, badge-not-banner, glossary + limitations page, GitHub-issues
destination, per-language confidence call, es-first pilot all confirmed
in brainstorm).
Scope: replace the binary translated/untranslated model in
`vanilla/locales/*.json` with a three-state provenance model; add the
in-app honesty surfaces that make machine text trustworthy; fill the
`es` locale to full coverage as the pilot; extend the i18n gates to
enforce the new model. Crowdin is explicitly **not** in scope — the
correction path is this repo's GitHub issues.

## 1. Goal

Principle #10 demands every locale be complete and audited. No human
translator is available in this loop, and the honest alternative —
leaving 8,786 strings as English stubs — is a gate on users. So fill
them, and make the fill's provenance **visible at every point where a
wrong reading could cost a user money**.

The old model had exactly two states, and this project already learned
what that costs: a value equal to English could be claimed as
"translated" and nobody could tell (8,098 such false claims were removed
in `89d90cc`; every locale carried 750-930 of them). The fix is not
another allowlist. It is a third state that cannot lie:

- **verified** — a human read it and signed off.
- **machine** — filled by the agent, never reviewed.
- **stub** — honestly English (still exists; nothing forces a fill).

A dict may only claim what it can prove, and the app must show the user
which of the three it is looking at. English must always be one tap
away. Nothing in this design asks the user to trust a label file; it
asks them to read a badge.

## 2. Decisions (from brainstorm, all owner-confirmed)

- **Fill everything, warn everywhere.** No string is left as a stub
  merely because it is dangerous; dangerous strings get *more* honesty
  (dual-line), not less.
- **Two risk tiers, because the danger is not uniform.** (a)
  *Surface-driven*: anything rendered inside `ConfirmDialog.show` is
  dual-line automatically — that is the signing path, and it is one
  code path shared by all 78 operations, so a new op cannot forget to
  opt in. Plus the standalone gates (unlock, backup/restore, vesting,
  worker/proposal, account creation). (b) *Key-driven*: an explicit,
  auditable list for high-risk strings rendered outside dialogs.
- **High-risk rule (mechanical, no judgement calls):** a key is
  high-risk iff its top-level section is in `HIGH_RISK_SECTIONS`
  **or** its *English* value matches `DANGER_RE`, **and** its English
  value is ≤120 characters. The length bound exists because long help
  prose renders as two unreadable paragraphs; those are covered by the
  page-level warning instead.

  ```js
  var HIGH_RISK_SECTIONS = {
    unlockconfirm: 1, auth: 1, createaccount: 1, createworker: 1,
    vesting: 1, proposal: 1, proposals_ticket: 1, confirm: 1,
    ticket: 1, tickets: 1, htlc: 1, transfer: 1, credit: 1,
    samet: 1, wallet: 1, security: 1, backup: 1, debit: 1
  };
  var DANGER_RE = /\b(sign|send|irreversib|permanently|unrecover|password|
    private key|brainkey|backup|scam|never share|withdraw|delegate|vesting|
    memo)\b/i;
  var MAX_RISK_LEN = 120;
  ```

  The regex runs against the **English** value only — matching against
  a translation would make the rule drift per locale. Sections are
  matched on the top-level segment, so `transfer.fee_note` is caught by
  section and `account.op_vesting_withdraw` by the word rule.
- **GitHub issues, no Crowdin.** The warning's "help improve" link
  targets `https://github.com/litepresence/bitshares-vanilla-ui/issues/new?labels=translation`.
  GitHub ignores unknown labels in that parameter, so the link works
  before the label exists; the owner creates the label once. No
  external service, nothing to configure, nothing to break.
- **es first.** Pilot one locale end-to-end before spending the other
  10 locales' strings. Success is concrete: `validate_translations.py
  es` green for the first time ever, every gate green, and the honest
  surfaces screenshotted.

## 3. Data model — `_meta` version 2

`en.json` stays version 1 (it is the master; there is nothing to
verify). Non-English dicts move to:

```json
"_meta": {
  "version": 2,
  "provenance": "machine",
  "coverage": ["<every en key>"],
  "verified": [],
  "high_risk": ["<keys needing dual-line>"]
}
```

- `provenance`: file-level review state — `"machine"` until a human has
  reviewed the dict, `"human"` once they have. Drives the shell badge.
- `coverage`: replaces v1 `translated` with honest meaning — "this dict
  has a value for every key", which is a coverage statement, not a
  quality claim. (v1 conflated the two; that conflation is the bug.)
- `verified`: human-signed-off keys, starts empty, grows as people
  review. A key in `verified` renders without the asterisk.
- `high_risk`: the dual-line list from §2, enumerated once in the
  module that owns it (single source of truth for the views, the
  glossary check, and the tests).

**Compatibility:** `i18n.js#allowlisted` reads `coverage` when
`version === 2` and `translated` otherwise, so `en.json` and any
surviving v1 dict keep working. With a full `coverage` the v2 gate is a
pass-through, which is correct: in v2 there are no stub keys, because
every key has a value.

## 4. The honesty surfaces

### 4.1 Dual-line text (`RiskText`)

One shared module owns the widget; no view hand-rolls it (§7 rule 9).

```
<div class="i18n-risk">
  <span class="i18n-risk-native">Texto traducido</span>
  <button class="i18n-risk-star" aria-expanded="false"
          aria-controls="…-en">*</button>
  <div class="i18n-risk-en" id="…-en" hidden>English reference</div>
</div>
```

The `*` is a real focusable `<button>` with `aria-expanded`, 44px touch
target — tap reveals the English line. No `title=`-only affordance and
nothing hover-dependent (principle #7). The button also links back to
the limitations article, so the asterisk is a route to the caveat, not
just a disclosure. Keys in `_meta.verified` render native-only, no `*`.

### 4.2 Where it mounts

- `ConfirmDialog.show` renders title, named rows, and fee lines through
  `RiskText` — this covers all 78 operations at once.
- The standalone unlock / backup-restore / vesting / worker-proposal /
  create-account surfaces use the same module for their own keys.
- `high_risk` keys rendered anywhere else are picked up by the same
  helper, so the list is honoured without each view knowing about it.

### 4.3 Shell badge (not a nag bar)

Mirrors the repo's existing extension-badge precedent (`docs/vanilla-ui-dialog.md`
§2, "badge renders only when protected… in-browser users pay zero
pixels", 44px target, no hover, keyed i18n):

- Renders **only** when the active locale has `provenance === "machine"`.
  English users and fully-reviewed locales pay zero pixels.
- Collapsed: a compact `i18n` badge in the header. Tap expands a
  one-line explanation with two links — *Details* (limitations article)
  and *Help improve* (GitHub issues).
- It cannot be lost by accident: expanding persists for the session, and
  collapsing is an explicit tap. It also never covers page content or
  blocks the nav; it occupies one header slot.
- `aria-live="polite"` on the expanded text so a screen reader announces
  the change.

### 4.4 Confidence and the limitations page

New help article "Translation limitations and how to help", reachable
from the badge **and** listed in the sitemap (AGENTS.md rule 10 — a page
reachable only from a banner is not done). It states:

- What "machine" means and that English is always one tap away.
- Per-language confidence, honest and unflattering where warranted:
  **es, fr, de, it, pt — high**; **ru, zh, ja, ko — good**; **hi, tr —
  moderate, please verify**. The owner's own instruction was to express
  a real sense of confidence per language, and these are my actual
  assessments; hi and tr are flagged because that is where my fluency is
  weakest and where a silent error is most likely.
- How to correct one string (open an issue with the key and the
  suggested wording), and that corrections are the only way
  `provenance` flips to `"human"`.

## 5. Glossary (the external-audit surface)

`docs/i18n-glossary/<code>.md`, one per language, from a shared canonical
BitShares term list: witness, committee, worker, proxy, brainkey,
vesting, HTLC, swap, slate, liquidity pool, credit offer, ticket,
proposal, precision, share, balance, fee, orderbook, limit order, and
the market/explorer nouns. Each row: English term, the locale's chosen
term, and a note on why.

Generation is **glossary-constrained** — one term per concept, reused
everywhere it appears — so an external audit (stronger LLM or human) can
correct a term once and the fix propagates. This is the artifact the
owner hands to other models; it is documentation, not runtime, and
deleting it breaks nothing.

## 6. Pilot: es, 688 stubs → 3921

Measured from `es.json` as of `89d90cc`:

| bucket | count | treatment |
|---|---|---|
| high-risk, ≤120 chars | **69** | dual-line + glossary + `*` |
| high-risk, >120 chars (help prose) | **8** | page-level warning only |
| ordinary labels/prose | **611** | machine fill, badge covers it |

Longest high-risk string is 98 characters, so every dual-line renders as
two short lines, never a wall of text.

Per-string rules for the fill, in order of precedence:
1. Placeholders (`%(name)s`), object IDs (`1.2.x`), URLs, operation
   numbers, asset symbols and theme/network ids stay byte-verbatim.
2. Glossary terms win over ad-hoc wording, every occurrence.
3. Formal/informal register matched per locale (Spanish wallet UIs are
   informal-tú; German formal-Sie; Japanese polite).
4. Numeric and money strings keep their digits and punctuation
   conventions per locale (Spanish decimal comma) **only** where it is a
   rendered sentence — the numbers themselves come from `Format`, never
   from the locale file.
5. A value that would be identical to English stays English and is
   recorded as a stub rather than faked — loanwords ("DEX", "HTLC") are
   correct in Spanish too.

## 7. Gates (both extended, both must be green)

`check_i18n.py` v2 rules:
- `version`/`provenance`/`coverage`/`verified`/`high_risk` present and
  well-formed; `coverage` == the en key set exactly; `verified ⊆
  coverage`; `high_risk ⊆ coverage`.
- Every `verified` key must **differ** from en (a human verified it, so
  an English value is either a mistake or should not be claimed).
- **Identical-to-en values are reported as a review list, not a
  failure** — in v2 a machine string may legitimately coincide with
  English, so this becomes a "needs a human look" note instead of the
  v1 hard failure.
- No locale may regress to claiming unverifiable coverage: a v1 dict
  that claims a key identical to en still fails. The old lie stays
  fatal.
- `en.json` is exempt (v1 master).

`validate_translations.py` v2 rules: checks 1-5 unchanged; check 6
accepts the v2 `_meta` shape. After the pilot, `es` passes all six for
the first time.

New tests (stdlib-only, matching the repo's tooling style):
- high-risk enumeration matches the rule (no hand-edit drift);
- dual-line renders on every `ConfirmDialog` row, and the `*` toggles
  the English line;
- badge hidden for `en`, shown for a machine locale, hidden when
  `provenance === "human"`;
- limitations article is reachable **and** present in the sitemap;
- glossary covers every high-risk key's terms.

## 8. Verification before "done"

1. `python3 tooling/check_i18n.py` — green, 12 dicts, call sites drift-free.
2. `python3 tooling/validate_translations.py es` — **green (first ever)**.
3. `bash tooling/check_types.sh` — zero emit, no new `any` leakage.
4. `python3 tooling/check_rot.py` — pass (no runtime deps introduced).
5. New/updated tooling tests green; full existing suite re-run.
6. Browser probe (`tooling/visual/`) capturing: es page with badge
   expanded, a `ConfirmDialog` with dual-line rows and the `*` revealed,
   and the limitations page — in all three themes, at 360px and desktop.
7. §4.5 anti-rot answers: (a) plain JSON/CSS/DOM/ARIA, no new platform
   surface, runs in any contemporary browser indefinitely; (b) new
   dependency: **none** — the GitHub URL is inert link data, the
   glossary is documentation; (c) smallest removable subset: the
   glossary docs and the confidence table can be deleted with zero code
   change; the badge is one module.

## 9. Out of scope, and the honest limits

- **No Crowdin, no external service, no build step.** The doctrine holds.
- **Not a substitute for translation.** This gets the strings in front
  of users with their provenance attached; it does not make them good.
  A fluent-but-wrong security phrase is the failure mode no labeling
  scheme can engineer away — which is exactly why the dual-line, the
  asterisk, the glossary, and the external audit exist. The owner has
  accepted this and will have the glossary audited by stronger models.
- **Scaling to the other 10 locales is a separate pass**, only after
  the es pilot is reviewed. Each gets the same pipeline; each gets its
  own glossary and confidence line. Budget ~740-930 strings per locale.
- **`provenance: "human"`** is not something this change can grant. It
  arrives when people have actually reviewed the strings, and the gate
  refuses to let a machine set it.
