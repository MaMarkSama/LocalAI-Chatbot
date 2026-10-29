@echo off
setlocal
cd /d "%~dp0"
python create_safe_source_zip.py
pause
