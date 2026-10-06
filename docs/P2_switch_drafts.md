# Pass 2 switch-commit drafts (P2-3a; nothing here is applied)

**Status.** Drafts for Isaiah's decision checkpoint (P51). Nothing below changes a file until the
P2-3b switch commit, and only as approved there. Every "old" text is copied from the files at commit
`checkpoint: P2-2b`; every ⟨…⟩ is decided at the checkpoint or filled after P2-4.

Contents:
1. `ofilt/drift/schema.py` (P50)
2. `targets.HEDGE_GAP_FOR` (AM-03), `io` registration of `y_1306_oc` and `blind.FX_NAMES` (P52)
3. Spec amendments AM-03 to AM-06 (SPEC_AMENDMENTS JSONL form)
4. `docs/replacements/DATA_DICTIONARY.md` for the 60-column panel
5. The complete test-change table
6. Points for the checkpoint found while drafting

---

## 1. `ofilt/drift/schema.py` (P50)

`PRE_OPEN_FEATURES` stays exactly the 20 Pass 1 columns. The new group `PRE_OPEN_ROBUSTNESS` is
appended to `GROUPS` last. `select_features` refuses it without any code change, because
`ALLOWED_FEATURES` is still `PRE_OPEN_FEATURES | DERIVED | SYNTHETIC`.

```diff
-AT_OPEN = frozenset({"ao_gap_adj", "ao_gap_raw", "ao_topix_gap"})  # uses the 09:00 print
-TARGET_INPUTS = frozenset({"y_oc", "y_topix_oc"})             # outcomes of day t's session
+AT_OPEN = frozenset({"ao_gap_adj", "ao_gap_raw", "ao_topix_gap",   # uses the 09:00 print
+                     "ao_1306_gap_raw", "ao_1306_gap_adj",        # P50: the 1306 hedge gap (AM-03)
+                     "ao_topix_gap_tradj"})                       # P50, P40: TOPIX gap + TR component; fallback path only
+TARGET_INPUTS = frozenset({"y_oc", "y_topix_oc", "y_1306_oc"})  # outcomes of day t's session; y_1306_oc: P50
 PROVENANCE = frozenset({
     "open", "close", "prev_close",                            # auction / target information
     "window_start_utc", "window_end_utc",
     "usdjpy_bars", "usdjpy_stale_start_min", "usdjpy_stale_end_min",
     "eurusd_bars", "eurusd_stale_end_min",
+    # P50: bar counts and endpoint staleness of the XAU and Japan 225 dark windows. The P42 rule reads
+    # the n225 staleness as a sample filter (like earn_flag); never regressors.
+    "xau_bars", "xau_stale_start_min", "xau_stale_end_min",
+    "n225_bars", "n225_stale_start_min", "n225_stale_end_min",
 })
-CONTEMPORANEOUS = frozenset()  # Pass 2 placeholder (e.g. post-open FX); empty in Pass 1
+CONTEMPORANEOUS = frozenset({"c_usdjpy_sess_ret", "c_eurusd_sess_ret"})  # P50: session FX 09:00 JST -> close of t; never a feature
+# P50: known by 08:59 JST but outside the primary allowlist; robustness designs only (refused by
+# select_features). gotobi_day is a calendar flag (P48).
+PRE_OPEN_ROBUSTNESS = frozenset({
+    "xau_ret", "xau_rv", "xau_bv", "n225_ret", "usdjpy_us_ret", "ewj_oc_jpy", "gotobi_day",
+})

 GROUPS: dict[str, frozenset] = {
     ...
     "CONTEMPORANEOUS": CONTEMPORANEOUS,
+    "PRE_OPEN_ROBUSTNESS": PRE_OPEN_ROBUSTNESS,
 }

 _FORBIDDEN_REASON = {
     ...
     "CONTEMPORANEOUS": "contemporaneous with the session; not pre-open",
+    "PRE_OPEN_ROBUSTNESS": "pre-open robustness control (P50); robustness designs only, never a model feature",
 }
```

Resulting sizes: KEYS 2, PRE_OPEN_FEATURES 20, EXCLUSION_FLAGS 2, INFORMATIONAL 1, ROBUSTNESS_ONLY 1,
AT_OPEN 6, TARGET_INPUTS 3, PROVENANCE 16, CONTEMPORANEOUS 2, PRE_OPEN_ROBUSTNESS 7; total 60.

**New test (P50):** pin `PRE_OPEN_FEATURES` to the 20 names, and M7's features
(`models/gbm.M7.features`) to `tuple(sorted(those 20))`:

