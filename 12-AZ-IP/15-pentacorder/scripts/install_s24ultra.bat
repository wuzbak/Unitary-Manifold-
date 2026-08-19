@echo off
:: =============================================================================
:: install_s24ultra.bat — GibberNode installer for Samsung Galaxy S24 Ultra
:: =============================================================================
:: Run this on your Windows laptop with the S24 Ultra connected via USB.
:: Requires: adb.exe in PATH (download Android Platform Tools)
::
:: Usage:
::   install_s24ultra.bat                         (auto-downloads latest APK)
::   install_s24ultra.bat path\to\GibberNode.apk  (use a local APK)
::
:: Auto-download URL (requires internet access):
::   https://github.com/wuzbak/diary/releases/download/android-latest/gibbernode-s24ultra.apk
::
:: To UNINSTALL everything cleanly:
::   uninstall_s24ultra.bat
::
:: All ADB commands are non-destructive and fully reversible.
:: Bootloader is untouched. Knox is intact.
:: =============================================================================
setlocal EnableDelayedExpansion

set APK_PATH=%~1
set SCRIPT_DIR=%~dp0
set RELEASE_APK_URL=https://github.com/wuzbak/diary/releases/download/android-latest/gibbernode-s24ultra.apk
set RELEASE_APK_NAME=gibbernode-s24ultra.apk

:: ── Dependency check ──────────────────────────────────────────────────────────
echo.
echo ════ Dependency check ════
where adb >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] adb not found in PATH.
    echo        Download Android Platform Tools:
    echo        https://developer.android.com/tools/releases/platform-tools
    echo        and add the folder to your PATH environment variable.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('adb version 2^>nul') do (echo [INFO] %%i & goto :adb_ok)
:adb_ok

:: ── Step 0 — Detect device ────────────────────────────────────────────────────
echo.
echo ════ Step 0 — Detect S24 Ultra ════
adb kill-server >nul 2>&1
adb start-server >nul 2>&1

for /f "skip=1 tokens=1" %%D in ('adb devices 2^>nul') do (
    set SERIAL=%%D
    goto :device_found
)

echo [FAIL] No device detected.
echo        To enable USB Debugging on the S24 Ultra:
echo          1. Settings ^> About Phone ^> Software Information
echo          2. Tap 'Build Number' exactly 7 times
echo          3. Settings ^> Developer Options ^> USB Debugging: ON
echo          4. Connect via USB-C and tap Allow on the phone
pause
exit /b 1

:device_found
set ADB=adb -s %SERIAL%
echo [ OK ] Device: %SERIAL%

for /f "tokens=*" %%M in ('%ADB% shell getprop ro.product.model 2^>nul') do set MODEL=%%M
for /f "tokens=*" %%V in ('%ADB% shell getprop ro.build.version.release 2^>nul') do set ANDROID_VER=%%V
echo [INFO] Model: %MODEL%   Android: %ANDROID_VER%

:: ── Step 1 — Enable sideloading ───────────────────────────────────────────────
echo.
echo ════ Step 1 — Enable APK sideloading ════

%ADB% shell "settings put global install_non_market_apps 1" >nul 2>&1
%ADB% shell "settings put secure install_non_market_apps 1" >nul 2>&1
echo [ OK ] Sideloading enabled

:: ── Step 2 — Disable Samsung / Google bloatware ───────────────────────────────
echo.
echo ════ Step 2 — Disable Samsung / Google bloatware (reversible) ════

set BLOATWARE=com.samsung.android.bixby.agent com.samsung.android.app.spage com.samsung.android.bixbyvision.framework com.samsung.android.game.gamehome com.microsoft.skydrive com.facebook.appmanager com.facebook.services com.google.android.videos com.google.android.apps.tachyon

for %%P in (%BLOATWARE%) do (
    %ADB% shell "pm disable-user --user 0 %%P" >nul 2>&1
    echo [INFO] Disabled (if present): %%P
)
echo [ OK ] Bloatware disabled (reversible — run uninstall_s24ultra.bat to restore)

:: ── Step 3 — Battery optimisation ────────────────────────────────────────────
echo.
echo ════ Step 3 — Battery optimisation exemption ════

