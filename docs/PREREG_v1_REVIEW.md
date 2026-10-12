# Advisor-style review of `docs/PREREG_v1.md`

Written 2026-10-12 by the Pass 5 supervisor chat, for Isaiah as acting advisor (P5Q11). **This is not an independent review.** It was written by the session that drafted the document under review, and the pre-registration discloses that (§9.9). It sets out what a careful advisor would ask, what the document answers, and what risk remains, so that Isaiah's sign-off is an informed one.

## 1. Verdict

I recommend sign-off, with no change to any computation. The document fixes one primary test, states its reading, its claims and their exact wording before the data are seen, fixes the run and the holdout, and discloses everything seen on dev. Every computation it relies on was frozen before the dev first look, and the code that opens the panel is pinned by SHA-256. The residual risks in §4 are real but disclosed, and none can be removed before the tag without new data or an independent reader.

## 2. What was checked

- **Consistency with the governing record.** Every number and rule was checked against the frozen spec and amendments, the configuration (version 1), PLAN v2.6, the decision files P14 to P87, PASS4_STATUS's decision log and the audit's 71 rows. Every hash in Appendix A was recomputed from the H10 snapshot, which is byte-identical to REPO at `3c37f0ae` (P5-boot a.4). The P5 files were recomputed from the P5-1 kit.
- **The dev numbers.** Every number in §9.6 was recomputed from `reports/P4_runs/dev/document.json`.
- **Consistency with what the code does.** The claim rules of §4 match the configuration and the claim rows (R10, R11, R14, R21). The run of §7 matches `tools/p6_confirm_run.py`, its refusal order and its one-shot check. The contingencies match P4Q31.

## 3. Points an advisor raises, and how the document answers them

1. **Forking paths after the dev first look.**
   - Answer: §9.7's chronology. Spec, configuration, modules and dry-run criteria all predate the dev run, and nothing that computes has changed since.
   - What changed afterwards is readings only (P84, P85), derived blind before the dev run, and the loader script. The script's equivalence test shows it produces the same document as the dev run's script from the same frames.
   - Adequate.
2. **A significant result alongside equivalence.** Dev shows exactly this, and the configuration licenses both sentences independently.
   - Answer: §4.3 pre-states the joint reading, and neither claim is reported without the other.
   - Adequate. This was the most likely source of after-the-fact emphasis.
3. **The inference is effectively time-series, with three units.** DK-normal is slightly liberal at T_conf (5.82% size; size-adjusted critical value 2.0041).
   - Answer: §4.1's borderline rule, added at review. A result with 1.96 < |z| ≤ 2.0041 is still a rejection, the pre-registered decision, but is labelled as not surviving the size adjustment.
   - Adequate. Changing the decision rule itself after `spec-dev-v1` would be a deviation, and this does not.
4. **Tier (ii) is underpowered.** On dev it failed through power, not absorption (ratio 0.99, p 0.074), and the confirmation has fewer dates.
   - Answer: §4.2's failure reading, added at review: "not established", with "power, not absorption" stated when only significance fails.
   - Adequate. The criterion itself is unchanged (P4Q16).
5. **The reading of b's sign.**
   - Answer: §4.4 states the qualifier, names S1 to S3, and bars "overreaction" for b̂ < 0 and "fully priced" for a null.
   - Adequate. It follows the M2 note's Proposition 4 exactly.
6. **The power statement.**
   - Answer: §3 leads with the design's binding curve. It gives the dev-centred remark second, labelled, with the width of the dev interval, and notes the larger expected SE at T_conf.
   - Adequate.
7. **The one-shot rule in practice.**
   - Answer: §7's crash rule and the script's refusal on an existing `ACCESS_LOG` make a second opening impossible without a visible, recorded act. The external registration must exist before the sanction.
   - Adequate.
8. **The forward holdout as a second chance.**
   - Answer: §8 makes it H1-only, never pooled, licensing no claim, with its window fixed now and its low power stated.
   - Adequate.
9. **Prior exposure.**
   - Answer: §9.1 and §9.4 state the Math 86 gap work and Isaiah's 2026 cost note plainly, with their consequence (f confirmatory for 2022 only).
   - Adequate.
10. **f in 2022.**
    - Answer: §2 and §4.4 present it as an estimate with uncalibrated intervals at about 250 dates, not as a test.
    - Adequate.

## 4. Residual risks (disclosed; not removable before the tag)

1. **No independent review.** Author and reviewer coincide, and the drafting and reviewing sessions coincide. An outside reader might find a reading this review shares with the draft. The disclosure (§9.9) and the external timestamp (§10) are the mitigations.
2. **The SESOI is a cost-model quantity.** "Exploitable" means b·mean|ẽ| below the mean round trip under Isaiah's primary cost inputs. The SESOI's economics assume knowledge of e's sign; O45's strategy trades a forecast's sign, so the two economic readings are related but not identical. Both are reported, with the low and high cases.
3. **The abnormal target measures underreaction relative to the market.** If 1306 itself under- or over-reacts to FX, b_abn moves by mean(β)·b_mkt. The decomposition (O9) reports this; on dev b_mkt was −0.039.
4. **The 2024-11-05 session change** lengthened the session by 30 minutes for the last 16 months. b_post is descriptive, and the primary b pools both regimes.
5. **AI-drafted machinery.** The code and documents were drafted by AI sessions. The mitigations are the test suite (398 tests at P5-1), the simulated dry run, the equivalence test and the recorded decisions, not human line-by-line review. §9.10 discloses this.

## 5. Recommendations

- **Sign off** on the document as installed at P5-2, recording its SHA-256 in `PASS5_STATUS.md`'s Decision log.
- **Commit this review** with it (`docs/PREREG_v1_REVIEW.md`), so the acting-advisor arrangement is auditable.
- **File the OSF registration** promptly after the tag, and before the Pass 6 sanction (§7.1).
- **Optional:** if any faculty member or peer will read the document before the tag, even briefly, their comments can be added and disclosed. Without one, the arrangement above stands as decided (P5Q11).
