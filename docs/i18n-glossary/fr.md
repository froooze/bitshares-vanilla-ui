# French glossary — `bitshares-vanilla-ui`

This is the file an external auditor reads **before** trusting a machine-filled
French translation. It fixes **one French term per concept**, so a single
correction here (plus the same word in `vanilla/locales/fr.json`) propagates
everywhere instead of leaving three near-synonyms in the UI.

**How to use it**

- Translate the English term in column 1 as the French term in column 2. Do not
  invent a second French word for the same concept: a synonym split is the one
  mistake this file exists to prevent.
- Column 3 says why, and names the `fr.json` keys that already prove the
  wording. Keys cited there were read out of `vanilla/locales/fr.json` after the
  2026-10-13 fill pass; a citation is evidence, not decoration. In the notes,
  a French WORD in bold is a form under discussion, not a locale key — only
  things shaped like `section.key` are citations.
- Corrections land through the `translation` issue label on the project tracker —
  the same route `#/help/translation-limitations` in the wallet gives readers.
- **Status:** the French column below is the agreed vocabulary, not yet a claim
  of human review. The French fill pass cross-checked every row against
  `fr.json` and chose the form that file actually uses. Until a person has read
  a string in French, the wallet labels it machine-filled.
- **Every row names the form `fr.json` uses.** Where a second form exists for
  the same concept, the row lists **every** string carrying it — as a
  counter-example (align it on the next pass) or as a same-root other sense
  (leave it alone). A glossary that breaks a dozen correct pool strings is worse
  than no glossary.
- **Typography follows the section, not the string.** `fr.json` writes the
  typographic apostrophe (U+2019) and U+00A0 before the high punctuation in
  `approval`, `barter`, `credit`, `explorer`, `gateway`, `help`, `htlc`, `i18n`,
  `instant`, `proposal`, `trade`, `transfer`; every other section writes the
  ASCII apostrophe and a plain space. So the ASCII and the typographic spelling
  of the same phrase are the **same word** — do not "fix" one into the other.
  The split is pre-existing, deliberate, and asserted by
  `tooling/apply_i18n_fr_chunkB.py` (gate G7).

Placeholders (`%(name)s`), URLs, object ids (`1.2.x`), asset symbols and theme
or network ids are **byte-verbatim** in every language and never appear here.

