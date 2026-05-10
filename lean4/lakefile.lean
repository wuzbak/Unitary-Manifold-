import Lake
open Lake DSL

package «unitary-manifold» where
  version := v!"0.1.0"
  keywords := #["physics", "kaluza-klein", "unitary-manifold"]

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "v4.22.0-rc2"

lean_lib UnitaryManifold where
  roots := #[`UnitaryManifold]
