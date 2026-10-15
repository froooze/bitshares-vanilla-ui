# Proto-English — writing English that translates well

> Status: approved doctrine. Applies to every user-visible English string
> added or changed in this repo from 2026-10-14 onward.

## The three tiers

English in this repo comes in three tiers. Name which one you are writing
before you write it:

1. **Proto-english** — English designed so it translates well. Short
   sentences, one clause each. No idioms, no phrasal verbs where a plain
   verb exists, no culture-bound metaphors, no acronyms that are not
   industry standard. A translator with no crypto background should render
   it correctly on the first pass. THIS is the tier all user-visible
   strings must aim for.
2. **Colloquial english** — what we commonly speak ("trollbox", "walk the
   book", "dust", "moon"). May not translate cleanly, and usually does not.
   Never ship it in UI strings. If you catch yourself writing it, rewrite.
3. **Proper english** — grammatically correct but translation-hostile:
   long nested clauses, nominalizations ("utilization of funds" for "use"),
   Latinate diction where Germanic is plainer. Correct and untranslatable
   is still a defect here.

## The test

Before committing any user-visible string, read it as a translator with no
crypto background would: **could they render this correctly without asking
you what it means?** If the answer needs a glossary entry to survive, the
string failed — simplify the English instead of documenting around it.

## Worked examples (both directions)

**Same-T → flash loans.** "Same-T" names an op family, not a concept a
user holds. The industry word for borrow-and-repay-atomically is "flash
loan", so the UI says flash loan and keeps "Same-T" exactly once, as a
parenthetical bridge in the help article. Rule: use the term the user
already knows; keep the dev term discoverable, never primary.

**HTLC stays.** The same test, the opposite answer. HTLC is the
cross-chain industry term (Lightning, atomic swaps, every chain's docs) —
dropping it would disconnect our users from the ecosystem's vocabulary.
So HTLC stays in chrome, glossed once in teaching prose. Rule: keep terms
the wider world uses (HTLC, DEX, multisig, vesting, memo, faucet); drop
terms only we use. The eight renames this doctrine has produced so far:
chat, ballot list, private transfer, user issued token, voting stake,
grant proposal, recovery phrase, block validator — each with its dev term
kept findable in help or glossary, never primary.

## What this does NOT license

- Renaming keys, routes, op names, or file paths. Identifiers stay.
- Rewriting a locale's existing translations to match a new English
  sentence structure. Change the English, then re-translate properly.
- Marking anything verified. A proto-english source still produces
  machine translations until a human reviews them.
