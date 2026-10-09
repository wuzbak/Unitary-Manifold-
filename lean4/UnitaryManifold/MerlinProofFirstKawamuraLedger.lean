-- SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
-- Copyright (C) 2026  ThomasCory Walker-Pearson
/-!
# Kawamura ledger — conditional proof accounting only

The historical unconditional `mpf_kawamura_kernel_1`–`8` declarations are
withdrawn: declaring an arbitrary `Prop` does not provide a proof of it.
Their four proposition axioms are removed. These explicitly renamed
conditional lemmas require evidence supplied by the caller; they neither
establish ledger policy nor close the Kawamura independence residual.
-/

namespace UnitaryManifold.MerlinProofFirstKawamuraLedger

/-- Taking the arbitrary proposition to be False refutes any blanket
    unconditional proof rule. The Kawamura residual remains open. -/
theorem mpf_kawamura_unconditional_prop_counterexample :
    ¬ (∀ claim : Prop, claim) := by
  intro h
  exact h False

variable (ResidualOpen TraceabilityNotClosure DualLoopAgreement ExternalBoundary : Prop)

theorem mpf_kawamura_kernel_1_given (h : ResidualOpen) : ResidualOpen := h
theorem mpf_kawamura_kernel_2_given (h : TraceabilityNotClosure) : TraceabilityNotClosure := h
theorem mpf_kawamura_kernel_3_given (h : DualLoopAgreement) : DualLoopAgreement := h
theorem mpf_kawamura_kernel_4_given (h : ExternalBoundary) : ExternalBoundary := h

theorem mpf_kawamura_kernel_5_given
    (hr : ResidualOpen) (ht : TraceabilityNotClosure) :
    ResidualOpen ∧ TraceabilityNotClosure := ⟨hr, ht⟩

theorem mpf_kawamura_kernel_6_given
    (hd : DualLoopAgreement) (he : ExternalBoundary) :
    DualLoopAgreement ∧ ExternalBoundary := ⟨hd, he⟩

theorem mpf_kawamura_kernel_7_given
    (hr : ResidualOpen) (hd : DualLoopAgreement) :
    ResidualOpen ∧ DualLoopAgreement := ⟨hr, hd⟩

theorem mpf_kawamura_kernel_8_given
    (ht : TraceabilityNotClosure) (he : ExternalBoundary) :
    TraceabilityNotClosure ∧ ExternalBoundary := ⟨ht, he⟩

end UnitaryManifold.MerlinProofFirstKawamuraLedger
