; SPDX-License-Identifier: AGPL-3.0-or-later
; Copyright (C) 2026 ThomasCory Walker-Pearson
!include "${PROJECT_DIR}\build\offline-payload\payload-config.nsh"

!macro customInit
  InitPluginsDir
  File /oname=$PLUGINSDIR\p45-offline-payload.ps1 "${PROJECT_DIR}\scripts\install-offline-payload.ps1"
  File /oname=$PLUGINSDIR\p45-runtime-manifest.json "${PROJECT_DIR}\build\offline-payload\runtime-manifest.json"
  ; Validate before electron-builder removes an existing installation. No web fallback.
  nsExec::ExecToLog '"$SYSDIR\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "$PLUGINSDIR\p45-offline-payload.ps1" -PayloadDirectory "$EXEDIR" -ManifestName "${P45_PAYLOAD_MANIFEST}" -ManifestSha256 "${P45_PAYLOAD_SHA256}" -RuntimeManifest "$PLUGINSDIR\p45-runtime-manifest.json" -ValidateOnly'
  Pop $0
  ${If} $0 != 0
    MessageBox MB_OK|MB_ICONSTOP "The complete offline installer kit is required, not just this EXE. Extract the entire axiomzero-pc-suite-windows artifact ZIP into one folder, or download every release model part and offline manifest beside this installer without renaming them. A missing or invalid part cannot be repaired by setup. No model will be downloaded." /SD IDOK
    SetErrorLevel 1
    Quit
  ${EndIf}
!macroend

!macro customInstall
  nsExec::ExecToLog '"$SYSDIR\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "$PLUGINSDIR\p45-offline-payload.ps1" -PayloadDirectory "$EXEDIR" -ManifestName "${P45_PAYLOAD_MANIFEST}" -ManifestSha256 "${P45_PAYLOAD_SHA256}" -RuntimeManifest "$INSTDIR\resources\psicat-instruction\manifest.json" -DestinationDirectory "$INSTDIR\resources\psicat-instruction"'
  Pop $0
  ${If} $0 != 0
    MessageBox MB_OK|MB_ICONSTOP "Offline model installation failed verification. Installation is NOT qualified; do not launch it. Correct the companion payload and run the installer again." /SD IDOK
    SetErrorLevel 1
    Quit
  ${EndIf}
!macroend
