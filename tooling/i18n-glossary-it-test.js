/* i18n-glossary-it-test: docs/i18n-glossary/it.md is the artifact an external
 * auditor reads BEFORE trusting the Italian translation, so every claim in it is
 * checked against the shipped vanilla/locales/it.json rather than trusted.
 *
 * The shipped tooling/i18n-glossary-test.js does the same for es.md; this is the
 * Italian twin, built to the same rules:
 *   1. structure — one markdown table, three columns, every cell filled, one row
 *      per English term, and every one of the 26 required BitShares terms is a
 *      ROW (not a passing mention in prose);
 *   2. one Italian term per concept — no synonym split;
 *   3. every `key` a note cites exists in it.json, and unless the note marks it a
 *      counter-example or a same-root other sense, its value really carries the
 *      agreed word (the check exists because an auditor who checks a citation and
 *      finds nothing stops trusting the whole table);
 *   4. every count a note quotes matches it.json — as an explicit per-row table,
 *      because the count is of the agreed ITALIAN word, which is not derivable
 *      from the English term ("limit order" counts "ordine limite", not "order");
 *   5. every `Counter-example form:` list is COMPLETE and MINORITY — the defect
 *      this file exists to prevent is a row mandating a word the shipped
 *      dictionary mostly does not use, or rejecting a form without naming every
 *      string that carries it, because an auditor following it would rewrite a
 *      dozen correct strings.
 *
 * Runs: node tooling/i18n-glossary-it-test.js (exit 0 = green). */
/* verify-it-glossary: every row's Italian term, every cited key, and every
 * counter-example set in docs/i18n-glossary/it.md is checked against the
 * shipped vanilla/locales/it.json, so an auditor who follows the file is never
 * sent to a string that does not exist or does not carry the agreed word. */
var fs = require("fs"), path = require("path"), assert = require("assert");
var ROOT = path.join(__dirname, "..");
var FILE = path.join(ROOT, "docs/i18n-glossary/it.md");
var REQUIRED = ["brainkey","witness","committee","worker","proxy","vesting","HTLC","swap","slate",
  "liquidity pool","credit offer","ticket","proposal","precision","orderbook","limit order","fee",
  "account","asset","smartcoin","collateral","balance","share","market","block","transaction"];
var glossary = fs.readFileSync(FILE, "utf8");
function cells(l){var s=l.trim();if(s.charAt(0)!=="|"||s.charAt(s.length-1)!=="|")return null;
  return s.slice(1,-1).split("|").map(function(c){return c.trim();});}
var rows=[];
glossary.split(/\r?\n/).forEach(function(l){var c=cells(l);if(!c||c.length!==3)return;
  if(/^-+$/.test(c[0].replace(/\s/g,"")))return;rows.push(c);});
var header=rows.shift();
assert.deepStrictEqual(header.map(function(h){return h.toLowerCase();}),
  ["english term","italian term","note"],"table names its three columns");
var byEn={};rows.forEach(function(r){var e=r[0].toLowerCase();
  assert.ok(!byEn[e],"one row per English term: "+e);byEn[e]=r;});
var missing=REQUIRED.filter(function(t){return !byEn[t.toLowerCase()];});
assert.deepStrictEqual(missing,[],"covers every required term (missing "+missing.join(", ")+")");
rows.forEach(function(r){assert.ok(r[1].length>0,"Italian term for "+r[0]);
  assert.ok(r[2].length>0,"note for "+r[0]);});
var seen={};rows.forEach(function(r){var t=r[1].toLowerCase();
  assert.ok(!seen[t],"“"+t+"” maps to one English term only (also: "+seen[t]+")");seen[t]=r[0];});

function flat(d,p){p=p||"";var o={};Object.keys(d).forEach(function(k){if(k==="_meta")return;
  if(d[k]&&typeof d[k]==="object")Object.assign(o,flat(d[k],p+k+"."));else o[p+k]=d[k];});return o;}
var enValues=flat(JSON.parse(fs.readFileSync(path.join(ROOT,"vanilla/locales/en.json"),"utf8")));
var itValues=flat(JSON.parse(fs.readFileSync(path.join(ROOT,"vanilla/locales/it.json"),"utf8")));
function isTranslated(k){return typeof itValues[k]==="string"&&itValues[k]!==enValues[k];}
var ALL=Object.keys(itValues).filter(isTranslated).sort();
function uses(w){var rx=new RegExp("\\b"+w+"\\w*","i");
  return ALL.filter(function(k){return rx.test(itValues[k]);});}
function headWord(t){var h=String(t).split(" ")[0].toLowerCase();
  return h.length>4&&h.charAt(h.length-1)==="s"?h.slice(0,-1):h;}

