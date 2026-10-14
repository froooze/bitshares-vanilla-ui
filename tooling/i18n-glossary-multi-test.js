/* i18n-glossary-multi-test: docs/i18n-glossary/{de,ko,hi,tr}.md are the
 * artifacts an external auditor reads BEFORE trusting a machine-filled German,
 * Korean, Hindi or Turkish translation. Every claim in them is checked against
 * the shipped vanilla/locales/<code>.json rather than trusted.
 *
 * tooling/i18n-glossary-test.js does this for es.md and
 * tooling/i18n-glossary-it-test.js for it.md; this is the multi-locale twin,
 * one pass over the four remaining glossaries. Same five rules:
 *   1. structure — one markdown table, three columns, every cell filled, one row
 *      per English term, and every one of the 26 required BitShares terms is a
 *      ROW (matched on the English cell exactly, so a term cannot be "covered"
 *      by a passing mention in prose);
 *   2. one <locale> term per concept — no synonym split;
 *   3. every `key` a note cites EXISTS in the dictionary, and unless the note
 *      marks it a counter-example or a same-root other sense, its value really
 *      carries the agreed word;
 *   4. every count a note quotes is REAL — the COUNTS table below names the
 *      literal string each quoted count is about, because a count is of the
 *      agreed <LOCALE> word, which is not derivable from the English term
 *      ("limit order" counts "지정가 주문", not "주문"), and every "N strings"
 *      number in the prose must be one of that row's asserted counts;
 *   5. every `Counter-example form:` set is COMPLETE and MINORITY — the defect
 *      this file exists to prevent is a row mandating a word the shipped
 *      dictionary mostly does not use, or rejecting a form without naming every
 *      string that carries it, because an auditor following the file would
 *      rewrite a dozen correct strings.
 *
 * Word matching is Unicode-aware (lookbehind on any letter/digit, then the word
 * plus a letter/digit tail), because `\b` is ASCII-only and would silently fail
 * to find "지갑" or "स्टेक" inside a Korean or Devanagari sentence.
 *
 * Runs: node tooling/i18n-glossary-multi-test.js (exit 0 = green). */
var fs = require("fs"), path = require("path"), assert = require("assert");
var ROOT = path.join(__dirname, "..");

var REQUIRED = ["brainkey","witness","committee","worker","proxy","vesting","HTLC","swap","slate",
  "liquidity pool","credit offer","ticket","proposal","precision","orderbook","limit order","fee",
  "account","asset","smartcoin","collateral","balance","share","market","block","transaction"];

/* COUNTS: english term -> [ [string, n], ... ]. Each pair asserts that `n`
 * translated keys of that locale contain `string`. The table lives here, where
 * a reviewer sees it, because the number in a note is about a word that only
 * the note itself names. */
