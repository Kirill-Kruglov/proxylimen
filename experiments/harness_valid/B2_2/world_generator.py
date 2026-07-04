"""Synthetic worlds for B2.2 blind dimension estimation.

NOT the B2 relational generator — different data structure entirely. Here a world
is n points sampled from a distribution in R^D, from which we build a DIRECTED
unweighted kNN graph (Euclidean distance in generation space) and then DISCARD
the coordinates and distances. Only the adjacency (out-neighbour lists) crosses
into learner_view. No coordinate or distance value ever leaves this module.

Distributions reproduce the paper's Table 1 artificial datasets exactly, so each
d_true carries a literal Table 1 tolerance anchor:
    helix (d=1, R^3)  swiss_roll (d=2, R^3)  gaussian N_5 (d=5, R^5)
    sphere S^7 (d=7, R^8)  cube [0,1]^12 (d=12, R^12)

k rule (paper Section 4.1, p.6, verbatim): k=15 if n<=1000 else k=20.

random_graph_control: a k-regular directed graph with random out-edges and NO
underlying geometry — not a projection from any R^d, no coordinates at all.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

# distribution label -> (sampler(rng, n) -> (N, D) array, d_true, ambient_D)
_SAMPLERS: dict[str, tuple[Callable, int, int]] = {}


def _register(name, d_true, ambient):
    def deco(fn):
        _SAMPLERS[name] = (fn, d_true, ambient)
        return fn
    return deco


@_register("helix", d_true=1, ambient=3)
def _helix(rng, n):
    t = rng.uniform(0.0, 6.0 * np.pi, size=n)  # uniform in arc-length (const speed)
    return np.stack([np.cos(t), np.sin(t), 0.5 * t], axis=1)


@_register("swiss_roll", d_true=2, ambient=3)
def _swiss_roll(rng, n):
    t = 1.5 * np.pi * (1.0 + 2.0 * rng.uniform(0.0, 1.0, size=n))
    height = 21.0 * rng.uniform(0.0, 1.0, size=n)
    return np.stack([t * np.cos(t), height, t * np.sin(t)], axis=1)


@_register("gaussian", d_true=5, ambient=5)
def _gaussian5(rng, n):
    return rng.standard_normal(size=(n, 5))  # N_5(0, I)


@_register("sphere", d_true=7, ambient=8)
def _sphere7(rng, n):
    x = rng.standard_normal(size=(n, 8))
    return x / np.linalg.norm(x, axis=1, keepdims=True)  # uniform on S^7 ⊆ R^8


@_register("cube", d_true=12, ambient=12)
def _cube12(rng, n):
    return rng.uniform(0.0, 1.0, size=(n, 12))  # uniform on [0,1]^12


def k_for_n(n: int) -> int:
    """Paper Section 4.1: k=15 if n<=1000 else k=20."""
    return 15 if n <= 1000 else 20


def _directed_knn_adjacency(points: np.ndarray, k: int, chunk: int = 512) -> list[list[int]]:
    """Out-neighbour lists: the k nearest points (excluding self) by Euclidean
    distance in generation space. Distances are used here and then discarded."""
    n = points.shape[0]
    adjacency: list[list[int]] = []
    sq = np.einsum("ij,ij->i", points, points)
    for start in range(0, n, chunk):
        end = min(start + chunk, n)
        block = points[start:end]
        # squared distances block x n
        d2 = sq[None, :] + np.einsum("ij,ij->i", block, block)[:, None] - 2.0 * block @ points.T
        for r in range(end - start):
            i = start + r
            d2[r, i] = np.inf  # exclude self
            nn = np.argpartition(d2[r], k)[:k]
            nn = nn[np.argsort(d2[r, nn])]  # deterministic order
            adjacency.append([int(j) for j in nn])
    return adjacency


def generate_world(seed: int, distribution: str, n: int) -> dict:
    """Build a geometric world. Returns learner_view (adjacency only) plus a
    SEPARATE truth block (d_true) used exclusively for evaluation."""
    if distribution not in _SAMPLERS:
        raise ValueError(f"unknown distribution {distribution!r}")
    sampler, d_true, ambient = _SAMPLERS[distribution]
    rng = np.random.default_rng(seed)
    points = sampler(rng, n)
    k = k_for_n(n)
    adjacency = _directed_knn_adjacency(points, k)
    return {
        "learner_view": {"adjacency": adjacency, "n": n, "k": k},
        "truth": {"d_true": d_true, "distribution": distribution, "ambient_D": ambient, "seed": seed},
    }


def generate_random_graph_control(seed: int, n: int, k: int | None = None) -> dict:
    """Negative control: strictly k-regular directed random graph, NO geometry,
    NO coordinates. Each vertex gets k distinct random out-neighbours (!= self)."""
    k = k_for_n(n) if k is None else k
    rng = np.random.default_rng(seed)
    adjacency: list[list[int]] = []
    for i in range(n):
        choices = rng.choice(np.delete(np.arange(n), i), size=k, replace=False)
        adjacency.append([int(j) for j in choices])
    return {
        "learner_view": {"adjacency": adjacency, "n": n, "k": k},
        "truth": {"d_true": None, "distribution": "random_graph_control", "ambient_D": None, "seed": seed},
    }


def learner_view(world: dict) -> dict:
    """The ONLY thing an estimator may see: the adjacency (no coords/distances)."""
    return world["learner_view"]


AVAILABLE_DISTRIBUTIONS = tuple(_SAMPLERS.keys())
