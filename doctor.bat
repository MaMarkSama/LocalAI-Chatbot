@echo off
chcp 65001 >nul
title Gemma AI — System & Framework Doctor
color 0B

echo.
echo  ======================================================
echo    Gemma AI — System & Framework Diagnostics
echo  ======================================================
echo.

cd /d "%~dp0"

where python >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo  [ X ] Error: Python not found.
    pause
    exit /b 1
)

python system_doctor.py %*

echo.
echo  คำแนะนำ:
echo  - หากต้องการซ่อมแซม/ติดตั้งทุกอย่างที่ขาดหาย ให้รัน: doctor.bat --fix
echo  ======================================================
echo.
pause