%ADB% shell "dumpsys deviceidle whitelist +com.termux" >nul 2>&1
%ADB% shell "settings put global background_process_limit 4" >nul 2>&1
%ADB% shell "settings put global app_standby_enabled 0" >nul 2>&1
echo [ OK ] Termux exempted from battery optimisation

:: ── Step 4 — Install Termux ───────────────────────────────────────────────────
echo.
echo ════ Step 4 — Install Termux ════

%ADB% shell "pm list packages" 2>nul | find "com.termux" >nul
if %ERRORLEVEL% equ 0 (
    echo [ OK ] Termux already installed
) else (
    echo [WARN] Termux not installed.
    echo        Download from F-Droid (NOT Google Play — Play Store build lacks full permissions):
    echo          https://f-droid.org/packages/com.termux/
    echo          https://f-droid.org/packages/com.termux.boot/
    echo          https://f-droid.org/packages/com.termux.api/
    echo        Then install with: adb install -r com.termux_xxxxxx.apk
)

:: ── Step 5 — Bootstrap Termux (push and run setup_android.sh) ────────────────
echo.
echo ════ Step 5 — Bootstrap Termux via setup_android.sh ════

if exist "%SCRIPT_DIR%setup_android.sh" (
    %ADB% push "%SCRIPT_DIR%setup_android.sh" /sdcard/setup_android.sh >nul
    echo [ OK ] setup_android.sh pushed to /sdcard/
    %ADB% shell "am start -n com.termux/.HomeActivity" >nul 2>&1
    timeout /t 3 /nobreak >nul
    %ADB% shell "input text 'bash /sdcard/setup_android.sh'" >nul 2>&1
    %ADB% shell "input keyevent 66" >nul 2>&1
    echo [INFO] Bootstrap command sent to Termux — watch the phone screen.
    echo [INFO] This takes 2-5 minutes. The phone will show progress.
) else (
    echo [WARN] setup_android.sh not found in %SCRIPT_DIR%
    echo [INFO] Open Termux on the phone and run manually:
    echo.
    echo          pkg update ^&^& pkg upgrade -y
    echo          pkg install -y python python-pip portaudio libzmq git
    echo          pip install ggwave numpy pyaudio requests
    echo          git clone https://github.com/wuzbak/diary.git ~/diary
)

echo.
echo [INFO] IMPORTANT: After bootstrap, open Termux on the phone and run:
echo          python ~/diary/Gibberlink/scripts/noise_calibrate.py --sweep --play
echo        The S24 Ultra has Dolby Atmos processing that may affect ggwave FSK.
echo        Calibration identifies the safe_ceiling_hz before first use.

:: ── Step 6 — Install GibberNode APK ──────────────────────────────────────────
echo.
echo ════ Step 6 — Install GibberNode.apk ════

:: Auto-download from GitHub release if no APK was supplied
if "%APK_PATH%"=="" (
    echo [INFO] No APK path given — attempting auto-download from GitHub...
    echo [INFO] %RELEASE_APK_URL%
    set DOWNLOAD_PATH=%TEMP%\%RELEASE_APK_NAME%

    :: Try curl.exe first (built into Windows 10 1803+)
    where curl.exe >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        curl.exe -fsSL -o "!DOWNLOAD_PATH!" "%RELEASE_APK_URL%"
        if %ERRORLEVEL% equ 0 (
            echo [ OK ] Downloaded %RELEASE_APK_NAME%
            set APK_PATH=!DOWNLOAD_PATH!
        ) else (
            echo [WARN] curl download failed
        )
    ) else (
        :: Fallback: PowerShell Invoke-WebRequest
        echo [INFO] curl not available — trying PowerShell...
        powershell -NoProfile -Command ^
          "try { Invoke-WebRequest -Uri '%RELEASE_APK_URL%' -OutFile '!DOWNLOAD_PATH!' -UseBasicParsing; exit 0 } catch { exit 1 }"
        if %ERRORLEVEL% equ 0 (
            echo [ OK ] Downloaded %RELEASE_APK_NAME% via PowerShell
            set APK_PATH=!DOWNLOAD_PATH!
        ) else (
            echo [WARN] PowerShell download also failed
        )
    )

    if "!APK_PATH!"=="" (
        echo [WARN] Auto-download failed. Possible reasons:
        echo        - No internet access
        echo        - No release published yet (CI has not run or build failed^)
        echo        Build the APK manually and re-run:
        echo          cd Android ^&^& gradlew assembleDebug
        echo          install_s24ultra.bat Android\app\build\outputs\apk\debug\app-debug.apk
    )
)

