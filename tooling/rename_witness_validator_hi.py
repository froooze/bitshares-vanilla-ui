#!/usr/bin/env python3
"""Rename "विटनेस" -> "ब्लॉक सत्यापनकर्ता" in vanilla/locales/hi.json.

Scope: ONLY the 38 block-producer keys (27 short + 11 long bodies).
Keys unchanged. Excluded by design (aborts if touched, never rewritten):
  * placeholders — %(account)s / %(op)s stay byte-identical.
  * route targets — "#/explorer/witnesses" stays (router path, code).
  * key names (*witness*, topic_witnesses_*) stay (code).
  * the DEFINITION ब्लॉक उत्पादक stays — it glosses the office, not the term.
  * गवाह (court witness) never appears here; do not introduce it.

Compound (per brief, from the locale's OWN attested words):
ब्लॉक सत्यापनकर्ता — block ब्लॉक (87 keys) + validation सत्यापन
(prediction.pmo_attestation, dex-intro सत्यापनीय) + agent कर्ता
(productive suffix, 101 keys). Hyphen "विटनेस-फ़ीड" renders as
ब्लॉक सत्यापनकर्ता-फ़ीड (hyphen structure mirrored); "विटनेस बने"
becoming-verb and "के रूप में जुड़ें" action phrasing keep locale grammar.

Safety gates (assert before write):
  G1 every target's CURRENT value contains विटनेस, else abort.
  G2 every FULL target's current value EQUALS the expected old string.
  G3 every snippet occurs exactly its expected count.
  G4 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged.
  G5 key set + _meta deep-equal before/after; non-target values untouched.
  G6 json.dumps(indent=2, ensure_ascii=False)+"\\n" formatting.

Usage: python3 tooling/rename_witness_validator_hi.py [--apply]
Dry run (asserts only) by default; --apply writes hi.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOC = os.path.join(HERE, "..", "vanilla", "locales", "hi.json")

WITNESS_RE = re.compile(r"विटनेस")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {'account.op_witness_join': ('विटनेस में जुड़ाव', 'ब्लॉक सत्यापनकर्ता में जुड़ाव'),
 'account.op_witness_update': ('विटनेस अपडेट', 'ब्लॉक सत्यापनकर्ता अपडेट'),
 'account.sum_witness_create': ('विटनेस बने: %(account)s', 'ब्लॉक सत्यापनकर्ता बने: %(account)s'),
 'account.sum_witness_update': ('विटनेस %(account)s अपडेट हुआ',
                                'ब्लॉक सत्यापनकर्ता %(account)s अपडेट हुआ'),
 'asset.witness_fed_note': ('विटनेस-फ़ीड: सक्रिय विटनेस सभी प्रकाशित कर सकते हैं।',
                            'ब्लॉक सत्यापनकर्ता-फ़ीड: सक्रिय ब्लॉक सत्यापनकर्ता सभी प्रकाशित कर '
                            'सकते हैं।'),
 'explorer.stat_wit': ('सक्रिय विटनेस', 'सक्रिय ब्लॉक सत्यापनकर्ता'),
 'explorer.th_witness': ('विटनेस', 'ब्लॉक सत्यापनकर्ता'),
 'explorer.witness_row': ('विटनेस', 'ब्लॉक सत्यापनकर्ता'),
 'help.topic_assets-mpa_text': ('विटनेस के मूल्य फ़ीड सहित कोलैटरल-समर्थित स्मार्टकॉइन।',
                                'ब्लॉक सत्यापनकर्ता के मूल्य फ़ीड सहित कोलैटरल-समर्थित '
                                'स्मार्टकॉइन।'),
 'help.topic_glossary_text': ('इस वॉलेट में प्रयुक्त नाम: ऑब्जेक्ट (1.x.y), ऑपरेशन, विटनेस, कमेटी।',
                              'इस वॉलेट में प्रयुक्त नाम: ऑब्जेक्ट (1.x.y), ऑपरेशन, ब्लॉक '
                              'सत्यापनकर्ता, कमेटी।'),
 'help.topic_voting_text': ('विटनेस, कमेटी, अनुदान प्रस्ताव को वोट दें — या प्रॉक्सी को सौंप दें।',
                            'ब्लॉक सत्यापनकर्ता, कमेटी, अनुदान प्रस्ताव को वोट दें — या प्रॉक्सी '
                            'को सौंप दें।'),
 'help.topic_witnesses_title': ('विटनेस', 'ब्लॉक सत्यापनकर्ता'),
 'menu.d_asset_feed': ('जारीकर्ता या विटनेस के रूप में मूल्य फ़ीड प्रकाशित करें।',
                       'जारीकर्ता या ब्लॉक सत्यापनकर्ता के रूप में मूल्य फ़ीड प्रकाशित करें।'),
 'menu.d_voting': ('विटनेस, कमेटी, अनुदान प्रस्ताव और प्रॉक्सी।',
                   'ब्लॉक सत्यापनकर्ता, कमेटी, अनुदान प्रस्ताव और प्रॉक्सी।'),
 'news.voting_witnesses_committee_workers': ('वोटिंग — विटनेस, कमेटी, अनुदान प्रस्ताव',
                                             'वोटिंग — ब्लॉक सत्यापनकर्ता, कमेटी, अनुदान प्रस्ताव'),
 'seo.desc_voting': ('BitShares विटनेस, कमेटी सदस्य व अनुदान प्रस्ताव हेतु वोट दें। प्रत्येक मत '
                     'आपके डिवाइस पर स्थानीय रूप से हस्ताक्षरित है।',
                     'BitShares ब्लॉक सत्यापनकर्ता, कमेटी सदस्य व अनुदान प्रस्ताव हेतु वोट दें। '
                     'प्रत्येक मत आपके डिवाइस पर स्थानीय रूप से हस्ताक्षरित है।'),
 'seo.title_voting': ('विटनेस को वोट दें — BitShares वॉलेट',
                      'ब्लॉक सत्यापनकर्ता को वोट दें — BitShares वॉलेट'),
 'splash.pulse_witnesses': ('विटनेस', 'ब्लॉक सत्यापनकर्ता'),
 'vote.ballot_intro': ('आपकी स्टेक विटनेस व कमेटी का चुनाव करती है और अनुदान प्रस्तावों को धन देती '
                       'है — नीचे दी गई हर गिनती व हिस्सा लाइव चेन पठन है।',
                       'आपकी स्टेक ब्लॉक सत्यापनकर्ता व कमेटी का चुनाव करती है और अनुदान '
                       'प्रस्तावों को धन देती है — नीचे दी गई हर गिनती व हिस्सा लाइव चेन पठन है।'),
 'vote.confirm_witness_update_op_21': ('विटनेस अद्यतन की पुष्टि करें (op %(op)s)',
                                       'ब्लॉक सत्यापनकर्ता अद्यतन की पुष्टि करें (op %(op)s)'),
 'vote.empty_list': ('नोड ने कोई विटनेस या कमेटी सदस्य नहीं लौटाया।',
                     'नोड ने कोई ब्लॉक सत्यापनकर्ता या कमेटी सदस्य नहीं लौटाया।'),
 'vote.join_as_witness': ('विटनेस के रूप में जुड़ें', 'ब्लॉक सत्यापनकर्ता के रूप में जुड़ें'),
 'vote.no_witness_object_for_this_account_use_join_a': ('इस खाते के लिए कोई विटनेस ऑब्जेक्ट नहीं — '
                                                        'इसके बजाय विटनेस के रूप में जुड़ें का '
                                                        'उपयोग करें।',
                                                        'इस खाते के लिए कोई ब्लॉक सत्यापनकर्ता '
                                                        'ऑब्जेक्ट नहीं — इसके बजाय ब्लॉक '
                                                        'सत्यापनकर्ता के रूप में जुड़ें का उपयोग '
                                                        'करें।'),
 'vote.tab_witnesses': ('विटनेस (', 'ब्लॉक सत्यापनकर्ता ('),
 'vote.update_witness': ('विटनेस अपडेट करें', 'ब्लॉक सत्यापनकर्ता अपडेट करें'),
 'vote.witness': ('विटनेस', 'ब्लॉक सत्यापनकर्ता'),
 'vote.witness_updated': ('विटनेस अपडेट हुआ', 'ब्लॉक सत्यापनकर्ता अपडेट हुआ')}

SNIPPETS = {'help.topic_assets-mpa_body': [('विटनेस', 'ब्लॉक सत्यापनकर्ता', 1)],
 'help.topic_assets-private_body': [('विटनेस', 'ब्लॉक सत्यापनकर्ता', 3)],
 'help.topic_blockchain_body': [('विटनेस', 'ब्लॉक सत्यापनकर्ता', 3)],
 'help.topic_committee_body': [('विटनेस', 'ब्लॉक सत्यापनकर्ता', 1)],
 'help.topic_dex-shorting_body': [('विटनेस', 'ब्लॉक सत्यापनकर्ता', 1)],
 'help.topic_glossary_body': [('विटनेस', 'ब्लॉक सत्यापनकर्ता', 2)],
 'help.topic_settings_body': [('विटनेस', 'ब्लॉक सत्यापनकर्ता', 1)],
 'help.topic_sitemap_body': [('विटनेस', 'ब्लॉक सत्यापनकर्ता', 1)],
 'help.topic_tickets_body': [('विटनेस', 'ब्लॉक सत्यापनकर्ता', 1)],
 'help.topic_voting_body': [('विटनेस', 'ब्लॉक सत्यापनकर्ता', 4)],
 'help.topic_witnesses_body': [('विटनेस', 'ब्लॉक सत्यापनकर्ता', 3)]}


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
        if not isinstance(cur, str) or not WITNESS_RE.search(cur):
            problems.append("ABORT %s: current value has no witness-family word: %r" % (key, cur))
            continue
        if cur != old:
            problems.append("ABORT %s: current != expected old.\n got: %r\n exp: %r" % (key, cur, old))
            continue
        if sorted(PLACEHOLDER_RE.findall(cur)) != sorted(PLACEHOLDER_RE.findall(new)):
            problems.append("ABORT %s: placeholder multiset would change" % key)
            continue
        if not WITNESS_RE.search(old):
            problems.append("ABORT %s: script old has no witness word (script bug)" % key)
            continue

    for key, reps in SNIPPETS.items():
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not WITNESS_RE.search(cur):
            problems.append("ABORT %s: current value has no witness-family word" % key)
            continue
        # Occurrence tally with a leftmost-longest alternation: a bare form
        # (e.g. 증인) is a substring of its own particle/case siblings, so
        # str.count would attribute one occurrence twice. Each occurrence
        # belongs to exactly one (longest) alternative.
        ordered_gate = sorted(reps, key=lambda r: len(r[0]), reverse=True)
        alt_gate = re.compile("|".join(re.escape(o) for o, _n, _c in ordered_gate))
        tally = {}
        for m in alt_gate.finditer(cur):
            tally[m.group(0)] = tally.get(m.group(0), 0) + 1
        for old_snip, new_snip, count in reps:
            if not WITNESS_RE.search(old_snip):
                problems.append("ABORT %s: snippet has no witness word (script bug): %r" % (key, old_snip))
                continue
            if tally.get(old_snip, 0) != count:
                problems.append("ABORT %s: snippet occurs %d != %d: %r" % (key, tally.get(old_snip, 0), count, old_snip))
            if sorted(PLACEHOLDER_RE.findall(old_snip)) != sorted(PLACEHOLDER_RE.findall(new_snip)):
                problems.append("ABORT %s: snippet placeholder change: %r" % (key, old_snip))

    if "help.topic_sitemap_body" in SNIPPETS:
        sm = before_vals["help.topic_sitemap_body"]
        if sm.count("#/explorer/witnesses") != 1:
            problems.append("ABORT sitemap: expected exactly one #/explorer/witnesses link")

    if problems:
        print("FAIL (%d):" % len(problems))
        print("\n".join(problems))
        return 1

    for key, (old, new) in FULL.items():
        set_dig(d, key, new)
    for key, reps in SNIPPETS.items():
        cur = dig(d, key)
        # Single leftmost-longest pass: sequential replaces would miscount,
        # because a bare form (e.g. 증인) is a substring of its own
        # particle/case siblings. Alternation ordered longest-first replaces
        # each occurrence exactly once; the gate above already proved the
        # per-form counts on the pristine string.
        ordered = sorted(reps, key=lambda r: len(r[0]), reverse=True)
        alt = re.compile("|".join(re.escape(o) for o, _n, _c in ordered))
        mapping = {o: n for o, n, _c in ordered}
        cur, nsub = alt.subn(lambda m: mapping[m.group(0)], cur)
        assert nsub == sum(c for _o, _n, c in reps), key
        if key == "help.topic_sitemap_body":
            assert HREF_RE.findall(before_vals[key]) == HREF_RE.findall(cur), "sitemap href drift"
            assert cur.count("#/explorer/witnesses") == 1, "sitemap link drift"
        set_dig(d, key, cur)

    for key in list(FULL) + list(SNIPPETS):
        v = dig(d, key)
        if WITNESS_RE.search(v):
            print("FAIL: %s still carries a witness-family word: %r" % (key, v[:160]))
            return 1

    after_keys = set(flatten(d))
    if after_keys != before_keys:
        print("FAIL: key set drift")
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
        print("OK hi: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
