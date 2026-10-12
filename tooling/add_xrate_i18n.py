#!/usr/bin/env python3
"""Add the cross-rates i18n keys to all 12 vanilla locales.

Follows the add_account_net_i18n.py precedent: every dict is
fully-translated (untranslated=false), so new keys land allowlisted with
honest English values — translators refine wording, never keys. The
_meta.translated inventory is kept sorted in every dict, as check_i18n expects.

The values below must be byte-identical to the t() defaults at the call sites
in vanilla/js/views/xrate-ui.js (and menu-ui.js / router.js for the card +
SEO strings) — check_i18n.py enforces both directions.

Idempotent: re-running reports existing keys and changes nothing.
"""
import io
import json
import sys

LOCALES = ["en", "de", "es", "fr", "it", "ja", "ko", "ru", "tr", "zh", "hi", "pt"]

# Verbatim I18n.t defaults from the call sites.
NEW_KEYS = {
    # ---- page shell (xrate-ui.js) ----
    "xrate.title": "Cross Rates",
    "xrate.intro": "Every pool asset priced at its last swap, crossed through the pool graph. Nothing is signed and nothing is stored.",
    "xrate.token_label": "Add quote token",
    "xrate.token_placeholder": "USD, CNY, BTC…",
    "xrate.add_btn": "Add column",
    "xrate.base_pinned": "BTS is the base column and cannot be removed.",
    "xrate.loading": "Reading pools…",
    "xrate.load_failed": "Could not load cross rates: ",
    "xrate.refresh_btn": "Refresh prices",
    "xrate.show_all": "Show all assets",
    "xrate.retry_btn": "Retry",
    "xrate.remove_btn": "Remove ",
    "xrate.empty": "No pool assets within 3 hops of BTS on this chain.",
    "xrate.asset_col": "Asset",
    "xrate.unknown_token": "No pool asset named %(sym)s.",
    "xrate.unpriced": "A leg on this route has no recorded swap yet.",
    "xrate.no_route_col": "No route to %(sym)s within 6 pool hops.",
    "xrate.status": "%(pools)s pools · %(assets)s assets within 3 hops · %(done)s of %(total)s pools hold a last swap",
    # ---- sitemap card (menu-ui.js, Trade section) ----
    "menu.p_xrates": "Cross Rates",
    "menu.d_xrates": "Pool prices for every asset in BTS and more.",
    # ---- SEO meta (router.js ROUTE_META) ----
    "seo.title_xrates": "Cross Rates — BitShares Wallet",
    "seo.desc_xrates": "Every pool asset priced in BTS and more at last swap prices. No login needed.",
}


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
        data["_meta"]["translated"] = sorted(data["_meta"]["translated"])
        if changed:
            with io.open(path, "w", encoding="utf-8", newline="\n") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print(("updated " if changed else "unchanged ") + path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