```python
class TestP50FeaturePins(unittest.TestCase):
    PASS1 = {"usdjpy_ret", "usdjpy_rv", "usdjpy_bv", "eurusd_ret", "eurusd_rv", "spy_oc", "ewj_oc", "fcx_oc",
             "copx_oc", "us_n_sessions", "window_hours", "gap_adj_lag1", "oc_lag1", "range_lag1",
             "topix_oc_lag1", "boj_day", "sq_day", "sq_major", "exdiv_day", "div_exdate"}

    def test_pre_open_features_and_m7_unchanged(self):
        self.assertEqual(set(SC.PRE_OPEN_FEATURES), self.PASS1)       # P50: exactly the 20 Pass 1 columns
        from ofilt.drift.models.gbm import M7
        self.assertEqual(M7.features, tuple(sorted(self.PASS1)))       # M7's inputs unchanged (P43/P50)
        for c in SC.PRE_OPEN_ROBUSTNESS | SC.CONTEMPORANEOUS:
            with self.assertRaises(SC.FeatureNotAllowedError):
                SC.select_features(pd.DataFrame({c: [0.0]}), [c])
```

## 2. `targets`, `io` and `blind` (AM-03; P52)

```diff
 # ofilt/drift/targets.py
-# Gap column of each permitted hedge. Pass 2 (1306 ETF) must add its pair explicitly.
-HEDGE_GAP_FOR = {"y_topix_oc": "ao_topix_gap"}
+# Gap column of each permitted hedge. AM-03 (P18): the 1306 ETF's open->close, with its own
+# dividend-adjusted gap (Flag 6 fixed on the hedge leg). The TOPIX pair stays for the fallback path.
+HEDGE_GAP_FOR = {"y_topix_oc": "ao_topix_gap", "y_1306_oc": "ao_1306_gap_adj"}

 # ofilt/drift/io.py, _register_real_targets
-        for c in ("y_oc", "y_topix_oc"):
+        for c in ("y_oc", "y_topix_oc", "y_1306_oc"):   # P52: y_1306_oc registered (label dev_real:y_1306_oc)

 # ofilt/drift/blind.py (P52: a data-list exception to the Flag 2 freeze)
 FX_NAMES = frozenset({
     "usdjpy_ret", "usdjpy_rv", "usdjpy_bv", "eurusd_ret", "eurusd_rv",
     "usdjpy_bars", "eurusd_bars", "usdjpy_stale_start_min", "usdjpy_stale_end_min",
-    "eurusd_stale_end_min", "e_pos", "e_neg", "jumpshare", "rv_per_bar"})
+    "eurusd_stale_end_min", "e_pos", "e_neg", "jumpshare", "rv_per_bar",
+    # P52: Pass 2 predictors, never fingerprint-compared with targets. gotobi_day is a calendar flag, not added.
+    "xau_ret", "xau_rv", "xau_bv", "xau_bars", "xau_stale_start_min", "xau_stale_end_min",
+    "n225_ret", "n225_bars", "n225_stale_start_min", "n225_stale_end_min",
+    "usdjpy_us_ret", "ewj_oc_jpy", "c_usdjpy_sess_ret", "c_eurusd_sess_ret"})
```

Unchanged: `targets.past_beta`'s default hedge stays `y_topix_oc`, because `tools/report_A7.py`
(the TOPIX A7 report, which stays as it is) relies on it. The A7 rerun on 1306 (P2-5) passes the
hedge explicitly.

## 3. Spec amendments (SPEC_AMENDMENTS JSONL form)

**Constraint (tests/test_spec.py, verbatim-diff test).** The live spec must have the same 70 lines as
`analysis_spec_dev_v1.VERBATIM.yaml`, and each changed line has exactly one JSONL record with its
exact old and new text. So every amendment is a one-for-one line replacement, and no line can carry
two records. AM-05 and AM-06 both concern `robustness.others` (line 42); see the placement options
under AM-05.

### AM-03 (⟨date⟩, Isaiah): the hedge is 1306 (P18)

**Change.** `target.hedge_oc_column`: `y_topix_oc` (placeholder) -> `y_1306_oc`, the open->close
return of NEXT FUNDS TOPIX ETF (1306). Its gap pair is `ao_1306_gap_adj`, adjusted with 1306's own
distributions (P39, P47; Flag 6 fixed on the hedge leg).

