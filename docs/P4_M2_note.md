# P4 M2: the sign of the conditional EUR/USD coefficient a₂

Blind derivation for the ofilt/drift study, 2026-10-08. Referee note: it recommends; Isaiah decides after supervisor review. Everything below is symbolic. The only numbers are from synthetic draws with arbitrary parameter values (§7).

## 1. Summary

**Sign result.** In the primary design, a₂ = θ_E + π·Γ (Lemma 1). Here Γ is the gap between the yen-specific drift and the unspanned dollar-wide drift, per unit of USD/JPY. θ_E is the drift loading on the euro-specific factor, and π > 0 is a weight fixed by the regressors' second moments.

Under the cascade (the miners' metals channel underpriced at the open), the miners' own contribution to a₂ is −π·Σ c·κ_q. Its sign is opposite to κ, so it is **positive if metals fall when the dollar strengthens (κ < 0)**. It is zero if the metals channel is fully priced, and negative if overweighted.

That sign carries over to a₂ itself only under six assumptions, none of which can be checked before the data are seen:
- the sign of κ (S1) and of the miners' metals exposures (S2);
- a no-collider condition on SPY and COPX (S3);
- for the abnormal target, that 1306 fully prices its own non-dollar translation and metals channels (S4);
- that no other unpriced overnight channel is correlated with the residual FX factors (S5);
- for the XAU row, that gold- and base-metal-specific news are uncorrelated (S6).

The raw target needs S5 in a stronger form, but not S4.

Even when all six hold, a positive a₂ is not specific to metals. Any underpriced channel whose fair value falls when the dollar strengthens gives the same sign, and the same `copx_to_fcx` and `xau_control` patterns. Off-session global risk sentiment is the leading example.

**Recommendation: option (c).** Make no tier-(iii) claim, and report H3 and the metals rows without a tier-(iii) reading. The reason is that no (a)-type criterion survives without those assumptions.

The derivation also qualifies how b and P15 are read:
- the cascade leaks into b with the sign of κ (Prop 4);
- P15's "common weight" label for a₂ = 0 does not hold as stated (Prop 6).

## 2. Assumptions

Structural assumptions (used throughout):

- **A1 (linear, i.i.d.).** Window and session returns are linear in mutually independent, mean-zero, finite-variance primitive shocks, i.i.d. across days. Coefficients are population linear projections, so no Gaussianity is needed. The panel is balanced, or missingness is independent of the shocks.
- **A2 (FX factors).**
  - usdjpy_ret = u = D + Y and eurusd_ret = v = −λD + E, with λ > 0.
  - D = Dˢ + Dⁿ is the dollar-wide factor (positive = USD strengthens), split into its US-session part Dˢ and its off-US-session part Dⁿ inside the window. Y is yen-specific (positive = JPY weakens). E is euro-specific (positive = EUR strengthens).
  - Dˢ, Dⁿ, Y and E are independent, each with positive variance (V_s, V_n, V_Y, V_E).
  - Other currencies in 1306's foreign revenue: x_o = −λ_o·D + C_o, with C_o independent of everything.
- **A3 (metals).**
  - The base-metal basket that matters to the miners is m = κD + μˢ + μⁿ; gold is a = xau_ret = κ_A·D + μ_A.
  - The metal-specific shocks are independent of the FX shocks, and metals do not load on Y or E.
  - μ_A is independent of μˢ, while Cov(μ_A, μⁿ) = C_n is allowed.
- **A4 (US-session controls).**
  - Rˢ = σDˢ + G is the US-session global equity factor, with G independent.
  - spy = Rˢ + ν_S, copx = φ_C·mˢ + g_C·Rˢ + ν_C and fcx = φ_F·mˢ + g_F·Rˢ + ν_F, where mˢ = κDˢ + μˢ and the ν's are independent noises.
  - So the controls load on the FX factors only through D. They do not load on Y, E, Dⁿ, μⁿ, μ_A or C_o.
- **A5 (fair values over the window).**
  - Miner i: ΔV_i = δ_X,i·u + δ_m,i·m + δ_A,i·a + n_i·Z + n^R_i·Rˢ + (independent news).
  - 1306: ΔH = δ^X_M·u + δ^€_M·v + δ^o_M·x_o + δ^m_M·m + δ^A_M·a + n_M·Z + n^R_M·Rˢ + (independent news). The yen value of euro revenue moves with u + v and that of other revenue with u + x_o, so δ^X_M is the total foreign-revenue elasticity and δ^€_M and δ^o_M are the euro and other-currency parts.
  - Z = ζ_D·Dⁿ + ζ_Y·Y + ζ_E·E + Z⊥ is off-session non-FX news: global risk sentiment outside US hours and Japan-specific news. No sign is assumed for the ζ's.
- **A6 (pricing at the open).** This extends A′.
  - Channel k is priced at the open with share ρ_k; the share may differ by channel and by firm.
  - The open→close return carries (1 − ρ_k) × channel k, minus the reverting auction noise η, plus session news.
  - η and session news are independent of the window shocks; in particular, session FX and metals moves are martingale increments.
  - The unpriced loadings are written c_k = (1 − ρ_k)·δ_k. For the nuisance channels the unpriced loadings n are written directly.
  - Operating leverage multiplies a firm's δ's. If, as in A5, leverage scales every channel by a common factor L, then L cancels from every sign and threshold below. It matters only when leverage differs across channels, and the δ's absorb that case.
- **A7 (hedge).** β_i is known and constant; Lemma 3(iv) covers the estimated case.
- **A8 (design).** The primary design is P14's: ticker fixed effects, a common (b, a₂), and ticker-specific slopes on q = (spy_oc, copx_oc). The metals rows replace q with (spy, fcx), or add xau with ticker-specific slopes.

Sign assumptions (each stated where used; none can be checked before the data are seen):

- **S1.** κ < 0 and κ_A < 0: the metals' dollar prices fall when the dollar strengthens. The mirror case κ, κ_A > 0 flips every sign below.
- **S2.** δ_m,i > 0 and δ_A,i ≥ 0: the miners are net long metal prices. Smelting margins (TC/RC) are largely metal-price-neutral, so this is an assumption, not an identity.
- **S3 (no collider).** B := g_C·σ·V_s·V_S/S = 0, where S = σ²V_s + V_G + V_S. That is, either SPY does not co-move with the US-session dollar (σ = 0), or SPY spans the US equity factor that COPX loads on (V_S = 0), or COPX has no equity-market loading (g_C = 0). The FCX row uses the same condition with g_F.
- **S4 (hedge neutrality, abnormal target only).** c^€_M = c^o_M = c^m_M = c^A_M = 0. 1306 fully prices its non-dollar translation and metals channels. Its dollar translation c^X_M is unrestricted, because it enters b only.
- **S5 (nuisance neutrality).** For the abnormal target, n_i − β_i·n_M = 0 and n^R_i − β_i·n^R_M = 0. For the raw target, n_i = n^R_i = 0. In either case the condition also holds if the nuisance factors are orthogonal to the residual FX factors (ζ_D = ζ_Y = ζ_E = 0 and V_S = 0).
- **S6.** C_n = 0 (used only for the XAU row).

Hypotheses on the miners' metals pricing (for δ_m, δ_A > 0):
- the **cascade H_C**: ρ_m,i ≤ 1 and ρ_A,i ≤ 1 for all i, with at least one strict;
- **fully priced H_F**: all equal 1;
- **overweighted H_O**: all ≥ 1, with at least one strict.

Mixed cases leave the sign undetermined.

## 3. Model

**Targets.** Write c_X,i = (1−ρ_X,i)δ_X,i, c_m,i = (1−ρ_m,i)δ_m,i and c_A,i = (1−ρ_A,i)δ_A,i.

- Raw target: y_i = c_X,i·u + c_m,i·m + c_A,i·a + n_i·Z + n^R_i·Rˢ − η_i + (session news).
- Hedge: h = c^X_M·u + c^€_M·v + c^o_M·x_o + c^m_M·m + c^A_M·a + n_M·Z + n^R_M·Rˢ − η_M + (session news), where c^·_M = (1 − ρ^·_M)δ^·_M is 1306's own pricing at the open.
- Primary target: abn_i = y_i − β_i·h.

**Notation for the design.** For the control vector q:
- V_q := Var(D | q) is the variance of the unspanned dollar factor D_q := D − Proj(D | q), where Var(· | q) and Cov(· | q) are partial (residual) moments after linear projection on q;
- κ_q(x) := Cov(D, x | q)/V_q is the effective dollar elasticity of a variable x after the controls;
- Δ := λ²V_qV_Y + V_qV_E + V_YV_E;
- π := λV_qV_Y/Δ, which lies in (0, 1/λ);
- ω := V_Y(λ²V_q + V_E)/Δ, which lies in (0, 1), with 1 − ω = V_qV_E/Δ;
- γ_q := −λV_q/(λ²V_q + V_E) is P15's γ, conditional on the controls.

**Drift loadings.** For any drift z:
- θ_D(z) := Cov(D, z | q)/V_q;
- θ_Y(z) := Cov(Y, z)/V_Y;
- θ_E(z) := Cov(E, z)/V_E;
- Γ(z) := θ_Y − θ_D − λθ_E.

Γ is the per-unit-USD/JPY gap between the yen-specific and the unspanned dollar-wide drift, after removing the part of the dollar-wide drift that is a multiple of v.

**What SPY absorbs.** SPY absorbs the US-session global equity factor Rˢ, exactly if V_S = 0 and partly otherwise. It does not absorb:
- risk sentiment and Japan news outside US hours (Z);
- the off-session dollar move Dⁿ;
- the yen- and euro-specific moves.

If σ ≠ 0, SPY is also a noisy proxy for the US-session dollar. That shrinks V_q, but it opens the SPY–COPX collider in Lemma 2.

**What COPX and FCX absorb.** COPX (or FCX) is a noisy view of mˢ only. The off-session dollar–metals response κDⁿ is never in it.

Global risk sentiment is the dollar-wide channel I judge material besides metals. It is modelled two ways: as Z, unrestricted in its loadings on Dⁿ, Y and E, and as the US-session factor Rˢ.

## 4. Propositions and proofs

**Lemma 1 (reduction of the primary design).** Under A1, A2, A4 and A8, and per ticker:
- a₂ = θ_E + π·Γ;
- b = θ_Y − (1 − ω)·Γ;
- p$ := b + a₂/γ_q = θ_D − θ_E·V_E/(λV_q).

P15's dollar-wide coefficient is b^$ = γ_q·b + a₂ = γ_q·p$, so p$ is the dollar-wide drift per unit of USD/JPY.

*Proof.* By A2 and A4, Cov(q, u) = Cov(q, D), Cov(q, v) = −λCov(q, D) and Cov(q, Y) = Cov(q, E) = 0. So the FWL residuals on q (and the fixed effects) are ũ = D_q + Y and ṽ = −λD_q + E. Here D_q, Y and E are mutually uncorrelated, because D_q is a linear function of (D, q) and both are uncorrelated with Y and E.

The residual covariance matrix is [[V_q + V_Y, −λV_q], [−λV_q, λ²V_q + V_E]], with determinant Δ. Also Cov(ũ, z) = θ_D·V_q + θ_Y·V_Y and Cov(ṽ, z) = −λθ_D·V_q + θ_E·V_E. Inverting:
- a₂ = [λV_qV_Y(θ_Y − θ_D) + θ_E·V_E(V_q + V_Y)]/Δ. Since V_E(V_q + V_Y)/Δ = 1 − λπ, this is θ_E + πΓ.
- b = [V_qV_E·θ_D + V_Y(λ²V_q + V_E)·θ_Y + λV_qV_E·θ_E]/Δ = (1 − ω)(θ_D + λθ_E) + ωθ_Y = θ_Y − (1 − ω)Γ.
- π/γ_q = −ω, so a₂/γ_q = θ_E/γ_q − ωΓ, and p$ = θ_Y − Γ + θ_E/γ_q = θ_D + θ_E(λ + 1/γ_q) = θ_D − θ_E·V_E/(λV_q). ∎

**Lemma 2 (unspanned dollar and effective elasticities, controls q = (spy, copx)).** Let:
- S = σ²V_s + V_G + V_S;
- A = V_s(V_G + V_S)/S;
- Q_S = V_S(σ²V_s + V_G)/S;
- B = g·σ·V_s·V_S/S;
- Ω = φ²κ²A + 2φκB + φ²V_μs + V_C + g²Q_S;
- X_c = φκA + B;
- U = σV_sV_S/S.

Here (φ, g, V_C) = (φ_C, g_C, Var ν_C), and FCX's parameters replace them in the FCX row. Then:
- V_q = V_n + A − X_c²/Ω;
- Cov(D, m | q) = κK + χ, where K = V_n + [A(V_C + g²Q_S) − B²]/Ω ≥ V_n ≥ 0 and χ = −g·σ·φ·V_s·V_S·V_μs/(S·Ω);
- κ_q(a) = κ_A, κ_q(x_o) = −λ_o, θ_D(Z) = ζ_D·V_n/V_q, and κ_q(Rˢ) = [U − X_c(gQ_S + φκU)/Ω]/V_q, which is 0 if V_S = 0.

Under S3 (B = 0), χ = 0, and with ψ := φ²(κ²A + V_μs)/Ω ∈ [0, 1] and ϱ² := κ²A/(κ²A + V_μs):
- K = V_n + A(1 − ψ);
- V_q = V_n + A(1 − ψϱ²);
- κ_q(m) = κ·k, with k := K/V_q ∈ [0, 1].

So sign κ_q(m) = sign κ. With B ≠ 0, χ has sign −sign(gσφ) and can exceed |κ|K, which reverses sign κ_q(m).

*Proof.* span(spy, copx) = span(spy, c′), where c′ = copx − g·spy = φκDˢ + φμˢ + ν_C − g·ν_S. Project on spy first, then on c′ given spy. Given spy:
- Var(Dˢ) = A, Var(ν_S) = Q_S and Cov(Dˢ, ν_S) = −U;
- Ω = Var(c′ | spy) and X_c = Cov(Dˢ, c′ | spy).

Dⁿ is orthogonal to q, so V_q = V_n + A − X_c²/Ω. Also Cov(mˢ, c′ | spy) = κX_c + φV_μs, so

Cov(D, m | q) = κV_n + κA − X_c(κX_c + φV_μs)/Ω = κ[V_n + (AΩ − X_c² − φ²AV_μs)/Ω] − BφV_μs/Ω.

The bracketed numerator equals A(V_C + g²Q_S) − B², which is ≥ 0 because A·Q_S ≥ U² (Cauchy–Schwarz) and B = gU.

For B = 0, substitute Ω = φ²(κ²A + V_μs) + V_C + g²Q_S. Then k ≤ 1 because 1 − ψ ≤ 1 − ψϱ².

The remaining claims hold because μ_A, C_o, Y, E and Z⊥ are orthogonal to (D, q), and Cov(D, Dⁿ | q) = V_n. ∎

**Lemma 3 (linearity, pooling, hedge, estimated β).**
- (i) a₂ and b are linear in a drift's loadings.
- (ii) With a balanced panel, a common FX block and ticker-specific slopes on day-level controls, the pooled (b, a₂) is the equal-weighted mean of the per-ticker coefficients. The FWL residual of (u, v) on the block-diagonal controls is the same series in every block, so the pooled estimator is (N·X̃′X̃)⁻¹·Σ_i X̃′z_i. With independent missingness the weights are proportional to row counts.
- (iii) a₂^abn = a₂^raw − β̄·a₂^M and b^abn = b^raw − β̄·b^M. Here β̄ is the mean of β_i, and a₂^M and b^M are 1306's own coefficients in the same design.
- (iv) If β̂_{i,t−1} uses only days before t and the day-t shocks are independent of the past (A1), then E[x̃_t·β̂_{i,t−1}·h_t] = E[β̂_{i,t−1}]·E[x̃_t·h_t]. So (iii) holds with β_i replaced by E[β̂_i].
  - For the expanding oc-on-oc β, E[β̂_i] tends to β*_i = Cov(y_i, h)/Var(h). That ratio is chosen to neutralise no particular channel.
  - Under time-varying volatility, an extra term Cov(β̂_{t−1}, E_{t−1}[x̃_t·h_t]) appears.
  - Sampling error in β̂ adds variance, not population bias; that is M3's remit.

*Proof.* (i) and (iii) follow from linearity of projection; (ii) is FWL; (iv) follows from independence. Cell C12 checks (iv) with an estimated expanding β. ∎

**Channel table** (Lemma 1 applied to one unit of each channel):

| Channel | (θ_D, θ_Y, θ_E) | Contribution to a₂ | Contribution to b |
|---|---|---|---|
| u (translation) | (1, 1, 0) | 0 | 1 |
| v (euro cross) | (−λ, 0, 1) | 1 | 0 |
| pure-dollar x ∈ {m, a, x_o, Rˢ} | (κ_q(x), 0, 0) | −π·κ_q(x) | (1 − ω)·κ_q(x) |
| Z | (ζ_D·V_n/V_q, ζ_Y, ζ_E) | A_Z := ζ_E + π(ζ_Y − ζ_D·V_n/V_q − λζ_E) | ζ_Y − (1 − ω)(ζ_Y − ζ_D·V_n/V_q − λζ_E) |

For every pure-dollar channel, the ratio of its b part to its a₂ part is −(1 − ω)/π = −V_E/(λV_Y).

**Proposition 1 (a₂ for the abnormal target).** Write c̄ for a cross-ticker mean. In the primary design:

a₂^abn = −π[(c̄_m − β̄c^m_M)·κ_q(m) + (c̄_A − β̄c^A_M)·κ_A] − β̄·c^€_M − β̄·π·λ_o·c^o_M + (n̄ − β̄n_M)·A_Z − π(n̄^R − β̄n^R_M)·κ_q(Rˢ).

- (i) Under S1–S5, a₂^abn = −π(c̄_m·κ·k + c̄_A·κ_A). Its sign is:
  - positive under H_C (strictly if k·c̄_m > 0 or c̄_A > 0);
  - zero under H_F;
  - negative under H_O.
  
  If κ, κ_A > 0, the signs are reversed.
- (ii) The model restricts the signs of none of the following: the hedge loadings (c^€_M, c^o_M, c^m_M, c^A_M), the nuisance loadings, and B. Each enters linearly with a nonzero coefficient. So for any value of the miners' cascade term there are admissible values that give a₂^abn either sign. The sign of a₂^abn is therefore implied by the hypothesis on the miners' metals pricing **exactly when** S4 and S5 hold, or when the hedge and nuisance terms are assumed to share the cascade term's sign. The cascade term's own sign needs S1–S3.
- (iii) The natural failures of S4 go both ways:
  - If 1306 underprices its own foreign-currency translation, the hedge terms are negative and oppose the cascade. This is what A′(vi) allows with ρ^M < 1, applied with a common ρ^M across currencies so that c^€_M and c^o_M are positive. In C05, a₂^abn < 0 under the cascade.
  - If 1306 overprices it, the terms are positive and mimic the cascade. In C06, a₂^abn > 0 with no cascade.
  - If c^m_M > 0, a₂^abn measures the miners' cascade relative to β̄ times the market's.

*Proof.* Lemma 3(i, iii) and the channel table give the formula; c^€_M·v contributes exactly c^€_M to a₂^M, and x_o has κ_q(x_o) = −λ_o. For (i), substitute S4, S5 and Lemma 2 under S3; then −π·c·κ·k ≥ 0 and −π·c_A·κ_A ≥ 0 under S1, S2 and H_C. (ii) follows from linearity with nonzero coefficients. ∎

**Proposition 2 (a₂ for the raw target; the difference between the targets).**

a₂^raw = −π(c̄_m·κ_q(m) + c̄_A·κ_A) + n̄·A_Z − π·n̄^R·κ_q(Rˢ).

Under S1–S3 and S5 (raw), its sign is as in Proposition 1(i); S4 is not needed.

The two targets differ by a₂^raw − a₂^abn = β̄·a₂^M, where

a₂^M = c^€_M + π·λ_o·c^o_M − π(c^m_M·κ_q(m) + c^A_M·κ_A) + n_M·A_Z − π·n^R_M·κ_q(Rˢ)

is 1306's own a₂ in the same design. Under S4, and with the nuisance terms hedged the same way, the two targets have equal a₂ in population.

The targets trade contaminations:
- the raw target is free of 1306's channels but carries the miners' full unpriced nuisance exposure n̄;
- the abnormal target carries only n̄ − β̄n_M, but adds 1306's non-dollar channels.

*Proof.* Set β = 0 in Proposition 1, then apply Lemma 3(iii). ∎

**Corollary (the sign is not specific to metals).** A pure-dollar channel with unpriced loading c contributes −π·c·κ_q(x) to a₂. So any underpriced channel whose fair value falls when the dollar strengthens gives a₂ > 0, as the cascade does under S1.

Off-session risk sentiment is one such channel. Suppose risk-on news weakens both the dollar and the yen (ζ_D < 0, ζ_Y > 0) and ζ_E ≥ 0. Then A_Z = (1 − λπ)ζ_E + π(ζ_Y + |ζ_D|·V_n/V_q) > 0. So an unpriced positive risk exposure gives a₂ > 0 on both targets with no metals channel at all; C07 has a₂^raw > 0 and a₂^abn > 0 with metals fully priced.

The same channel also passes both metals-row checks of Proposition 5. Under those sign conditions every term of A_Z stays positive when FCX replaces COPX, so the sign is preserved. Adding XAU leaves θ_D(Z) unchanged (§6 proof), so Z's contribution becomes ζ_E + π′(ζ_Y − θ_D − λζ_E): with ζ_E = 0 it is attenuated by exactly π′/π, as a metals channel would be. C07 shows both patterns. ∎

**Proposition 4 (the effect on b).** In the primary design:

b^raw = c̄_X + (1 − ω)(c̄_m·κ_q(m) + c̄_A·κ_A) + n̄·[ζ_Y − (1 − ω)(ζ_Y − ζ_D·V_n/V_q − λζ_E)] + (1 − ω)·n̄^R·κ_q(Rˢ),

and b^abn = b^raw − β̄·b^M, where

b^M = c^X_M + (1 − ω)(−λ_o·c^o_M + c^m_M·κ_q(m) + c^A_M·κ_A) + (1306's nuisance terms).

c^€_M does not enter b.

- (i) The cascade loads on usdjpy_ret with coefficient (1 − ω)(c̄_m·κ_q(m) + c̄_A·κ_A). Under S1–S3 its sign is that of κ, so it is negative. It is zero only if there is no cascade, if κ_q(m) = κ_A = 0, or if V_E = 0 (then ω = 1 and EUR/USD is an exact dollar proxy). Its ratio to the cascade's a₂ part is −V_E/(λV_Y).
- (ii) The reason is that holding eurusd_ret fixed does not hold the dollar factor fixed. The yen residual e^¥ = u − γ_q·v = [V_E/(λ²V_q + V_E)]·D_q + Y − γ_q·E carries a share of the unspanned dollar.
- (iii) Reading b's sign.
  - A′(i), b = (1 − ρ)δ, and A′(vi) hold only when the dollar-wide channels are fully priced or V_E = 0.
  - P14's "holding the dollar-wide move fixed" holds only up to the euro-specific noise.
  - Under S1–S3 the cascade pushes b down. So b < 0 can arise with the translation channel fully priced (C11: closed-form b^raw = −0.09953 with c_X = 0) or even underpriced (C10). Hence "b < 0 means overreaction" and "b = 0 means fully priced" (PLAN §1.2) need this qualifier.
  - The cascade does not produce b > 0 under S1–S3. A positive b is therefore conservative with respect to the cascade, though not with respect to yen-correlated nuisance.
  - H1, the two-sided test of b ≠ 0, is unaffected as a test; only its reading changes.
  - f = b/δ_cc (P24) inherits the same term.

*Proof.* The channel table, Lemma 3, and the e^¥ algebra (1 + λγ_q = V_E/(λ²V_q + V_E)). ∎

**Proposition 6 (P15's two statements).**
- (i) The identity b·u + a₂·v = b·e^¥ + (bγ + a₂)·v holds for any γ. With γ = γ_q, b^$ = γ_q·p$. **Agree.**
- (ii) "a₂ = 0 is exactly the restriction that dollar-wide and yen-specific moves carry the same session drift per unit of USD/JPY." This holds exactly when θ_E = 0. Then a₂ = πΓ and p$ = θ_D, so a₂ = 0 ⇔ Γ = 0 ⇔ θ_Y = θ_D, where "dollar-wide" means the part the controls do not span; this matches P15's conditional reading. If θ_E ≠ 0, a₂ = 0 neither implies nor is implied by equal per-unit drift. That is the case for the abnormal target whenever c^€_M ≠ 0, and for any euro-correlated nuisance. **Agree with a qualifier.**
- (iii) "The 'common weight' auction." Suppose a common partial-adjustment share ρ < 1 applies to all of a miner's channels. Then a₂^raw = −π(1 − ρ)(δ̄_m·κ_q(m) + δ̄_A·κ_A) ≠ 0. The dollar-wide move carries an extra fair-value channel, so equal pricing weights do not give equal drift per unit of USD/JPY.
  - With θ_E = 0 and S5, a₂ = 0 ⇔ c̄_m·κ_q(m) + c̄_A·κ_A = 0. Under S2 and one-signed mispricing, that is ρ_m = ρ_A = 1: the unspanned metals channel is fully priced.
  - a₂ cannot compare ρ_m with ρ_X. A cascade defined as "metals priced less than translation" is not what a₂ tests.
  
  **Disagree with the label.** a₂ = 0 is "the metals channel fully priced (given θ_E = 0)", not a common-weight auction.
- (iv) "The cascade model predicts a₂ ≠ 0." This holds generically, but only if κ_q(m) ≠ 0 or κ_A ≠ 0, that is, if some of the dollar–metals response is not spanned by COPX (V_n > 0, or COPX is noisy). If COPX spanned it (V_n = 0, ψ = 1, B = 0), the cascade would load on COPX's slope and predict a₂ = 0. The predicted direction, a₂ > 0, needs S1–S5. **Agree with a qualifier.**

*Proof.* Lemma 1 and the channel table; for (iii), set c_k = (1 − ρ)δ_k for every channel. ∎

## 5. The κ condition

**Proposition 3 (opposite signs of dollar-wide and yen-specific pass-through).** The condition can be read at three levels.

**(a) Fair value, raw target.** The dollar-wide fair-value change per unit of USD/JPY is δ_X + δ_m·κ + δ_A·κ_A; the yen-specific change is δ_X. With δ_X > 0, the two have opposite signs iff δ_m·κ + δ_A·κ_A < −δ_X. With one metal, that is κ < −δ_X/δ_m.
- A common operating-leverage factor cancels from this threshold.
- If every dollar flow is metal-linked and costs are in yen, then δ_X = δ_m and the threshold is κ < −1.
- κ = −1 is the boundary case in which the yen price of the metal does not move with a dollar-wide move. This is a reference point of the model, not a calibration.
- For the abnormal target, replace each δ with its relative counterpart δ − β·δ_M (yen-specific loading δ_X − βδ^X_M). The D-loading also gains β(λδ^€_M + λ_o·δ^o_M).

**(b) Unpriced structural drift.** The yen-specific drift is θ_Y = c_X and the dollar-wide drift is θ_D = c_X + c_m·κ_q(m) + c_A·κ_A. They have opposite signs iff c_X·(c_X + c_m·κ_q(m) + c_A·κ_A) < 0.

**(c) What the study estimates: b and p$ = b^$/γ_q.** Both are affine in Γ (Lemma 1), with slopes −(1 − ω) and −1, which have the same sign. So b·p$ < 0 iff Γ lies strictly between the roots
- Γ_b = θ_Y/(1 − ω) and
- Γ_p = θ_Y + θ_E/γ_q.

*Raw target, under S3 and S5.* Here θ_E = 0, θ_Y = c̄_X and Γ = −(c̄_m·κ·k + c̄_A·κ_A). With c̄_X > 0 and the cascade, the signs are opposite iff

  −c̄_X/(1 − ω) < c̄_m·κ·k + c̄_A·κ_A < −c̄_X.

With one metal this is κ ∈ (−c̄_X/((1 − ω)c̄_m·k), −c̄_X/(c̄_m·k)). That interval holds k and ω fixed; κ also moves k and V_q through COPX's view, so the exact statement is in the effective elasticity κ·k.
- Below the interval, b and p$ are both negative: b < 0 although the translation channel is underpriced (C10).
- Above it, both are positive.
- If c̄_X = 0, the signs are never opposite; both take the sign of the cascade term (C11).

So opposite signs need the translation channel to be mispriced, and κ negative enough to reverse the dollar-wide drift but not so negative that it also reverses b.

*Abnormal target.*
- θ_Y = c̄_X − β̄c^X_M;
- θ_E = −β̄c^€_M;
- Γ = −[(c̄_m − β̄c^m_M)·κ_q(m) + (c̄_A − β̄c^A_M)·κ_A + β̄·λ_o·c^o_M];
- each plus the nuisance terms.

The same rule applies. Under S4 and S5 it is the raw rule with c̄_X replaced by c̄_X − β̄c^X_M. When c^€_M ≠ 0, the root Γ_p shifts by −β̄c^€_M/γ_q, so the euro channel moves the interval even though it never enters b.

*Proof.* Two affine functions with slopes of the same sign have opposite signs exactly between their roots. The roots follow from Lemma 1. ∎

The check script tests the interval rule against the closed-form and simulated sign patterns of (b, p$) for both targets in every cell (28 checks).

## 6. The metals rows

**Proposition 5.**

**(i) `copx_to_fcx`.** The swap changes only V_q and κ_q(m) (and κ_q(Rˢ) if V_S > 0). It leaves θ_E, κ_A and κ_q(x_o) = −λ_o unchanged.

Under B = 0 for both COPX and FCX, the metals control affects V_q and K only through ψ, its metals share. Both π and π·k are nonincreasing in ψ. So under S1–S5:
- sign(a₂^fcx) = sign(a₂^prim);
- |a₂^fcx| ≥ |a₂^prim| iff ψ_F ≤ ψ_C, that is, iff FCX is the noisier view of the US-session metals response, given SPY;
- under H_F with no other channel, both are zero.

Without S4 or S5, θ_E ≠ 0 or mixed-sign terms can make the swap change the sign. The ordering of ψ is not observable even after the data are seen, because it requires the unobserved mˢ. So the model predicts only sign preservation, not the direction of the change.

*Proof.* From Lemma 2, dK/dψ = −A and dV_q/dψ = −Aϱ². Hence dπ/dψ = λV_Y·(V_YV_E/Δ²)·dV_q/dψ ≤ 0. Writing Δ = αV_q + V_YV_E with α = λ²V_Y + V_E:

  d(K/Δ)/dψ = −A(Δ − α·K·ϱ²)/Δ² ≤ −A·V_YV_E/Δ² < 0,

because K·ϱ² ≤ V_q. Since π·k = λV_Y·K/Δ, the claim follows. Every term is pure-dollar with one sign, and θ_E = 0. ∎

In every cell where the swap check applies, |a₂| moves as ψ predicts: it rises where ψ_F < ψ_C and falls in C14, the one cell with ψ_F > ψ_C.

**(ii) `xau_control`.** Add a to q, assuming μ_A ⟂ q. Then:
- V_q′ = s_A·V_q, where s_A = V_μA/(κ_A²V_q + V_μA) ∈ (0, 1];
- κ_q′(x) = κ_q(x) for every pure-dollar x whose non-dollar part is orthogonal to μ_A (x_o, Rˢ, and the dollar part of Z);
- κ_q′(m) = κ_q(m) − κ_A·C_n/V_μA;
- the gold channel is absorbed by its own slopes.

So π′ < π whenever κ_A ≠ 0. Under S1–S6, for both targets,

  a₂^xau/a₂^prim = (π′/π)·c̄_m·κ_q(m)/(c̄_m·κ_q(m) + c̄_A·κ_A) ∈ [0, π′/π] ⊂ [0, 1), with the upper end reached iff c̄_A·κ_A = 0.

The row is attenuated toward zero, with its sign weakly preserved. It is zero if the cascade runs through gold only. Under H_F both are zero; under H_O the same pattern holds below zero.

*Proof.* Use Cov(D, x | q, a) = Cov(D, x | q) − Cov(D, a | q)·Cov(a, x | q)/Var(a | q), with
- Cov(D, a | q) = κ_A·V_q;
- Var(a | q) = κ_A²·V_q + V_μA;
- Cov(a, x | q) = κ_A·Cov(D, x | q) + Cov(μ_A, x).

For x = m, the last term is C_n. ∎

**Attenuation is not specific to metals.** The factor π′/π attenuates every pure-dollar channel, including off-session risk and 1306's other-currency term, and it leaves θ_E unchanged. Only the extra loss of the gold term is metals-specific, and its size depends on c̄_A, which is unknown.

With C_n > 0 and κ_A < 0, κ_q′(m) rises by |κ_A|·C_n/V_μA, and the XAU row can reverse sign under the cascade. In C09 the closed forms give +0.09161 in the primary design and −0.02502 with XAU.

**(iii) What the rows can falsify.** Within the model, only two row patterns are inconsistent with the clean cascade (S1–S6):
- a sign change in either row;
- |a₂^xau| > |a₂^prim|.

Both can also come from a failure of S4, S5 or S6. A failing row therefore does not identify which assumption failed, and a passing row does not distinguish the cascade from any other dollar-wide channel.

## 7. Numerical check

**Script.** P4_M2_check.py (numpy only, synthetic data, seed 20261008), SHA-256 faa4f6c15699658b191618598b9ce2bd18eaa4d6cd6304ba5b1a920bf7dd27a4. Run it as

    python3 P4_M2_check.py

**What each cell does.** Each of the 14 cells is a parameter vector, all values arbitrary. For each cell the script computes three things:
- **closed:** the closed forms of Lemmas 1–3 and Propositions 1, 2 and 5;
- **exact:** the exact population projection, computed from the model's covariance matrix with no closed form used;
- **sim:** the pooled OLS fit of the primary design and of the two metals rows. The fit uses ticker fixed effects and ticker-specific control slopes on 400,000 synthetic days × 3 tickers. Some shocks are Student-t(6), because A1 assumes no Gaussianity.

SE is a cluster-by-day sandwich standard error, shown only to scale the Monte Carlo error.

Rows are labelled quantity_target_row:
- quantity: a2, b, or p$ = b + a₂/γ_q;
- target: abn (primary), raw (raw_target), or M (1306's own coefficients);
- row: prim (primary design), fcx (copx_to_fcx), or xau (xau_control).

The pred column is the sign the propositions imply, or ? where an assumption fails. Cell C12 uses a past-only expanding β estimated inside the simulation (Lemma 3(iv)). It compares with the closed form at β* (the plim of the expanding β, Cov(y_i, h)/Var(h)), and its header line prints mean β* and mean β̂.

**Tolerances (fixed in the script's docstring before its first run, and not changed since):**
- TOL_ALG = 1e-9 for closed vs exact;
- TOL_MC = 0.025 for closed vs sim, for a₂ and b;
- TOL_P = 0.05 for the ratio p$.

**Verdict rule.** The verdict is True only if all of the following hold:
- every tolerance holds;
- every determined sign agrees in both closed and sim (a predicted 0 must be within TOL_MC);
- every Proposition 5 ordering and attenuation prediction holds in both closed and sim;
- Proposition 3's interval rule agrees with the closed-form sign pattern of (b, p$) in all 28 target-cell pairs, and with the simulated pattern wherever both |b| and |p$| exceed 3·TOL_P.

**Disclosure.** The first runs failed because of three coding errors in the check, none in the derivation:
- the exact coefficients were unpacked in the wrong order;
- the XAU row's off-session risk term used the post-XAU unspanned variance, where the derivation (§6 proof) keeps θ_D(Z) unchanged;
- the shock draws iterated over a Python set, so the output depended on the hash seed.

All three were fixed, with no tolerance changed. Cell C07 also gained a US-session risk loading, so that the κ_q(Rˢ) term is exercised. The output below is byte-identical across two runs with different hash seeds.

**Reading the result.**
- The largest closed-vs-exact gap, 2.2e-16, confirms the closed forms are exact.
- The largest closed-vs-sim gap is 0.0037, or 3.05 SE. That is the maximum over about 140 correlated comparisons, which is consistent with Monte Carlo error.

**Script output** (verbatim; synthetic values only):

    M2 numerical check  seed=20261008  T=400000  N=3  TOL_ALG=1e-09  TOL_MC=0.025  TOL_P=0.05
    Rows: q_target_row. targets abn (primary target), raw (raw_target), M (1306 own);
    rows prim (primary design), fcx (copx_to_fcx), xau (xau_control).
    pred: sign implied by Props 1, 2 and 5 ('?' = not determined: an assumption fails).

    C01 cascade, all sign assumptions hold
    cell quantity       closed      exact        sim    |c-s|      SE  pred  ok
    C01  a2_abn_prim    0.15925    0.15925    0.15810  0.00116  0.0011     +   Y
    C01  b_abn_prim    0.07547    0.07547    0.07653  0.00106  0.0010         Y
    C01  p$_abn_prim   -0.17341   -0.17341   -0.16963  0.00377       -         Y
    C01  a2_raw_prim    0.15925    0.15925    0.15890  0.00035  0.0013     +   Y
    C01  b_raw_prim    0.17547    0.17547    0.17596  0.00049  0.0012         Y
    C01  p$_raw_prim   -0.07341   -0.07341   -0.07145  0.00196       -         Y
    C01  a2_M_prim     0.00000   -0.00000    0.00080  0.00080  0.0010         Y
    C01  b_M_prim      0.10000    0.10000    0.09943  0.00057  0.0009         Y
    C01  a2_abn_fcx    0.17148    0.17148    0.17087  0.00061  0.0011     +   Y
    C01  a2_raw_fcx    0.17148    0.17148    0.17173  0.00025  0.0013     +   Y
    C01  a2_abn_xau    0.10844    0.10844    0.10698  0.00146  0.0011     +   Y
    C01  a2_raw_xau    0.10844    0.10844    0.10813  0.00031  0.0014     +   Y

    C02 metals fully priced
    cell quantity       closed      exact        sim    |c-s|      SE  pred  ok
    C02  a2_abn_prim    0.00000    0.00000    0.00080  0.00080  0.0008     0   Y
    C02  b_abn_prim    0.17500    0.17500    0.17428  0.00072  0.0008         Y
    C02  p$_abn_prim    0.17500    0.17500    0.17303  0.00197       -         Y
    C02  a2_raw_prim    0.00000    0.00000    0.00032  0.00032  0.0011     0   Y
    C02  b_raw_prim    0.27500    0.27500    0.27565  0.00065  0.0010         Y
    C02  p$_raw_prim    0.27500    0.27500    0.27514  0.00014       -         Y
    C02  a2_M_prim     0.00000   -0.00000   -0.00048  0.00048  0.0010         Y
    C02  b_M_prim      0.10000    0.10000    0.10136  0.00136  0.0009         Y
    C02  a2_abn_fcx    0.00000    0.00000    0.00092  0.00092  0.0008     0   Y
    C02  a2_raw_fcx    0.00000    0.00000    0.00010  0.00010  0.0011     0   Y
    C02  a2_abn_xau    0.00000    0.00000    0.00087  0.00087  0.0009     0   Y
    C02  a2_raw_xau    0.00000    0.00000   -0.00012  0.00012  0.0012     0   Y

    C03 metals overweighted
    cell quantity       closed      exact        sim    |c-s|      SE  pred  ok
    C03  a2_abn_prim   -0.15438   -0.15438   -0.15391  0.00046  0.0011     -   Y
    C03  b_abn_prim    0.27148    0.27148    0.27206  0.00058  0.0010         Y
    C03  p$_abn_prim    0.51274    0.51274    0.51350  0.00076       -         Y
    C03  a2_raw_prim   -0.15438   -0.15438   -0.15334  0.00103  0.0013     -   Y
    C03  b_raw_prim    0.37148    0.37148    0.37180  0.00032  0.0012         Y
    C03  p$_raw_prim    0.61274    0.61274    0.61234  0.00040       -         Y
    C03  a2_M_prim     0.00000   -0.00000    0.00057  0.00057  0.0010         Y
    C03  b_M_prim      0.10000    0.10000    0.09974  0.00026  0.0009         Y
    C03  a2_abn_fcx   -0.16655   -0.16655   -0.16608  0.00047  0.0011     -   Y
    C03  a2_raw_fcx   -0.16655   -0.16655   -0.16539  0.00116  0.0013     -   Y
    C03  a2_abn_xau   -0.10844   -0.10844   -0.10808  0.00036  0.0011     -   Y
    C03  a2_raw_xau   -0.10844   -0.10844   -0.10778  0.00066  0.0014     -   Y

    C04 cascade, kappa > 0
    cell quantity       closed      exact        sim    |c-s|      SE  pred  ok
    C04  a2_abn_prim   -0.12585   -0.12585   -0.12692  0.00106  0.0010     -   Y
    C04  b_abn_prim    0.25366    0.25366    0.25364  0.00002  0.0009         Y
    C04  p$_abn_prim    0.44786    0.44786    0.45001  0.00215       -         Y
    C04  a2_raw_prim   -0.12585   -0.12585   -0.12738  0.00152  0.0013     -   Y
    C04  b_raw_prim    0.35366    0.35366    0.35234  0.00132  0.0012         Y
    C04  p$_raw_prim    0.54786    0.54786    0.54942  0.00156       -         Y
    C04  a2_M_prim     0.00000   -0.00000   -0.00046  0.00046  0.0010         Y
    C04  b_M_prim      0.10000    0.10000    0.09870  0.00130  0.0009         Y
    C04  a2_abn_fcx   -0.13623   -0.13623   -0.13740  0.00118  0.0011     -   Y
    C04  a2_raw_fcx   -0.13623   -0.13623   -0.13787  0.00164  0.0013     -   Y
    C04  a2_abn_xau   -0.09435   -0.09435   -0.09552  0.00117  0.0011     -   Y
    C04  a2_raw_xau   -0.09435   -0.09435   -0.09531  0.00096  0.0013     -   Y

    C05 cascade, 1306 EUR/other-ccy underpriced (S4 fails)
    cell quantity       closed      exact        sim    |c-s|      SE  pred  ok
    C05  a2_abn_prim   -0.53674   -0.53674   -0.53730  0.00057  0.0010     ?   Y
    C05  b_abn_prim    0.13546    0.13546    0.13565  0.00019  0.0010         Y
    C05  p$_abn_prim    0.97426    0.97426    0.97903  0.00477       -         Y
    C05  a2_raw_prim    0.15925    0.15925    0.15632  0.00293  0.0013     +   Y
    C05  b_raw_prim    0.17547    0.17547    0.17418  0.00129  0.0012         Y
    C05  p$_raw_prim   -0.07341   -0.07341   -0.07119  0.00222       -         Y
    C05  a2_M_prim     0.69599    0.69599    0.69362  0.00236  0.0011         Y
    C05  b_M_prim      0.04001    0.04001    0.03853  0.00148  0.0010         Y
    C05  a2_abn_fcx   -0.52564   -0.52564   -0.52648  0.00083  0.0011     ?   Y
    C05  a2_raw_fcx    0.17148    0.17148    0.16829  0.00319  0.0013     +   Y
    C05  a2_abn_xau   -0.56874   -0.56874   -0.56903  0.00029  0.0011     ?   Y
    C05  a2_raw_xau    0.10844    0.10844    0.10555  0.00289  0.0014     +   Y

    C06 no cascade, 1306 EUR overreacts (S4 fails)
    cell quantity       closed      exact        sim    |c-s|      SE  pred  ok
    C06  a2_abn_prim    0.40000    0.40000    0.39796  0.00204  0.0009     ?   Y
    C06  b_abn_prim    0.17500    0.17500    0.17388  0.00112  0.0008         Y
    C06  p$_abn_prim   -0.45011   -0.45011   -0.44871  0.00140       -         Y
    C06  a2_raw_prim    0.00000    0.00000   -0.00342  0.00342  0.0011     0   Y
    C06  b_raw_prim    0.27500    0.27500    0.27412  0.00088  0.0010         Y
    C06  p$_raw_prim    0.27500    0.27500    0.27947  0.00447       -         Y
    C06  a2_M_prim    -0.40000   -0.40000   -0.40138  0.00138  0.0010         Y
    C06  b_M_prim      0.10000    0.10000    0.10024  0.00024  0.0009         Y
    C06  a2_abn_fcx    0.40000    0.40000    0.39783  0.00217  0.0008     ?   Y
    C06  a2_raw_fcx    0.00000    0.00000   -0.00332  0.00332  0.0011     0   Y
    C06  a2_abn_xau    0.40000    0.40000    0.39771  0.00229  0.0009     ?   Y
    C06  a2_raw_xau    0.00000    0.00000   -0.00370  0.00370  0.0012     0   Y

    C07 no cascade, off-session risk (S5 fails)
    cell quantity       closed      exact        sim    |c-s|      SE  pred  ok
    C07  a2_abn_prim    0.11707    0.11707    0.11758  0.00050  0.0010     ?   Y
    C07  b_abn_prim    0.27058    0.27058    0.27078  0.00020  0.0009         Y
    C07  p$_abn_prim    0.08762    0.08762    0.08752  0.00010       -         Y
    C07  a2_raw_prim    0.19592    0.19592    0.19847  0.00254  0.0013     ?   Y
    C07  b_raw_prim    0.43380    0.43380    0.43423  0.00043  0.0012         Y
    C07  p$_raw_prim    0.12761    0.12761    0.12490  0.00272       -         Y
    C07  a2_M_prim     0.07885    0.07885    0.08089  0.00204  0.0011         Y
    C07  b_M_prim      0.16322    0.16322    0.16345  0.00024  0.0010         Y
    C07  a2_abn_fcx    0.11766    0.11766    0.11805  0.00039  0.0010     ?   Y
    C07  a2_raw_fcx    0.19671    0.19671    0.19900  0.00229  0.0013     ?   Y
    C07  a2_abn_xau    0.10001    0.10001    0.10100  0.00099  0.0010     ?   Y
    C07  a2_raw_xau    0.16732    0.16732    0.16985  0.00253  0.0014     ?   Y

    C08 cascade, SPY/COPX collider (S3 fails)
    cell quantity       closed      exact        sim    |c-s|      SE  pred  ok
    C08  a2_abn_prim   -0.01499   -0.01499   -0.01401  0.00097  0.0011     ?   Y
    C08  b_abn_prim    0.18437    0.18437    0.18425  0.00012  0.0010         Y
    C08  p$_abn_prim    0.21996    0.21996    0.21739  0.00258       -         Y
    C08  a2_raw_prim   -0.01499   -0.01499   -0.01615  0.00116  0.0014     ?   Y
    C08  b_raw_prim    0.28437    0.28437    0.28395  0.00042  0.0012         Y
    C08  p$_raw_prim    0.31996    0.31996    0.32214  0.00218       -         Y
    C08  a2_M_prim     0.00000    0.00000   -0.00214  0.00214  0.0012         Y
    C08  b_M_prim      0.10000    0.10000    0.09970  0.00030  0.0010         Y
    C08  a2_abn_fcx   -0.00683   -0.00683   -0.00605  0.00078  0.0011     ?   Y
    C08  a2_raw_fcx   -0.00683   -0.00683   -0.00821  0.00139  0.0014     ?   Y
    C08  a2_abn_xau   -0.01272   -0.01272   -0.01175  0.00097  0.0012     ?   Y
    C08  a2_raw_xau   -0.01272   -0.01272   -0.01397  0.00125  0.0014     ?   Y

    C09 cascade, gold/base co-movement (S6 fails)
    cell quantity       closed      exact        sim    |c-s|      SE  pred  ok
    C09  a2_abn_prim    0.09161    0.09161    0.09076  0.00085  0.0010     +   Y
    C09  b_abn_prim    0.11774    0.11774    0.11725  0.00049  0.0009         Y
    C09  p$_abn_prim   -0.02135   -0.02135   -0.02069  0.00066       -         Y
    C09  a2_raw_prim    0.09161    0.09161    0.09146  0.00015  0.0013     +   Y
    C09  b_raw_prim    0.21774    0.21774    0.21798  0.00023  0.0011         Y
    C09  p$_raw_prim    0.07865    0.07865    0.07897  0.00032       -         Y
    C09  a2_M_prim     0.00000   -0.00000    0.00070  0.00070  0.0010         Y
    C09  b_M_prim      0.10000    0.10000    0.10073  0.00073  0.0009         Y
    C09  a2_abn_fcx    0.09862    0.09862    0.09751  0.00111  0.0011     +   Y
    C09  a2_raw_fcx    0.09862    0.09862    0.09820  0.00042  0.0013     +   Y
    C09  a2_abn_xau   -0.02502   -0.02502   -0.02514  0.00011  0.0010     ?   Y
    C09  a2_raw_xau   -0.02502   -0.02502   -0.02463  0.00039  0.0013     ?   Y

    C10 strong cascade: b < 0 with cX > 0
    cell quantity       closed      exact        sim    |c-s|      SE  pred  ok
    C10  a2_abn_prim    0.44145    0.44145    0.44053  0.00092  0.0016     +   Y
    C10  b_abn_prim   -0.10091   -0.10091   -0.10122  0.00031  0.0014         Y
    C10  p$_abn_prim   -0.86259   -0.86259   -0.86335  0.00076       -         Y
    C10  a2_raw_prim    0.44145    0.44145    0.44094  0.00052  0.0018     +   Y
    C10  b_raw_prim   -0.00091   -0.00091    0.00063  0.00154  0.0015         Y
    C10  p$_raw_prim   -0.76259   -0.76259   -0.76221  0.00039       -         Y
    C10  a2_M_prim     0.00000   -0.00000    0.00041  0.00041  0.0011         Y
    C10  b_M_prim      0.10000    0.10000    0.10185  0.00185  0.0010         Y
    C10  a2_abn_fcx    0.45690    0.45690    0.45591  0.00099  0.0016     +   Y
    C10  a2_raw_fcx    0.45690    0.45690    0.45609  0.00081  0.0018     +   Y
    C10  a2_abn_xau    0.34132    0.34132    0.34091  0.00041  0.0015     +   Y
    C10  a2_raw_xau    0.34132    0.34132    0.34166  0.00035  0.0017     +   Y

    C11 translation fully priced, cascade
    cell quantity       closed      exact        sim    |c-s|      SE  pred  ok
    C11  a2_abn_prim    0.15925    0.15925    0.15942  0.00017  0.0011     +   Y
    C11  b_abn_prim   -0.09953   -0.09953   -0.10077  0.00124  0.0010         Y
    C11  p$_abn_prim   -0.34841   -0.34841   -0.34986  0.00145       -         Y
    C11  a2_raw_prim    0.15925    0.15925    0.16016  0.00091  0.0013     +   Y
    C11  b_raw_prim   -0.09953   -0.09953   -0.10001  0.00047  0.0012         Y
    C11  p$_raw_prim   -0.34841   -0.34841   -0.35025  0.00185       -         Y
    C11  a2_M_prim     0.00000    0.00000    0.00074  0.00074  0.0010         Y
    C11  b_M_prim      0.00000    0.00000    0.00076  0.00076  0.0009         Y
    C11  a2_abn_fcx    0.17148    0.17148    0.17157  0.00009  0.0011     +   Y
    C11  a2_raw_fcx    0.17148    0.17148    0.17222  0.00074  0.0013     +   Y
    C11  a2_abn_xau    0.10844    0.10844    0.10999  0.00155  0.0011     +   Y
    C11  a2_raw_xau    0.10844    0.10844    0.11053  0.00209  0.0014     +   Y

    C12 estimated expanding beta, S4 fails   [beta* mean 0.7052, mean beta_hat 0.7008]
    cell quantity       closed      exact        sim    |c-s|      SE  pred  ok
    C12  a2_abn_prim   -0.05231   -0.05231   -0.05233  0.00002  0.0010     ?   Y
    C12  b_abn_prim    0.10495    0.10495    0.10473  0.00022  0.0009         Y
    C12  p$_abn_prim    0.18670    0.18670    0.18669  0.00001       -         Y
    C12  a2_raw_prim    0.15925    0.15925    0.15853  0.00072  0.0013     +   Y
    C12  b_raw_prim    0.17547    0.17547    0.17540  0.00007  0.0012         Y
    C12  p$_raw_prim   -0.07341   -0.07341   -0.07287  0.00053       -         Y
    C12  a2_M_prim     0.30000    0.30000    0.30089  0.00089  0.0010         Y
    C12  b_M_prim      0.10000    0.10000    0.10083  0.00083  0.0009         Y
    C12  a2_abn_fcx   -0.04008   -0.04008   -0.03997  0.00011  0.0011     ?   Y
    C12  a2_raw_fcx    0.17148    0.17148    0.17101  0.00047  0.0013     +   Y
    C12  a2_abn_xau   -0.10312   -0.10312   -0.10265  0.00048  0.0011     ?   Y
    C12  a2_raw_xau    0.10844    0.10844    0.10827  0.00017  0.0014     +   Y

    C13 near-perfect dollar proxy (V_E small)
    cell quantity       closed      exact        sim    |c-s|      SE  pred  ok
    C13  a2_abn_prim    0.34032    0.34032    0.33981  0.00052  0.0015     +   Y
    C13  b_abn_prim    0.17075    0.17075    0.17184  0.00109  0.0011         Y
    C13  p$_abn_prim   -0.17341   -0.17341   -0.17166  0.00175       -         Y
    C13  a2_raw_prim    0.34032    0.34032    0.34095  0.00063  0.0018     +   Y
    C13  b_raw_prim    0.27075    0.27075    0.27257  0.00183  0.0013         Y
    C13  p$_raw_prim   -0.07341   -0.07341   -0.07208  0.00132       -         Y
    C13  a2_M_prim     0.00000   -0.00000    0.00115  0.00115  0.0015         Y
    C13  b_M_prim      0.10000    0.10000    0.10073  0.00073  0.0011         Y
    C13  a2_abn_fcx    0.36235    0.36235    0.36221  0.00014  0.0015     +   Y
    C13  a2_raw_fcx    0.36235    0.36235    0.36332  0.00096  0.0018     +   Y
    C13  a2_abn_xau    0.28525    0.28525    0.28498  0.00028  0.0017     +   Y
    C13  a2_raw_xau    0.28525    0.28525    0.28694  0.00169  0.0022     +   Y

    C14 FCX a cleaner metals view than COPX
    cell quantity       closed      exact        sim    |c-s|      SE  pred  ok
    C14  a2_abn_prim    0.15925    0.15925    0.15963  0.00038  0.0011     +   Y
    C14  b_abn_prim    0.07547    0.07547    0.07581  0.00034  0.0010         Y
    C14  p$_abn_prim   -0.17341   -0.17341   -0.17393  0.00052       -         Y
    C14  a2_raw_prim    0.15925    0.15925    0.15886  0.00039  0.0013     +   Y
    C14  b_raw_prim    0.17547    0.17547    0.17548  0.00001  0.0012         Y
    C14  p$_raw_prim   -0.07341   -0.07341   -0.07305  0.00035       -         Y
    C14  a2_M_prim     0.00000   -0.00000   -0.00077  0.00077  0.0010         Y
    C14  b_M_prim      0.10000    0.10000    0.09967  0.00033  0.0009         Y
    C14  a2_abn_fcx    0.14245    0.14245    0.14266  0.00021  0.0011     +   Y
    C14  a2_raw_fcx    0.14245    0.14245    0.14175  0.00070  0.0013     +   Y
    C14  a2_abn_xau    0.10844    0.10844    0.10849  0.00005  0.0011     +   Y
    C14  a2_raw_xau    0.10844    0.10844    0.10732  0.00112  0.0014     +   Y

    Proposition checks
    C01  Prop5 fcx abn: |a2_fcx| > |a2_prim| (psi_F 0.390, psi_C 0.627)                 Y
    C01  Prop5 xau abn: 0 <= a2_xau/a2_prim < 1 (closed 0.681, sim 0.677)               Y
    C01  Prop3 abn: opposite signs of b and p$ predicted True                           Y
    C01  Prop5 fcx raw: |a2_fcx| > |a2_prim| (psi_F 0.390, psi_C 0.627)                 Y
    C01  Prop5 xau raw: 0 <= a2_xau/a2_prim < 1 (closed 0.681, sim 0.681)               Y
    C01  Prop3 raw: opposite signs of b and p$ predicted True                           Y
    C02  Prop3 abn: opposite signs of b and p$ predicted False                          Y
    C02  Prop3 raw: opposite signs of b and p$ predicted False                          Y
    C03  Prop5 fcx abn: |a2_fcx| > |a2_prim| (psi_F 0.390, psi_C 0.627)                 Y
    C03  Prop5 xau abn: 0 <= a2_xau/a2_prim < 1 (closed 0.702, sim 0.702)               Y
    C03  Prop3 abn: opposite signs of b and p$ predicted False                          Y
    C03  Prop5 fcx raw: |a2_fcx| > |a2_prim| (psi_F 0.390, psi_C 0.627)                 Y
    C03  Prop5 xau raw: 0 <= a2_xau/a2_prim < 1 (closed 0.702, sim 0.703)               Y
    C03  Prop3 raw: opposite signs of b and p$ predicted False                          Y
    C04  Prop5 fcx abn: |a2_fcx| > |a2_prim| (psi_F 0.349, psi_C 0.586)                 Y
    C04  Prop5 xau abn: 0 <= a2_xau/a2_prim < 1 (closed 0.750, sim 0.753)               Y
    C04  Prop3 abn: opposite signs of b and p$ predicted False                          Y
    C04  Prop5 fcx raw: |a2_fcx| > |a2_prim| (psi_F 0.349, psi_C 0.586)                 Y
    C04  Prop5 xau raw: 0 <= a2_xau/a2_prim < 1 (closed 0.750, sim 0.748)               Y
    C04  Prop3 raw: opposite signs of b and p$ predicted False                          Y
    C05  Prop3 abn: opposite signs of b and p$ predicted False                          Y
    C05  Prop5 fcx raw: |a2_fcx| > |a2_prim| (psi_F 0.390, psi_C 0.627)                 Y
    C05  Prop5 xau raw: 0 <= a2_xau/a2_prim < 1 (closed 0.681, sim 0.675)               Y
    C05  Prop3 raw: opposite signs of b and p$ predicted True                           Y
    C06  Prop3 abn: opposite signs of b and p$ predicted True                           Y
    C06  Prop3 raw: opposite signs of b and p$ predicted False                          Y
    C07  Prop3 abn: opposite signs of b and p$ predicted False                          Y
    C07  Prop3 raw: opposite signs of b and p$ predicted False                          Y
    C08  Prop3 abn: opposite signs of b and p$ predicted False                          Y
    C08  Prop3 raw: opposite signs of b and p$ predicted False                          Y
    C09  Prop5 fcx abn: |a2_fcx| > |a2_prim| (psi_F 0.299, psi_C 0.529)                 Y
    C09  Prop3 abn: opposite signs of b and p$ predicted True                           Y
    C09  Prop5 fcx raw: |a2_fcx| > |a2_prim| (psi_F 0.299, psi_C 0.529)                 Y
    C09  Prop3 raw: opposite signs of b and p$ predicted False                          Y
    C10  Prop5 fcx abn: |a2_fcx| > |a2_prim| (psi_F 0.744, psi_C 0.885)                 Y
    C10  Prop5 xau abn: 0 <= a2_xau/a2_prim < 1 (closed 0.773, sim 0.774)               Y
    C10  Prop3 abn: opposite signs of b and p$ predicted False                          Y
    C10  Prop5 fcx raw: |a2_fcx| > |a2_prim| (psi_F 0.744, psi_C 0.885)                 Y
    C10  Prop5 xau raw: 0 <= a2_xau/a2_prim < 1 (closed 0.773, sim 0.775)               Y
    C10  Prop3 raw: opposite signs of b and p$ predicted False                          Y
    C11  Prop5 fcx abn: |a2_fcx| > |a2_prim| (psi_F 0.390, psi_C 0.627)                 Y
    C11  Prop5 xau abn: 0 <= a2_xau/a2_prim < 1 (closed 0.681, sim 0.690)               Y
    C11  Prop3 abn: opposite signs of b and p$ predicted False                          Y
    C11  Prop5 fcx raw: |a2_fcx| > |a2_prim| (psi_F 0.390, psi_C 0.627)                 Y
    C11  Prop5 xau raw: 0 <= a2_xau/a2_prim < 1 (closed 0.681, sim 0.690)               Y
    C11  Prop3 raw: opposite signs of b and p$ predicted False                          Y
    C12  Prop3 abn: opposite signs of b and p$ predicted False                          Y
    C12  Prop5 fcx raw: |a2_fcx| > |a2_prim| (psi_F 0.390, psi_C 0.627)                 Y
    C12  Prop5 xau raw: 0 <= a2_xau/a2_prim < 1 (closed 0.681, sim 0.683)               Y
    C12  Prop3 raw: opposite signs of b and p$ predicted True                           Y
    C13  Prop5 fcx abn: |a2_fcx| > |a2_prim| (psi_F 0.390, psi_C 0.627)                 Y
    C13  Prop5 xau abn: 0 <= a2_xau/a2_prim < 1 (closed 0.838, sim 0.839)               Y
    C13  Prop3 abn: opposite signs of b and p$ predicted True                           Y
    C13  Prop5 fcx raw: |a2_fcx| > |a2_prim| (psi_F 0.390, psi_C 0.627)                 Y
    C13  Prop5 xau raw: 0 <= a2_xau/a2_prim < 1 (closed 0.838, sim 0.842)               Y
    C13  Prop3 raw: opposite signs of b and p$ predicted True                           Y
    C14  Prop5 fcx abn: |a2_fcx| < |a2_prim| (psi_F 0.929, psi_C 0.627)                 Y
    C14  Prop5 xau abn: 0 <= a2_xau/a2_prim < 1 (closed 0.681, sim 0.680)               Y
    C14  Prop3 abn: opposite signs of b and p$ predicted True                           Y
    C14  Prop5 fcx raw: |a2_fcx| < |a2_prim| (psi_F 0.929, psi_C 0.627)                 Y
    C14  Prop5 xau raw: 0 <= a2_xau/a2_prim < 1 (closed 0.681, sim 0.676)               Y
    C14  Prop3 raw: opposite signs of b and p$ predicted True                           Y

    max |closed - exact| = 2.220e-16
    max |closed - sim| (a2, b) = 0.00370   max |closed - sim|/SE = 3.05
    M2 CHECK: True

## 8. Criteria for tier (iii)

Throughout, "H3 rejects" means a two-sided rejection of a₂ = 0 at 5% under the primary inference method (Driscoll–Kraay with the normal reference), on the primary rows. Signs are stated for S1 (κ, κ_A < 0); under the mirror case every sign flips.

**(A) Directional H3 on the primary target, with metals rows that preserve the sign.** Maps to option (a).
- **H3:** rejects, with â₂ > 0.
- **`copx_to_fcx`:** â₂ > 0 with FCX, and also with COPX on the same FCX-finite rows. No requirement on the size of the change, because Proposition 5(i) cannot predict its direction.
- **`xau_control`:** â₂ > 0 with XAU added. The ratio â₂^xau/â₂^prim is reported, not required. The model predicts it lies in [0, π′/π], but it approaches π′/π, which may be near 1, when the miners' gold term is small, so noise alone can push it above 1.
- **`raw_target`:** reported; not required.
- **Rests on (not checkable before the data are seen):**
  - S1 and S2;
  - S3 for both metals controls;
  - S4, since 1306 must fully price its non-dollar translation and metals channels;
  - S5 in its abnormal form;
  - S6;
  - the absence of any other underpriced pure-dollar channel outside the model, such as dollar costs or debt revaluation (Corollary).
  
  S4 and S5 restrict unpriced loadings of the target itself. They add terms with the same footprint as the cascade in every row, so they cannot be checked even after the data are seen.

**(B) As (A), plus agreement of the raw target.** Maps to option (a).
- **H3 and the metals rows:** as in (A).
- **`raw_target`:** a₂ = 0 rejects with â₂^raw > 0, and both metals rows on the raw target keep â₂^raw > 0.
- **Rests on:**
  - S1–S3 and S6;
  - S5 in its raw form, n_i = n^R_i = 0, unless the nuisance factors are orthogonal to the residual FX factors;
  - the same out-of-model condition as (A).
  
  S4 is no longer needed for the raw conclusion. But the raw form of S5 is much stronger than the abnormal form: it requires each miner's full unpriced exposure to off-session news, including the market-wide part that the hedge would remove, to be orthogonal to the residual FX factors. The raw target is also noisier, so (B) costs power.

**(C) Sign-free H3.** Maps to option (a) in form, but it is not admissible as written.
- **H3:** rejects, in either direction.
- **Metals rows:** both rows keep the sign of â₂.
- **`raw_target`:** not required.
- **Rests on:** S3–S6 and the out-of-model condition; S1 and S2 drop out.

It fails P32's "in the predicted direction" requirement, so it could be used only by amending P32. It is listed because it shows that dropping the κ assumption removes only S1–S2; the uncheckable S4–S5 remain.

**(D) No tier-(iii) claim.** Maps to option (c). Report, without a tier-(iii) reading:
- H3: â₂, its DK SE and the two-sided p-value;
- `copx_to_fcx`, with and without the swap on the same rows;
- `xau_control`, with and without XAU;
- `raw_target`, with the gap â₂^raw − â₂^abn. Lemma 3(iii) says this gap is β̄·a₂^M in population, which is exact only with constant β.

The pre-stated reading is that a₂ is the session drift on EUR/USD conditional on usdjpy_ret, SPY and COPX. By this note's Propositions 1, 2 and 5, its sign is not attributable to the metals channel. b is read with the qualifier of Proposition 4.

**Recommendation: (D), that is, option (c).**
1. No (a)-type criterion survives without assumptions that cannot be checked before the data are seen. S4 and S5 cannot be checked even after.
2. Even with every assumption granted, no row of the design separates the metals channel from other dollar-linked underpricing. Off-session risk sentiment, which P32 already names as a confound for b, passes both metals-row checks (Corollary; cell C07). So the tier-(iii) wording, "dollar → metals → miner", would outrun the identification, the very thing P32's own reason forbids.
3. The tier-(ii) Japan 225 row partly controls off-session Japan-equity news. But it covers only eligible nights and is not part of H3's design, so it does not discharge S5 for a₂.
4. The cost of (c) is small. Every number is still reported, and nothing about H1 changes.

If Isaiah nevertheless prefers (a), (A) is the version to use, and its write-up should name S4 and S5 explicitly. S1 alone could be examined without the target: under A2–A3, Cov(xau_ret, eurusd_ret) = −λκ_A·Var(D), so sign(κ_A) = −sign Cov(xau_ret, eurusd_ret), conditional on gold not loading on euro-specific news. That is a look at window data, though, so whether to take it is Isaiah's decision. It would not rescue (a), because S4 and S5 remain.

## 9. Limits

1. **Linearity and constant coefficients.** Everything is a population linear projection with constant loadings. Threshold or state-dependent pricing, such as larger moves priced more fully, is outside the model. So are pricing shares that vary over time.
2. **Night types.** Some nights have no US session, so the US controls are exactly 0; others have several sessions or a longer window. Lemmas 1–3 still hold exactly, with every variance replaced by its pooled (sample-weighted) value, provided two things are true:
   - every loading (λ, λ_o, κ, κ_A, φ, g, σ, the ζ's and every c) is the same on all night types;
   - all shocks have mean zero within each type.
   
   *Proof:* the pooled second-moment matrix of the regressors and targets is then that of a single-type model with pooled primitive variances, because the primitives stay mutually uncorrelated in the pool. That justifies applying the closed forms to the pooled panel. If the loadings differ by night type, the pooled coefficients are second-moment-weighted mixtures and the sign results need the sign assumptions to hold for every type.

   This is shown by the argument above. The committed check does not include a mixed-night cell.
3. **Estimated β.** Lemma 3(iv) assumes independence over days. Under time-varying volatility it gains the term Cov(β̂_{t−1}, E_{t−1}[x̃_t·h_t]), and sampling error in β̂ adds variance; both are M3's remit. Cell C12 uses a shorter warm-up than the study's β rule; this does not affect the population results.
4. **One metals basket.** The three miners' metals mixes differ. With several metals, each term c_m·κ_q(m) becomes a sum over metals, and S1–S2 must hold for that sum. So a firm net short one metal through smelting margins can reverse its term.
5. **EUR/USD.** E is treated as independent of the other factors. Euro-area risk news is admitted only through ζ_E. If euro-specific moves carry their own unpriced channel for these firms, θ_E ≠ 0 even for the raw target, and P15's equal-drift reading fails (Proposition 6(ii)).
6. **Session dynamics.** A6 makes session FX and metals moves martingale increments. Session continuation, the case the mechanism specification separates, is outside the model.
7. **The FCX sample.** Proposition 5(i) compares population coefficients. In the study, the swap is reported on the FCX-finite rows with and without the swap. The population comparison carries over if the missingness is independent of the shocks.
8. **The check verifies algebra, not economics.** The parameter grid is arbitrary. The script shows that the closed forms are the projections of the stated model, and that the sample analogue converges to them. It says nothing about whether the model's sign assumptions hold for these firms. The model is also population-level, so no power is given for H3 or the rows.
9. **Literature.** The note relies on no external literature.

## 10. Attestation

I read only these passages, with the file viewer and line ranges:
- PLAN.md, lines 69–137, 326–347 and 348–395;
- DECISIONS_P14_onward.md, lines 21–42, 66–84 and 296–335;
- DECISIONS_P37_onward.md, lines 355–368;
- DATA_DICTIONARY.md, lines 30–40, 58–66 and 92–98.

I read no other Project file.

I opened, read, previewed, searched, hashed and listed none of the following: panel_dev.csv, events_firm.csv, events_boj.csv, or any .csv, .xlsx or .gz file. The interface attached column names and row counts of the three data files to the request; I ignored them and used none of them. I ran and imported no Project code. I used no web search and no project_knowledge_search. Every number in this note comes from the synthetic check in §7, with parameter values I chose arbitrarily.
