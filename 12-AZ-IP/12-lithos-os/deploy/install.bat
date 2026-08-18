@echo off
setlocal
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%..\.."
python "%SCRIPT_DIR%install.py" %*
endlocal