**Contingent on** D8 (open-auction timing; default (a)) and D9 (A7 on 1306: expanding lowest on common
rows for every ticker). If 1306 fails its checks, P18's fallback applies instead (raw primary; TOPIX
index secondary, with the P55 staleness reading and `ao_topix_gap_tradj`). AM-03 then reads
⟨fallback text⟩.

**Lines (exact):**
```jsonl
{"id": "AM-03", "line": 14, "old": "  hedge_oc_column: y_topix_oc          # PLACEHOLDER; 1306 open->close after Pass 2", "new": "  hedge_oc_column: y_1306_oc           # AM-03 (P18): 1306 open->close; gap pair ao_1306_gap_adj"}
```

### AM-04 (⟨date⟩, Isaiah): panel hashes after the Pass 2 rebuild (P10 superseded)

**Change.** Both panel hashes become the P2-4 outputs (60 columns: the 41 old ones plus 19 appended,
P50, P51). The old-column sources follow Isaiah's decision of 2026-10-05: dev = the original
`panel_dev.csv` (`736636…`); sealed = the frozen build run on the Mac (`138e5e21…`), Flag 16.
BLIND_FIT_LOG lines 1–6 keep referring to `736636…`, which is archived under its hash
(`DATA/archive/panel_dev_736636031ca1.csv`).

**Lines (exact; the new hashes are filled after P2-4):**
```jsonl
{"id": "AM-04", "line": 4, "old": "  dev_panel_sha256: 736636031ca1532548744440d3df9465eda3126ed93bdcdad2df06964ee36a42", "new": "  dev_panel_sha256: ⟨P2-4 dev panel SHA-256⟩"}
{"id": "AM-04", "line": 7, "old": "  sealed_panel_sha256: 9c18a6c106356139a375ecd7b3e6eaa085d937341c02817021003a4451c6b826   # superseded after Pass 2 rebuild", "new": "  sealed_panel_sha256: ⟨P2-4 sealed panel SHA-256⟩   # AM-04: Pass 2 rebuild (60 columns); supersedes 9c18a6c1… (P10)"}
```

### AM-05 (⟨date⟩, Isaiah): the Nikkei-proxy robustness row (P42, D7; P56 skeleton)

**Change (skeleton; every ⟨…⟩ is decided at the checkpoint):**
- **Design.** Primary design + `n225_ret`, with a ⟨ticker-specific (P19 default for market controls) | common⟩ slope. Tested coefficient: b on `usdjpy_ret`.
- **Estimation sample.** Rows whose night has `n225_stale_start_min <= 5` and `n225_stale_end_min <= 5` (P42 as proposed; threshold ⟨5⟩). A night whose window has no Japan 225 bar has every `n225_*` column empty, so it is ineligible. Dev eligibility starts at ⟨date⟩: the 08:59 JST price is fresh from 2018-04-13 (P2-1).
- **Reported (P56).** b with and without `n225_ret` on the **same eligible rows**, next to the full-sample primary b, with the same inference (DK, lag rule on the eligible dates).
- **Tier-(ii) criterion (P32, P56).** ⟨operational criterion, e.g. a bound on the change in b, decided at the checkpoint⟩.
- **Yen EWJ as a tier-(ii) check (P56).** ⟨yes | no⟩.

**Placement (line constraint).** ⟨Option A: one record for line 42 with id "AM-05+AM-06", the Nikkei
row written in the list as `{nikkei_proxy_p42: "<rule>"}` | Option B: amend `test_spec`'s
equal-length rule so that recorded inserted lines (`"old": null`) are allowed; AM-05 then gets its
own key under `robustness`, and `test_docs_d3`'s key list changes too⟩.

```jsonl
{"id": "AM-05", "line": ⟨42 (option A, shared) | inserted (option B)⟩, "old": ⟨…⟩, "new": "⟨nikkei_proxy_p42 with the rule above⟩"}
```

### AM-06 (⟨date⟩, Isaiah): the Pass 2 robustness rows (P33 list; P56 skeleton)

**Change (skeleton).** Line 42 (`robustness.others`):
- `ewj_yen_denominated_REQUIRES_PASS2` -> `ewj_yen_denominated`: primary + `ewj_oc_jpy` ⟨slope⟩. `ewj_oc_jpy` is NaN on the EWJ-stale nights (3 in 2015–16) ⟨rows dropped | …⟩.
- add `xau_control`: primary + `xau_ret` ⟨slope⟩; nights with an empty `xau_ret` ⟨dropped⟩.
- add the Nikkei row (AM-05).
- add `mechanism_session_fx_gotobi`: primary + `c_usdjpy_sess_ret` + `c_eurusd_sess_ret` ⟨+ `gotobi_day` ⟨and e × gotobi_day⟩⟩. Not tradable (PLAN §6, §9.2).
- each new row reports ⟨…⟩, on ⟨sample⟩ (P56).

