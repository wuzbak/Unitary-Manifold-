@echo off
:: =============================================================================
:: install_bv9900.bat — GibberNode installer for Blackview BV9900 Pro (Windows)
:: =============================================================================
:: Run this on your Windows laptop with the BV9900 Pro connected via USB.
:: Requires: adb.exe in PATH (download Android Platform Tools)
::
:: Usage:
::   install_bv9900.bat [path\to\GibberNode.apk]
::
:: =============================================================================
setlocal EnableDelayedExpansion

set APK_PATH=%~1
set SCRIPT_DIR=%~dp0

:: ── Dependency check ──────────────────────────────────────────────────────────
echo.
echo ════ Dependency check ════
where adb >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] adb not found in PATH.
    echo        Download Android Platform Tools from:
    echo        https://developer.android.com/tools/releases/platform-tools
    echo        and add the folder to your PATH environment variable.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('adb version 2^>nul') do (echo [INFO] %%i & goto :adb_ok)
:adb_ok

:: ── Step 0 — Detect device ────────────────────────────────────────────────────
echo.
echo ════ Step 0 — Detect BV9900 Pro ════
adb kill-server >nul 2>&1
adb start-server >nul 2>&1

for /f "skip=1 tokens=1" %%D in ('adb devices 2^>nul') do (
    set SERIAL=%%D
    goto :device_found
)

echo [FAIL] No device detected.
echo        1. Connect the BV9900 Pro via USB
echo        2. Settings ^> About Phone ^> Software Information
echo        3. Tap 'Build Number' exactly 7 times
echo        4. Settings ^> Developer Options ^> USB Debugging: ON
echo        5. Accept the ADB prompt on the phone
pause
exit /b 1

:device_found
set ADB=adb -s %SERIAL%
echo [ OK ] Device: %SERIAL%

for /f "tokens=*" %%M in ('%ADB% shell getprop ro.product.model 2^>nul') do set MODEL=%%M
for /f "tokens=*" %%V in ('%ADB% shell getprop ro.build.version.release 2^>nul') do set ANDROID_VER=%%V
echo [INFO] Model: %MODEL%   Android: %ANDROID_VER%

:: ── Step 1 — Disable Kids Mode ────────────────────────────────────────────────
echo.
echo ════ Step 1 — Disable Blackview Kids Mode / restricted profile ════

%ADB% shell "am force-stop com.blackview.kidzone" >nul 2>&1
%ADB% shell "settings put secure restricted_profile_id 0" >nul 2>&1
%ADB% shell "pm disable-user --user 0 com.blackview.kidzone" >nul 2>&1
%ADB% shell "pm disable-user --user 0 com.google.android.apps.kids.familylinkhelper" >nul 2>&1
echo [ OK ] Kids Mode cleared

:: ── Step 2 — Enable sideloading ───────────────────────────────────────────────
echo.
echo ════ Step 2 — Enable APK sideloading ════

%ADB% shell "settings put global install_non_market_apps 1"
%ADB% shell "settings put secure install_non_market_apps 1"
echo [ OK ] Sideloading enabled

:: ── Step 3 — Disable OEM bloatware ────────────────────────────────────────────
echo.
echo ════ Step 3 — Disable OEM bloatware ════

set BLOATWARE=com.mediatek.mdmconfig com.mediatek.mdmloge com.mediatek.wfo.legacy com.mediatek.engineermode com.mediatek.ygps com.mediatek.mtklogger com.facebook.appmanager com.facebook.services com.google.android.videos com.google.android.apps.tachyon

for %%P in (%BLOATWARE%) do (
    %ADB% shell "pm disable-user --user 0 %%P" >nul 2>&1
    echo [INFO] Disabled (if present): %%P
)
echo [ OK ] Bloatware disabled

:: ── Step 4 — Battery optimisation ────────────────────────────────────────────
echo.
echo ════ Step 4 — Battery optimisation exemption ════

%ADB% shell "dumpsys deviceidle whitelist +com.termux" >nul 2>&1
%ADB% shell "settings put global background_process_limit 4" >nul 2>&1
%ADB% shell "settings put global app_standby_enabled 0" >nul 2>&1
echo [ OK ] Termux exempted from battery optimisation

:: ── Step 5 — Install Termux ───────────────────────────────────────────────────
echo.
echo ════ Step 5 — Install Termux ════

