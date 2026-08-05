"""Shared deterministic hashing used by world_generator and sub_realm_generator.

No stored RNG state: any (seed, ...parts) always mixes down to the same
random.Random stream, so the whole world (overworld + every dungeon/sky
realm) is fully reproducible from one top-level seed.

Note: this does not aim for bit-exact parity with the old Kotlin engine's
kotlin.random.Random (a different PRNG algorithm) -- only for Python-internal
determinism, which is all a from-scratch web port needs.
"""
from __future__ import annotations

import random

_MASK64 = (1 << 64) - 1
_C1 = 0xBF58476D1CE4E5B9
_C2 = 0x94D049BB133111EB


def mix64(z0: int) -> int:
    """splitmix64-style bit mixer."""
    z = z0 & _MASK64
    z = ((z ^ (z >> 30)) * _C1) & _MASK64
    z = ((z ^ (z >> 27)) * _C2) & _MASK64
    return z ^ (z >> 31)


def seed(*parts: int) -> int:
    """Folds any number of int 'salt' parts into one deterministic seed via repeated mix64."""
    acc = 0
    for p in parts:
        acc = mix64((acc ^ mix64(p & _MASK64)) & _MASK64)
    return acc


def make_random(*parts: int) -> random.Random:
    return random.Random(seed(*parts))


def string_hash(s: str) -> int:
    """Deterministic string hash (Java/Kotlin String.hashCode algorithm) -- NOT Python's randomized hash()."""
    h = 0
    for ch in s:
        h = (31 * h + ord(ch)) & 0xFFFFFFFF
    if h >= 0x80000000:
        h -= 0x100000000
    return h
