@echo off
chcp 65001 >nul
title Gemma AI Launcher
color 0B

echo.
echo  ======================================================
echo.
echo     ██████╗ ███████╗███╗   ███╗███╗   ███╗ █████╗ 
echo    ██╔════╝ ██╔════╝████╗ ████║████╗ ████║██╔══██╗
echo    ██║  ███╗█████╗  ██╔████╔██║██╔████╔██║███████║
echo    ██║   ██║██╔══╝  ██║╚██╔╝██║██║╚██╔╝██║██╔══██║
echo    ╚██████╔╝███████╗██║ ╚═╝ ██║██║ ╚═╝ ██║██║  ██║
echo     ╚═════╝ ╚══════╝╚═╝     ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝
echo.
echo               Local AI Chatbot Assistant
echo  ======================================================
echo.

cd /d "%~dp0"

:: 1. Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    where py >nul 2>&1
    if %errorlevel% neq 0 (
        color 0C
        echo  [ X ] ไม่พบ Python ในระบบ กรุณารัน install.bat เพื่อติดตั้งอัตโนมัติ
        pause
        exit /b 1
    )
)

:: 2. Fast Framework Integrity Check
python -c "import fastapi, uvicorn, httpx, dotenv, pypdf, docx, openpyxl, multipart, ddgs, sqlite3" >nul 2>&1
if %errorlevel% neq 0 (
    color 0E
    echo  [ * ] พบ Framework หรือ Dependencies บางตัวยังไม่ครบ
    echo  [ * ] กำลังติดตั้งให้โดยอัตโนมัติ...
    python -m pip install -r requirements.txt -q --no-warn-script-location
)

:: 3. Check Ollama Status
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    color 0E
    echo  [ ! ] ยังไม่พบ Ollama ในระบบ (สามารถใช้งานโหมด Offline หรือรัน install.bat เพื่อติดตั้ง)
) else (
    :: Ping Ollama service on 11434
    powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri 'http://localhost:11434/api/tags' -TimeoutSec 1 -UseBasicParsing).StatusCode } catch { exit 1 }" >nul 2>&1
    if %errorlevel% neq 0 (
        echo  [ * ] กำลังเริ่มบริการ Ollama ในพื้นหลัง...
        start "" ollama serve >nul 2>&1
    )
)

:: 4. Launch
if exist "launcher.py" (
    color 0A
    echo  [ + ] กำลังเปิด Gemma AI Control Panel...
    python launcher.py
    if errorlevel 1 (
        color 0C
        echo.
        echo  [ X ] เกิดข้อผิดพลาดในการรัน launcher.py
        pause
    )
) else (
    color 0C
    echo  [ X ] Error: launcher.py not found!
    pause
    exit /b 1
)
