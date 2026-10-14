#!/usr/bin/env python3
"""Rename vote-locked "टिकट" -> "वोटिंग स्टेक" in vanilla/locales/hi.json.

Compound (per brief): "वोटिंग स्टेक" (vote वोटिंग + stake स्टेक, both
verbatim: vote.title "वोटिंग", tickets_body "वोटिंग वेट", vote.ballot_intro
"आपकी स्टेक", pool.confirm_stake "स्टेक की पुष्टि करें"). Sing/plur share
the form in the shipped dict (मेरे टिकट for plur), so the compound is
invariable too.
Bare "स्टेक" where the sentence already says vote (title + body line 1).

Keys unchanged. Placeholders byte-identical. Route "#/tickets" unchanged.
Event-admission "इवेंट टिकट" in help.topic_assets-uia_body EXCLUDED.

Gates G1-G5: same as rename_ticket_stake_de.py.
Usage: python3 tooling/rename_ticket_stake_hi.py [--apply]
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOC = os.path.join(HERE, "..", "vanilla", "locales", "hi.json")

TICKET_RE = re.compile("टिकट")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_ticket_create": (
        "टिकट निर्माण",
        "वोटिंग स्टेक निर्माण",
    ),
    "account.op_ticket_update": (
        "टिकट अपडेट",
        "वोटिंग स्टेक अपडेट",
    ),
    "account.sum_ticket_create": (
        "टिकट %(amount)s बनाया गया",
        "वोटिंग स्टेक %(amount)s बनाया गया",
    ),
    "account.sum_ticket_update": (
        "टिकट %(ticket)s अपडेट हुआ",
        "वोटिंग स्टेक %(ticket)s अपडेट हुआ",
    ),
    "help.topic_tickets_title": (
        "वोट-लॉक्ड टिकट",
        "वोट-लॉक्ड स्टेक",
    ),
    "menu.p_tickets": (
        "टिकट",
        "वोटिंग स्टेक",
    ),
    "proposal.err_downgrade_unproven": (
        "टिकट डाउनग्रेड अप्रमाणित हैं — वर्तमान लॉक या लंबा लॉक चुनें।",
        "वोटिंग स्टेक डाउनग्रेड अप्रमाणित हैं — वर्तमान लॉक या लंबा लॉक चुनें।",
    ),
    "proposal.err_unknown_ticket": (
        "अज्ञात टिकट।",
        "अज्ञात वोटिंग स्टेक।",
    ),
    "proposal.inner_ticket_amount_must_be_0": (
        "आंतरिक टिकट राशि > 0 होनी चाहिए।",
        "आंतरिक वोटिंग स्टेक राशि > 0 होनी चाहिए।",
    ),
    "proposal.op_57": (
        "टिकट निर्माण",
        "वोटिंग स्टेक निर्माण",
    ),
    "proposal.op_58": (
        "टिकट अद्यतन",
        "वोटिंग स्टेक अद्यतन",
    ),
    "proposal.ticket": (
        "टिकट",
        "वोटिंग स्टेक",
    ),
    "proposals_ticket.title": (
        "टिकट",
        "वोटिंग स्टेक",
    ),
    "ticket.confirm_ticket_create_op_57": (
        "टिकट निर्माण की पुष्टि करें (op 57)",
        "वोटिंग स्टेक निर्माण की पुष्टि करें (op 57)",
    ),
    "ticket.confirm_ticket_update_op_58": (
        "टिकट अपडेट की पुष्टि करें (op 58)",
        "वोटिंग स्टेक अपडेट की पुष्टि करें (op 58)",
    ),
    "ticket.could_not_build_the_ticket_check_account_asse": (
        "टिकट नहीं बन सका (खाता, एसेट और राशि जाँचें)।",
        "वोटिंग स्टेक नहीं बन सका (खाता, एसेट और राशि जाँचें)।",
    ),
    "ticket.could_not_load_tickets": (
        "टिकट लोड नहीं हो सके।",
        "वोटिंग स्टेक लोड नहीं हो सके।",
    ),
    "ticket.create_ticket": (
        "टिकट बनाएँ",
        "वोटिंग स्टेक बनाएँ",
    ),
    "ticket.loading_my_tickets": (
        "मेरे टिकट लोड हो रहे हैं…",
        "मेरे वोटिंग स्टेक लोड हो रहे हैं…",
    ),
    "ticket.loading_tickets": (
        "टिकट लोड हो रहे हैं…",
        "वोटिंग स्टेक लोड हो रहे हैं…",
    ),
    "ticket.my_tickets": (
        "मेरे टिकट",
        "मेरे वोटिंग स्टेक",
    ),
    "ticket.review_ticket": (
        "टिकट की समीक्षा करें",
        "वोटिंग स्टेक की समीक्षा करें",
    ),
    "ticket.ticket": (
        "टिकट",
        "वोटिंग स्टेक",
    ),
    "ticket.ticket_amount_must_be_0": (
        "टिकट राशि > 0 होनी चाहिए।",
        "वोटिंग स्टेक राशि > 0 होनी चाहिए।",
    ),
    "ticket.ticket_created_and_re_read_on_chain": (
        "टिकट बना और ऑन-चेन पुनः पढ़ा गया।",
        "वोटिंग स्टेक बना और ऑन-चेन पुनः पढ़ा गया।",
    ),
    "ticket.ticket_updated_and_re_read_on_chain": (
        "टिकट अपडेट हुआ और ऑन-चेन पुनः पढ़ा गया।",
        "वोटिंग स्टेक अपडेट हुआ और ऑन-चेन पुनः पढ़ा गया।",
    ),
    "ticket.tickets": (
        "टिकट",
        "वोटिंग स्टेक",
    ),
    "ticket.tickets_cannot_be_deleted_no_delete_op_exists": (
        "टिकट हटाए नहीं जा सकते (कोई डिलीट op नहीं) — ऊपर पंक्तियाँ स्थायी हैं।",
        "वोटिंग स्टेक हटाए नहीं जा सकते (कोई डिलीट op नहीं) — ऊपर पंक्तियाँ स्थायी हैं।",
    ),
    "ticket.tickets_lock_funds_for_vote_weight_there_is_n": (
        "टिकट वोट वेट के लिए फ़ंड लॉक करते हैं। कोई डिलीट ऑपरेशन नहीं है, इसलिए प्रत्येक टिकट पंक्ति स्थायी है।",
        "वोटिंग स्टेक वोट वेट के लिए फ़ंड लॉक करते हैं। कोई डिलीट ऑपरेशन नहीं है, इसलिए प्रत्येक वोटिंग स्टेक पंक्ति स्थायी है।",
    ),
    "tickets.title": (
        "टिकट",
        "वोटिंग स्टेक",
    ),
}

SNIPPETS = {
    "help.topic_glossary_body": [
        (
            "वोट, पूल गतियाँ, टिकट, चैट।",
            "वोट, पूल गतियाँ, वोटिंग स्टेक, चैट।",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [टिकट](#/tickets)",
            "- [वोटिंग स्टेक](#/tickets)",
            1,
        ),
    ],
    "help.topic_tickets_body": [
        (
            "वोट-लॉक्ड टिकट स्टेक व समय को वोटिंग वेट में बदलते हैं",
            "वोट-लॉक्ड स्टेक स्टेक व समय को वोटिंग वेट में बदलते हैं",
            1,
        ),
        (
            "लिक्विड स्टेक से टिकट बनाएँ, बढ़ाएँ, और लॉक समाप्ति पर वापस दावा करें।",
            "लिक्विड स्टेक से वोटिंग स्टेक बनाएँ, बढ़ाएँ, और लॉक समाप्ति पर वापस दावा करें।",
            1,
        ),
        (
            "टिकट वेट सामान्य मतपत्र से",
            "वोटिंग स्टेक वेट सामान्य मतपत्र से",
            1,
        ),
    ],
}


def dig(d, key):
    node = d
    for seg in key.split("."):
        node = node[seg]
    return node


def set_dig(d, key, value):
    segs = key.split(".")
    node = d
    for seg in segs[:-1]:
        node = node[seg]
    node[segs[-1]] = value


def flatten(d, prefix=""):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(flatten(v, prefix + k + "."))
        else:
            out[prefix + k] = v
    return out


def main():
    apply = "--apply" in sys.argv
    raw = open(LOC, encoding="utf-8").read()
    d = json.loads(raw)
    before_keys = set(flatten(d))
    before_meta = json.loads(json.dumps(d.get("_meta")))
    before_vals = flatten(d)

    problems = []
    for key, (old, new) in FULL.items():
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not TICKET_RE.search(cur):
            problems.append("ABORT %s: no ticket-family word: %r" % (key, cur))
            continue
        if cur != old:
            problems.append("ABORT %s: current != expected.\n got: %r\n exp: %r" % (key, cur, old))
            continue
        if sorted(PLACEHOLDER_RE.findall(cur)) != sorted(PLACEHOLDER_RE.findall(new)):
            problems.append("ABORT %s: placeholder change" % key)
            continue
        if not TICKET_RE.search(old):
            problems.append("ABORT %s: script old has no ticket word" % key)
            continue
    for key, reps in SNIPPETS.items():
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not TICKET_RE.search(cur):
            problems.append("ABORT %s: no ticket-family word" % key)
            continue
        for old_snip, new_snip, count in reps:
            if not TICKET_RE.search(old_snip):
                problems.append("ABORT %s: snippet w/o ticket: %r" % (key, old_snip))
                continue
            if cur.count(old_snip) != count:
                problems.append("ABORT %s: snippet x%d != %d: %r" % (key, cur.count(old_snip), count, old_snip))
            if sorted(PLACEHOLDER_RE.findall(old_snip)) != sorted(PLACEHOLDER_RE.findall(new_snip)):
                problems.append("ABORT %s: snippet placeholder change" % key)
    excl = dig(d, "help.topic_assets-uia_body")
    if "इवेंट टिकट" not in excl:
        problems.append("ABORT help.topic_assets-uia_body: event sense changed unexpectedly")
    if problems:
        print("FAIL (%d):" % len(problems))
        print("\n".join(problems))
        return 1

    for key, (old, new) in FULL.items():
        set_dig(d, key, new)
    for key, reps in SNIPPETS.items():
        cur = dig(d, key)
        for old_snip, new_snip, count in reps:
            assert cur.count(old_snip) == count, key
            cur = cur.replace(old_snip, new_snip)
        if key == "help.topic_sitemap_body":
            assert HREF_RE.findall(before_vals[key]) == HREF_RE.findall(cur), "sitemap href drift"
        set_dig(d, key, cur)

    if set(flatten(d)) != before_keys:
        print("FAIL: key drift")
        return 1
    if d.get("_meta") != before_meta:
        print("FAIL: _meta moved")
        return 1
    after_vals = flatten(d)
    for k, v in before_vals.items():
        if k not in FULL and k not in SNIPPETS and after_vals[k] != v:
            print("FAIL: untouched key moved: %s" % k)
            return 1

    out = json.dumps(d, indent=2, ensure_ascii=False) + "\n"
    if apply:
        open(LOC, "w", encoding="utf-8").write(out)
        print("OK hi: %d full + %d snippet keys renamed" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK hi: dry run green (%d full + %d snippet)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
