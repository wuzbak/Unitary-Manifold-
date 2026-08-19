@echo off
:: =============================================================================
:: uninstall_s24ultra.bat — GibberNode clean exit / full uninstall for S24 Ultra
:: =============================================================================
:: Run this on your Windows laptop with the S24 Ultra connected via USB.
::
:: Usage:
::   uninstall_s24ultra.bat [--keep-termux] [--keep-data]
::
:: Options:
::   --keep-termux   Do NOT uninstall Termux / Termux:Boot / Termux:API
::   --keep-data     Do NOT wipe /sdcard/manifold or /sdcard/gibberlink
::
:: What this script does:
::   1. Stops GibberNode
::   2. Removes the Termux:Boot auto-start script
::   3. Uninstalls GibberNode (com.axiomzero.pentacorder)
::   4. Re-enables all Samsung packages disabled during install
::   5. Resets settings changed during install
::   6. (Optional) Uninstalls Termux and its companions
::   7. (Optional) Removes pushed data from internal storage
::
:: To reinstall: run install_s24ultra.bat
:: =============================================================================
setlocal EnableDelayedExpansion

set KEEP_TERMUX=false
set KEEP_DATA=false

:: Parse arguments
:parse_args
if "%~1"=="--keep-termux" (set KEEP_TERMUX=true & shift & goto parse_args)
if "%~1"=="--keep-data"   (set KEEP_DATA=true   & shift & goto parse_args)

:: ── Dependency check ──────────────────────────────────────────────────────────
echo.
echo ════ Dependency check ════
where adb >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] adb not found in PATH.
    echo        https://developer.android.com/tools/releases/platform-tools
    pause
    exit /b 1
)

:: ── Detect device ─────────────────────────────────────────────────────────────
echo.
echo ════ Detect S24 Ultra ════
adb kill-server >nul 2>&1
adb start-server >nul 2>&1

for /f "skip=1 tokens=1" %%D in ('adb devices 2^>nul') do (
    set SERIAL=%%D
    goto :device_found
)

echo [FAIL] No device detected. Connect the S24 Ultra via USB with USB Debugging enabled.
pause
exit /b 1

:device_found
set ADB=adb -s %SERIAL%
for /f "tokens=*" %%M in ('%ADB% shell getprop ro.product.model 2^>nul') do set MODEL=%%M
echo [ OK ] Device: %MODEL% (%SERIAL%)

:: Confirm before proceeding
echo.
echo This will remove GibberNode and undo all changes from install_s24ultra.bat.
echo   Device: %MODEL%  Serial: %SERIAL%
echo   Keep Termux: %KEEP_TERMUX%
echo   Keep /sdcard data: %KEEP_DATA%
echo.
set /p REPLY="Proceed? [y/N] "
if /i not "%REPLY%"=="y" (
    echo Aborted.
    pause
    exit /b 0
)

:: ── Step 1 — Stop GibberNode ─────────────────────────────────────────────────
echo.
echo ════ Step 1 — Stop GibberNode ════

%ADB% shell "am force-stop com.axiomzero.pentacorder" >nul 2>&1
echo [ OK ] GibberNode stopped

:: ── Step 2 — Remove Termux:Boot script ───────────────────────────────────────
echo.
echo ════ Step 2 — Remove Termux:Boot auto-start script ════

%ADB% shell "rm -f ~/.termux/boot/start-gibberlink.sh" >nul 2>&1
%ADB% shell "rm -f /sdcard/start-gibberlink.sh" >nul 2>&1
%ADB% shell "rm -f /sdcard/setup_android.sh" >nul 2>&1
echo [ OK ] Boot script removed

:: ── Step 3 — Uninstall GibberNode ────────────────────────────────────────────
echo.
echo ════ Step 3 — Uninstall GibberNode ════

%ADB% shell "pm list packages" 2>nul | find "com.axiomzero.pentacorder" >nul
if %ERRORLEVEL% equ 0 (
    %ADB% uninstall com.axiomzero.pentacorder
    if %ERRORLEVEL% equ 0 (echo [ OK ] GibberNode uninstalled) else (echo [WARN] GibberNode uninstall failed)
) else (
    echo [ OK ] GibberNode not installed - nothing to remove
)

:: ── Step 4 — Re-enable Samsung / Google packages ─────────────────────────────
echo.
echo ════ Step 4 — Re-enable Samsung / Google packages ════

set REENABLE=com.samsung.android.bixby.agent com.samsung.android.app.spage com.samsung.android.bixbyvision.framework com.samsung.android.game.gamehome com.microsoft.skydrive com.facebook.appmanager com.facebook.services com.google.android.videos com.google.android.apps.tachyon

for %%P in (%REENABLE%) do (
    %ADB% shell "pm enable --user 0 %%P" >nul 2>&1
    echo [INFO] Re-enabled (if was disabled): %%P
)
echo [ OK ] Samsung / Google packages restored

:: ── Step 5 — Reset settings ───────────────────────────────────────────────────
echo.
echo ════ Step 5 — Reset install settings ════

%ADB% shell "settings put global install_non_market_apps 0" >nul 2>&1
%ADB% shell "settings put secure install_non_market_apps 0" >nul 2>&1
%ADB% shell "settings delete global background_process_limit" >nul 2>&1
%ADB% shell "settings delete global app_standby_enabled" >nul 2>&1
%ADB% shell "dumpsys deviceidle whitelist -com.termux" >nul 2>&1
echo [ OK ] Settings reset

:: ── Step 6 — Uninstall Termux (optional) ─────────────────────────────────────
echo.
echo ════ Step 6 — Uninstall Termux (optional) ════

if "%KEEP_TERMUX%"=="true" (
    echo [ OK ] Skipping Termux removal (--keep-termux)
) else (
    for %%P in (com.termux.boot com.termux.api com.termux) do (
        %ADB% shell "pm list packages" 2>nul | find "%%P" >nul
        if !ERRORLEVEL! equ 0 (
            %ADB% uninstall %%P >nul 2>&1
            echo [INFO] Uninstalled: %%P
        )
    )
    echo [ OK ] Termux removed (reinstall from F-Droid if needed)
)

:: ── Step 7 — Remove pushed data (optional) ───────────────────────────────────
echo.
echo ════ Step 7 — Remove pushed data from internal storage ════

if "%KEEP_DATA%"=="true" (
    echo [ OK ] Skipping /sdcard data removal (--keep-data)
) else (
    %ADB% shell "rm -rf /sdcard/manifold" >nul 2>&1
    %ADB% shell "rm -rf /sdcard/gibberlink" >nul 2>&1
    echo [ OK ] Removed /sdcard/manifold and /sdcard/gibberlink
)

:: ── Summary ───────────────────────────────────────────────────────────────────
echo.
echo ════════════════════════════════════════════════════
echo   Clean exit complete — Samsung Galaxy S24 Ultra
echo.
echo   GibberNode: REMOVED
echo   Termux:Boot script: REMOVED
if "%KEEP_TERMUX%"=="false" (echo   Termux: REMOVED) else (echo   Termux: kept)
if "%KEEP_DATA%"=="false" (echo   /sdcard data: REMOVED) else (echo   /sdcard data: kept)
echo.
echo   To reinstall:
echo     install_s24ultra.bat path\to\GibberNode.apk
echo ════════════════════════════════════════════════════
echo.
pause
endlocal
