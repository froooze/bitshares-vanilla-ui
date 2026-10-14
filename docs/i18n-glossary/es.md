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
- **Every row names the majority form.** Where `es.json` had already settled a
  word, that word wins and the row is re-grounded on the strings that use it;
  a row's "counter-example" list is then the COMPLETE set of keys that disagree,
  not a sample. `tooling/i18n-glossary-test.js` re-counts both sides against
  `es.json` and fails when the mandated word is the minority or when an
  unenumerated counter-example exists — a glossary that breaks a dozen correct
  pool strings is worse than no glossary.
- **Where a root is shared, the collision is named.** Spanish reuses one root
  across concepts that English keeps apart (`participación`, `parte`). Each such
  row says which strings carry the OTHER senses, so an auditor does not
  "correct" a correct string.

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
| share | parte | A generic fraction of something (`referrals.network_share`, `referrals.lifetime_referrer_share`, `topops.chart_aria` "partes de operaciones"). Same root, other sense — an unrelated "part", correct as it stands: `createaccount.each_dot_separated_part_must_be_1_63_characte` (a dot-separated part of an account name), `help.topic_htlc_body` (each side of an HTLC), `help.index_intro` (each part of the wallet). Match the SENSE before changing the word. |
| pool share | acciones LP | What you hold in a liquidity pool (`pool.shares_field`, `pool.list_sub`). A pool share — not a "parte de pool", and not a `participación` (that root means the STAKE you deposit, see the next row). |
| prediction-market share | participaciones | A YES/NO unit in a prediction market (`prediction.prediction_market_assets_yes_no_shares_positi`, `prediction.quick_position_hint`). Same root, other sense — `participación` meaning stake or delegated proof-of-stake, correct as they stand: `pool.staked` "Participación realizada" (pool stake), `vote.ballot_intro` "Tu participación elige testigos" (vote stake), `help.topic_bitshares_text` "prueba de participación delegada" (the chain's own name), `help.topic_settings_body` (witness participation in node health). |
| market | mercado | A base/quote trading pair (`shell.opening_market`, `dashboard.tagline`). |
| orderbook | libro de órdenes | The DEX book (`market.order_book`, `menu.d_exchange`). Not "libro de pedidos". |
| limit order | orden límite | A resting priced order (`account.op_limit_create`). |
| fee | comisión | The chain fee an operation pays, in 127 shipped strings (`barter.fee_payer`, `account.resolving_fee`). Never "tarifa" (0 strings). "costo" is a DIFFERENT word and is correct where the sense is cost in the abstract, not the chain fee — `help.topic_dex-trading_body` shows the split exactly: "la billetera calcula el costo y suma la comisión de la cadena". Same root, other sense: `help.topic_trollbox_body` (heading "Honestidad de costo") and `help.topic_settings_body` (the privacy cost). Leave them. |
| operation | operación | One chain action, e.g. transfer or limit_order_create (`account.unknown_operation`). |
| transaction | transacción | A signed bundle of operations (`credit.could_not_prepare_the_transaction`). |
| block | bloque | A block in the explorer (`explorer_blocks.title`, `explorer.viewing_as_committee`). The wallet lock/unlock buttons stay English-only verbs — `shell.lock` is "Bloquear" and `shell.unlock` "Desbloquear", so never "bloquear" for locking a wallet; a substring search for "bloque" will match both. |
| memo | memo | The optional public note on a transfer (`gateway.memo_label`). |
| brainkey | frase de recuperación | The ordered word list that IS the backup (`wallet.s6` "Confirma que anotaste la frase de recuperación primero", `wallet.brainkey` "Frase de recuperación", `createaccount.step_brainkey` "Frase de recuperación"), 42 strings. Feminine, as the shipped prose has it ("Una frase de recuperación se genera", `splash.step2_d`). Never "clave mental" — it is not a password. Retired: "brainkey" — the old loanword survives only code-bound, 2 strings. Counter-example form: `brainkey` — the complete set is the `#/create-wallet-brainkey` route hash in `wallet.console_hint` and in `help.topic_sitemap_body`; both stay byte-verbatim as router identifiers. |
| witness | testigo | Block producer (`explorer.th_witness`, `help.topic_witnesses_body`). |
| committee | comité | Elected members that set fees and chain parameters (`help.topic_voting_body`). |
| worker | propuesta de grant | Paid proposal funded by the chain (`createworker.create_worker` "Crear propuesta de grant", `help.topic_workers_title` "Propuestas de grant" — 36 translated strings carry grant: 18 singular, 20 plural, 3 keys both). Retired: "trabajador" — 0 strings. Counter-example form: `trabajador` (nothing ships it; do not reintroduce it). Same root, other sense, correct as they stand — "trabajo" is the work itself (dates and prose), never the proposal: `createworker.work_begins`, `createworker.work_begins_2`, `createworker.work_end_must_be_after_work_begin`, `createworker.work_ends`, `createworker.work_ends_2`, `help.topic_authorities_body`, `help.topic_bitshares_body`, `help.topic_blockchain_body`, `help.topic_history-index_body`, `help.topic_translation-limitations_body`, `help.topic_workers_body`, `menu.d_worker`, `proposal.multisig_story`. Code, not prose — the get_all_workers identifier in `vote.hide_legacy_title` and the `#/create-worker` route hashes in `help.topic_sitemap_body`, `vote.empty_hint` stay byte-verbatim. |
| proxy | proxy | The account your votes follow. All 17 shipped strings keep the loanword (`vote.set_proxy`, `vote.remove_proxy`, `vote.what_is_a_proxy`, `vote.proxy_none`, `vote.proxy_aria`, `vote.proxy_empty`, `vote.proxy_needed`, `vote.proxy_ph`, `vote.proxy_votes_prefix`, `vote.retry_self`, `vote.retried_prefix`, `voting.s1`, `help.topic_voting_body`, `help.topic_witnesses_text`, `help.topic_witnesses_body`, `help.topic_committee_body`, `help.topic_glossary_body`), so the loanword is the agreed form. Counter-example form: `apoderado`. The full set is `help.topic_voting_text` alone ("delega en un apoderado") — align it on the next pass, do not align the other seventeen to it. |
| slate | → papeleta | Retired: the chain-vote list is now "papeleta" (ballot list) everywhere; see that row. Kept here so an auditor searching the old term lands in the right place. |
| ballot list | papeleta | A named set of witness votes (`vote.in_sync` "La papeleta coincide con la cadena — no hay cambios que publicar.", `vote.proxy_follows` "la papeleta siguiente es de solo lectura.", `vote.proxies_follow_another_account_s_slate_re` "Los proxies siguen la papeleta de otra cuenta…", `vote.sent_middle` ") pero la nueva papeleta no se observó en "). "Lista" alone collides with this app's own list pages, so the compound is always papeleta, never lista de votos. |
| vesting | consolidación | A time-locked balance (`vesting.title`). Not "vesting" in prose. |
| proposal | propuesta | Includes create_worker proposals (`account.proposals_page`). |
| ticket | participación de voto | A vote-locked stake (`ticket.create_ticket` "Crear participación de voto", `ticket.review_ticket` "Revisar participación de voto", `ticket.ticket` "Participación de voto"). Retired: "ticket" — the loanword survives only code-bound (the `%(ticket)s` placeholder in `account.sum_ticket_update`) and in the `#/tickets` route link. "Boleto" still reads as a bus ticket. |
| HTLC | HTLC | Never expanded in UI chrome; a help article may gloss it as "contrato con hash y tiempo" (`htlc.confirm_create`). |
| liquidity pool | pool | Loanword for a CPMM market (`pool.create_title`, `pool.mine_title`); "pool de liquidez" is the gloss the titles use (`pool_detail.title`, `pools.title`) and "pools" the plural in prose (`help.topic_pools_body`). One word, not three. |
| exchange | intercambio | The DEX venue itself (`nav.exchange`, `market.title`, `trade.title`). **Never "intercambio" for a swap** — that is the act of trading inside a pool, which is its own row. |
| swap | swap | Loanword for a pool or HTLC exchange: all 26 shipped strings keep it, every pool, desk and help string (`pool.confirm_swap`, `pool.review_swap`, `pool.swap_title`, `pool.swap_title_attr`, `pool.swap_stake_col`, `pool.fill_swap`, `pool.swapped`, `pool.swap_failed`, `menu.d_pools`, `help.topic_pools_text`, `help.topic_pools_body`, `debit.tile_barter_desc`, `about.s2_body`), so the loanword is the agreed form. Counter-example form: `canje`. The HTLC redeem leg says "canje" instead, and the full set is `htlc.confirm_redeem`, `htlc.review_redeem`, `htlc.redeem_title`, `htlc.redeem_fee_failed`, `htlc.redeemer_row`, `htlc.expired_note`, `help.topic_htlc_body`, `account.op_htlc_redeem`, `account.op_htlc_redeemed`, `account.sum_htlc_redeem` — align those on the next pass, do not align the pool strings to them. Same root, other sense — "canjeable" meaning redeemable-into, never a swap, correct as it stands: `help.topic_dex-intro_body`, `help.topic_gateways_body`, `help.topic_prediction_body`. |
| credit offer | oferta de crédito | A lender's offer on the credit desk (`credit.title`, plural in `account.no_credit_offers_for_this_account`). |

**Deliberate loanwords** (smartcoin, HTLC, slate, colateral,
memo, proxy, swap, pool): each names something BitShares invented or a piece of
its own jargon, and a literal translation reads as a different concept to a
Spanish speaker. They are still translated surrounding text, and the surrounding
text is where the explanation lives.

**Never translate** (byte-verbatim in every dictionary): `%(name)s`
placeholders, URLs, object ids like `1.2.105`, asset symbols like `BTS`, theme
ids (`ref-ui-theme`, `dex-ux-theme`, `vanilla-ui-theme`) and network ids
(`mainnet`, `testnet`).
