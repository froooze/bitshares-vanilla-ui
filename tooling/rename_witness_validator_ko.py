#!/usr/bin/env python3
"""Rename "증인" -> "블록 검증자" in vanilla/locales/ko.json.

Scope: ONLY the 38 block-producer keys (27 short + 11 long bodies).
Keys unchanged. Excluded by design (aborts if touched, never rewritten):
  * placeholders — %(account)s / %(op)s stay byte-identical.
  * route targets — "#/explorer/witnesses" stays (router path, code).
  * key names (*witness*, topic_witnesses_*) stay (code).
  * the DEFINITION "블록 생성자" stays — it glosses the office, not the term.

Compound (per brief, from the locale's OWN attested words): 블록 검증자 —
block 블록 (83 keys) + validate 검증 (19 keys, e.g. gateway.validate_btn)
+ agent 자 (발행자 32 keys, 생산자 16 keys). Spaced compound, mirroring
"블록 생성자". The loanword 밸리데 is unattested (0 strings).

Particles re-agree after the vowel-final 검증자 (consonant-final 증인 took
이/은/으로/으로서/이라/과; vowel-final takes 가/는/로/로서/라/와) — same
class of fix as the ticket pass, in reverse:
  증인이->블록 검증자가, 증인은->블록 검증자는, 증인과->블록 검증자와,
  증인으로->블록 검증자로, 증인으로서->블록 검증자로서,
  증인이라->블록 검증자라, 증인처럼->블록 검증자처럼;
  증인의/증인에 keep their particles. Bare noun (tabs, headers, comma-joined
  lists, sitemap label) maps plainly.

Safety gates (assert before write):
  G1 every target's CURRENT value contains 증인, else abort.
  G2 every FULL target's current value EQUALS the expected old string.
  G3 every snippet occurs exactly its expected count.
  G4 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged.
  G5 key set + _meta deep-equal before/after; non-target values untouched.
  G6 json.dumps(indent=2, ensure_ascii=False)+"\\n" formatting.

Usage: python3 tooling/rename_witness_validator_ko.py [--apply]
Dry run (asserts only) by default; --apply writes ko.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOC = os.path.join(HERE, "..", "vanilla", "locales", "ko.json")

WITNESS_RE = re.compile(r"증인")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {'account.op_witness_join': ('증인 참여', '블록 검증자 참여'),
 'account.op_witness_update': ('증인 업데이트', '블록 검증자 업데이트'),
 'account.sum_witness_create': ('증인이 되었습니다: %(account)s', '블록 검증자가 되었습니다: %(account)s'),
 'account.sum_witness_update': ('증인 %(account)s 업데이트됨', '블록 검증자 %(account)s 업데이트됨'),
 'asset.witness_fed_note': ('증인 피드: 활성 상태인 모든 증인이 게시할 수 있습니다.',
                            '블록 검증자 피드: 활성 상태인 모든 블록 검증자가 게시할 수 있습니다.'),
 'explorer.stat_wit': ('활성 증인', '활성 블록 검증자'),
 'explorer.th_witness': ('증인', '블록 검증자'),
 'explorer.witness_row': ('증인', '블록 검증자'),
 'help.topic_assets-mpa_text': ('증인의 가격 피드로 담보되는 스마트코인.', '블록 검증자의 가격 피드로 담보되는 스마트코인.'),
 'help.topic_glossary_text': ('이 지갑에서 사용하는 이름: 객체(1.x.y), 작업, 증인, 위원회.',
                              '이 지갑에서 사용하는 이름: 객체(1.x.y), 작업, 블록 검증자, 위원회.'),
 'help.topic_voting_text': ('증인, 위원회 위원, 그랜트 제안에 투표하십시오 — 또는 프록시에 위임하십시오.',
                            '블록 검증자, 위원회 위원, 그랜트 제안에 투표하십시오 — 또는 프록시에 위임하십시오.'),
 'help.topic_witnesses_title': ('증인', '블록 검증자'),
 'menu.d_asset_feed': ('발행자 또는 증인으로서 가격 피드를 게시합니다.', '발행자 또는 블록 검증자로서 가격 피드를 게시합니다.'),
 'menu.d_voting': ('증인, 위원회, 그랜트 제안 및 프록시를 관리합니다.', '블록 검증자, 위원회, 그랜트 제안 및 프록시를 관리합니다.'),
 'news.voting_witnesses_committee_workers': ('투표 — 증인, 위원회, 그랜트 제안', '투표 — 블록 검증자, 위원회, 그랜트 제안'),
 'seo.desc_voting': ('BitShares 증인, 위원, 그랜트 제안에 투표하십시오. 모든 투표는 기기에서 로컬 서명됩니다.',
                     'BitShares 블록 검증자, 위원, 그랜트 제안에 투표하십시오. 모든 투표는 기기에서 로컬 서명됩니다.'),
 'seo.title_voting': ('증인 투표 — BitShares 지갑', '블록 검증자 투표 — BitShares 지갑'),
 'splash.pulse_witnesses': ('증인', '블록 검증자'),
 'vote.ballot_intro': ('본인의 지분으로 증인과 위원회를 선출하고 그랜트 제안에 자금을 보냅니다 — 아래의 모든 수치와 지분은 체인에서 실시간으로 읽은 '
                       '값입니다.',
                       '본인의 지분으로 블록 검증자와 위원회를 선출하고 그랜트 제안에 자금을 보냅니다 — 아래의 모든 수치와 지분은 체인에서 실시간으로 읽은 '
                       '값입니다.'),
 'vote.confirm_witness_update_op_21': ('증인 업데이트 확인(op %(op)s)', '블록 검증자 업데이트 확인(op %(op)s)'),
 'vote.empty_list': ('노드가 증인 또는 위원회 위원을 반환하지 않았습니다.', '노드가 블록 검증자 또는 위원회 위원을 반환하지 않았습니다.'),
 'vote.join_as_witness': ('증인으로 참여', '블록 검증자로 참여'),
 'vote.no_witness_object_for_this_account_use_join_a': ('이 계정에 대한 증인 오브젝트가 없습니다 — 대신 증인 참여를 '
                                                        '사용하십시오.',
                                                        '이 계정에 대한 블록 검증자 오브젝트가 없습니다 — 대신 블록 검증자 '
                                                        '참여를 사용하십시오.'),
 'vote.tab_witnesses': ('증인(', '블록 검증자('),
 'vote.update_witness': ('증인 업데이트', '블록 검증자 업데이트'),
 'vote.witness': ('증인', '블록 검증자'),
 'vote.witness_updated': ('증인이 업데이트되었습니다', '블록 검증자가 업데이트되었습니다')}

SNIPPETS = {'help.topic_assets-mpa_body': [('증인은', '블록 검증자는', 1)],
 'help.topic_assets-private_body': [('증인이', '블록 검증자가', 2), ('증인', '블록 검증자', 1)],
 'help.topic_blockchain_body': [('증인이라', '블록 검증자라', 1), ('증인의', '블록 검증자의', 1), ('증인', '블록 검증자', 1)],
 'help.topic_committee_body': [('증인처럼', '블록 검증자처럼', 1)],
 'help.topic_dex-shorting_body': [('증인이', '블록 검증자가', 1)],
 'help.topic_glossary_body': [('증인은', '블록 검증자는', 1), ('증인', '블록 검증자', 1)],
 'help.topic_settings_body': [('증인', '블록 검증자', 1)],
 'help.topic_sitemap_body': [('증인', '블록 검증자', 1)],
 'help.topic_tickets_body': [('증인', '블록 검증자', 1)],
 'help.topic_voting_body': [('증인은', '블록 검증자는', 1), ('증인', '블록 검증자', 3)],
 'help.topic_witnesses_body': [('증인은', '블록 검증자는', 1), ('증인의', '블록 검증자의', 1), ('증인에', '블록 검증자에', 1)]}


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
        print("OK ko: %d full + %d snippet keys renamed" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK ko: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