| English term | French term | Note |
| --- | --- | --- |
| wallet | portefeuille | The local vault this app calls a wallet (`account.this_wallet`, `wallet.title`, `auth.create_a_local_wallet`), 196 shipped strings. Never "porte-monnaie", which reads as a physical purse. The English word survives inside file paths only (`auth.wallet_backend_missing_js_wallet_js_failed_to` names `js/wallet.js`) — that is a path, not prose. |
| account | compte | Any name on chain (`nav.account`, `account.manager_title`), 308 strings. Also the account object in the explorer. |
| balance | solde | What an account holds (`account.balance_th`, `vesting.balance`), 75 strings. Same root, other sense and correct as they stand — the lock and unlock verbs are a near-collision: `shell.lock` "Verrouiller" and `shell.unlock` "Déverrouiller" mean LOCK, never block — same root, other sense, correct as they stand, and never to be replaced by a balancing verb. |
| asset | actif | Any token on chain (`account.asset_th`, `misc.asset`), 291 strings. `explorer.asset_actions` is "Actions de l'actif" (the asset's own action list), not a share. |
| smartcoin | smartcoin | Loanword for a market-pegged asset (`explorer.assets_mode_market` "SmartCoins", `asset.smartcoin_field`), 23 strings. Never "monnaie intelligente" — 0 shipped strings. Same root, other sense and correct as they stand — the phrase **actif ancré au marché** is the *gloss* the help prose introduces the concept with, not a replacement of the term: `help.topic_assets-mpa_body`, `help.topic_assets-feed_body`, `help.topic_assets-private_body`. |
| collateral | collatéral | Backing locked behind a smartcoin or a credit position (`borrow.hdr_collateral`, `credit.collateral`), 42 strings. Counter-example form: **garantie**. Four strings carry it and three mean something else — `gateway.backing_fact` "Monnaie de garantie" (the backing COIN), `prediction.backing_asset` "Actif de garantie" (the backing ASSET), `help.topic_disclaimer_body` "Aucune garantie, responsabilité limitée" (a warranty) — leave those; the fourth, `prediction.quick_position_hint` ("OUI dépense la garantie"), is collateral and should be aligned. |
| precision | précision | Decimal places an asset stores (`explorer.precision_row`, `asset.precision_field`), 18 strings. Never translated away inside an amount string. |
| share | part | A generic fraction of something: a fee split (`referrals.network_share` "Part du réseau", `referrals.lifetime_referrer_share`), a contribution in a chart (`topops.chart_aria`), 95 strings. Four other senses share the root, are correct as they stand, and must not be "aligned" onto **part** — match the SENSE before changing the word. Same root, other sense 1 — **partie** = a piece or a segment: `createaccount.each_dot_separated_part_must_be_1_63_characte` and `createaccount.each_dot_separated_part_must_start_with_a_let` (a dot-separated part of an account name), `help.index_intro` and `news.help_how_each_part_works` and `menu.d_help` and `help.topic_tour_body` (each part of the wallet), `help.topic_htlc_body` and `help.topic_proposals_body` (each side), `barter.side_a` and `barter.side_b` (each side of a barter). Same root, other sense 2 — **jambe** = a leg: `borrow.both_legs_must_be_above_zero_nonzero_debt_nee`, `pool.virgin_note`, `pool.asset_1_field`, `market_net.asset_2_field`, `samet.fee_borrow_leg_op_67`, `xrate.unpriced`. Same root, other sense 3 — **action** = a step or an operation, not a quantity: `help.topic_accounts-permissions_body` "passé le seuil l'action est autorisée", `help.topic_translation-limitations_body` "action irréversible", `menu.d_proposals`, `help.topic_proposals_body`. Same root, other sense 4 — **action** = an equity share, a rarer sense still: `help.topic_assets-uia_body` "actions de société", and **actionnaires** in `help.topic_witnesses_body` and `help.topic_committee_body`. |
| pool share | parts LP | What you hold in a liquidity pool (`pool.shares_field` "Parts LP", `pool.list_sub`, `pool.stake_shares_row` "Parts LP estimées"). Plain "parts" in the same sense — `pool.virgin_note`, `pool.stake_preview_bad`, `pool.stake_preview_need_both`, `pool.stake_preview_unavailable` — is the same concept shortened, not a different term. A pool share is NOT the stake you deposit (next row) and NOT a **partie**. |
| prediction-market share | part OUI/NON | A YES/NO unit in a prediction market (`prediction.prediction_market_assets_yes_no_shares_positi`, `menu.d_prediction`, `help.topic_prediction_text`, `help.topic_prediction_body`, `prediction.quick_position_hint`). Same word, other sense — the same root meaning stake or a fee share is correct there: `pool.list_sub`, `vote.ballot_intro`, `referrals.network_share`, `topops.chart_aria`. |
| stake | stake | The locked balance that earns voting weight or a pool's yield (`pool.list_sub` "Le stake est un dépôt des deux jambes contre des parts LP", `menu.d_tickets`, `pool.stake_title`), 47 strings. Thirty-three of them are the "stake de vote" compound (see the ticket row). Counter-example form: **mise** in the stake sense — the complete set is `help.topic_tickets_text`, `help.topic_tickets_body` and `help.topic_txbuilder_body` ("Mise de pool", which reads as a typo for the loanword); align those three on the next pass. Same root, other sense and correct — "mise à jour" is *update*, in about sixty shipped strings (`account.op_account_update`, `market.fail_update`, `credit.review_update`, …): a reviewer searching "mise" will hit all of them and none of them is a stake. |
| market | marché | A base/quote trading pair (`shell.opening_market`, `dashboard.tagline`), 181 strings. One graph step on the market map is a **saut** (see the hop row), not a market. |
| exchange | bourse | The DEX venue itself (`nav.exchange`, `market.title`, `market.exchange_desk`, `menu.p_exchange`, `seo.title_market`), 18 strings. Counter-example form: **échange** in the venue sense — the complete set is `help.topic_bitshares_text`, `help.topic_bitshares_body`, `help.topic_dex-intro_title`, `help.topic_dex-intro_body`, `help.topic_spotlight_body`, `help.topic_gateways-xbts_body`, `help.topic_dex-shorting_body`, `help.topic_blockchain_body`, `help.topic_accounts-general_body`, `help.topic_assets-mpa_body`, `help.topic_assets-private_body`; align those eleven on the next pass, do not align the eighteen to them. Same root, other sense and correct as they stand — **échange** meaning the ACT of trading or a conversion: `market.map_connects`, `market.map_connects_fallback`, `pool_detail.map_connects`, `pool_detail.map_connects_fallback`, `prediction.quick_position_hint`, `help.topic_gateways_body` ("un pont échange votre dépôt"). And never translate the build-dialog "exchange" as "bourse" at all: `about.dlg_bad_link`, `about.dlg_no_match`, `about.dlg_search_ph`, `help.topic_about-making_body` use it for a prompt/response pair. |
| swap | swap | Loanword for a pool or an HTLC exchange (`pool.swap_title` "Swap dans le pool", `menu.d_pools` "gagner des frais de swap", `help.topic_htlc_text`, `help.topic_barter_body`), 43 strings. Counter-example form: **échangé** — 0 strings today; the one history line that used it, `account.sum_pool_swap`, was moved onto the loanword in the same pass precisely because that verb reads as the exchange venue above. Never **troc** for a swap: that word is barter (`barter.title`, `barter.propose_barter_op_22`). |
| orderbook | carnet d'ordres | The DEX book (`market.order_book`, `market.raw_book`, `menu.d_exchange`, `about.s2_title`, `seo.desc_market`), 13 strings. Not "livre d'ordres" (0 strings). The apostrophe follows the section convention, so the ASCII and the typographic spelling of this phrase both ship. |
| limit order | ordre limite | A resting priced order (`account.op_limit_create`, `account.op_limit_cancel`), 8 strings. Same root, other sense and correct — the ORDER tabs are not limit orders: `trade.tab_single` "Unique" and `trade.tab_scaled` "Échelonné". |
| order | ordre | Anything resting on or filled from the book (`account.order_th`, `market.col_order`). |
| operation | opération | One chain action, e.g. a transfer or a limit-order creation (`account.unknown_operation`, `misc.operation_type`), 70 strings. Same root, other sense and correct — the abbreviation "Ops" stays the loanword where the English keeps it: `proposal.enclosed_ops` "Ops incluses", `txbuilder.added_body_tpl`, `account_net.twin_count` (byte-identical to English). |
| fee | frais | The chain fee an operation pays (`barter.fee_payer`, `account.resolving_fee`, `vesting.fee`), 182 strings. Never **coût** — same root, other sense and correct as they stand, it is cost in the abstract: `prediction.avg_cost`, `prediction.mixed_cost`, `prediction.zero_cost`, `prediction.history_unavailable`, `prediction.portfolio_hint` (average cost), `menu.d_fees`, `help.topic_fees_text`, `help.topic_fees_body` (what it costs), `help.topic_bitshares_body` (low cost), `help.topic_committee_body` (raise everyone's costs), `help.topic_dex-trading_body` (the cost of size), `help.topic_credit_body`, `help.topic_trollbox_body`, `help.topic_settings_body` (the privacy cost), `help.topic_airdrop_body`, `help.topic_translation-limitations_body` (the costly case), `fees.network_percent_of_fee_unavailable_member_cos`. Leave them. |
| transaction | transaction | A signed bundle of operations (`proposal.could_not_prepare_the_transaction`, `explorer.tx_title_prefix`), 78 strings. Same root, other sense and correct — broadcasting it is a different verb: `common.status_broadcasting` "Diffusion…". |
| block | bloc | A block in the explorer (`explorer_blocks.title`, `market.th_block`), 90 strings. Same root, other sense and correct — a *head* block is not a lock: `explorer.head_prefix` "Tête #". And the wallet lock buttons, `shell.lock` "Verrouiller" and `shell.unlock` "Déverrouiller", are near-collisions for anyone searching "verrou": they mean LOCK, never block. |
| memo | mémo | The optional public note on a transfer (`transfer.memo_label`, `gateway.memo_label`), 34 strings. Same root, other sense and correct — the key that decrypts it keeps the loanword "clé memo", without the accent: `transfer.no_memo_key`, `vote.no_memo`, `proposal.inner_memo_needs_both_accounts_to_have_a_memo`. |
| brainkey | phrase de récupération | The ordered word list that IS the backup (`wallet.brainkey` "Phrase de récupération", `createaccount.step_brainkey` "Phrase de récupération", `help.topic_wallets_body`, `help.topic_backups_body`), 42 strings. Feminine, as the shipped prose has it ("Une phrase de récupération est générée", `splash.step2_d`). Never "clé mentale" — it is not a password. The prose says "une suite de mots" where it glosses the word list. Retired: "brainkey" — the old loanword survives only code-bound: the `#/create-wallet-brainkey` route hash in `wallet.console_hint` and in `help.topic_sitemap_body`; both stay byte-verbatim as router identifiers. |
| witness | validateur de blocs | Block producer (`explorer.th_witness` "Validateur de blocs", `vote.join_as_witness` "Devenir validateur de blocs", `asset.witness_fed_note` "Alimenté par les validateurs de blocs : tous les validateurs de blocs actifs peuvent publier."), 38 strings (13 singular, 25 plural). `account.op_witness_join` is "Adhésion comme validateur de blocs", not "de validateur de blocs". Retired: "témoin" — 0 strings. Counter-example form: `témoin` (nothing ships it; do not reintroduce it). Same root, other sense and correct — "producteurs de blocs" appears in `help.topic_witnesses_body` as the *definition* of a validateur de blocs, not as a replacement for it. |
| committee | comité | Elected members that set fees and chain parameters (`vote.join_committee`, `help.topic_voting_body`), 24 strings. No other meaning of the word appears anywhere in the dictionary. |
| worker | proposition de grant | Paid proposal funded by the chain (`menu.p_worker` "Créer une proposition de grant", `help.topic_workers_title` "Propositions de grant" — 36 translated strings carry grant: 17 singular, 21 plural, 3 keys both). Retired: "travailleur" — 0 strings. Counter-example form: `travailleur` (nothing ships it; do not reintroduce it). Same root, other sense, correct as they stand — "travail/travaux" is the work itself, never the proposal: `help.topic_blockchain_body`, `help.topic_translation-limitations_body`, `help.topic_workers_body`, `menu.blurb_labs`, `proposal.multisig_story`. Code, not prose — the get_all_workers identifier in `vote.hide_legacy_title` and the `#/create-worker` route hashes in `help.topic_sitemap_body`, `vote.empty_hint` stay byte-verbatim. |
| proxy | proxy | The account your votes follow — all 19 shipped strings keep the loanword (`vote.proxy_row`, `vote.what_is_a_proxy`, `vote.proxy_aria`, `help.topic_voting_body`, `help.topic_voting_text`). Counter-example form: **délégué** — never introduce it. Four strings carry the stem, and none is a proxy: same root, other sense, they are the chain's own name "preuve de participation déléguée" in `help.topic_bitshares_text`, `help.topic_bitshares_body`, `help.topic_blockchain_body` and `help.topic_witnesses_body`. |
| slate | slate | A named set of witness votes (`vote.in_sync`, `vote.sent_middle`, `help.topic_tickets_body`), 7 strings. Never "liste" — same root, other sense, correct as they stand: this app has its own list pages, `menu.p_lists` "Listes de comptes". |
| vesting | vesting | A time-locked balance (`vesting.title`, `referrals.vesting_balances`), 49 strings. Never "acquisition" or "consolidation" (0 strings each). Same root, other sense and correct — the adjectival form is a participle: `vesting.instant_fully_vested` "instantané (entièrement acquis)". |
| proposal | proposition | Includes create_worker proposals (`proposal.create_proposal`, `menu.p_proposals`), 94 strings. |
| ticket | stake de vote | A vote-locked stake (`ticket.create_ticket` "Créer un stake de vote", `menu.p_tickets` "Stakes de vote", `help.topic_tickets_title` "Stakes de vote verrouillé"), 33 strings carrying the compound — 21 singular, 12 plural. Retired: "ticket" — the loanword survives only code-bound (the `%(ticket)s` placeholder in `account.sum_ticket_update`) and in the `#/tickets` route link. "Billet" still reads as a bus ticket (0 strings). |
| HTLC | HTLC | Never expanded in UI chrome, 27 strings. Same root, other sense and correct — the help article GLOSSES it in prose rather than naming it: `help.topic_htlc_body` "contrat à verrouillage temporel et haché", `htlc.list_sub` "derrière un hachage". |
| liquidity pool | pool | Loanword for a CPMM market (`pool.create_title`, `pool.mine_title`), 124 strings. "Pool de liquidité" is the gloss the titles use — the complete set is `menu.p_pools`, `pools.title`, `pool_detail.title`, `help.topic_pools_title`, `help.topic_pools_body`, `help.topic_sitemap_body`, `pool.map_takeover`, `tour.s5_body`, `splash.step3_d`, `about.s2_body`, `seo.title_pools`, `seo.desc_pools`. One word in prose, the gloss in titles: not three words. Never "réserve de liquidité". |
| credit offer | offre de crédit | A lender's offer on the credit desk (`credit.credit_offer`, plural in `account.no_credit_offers_for_this_account`), 11 strings. Same root, other sense and correct — a loan already struck against one is a deal, `credit.deal` (29 strings, loanword), and the two are never interchanged. |
| deal | deal | A credit deal (`credit.deals_on_this_offer` "Deals sur cette offre") or, on the prediction desk, a position held. Loanword: "accord" would read as a contract, and the same spelling is already the French word for a bargain. |
| gateway | passerelle | An external bridge operator (`gateway.s1` "Fil d'état des passerelles", `menu.d_gateway`), 29 strings. Never "portail". |
| node | nœud | A chain API endpoint (`settings.th_node`, `settings.add_node`, `settings.discover_none`), 66 strings. |
| chain | chaîne | The BitShares ledger (`txbuilder.chain_prefix`, `settings.es_note`), 118 strings. Same root, other sense and correct — the protocol's own name keeps its English spelling where English says blockchain: `explorer.tab_blocks` "Blockchain", `seo.title_explorer` "Explorateur de blockchain", `about.hero_lede`. |
| feed | flux | A price feed (`assets_feed.title` "Publier le flux", `asset.producers_title`, `market.stat_feed`), 69 strings. Same root, other sense and correct — the VERB "publier" is shared with proposal publishing (`proposal.create_proposal`), which is a different concept; no clash in practice. |
| settlement | règlement | Forced settlement of a bitasset (`prediction.settlement`, `borrow.settlement_bids_op_45`), 47 strings. Never the legal sense of settlement; the product sense is the only one shipped. |
| referrer | parrain | The account that brought a user in (`referrals.referrer`, `menu.p_referrals`), 19 strings; the plural page title is `referrals.referrals` "Parrainages". Same root, other sense and correct — a **registrar** is a different actor and keeps the loanword: `referrals.registrar_referrer` "Registrar et parrain". |
| hop | saut | One graph step on the market, pool or account maps (`pool.map_a_hops`, `pool_net.verdict_path`, `account_net.depth_2`, `xrate.empty`), 10 strings. Never "hop". |

**Deliberate loanwords** (smartcoin, stake, proxy, slate, vesting,
ticket, HTLC, pool, swap, worker, deal, registrar, quote): each names something
BitShares invented or a piece of its own jargon, and a literal translation reads
as a different concept to a French speaker. They are still translated
surrounding text, and the surrounding text is where the explanation lives
(`help.topic_backups_body`, `help.topic_htlc_body`, `help.topic_pools_body`).

**Loanwords kept because French technical usage keeps them** — acronyms and
product names, never spelled out: DEX, API, BTS, BitShares, core, PnL,
Spotlight, Trollbox, Airdrop, the `Swap/Stake` column headers, and the
indicator and ratio acronyms SMA, EMA, RSI, MACD, VWAP, Stochastic, CPMM, CER,
MCR, MSSR, NFT, PMA, UIA, FBA, LP, TxBuilder. The fill run printed every value
left byte-identical to English, so the list is checkable rather than implied:
see `tooling/apply_i18n_fr_chunkA.py` and `tooling/apply_i18n_fr_chunkB.py`
(their `KEPT_ENGLISH` tables, 47 + 124 keys).

**Never translate** (byte-verbatim in every dictionary): `%(name)s`
placeholders, URLs, object ids like `1.2.105`, asset symbols like `BTS`, theme
ids (`ref-ui-theme`, `dex-ux-theme`, `vanilla-ui-theme`), network ids
(`mainnet`, `testnet`, `devnet`) and persisted theme ids (`original-blue`,
`light`, `dark`).
