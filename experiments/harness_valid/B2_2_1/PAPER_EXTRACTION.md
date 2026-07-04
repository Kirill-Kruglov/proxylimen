# PAPER_EXTRACTION — Kleindessner & von Luxburg, AISTATS 2015

Source: M. Kleindessner and U. von Luxburg, "Dimensionality estimation without
distances", Proc. 18th AISTATS, PMLR vol. 38, pp. 471–479, 2015.
PDF: https://www.tml.cs.uni-tuebingen.de/team/luxburg/publications/KleindessnerLuxburg_AISTATS2015.pdf
PMLR: https://proceedings.mlr.press/v38/kleindessner15.html

All quotes below were transcribed from the rendered PDF (read directly), NOT from
any numbers passed in a prompt. Page numbers refer to the PDF's printed pages.

---

## (a) Formulas

### kNN graph (Section 2, "Setup", p.2), verbatim
> "It has the vertex set V = {1, …, n} and a directed, unweighted edge from i to j
> (written as i → j) if and only if x_j is among the k nearest sample points to
> x_i with respect to ‖·‖_{R^D}."

### E_DP — doubling property (Section 2.1, p.2), verbatim
Continuous property and definition:
> "d = −log₂(λ_d(B(x,r)) / λ_d(B(x,2r)))."

> "L_DP(i) := |B_SP(i,1)| / |B_SP(i,2)| ≈ … = 1/2^d."

> "Note that |B_SP(i,1)| always equals k + 1."

> "Hence, an estimate of d is given by −log₂ L_DP(i). However, in order to obtain
> a more robust estimator we average over L_DP(i) for various vertices i ∈ A ⊆ V.
> With L_DP(A) := (1/|A|) Σ_{i∈A} L_DP(i) this leads to our first dimension
> estimator  E_DP(A) := −log₂ L_DP(A)."

### E_CAP — spherical caps (Section 2.2, p.3), verbatim
Cap volume (attributed to Li, 2011):
> "the volume of such a cap is given by  ½ η_d r^d I_{3/4}((d+1)/2, 1/2),  where
> I_x(a,b) is the regularized incomplete beta function."

Equation (1):
> "λ_d(B(x,r) ∩ B(y,r)) / λ_d(B(x,r)) = I_{3/4}((d+1)/2, 1/2) =: S(d),   (1)
> a quantity injectively depending on d > 0."

Local statistic and estimator:
> "L_CAP(i) := min_{j∈V : i→j} |B_SP(i,1) ∩ B_SP(j,1)| / (k+1) ≈ S(d)."

> "With L_CAP(A) := (1/|A|) Σ_{i∈A} L_CAP(i), our second dimension estimator is
> given by  E_CAP(A) := S^{-1}(L_CAP(A))."

Note: E_CAP and E_DP both **average the local L over the vertex subset first,
then invert** (S^{-1} resp. −log₂). Not the reverse.

### Inversion of S (Section 4.1, p.6), verbatim
> "There is no closed form for the inverse of the function S as given in (1). If
> one is merely interested in an integer estimate, the simplest procedure is to
> set E_CAP(A) to d* = arg min_{d∈N} |S(d) − L_CAP(A)|. In case one would rather
> like a real-valued estimate, the simplest way is to create a fine-meshed lookup
> table."

---

## (b) B_SP(i,r) — DIRECTED, not symmetrized (Section 2, p.2), verbatim

> "we denote by B_SP(i,r) the closed ball with center i ∈ V and radius r > 0 in
> the graph G with respect to the (directed) shortest path distance d_SP, that is
> B_SP(i,r) = {j ∈ V : d_SP(i,j) ≤ r}."

**Resolution: the shortest-path distance is DIRECTED (edges used as i→j only); the
graph is NOT symmetrized.** So B_SP(i,1) = {i} ∪ out-neighbours(i) (size k+1), and
B_SP(i,2) = vertices reachable from i by a directed walk of length ≤ 2.

Confirmed by the matrix identities (Section 4.1, p.6), verbatim:
> "(J̃ · J̃)_{ij} > 0 ⟺ j ∈ B_SP(i,2),   (J̃ · J̃^T)_{ij} = |B_SP(i,1) ∩ B_SP(j,1)|.
> Here, J̃ is the matrix J with the diagonal entries set to 1."
(J is the directed adjacency matrix J_{ij}=1 iff i→j.) J̃·J̃ (not symmetrized)
gives directed 2-reachability; J̃·J̃^T gives the shared-1-ball count.