```jsonl
{"id": "AM-06", "line": 42, "old": "  others: [beta_rolling_250, raw_target, copx_to_fcx, ewj_yen_denominated_REQUIRES_PASS2, exclusion_d_plus_2, exclude_audit_flag, exclude_boj_day, exclude_sq_major, post_2024_11_05_indicator_CONFIRMATION_ONLY, per_ticker_slopes_holm]", "new": "⟨the list above⟩"}
```

## 4. `docs/replacements/DATA_DICTIONARY.md` for the 60-column panel

Full replacement text below. Its groups table follows `test_docs_d5`'s format; the P20 sentences
that test pins are unchanged.

````markdown
# Analysis panel — data dictionary

Built by `build/pass2/build_panel_p2.py` (Pass 2; append-only, P51). The frozen `build/pass1/build_panel.py` produces the 41 Pass 1 columns from `Book2.xlsx`, the two Dukascopy FX files and `events_firm.csv` / `events_boj.csv`. The 19 Pass 2 columns are appended from `newbloombergdata_fixed.xlsx` (1306, its distributions, TOPIX total return) and the XAU and Japan 225 Dukascopy files. Input, code and output SHA-256 hashes are in `MANIFEST.json`.

One row per (ticker, Tokyo trading day). Tickers 5713, 5711, 5706. Returns are log returns.

| File | Span | Rows | Use |
|---|---|---|---|
| `panel_dev.csv` | 2015-01-06 → 2021-12-30 | 5,124 | Development: synthetic-only model building until `spec-dev-v1`, then the first look (PLAN §8) |
| `panel_confirm_SEALED.csv` | 2022-01-04 → 2026-03-05 | 3,057 | **Do not open** until `prereg-v1` is tagged. 1,019 trading days; T_conf = 1013 dates with a non-excluded row. Its Pass 1 hash `9c18a6c1…` is superseded by AM-04 |

Both panels have 60 columns: the 41 Pass 1 columns, then the 19 Pass 2 columns. The 41 old columns are the original strings, never recomputed: dev's are the original Pass 1 panel's (`736636…`), sealed's the frozen build's output on the Mac (`138e5e21…`; Flag 16, Isaiah 2026-10-05).

## Schema groups — which columns may be features

Every column is in exactly one group, defined as explicit frozensets in `ofilt/drift/schema.py` (DECISIONS P20). Unknown columns are refused everywhere, and nothing selects columns by prefix. **Only PRE_OPEN_FEATURES may be model features.** Being unprefixed does not make a column a feature: `open`, `close`, `prev_close` and `audit_flag` are unprefixed and forbidden. PRE_OPEN_ROBUSTNESS columns are known before the open but enter only the pre-listed robustness designs (P50).

| Group | n | Columns | Role |
|---|---|---|---|
| KEYS | 2 | `date`, `ticker` | Identifiers |
| PRE_OPEN_FEATURES | 20 | listed below | Known by 08:59 JST on day t; the only allowed features (unchanged in Pass 2, P50) |
| EXCLUSION_FLAGS | 2 | `earn_flag`, `news_flag` | Sample filters (D, D+1), never features |
| INFORMATIONAL | 1 | `mech_flag` | Recorded, not used |
| ROBUSTNESS_ONLY | 1 | `audit_flag` | Outcome-identified; a robustness exclusion only (P08) |
| AT_OPEN | 6 | `ao_gap_adj`, `ao_gap_raw`, `ao_topix_gap`, `ao_1306_gap_raw`, `ao_1306_gap_adj`, `ao_topix_gap_tradj` | Known only at the 09:00 auction; decomposition, f and the hedge gap only |
| TARGET_INPUTS | 3 | `y_oc`, `y_topix_oc`, `y_1306_oc` | Outcomes; never features |
| PROVENANCE | 16 | `open`, `close`, `prev_close`, `window_start_utc`, `window_end_utc`, `usdjpy_bars`, `usdjpy_stale_start_min`, `usdjpy_stale_end_min`, `eurusd_bars`, `eurusd_stale_end_min`, `xau_bars`, `xau_stale_start_min`, `xau_stale_end_min`, `n225_bars`, `n225_stale_start_min`, `n225_stale_end_min` | QA, prices, bar counts and staleness; never features (P42 reads the n225 staleness as a sample filter) |
| CONTEMPORANEOUS | 2 | `c_usdjpy_sess_ret`, `c_eurusd_sess_ret` | Session FX, 09:00 JST → the close of day t; never features |
| PRE_OPEN_ROBUSTNESS | 7 | `xau_ret`, `xau_rv`, `xau_bv`, `n225_ret`, `usdjpy_us_ret`, `ewj_oc_jpy`, `gotobi_day` | Known by 08:59 JST; robustness designs only (P50), refused by `select_features` |

