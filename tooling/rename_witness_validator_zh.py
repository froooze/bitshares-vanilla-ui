#!/usr/bin/env python3
"""Rename "见证人" -> "区块验证者" in vanilla/locales/zh.json.

Scope: ONLY the 38 block-producer keys (27 short + 11 long bodies).
Keys unchanged. Excluded by design (aborts if touched, never rewritten):
  * placeholders — %(account)s / %(op)s stay byte-identical.
  * route targets — "#/explorer/witnesses" stays (router path, code).
  * key names (*witness*, topic_witnesses_*) stay (code).
  * the DEFINITIONS 区块生产者 / 出块者 stay — they gloss the office.
  * bare 见证 (witnessing, not the office) never appears here; never use it.

Compound (per brief, from the locale's OWN attested words): 区块验证者 —
block 区块 (86 keys) + validate 验证 (20 keys, e.g. gateway.validate_btn)
+ agent 者 (生产者 19 keys, 出块者 2 keys). No spaces, mirroring 见证人.
Hyphen "见证人喂价" renders as 区块验证者喂价 (mirrored concatenation);
"作为见证人加入" keeps the becoming-member action; "无见证人对象" keeps
technical precision; tab headers stay short but explicit.

Safety gates (assert before write):
  G1 every target's CURRENT value contains 见证人, else abort.
  G2 every FULL target's current value EQUALS the expected old string.
  G3 every snippet occurs exactly its expected count.
  G4 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged.
  G5 key set + _meta deep-equal before/after; non-target values untouched.
  G6 json.dumps(indent=2, ensure_ascii=False)+"\\n" formatting.

Usage: python3 tooling/rename_witness_validator_zh.py [--apply]
Dry run (asserts only) by default; --apply writes zh.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOC = os.path.join(HERE, "..", "vanilla", "locales", "zh.json")

WITNESS_RE = re.compile(r"见证人")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {'account.op_witness_join': ('加入见证人', '加入区块验证者'),
 'account.op_witness_update': ('见证人更新', '区块验证者更新'),
 'account.sum_witness_create': ('已成为见证人：%(account)s', '已成为区块验证者：%(account)s'),
 'account.sum_witness_update': ('已更新见证人 %(account)s', '已更新区块验证者 %(account)s'),
 'asset.witness_fed_note': ('见证人喂价：所有活跃见证人均可发布。', '区块验证者喂价：所有活跃区块验证者均可发布。'),
 'explorer.stat_wit': ('活跃见证人', '活跃区块验证者'),
 'explorer.th_witness': ('见证人', '区块验证者'),
 'explorer.witness_row': ('见证人', '区块验证者'),
 'help.topic_assets-mpa_text': ('由抵押物支撑、见证人提供价格源的智能币。', '由抵押物支撑、区块验证者提供价格源的智能币。'),
 'help.topic_glossary_text': ('本钱包通用名称：对象 (1.x.y)、操作、见证人、理事会。', '本钱包通用名称：对象 (1.x.y)、操作、区块验证者、理事会。'),
 'help.topic_voting_text': ('为见证人、理事会、资助提案投票——也可交给代理。', '为区块验证者、理事会、资助提案投票——也可交给代理。'),
 'help.topic_witnesses_title': ('见证人', '区块验证者'),
 'menu.d_asset_feed': ('作为发行者或见证人发布价格喂价。', '作为发行者或区块验证者发布价格喂价。'),
 'menu.d_voting': ('见证人、理事会、资助提案与代理。', '区块验证者、理事会、资助提案与代理。'),
 'news.voting_witnesses_committee_workers': ('投票 — 见证人、理事会、资助提案', '投票 — 区块验证者、理事会、资助提案'),
 'seo.desc_voting': ('为 BitShares 见证人、理事会成员与资助提案投票。每一张选票都在您的设备本地签名。',
                     '为 BitShares 区块验证者、理事会成员与资助提案投票。每一张选票都在您的设备本地签名。'),
 'seo.title_voting': ('见证人投票 — BitShares 钱包', '区块验证者投票 — BitShares 钱包'),
 'splash.pulse_witnesses': ('见证人', '区块验证者'),
 'vote.ballot_intro': ('您的质押选出见证人与理事会，并为资助提案提供资金 — 下方所有计数与份额都是实时链上读取。',
                       '您的质押选出区块验证者与理事会，并为资助提案提供资金 — 下方所有计数与份额都是实时链上读取。'),
 'vote.confirm_witness_update_op_21': ('确认见证人更新（op %(op)s）', '确认区块验证者更新（op %(op)s）'),
 'vote.empty_list': ('节点未返回见证人与理事会成员。', '节点未返回区块验证者与理事会成员。'),
 'vote.join_as_witness': ('作为见证人加入', '作为区块验证者加入'),
 'vote.no_witness_object_for_this_account_use_join_a': ('该账户无见证人对象——请改用“作为见证人加入”。',
                                                        '该账户无区块验证者对象——请改用“作为区块验证者加入”。'),
 'vote.tab_witnesses': ('见证人 (', '区块验证者 ('),
 'vote.update_witness': ('更新见证人', '更新区块验证者'),
 'vote.witness': ('见证人', '区块验证者'),
 'vote.witness_updated': ('见证人已更新', '区块验证者已更新')}

SNIPPETS = {'help.topic_assets-mpa_body': [('见证人', '区块验证者', 1)],
 'help.topic_assets-private_body': [('见证人', '区块验证者', 3)],
 'help.topic_blockchain_body': [('见证人', '区块验证者', 3)],
 'help.topic_committee_body': [('见证人', '区块验证者', 1)],
 'help.topic_dex-shorting_body': [('见证人', '区块验证者', 1)],
 'help.topic_glossary_body': [('见证人', '区块验证者', 2)],
 'help.topic_settings_body': [('见证人', '区块验证者', 1)],
 'help.topic_sitemap_body': [('见证人', '区块验证者', 1)],
 'help.topic_tickets_body': [('见证人', '区块验证者', 1)],
 'help.topic_voting_body': [('见证人', '区块验证者', 4)],
 'help.topic_witnesses_body': [('见证人', '区块验证者', 3)]}


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
        print("OK zh: %d full + %d snippet keys renamed" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK zh: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
