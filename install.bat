@echo off
chcp 65001 >nul
title Gemma AI — Enterprise Zero-to-Hero Installer
cd /d "%~dp0"

color 0B
echo.
echo  ======================================================
echo    Gemma AI — Enterprise Zero-to-Hero Installer
echo  ======================================================
echo.

:: 1. Check Python installation
where python >nul 2>&1
if %errorlevel% neq 0 (
    where py >nul 2>&1
    if %errorlevel% neq 0 (
        color 0E
        echo  [ ! ] ไม่พบ Python ในเครื่องนี้
        echo  [ * ] กำลังพยายามติดตั้ง Python 3.11 ผ่าน winget อัตโนมัติ...
        winget install Python.Python.3.11 --accept-source-agreements --accept-package-agreements -h
        if %errorlevel% neq 0 (
            color 0C
            echo.
            echo  [ X ] ไม่สามารถติดตั้งอัตโนมัติได้
            echo  กรุณาดาวน์โหลดและติดตั้ง Python 3.11 จาก:
            echo  https://www.python.org/downloads/
            echo  (สำคัญ: ให้ติ๊กเลือก "Add Python to PATH" ก่อนกด Install)
            echo.
            pause
            exit /b 1
        )
        echo  [ + ] ติดตั้ง Python สำเร็จ! กรุณาเปิด install.bat ใหม่อีกครั้งเพื่อโหลด PATH
        pause
        exit /b 0
    )
)

:: 2. Run Diagnostics & Auto-Fix for dependencies
color 0E
echo  [ * ] กำลังตรวจสอบและเตรียมความพร้อมของ Framework & Dependencies...
python system_doctor.py --fix

:: 3. Launch Setup Wizard GUI
color 0A
echo.
echo  [ + ] กำลังเปิด Setup Wizard...
python setup_wizard.py

pause
