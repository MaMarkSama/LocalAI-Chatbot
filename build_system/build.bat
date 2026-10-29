@echo off
chcp 65001 >nul
title Gemma AI - Build Installer

color 0D
echo.
echo  ======================================================
echo.
echo      ██████╗ ██╗   ██╗██╗██╗     ██████╗  ██████╗ 
echo      ██╔══██╗██║   ██║██║██║     ██╔══██╗██╔════╝ 
echo      ██████╔╝██║   ██║██║██║     ██║  ██║███████╗ 
echo      ██╔══██╗██║   ██║██║██║     ██║  ██║╚════██║ 
echo      ██████╔╝╚██████╔╝██║███████╗██████╔╝███████║ 
echo      ╚═════╝  ╚═════╝ ╚═╝╚══════╝╚═════╝ ╚══════╝ 
echo.
echo                 Gemma AI - Build Setup.exe
echo  ======================================================
echo.

cd /d "%~dp0"

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo  [ X ] Error: Python not found.
    pause & exit /b 1
)

:: Terminate running installer instances to prevent file lock PermissionError
taskkill /F /IM GemmaAI_Setup.exe >nul 2>&1

:: Install build tools
color 0E
echo  [ * ] Installing PyInstaller and build tools...
pip install pyinstaller pillow -q

:: Run build script
color 0B
echo  [ * ] Starting the build process. This may take a few minutes...
python build.py

if %errorlevel% neq 0 (
    color 0C
    echo  [ X ] Error: Build failed. Please check the logs above.
    pause & exit /b 1
)

echo.
color 0A
echo  ======================================================
echo  [ v ] Build Successful! 
echo  [ i ] You can find the installer in the 'dist' folder.
echo  ======================================================
pause
