#!/usr/bin/env python3
"""Rename treasury worker -> grant proposal in vanilla/locales/ko.json.

Scope: ONLY values carrying the treasury-proposal sense (30 FULL + 6 snippet bodies). Keys unchanged.
Excluded by design (aborts if touched, reported, never rewritten):
  * placeholders (%(name)s, %(op)s stay byte-identical; code-bound).
  * code identifiers (get_all_workers in vote.hide_legacy_title stays).
  * route hashes (#/create-worker in sitemap + empty_hint stays).
  * file paths (js/ in backend-missing strings stays).
  * chrome with no worker word (daily_pay, work dates, pay_destination ...),
    help.topic_workers_text and menu.d_worker — untouched.

Compound (per brief, from dict's OWN attested words where possible): 그랜트 제안 / 그랜트 수혜자.
Pay keeps attested pay word (never transliterated pay); budget/funding keep attested words;
recipients (PEOPLE) use beneficiary word attested in referrals body, not proposals.

Safety gates: G1 current has worker-family word; G2 current == expected old
(FULL) or snippet counts (SNIPPETS); G3 placeholders/hrefs/identifiers kept;
G4 key set + _meta + untouched values; G5 formatting round-trip.

Usage: python3 tooling/rename_worker_grant_ko.py [--apply]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "vanilla", "locales", "ko.json")

WORKER_RE = re.compile(r"워커")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_worker_create": (
        "워커 생성",
        "그랜트 제안 생성",
    ),
    "account.sum_worker_create": (
        "워커 “%(name)s” 생성",
        "그랜트 제안 “%(name)s” 생성",
    ),
    "createworker.confirm_worker_op_34": (
        "워커 확인(op %(op)s)",
        "그랜트 제안 확인(op %(op)s)",
    ),
    "createworker.could_not_preview_the_worker": (
        "워커를 미리볼 수 없습니다.",
        "그랜트 제안를 미리볼 수 없습니다.",
    ),
    "createworker.create_worker": (
        "워커 생성",
        "그랜트 제안 생성",
    ),
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        "워커를 작성하십시오(op %(op)s). 미리보기는 실시간이며 검토 단계에서 실시간 수수료를 고지하고, 서명 및 전송하면 작업 %(op)s를 바로 브로드캐스트합니다 — 워커는 제안이 아니라 직접 작업으로 생성됩니다.",
        "그랜트 제안를 작성하십시오(op %(op)s). 미리보기는 실시간이며 검토 단계에서 실시간 수수료를 고지하고, 서명 및 전송하면 작업 %(op)s를 바로 브로드캐스트합니다 — 그랜트 제안는 제안이 아니라 직접 작업으로 생성됩니다.",
    ),
    "createworker.enter_a_worker_name": (
        "워커 이름을 입력하십시오.",
        "그랜트 제안 이름을 입력하십시오.",
    ),
    "createworker.owner_pays_the_fee_and_receives_the_": (
        "소유자가 수수료를 부담하고 워커 지급액을 받습니다 — 직접 관리하는 평생회원 계정을 사용하십시오.",
        "소유자가 수수료를 부담하고 그랜트 제안 지급액을 받습니다 — 직접 관리하는 평생회원 계정을 사용하십시오.",
    ),
    "createworker.preview_worker": (
        "워커 미리보기",
        "그랜트 제안 미리보기",
    ),
    "createworker.publishing_a_worker_requires_a_lifeti": (
        "워커를 게시하려면 평생회원 계정이 필요합니다 — 기본 계정은 이 수수료를 낼 수 없습니다. 아래 소유자가 이미 업그레이드되어 있어야 합니다.",
        "그랜트 제안를 게시하려면 평생회원 계정이 필요합니다 — 기본 계정은 이 수수료를 낼 수 없습니다. 아래 소유자가 이미 업그레이드되어 있어야 합니다.",
    ),
    "createworker.reading_existing_workers": (
        "기존 워커 읽는 중…",
        "기존 그랜트 제안 읽는 중…",
    ),
    "createworker.worker_backend_missing_js_account_js_or_js_fo": (
        "워커 백엔드를 사용할 수 없습니다. js/account.js 또는 js/format.js를 불러오지 못했습니다.",
        "그랜트 제안 백엔드를 사용할 수 없습니다. js/account.js 또는 js/format.js를 불러오지 못했습니다.",
    ),
    "createworker.worker_backend_missing_js_asset_ops_js_failed": (
        "워커 백엔드를 사용할 수 없습니다. js/asset-ops.js를 불러오지 못했습니다.",
        "그랜트 제안 백엔드를 사용할 수 없습니다. js/asset-ops.js를 불러오지 못했습니다.",
    ),
    "createworker.worker_name": (
        "워커 이름 ",
        "그랜트 제안 이름 ",
    ),
    "createworker.worker_preview_op_34": (
        "워커 미리보기(op %(op)s)",
        "그랜트 제안 미리보기(op %(op)s)",
    ),
    "help.topic_workers_title": (
        "워커",
        "그랜트 제안",
    ),
    "help.topic_voting_text": (
        "증인, 위원회 위원, 워커에 투표하십시오 — 또는 프록시에 위임하십시오.",
        "증인, 위원회 위원, 그랜트 제안에 투표하십시오 — 또는 프록시에 위임하십시오.",
    ),
    "menu.d_voting": (
        "증인, 위원회, 워커 및 프록시를 관리합니다.",
        "증인, 위원회, 그랜트 제안 및 프록시를 관리합니다.",
    ),
    "menu.p_worker": (
        "워커 생성",
        "그랜트 제안 생성",
    ),
    "news.voting_witnesses_committee_workers": (
        "투표 — 증인, 위원회, 워커",
        "투표 — 증인, 위원회, 그랜트 제안",
    ),
    "seo.desc_voting": (
        "BitShares 증인, 위원, 워커에 투표하십시오. 모든 투표는 기기에서 로컬 서명됩니다.",
        "BitShares 증인, 위원, 그랜트 제안에 투표하십시오. 모든 투표는 기기에서 로컬 서명됩니다.",
    ),
    "vote.ballot_intro": (
        "본인의 지분으로 증인과 위원회를 선출하고 워커에 자금을 보냅니다 — 아래의 모든 수치와 지분은 체인에서 실시간으로 읽은 값입니다.",
        "본인의 지분으로 증인과 위원회를 선출하고 그랜트 제안에 자금을 보냅니다 — 아래의 모든 수치와 지분은 체인에서 실시간으로 읽은 값입니다.",
    ),
    "vote.empty_hint": (
        " 체인이 해당 항목을 보유하면 표시됩니다 — 워커는 #/create-worker에서 제안됩니다.",
        " 체인이 해당 항목을 보유하면 표시됩니다 — 그랜트 제안는 #/create-worker에서 제안됩니다.",
    ),
    "vote.funding_unavailable_prefix": (
        "워커 자금을 사용할 수 없습니다(",
        "그랜트 제안 자금을 사용할 수 없습니다(",
    ),
    "vote.hide_legacy_label": (
        " 기존 제안을 숨깁니다(항상 켜짐 — 만료된 워커는 가져올 때 제외됨)",
        " 기존 제안을 숨깁니다(항상 켜짐 — 만료된 그랜트 제안는 가져올 때 제외됨)",
    ),
    "vote.hide_legacy_title": (
        "워커 목록은 get_all_workers(false)에서 가져오며 만료된 행은 수신되지 않습니다.",
        "그랜트 제안 목록은 get_all_workers(false)에서 가져오며 만료된 행은 수신되지 않습니다.",
    ),
    "vote.no_workers": (
        "워커가 없습니다. 테스트넷에는 종종 없습니다 — 이는 정상이며 오류가 아닙니다.",
        "그랜트 제안가 없습니다. 테스트넷에는 종종 없습니다 — 이는 정상이며 오류가 아닙니다.",
    ),
    "vote.tab_workers": (
        "워커(",
        "그랜트 제안(",
    ),
    "vote.worker_budget": (
        "워커 예산: —",
        "그랜트 제안 예산: —",
    ),
    "vote.worker_budget_loading": (
        "워커 예산: 불러오는 중입니다…",
        "그랜트 제안 예산: 불러오는 중입니다…",
    ),
}

SNIPPETS = {
    "help.topic_glossary_body": [
        ("워커는 유급 프로젝트를 수행하고", "그랜트 수혜자는 유급 프로젝트를 수행하고", 1,),
    ],
    "help.topic_sitemap_body": [
        ("워커", "그랜트 제안", 1,),
    ],
    "help.topic_tickets_body": [
        ("워커", "그랜트 제안", 1,),
    ],
    "help.topic_vesting_body": [
        ("워커", "그랜트 제안", 1,),
    ],
    "help.topic_voting_body": [
        ("워커", "그랜트 제안", 6,),
    ],
    "help.topic_workers_body": [
        ("워커", "그랜트 제안", 5,),
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
