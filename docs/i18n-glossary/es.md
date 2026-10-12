# Spanish glossary — `bitshares-vanilla-ui`

This is the file an external auditor reads **before** trusting a machine-filled
Spanish translation. It fixes **one Spanish term per concept**, so a single
correction here (plus the same word in `vanilla/locales/es.json`) propagates
everywhere instead of leaving three near-synonyms in the UI.

**How to use it**

- Translate the English term in column 1 as the Spanish term in column 2. Do not
  invent a second Spanish word for the same concept: a synonym split is the one
  mistake this file exists to prevent, and `tooling/i18n-glossary-test.js` fails
  when two English terms claim the same Spanish one.
- Column 3 says why, and usually names the `es.json` key that already proves the
  wording ("checked 2026-10-12"). Keys cited there were read out of
  `vanilla/locales/es.json`; a citation is evidence, not decoration.
- Corrections land through the `translation` issue label on the project tracker —
  the same route `#/help/translation-limitations` in the wallet gives readers.
- **Status:** the Spanish column below is the agreed vocabulary, not yet a claim
  of human review. The Spanish fill pass cross-checks every row against
  `es.json` and flips the wording here when the shipped string disagrees. Until a
  person has read a string in Spanish, the wallet labels it machine-filled.

Placeholders (`%(name)s`), URLs, object ids (`1.2.x`), asset symbols and theme
or network ids are **byte-verbatim** in every language and never appear here.

| English term | Spanish term | Note |
| --- | --- | --- |
| wallet | billetera | The local vault this app calls a wallet (`wallet.s4`, `settings.es_note`). Not "monedero", which reads as a purse. |
| account | cuenta | Any name on chain (`nav.account`). Also the account object in the explorer. |
| balance | saldo | What an account holds (`account.s1`, `vesting.balance`). |
| asset | activo | Any token on chain (`account.asset_th`). |
| smartcoin | smartcoin | Loanword for a market-pegged asset (`explorer.no_smartcoins`). Never "moneda inteligente" in the UI. |
| collateral | colateral | Backing behind a smartcoin position (`borrow.a_bid_locks_your_collateral_against_the_settl`). |
| precision | precisión | Decimal places an asset stores (`explorer.precision_row`). Never translated away in an amount string. |
| share | parte | Generic ownership fraction (`referrals.network_share`). |
| pool share | acciones LP | What you hold in a liquidity pool (`pool.shares_field`). A pool share, not a "parte de pool". |
| prediction-market share | participaciones | YES/NO participaciones in a prediction market (`prediction.prediction_market_assets_yes_no_shares_positi`). |
| market | mercado | A base/quote trading pair (`shell.opening_market`, `dashboard.tagline`). |
| orderbook | libro de órdenes | The DEX book (`market.order_book`, `menu.d_exchange`). Not "libro de pedidos". |
| limit order | orden límite | A resting priced order (`account.op_limit_create`). |
| fee | comisión | Chain fee paid per operation (`barter.fee_payer`, `account.resolving_fee`). Never "tarifa" or "costo". |
| operation | operación | One chain action, e.g. transfer or limit_order_create (`account.unknown_operation`). |
| transaction | transacción | A signed bundle of operations (`credit.could_not_prepare_the_transaction`). |
| block | bloque | A block in the explorer (`explorer_blocks.title`). The wallet lock/unlock buttons stay English-only verbs — never "bloquear" for locking a wallet. |
| memo | memo | The optional public note on a transfer (`gateway.memo_label`). |
| brainkey | brainkey | Loanword: the ordered word list that IS the backup (`wallet.s6`). Never "clave mental" — it is not a password. |
| witness | testigo | Block producer (`explorer.th_witness`, `help.topic_witnesses_body`). |
| committee | comité | Elected members that set fees and chain parameters (`help.topic_voting_text`). |
| worker | trabajador | Paid proposal funded by the chain (`createworker.create_worker`). |
| proxy | apoderado | The account your votes follow (`help.topic_voting_text` reads "delega en un apoderado"). Counter-example: `voting.s1` still says "proxy" — align it on the next pass. |
| slate | slate de voto | Loanword for a named set of witness votes (`vote.proxies_follow_another_account_s_slate_re`). "Lista" collides with this app's own list pages. |
| vesting | consolidación | A time-locked balance (`vesting.title`). Not "vesting" in prose. |
| proposal | propuesta | Includes create_worker proposals (`account.proposals_page`). |
| ticket | ticket | Loanword for a vote-locked stake (`help.topic_tickets_title`). "Boleto" reads as a bus ticket. |
| HTLC | HTLC | Never expanded in UI chrome; a help article may gloss it as "contrato con hash y tiempo" (`htlc.confirm_create`). |
| liquidity pool | pool de liquidez | Pooled automated market (`pool_detail.title`, plural in `pools.title`). |
| swap | canje | A pool or HTLC exchange (`htlc.confirm_redeem`). **Never "intercambio"** — counter-example: `market.title` is the DEX/exchange itself. |
| credit offer | oferta de crédito | A lender's offer on the credit desk (`credit.title`, plural in `account.no_credit_offers_for_this_account`). |

**Deliberate loanwords** (brainkey, smartcoin, ticket, HTLC, slate, colateral,
memo): each names something BitShares invented, and a literal translation reads
as a different concept to a Spanish speaker. They are still translated
surrounding text, and the surrounding text is where the explanation lives.

**Never translate** (byte-verbatim in every dictionary): `%(name)s`
placeholders, URLs, object ids like `1.2.105`, asset symbols like `BTS`, theme
ids (`ref-ui-theme`, `dex-ux-theme`, `vanilla-ui-theme`) and network ids
(`mainnet`, `testnet`).
