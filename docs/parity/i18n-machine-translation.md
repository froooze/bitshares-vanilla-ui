# i18n-machine-translation — honest-translation surface on signing dialogs

**Status:** complete (Task 4 + fix wave 1 + fix wave 2)
**Scope:** `vanilla/js/ui/risk-text.js` (widget), `vanilla/js/ui/confirm.js`
(shared dialog), `vanilla/js/ui/unlock-confirm.js` (shared unlock modal), and
every call site that builds a `ConfirmDialog` / `UnlockConfirm` line.
**Gate:** `tooling/check_i18n.py` gate 7 (keyed signing-dialog lines) +
`tooling/confirm-risk-test.js`, `tooling/i18n-risk-keys-test.js`,
`tooling/i18n-key-gate-test.js`, `tooling/risk-text-test.js`.

---

## 1. What this is

BitShares is global; the wallet ships 12 languages. Machine translation is
what keeps a language *present* before a human translator arrives — but a
machine-rendered string on a **signing dialog** is a different risk class than
one on a read-only page. The user is about to authorise a transaction, and a
mis-rendered "Fee", "Auto-disable" or "Collateral legs" is a silent
money-looking bug (AGENTS.md principle #6) that no amount of careful phrasing
fixes.

So the surface does one thing: **on a machine-filled locale, every keyed line
on a signing dialog carries an asterisk that discloses the English master
one tap away.** Not a translation — the reference. The user's language stays
on the line they read; the English sits behind one disclosure, collapsed by
default, with a link to the translation-limitations article on the same line.

Three properties are load-bearing:

1. **Opt-in.** `titleKey`, `rows[i][3]` (term key) and `feeTermKey` are all
   optional. A dialog with none of them renders exactly as it did before the
   widget existed. That is what keeps the 27 + 12 call sites working.
2. **Labels only, never values.** Amounts, asset symbols, object ids and
   dates are locale-independent by §3.5 and are NEVER keyed — a "disclosure"
   for `1.23456 BTS` would be noise. The widget sees static labels and
   nothing else.
3. **Key correctness is gated.** A key that does not exist, or that names a
   different string than the line shows, is *worse* than no key: the widget
   would disclose a confidently wrong English reference. Gate 7 exists for
   that reason and nothing else catches it (§5).

## 2. True migration counts

Measured on the tree as merged (fix wave 2), not carried over from an earlier
report. An earlier report's "107 keyed titles" counted the 74 **pre-existing,
unrelated** `titleKey` fields in `menu-ui.js` (burger-menu nav, paired with
`titleDefault`) and `router.js` (SEO meta, titles are plain strings) — none of
which a RiskText widget ever reads. They are excluded here and explicitly
exempted in the gate.

| Measure | Count | How it is counted |
|---|---|---|
| `ConfirmDialog.show` call sites | **27** | `grep -rn 'ConfirmDialog\.show(' vanilla/js/` minus `ui/confirm.js` |
| `UnlockConfirm.open` call sites | **12** | `grep -rn 'UnlockConfirm\.open(' vanilla/js/` minus `ui/unlock-confirm.js` |
| Distinct `titleKey` values passed | **29** | keys reaching a dialog (incl. `trade.uc_title`, added by fix wave 2) |
| Distinct `feeTermKey` values passed | **5** | `borrow.fee`, `common.fee_live`, `confirm.fee`, `trade.row_fee`, `trollbox.fee` |
| Keyed titles + fee terms gated | **60** | gate 7's `title_like` counter (includes the `cfg.titleKey = "…"` assignment form) |
| Confirm-row term key slots gated | **186** | gate 7's `row_slots` counter = **179** at the end of fix wave 1 **+ 7** added by fix wave 2's I2 migration (`trade-panels.js`) |

Fix wave 1 added **33** `titleKey` passes across **28** distinct keys
(`trade.uc_title` was the 29th, added by wave 2's I2).

## 3. Which call sites were migrated, and which were not

### Migrated (keyed)

Every static label that reaches a signing dialog through the shared builders:
`transfer-confirm.js`, `trade-cancel.js`, `market-orders.js`, `trade-panels.js`
(fix wave 2), `settings.js`, `trollbox-ui.js`, `asset-ui.js`,
`asset-manage-ui.js`, `asset-feed-ui.js`, `barter-ui.js`, `borrow-ui.js`,
`credit-ui.js`, `debit-ui.js`, `htlc-ui.js`, `instant-trade-ui.js`,
`pool-ui.js`, `prediction-flows.js`, `proposal-ui.js`, `transfer-preview.js`,
`transfer-propose.js`.

Titles: every `ConfirmDialog`/`UnlockConfirm` title that was already a
`t()` call — the unlock-and-review titles (`*.uc_title`), the confirm-action
titles (`*.confirm_*`) and `settings.confirm_remove_title`.

Row terms: **186** slots, e.g. `credit.owner` / `credit.asset` /
`credit.balance` / `credit.fee_rate` / `credit.auto_disable` /
`credit.collateral_legs` / `credit.borrowers` / `credit.fee` /
`credit.network`; `asset.confirm_*`; `borrow.account`; `htlc.*`;
`proposal.*`; `barter.*`; `transfer.*`; `trade.*`; `explorer.issuer_row`;
`settings.th_node`; `account.card_account`; `asset_ops.title`; and the help
topic keys (`help.topic_*`).

Fee terms: all 25 `feeTerm:` call sites plus the two forwarding bags
(`borrow-ui.js` `signGateLocked`, `prediction-flows.js` `signGateLockedP`),
which now carry `feeTermKey` through `UnlockConfirm.open` → `ConfirmDialog.show`.

### Skipped, with reasons

| Site | Why skipped |
|---|---|
| **Dynamic values** (every row's `dd`, the fee amount) | Locale-independent by §3.5. Keying a disclosure for `1.23456 BTS` would be noise and would put a non-translatable value through a translation-shaped API. This is the single largest deliberate exclusion. |
| **`paintConfirmSingle` / `paintConfirmScaled` term rows** (`trade-panels.js:1061+`) | These build their own `<h3>` + `<dl>` inline and never pass through `ConfirmDialog`, so `titleKey`/`rows[i][3]` do not reach a RiskText. Migrating them means adopting `ConfirmDialog` — a structural change to the trade desk's human-readable confirm, deliberately out of scope for a key-wiring task. **Documented, not done.** |
| **`ConfirmDialog`'s default labels** (`"Back"`, `"Sign & Send"`, `"Raw JSON"`, bare `"Fee"`) | Overridable fallbacks used when a caller passes nothing. Every real caller passes `t("confirm.back", …)` / `t("common.sign_send", …)`; the literals are the no-caller path and are not user-visible on a keyed dialog. |
| **`ui/confirm.js` `feeTerm` default `"Fee"`** | Same: the fallback for a caller that passes neither `feeTerm` nor `feeTermKey`. |
| **`menu-ui.js`, `router.js` `titleKey`** | Pre-existing nav/SEO tables whose keys are consumed by `t(link.titleKey, link.titleDefault)`. No widget, no dialog. Explicitly listed in `check_i18n.py`'s `NON_DIALOG_TITLEKEY_FILES` so a THIRD file pairing a hardcoded title with a key fails loudly instead of inheriting a silent exemption. |
| **`app.js`, `views/*` non-dialog `t()` strings** | The surface is the signing dialog. Page chrome was already locale-correct via gate 6 (5,131 `t()` call sites drift-free). |

## 4. Deliberate design decisions a reviewer should check

**The asterisk stays inside the `<h3>`.** It is a real
`<button type="button">` with `aria-expanded` + `aria-controls` + the 44px
touch floor (`utils/touchable.js`), mounted inside the heading, not floated to
a corner. A disclosure control belongs to the line it discloses. The cost was
a positional-button-indexing bug (C3, below) — paid in one place rather than
by moving the control somewhere less accessible.

**The wrapper is a `<span>`, not a `<div>`.** `h1`–`h6` accept phrasing
content only. `<div>` wrapper + `<div>` English panel inside an `<h3>` is an
invalid content model that browsers tolerate and assistive tech does not.
Everything in the subtree is `span`/`button`/`span`/`a`. The English line
still renders on its own line because `.i18n-risk-en` carries `display:block`
in `app.css`, which a `<span>` honours exactly as a `<div>` did.

**The semantic host is kept and the widget is nested.** `line()` builds the
`h3`/`dt` EMPTY and mounts the widget inside. Substituting RiskText for the
host would demote the dialog heading to a `span` and un-pair every `<dl>`
dt/dd — a screen-reader regression on the one dialog a user reads before
signing.

**`render()` never returns null.** `appendChild(null)` inserts the literal
text "null" into a signing dialog. On the no-document floor it returns an
empty structural stand-in instead; that is why `globals.d.ts` declares
`RiskTextLine` **structurally** rather than as `HTMLElement` — the type must
not promise an element the floor cannot produce.

## 5. Why a gate was needed (and what it checks)

It was demonstrated during fix wave 1 that repointing a call site at a
**wrong-but-existing** key, or at a **non-existent** key, left every existing
gate green:

- gate 6 (t() default vs `en.json`) is equally happy with either key;
- a missing key simply degrades the line to plain text, so nothing fails;
- RiskText's own decision is honest — it discloses whatever `I18n.enFor(key)`
  returns, which is precisely the thing that would be wrong.

So `tooling/check_i18n.py` gained **gate 7**, bracket-aware (strings, comments
and nesting respected, so a value like `Format.formatAmount(a, b)` never
splits the row it lives in):

- **7a** every `titleKey` / `feeTermKey` literal exists in `en.json`;
- **7b** every `titleKey` / `feeTermKey` with a sibling `title` / `feeTerm`
  in the same object literal names exactly the key that sibling's `t()` call
  uses — object-literal form *and* the `cfg.titleKey = "…"` assignment form;
- **7c** every 4-slot confirm row `[t("k", d), value, raw, "rk"]` has
  `k == rk`.

It is loud, not lenient: a keyed line whose sibling label is not a `t()` call
is **reported**, not skipped, unless the file is one of the two documented
non-dialog tables. "The gate could not see it" is how a wrong key reaches
production.

`tooling/i18n-key-gate-test.js` proves each half fails without its fix, by
mutating a throwaway copy of the tree (never the real one): wrong-but-existing
title key, missing title key, wrong row key, missing row key, hyphenated row
key, wrong `feeTermKey`, wrong assignment-form key — plus a negative case
(dropping a key must stay green) and a coverage assertion so a silently-empty
gate is visible.

## 6. Verification

```
node tooling/confirm-risk-test.js    # 116 — dialog wiring, C3 hooks, I4 content model
node tooling/confirm-test.js         #  39 — the pre-existing dialog contract, unchanged
node tooling/risk-text-test.js       # the widget in isolation
node tooling/i18n-risk-keys-test.js  # which keys are high-risk
node tooling/i18n-key-gate-test.js   #  25 — gate 7 fails on wrong/missing keys
node tooling/unlock-confirm-test.js  #  31 — key forwarding through the unlock modal
node tooling/credit-offer-confirm-test.js  #  35 — the op-69 signing rows
python3 tooling/check_i18n.py         # 12 dicts, 5131 t() sites, 60 + 186 keyed lines
python3 tooling/check_rot.py         # anti-rot gate (§4.5)
bash tooling/check_types.sh          # tsc --checkJs, zero emit
```

And for the v2 conversion (§7):

```
node tooling/convert_locale_meta_v2.js es   # rewrites _meta, proves values unchanged
python3 tooling/i18n_translation_census.py  # the differing/identical record, per locale
python3 tooling/validate_translations.py es # pre-merge gate, version-aware
node tooling/i18n-v2-meta-test.js           # 57 vectors: both _meta shapes enforced
```

## 7. `_meta` v2 — `es.json` converted, and what happened to its 3,233-key `translated` list

`es.json` is now `_meta` version 2. `provenance: "machine"`, `verified: []`,
`coverage` = all 3,938 `en.json` keys, `high_risk` = 1,118 keys enumerated from
`vanilla/js/i18n/risk-keys.js` (`RiskKeys.listFor` against the shipped `es.json`
and `en.json`) by `tooling/convert_locale_meta_v2.js`. No value changed: the
non-`_meta` payload hashes to `6f86daca…1be53` before and after.

### The `translated` list, and why it is not in the file any more

v1's `_meta.translated` held **3,233** keys for `es`: the keys whose Spanish
value differs from English. v2 has no such field, and nothing was lost:

- **It is exactly recomputable, and the recomputation is proven equal.** v1's
  own rule required a listed key to differ from English (`check_i18n.py`:
  "translated %s identical to en"), so
  `{k : es[k] ≠ en[k]}` IS the `translated` set — 3,233 entries, `== differs`
  came back `True` for `es` and for all nine other v1 locales on the day of
  conversion. `tooling/i18n_translation_census.py` prints the set
  (`--keys es`), its size, and a payload hash; `check_i18n.py` prints the
  complement (705 identical values) as a review note on every run.
- **A second stored copy would be rot, not a record.** The list can only
  disagree with the values it describes, and nothing but the bytes can settle
  that — which is the whole reason v2 exists.
- **The name cannot come back under v2 without reintroducing the lie.**
  `i18n.js`'s `allowlisted()` reads `coverage` on a v2 dict and `translated` on
  a v1 one (`vanilla/js/i18n.js:62`). One field name meaning "translated" in
  one shape and "covered" in the other, in the same file, is the ambiguity gate
  8 was written to remove. It would also be destroyed by
  `validate_translations.py --fix-meta`, which rewrites a v2 `_meta` as exactly
  the five v2 fields.
- **What it was honest evidence OF is now stated more honestly.** The list said
  "a human translated these 3,233". `provenance: "machine"` with `verified: []`
  says the thing that is actually true of all 3,938: nobody has read any of
  them. A list of 3,233 claims and a dict-wide "machine" are not the same
  claim, and only the second one is defensible.

The 3,233/705 split is therefore a **measurement, not a stored claim** — dated
here, recomputable on demand, and never able to rot:

```
python3 tooling/i18n_translation_census.py            # every locale, both counts
python3 tooling/i18n_translation_census.py --keys es  # the 3,233 differing keys
python3 tooling/i18n_translation_census.py --hash es  # payload sha256
```

The other ten non-English dicts stay v1 for now; when they convert, the same
rule applies to each, and the census tool prints their `translated`-equals-
`differs` proof at the moment of conversion.

### What the conversion changes in the running app

Nothing renders differently. For the 3,233 translated keys `allowlisted()` was
already true; for the 705 that equal English it was false and `t()` fell
through to the en master, which returns the same string. What changes is the
chip: `I18n.provenance("es")` is now `"machine"` and `isMachineLocale("es")`
true, so the honesty chip appears in the header and the signing lines dual-line
their English. Both surfaces key off that single condition
(`vanilla/js/ui/i18n-badge.js:98`, `vanilla/js/ui/risk-text.js:64`). Pinned in
`tooling/i18n-provenance-test.js` against the real twelve shipped dictionaries.

### One consequence to press on

`validate_translations.py es` no longer fails. It failed before conversion only
because v1's `translated` list was a coverage claim that was 705 keys short; v2's
`coverage` claim is honest (a value exists for all 3,938 keys), and v2
deliberately downgrades "value equals English" from a failure to a counted review
note, because no gate can tell a loanword (DEX, HTLC, a brand) from a machine
that copied English. The remaining translation gap in Spanish is therefore
tracked by the census tool and the gate's note — **not** by an exit code. Phase C
progress must be read from `i18n_translation_census.py`, not from a red gate.

---

## 8. Open items / what a reviewer should press on

- **`paintConfirmSingle` / `paintConfirmScaled` remain unkeyed** (§3). They
  are the trade desk's own confirm and do not use `ConfirmDialog`. The honest
  fix is to adopt `ConfirmDialog` there, not to bolt a second widget on.
- **The gate's "is this a confirm row?" test is shape-based** (4 elements,
  `t()` first, dotted-key-shaped 4th). A future subsystem that reuses that
  shape for something else would be gated too and could false-fail. The
  hyphen case (`help.topic_accounts-permissions_title`) proved the shape
  needs widening; it is now pinned by a mutation test so the next widening
  cannot silently shrink coverage again.
- **`RiskText.isVerified()` always returns `false`** — the per-key human-review
  seam is deliberately unwired, so today a machine-filled locale marks every
  unverified key. Wiring it to the locale `_meta.verified` list is the
  follow-up, and it is one `return` statement in one function.
- **Two UI strings are still English literals** in `risk-text.js`: the
  asterisk's `aria-label` and the article link's text. They cannot be keyed
  without touching `vanilla/locales/*.json`, which was out of scope for this
  wave; the keys reserved for them are named in the file header.