No ambiguity remains for the implementation.

### k rule (Section 4.1, p.6), verbatim
> "For E_DP and E_CAP we simply set k = 15 if the size of the dataset is less than
> or equal to 1000 (for the real datasets this is (8) and (9)) and k = 20 in all
> other experiments (which deal with datasets of size 5000 or slightly greater)."

Table 1 has NO explicit k column; k is fixed by this text rule.

---

## (c) Table 1 (p.6) — "Estimated dimensions for several datasets."

Columns: n | Distribution / Dataset | d | E_CAP(V) | E_DP(V) | MLE | CorrDim | RegDim.
Artificial datasets: results averaged over 100 runs, ±STD. Real datasets: D =
dimension of observation space; d unknown ("?").

| # | n | Distribution / Dataset | d | E_CAP(V) | E_DP(V) | MLE | CorrDim | RegDim |
|---|---|---|---|---|---|---|---|---|
| 1 | 1000 | uniform on a helix in R³ | 1 | 1.00 (±0.05) | 0.88 (±0.01) | 1.00 (±0.01) | 1.00 (±0.11) | 0.99 (±0.01) |
| 2 | 1000 | Swiss roll in R³ | 2 | 2.14 (±0.05) | 1.44 (±0.01) | 1.94 (±0.02) | 1.99 (±0.23) | 1.87 (±0.04) |
| 3 | 1000 | N₅(0,I) | 5 | 5.33 (±0.07) | 2.47 (±0.01) | 5.00 (±0.04) | 4.91 (±0.56) | 4.86 (±0.05) |
| 4 | 1000 | uniform on sphere S⁷ ⊆ R⁸ | 7 | 5.88 (±0.06) | 2.82 (±0.01) | 6.53 (±0.07) | 6.85 (±0.66) | 6.23 (±0.09) |
| 5 | 5000 | uniform on sphere S⁷ ⊆ R⁸ | 7 | 6.85 (±0.03) | 3.21 (±0.00) | 6.72 (±0.03) | 6.95 (±0.98) | 6.46 (±0.04) |
| 6 | 1000 | uniform on [0,1]¹² | 12 | 7.74 (±0.07) | 3.04 (±0.01) | 9.32 (±0.10) | 10.66 (±1.18) | 8.78 (±0.10) |
| 7 | 5000 | uniform on [0,1]¹² | 12 | 9.24 (±0.04) | 3.50 (±0.00) | 9.76 (±0.05) | 10.83 (±1.49) | 9.26 (±0.05) |
| 8 | 698 | Isomap faces, D=4096=64² | ? | 3.04 | 1.73 | 3.99 | 3.53 | 4.22 |
| 9 | 481 | Hands, D=245760 | ? | 1.27 | 0.95 | 2.88 | 3.92 | 2.56 |
| 10 | 7141 | MNIST digit 3, D=784=28² | ? | 8.92 | 3.21 | 15.95 | 14.17 | 14.75 |
| 11 | 6824 | MNIST digit 4, D=784=28² | ? | 8.13 | 3.07 | 14.44 | 9.54 | 13.16 |
| 12 | 6313 | MNIST digit 5, D=784=28² | ? | 8.40 | 3.12 | 15.55 | 18 | 14.28 |

Rows 1–7 are the artificial datasets used as B2.2.1 core worlds (each carries a
literal E_CAP(V) anchor). Rows 8–12 (real data, unknown d) are not used for
PASS/FAIL. k per row: 15 for n=1000 rows, 20 for n=5000 rows (Section 4.1 rule).

### Supporting: Table 2 (p.6) — N₇(0,I), E over 10 random vertices R, ±STD
Used to note E_CAP's mild "overshoot" and E_DP's severe underestimation at scale:
n=5·10⁴ k=500 → E_CAP(R) 6.77(±0.19), E_DP(R) 4.36(±0.01); … n=10⁷ k=5000 →
E_CAP(R) 7.95(±0.20), E_DP(R) 5.84(±0.02). (Not used for B2.2.1 gate cells.)
