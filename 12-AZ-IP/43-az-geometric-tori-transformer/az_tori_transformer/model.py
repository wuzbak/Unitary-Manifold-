# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""The Geometric Tori Transformer model: a stack of toroidal attention blocks."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .attention import ToroidalMultiHeadAttention
from .baseline_attention import MatchedRopeMultiHeadAttention, RopeMultiHeadAttention
from .layers import Embedding, FeedForward, Linear, LayerNorm
from .tensor import Tensor

__all__ = ["GeometricToriTransformerConfig", "TransformerBlock", "GeometricToriTransformer"]


@dataclass(frozen=True)
class GeometricToriTransformerConfig:
    vocab_size: int
    dim: int = 32
    num_heads: int = 4
    num_layers: int = 2
    ff_hidden_dim: int = 64
    causal: bool = True
    seed: int = 0
    #: "toroidal" (default): Z_74 rotary encoding + learned bank bias.
    #: "rope": legacy continuous RoPE without bias.
    #: "rope_matched": continuous RoPE with the same learned bank bias,
    #: reserved for parameter-matched positional ablations.
    positional_mode: str = "toroidal"

    def __post_init__(self) -> None:
        if self.dim % self.num_heads != 0:
            raise ValueError("dim must be divisible by num_heads")
        if (self.dim // self.num_heads) % 2 != 0:
            raise ValueError("head_dim (dim / num_heads) must be even for pairwise rotation")
        if self.positional_mode not in ("toroidal", "rope", "rope_matched"):
            raise ValueError(
                "positional_mode must be 'toroidal', 'rope', or 'rope_matched', "
                f"got {self.positional_mode!r}"
            )


class TransformerBlock:
    def __init__(self, cfg: GeometricToriTransformerConfig, rng: np.random.Generator):
        if cfg.positional_mode == "rope":
            self.attn = RopeMultiHeadAttention(cfg.dim, cfg.num_heads, rng, causal=cfg.causal)
        elif cfg.positional_mode == "rope_matched":
            self.attn = MatchedRopeMultiHeadAttention(cfg.dim, cfg.num_heads, rng, causal=cfg.causal)
        else:
            self.attn = ToroidalMultiHeadAttention(cfg.dim, cfg.num_heads, rng, causal=cfg.causal)
        self.ff = FeedForward(cfg.dim, cfg.ff_hidden_dim, rng)
        self.ln1 = LayerNorm(cfg.dim)
        self.ln2 = LayerNorm(cfg.dim)

    def parameters(self) -> list[Tensor]:
        return self.attn.parameters() + self.ff.parameters() + self.ln1.parameters() + self.ln2.parameters()

    def __call__(self, x: Tensor) -> tuple[Tensor, np.ndarray]:
        attn_out, attn_weights = self.attn(self.ln1(x))
        x = x + attn_out
        x = x + self.ff(self.ln2(x))
        return x, attn_weights


class GeometricToriTransformer:
    """Decoder-style (or encoder-style, if ``causal=False``) tori transformer.

    Positional information is carried entirely by the toroidal rotary
    encoding and toroidal relative bias inside each attention block — there
    is deliberately no separate additive absolute positional embedding, so
    the architecture's only source of position-awareness is the geometric
    torus structure described in ``positional.py``.
    """

    def __init__(self, cfg: GeometricToriTransformerConfig):
        self.cfg = cfg
        rng = np.random.default_rng(cfg.seed)
        self.token_embedding = Embedding(cfg.vocab_size, cfg.dim, rng)
        self.blocks = [TransformerBlock(cfg, rng) for _ in range(cfg.num_layers)]
        self.ln_final = LayerNorm(cfg.dim)
        self.head = Linear(cfg.dim, cfg.vocab_size, rng)

    def parameters(self) -> list[Tensor]:
        params = self.token_embedding.parameters()
        for block in self.blocks:
            params += block.parameters()
        params += self.ln_final.parameters() + self.head.parameters()
        return params

    def __call__(self, token_ids: np.ndarray) -> tuple[Tensor, list[np.ndarray]]:
        """``token_ids``: int array ``(batch, seq_len)``. Returns logits and per-layer attention maps."""
        x = self.token_embedding(token_ids)
        attn_maps: list[np.ndarray] = []
        for block in self.blocks:
            x, attn_weights = block(x)
            attn_maps.append(attn_weights)
        x = self.ln_final(x)
        logits = self.head(x)
        return logits, attn_maps

    def num_parameters(self) -> int:
        return sum(p.data.size for p in self.parameters())
