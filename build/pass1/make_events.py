"""Write the event calendars as tidy CSVs (source: Deep Research report, Sept 2026)."""
import pandas as pd
from events import T, OTHER, BOJ

# Standalone disclosures with economic content -> treated like earnings (D, D+1).
NEWS = {
    ("5711", "2018-03-20"): "special loss (environmental provision)",
    ("5711", "2019-04-25"): "forecast revision",
    ("5711", "2020-04-27"): "results-delay notice",
    ("5711", "2020-05-13"): "forecast revision + special loss",
    ("5711", "2020-09-29"): "forecast revision + special loss",
    ("5711", "2020-11-02"): "results-delay notice",
    ("5711", "2026-03-25"): "impairment (after sample end)",
    ("5706", "2021-03-24"): "forecast + dividend revision",
}
# Mechanical / corrections: recorded, NOT excluded.
MECH = {
    ("5713", "2017-06-27"): "dividend restatement for share consolidation",
    ("5713", "2022-02-09"): "tanshin correction",
    ("5713", "2022-06-20"): "tanshin correction",
    ("5713", "2024-07-31"): "tanshin correction",
    ("5706", "2018-08-13"): "correction of 2018-08-10 revision",
}
# Outcome-identified candidates from the price audit -- robustness only, never primary.
AUDIT = {
    "5713": "2017-01-13 2018-04-24 2025-03-14",
    "5711": "2017-07-26 2017-11-24 2025-01-22 2025-09-25",
    "5706": "2015-03-27 2015-10-29 2016-02-05 2016-10-21 2020-12-10 2023-06-14 2025-08-15 2025-08-20",
}
rows = []
for t, s in T.items():
    for d in s.split():
        rows.append(dict(ticker=t, date=d, category="TANSHIN", note=""))
for t, s in OTHER.items():
    for d in s.split():
        if (t, d) in NEWS:
            rows.append(dict(ticker=t, date=d, category="STANDALONE_NEWS", note=NEWS[(t, d)]))
        elif (t, d) in MECH:
            rows.append(dict(ticker=t, date=d, category="MECHANICAL", note=MECH[(t, d)]))
        else:
            raise SystemExit(f"unclassified OTHER event {t} {d}")
for t, s in AUDIT.items():
    for d in s.split():
        rows.append(dict(ticker=t, date=d, category="AUDIT_CANDIDATE",
                         note="large unexplained move; robustness only"))
ev = pd.DataFrame(rows).sort_values(["ticker", "date"])

# Verification status (recorded Oct 2026). "user_checked_ok" = checked by
# Isaiah against primary sources, no change required. Everything else is
# as delivered by the Deep Research report and validated statistically
# against price reactions (68% of TANSHIN rows > 2 sigma vs ~8% base rate).
CHECKED = {("5711", "2022-08-09"): "TDnet PDF checked; date confirmed"}
for t, s in AUDIT.items():
    for d in s.split():
        CHECKED[(t, d)] = "news check done; no reclassification; remains robustness-only"
ev["check_status"] = [
    "user_checked_ok" if (t, d) in CHECKED else "source_report_price_validated"
    for t, d in zip(ev.ticker, ev.date)]
ev["check_note"] = [CHECKED.get((t, d), "") for t, d in zip(ev.ticker, ev.date)]
ev.to_csv("events_firm.csv", index=False)
pd.DataFrame({"announcement_date": BOJ}).to_csv("events_boj.csv", index=False)
print(ev.category.value_counts().to_string()); print("BoJ:", len(BOJ))