var SPEC = {
  de: {
    word: "german",
    COUNTS: {
      "wallet": [["Wallet",190]], "account": [["Konto",247]], "asset": [["Asset",269]],
      "balance": [["Saldo",20],["Guthaben",14]],
      "claim": [["Claim",20],["Balance",7]],
      "smartcoin": [["Smartcoin",21]], "collateral": [["Sicherheiten",34]],
      "precision": [["Präzision",16]], "share": [["Anteil",23]],
      "liquidity pool": [["Liquiditätspool",9],["Pool",108]],
      "pool share": [["LP-Anteil",3]], "stake": [["Stake",23]],
      "market": [["Markt",115]], "exchange": [["Börse",31]], "desk": [["Desk",47]],
      "swap": [["Swap",39]], "orderbook": [["Orderbuch",15]], "limit order": [["Limit-Order",10]],
      "order": [["Order",117]], "operation": [["Operation",64]], "fee": [["Gebühr",134]],
      "transaction": [["Transaktion",66]], "block": [["Block",58]], "memo": [["Memo",37]],
      "brainkey": [["Brainkey",41]], "witness": [["Zeuge",38]], "committee": [["Komitee",24]],
      "worker": [["Worker",36],["Arbeiter",0]],
      "proxy": [["Proxy",21]], "slate": [["Slate",4]],
      "vesting": [["Vesting",41]], "proposal": [["Vorschlag",86]],
      "credit offer": [["Kreditangebot",18]], "deal": [["Deal",28]], "ticket": [["Ticket",27],["Fahrschein",0]],
      "HTLC": [["HTLC",24]], "gateway": [["Gateway",28]], "node": [["Knoten",66]],
      "chain": [["Chain",130]], "authority": [["Authority",15],["Autorität",10]],
      "issuer": [["Emittent",29]], "producer": [["Produzent",18]],
      "publisher": [["Herausgeber",7]], "settle": [["Settlement",46],["Abwicklung",0],["Rückführung",0]],
      "referral": [["Empfehlung",8]], "quote": [["Quote",35]], "lock": [["Lock",8],["Sperre",16]],
      "prediction": [["Prognosemarkt",11]], "borrow": [["Leihen",29]]
    }
  },
  ko: {
    word: "korean",
    COUNTS: {
      "wallet": [["지갑",189]], "account": [["계정",298]], "asset": [["자산",290]],
      "balance": [["잔액",76]], "claim": [["청구",14]],
      "smartcoin": [["스마트코인",22]], "collateral": [["담보",46]],
      "precision": [["정밀도",17]], "share": [["지분",20]],
      "liquidity pool": [["유동성 풀",12],["풀",126]],
      "pool share": [["LP 지분",3]], "stake": [["스테이크",20]],
      "market": [["시장",180]], "exchange": [["거래소",30]], "desk": [["데스크",44]],
      "swap": [["스왑",43]], "orderbook": [["호가창",28]], "limit order": [["지정가 주문",9]],
      "order": [["주문",113]], "operation": [["작업",78]], "fee": [["수수료",183]],
      "transaction": [["트랜잭션",68]], "block": [["블록",83]], "memo": [["메모",41]],
      "brainkey": [["브레인키",42]], "witness": [["증인",38]], "committee": [["위원회",23]],
      "worker": [["워커",36]], "proxy": [["프록시",23]], "slate": [["슬레이트",7]],
      "vesting": [["베스팅",50]], "proposal": [["제안",166]],
      "credit offer": [["신용 제안",18]], "deal": [["딜",7]], "ticket": [["티켓",34]],
      "HTLC": [["HTLC",24]], "gateway": [["게이트웨이",28]], "node": [["노드",67]],
      "chain": [["체인",98]], "authority": [["권한",67]],
      "issuer": [["발행자",32]], "producer": [["생산자",16]],
      "publisher": [["발행자",6]], "settle": [["정산",59]],
      "referral": [["추천인",9]], "lock": [["잠금",110]], "prediction": [["예측",29]],
      "borrow": [["대출",32]]
    }
  },
  hi: {
    word: "hindi",
    COUNTS: {
      "wallet": [["वॉलेट",189]], "account": [["खाता",228]], "asset": [["एसेट",276]],
      "balance": [["बैलेंस",75]], "claim": [["दावा",17]],
      "smartcoin": [["स्मार्टकॉइन",23]], "collateral": [["कोलैटरल",45]],
      "precision": [["परिशुद्धता",17]], "share": [["शेयर",20]],
      "liquidity pool": [["तरलता पूल",10],["पूल",125]],
      "pool share": [["LP शेयर",3]], "stake": [["स्टेक",26]],
      "market": [["मार्केट",178]], "exchange": [["एक्सचेंज",38]], "desk": [["डेस्क",45]],
      "swap": [["स्वैप",44]], "orderbook": [["ऑर्डर बुक",17]], "limit order": [["लिमिट ऑर्डर",10]],
      "order": [["ऑर्डर",123]], "operation": [["ऑपरेशन",73]], "fee": [["शुल्क",191]],
      "transaction": [["लेनदेन",68]], "block": [["ब्लॉक",86]], "memo": [["मेमो",40]],
      "brainkey": [["ब्रेनकी",42]], "witness": [["विटनेस",38]], "committee": [["कमेटी",24]],
      "worker": [["वर्कर",36]], "proxy": [["प्रॉक्सी",23]], "slate": [["स्लेट",7]],
      "vesting": [["वेस्टिंग",45]], "proposal": [["प्रस्ताव",145]],
      "credit offer": [["क्रेडिट ऑफ़र",11]], "deal": [["डील",15]], "ticket": [["टिकट",34]],
      "HTLC": [["HTLC",24]], "gateway": [["गेटवे",28]], "node": [["नोड",64]],
      "chain": [["चेन",133]], "authority": [["प्राधिकरण",22]],
      "issuer": [["जारीकर्ता",29]], "producer": [["उत्पादक",20]],
      "publisher": [["प्रकाशक",9]], "settle": [["सेटल",60]],
      "referral": [["रेफ़रल",8]], "lock": [["लॉक",159]], "prediction": [["प्रेडिक्शन",19]],
      "borrow": [["उधार",62]], "community": [["कम्युनिटी",15]]
    }
  },
  tr: {
    word: "turkish",
    COUNTS: {
      "wallet": [["cüzdan",189]], "account": [["hesap",231]], "asset": [["varlık",223]],
      "balance": [["bakiye",75]], "claim": [["talep",21]],
      "smartcoin": [["Akıllı para",23]], "collateral": [["teminat",43]],
      "precision": [["Hassasiyet",10]], "share": [["pay",55]],
      "liquidity pool": [["Likidite havuz",12],["havuz",124]],
      "pool share": [["LP pay",3]], "stake": [["stake",19]],
      "market": [["piyasa",179]], "exchange": [["borsa",34]], "desk": [["Masa",45]],
      "swap": [["takas",59]], "orderbook": [["emir defteri",14]], "limit order": [["limit emir",8]],
      "order": [["emir",112]], "operation": [["işlem",160]], "fee": [["ücret",190]],
      "transaction": [["işlem",160]], "block": [["blok",84]], "memo": [["Not",34]],
      "brainkey": [["Beyin anahtarı",42]], "witness": [["tanık",36]], "committee": [["komite",24]],
      "worker": [["Çalışan",41]], "proxy": [["vekil",23]], "slate": [["oylama listesi",3]],
      "vesting": [["Hakediş",50]], "proposal": [["öneri",108]],
      "credit offer": [["Kredi Teklifi",11]], "deal": [["anlaşma",4]], "ticket": [["bilet",34]],
      "HTLC": [["HTLC",24]], "gateway": [["geçit",27]], "node": [["düğüm",65]],
      "chain": [["zincir",136]], "authority": [["yetki",53]],
      "issuer": [["ihraççı",23]], "producer": [["üretici",20]],
      "publisher": [["yayınlayıcı",9]], "settle": [["uzlaşma",50]],
      "referral": [["Yönlendirme",6]], "lock": [["kilit",90]], "prediction": [["Tahmin",50]],
      "borrow": [["Ödünç",30]], "broadcast": [["yayımlandı",14]], "publish": [["yayınlandı",12]]
    }
  }
};

