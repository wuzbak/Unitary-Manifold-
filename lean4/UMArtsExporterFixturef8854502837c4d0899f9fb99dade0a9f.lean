import Lean
namespace ExportFixture
axiom assumed : True
theorem clean : True := True.intro
theorem conditional : True := assumed
theorem indirect : True := conditional
theorem unfinished : True := by sorry
theorem indirectSorry : True := unfinished
def value : Nat := 7
opaque hidden : Nat := 3
end ExportFixture
