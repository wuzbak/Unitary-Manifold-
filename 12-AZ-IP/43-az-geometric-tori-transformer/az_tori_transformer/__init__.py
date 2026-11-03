# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""AZ Geometric Tori Transformer — Product 43.

A from-scratch (NumPy-only, no PyTorch/JAX dependency), trainable transformer
whose positional structure is built entirely from the repository's exact
integer toroidal phase lattice (Z_74, the (5, 7) braid winding, and the
12/37 tick cadence already canonical to the Navigator's toroidal lane):

* ``toroidal_geometry.py`` — the exact Z_74 lattice primitives (wrap,
  circular distance, braid bank), duplicated from and cross-checked against
  ``12-AZ-IP/20-psicat-navigator``'s golden-vector export.
* ``positional.py`` — toroidal rotary encoding (exact-lattice RoPE) and a
  toroidal relative-position attention bias.
* ``tensor.py`` — a minimal from-scratch reverse-mode autograd engine.
* ``attention.py`` / ``layers.py`` / ``model.py`` — the attention block,
  feed-forward/embedding layers, and the assembled
  ``GeometricToriTransformer`` model.
* ``train_demo.py`` — a toy cyclic ("toroidal") copy task that exercises the
  architecture's namesake wraparound property end to end, with real
  backpropagation and a measured loss trace.

Epistemic status: ADJACENT TRACK. This is a software architecture product
motivated by the repository's existing geometric/extra-dimensional framing;
it is not a hardgate physics claim, and no benchmark claim is made that this
architecture outperforms standard Transformers in general. See the
product README's "Epistemic status" section for the precise boundary.
"""

from .api import API_ENDPOINTS, dispatch_api_request
from .attention import ToroidalMultiHeadAttention
from .model import GeometricToriTransformer, GeometricToriTransformerConfig, TransformerBlock
from .optim import Adam
from .positional import (
    modular_alias_diagnostics,
    relative_distance,
    rotation_orbit_periods,
    rotation_steps_for_dim,
    toroidal_relative_bias_indices,
    toroidal_rotation_table,
)
from .positional_ablation import run_positional_ablation
from .tensor import Tensor
from .toroidal_geometry import (
    BRAID_WINDINGS,
    HALF_TURN,
    K_CS,
    LATTICE_ORDER,
    TICK_PHASE_STEP,
    braid_bank,
    circular_distance,
    orbifold_fold,
    position_bank,
    position_code,
    wrap,
)
from .train_demo import run_toroidal_copy_demo, toroidal_copy_batch
from .text_workflow import generate_text, train_text_file

__all__ = [
    "API_ENDPOINTS",
    "dispatch_api_request",
    "ToroidalMultiHeadAttention",
    "GeometricToriTransformer",
    "GeometricToriTransformerConfig",
    "TransformerBlock",
    "Adam",
    "Tensor",
    "relative_distance",
    "modular_alias_diagnostics",
    "run_positional_ablation",
    "rotation_orbit_periods",
    "rotation_steps_for_dim",
    "toroidal_relative_bias_indices",
    "toroidal_rotation_table",
    "BRAID_WINDINGS",
    "HALF_TURN",
    "K_CS",
    "LATTICE_ORDER",
    "TICK_PHASE_STEP",
    "braid_bank",
    "circular_distance",
    "orbifold_fold",
    "position_bank",
    "position_code",
    "wrap",
    "run_toroidal_copy_demo",
    "train_text_file",
    "generate_text",
    "toroidal_copy_batch",
]

__version__ = "1.2.0"