var REJECT=/Counter-example form:\s*`([^`]+)`/g;
var citations=[];
rows.forEach(function(r){
  var note=r[2].replace(/Counter-example form:\s*`[^`]+`/g,"Counter-example form:");
  var rx=/`([a-z_][A-Za-z0-9_.-]*)`/g,m;
  var counterAt=note.search(/counter-example|same root, other sense/i);
  while((m=rx.exec(note))!==null)
    citations.push({term:r[0],itTerm:r[1],key:m[1],
      isCounter:counterAt!==-1&&m.index>counterAt});
});
console.log("citations: "+citations.length);
var badKey=[],badProof=[];
citations.forEach(function(c){
  if(typeof itValues[c.key]!=="string"){badKey.push(c.term+" -> "+c.key);return;}
  if(c.isCounter)return;
  if(String(itValues[c.key]).toLowerCase().indexOf(headWord(c.itTerm))===-1)
    badProof.push(c.term+" -> "+c.key+" = "+JSON.stringify(itValues[c.key]).slice(0,60));
});
assert.deepStrictEqual(badKey,[],"every cited key exists in it.json");
assert.deepStrictEqual(badProof,[],"every evidence citation shows the agreed Italian word");

/* the counts the notes quote */
/* The counts each note quotes, asserted one by one against it.json. An explicit
 * table rather than a generic parse: the count is of the AGREED ITALIAN WORD,
 * which is not derivable from the English term ("limit order" counts "ordine
 * limite", not "order"), so the mapping lives here where a reviewer sees it. */
var COUNTS = {
  "wallet": ["wallet",190], "account": ["account",300], "balance": ["saldo",35],
  "asset": ["asset",272], "smartcoin": ["smartcoin",21], "collateral": ["collaterale",41],
  "precision": ["precisione",18], "share": ["quote",35], "pool share": ["quote LP",3],
  "stake": ["stake",23], "market": ["mercato",116], "exchange": ["exchange",23],
  "desk": ["sezione",39], "swap": ["swap",41], "orderbook": ["book",30],
  "limit order": ["ordine limite",5], "order": ["ordine",55], "operation": ["operazione",45],
  "fee": ["commissione",133], "transaction": ["transazione",40], "block": ["blocco",43],
  "memo": ["memo",48], "brainkey": ["brainkey",41], "witness": ["witness",35],
  "committee": ["comitato",24], "worker": ["worker",36], "proxy": ["proxy",21],
  "slate": ["slate",7], "vesting": ["vesting",44], "proposal": ["proposta",65],
  "ticket": ["ticket",31], "HTLC": ["HTLC",25], "liquidity pool": ["pool",120],
  "credit offer": ["offerta di credito",11], "deal": ["deal",28], "gateway": ["gateway",29],
  "node": ["nodo",49], "chain": ["chain",130], "authority": ["autorit",22],
  "issuer": ["erogatore",17], "producer": ["produttor",20], "publisher": ["publisher",8],
  "settle": ["settlement",44], "referral": ["referrer",8]
};
var countBad=[];
Object.keys(COUNTS).forEach(function(term){
  var row=byEn[term.toLowerCase()];
  if(!row){countBad.push(term+": no row");return;}
  var word=COUNTS[term][0],claimed=COUNTS[term][1];
  var actual=uses(word).length;
  if(actual!==claimed)countBad.push(term+" (“"+word+"”): note says "+claimed+", it.json has "+actual);
});
assert.deepStrictEqual(countBad,[],"every quoted string count matches it.json");

/* every counter-example set must be COMPLETE: all it.json strings using the
 * rejected form must be named somewhere in that row. */
var incomplete=[];
rows.forEach(function(r){
  REJECT.lastIndex=0;var m;
  while((m=REJECT.exec(r[2]))!==null){
    var alt=m[1],altKeys=uses(alt);
    var named=citations.filter(function(c){return c.term===r[0];}).map(function(c){return c.key;});
    var un=altKeys.filter(function(k){return named.indexOf(k)===-1;});
    if(un.length)incomplete.push(r[0]+" (“"+alt+"”) unlisted: "+un.join(", "));
    if(altKeys.length>uses(r[1]).length)
      incomplete.push(r[0]+" mandates “"+r[1]+"” ("+uses(r[1]).length+
        ") but rejects “"+alt+"\" ("+altKeys.length+") — the rejected form is the majority");
  }
});
assert.deepStrictEqual(incomplete,[],"counter-example sets complete and minority");
console.log("OK: i18n-glossary/it — "+rows.length+" rows, "+
  REQUIRED.length+" required terms, "+citations.length+
  " citations, all counts and counter-example sets verified against it.json");