function flat(d, p, o) {
  p = p || ""; o = o || {};
  Object.keys(d).forEach(function (k) {
    if (k === "_meta") return;
    if (d[k] && typeof d[k] === "object") flat(d[k], p + k + ".", o);
    else o[p + k] = d[k];
  });
  return o;
}
var enValues = flat(JSON.parse(fs.readFileSync(path.join(ROOT, "vanilla/locales/en.json"), "utf8")));

function loadLocale(code) {
  var values = flat(JSON.parse(fs.readFileSync(path.join(ROOT, "vanilla/locales/" + code + ".json"), "utf8")));
  /* A stub is a value byte-equal to the English master — an honest unverified
   * copy that says nothing about this locale's vocabulary. Only a value that
   * DIFFERS from English is a claim about wording, so only those are counted. */
  var all = Object.keys(values).filter(function (k) {
    return typeof values[k] === "string" && values[k] !== enValues[k];
  }).sort();
  return { values: values, all: all };
}
/* uses: translated keys whose text contains `word` at a Unicode word boundary,
 * inflections included ("Gebühr" finds Gebühren, "varlık" finds varlıklar). */
function uses(all, values, word) {
  var re = new RegExp("(?<![\\p{L}\\p{N}])" + String(word).replace(/[.*+?^${}()|[\]\\]/g, "\\$&") +
    "[\\p{L}\\p{N}]*", "iu");
  return all.filter(function (k) { return re.test(values[k]); });
}
/* head word of the locale term, plural-tolerant: the check that an evidence
 * citation really carries the agreed word looks at the first space-separated
 * token, so an inflected second word cannot read as drift. */