### PRE_OPEN_FEATURES (known by 08:59 JST on day t)

| Column | Definition |
|---|---|
| `usdjpy_ret` | log USD/JPY from the previous TSE close (15:00 JST to 2024-11-04, 15:30 JST from 2024-11-05) to 08:59:00 JST. Positive = yen weakens. **H1 regressor.** |
| `usdjpy_rv`, `usdjpy_bv` | Realized variance and bipower variation of 1-minute returns over the same window. Dukascopy's flat rollover bars bias BV down. |
| `eurusd_ret`, `eurusd_rv` | Same window for EUR/USD. Positive = dollar weakens. `eurusd_ret` is in the primary design, which makes b the yen-specific pass-through; its coefficient is H3 (P14, P15). |
| `spy_oc`, `ewj_oc`, `fcx_oc`, `copx_oc` | Sum of US open→close log returns over the NY sessions inside the window (NY dates from t_prev to t−1). 0 if there was no US session; NaN on 3 nights where EWJ was stale. Primary controls: `spy_oc`, `copx_oc`. `ewj_oc` and `fcx_oc` are robustness only (P19). |
| `us_n_sessions` | Number of US sessions in the window (0 on US holidays; up to 7 in Golden Week). Written as a float (e.g. `1.0`). |
| `window_hours` | Window length (18 h on normal nights; 258 h max). |
| `gap_adj_lag1`, `oc_lag1`, `range_lag1`, `topix_oc_lag1` | The previous session's gap, open→close, log(high/low), and TOPIX open→close. Not in the primary design (P19). |
| `boj_day` | BoJ policy announcement day (announced intraday). Exclusion is a robustness row. |
| `sq_day`, `sq_major` | SQ day (2nd Friday, moved to the prior trading day if a holiday); major = Mar/Jun/Sep/Dec. Major-SQ exclusion is a robustness row. |
| `exdiv_day`, `div_exdate` | Ex-dividend day and the yen amount (cash items with the same ex-date summed). |

**Model-side features** (built by `schema.select_features`; deterministic, row-wise, no estimated parameters):
- `long_window` = 1[window_hours > 18]
- `jumpshare` = clip((rv − bv)/rv, 0, 1)
- `rv_per_bar` = usdjpy_rv / usdjpy_bars. `usdjpy_bars` is the only PROVENANCE column a derived feature may read.
- `e_pos` = max(usdjpy_ret, 0) and `e_neg` = min(usdjpy_ret, 0)
- `no_us_session` = 1[us_n_sessions = 0]
- `noise_N01`: a seeded N(0,1) column generated by a model itself (M7) for importance calibration. It is not a panel column.

Thresholds such as `highrv` (rv_per_bar above its development median, 1.2950114214e-08) are applied in the design, not stored.

### PRE_OPEN_ROBUSTNESS (known by 08:59 JST; robustness designs only, P50)

