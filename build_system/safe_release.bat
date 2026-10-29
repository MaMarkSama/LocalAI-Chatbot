@echo off
setlocal
cd /d "%~dp0\.."
python build_system\safe_release.py %*
endlocal