function headWord(term) {
  var head = String(term).split(" ")[0].toLowerCase();
  return head.length > 4 && head.charAt(head.length - 1) === "s" ? head.slice(0, -1) : head;
}

var totalRows = 0, totalCitations = 0, totalRejects = 0;
Object.keys(SPEC).forEach(function (code) {
  var spec = SPEC[code];
  var FILE = path.join(ROOT, "docs/i18n-glossary/" + code + ".md");
  var glossary = fs.readFileSync(FILE, "utf8");
  var dict = loadLocale(code);

  /* --- structure ------------------------------------------------------- */
  function cells(l) {
    var s = l.trim();
    if (s.charAt(0) !== "|" || s.charAt(s.length - 1) !== "|") return null;
    return s.slice(1, -1).split("|").map(function (c) { return c.trim(); });
  }
  var rows = [];
  glossary.split(/\r?\n/).forEach(function (l) {
    var c = cells(l);
    if (!c || c.length !== 3) return;
    if (/^-+$/.test(c[0].replace(/\s/g, ""))) return;
    rows.push(c);
  });
  var header = rows.shift();
  assert.deepStrictEqual(header.map(function (h) { return h.toLowerCase(); }),
    ["english term", spec.word + " term", "note"],
    code + ".md names its three columns (English | " + spec.word + " | note)");

  var byEn = {};
  rows.forEach(function (r) {
    var e = r[0].toLowerCase();
    assert.ok(!byEn[e], code + ".md: one row per English term: " + e);
    byEn[e] = r;
  });
  var missing = REQUIRED.filter(function (t) { return !byEn[t.toLowerCase()]; });
  assert.deepStrictEqual(missing, [],
    code + ".md covers every required term (missing " + missing.join(", ") + ")");

  rows.forEach(function (r) {
    assert.ok(r[1].length > 0, code + ".md: " + spec.word + " term present for “" + r[0] + "”");
    assert.ok(r[2].length > 0, code + ".md: note present for “" + r[0] + "” (why this wording)");
  });

  /* --- one locale term per concept: no synonym split --------------------- */
  var seen = {};
  rows.forEach(function (r) {
    var t = r[1].toLowerCase();
    assert.ok(!seen[t], code + ".md: “" + t + "” maps to one English term only (also: " + seen[t] + ")");
    seen[t] = r[0];
  });
  assert.ok(/^#\s/m.test(glossary), code + ".md has a markdown heading");
  assert.ok(glossary.indexOf("i18n-glossary") !== -1 || glossary.indexOf(spec.word) !== -1,
    code + ".md says what language it governs");

  /* --- citations: exist, and really show the agreed word ----------------- */
  var REJECT_ONE = /Counter-example form:\s*`([^`]+)`/;
  var citations = [];
  rows.forEach(function (r) {
    /* the `Counter-example form: `word`` marker names a WORD, not a key, so it
     * is lifted out before citation parsing — otherwise it reads as a citation
     * of a nonexistent locale key. */
    var note = r[2].replace(/Counter-example form:\s*`[^`]+`/g, "Counter-example form:");
    var rx = /`([a-z_][A-Za-z0-9_.-]*)`/g, m;
    var markerAt = note.search(/counter-example|same root, other sense/i);
    while ((m = rx.exec(note)) !== null) {
      citations.push({ term: r[0], term_: r[1], key: m[1],
        isCounter: markerAt !== -1 && m.index > markerAt });
    }
  });
  assert.ok(citations.length >= 20, code + ".md cites real keys as evidence (" + citations.length + ")");

  var badKey = [], badProof = [];
  citations.forEach(function (c) {
    if (typeof dict.values[c.key] !== "string") { badKey.push(c.term + " -> " + c.key); return; }
    if (c.isCounter) return;
    if (String(dict.values[c.key]).toLowerCase().indexOf(headWord(c.term_)) === -1) {
      badProof.push(c.term + " -> " + c.key + " = " + JSON.stringify(dict.values[c.key]).slice(0, 60));
    }
  });
  assert.deepStrictEqual(badKey, [], code + ".md: every cited key exists in " + code + ".json");
  assert.deepStrictEqual(badProof, [],
    code + ".md: every evidence citation really shows the agreed " + spec.word + " word");

  /* --- the counts the notes quote --------------------------------------- */
  var countBad = [], proseBad = [];
  rows.forEach(function (r) {
    var table = spec.COUNTS[r[0]];
    if (!table) { countBad.push(code + ": no COUNTS entry for row “" + r[0] + "”"); return; }
    table.forEach(function (pair) {
      var actual = uses(dict.all, dict.values, pair[0]).length;
      if (actual !== pair[1]) {
        countBad.push(code + " “" + r[0] + "” (“" + pair[0] + "”): note says " + pair[1] +
          ", " + code + ".json has " + actual);
      }
    });
    /* Every "N strings" number in the prose must be one this row asserts —
     * otherwise a number an auditor reads is unchecked by this file. */
    var claimed = [], m;
    var rx = /(\d[\d.]*)\s+string/gi;
    while ((m = rx.exec(r[2])) !== null) claimed.push(Number(m[1].replace(/\.$/, "")));
    var allowed = table.map(function (p) { return p[1]; });
    claimed.forEach(function (n) {
      if (allowed.indexOf(n) === -1) {
        proseBad.push(code + " “" + r[0] + "”: prose quotes " + n + " strings but the row asserts " +
          allowed.join("/"));
      }
    });
    if (!claimed.length) proseBad.push(code + " “" + r[0] + "”: no string count quoted");
  });
  assert.deepStrictEqual(countBad, [], code + ".md: every quoted string count matches " + code + ".json");
  assert.deepStrictEqual(proseBad, [], code + ".md: every quoted count is asserted for that row");

  /* --- counter-example sets: COMPLETE and MINORITY ---------------------- */
  var incomplete = [], minority = [];
  var rejects = 0;
  rows.forEach(function (r) {
    var m = REJECT_ONE.exec(r[2]);
    if (!m) return;
    rejects++;
    var alt = m[1];
    var altKeys = uses(dict.all, dict.values, alt);
    var own = uses(dict.all, dict.values, r[1]).length;
    var named = citations.filter(function (c) { return c.term === r[0]; }).map(function (c) { return c.key; });
    var un = altKeys.filter(function (k) { return named.indexOf(k) === -1; });
    if (un.length) incomplete.push(code + " “" + r[0] + "” (“" + alt + "”) unlisted: " + un.join(", "));
    if (altKeys.length > own) {
      minority.push(code + " “" + r[0] + "” mandates “" + r[1] + "” (" + own +
        " strings) but rejects “" + alt + "” (" + altKeys.length + ") — the rejected form is the majority");
    }
  });
  assert.ok(rejects >= 2, code + ".md declares at least two rejected forms (" + rejects + ")");
  assert.deepStrictEqual(incomplete, [], code + ".md: counter-example sets are complete");
  assert.deepStrictEqual(minority, [], code + ".md: no row mandates the minority form");

  console.log("OK: " + code + ".md — " + rows.length + " rows, " + REQUIRED.length +
    " required terms, " + citations.length + " citations, " + rejects + " counter-example sets, " +
    "all counts verified against " + code + ".json");
  totalRows += rows.length; totalCitations += citations.length; totalRejects += rejects;
});
console.log("OK: i18n-glossary multi-locale (de, ko, hi, tr) — " + totalRows + " rows, " +
  totalCitations + " citations verified, " + totalRejects + " counter-example sets complete and minority");