| Column | Definition |
|---|---|
| `xau_ret`, `xau_rv`, `xau_bv` | XAU/USD (Dukascopy, bid) log return, realized variance and bipower variation over the `usdjpy_ret` window, by the same frozen rule (P41). |
| `n225_ret` | Japan 225 CFD (Dukascopy, bid) log return over the same window (P42). Used only on nights where both window endpoints are at most 5 minutes stale (P42; AM-05). The 08:59 JST price is fresh on every Tokyo day only from 2018-04-13 (P2-1). |
| `usdjpy_us_ret` | Sum over the night's NY sessions (the dates counted by `us_n_sessions`) of ln(USD/JPY at the NY close / at the NY open). Open 09:30 ET; close 16:00 ET, or 13:00 ET on the 23 NYSE early closes; DST from the tz database (P49). Exactly 0.0 when `us_n_sessions` = 0, and possibly also on a night with sessions (amended assertion, 2026-10-05). |
| `ewj_oc_jpy` | `ewj_oc` + `usdjpy_us_ret`: EWJ in yen (P49). NaN exactly where `ewj_oc` is NaN. |
| `gotobi_day` | 1 if a nominal date (the 5th, 10th, 15th, 20th, 25th, 30th, and the month's last calendar day) lands on day t, rolling a non-trading nominal date back to the preceding trading day (P48). Dev 529 of 1,708 dates; confirmation 319 of 1,019. |

On a night with no XAU (or Japan 225) bar in the window, every `xau_*` (or `n225_*`) column of that night is empty, including the bar count and staleness. The P42 rule therefore treats such a night as ineligible.

### Flags (never features)

| Column | Definition |
|---|---|
| `earn_flag` | 1 on trading days D and D+1 of each 決算短信 release (D = first trading day ≥ release date). |
| `news_flag` | Same D/D+1 rule for standalone forecast revisions, special losses and delay notices. Forecast evaluation keeps day D (P27). |
| `mech_flag` | Day of mechanical disclosures (corrections, consolidation restatement). Not an exclusion. |
| `audit_flag` | D/D+1 of outcome-identified audit candidates. **Robustness only**: using it in the primary spec selects on the outcome. |

### At-open (`ao_`, known only once the 09:00 auction prints)

These columns are **not features in any specification**. The auction-conditional specification is retired (P16). They build the gap and close-to-close targets for the decomposition and the fraction unpriced f (P24), and the hedge gap.

| Column | Definition |
|---|---|
| `ao_gap_adj` | log(open_t / (close_{t−1} − dividend_t)), the ex-dividend-adjusted gap. |
| `ao_gap_raw` | Unadjusted gap. |
| `ao_topix_gap` | TOPIX gap. Not dividend-adjusted (Flag 6); `ao_topix_gap_tradj` is the adjusted version. |
| `ao_1306_gap_raw` | 1306 gap, log(open_t / close_{t−1}). |
| `ao_1306_gap_adj` | log(open_t / (close_{t−1} − D_t)), with D_t the 1306 distribution with ex-date t, else 0. D_t is the stored corrected amount (P39, P47; never recomputed). The hedge gap under AM-03. |
| `ao_topix_gap_tradj` | `ao_topix_gap` + [ln(TR_t/TR_{t−1}) − ln(PR_t/PR_{t−1})]. TR is the TOPIX total return (TPXDDVD Index), PR Book2's TOPIX close, both without 2020-10-01. Fallback path only (P40). |

### Targets (`y_`; never features)

| Column | Definition |
|---|---|
| `y_oc` | Stock open→close on day t. |
| `y_topix_oc` | TOPIX open→close on day t; the Pass 1 placeholder hedge, and the fallback secondary's hedge (P18). |
| `y_1306_oc` | 1306 (NEXT FUNDS TOPIX ETF) open→close on day t; the hedge under AM-03 (P18). |

The primary target is built in model code (`ofilt/drift/targets.py`), not stored: `abn_oc` = y_oc − β_{i,t−1}·hedge_oc. β_{i,t−1} is the past-only **expanding** OLS slope on non-excluded rows (at least 250 observations, lagged one day, continued across the dev/confirmation boundary; P17). The secondary target is `raw_oc` = y_oc. `gap_abn` and `cc_abn` serve the decomposition and f.

### Contemporaneous (never features)

| Column | Definition |
|---|---|
| `c_usdjpy_sess_ret`, `c_eurusd_sess_ret` | ln(P(t, close) / P(t, 09:00:00 JST)): the session move from the 09:00 JST price (close of the bar labeled 08:59) to the TSE close of day t itself (15:00 JST through 2024-11-04, 15:30 JST from 2024-11-05). For the mechanism specification only (PLAN §6). |

### Provenance added in Pass 2 (never features)

| Column | Definition |
|---|---|
| `xau_bars`, `n225_bars` | 1-minute bars between the window's endpoint bars, as `usdjpy_bars`. Written as integers; the Pass 1 `usdjpy_bars` and `eurusd_bars` are written as floats (e.g. `1079.0`). |
| `xau_stale_start_min`, `xau_stale_end_min`, `n225_stale_start_min`, `n225_stale_end_min` | Minutes between each endpoint's target bar label and the last bar at or before it, as `usdjpy_stale_*`. The P42 rule reads the n225 values as a sample filter. |

## Conventions baked in (verified, not assumed)

- Dukascopy bars are true UTC and start-labeled. The price at instant X is the close of the last bar labeled ≤ X − 1 min.
- Miner prices are adjusted for capital changes but not for cash dividends. This includes 5706's 10:1 split, ex-date 2026-09-29. Never mix these prices with the Math 86 `JPEquities.xlsx`.
- The stale TOPIX row for 2020-10-01 (the TSE outage) is dropped, in TOPIX and in the TOPIX total return.
- The XAU and Japan 225 windows are exactly the `usdjpy_ret` window (asserted at build time).
- The US session is 09:30–16:00 America/New_York, or to 13:00 on NYSE early closes (P49).
- The 41 Pass 1 columns are read back as strings and never recomputed; the 19 new columns are appended by date (P51).

## Verification status (October 2026)

- `events_firm.csv` has a `check_status` column. The 15 audit candidates and 5711's 2022-08-09 release were checked by hand: no corrections, no reclassification. The remaining rows come from the Deep Research report, validated statistically against price reactions.
- FCX 2016-01-11 (−22.5% open→close): checked, genuine; no data change.
- The event layer is unchanged by the Pass 2 rebuild.
- The Pass 2 inputs are validated in `reports/P2_1_inputs.md`.

## Not panel columns

- The index-staleness test of the TOPIX 09:00 print is a dev report (P55), not a column.
- The post-2024-11-05 indicator is built in model code (confirmation only; P33).
- MoF intervention dates: optional, not included.
````

## 5. The complete test-change table

Protocol: PASS2_ADDENDUM §5. All rows are for approval at the checkpoint; none is applied. Line
numbers are those at `checkpoint: P2-2b`. Rows 1–14 are addendum §5's switch-commit list; rows 15–24
were found while drafting.

| # | Test (line) | Current assertion | New assertion | Entry |
|---|---|---|---|---|
| 1 | `test_spec` (34–35) | dev hash `736636…` | the P2-4 dev-panel hash | AM-04 |
| 2 | `test_spec` (101) | `hedge_oc_column == "y_topix_oc"` | `"y_1306_oc"` | AM-03 |
| 3 | `test_spec` (59–60) | amended lines {33, 43–46, 62}; ids {AM-01, AM-02} | plus 4, 7 (AM-04), 14 (AM-03) and the AM-05/AM-06 lines; ids plus AM-03…AM-06 (⟨placement option⟩) | AM-03…06 |
| 4 | `test_schema` (27–31) | sizes 20 / 10 / 3 / 0 | PRE_OPEN 20 (unchanged), PROVENANCE 16, AT_OPEN 6, CONTEMPORANEOUS 2; add PRE_OPEN_ROBUSTNESS 7 | P50 |
| 5 | `test_schema` (35) | `len(cols) == 41` | 60 | P50 |
| 6 | `test_schema`, new | — | `TestP50FeaturePins` (section 1) | P50 |
| 7 | `test_docs_d1` (98, 100) | hedge `y_topix_oc`; `HEDGE_GAP_FOR == {y_topix_oc: ao_topix_gap}` | `y_1306_oc`; both pairs | AM-03 |
| 8 | `test_docs_d1` (111) | `ewj_yen_denominated_REQUIRES_PASS2` in the list | the AM-06 name | AM-06 |
| 9 | `test_docs_d1` (120–127) | group counts with CONTEMPORANEOUS 0; 41 columns | P50 counts plus `PRE_OPEN_ROBUSTNESS: 7`; 60 | P50 |
| 10 | `test_docs_d3` (110–113) | the exact robustness list | the AM-06 list | AM-06 |
| 11 | `test_docs_d3` (118) | sealed hash starts `9c18a6c1` | the P2-4 sealed prefix | AM-04 |
| 12 | `test_docs_d3` (68–69) | every BLIND_FIT_LOG `panel_sha256` equals the spec's dev hash | equals the constant `736636031ca1…` (lines 1–6 are Pass 1 history) | AM-04, P51 |
| 13 | `test_docs_d5` (15–16, 26, 54, 60) | pin `c6aeded2f93a3cd5`; 9 groups; total 41; "all 41 columns" | the new pin; GROUPS + `PRE_OPEN_ROBUSTNESS`; 60 | P50 |
| 14 | `test_blind` (116–118) | `usdjpy_`/`eurusd_` columns ⊆ `FX_NAMES` | also every P52 column ⊆ `FX_NAMES` | P52 |
| 15 | `test_blind` (42), additive | `dev_real:y_topix_oc` registered | also `dev_real:y_1306_oc` | P52 |
| 16 | `test_lookahead` (21, 35, 38; real-dev and synthetic cases) | `REAL_COLS` and `perturb` use `y_topix_oc`/`ao_topix_gap`; `Spec.load()` hedge | add `y_1306_oc`, `ao_1306_gap_adj` to `REAL_COLS` and perturb them. Not purely additive: with AM-03 the spec-driven checks become 1306 checks; the TOPIX case needs a spec copy with `hedge_oc_column: y_topix_oc` ⟨keep it | drop it⟩ | AM-03 |
| 17 | `test_targets` (16–28 `synth_panel`; 39 `brute_beta`; 51, 72, 77, 82, 96) | synthetic panels carry only `y_topix_oc`/`ao_topix_gap`; `add_targets(df, spec)` | `synth_panel` also writes `y_1306_oc` (the hedge series) and `ao_1306_gap_adj`; `brute_beta` reads the spec's hedge. Without this, `add_targets` raises KeyError under AM-03 | AM-03 |
| 18 | `test_inference_b3` (16–29 `panel3`; 104, 119, 122, 152–153) | `panel3` writes `y_topix_oc`; `fit_market`/`decomposition` read the spec's hedge | `panel3` also writes `y_1306_oc` (same series) | AM-03 |
| 19 | `test_sim_b4` (32–33) | `decomposition` on `sim.synthetic_panel`, which writes only `y_topix_oc` | the test adds `df["y_1306_oc"] = df["y_topix_oc"]` before the call. `sim.py` is frozen and C7-hashed (D11) and must not change | AM-03 |
| 20 | `test_validation_c7` | report key | unchanged; the report is regenerated by the one C7 rerun (D16: where it runs), never edited | P51 |
| 21 | `test_docs_d4` (11) | Project file name for README `"README__2_.md"` | `"README.md"` (the Project now holds `README.md`; the byte comparison silently never runs in a sandbox) | Isaiah 2026-10-05 |
| 22 | `test_docs_p2` (`PINNED`) | the 2026-10-05 kit hashes | old → new hash for every kit doc edited at P2-6: at least `docs/DATA_PROVENANCE.md` and `docs/PASS2_INPUTS.json`; `docs/replacements/README.md` and `PLAN.md` if refreshed (README line 16 still says "`PLAN.md` (v2.2)") | P2-6 records |
| 23 | proposal | — | decisions P58 onward go in a new `docs/DECISIONS_P58_onward.md`, so `docs/DECISIONS_P37_onward.md` keeps its pin | Isaiah, to decide |
| 24 | `test_build_pass1_pin` | — | unchanged (P2-6 changes no `code` entry of PASS2_INPUTS.json) | — |

**Not affected (checked):**
- `tests/test_io.py` `test_load_dev` (5,124 rows, 1,708 dates, span): unchanged.
- `tests/test_lookahead.py` `TestA7Reference` rewrites `reports/A_hedge_efficiency.md` from the dev
  panel's `y_oc`/`y_topix_oc`. Those are old columns, byte-identical by construction, so the TOPIX
  report should come out byte-identical. To be confirmed in the switch-commit suite run.
- `inference.FORBIDDEN_TARGET_NAMES` derives from the groups, so the new predictor groups are refused
  as targets with no edit to `inference.py` (P50). `y_1306_oc` (TARGET_INPUTS) stays usable as a hedge.
- `tools/c7_mc.py` and `sim.py` never read the hedge column. The switch changes C7's staleness key
  only through the spec's SHA-256 (P51).

**Confirmation still to do.** This table comes from reading the code. A dry run of the switch on a
scratch copy (all of sections 1–3 applied, the P2-4 dev panel as DATA) would list every failing test
directly, before the switch commit. ⟨Run it before the checkpoint?⟩

## 6. Points for the checkpoint found while drafting

- **`blind.VALUE_EXEMPT` grows with AT_OPEN.** It is defined as `PRE_OPEN_FEATURES | AT_OPEN`, so the
  schema change adds the three new AT_OPEN columns to the value-only exemption. That follows the A4
  rationale (gap columns collide with tick-grid targets), and the row-aligned check still covers
  them. It is still a change to an exemption set, which P52 says stays unchanged ⟨approve, or pin
  VALUE_EXEMPT to the Pass 1 three⟩.
- **`targets.past_beta(hedge=…)`'s default** stays `y_topix_oc` (section 2).
- **The C7 rerun's platform** is D16 (PASS2_STATUS).
