"""Split-half consistency — a blind honesty check (no ground truth).

For a world's kNN graph, split the vertex set into two disjoint random halves
A1, A2, estimate E_CAP independently on each, and report |E_CAP(A1) - E_CAP(A2)|.
For a genuine geometric world this should be small; the check requires NO d_true,
so it is a self-standing gate-check that runs before any comparison to truth.

The same statistic on the random_graph_control tells us whether small split-half
disagreement actually certifies geometry or is just an artifact of k-regularity —
if the control is also consistent, that is reported as a finding, not hidden.
"""

from __future__ import annotations

import numpy as np

from estimators import e_cap, e_dp


def split_half(adjacency, seed: int) -> dict:
    n = len(adjacency)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)
    half = n // 2
    a1 = sorted(int(v) for v in perm[:half])
    a2 = sorted(int(v) for v in perm[half:])
    ec1, ec2 = e_cap(adjacency, a1), e_cap(adjacency, a2)
    ed1, ed2 = e_dp(adjacency, a1), e_dp(adjacency, a2)
    return {
        "e_cap_A1": ec1,
        "e_cap_A2": ec2,
        "e_cap_abs_diff": abs(ec1 - ec2),
        "e_dp_A1": ed1,
        "e_dp_A2": ed2,
        "e_dp_abs_diff": abs(ed1 - ed2),
    }
