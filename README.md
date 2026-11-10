# Overnight FX and the Tokyo opening auction

A pre-registered test of one question: does the Tokyo Stock Exchange's 09:00 opening auction fully price the overnight USD/JPY move for three FX-exposed non-ferrous miners (5713 Sumitomo Metal Mining, 5711 Mitsubishi Materials, 5706 Mitsui Kinzoku), or do the stocks keep absorbing it during the session?

Author: Isaiah Choi (Dartmouth College).

## Design

- **Outcome.** Each stock's open-to-close return, abnormal against the 1306 ETF, using a past-only expanding hedge beta.
- **Estimand.** b, the coefficient on the overnight USD/JPY return, with EUR/USD, SPY and COPX as controls and ticker fixed effects. Pooled OLS with Driscoll-Kraay standard errors, tested two-sided at 5%.
- **Samples.** Development: 2015 to 2021. Confirmation: 2022-01-04 to 2026-03-05.
- **Sealing.** The confirmation panel was built, hashed (its SHA-256 is recorded in AM-04), and kept sealed behind a guard until the pre-registration was tagged. The analysis spec was frozen at the tag `spec-dev-v1` before the development first look.
- **Power.** From dev-calibrated simulations made before any dev result was seen: the minimum detectable effect at 80% power is 0.2471.
- **Pre-registration.** [`docs/PREREG_v1.md`](https://github.com/IsaiahChoi/ofilt-study/blob/prereg-v1/docs/PREREG_v1.md), fixed by the annotated tag `prereg-v1`, with an embargoed OSF registration (`osf.io/3mr5h`).

## Result: the null

- **Development years** (exploratory first look): b = 0.245, p = 0.0008.
- **Confirmation** (the sealed sample, opened once by the pre-registered script): H1 not rejected. b = 0.0954, standard error 0.0946, p = 0.313. Under the pre-registration, a null is read against the minimum detectable effect, never as "no effect" or as full pricing.
- **Equivalence.** The pre-registered equivalence test against trading costs licenses the claim "no drift exploitable net of costs".
- **What remained.** Most of the remaining estimate comes from the August 2024 yen carry unwind: removing 2024-08-06 and 2024-08-05 brings b from 0.095 to 0.019 (the influence-curve row O14).
- **Deviation, on record.** The first request of the confirmation panel failed before any byte was read, because the panel was not in the data folder. The second attempt is the labelled deviation D2. Both requests are reported in `PASS6_STATUS.md`.
- **Next.** The write-up, then the forward holdout (2026-03-06 to 2026-09-30), a sanity check that licenses no claim.

## Where things are

| Path | Contents |
|---|---|
| `docs/PREREG_v1.md` | The pre-registration (locked at the tag `prereg-v1`) |
| `docs/replacements/PLAN.md` | The research plan, with its change log |
| `docs/replacements/README.md` | The working README: pipeline and session rules |
| `docs/DECISIONS_*.md`, `PASS1_STATUS.md` to `PASS6_STATUS.md` | The decision log and the record of each pass |
| `spec/` | The frozen analysis spec and its amendments |
| `ofilt/drift/` | The analysis code: inference, forecasting, and the confirmation modules |
| `build/` | The panel build |
| `tools/` | Run scripts, including `tools/p6_confirm_run.py`, the confirmation run |
| `tests/` | The test suite (398 tests at the confirmation run) |
| `reports/P6_runs/confirm/` | The confirmation document |
| `reports/P4_runs/dev/` | The development first look |
| `BLIND_FIT_LOG`, `ACCESS_LOG`, `RUN_REGISTRY.jsonl` | Append-only logs of the sealed fits, the confirmation panel's openings, and the runs |

## Data

Licensed data is not included: the Bloomberg equity, index, ETF and dividend data, and the Dukascopy 1-minute FX bars. Data files are gitignored. `docs/DATA_PROVENANCE.md` documents the sources and the checks run on them, and the code verifies each input panel by its SHA-256.

## Assistance

The analysis code, the specifications, the simulations and the pre-registration were drafted by AI assistant sessions (Claude), directed and decided by Isaiah Choi. Every decision is recorded with its reason in the decision files.
