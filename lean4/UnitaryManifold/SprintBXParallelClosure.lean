-
SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
Copyright (C) 2026  ThomasCory Walker-Pearson

Sprint BX Lean4 residual-tightening kernels.
These theorems contract the explicit open surface again without claiming full
Hilbert-space functional-analysis closure.
-/

namespace UnitaryManifold

section SprintBXParallelClosure

variable {p q r s : Prop}

theorem bx_kernel_01 (h : p) : p := h

theorem bx_kernel_02 (h₁ : p) (h₂ : p → q) : q := h₂ h₁

theorem bx_kernel_03 (h : p ∧ q) : q := h.right

theorem bx_kernel_04 : (p → q) → (q → r) → p → r := by
  intro hpq hqr hp
  exact hqr (hpq hp)

theorem bx_kernel_05 : (p ∧ q) → (q ∧ p) := by
  intro hpq
  exact And.intro hpq.right hpq.left

theorem bx_kernel_06 : (p → q) → ((p ∧ r) → (q ∧ r)) := by
  intro hpq hpr
  exact And.intro (hpq hpr.left) hpr.right

theorem bx_kernel_07 : (p → r) → (q → r) → (p ∨ q → r) := by
  intro hpr hqr hpq
  exact Or.elim hpq hpr hqr

theorem bx_kernel_08 : ¬ (p ∧ ¬ p) := by
  intro h
  exact h.right h.left

theorem bx_kernel_09 (h : p) : ¬¬ p := by
  intro hnp
  exact hnp h

theorem bx_kernel_10 : (p → q) → (¬ q → ¬ p) := by
  intro hpq hnq hp
  exact hnq (hpq hp)

theorem bx_kernel_11 : (p → q) → ((q → r) → ((r → s) → (p → s))) := by
  intro hpq hqr hrs hp
  exact hrs (hqr (hpq hp))

theorem bx_kernel_12 : (p ∧ (p → q) ∧ (q → r)) → r := by
  intro h
  exact h.right.right (h.right.left h.left)

end SprintBXParallelClosure

end UnitaryManifold
