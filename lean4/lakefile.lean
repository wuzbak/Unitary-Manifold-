import Lake
open Lake DSL

package «unitary-manifold» where
  version := v!"0.1.0"
  keywords := #["physics", "kaluza-klein", "unitary-manifold"]

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "v4.22.0-rc2"

@[default_target]
lean_lib UnitaryManifold where
  roots := #[`UnitaryManifold]
  globs := #[.one `UnitaryManifold, .submodules `UnitaryManifold]

lean_exe um_arts_export where
  root := `UMArtsExport
