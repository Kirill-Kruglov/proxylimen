"""Kleindessner & von Luxburg (AISTATS 2015) dimension estimators, exact.

"Dimensionality estimation without distances", PMLR v38, pp.471-479.
Implemented verbatim from the paper; NOT a home-grown heuristic.

E_CAP  (spherical-cap, elaborate estimator; paper Section 2.2, Eq. 1):
    S(d) = I_{3/4}((d+1)/2, 1/2)                                     (Eq. 1, p.3)
    L_CAP(i) = min_{j : i->j} |B_SP(i,1) ∩ B_SP(j,1)| / (k+1)  ≈ S(d)  (p.3)
    L_CAP(A) = mean_{i in A} L_CAP(i);  E_CAP(A) = S^{-1}(L_CAP(A))     (p.3)
    (average the L's, THEN invert — not the other way round.)

E_DP   (doubling-property, naive baseline; paper Section 2.1):
    L_DP(i)  = |B_SP(i,1)| / |B_SP(i,2)|                                (p.2)
    L_DP(A)  = mean_{i in A} L_DP(i);  E_DP(A) = -log2(L_DP(A))          (p.2)

Graph balls (paper p.2): B_SP(i,r) = {j : d_SP(i,j) <= r} under the DIRECTED
shortest-path distance in the kNN graph. |B_SP(i,1)| = k+1 always. Paper's
matrix identities (Section 4.1, p.6): with J~ = adjacency + self-loops,
(J~ J~)_{ij} > 0  <=>  j in B_SP(i,2);  (J~ J~^T)_{ij} = |B_SP(i,1) ∩ B_SP(j,1)|.
We compute these directly as set operations, which is equivalent.

DEVIATION FROM SPEC: the task assumed scipy.special.betainc is available; it is
NOT installed in this environment (numpy only). The regularized incomplete beta
I_x(a,b) is therefore implemented here via the Numerical-Recipes continued
fraction (betacf/betai) and validated in __main__ against closed-form values
(I_{3/4}(1,1/2)=1/2 exactly; I_{3/4}(1/2,1/2)=(2/pi)arcsin(sqrt(3/4))=2/3).

LEAKAGE DISCIPLINE: e_cap / e_dp take ONLY the graph adjacency and a vertex
subset. No d_true, coordinates, or distances appear in any signature or closure.
"""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np

Adjacency = Sequence[Sequence[int]]  # adjacency[i] = out-neighbours of vertex i


# --------------------------------------------------------------------------- #
# regularized incomplete beta  I_x(a,b)  (Numerical Recipes betai/betacf)
# --------------------------------------------------------------------------- #
def _betacf(a: float, b: float, x: float) -> float:
    MAXIT, EPS, FPMIN = 300, 3.0e-16, 1.0e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < FPMIN:
        d = FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < EPS:
            break
    return h


def reg_incomplete_beta(a: float, b: float, x: float) -> float:
    """I_x(a,b), the regularized incomplete beta function."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    ln_beta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(ln_beta + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def S(d: float) -> float:
    """Paper Eq. (1): S(d) = I_{3/4}((d+1)/2, 1/2). Strictly decreasing in d."""
    return reg_incomplete_beta((d + 1.0) / 2.0, 0.5, 0.75)


# fine-meshed lookup table for S^{-1} (paper Section 4.1: real-valued estimate)
_D_GRID = np.round(np.arange(0.5, 30.0 + 1e-9, 0.1), 4)
_S_GRID = np.array([S(float(d)) for d in _D_GRID])


def invert_S(l_value: float) -> float:
    """S^{-1}(l): the grid dimension whose S is closest to l (paper's lookup)."""
    return float(_D_GRID[int(np.argmin(np.abs(_S_GRID - l_value)))])


# --------------------------------------------------------------------------- #
# graph balls
# --------------------------------------------------------------------------- #
def _ball1(adjacency: Adjacency) -> list[frozenset]:
    """B_SP(i,1) = {i} ∪ out-neighbours(i)."""
    return [frozenset((i, *adjacency[i])) for i in range(len(adjacency))]


# --------------------------------------------------------------------------- #
# estimators  (graph + vertex subset ONLY; no ground truth anywhere)
# --------------------------------------------------------------------------- #
def l_cap_local(adjacency: Adjacency, vertex_subset: Sequence[int], _ball=None) -> list[float]:
    ball1 = _ball if _ball is not None else _ball1(adjacency)
    out: list[float] = []
    for i in vertex_subset:
        bi = ball1[i]
        kp1 = len(bi)  # = k+1
        neighbours = adjacency[i]
        if not neighbours:
            continue
        overlap_min = min(len(bi & ball1[j]) for j in neighbours)
        out.append(overlap_min / kp1)
    return out


def e_cap(adjacency: Adjacency, vertex_subset: Sequence[int]) -> float:
    """E_CAP(A) = S^{-1}( mean_i L_CAP(i) )."""
    locals_ = l_cap_local(adjacency, vertex_subset)
    if not locals_:
        raise ValueError("empty vertex subset for e_cap")
    return invert_S(sum(locals_) / len(locals_))


def l_dp_local(adjacency: Adjacency, vertex_subset: Sequence[int], _ball=None) -> list[float]:
    ball1 = _ball if _ball is not None else _ball1(adjacency)
    out: list[float] = []
    for i in vertex_subset:
        two_hop = set(ball1[i])
        for j in adjacency[i]:
            two_hop |= ball1[j]  # B_SP(i,2) = ball1(i) ∪ (∪_{j->} ball1(j))
        out.append(len(ball1[i]) / len(two_hop))
    return out


def e_dp(adjacency: Adjacency, vertex_subset: Sequence[int]) -> float:
    """E_DP(A) = -log2( mean_i L_DP(i) )."""
    locals_ = l_dp_local(adjacency, vertex_subset)
    if not locals_:
        raise ValueError("empty vertex subset for e_dp")
    return -math.log2(sum(locals_) / len(locals_))


if __name__ == "__main__":
    # betai validation against closed forms
    v1 = reg_incomplete_beta(1.0, 0.5, 0.75)          # I_{3/4}(1,1/2) = 1-(1-x)^0.5 = 0.5
    v2 = reg_incomplete_beta(0.5, 0.5, 0.75)          # (2/pi) arcsin(sqrt(0.75)) = 2/3
    print("I_3/4(1,1/2)   =", v1, " expected 0.5      err", abs(v1 - 0.5))
    print("I_3/4(1/2,1/2) =", v2, " expected 0.666667 err", abs(v2 - 2/3))
    print("S(1) =", S(1), " S(2) =", S(2), " S(5) =", S(5), " S(7) =", S(7), " S(12) =", S(12))
    print("S monotone decreasing on grid:", bool(np.all(np.diff(_S_GRID) < 0)))
    for d in (1, 2, 5, 7, 12):
        print(f"  invert_S(S({d})) = {invert_S(S(d))}")
