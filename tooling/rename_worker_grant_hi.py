#!/usr/bin/env python3
"""Rename treasury worker -> grant proposal in vanilla/locales/hi.json.

Scope: ONLY values carrying the treasury-proposal sense (30 FULL + 6 snippet bodies). Keys unchanged.
Excluded by design (aborts if touched, reported, never rewritten):
  * placeholders (%(name)s, %(op)s stay byte-identical; code-bound).
  * code identifiers (get_all_workers in vote.hide_legacy_title stays).
  * route hashes (#/create-worker in sitemap + empty_hint stays).
  * file paths (js/ in backend-missing strings stays).
  * chrome with no worker word (daily_pay, work dates, pay_destination ...),
    help.topic_workers_text and menu.d_worker — untouched.

Compound (per brief, from dict's OWN attested words where possible): अनुदान प्रस्ताव / अनुदान लाभार्थी.
Pay keeps attested pay word (never transliterated pay); budget/funding keep attested words;
recipients (PEOPLE) use beneficiary word attested in referrals body, not proposals.

Safety gates: G1 current has worker-family word; G2 current == expected old
(FULL) or snippet counts (SNIPPETS); G3 placeholders/hrefs/identifiers kept;
G4 key set + _meta + untouched values; G5 formatting round-trip.

Usage: python3 tooling/rename_worker_grant_hi.py [--apply]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "vanilla", "locales", "hi.json")

WORKER_RE = re.compile(r"वर्कर")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_worker_create": (
        "वर्कर निर्माण",
        "अनुदान प्रस्ताव निर्माण",
    ),
    "account.sum_worker_create": (
        "वर्कर “%(name)s” बनाया गया",
        "अनुदान प्रस्ताव “%(name)s” बनाया गया",
    ),
    "createworker.confirm_worker_op_34": (
        "वर्कर की पुष्टि करें (op %(op)s)",
        "अनुदान प्रस्ताव की पुष्टि करें (op %(op)s)",
    ),
    "createworker.could_not_preview_the_worker": (
        "वर्कर का पूर्वावलोकन नहीं हो सका।",
        "अनुदान प्रस्ताव का पूर्वावलोकन नहीं हो सका।",
    ),
    "createworker.create_worker": (
        "वर्कर बनाएँ",
        "अनुदान प्रस्ताव बनाएँ",
    ),
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        "वर्कर का मसौदा तैयार करें (op %(op)s)। प्रीव्यू लाइव है; समीक्षा में लाइव शुल्क बताया जाता है, फिर साइन और भेजें op %(op)s को सीधे प्रसारित करता है — वर्कर प्रस्ताव से नहीं, सीधे op से बनते हैं।",
        "अनुदान प्रस्ताव का मसौदा तैयार करें (op %(op)s)। प्रीव्यू लाइव है; समीक्षा में लाइव शुल्क बताया जाता है, फिर साइन और भेजें op %(op)s को सीधे प्रसारित करता है — अनुदान प्रस्ताव प्रस्ताव से नहीं, सीधे op से बनते हैं।",
    ),
    "createworker.enter_a_worker_name": (
        "वर्कर नाम डालें।",
        "अनुदान प्रस्ताव नाम डालें।",
    ),
    "createworker.owner_pays_the_fee_and_receives_the_": (
        "मालिक शुल्क देता है और वर्कर वेतन पाता है — अपने नियंत्रण का लाइफ़टाइम-सदस्य खाता उपयोग करें।",
        "मालिक शुल्क देता है और अनुदान प्रस्ताव वेतन पाता है — अपने नियंत्रण का लाइफ़टाइम-सदस्य खाता उपयोग करें।",
    ),
    "createworker.preview_worker": (
        "वर्कर का पूर्वावलोकन करें",
        "अनुदान प्रस्ताव का पूर्वावलोकन करें",
    ),
    "createworker.publishing_a_worker_requires_a_lifeti": (
        "वर्कर प्रकाशन के लिए लाइफ़टाइम-सदस्य खाता आवश्यक है — बुनियादी खाते यह शुल्क नहीं दे सकते। नीचे मालिक पहले से अपग्रेडेड होना चाहिए।",
        "अनुदान प्रस्ताव प्रकाशन के लिए लाइफ़टाइम-सदस्य खाता आवश्यक है — बुनियादी खाते यह शुल्क नहीं दे सकते। नीचे मालिक पहले से अपग्रेडेड होना चाहिए।",
    ),
    "createworker.reading_existing_workers": (
        "मौजूदा वर्कर पढ़े जा रहे हैं…",
        "मौजूदा अनुदान प्रस्ताव पढ़े जा रहे हैं…",
    ),
    "createworker.worker_backend_missing_js_account_js_or_js_fo": (
        "वर्कर बैकएंड गायब है: js/account.js या js/format.js लोड नहीं हुआ।",
        "अनुदान प्रस्ताव बैकएंड गायब है: js/account.js या js/format.js लोड नहीं हुआ।",
    ),
    "createworker.worker_backend_missing_js_asset_ops_js_failed": (
        "वर्कर बैकएंड गायब है: js/asset-ops.js लोड नहीं हुआ।",
        "अनुदान प्रस्ताव बैकएंड गायब है: js/asset-ops.js लोड नहीं हुआ।",
    ),
    "createworker.worker_name": (
        "वर्कर नाम ",
        "अनुदान प्रस्ताव नाम ",
    ),
    "createworker.worker_preview_op_34": (
        "वर्कर प्रीव्यू (op %(op)s)",
        "अनुदान प्रस्ताव प्रीव्यू (op %(op)s)",
    ),
    "help.topic_workers_title": (
        "वर्कर",
        "अनुदान प्रस्ताव",
    ),
    "help.topic_voting_text": (
        "विटनेस, कमेटी, वर्कर को वोट दें — या प्रॉक्सी को सौंप दें।",
        "विटनेस, कमेटी, अनुदान प्रस्ताव को वोट दें — या प्रॉक्सी को सौंप दें।",
    ),
    "menu.d_voting": (
        "विटनेस, कमेटी, वर्कर और प्रॉक्सी।",
        "विटनेस, कमेटी, अनुदान प्रस्ताव और प्रॉक्सी।",
    ),
    "menu.p_worker": (
        "वर्कर बनाएँ",
        "अनुदान प्रस्ताव बनाएँ",
    ),
    "news.voting_witnesses_committee_workers": (
        "वोटिंग — विटनेस, कमेटी, वर्कर",
        "वोटिंग — विटनेस, कमेटी, अनुदान प्रस्ताव",
    ),
    "seo.desc_voting": (
        "BitShares विटनेस, कमेटी सदस्य व वर्कर हेतु वोट दें। प्रत्येक मत आपके डिवाइस पर स्थानीय रूप से हस्ताक्षरित है।",
        "BitShares विटनेस, कमेटी सदस्य व अनुदान प्रस्ताव हेतु वोट दें। प्रत्येक मत आपके डिवाइस पर स्थानीय रूप से हस्ताक्षरित है।",
    ),
    "vote.ballot_intro": (
        "आपकी स्टेक विटनेस व कमेटी का चुनाव करती है और वर्करों को धन देती है — नीचे दी गई हर गिनती व हिस्सा लाइव चेन पठन है।",
        "आपकी स्टेक विटनेस व कमेटी का चुनाव करती है और अनुदान प्रस्तावों को धन देती है — नीचे दी गई हर गिनती व हिस्सा लाइव चेन पठन है।",
    ),
    "vote.empty_hint": (
        " चेन में आने पर प्रविष्टियाँ दिखेंगी — वर्कर #/create-worker से प्रस्तावित होते हैं।",
        " चेन में आने पर प्रविष्टियाँ दिखेंगी — अनुदान प्रस्ताव #/create-worker से प्रस्तावित होते हैं।",
    ),
    "vote.funding_unavailable_prefix": (
        "वर्कर फंडिंग अनुपलब्ध (",
        "अनुदान प्रस्ताव फंडिंग अनुपलब्ध (",
    ),
    "vote.hide_legacy_label": (
        " पुराने प्रस्ताव छिपाएँ (हमेशा चालू — समाप्त वर्कर फ़ेच पर बाहर रखे जाते हैं)",
        " पुराने प्रस्ताव छिपाएँ (हमेशा चालू — समाप्त अनुदान प्रस्ताव फ़ेच पर बाहर रखे जाते हैं)",
    ),
    "vote.hide_legacy_title": (
        "वर्कर सूचियाँ get_all_workers(false) से आती हैं; समाप्त पंक्तियाँ कभी नहीं आतीं।",
        "अनुदान प्रस्ताव सूचियाँ get_all_workers(false) से आती हैं; समाप्त पंक्तियाँ कभी नहीं आतीं।",
    ),
    "vote.no_workers": (
        "कोई वर्कर नहीं मिला। testnet में अक्सर कोई नहीं होता — यह वैध है, त्रुटि नहीं।",
        "कोई अनुदान प्रस्ताव नहीं मिला। testnet में अक्सर कोई नहीं होता — यह वैध है, त्रुटि नहीं।",
    ),
    "vote.tab_workers": (
        "वर्कर (",
        "अनुदान प्रस्ताव (",
    ),
    "vote.worker_budget": (
        "वर्कर बजट: —",
        "अनुदान प्रस्ताव बजट: —",
    ),
    "vote.worker_budget_loading": (
        "वर्कर बजट: लोड हो रहा है…",
        "अनुदान प्रस्ताव बजट: लोड हो रहा है…",
    ),
}

SNIPPETS = {
    "help.topic_glossary_body": [
        ("वर्कर भुगतानित परियोजनाएँ देते हैं", "अनुदान लाभार्थी भुगतानित परियोजनाएँ देते हैं", 1,),
    ],
    "help.topic_sitemap_body": [
        ("वर्कर", "अनुदान प्रस्ताव", 1,),
    ],
    "help.topic_tickets_body": [
        ("वर्कर", "अनुदान प्रस्ताव", 1,),
    ],
    "help.topic_vesting_body": [
        ("वर्कर", "अनुदान प्रस्ताव", 1,),
    ],
    "help.topic_voting_body": [
        ("वर्कर", "अनुदान प्रस्ताव", 6,),
    ],
    "help.topic_workers_body": [
        ("वर्कर", "अनुदान प्रस्ताव", 5,),
    ],
}


def digd(d, key):
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
    raw = open(P, encoding="utf-8").read()
    d = json.loads(raw)
    if json.dumps(d, indent=2, ensure_ascii=False) + "\n" != raw:
        print(f"FAIL: {P} does not round-trip indent=2/ensure_ascii=False + \\n")
        return 1
    before_keys = set(flatten(d))
    before_meta = json.loads(json.dumps(d.get("_meta")))
    before_vals = flatten(d)

    problems = []

    for key, (old, new) in FULL.items():
        try:
            cur = digd(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not WORKER_RE.search(cur):
            problems.append("ABORT %s: current value has no worker-family word: %r" % (key, cur))
            continue
        if cur != old:
            problems.append("ABORT %s: current != expected old.\n got: %r\n exp: %r" % (key, cur, old))
            continue
        if sorted(PLACEHOLDER_RE.findall(cur)) != sorted(PLACEHOLDER_RE.findall(new)):
            problems.append("ABORT %s: placeholder multiset would change" % key)
            continue
        if not WORKER_RE.search(old):
            problems.append("ABORT %s: script old has no worker word (script bug)" % key)
            continue

    for key, reps in SNIPPETS.items():
        try:
            cur = digd(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not WORKER_RE.search(cur):
            problems.append("ABORT %s: current value has no worker-family word" % key)
            continue
        for old_snip, new_snip, count in reps:
            if not WORKER_RE.search(old_snip) and key != "help.topic_glossary_body":
                # glossary old_snip contains worker word by definition; allow generic check
                pass
            # For glossary, old_snip must contain worker word; enforce
            if key == "help.topic_glossary_body" and not WORKER_RE.search(old_snip):
                problems.append("ABORT %s: snippet has no worker word (script bug): %r" % (key, old_snip))
                continue
            if key != "help.topic_glossary_body" and not WORKER_RE.search(old_snip):
                problems.append("ABORT %s: snippet has no worker word (script bug): %r" % (key, old_snip))
                continue
            got = cur.count(old_snip)
            if got != count:
                problems.append("ABORT %s: snippet occurs %d != %d: %r" % (key, got, count, old_snip))
            if sorted(PLACEHOLDER_RE.findall(old_snip)) != sorted(PLACEHOLDER_RE.findall(new_snip)):
                problems.append("ABORT %s: snippet placeholder change: %r" % (key, old_snip))

    if problems:
        print("FAIL (%d):" % len(problems))
        print("\n".join(problems))
        return 1

    for key, (old, new) in FULL.items():
        set_dig(d, key, new)
    for key, reps in SNIPPETS.items():
        cur = digd(d, key)
        for old_snip, new_snip, count in reps:
            assert cur.count(old_snip) == count, key
            cur = cur.replace(old_snip, new_snip)
        if key == "help.topic_sitemap_body":
            assert HREF_RE.findall(before_vals[key]) == HREF_RE.findall(cur), "sitemap href drift"
        set_dig(d, key, cur)

    after_vals = flatten(d)
    if "get_all_workers" not in after_vals["vote.hide_legacy_title"]:
        print("FAIL: get_all_workers token lost")
        return 1
    for k in ("createworker.worker_backend_missing_js_account_js_or_js_fo",
              "createworker.worker_backend_missing_js_asset_ops_js_failed"):
        if "js/" not in after_vals[k]:
            print("FAIL: file path lost in %s" % k)
            return 1
    for k in ("help.topic_sitemap_body", "vote.empty_hint"):
        if "#/create-worker" not in after_vals[k]:
            print("FAIL: route hash lost in %s" % k)
            return 1

    if set(after_vals) != before_keys:
        print("FAIL: key set drift")
        return 1
    if d.get("_meta") != before_meta:
        print("FAIL: _meta moved")
        return 1
    for k, v in before_vals.items():
        if k not in FULL and k not in SNIPPETS and after_vals[k] != v:
            print("FAIL: untouched key moved: %s" % k)
            return 1

    out = json.dumps(d, indent=2, ensure_ascii=False) + "\n"
    if apply:
        open(P, "w", encoding="utf-8").write(out)
        print(f"OK {P}: renamed")
    else:
        print(f"OK {P}: dry run green")
    return 0


if __name__ == "__main__":
    import sys as _sys
    _sys.exit(main())