%ADB% shell "pm list packages" 2>nul | find "com.termux" >nul
if %ERRORLEVEL% equ 0 (
    echo [ OK ] Termux already installed
) else (
    echo [WARN] Termux not installed. Download manually from F-Droid:
    echo        https://f-droid.org/packages/com.termux/
    echo        Then install with: adb install -r com.termux.apk
    echo.
    echo        Also install Termux:Boot and Termux:API from F-Droid.
)

:: ── Step 6 — Bootstrap Termux (guidance only on Windows) ─────────────────────
echo.
echo ════ Step 6 — Termux bootstrap (run manually in Termux) ════
echo [INFO] Open Termux on the phone and run:
echo.
echo          pkg update ^&^& pkg upgrade -y
echo          pkg install -y python python-pip portaudio libzmq git
echo          pip install ggwave numpy pyaudio requests
echo          git clone https://github.com/wuzbak/diary.git ~/diary
echo.
echo        (These commands run on the phone, not on Windows)

:: ── Step 7 — Install GibberNode APK ──────────────────────────────────────────
echo.
echo ════ Step 7 — Install GibberNode.apk ════

if not "%APK_PATH%"=="" (
    if exist "%APK_PATH%" (
        %ADB% install -r "%APK_PATH%"
        if %ERRORLEVEL% equ 0 (
            echo [ OK ] GibberNode installed
            %ADB% shell "pm grant com.axiomzero.pentacorder android.permission.RECORD_AUDIO" >nul 2>&1
            %ADB% shell "pm grant com.axiomzero.pentacorder android.permission.ACCESS_FINE_LOCATION" >nul 2>&1
            echo [ OK ] Runtime permissions granted
        ) else (
            echo [WARN] APK install failed
        )
    ) else (
        echo [WARN] APK file not found: %APK_PATH%
    )
) else (
    echo [WARN] No APK path given. Usage: install_bv9900.bat path\to\GibberNode.apk
)

:: ── Step 8 — Configure Termux:Boot ───────────────────────────────────────────
echo.
echo ════ Step 8 — Configure Termux:Boot auto-start ════

if exist "%SCRIPT_DIR%termux_boot.sh" (
    %ADB% push "%SCRIPT_DIR%termux_boot.sh" /sdcard/start-gibberlink.sh
    %ADB% shell "mkdir -p ~/.termux/boot && cp /sdcard/start-gibberlink.sh ~/.termux/boot/ && chmod +x ~/.termux/boot/start-gibberlink.sh"
    echo [ OK ] Boot script installed
) else (
    echo [WARN] termux_boot.sh not found in %SCRIPT_DIR%
)

:: ── Step 9 — Push SD card content ────────────────────────────────────────────
echo.
echo ════ Step 9 — Push content to SD card ════

set REPO_ROOT=%SCRIPT_DIR%..\..\

if exist "%REPO_ROOT%Unitary-Manifold\" (
    %ADB% shell "mkdir -p /sdcard/manifold"
    %ADB% push "%REPO_ROOT%Unitary-Manifold\" /sdcard/manifold\ >nul 2>&1
    echo [ OK ] Unitary-Manifold pushed
)

if exist "%REPO_ROOT%Gibberlink\" (
    %ADB% shell "mkdir -p /sdcard/gibberlink"
    %ADB% push "%REPO_ROOT%Gibberlink\" /sdcard/gibberlink\ >nul 2>&1
    echo [ OK ] Gibberlink pushed
)

:: ── Step 10 — Verify ─────────────────────────────────────────────────────────
echo.
echo ════ Step 10 — Verify ════

%ADB% shell "pm list packages" 2>nul | find "com.termux" >nul
if %ERRORLEVEL% equ 0 (echo [ OK ] Termux: installed) else (echo [WARN] Termux: NOT found)

%ADB% shell "pm list packages" 2>nul | find "com.axiomzero.pentacorder" >nul
if %ERRORLEVEL% equ 0 (
    echo [ OK ] GibberNode: installed
    %ADB% shell "am start -n com.axiomzero.pentacorder/.MainActivity" >nul 2>&1
    echo [INFO] GibberNode launched on device
) else (
    echo [WARN] GibberNode: NOT installed
)

echo.
echo ════════════════════════════════════════════════════
echo   Installation complete.
echo   Next steps:
echo     1. Open Termux and run the bootstrap command above
echo     2. Open GibberNode and complete the Calibration Wizard
echo     3. Reboot the phone to verify Termux:Boot auto-start
echo   Revert: adb shell pm enable ^<package.name^>
echo ════════════════════════════════════════════════════
echo.
pause
endlocal