if not "!APK_PATH!"=="" (
    if exist "!APK_PATH!" (
        %ADB% install -r "!APK_PATH!"
        if %ERRORLEVEL% equ 0 (
            echo [ OK ] Unitary Pentacorder installed
            %ADB% shell "pm grant com.axiomzero.pentacorder android.permission.RECORD_AUDIO" >nul 2>&1
            %ADB% shell "pm grant com.axiomzero.pentacorder android.permission.ACCESS_FINE_LOCATION" >nul 2>&1
            %ADB% shell "pm grant com.axiomzero.pentacorder android.permission.ACCESS_COARSE_LOCATION" >nul 2>&1
            echo [ OK ] Runtime permissions granted
        ) else (
            echo [WARN] APK install failed
        )
    ) else (
        echo [WARN] APK file not found: !APK_PATH!
    )
) else (
    echo [WARN] APK not available — skipping GibberNode installation.
)

:: ── Step 7 — Configure Termux:Boot auto-start ─────────────────────────────────
echo.
echo ════ Step 7 — Configure Termux:Boot auto-start ════

:: Prefer the S24 Ultra-specific boot script
set BOOT_SCRIPT=%SCRIPT_DIR%termux_boot_s24ultra.sh
if not exist "%BOOT_SCRIPT%" set BOOT_SCRIPT=%SCRIPT_DIR%termux_boot.sh

if exist "%BOOT_SCRIPT%" (
    %ADB% push "%BOOT_SCRIPT%" /sdcard/start-gibberlink.sh
    %ADB% shell "mkdir -p ~/.termux/boot && cp /sdcard/start-gibberlink.sh ~/.termux/boot/ && chmod +x ~/.termux/boot/start-gibberlink.sh"
    echo [ OK ] Boot script installed
) else (
    echo [WARN] No boot script found in %SCRIPT_DIR%
)

:: ── Step 8 — Push content to internal storage ────────────────────────────────
echo.
echo ════ Step 8 — Push content to internal storage (/sdcard) ════

set REPO_ROOT=%SCRIPT_DIR%..\

if exist "%REPO_ROOT%Unitary-Manifold\" (
    %ADB% shell "mkdir -p /sdcard/manifold"
    %ADB% push "%REPO_ROOT%Unitary-Manifold\" /sdcard/manifold\ >nul 2>&1
    echo [ OK ] Unitary-Manifold pushed to /sdcard/manifold/
)

if exist "%REPO_ROOT%Gibberlink\" (
    %ADB% shell "mkdir -p /sdcard/gibberlink"
    %ADB% push "%REPO_ROOT%Gibberlink\" /sdcard/gibberlink\ >nul 2>&1
    echo [ OK ] Gibberlink pushed to /sdcard/gibberlink/
)

:: ── Step 9 — Verify ──────────────────────────────────────────────────────────
echo.
echo ════ Step 9 — Verify ════

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
echo   Installation complete — Samsung Galaxy S24 Ultra
echo.
echo   Next steps:
echo     1. Open Termux and run: source ~/diary/Gibberlink/.env
echo     2. Run calibration:
echo          python ~/diary/Gibberlink/scripts/noise_calibrate.py --sweep --play
echo     3. Open GibberNode and complete the Calibration Wizard
echo     4. Reboot the phone to verify Termux:Boot auto-start
echo.
echo   To undo everything cleanly:
echo     uninstall_s24ultra.bat
echo.
echo   Re-enable a disabled package:
echo     adb shell pm enable --user 0 ^<package.name^>
echo ════════════════════════════════════════════════════
echo.
pause
endlocal
