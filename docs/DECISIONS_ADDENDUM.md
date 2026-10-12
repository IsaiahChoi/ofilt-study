# DECISIONS.md addendum — panel build, October 2026

These are ready to merge into `docs/DECISIONS.md`. They are numbered P01–P13 to avoid colliding with existing D-numbers; renumber them on merge. Each entry has a status:
- **ADOPTED:** implemented in the panel.
- **PROPOSED:** not implemented; awaiting Isaiah's sign-off. (None outstanding as of 2026-09-30.)

---

**P01: Scope reduced to a Japan-only post-open drift study (ADOPTED).**
The study asks whether overnight USD/JPY is fully priced at the 09:00 TSE auction for 5713/5711/5706. It supersedes the Plan's multi-market scope; the Plan's evaluation discipline is retained.
*Reason:* feasibility and focus. The question is tradable and needs only daily equity data.

**P02: Dukascopy replaces HistData as the sole FX source (ADOPTED).**
*Reason:* Dukascopy passes the DST-gap release test, and it agrees with HistData to about 0.1 bp on ordinary nights. The disagreements are concentrated in HistData's defect windows, worst in autumn 2025 (80% of nights differ by more than 5 bp), where `histdata_tz.py` mis-corrects. Dukascopy also has no 2023 hole.
*Effect:* HistData masters, `histdata_tz.py`, `build_windows.py`, and `fx_dark_window_features.csv` are retired.

**P03: Dark-window endpoints (ADOPTED).**
The window starts at the previous TSE close (15:00 JST through 2024-11-04, 15:30 JST from 2024-11-05) and ends at 08:59:00 JST. Bars are start-labeled, so the price at instant X is the close of the last bar labeled at or before X − 1 min.
*Reason:* this gives a verified bar convention and a 60-second buffer before the auction.
*Effect:* this supersedes the earlier 08:59-bar-inclusive end, which used a price at 09:00:00.

**P04: Two specifications with separated information sets (ADOPTED).**
- **Pre-open (MOO-tradable):** only features known by 08:59.
- **Auction-conditional:** adds `ao_` columns (the day-t gap and TOPIX gap).

*Reason:* the day-t gap uses the 09:00 auction price. Using it as a feature while scoring returns from the auction price would overstate tradability.

**P05: Target (ADOPTED).**
The target is `y_oc − β·y_topix_oc`, with β estimated on past data only (or on development data for a fixed β). The FX dollar/yen split projection is estimated the same way.
*Reason:* fitting coefficients on the full sample would leak confirmation-period information.

**P06: Ex-dividend adjustment of the gap (ADOPTED).**
`ao_gap_adj = log(open_t / (close_{t−1} − D_t))`, with all cash dividend types summed by ex-date.
*Reason:* Bloomberg prices are not dividend-adjusted (verified across 48 ex-dates).
*Effect:* the mean ex-date gap moves from −1.53% to 0.00% in the development sample.

**P07: Earnings and standalone-news exclusion rule (ADOPTED).**
Exclude trading days D and D+1, where D is the first trading day on or after the release date. This applies to 決算短信 and to standalone forecast revisions, special losses, and delay notices. Mechanical items (corrections, the consolidation restatement) are flagged, not excluded.
*Reason:* release times (13:30, 14:30, 15:00, 15:30) fall in or at the end of the session, and next-session reactions are large. The rule also absorbs one-day date errors in the conservative direction.
*Robustness:* run a D+2 variant.

**P08: Outcome-identified audit dates are robustness only (ADOPTED).**
The 15 large unexplained moves were checked, with no reclassification. They are never used as primary exclusions.
*Reason:* excluding days found by searching for news behind large moves selects on the outcome and trims the target's tails.
*Consequence:* unscheduled firm news, such as 5711's move on 2017-11-24, stays in the primary sample.

**P09: BoJ announcement days are flagged; the following night is kept (ADOPTED).**
*Reason:* decisions are announced intraday and affect open→close (validated: 12% vs 6% of days above 2σ). The post-meeting overnight FX move is legitimate information for the model.

**P10: Development/confirmation split at 2022-01-01 (ADOPTED; signed off by Isaiah 2026-09-30).**
- Development: 2015-01-06 → 2021-12-30.
- Confirmation: 2022-01-04 → 2026-03-05, sealed with SHA-256 `9c18a6c106356139a375ecd7b3e6eaa085d937341c02817021003a4451c6b826`.

This is Plan §7.2 Design 1. **No lockbox is carved from the confirmation sample.**
*Reason:* the binding constraint is 1,019 confirmation trading days. Removing six months (about 120 days) would raise the minimum detectable correlation from about 0.088 to about 0.093. The lockbox alone could detect only about 0.26, roughly five times a plausible effect.
*Instead:* bugs are caught by a confirmation dry run (P13b), tinkering by the one-shot rule plus labeled deviations, and a final untouched check by the forward holdout (P13a).

**P11: US controls enter as summed open→close returns over the NY sessions inside the window (ADOPTED).**
The sessions counted are NY dates from t_prev through t−1. The control is 0 with `us_n_sessions = 0` on US holidays, and missing on the 3 stale EWJ dates.
*Reason:* every US regular session lies entirely inside the dark window.

**P12: Bad-row handling (ADOPTED).**
- The TOPIX 2020-10-01 outage row is dropped.
- The 3 stale EWJ rows are set to missing.
- The first panel day (2015-01-05) is dropped because it has no prior session in the data.
- FCX 2016-01-11 was checked and is genuine; no change.

**P13: Protecting the one-shot confirmation without spending data (ADOPTED; signed off by Isaiah 2026-09-30).**

(a) **Forward holdout.** Data after 2026-03-05 serves as the final untouched check: about 7 months as of 2026-09-30, about 12 by spring 2027. It is pulled only after the `prereg-v1` tag, with identical Bloomberg adjustment settings and the same Dukascopy pull. It requires extended event calendars (earnings from FY2025 FULL onward, plus 2026 BoJ meetings). It is evaluated once, after the confirmation run, and reported as a sanity check, not a second primary test: about 6–12 months has low power.
Note: 5706's 10:1 split (ex-date 2026-09-29) falls inside this period. Bloomberg's capital-change adjustment handles it, but verify that there is no price discontinuity on that date.

(b) **Confirmation dry run.** Before unsealing, run the exact confirmation script end to end on `panel_dev.csv` and on simulated data with a known b. Confirm that it recovers b and produces every pre-registered output.

(c) **One-shot rule.** The confirmation panel is opened once, by the pre-registered script. Any later change to code or specification is reported as a dated, labeled deviation alongside the original result.
