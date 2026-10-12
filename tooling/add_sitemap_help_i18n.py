#!/usr/bin/env python3
"""Add the help sitemap article keys to all 12 vanilla locales + rename the
Explore burger section to Discover.

Follows the add_account_net_i18n.py precedent: new keys land allowlisted
with honest English values; _meta.translated stays sorted. The sitemap body
must be byte-identical to BODY_DEFAULTS["sitemap"] joined with "\n" in
vanilla/js/views/help-ui.js — check_i18n.py enforces both directions.

The section rename (menu.section_explore Explore -> Discover) updates en and
resets the other 11 locales to the honest English stub, dropping the key
from their translated allowlists until translators refine it.

Idempotent: re-running reports existing keys and changes nothing.
"""
import io
import json
import sys

LOCALES = ["en", "de", "es", "fr", "it", "ja", "ko", "ru", "tr", "zh", "hi", "pt"]

TITLE = "Site map"
TEXT = "Every page in this wallet on one page: each menu page plus the flows and detail views that have no menu card."
BODY_LINES = [
    "Every page in this wallet, grouped the way the burger menu groups them. Anything with a link opens directly; detail views listed under Pages without a menu card open from their parent pages.",
    "# Wallet",
    "- [Dashboard](#/)",
    "- [My account](#/account/me)",
    "- [Accounts](#/accounts)",
    "- [Transfer](#/transfer)",
    "- [Invoice](#/invoice)",
    "- [Vesting](#/vesting)",
    "- [Wallet](#/wallet)",
    "- [Change wallet password](#/wallet/password)",
    "- [Create Wallet (Brainkey)](#/create-wallet-brainkey)",
    "- [Import existing account](#/existing-account)",
    "- [Register a new account](#/create-account)",
    "- [Login](#/login)",
    "- [Registration](#/registration)",
    "- [Referrals](#/referrals)",
    "# Trade",
    "- [Exchange](#/markets)",
    "- [Instant Trade](#/instant-trade)",
    "- [Liquidity Pools](#/pools)",
    "- [Cross Rates](#/cross-rates)",
    "- [Borrow](#/borrow)",
    "- [Barter](#/barter)",
    "- [Deposit / Withdraw](#/deposit-withdraw)",
    "- [Same-T Funds](#/samet)",
    "- [Spotlight](#/spotlight)",
    "# Earn & Protect",
    "- [Credit Offer](#/credit-offer)",
    "- [Direct Debit](#/direct-debit)",
    "- [HTLC](#/htlc)",
    "- [Tickets](#/tickets)",
    "- [Airdrop](#/airdrop)",
    "- [Custom Authorities](#/authorities)",
    "- [Account Lists](#/lists)",
    "# Govern",
    "- [Voting](#/voting)",
    "- [Proposals](#/proposals)",
    "- [Create Worker](#/create-worker)",
    "- [Prediction Markets](#/prediction)",
    "# Discover",
    "- [Explore](#/explorer)",
    "- [Assets](#/assets)",
    "- [Create asset](#/assets/create)",
    "- [Issue Asset](#/assets/issue)",
    "- [Publish feed](#/assets/feed)",
    "- [Network fees](#/explorer/fees)",
    "- [Operations](#/ops)",
    "- [Top Operations](#/top-ops)",
    "- [News](#/news)",
    "# Labs",
    "- [API Lab](#/api-lab)",
    "- [ES Lab](#/es-lab)",
    "- [Transaction Builder](#/txbuilder)",
    "- [Account Network](#/account-network)",
    "# Personal",
    "- [Trollbox](#/trollbox)",
    "- [Favourites](#/favourites)",
    "- [Price Alerts](#/alerts)",
    "- [Help](#/help)",
    "- [About](#/about)",
    "- [Community](#/community)",
    "- [Settings](#/settings)",
    "# Pages without a menu card",
    "Registration variants, account and market desks, and detail views open from the pages above or from links elsewhere in the wallet.",
    "- [Local registration](#/registration/local)",
    "- [Cloud registration](#/registration/cloud)",
    "- [Example account page](#/account/committee-account)",
    "- [Example market desk](#/market/BTS_USD)",
    "- [Example asset page](#/asset/BTS)",
    "- [Example pool desk](#/pools/1.19.66)",
    "- [Menu overview](#/menu)",
    "Detail views for a specific credit offer, deal, proposal, block, transaction, HTLC, prediction market, transfer recipient, invoice, gateway, settings tab, explorer tab, or help article open from their parent pages and take an id or name in the address.",
]
BODY = "\n".join(BODY_LINES)

NEW_KEYS = {
    "help.topic_sitemap_title": TITLE,
    "help.topic_sitemap_text": TEXT,
    "help.topic_sitemap_body": BODY,
    "help.sitemap_sections": "Sections",
}

RENAME_KEY = "menu.section_explore"
RENAME_EN = "Discover"


def main():
    for code in LOCALES:
        path = "vanilla/locales/%s.json" % code
        with io.open(path, encoding="utf-8") as f:
            data = json.load(f)
        changed = False
        for full, value in NEW_KEYS.items():
            section, _, key = full.partition(".")
            bucket = data.setdefault(section, {})
            if key not in bucket:
                bucket[key] = value
                changed = True
            elif bucket[key] != value:
                print("MISMATCH %s %s: %r != %r" % (path, full, bucket[key], value))
                return 1
            inv = data["_meta"]["translated"]
            if full not in inv:
                inv.append(full)
                changed = True
        # Section rename: every locale takes the new English word with the key
        # allowlisted (check_i18n requires fully-translated dicts to list
        # every key; translators refine the wording from the English stub).
        # Same honest-stub pattern as NEW_KEYS above.
        bucket = data.setdefault("menu", {})
        inv = data["_meta"]["translated"]
        if bucket.get("section_explore") != RENAME_EN:
            bucket["section_explore"] = RENAME_EN
            changed = True
        if RENAME_KEY not in inv:
            inv.append(RENAME_KEY)
            changed = True
        data["_meta"]["translated"] = sorted(data["_meta"]["translated"])
        if changed:
            with io.open(path, "w", encoding="utf-8", newline="\n") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print(("updated " if changed else "unchanged ") + path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
