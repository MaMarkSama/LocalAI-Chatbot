@echo off
chcp 65001 >nul
title Gemma AI — Docker Image Builder & Portable Exporter
color 0B

echo.
echo  ======================================================
echo    Gemma AI — Docker Build & Portable Exporter
echo  ======================================================
echo.

cd /d "%~dp0"

:: 1. Check Docker
where docker >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo  [ X ] Error: Docker is not installed or not in PATH!
    pause
    exit /b 1
)

docker info >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo  [ X ] Error: Docker daemon is not running! Please start Docker Desktop.
    pause
    exit /b 1
)

:: 2. Build Docker Image
color 0E
echo  [ 1/3 ] Building Docker Image 'gemma-ai-chatbot:latest'...
docker build -t gemma-ai-chatbot:latest .

if %errorlevel% neq 0 (
    color 0C
    echo  [ X ] Docker build failed!
    pause
    exit /b 1
)

:: 3. Prepare output directory
set "OUTDIR=docker-dist"
echo.
echo  [ 2/3 ] Preparing portable package directory: %OUTDIR%
if exist "%OUTDIR%" rmdir /s /q "%OUTDIR%"
mkdir "%OUTDIR%"

:: 4. Export Image to TAR archive
echo.
echo  [ 3/3 ] Exporting image to '%OUTDIR%\gemma-ai-chatbot-image.tar' (may take a few minutes)...
docker save -o "%OUTDIR%\gemma-ai-chatbot-image.tar" gemma-ai-chatbot:latest

if %errorlevel% neq 0 (
    color 0C
    echo  [ X ] Failed to export docker image!
    pause
    exit /b 1
)

:: 5. Copy configuration and launchers into portable package
copy "docker-compose.yml" "%OUTDIR%\" >nul
copy ".env.example" "%OUTDIR%\" >nul
copy "docker-run.bat" "%OUTDIR%\" >nul
copy "docker-run.sh" "%OUTDIR%\" >nul

color 0A
echo.
echo  ======================================================
echo    [ + ] EXPORT COMPLETED SUCCESSFULLY!
echo  ======================================================
echo.
echo  แพ็กเกจพร้อมนำไปลงเครื่องอื่นอยู่ที่โฟลเดอร์:
echo    "%~dp0%OUTDIR%"
echo.
echo  สิ่งที่อยู่ในโฟลเดอร์:
echo    1. gemma-ai-chatbot-image.tar  (อิมเมจระบบ AI พร้อมรัน)
echo    2. docker-compose.yml          (คอนฟิกการรัน Container)
echo    3. .env.example                (เทมเพลตคอนฟิก)
echo    4. docker-run.bat              (สคริปต์ดับเบิลคลิกเดียวรันบน Windows)
echo    5. docker-run.sh               (สคริปต์รันบน Linux/macOS)
echo.
echo  วิธีนำไปใช้กับเครื่องอื่น:
echo    - ก๊อปปี้โฟลเดอร์ "%OUTDIR%" (หรือบีบอัดเป็น .zip) ไปวางที่เครื่องปลายทาง
echo    - เครื่องปลายทางเพียงมี Docker แล้วดับเบิลคลิก "docker-run.bat" ก็ใช้งานได้ทันที!
echo  ======================================================
echo.

pause
