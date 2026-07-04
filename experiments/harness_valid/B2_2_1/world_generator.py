"""B2.2.1 world generator — side-channel-hardened.

Identical to B2.2's generator EXCEPT the fix required by the corrected prompt:
learner_view must expose NO side-channel. B2.2 returned each vertex's out-neighbour
list sorted by DISTANCE RANK, which leaks ordinal distance information the paper's
model explicitly excludes ("we do not know ... distances to the neighbours", p.2).
Here out-neighbours are emitted in VERTEX-ID order — an order-free canonical form
carrying zero distance/rank information. The set-based estimators are unaffected;
this only closes the boundary leak.

world_generator.py MAY use coordinates and distances internally (generation needs
them). The prohibition applies only to learner_view(), the single exit point.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

_SAMPLERS: dict[str, tuple[Callable, int, int]] = {}


def _register(name, d_true, ambient):
    def deco(fn):
        _SAMPLERS[name] = (fn, d_true, ambient)
        return fn
    return deco


@_register("helix", d_true=1, ambient=3)
def _helix(rng, n):
    t = rng.uniform(0.0, 6.0 * np.pi, size=n)
    return np.stack([np.cos(t), np.sin(t), 0.5 * t], axis=1)


@_register("swiss_roll", d_true=2, ambient=3)
def _swiss_roll(rng, n):
    t = 1.5 * np.pi * (1.0 + 2.0 * rng.uniform(0.0, 1.0, size=n))
    height = 21.0 * rng.uniform(0.0, 1.0, size=n)
    return np.stack([t * np.cos(t), height, t * np.sin(t)], axis=1)


@_register("gaussian", d_true=5, ambient=5)
def _gaussian5(rng, n):
    return rng.standard_normal(size=(n, 5))


@_register("sphere", d_true=7, ambient=8)
def _sphere7(rng, n):
    x = rng.standard_normal(size=(n, 8))
    return x / np.linalg.norm(x, axis=1, keepdims=True)


@_register("cube", d_true=12, ambient=12)
def _cube12(rng, n):
    return rng.uniform(0.0, 1.0, size=(n, 12))


def k_for_n(n: int) -> int:
    """Paper Section 4.1: k=15 if n<=1000 else k=20."""
    return 15 if n <= 1000 else 20


def _directed_knn_adjacency(points: np.ndarray, k: int, chunk: int = 512) -> list[list[int]]:
    """Out-neighbours = the k nearest points (excluding self) by Euclidean distance.
    Distances are used here and then discarded. Neighbours are returned in
    VERTEX-ID order (NOT distance order) so no ordinal information leaks."""
    n = points.shape[0]
    adjacency: list[list[int]] = []
    sq = np.einsum("ij,ij->i", points, points)
    for start in range(0, n, chunk):
        end = min(start + chunk, n)
        block = points[start:end]
        d2 = sq[None, :] + np.einsum("ij,ij->i", block, block)[:, None] - 2.0 * block @ points.T
        for r in range(end - start):
            i = start + r
            d2[r, i] = np.inf
            nn = np.argpartition(d2[r], k)[:k]
            adjacency.append(sorted(int(j) for j in nn))  # id-sorted: order-free
    return adjacency


def generate_world(seed: int, distribution: str, n: int) -> dict:
    if distribution not in _SAMPLERS:
        raise ValueError(f"unknown distribution {distribution!r}")
    sampler, d_true, ambient = _SAMPLERS[distribution]
    rng = np.random.default_rng(seed)
    points = sampler(rng, n)
    k = k_for_n(n)
    adjacency = _directed_knn_adjacency(points, k)
    return {
        "learner_view": {"adjacency": adjacency, "n": n, "k": k, "seed_id": seed},
        "truth": {"d_true": d_true, "distribution": distribution, "ambient_D": ambient, "seed": seed},
    }


def generate_random_graph_control(seed: int, n: int, k: int | None = None) -> dict:
    """Negative control: strictly k-regular directed random graph, NO geometry,
    NO coordinates. Out-neighbours = random k-subset of vertices (!= self),
    returned in vertex-id order."""
    k = k_for_n(n) if k is None else k
    rng = np.random.default_rng(seed)
    adjacency: list[list[int]] = []
    for i in range(n):
        choices = rng.choice(np.delete(np.arange(n), i), size=k, replace=False)
        adjacency.append(sorted(int(j) for j in choices))
    return {
        "learner_view": {"adjacency": adjacency, "n": n, "k": k, "seed_id": seed},
        "truth": {"d_true": None, "distribution": "random_graph_control", "ambient_D": None, "seed": seed},
    }


# allowed learner-facing keys — anything else in learner_view would be a leak
ALLOWED_LEARNER_KEYS = frozenset({"adjacency", "n", "k", "seed_id"})


def learner_view(world: dict) -> dict:
    """Single exit point. Returns ONLY adjacency + allowed metadata; asserts no
    truth key ever crosses (fail closed on accidental side-channel)."""
    view = world["learner_view"]
    leaked = set(view) - ALLOWED_LEARNER_KEYS
    if leaked:
        raise ValueError(f"learner_view side-channel: disallowed keys {sorted(leaked)}")
    return view


AVAILABLE_DISTRIBUTIONS = tuple(_SAMPLERS.keys())
