#!/usr/bin/env python3
"""Rename treasury worker -> grant proposal in vanilla/locales/tr.json.

Scope: ONLY values carrying the treasury-proposal sense (30 FULL + snippet bodies). Keys unchanged.
Excluded by design (aborts if touched, reported, never rewritten):
  * placeholders (%(name)s, %(op)s stay byte-identical; code-bound).
  * code identifiers (get_all_workers in vote.hide_legacy_title stays).
  * route hashes (#/create-worker in sitemap + empty_hint stays).
  * file paths (js/ in backend-missing strings stays).
  * chrome with no worker word (daily_pay, work dates, pay_destination ...),
    help.topic_workers_text and menu.d_worker — untouched.

Compound: hibe önerisi (sing) / hibe önerileri (plur) / hibe yararlanıcıları (recipients). Pay: ödeme/ücret attested; budget bütçe, funding fonlama attested.
Pay keeps attested pay word; budget/funding keep attested words; recipients use beneficiary word.

Safety gates: G1 current has worker-family word; G2 current == expected old
(FULL) or snippet counts (SNIPPETS); G3 placeholders/hrefs/identifiers kept;
G4 key set + _meta + untouched values; G5 formatting round-trip.

Usage: python3 tooling/rename_worker_grant_tr.py [--apply]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "vanilla", "locales", "tr.json")

WORKER_RE = re.compile(r"çalışan", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_worker_create": (
        "Çalışan oluşturma",
        "Hibe önerisi oluşturma",
    ),
    "account.sum_worker_create": (
        "“%(name)s” adlı çalışan oluşturuldu",
        "“%(name)s” adlı hibe önerisi oluşturuldu",
    ),
    "createworker.confirm_worker_op_34": (
        "Çalışanı onayla (op %(op)s)",
        "Hibe önerisini onayla (op %(op)s)",
    ),
    "createworker.could_not_preview_the_worker": (
        "Çalışan önizlenemedi.",
        "Hibe önerisi önizlenemedi.",
    ),
    "createworker.create_worker": (
        "Çalışan Oluştur",
        "Hibe Önerisi Oluştur",
    ),
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        "Bir çalışan taslağı oluşturun (op %(op)s). Önizleme canlıdır; inceleme canlı ücreti verir, ardından İmzala ve Gönder op %(op)s işlemini doğrudan yayınlar — çalışanlar doğrudan işlemle oluşturulur, öneriyle değil.",
        "Bir hibe önerisi taslağı oluşturun (op %(op)s). Önizleme canlıdır; inceleme canlı ücreti verir, ardından İmzala ve Gönder op %(op)s işlemini doğrudan yayınlar — hibe önerileri doğrudan işlemle oluşturulur, öneriyle değil.",
    ),
    "createworker.enter_a_worker_name": (
        "Bir çalışan adı girin.",
        "Bir hibe önerisi adı girin.",
    ),
    "createworker.owner_pays_the_fee_and_receives_the_": (
        "Sahip ücreti öder ve çalışan ödemesini alır — kontrol ettiğiniz ömür boyu üye bir hesap kullanın.",
        "Sahip ücreti öder ve hibe önerisi ödemesini alır — kontrol ettiğiniz ömür boyu üye bir hesap kullanın.",
    ),
    "createworker.preview_worker": (
        "Çalışanı önizle",
        "Hibe önerisini önizle",
    ),
    "createworker.publishing_a_worker_requires_a_lifeti": (
        "Çalışan yayınlamak ömür boyu üye hesap gerektirir — temel hesaplar bu ücreti ödeyemez. Aşağıdaki sahip zaten yükseltilmiş olmalı.",
        "Hibe önerisi yayınlamak ömür boyu üye hesap gerektirir — temel hesaplar bu ücreti ödeyemez. Aşağıdaki sahip zaten yükseltilmiş olmalı.",
    ),
    "createworker.reading_existing_workers": (
        "Mevcut çalışanlar okunuyor…",
        "Mevcut hibe önerileri okunuyor…",
    ),
    "createworker.worker_backend_missing_js_account_js_or_js_fo": (
        "Çalışan arka ucu eksik: js/account.js veya js/format.js yüklenemedi.",
        "Hibe önerisi arka ucu eksik: js/account.js veya js/format.js yüklenemedi.",
    ),
    "createworker.worker_backend_missing_js_asset_ops_js_failed": (
        "Çalışan arka ucu eksik: js/asset-ops.js yüklenemedi.",
        "Hibe önerisi arka ucu eksik: js/asset-ops.js yüklenemedi.",
    ),
    "createworker.worker_name": (
        "Çalışan adı ",
        "Hibe önerisi adı ",
    ),
    "createworker.worker_preview_op_34": (
        "Çalışan önizlemesi (op %(op)s)",
        "Hibe önerisi önizlemesi (op %(op)s)",
    ),
    "help.topic_workers_title": (
        "Çalışanlar",
        "Hibe önerileri",
    ),
    "help.topic_voting_text": (
        "Tanıklara, komiteye ve çalışanlara oy verin — ya da vekile devredin.",
        "Tanıklara, komiteye ve hibe önerilerine oy verin — ya da vekile devredin.",
    ),
    "menu.d_voting": (
        "Tanıklar, komite, çalışanlar ve vekiller.",
        "Tanıklar, komite, hibe önerileri ve vekiller.",
    ),
    "menu.p_worker": (
        "Çalışan Oluştur",
        "Hibe Önerisi Oluştur",
    ),
    "news.voting_witnesses_committee_workers": (
        "Oylama — tanıklar, komite, çalışanlar",
        "Oylama — tanıklar, komite, hibe önerileri",
    ),
    "seo.desc_voting": (
        "BitShares tanıklarına, komite üyelerine ve çalışanlara oy verin. Her oy pusulası cihazınızda yerel olarak imzalanır.",
        "BitShares tanıklarına, komite üyelerine ve hibe önerilerine oy verin. Her oy pusulası cihazınızda yerel olarak imzalanır.",
    ),
    "vote.ballot_intro": (
        "Hakedişiniz tanıkları ve komiteyi seçer, çalışanların bütçesini oluşturur — aşağıdaki tüm sayılar ve paylar canlı zincir okumalarıdır.",
        "Hakedişiniz tanıkları ve komiteyi seçer, hibe önerilerinin bütçesini oluşturur — aşağıdaki tüm sayılar ve paylar canlı zincir okumalarıdır.",
    ),
    "vote.empty_hint": (
        " Zincir taşıdığında kayıtlar görünür — çalışanlar #/create-worker adresinden önerilir.",
        " Zincir taşıdığında kayıtlar görünür — hibe önerileri #/create-worker adresinden önerilir.",
    ),
    "vote.funding_unavailable_prefix": (
        "Çalışan fonlama yok (",
        "Hibe önerisi fonlama yok (",
    ),
    "vote.hide_legacy_label": (
        " Eski önerileri gizle (her zaman açık — süresi dolmuş çalışanlar çekilirken elenir)",
        " Eski önerileri gizle (her zaman açık — süresi dolmuş hibe önerileri çekilirken elenir)",
    ),
    "vote.hide_legacy_title": (
        "Çalışan listeleri get_all_workers(false) ile gelir; süresi dolmuş satırlar hiç ulaşmaz.",
        "Hibe önerisi listeleri get_all_workers(false) ile gelir; süresi dolmuş satırlar hiç ulaşmaz.",
    ),
    "vote.no_workers": (
        "Çalışan bulunamadı. Testnetlerde genelde yoktur — bu geçerlidir, hata değildir.",
        "Hibe önerisi bulunamadı. Testnetlerde genelde yoktur — bu geçerlidir, hata değildir.",
    ),
    "vote.tab_workers": (
        "Çalışanlar (",
        "Hibe önerileri (",
    ),
    "vote.worker_budget": (
        "Çalışan bütçesi: —",
        "Hibe önerisi bütçesi: —",
    ),
    "vote.worker_budget_loading": (
        "Çalışan bütçesi: yükleniyor…",
        "Hibe önerisi bütçesi: yükleniyor…",
    ),
}

SNIPPETS = {
    "help.topic_glossary_body": [
        ("çalışanlar ücretli projeler sunar", "hibe yararlanıcıları ücretli projeler sunar", 1,),
    ],
    "help.topic_sitemap_body": [
        ("- [Çalışan Oluştur](#/create-worker)", "- [Hibe Önerisi Oluştur](#/create-worker)", 1,),
    ],
    "help.topic_tickets_body": [
        ("tanık, komite ve çalışan oylarını besler", "tanık, komite ve hibe önerisi oylarını besler", 1,),
    ],
    "help.topic_vesting_body": [
        ("çalışan ücretleri, yönlendirme ödülleri", "hibe önerisi ücretleri, yönlendirme ödülleri", 1,),
    ],
    "help.topic_voting_body": [
        ("ve hangi çalışan projelerin ödeneceğini seçer.", "ve hangi hibe önerisi projelerin ödeneceğini seçer.", 1,),
        ("veya çalışanlara doğrudan oy veremezsiniz.", "veya hibe önerilerine doğrudan oy veremezsiniz.", 1,),
        ("# Çalışanlar ve bütçe", "# Hibe önerileri ve bütçe", 1,),
        ("Çalışanlar, iade çalışanını oyla geçip", "Hibe önerileri, iade hibe önerisini oyla geçip", 1,),
        ("Tüm ayrıntı Çalışanlar makalesinde.", "Tüm ayrıntı Hibe Önerileri makalesinde.", 1,),
    ],
    "help.topic_workers_body": [
        ("Çalışanlar yararlı bir şey yapma önerileridir", "Hibe önerileri yararlı bir şey yapma önerileridir", 1,),
        ("Önerilen çalışanlar oy toplar.", "Önerilen hibe önerileri oy toplar.", 1,),
        ("iade çalışanını oyla geçince aktif olur", "iade hibe önerisini oyla geçince aktif olur", 1,),
        ("Tüm çalışanlar tek sabit günlük bütçeyi paylaşır", "Tüm hibe önerileri tek sabit günlük bütçeyi paylaşır", 1,),
        ("üst sıradaki çalışanlar günün fonunu tüketince", "üst sıradaki hibe önerileri günün fonunu tüketince", 1,),
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
