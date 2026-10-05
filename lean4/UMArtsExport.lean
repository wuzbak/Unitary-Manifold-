/- Copyright (C) 2026 ThomasCory Walker-Pearson
SPDX-License-Identifier: CC0-1.0 -/
import Lean
import Lean.Util.CollectAxioms

/-!
Checked-environment JSON v1 export, using only Lean's own libraries.

Usage: lake exe um_arts_export --module Module.Name --decl Namespace.theoremName
Repeat both options to request multiple imports and exact declaration names.
Modules must already have compiled oleans on LEAN_PATH; this exporter does not
build them. `checked` means a theorem in the imported kernel environment without
sorryAx, NOT an axiom-free proof or independent verification of imported oleans.
`axioms` are transitive; `dependencies` are direct type/value constant references.

API reference: leanprover/lean4 v4.22.0-rc2, src/Lean/Environment.lean,
src/Lean/Util/CollectAxioms.lean, src/Lean/Util/FoldConsts.lean,
src/Lean/Meta/Basic.lean, and src/Lean/PrettyPrinter.lean.
-/

open Lean

namespace UMArtsExport

structure Request where
  modules : Array String := #[]
  declarations : Array String := #[]

def usage : String :=
  "usage: um_arts_export --module Module.Name [--module ...] --decl Exact.Name [--decl ...]"

def validName (value : String) : Bool :=
  !value.isEmpty && (value.splitOn ".").all (fun part => !part.isEmpty) &&
    !value.toList.any Char.isWhitespace

def addName (values : Array String) (value : String) : Except String (Array String) :=
  if !validName value then
    .error s!"invalid module/declaration name: {value}"
  else if values.contains value then
    .ok values
  else
    .ok (values.push value)

def parseArgs : List String → Request → Except String Request
  | [], request =>
    if request.modules.isEmpty || request.declarations.isEmpty then
      .error usage
    else
      .ok request
  | "--module" :: value :: rest, request => do
    let modules ← addName request.modules value
    parseArgs rest { request with modules := modules }
  | "--decl" :: value :: rest, request => do
    let declarations ← addName request.declarations value
    parseArgs rest { request with declarations := declarations }
  | arg :: _, _ => .error s!"unknown or incomplete argument: {arg}\n{usage}"

def sortedStrings (values : Array String) : Array String :=
  values.qsort (fun a b => a < b)

def namesJson (names : Array Name) : Json :=
  .arr ((sortedStrings (names.map Name.toString)).map Json.str)

def kind : ConstantInfo → String
  | .axiomInfo _ => "axiom"
  | .thmInfo _ => "theorem"
  | .defnInfo _ => "definition"
  | .opaqueInfo _ => "opaque"
  | .inductInfo _ => "inductive"
  | .ctorInfo _ => "constructor"
  | .recInfo _ => "recursor"
  | .quotInfo _ => "quotient"

def declarationJson (requested : String) : MetaM Json := do
  let env ← getEnv
  let name := requested.toName
  -- The checked kernel map excludes elaborator-only/failed async declarations.
  let some info := env.checked.get.find? name
    | throwError "declaration not found in checked environment: {requested}"
  let axioms ← collectAxioms info.name
  let dependencies := Id.run do
    let mut names : Array Name := #[]
    for dependency in info.getUsedConstantsAsSet do
      if dependency != info.name then
        names := names.push dependency
    return names
  let hasSorry := axioms.contains ``sorryAx
  let isTheorem := match info with
    | .thmInfo _ => true
    | _ => false
  let checked := isTheorem && !hasSorry
  let statement := (← PrettyPrinter.ppExpr info.type).pretty 120
  return Json.mkObj [
    ("name", .str info.name.toString),
    ("statement", .str statement),
    ("kind", .str (kind info)),
    ("axioms", namesJson axioms),
    ("dependencies", namesJson dependencies),
    ("checked", .bool checked),
    ("proof_status", .str (if hasSorry then "depends_on_sorry"
      else if isTheorem then "checked" else "not_a_theorem"))
  ]

unsafe def exportRequest (request : Request) : IO Json := do
  if Lean.versionString != "4.22.0-rc2" then
    throw <| IO.userError s!"expected Lean 4.22.0-rc2, got {Lean.versionString}"
  initSearchPath (← findSysroot)
  enableInitializersExecution
  let modules := sortedStrings request.modules
  let imports : Array Import := modules.map (fun moduleName => { module := moduleName.toName })
  let options := ({} : Options).setBool `pp.fullNames true
  let env ← Lean.importModules imports options (trustLevel := 0) (loadExts := true)
  let action : MetaM (Array Json) :=
    (sortedStrings request.declarations).mapM declarationJson
  let (declarations, _, _) ← action.toIO
    { fileName := "<um_arts_export>", fileMap := default, options := options }
    { env := env }
  return Json.mkObj [
    ("schema_version", toJson (1 : Nat)),
    ("lean_version", .str Lean.versionString),
    ("modules", .arr (modules.map Json.str)),
    ("declarations", .arr declarations)
  ]

end UMArtsExport

unsafe def main (args : List String) : IO UInt32 := do
  try
    let request ← match UMArtsExport.parseArgs args {} with
      | .ok request => pure request
      | .error message => throw <| IO.userError message
    let document ← UMArtsExport.exportRequest request
    (← IO.getStdout).putStrLn document.compress
    return 0
  catch error =>
    (← IO.getStderr).putStrLn s!"um_arts_export: {error}"
    return 1
