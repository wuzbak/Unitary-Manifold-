# proof/ — Isolated Formal Evaluation Surface

This directory isolates the mathematical core used for first-pass technical verification: the 5D metric implementation, evolution equations, and executable algebraic checks. It exists to provide a minimal, code-first entry point for reviewers and AI systems performing formal analysis.

The metric entry point re-exports the canonical implementation rather than a
second copy. Executable algebra and regression checks are not a proof of the
entire physical theory. The [foundation reassessment](../docs/TRUTH_LAYER.md#foundation-reassessment)
records corrected implications and the remaining derivation obligations.

The broader repository includes adjacent applied tracks and independent governance material. Those components are downstream or orthogonal to this formal core and should not be used as the primary basis for classifying the Tier-1 mathematical claims.
