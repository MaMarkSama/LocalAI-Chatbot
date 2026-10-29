@echo off
chcp 65001 >nul
title Gemma AI — Docker Portable Launcher
color 0B

echo.
echo  ======================================================
echo    Gemma AI — Docker Portable Launcher
echo  ======================================================
echo.

cd /d "%~dp0"

:: 1. Check if Docker is installed and running
where docker >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo  [ X ] Error: Docker is not installed or not in PATH!
    echo  Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

docker info >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo  [ X ] Error: Docker daemon is not running!
    echo  Please start Docker Desktop and try again.
    echo.
    pause
    exit /b 1
)

:: 2. If pre-built image tar exists, load it
if exist "gemma-ai-chatbot-image.tar" (
    color 0E
    echo  [ * ] Found pre-built image archive. Loading image into Docker...
    docker load -i gemma-ai-chatbot-image.tar
    if %errorlevel% neq 0 (
        color 0C
        echo  [ X ] Failed to load docker image archive!
        pause
        exit /b 1
    )
    echo  [ + ] Image loaded successfully!
    echo.
)

:: 3. Prepare .env if not exists
if not exist ".env" (
    if exist ".env.example" (
        echo  [ * ] Creating default .env configuration from .env.example...
        copy ".env.example" ".env" >nul
    )
)

:: 4. Start Docker Container via Docker Compose
color 0A
echo  [ * ] Starting Gemma AI container...
docker compose up -d

if %errorlevel% neq 0 (
    color 0C
    echo  [ X ] Error: docker compose up failed!
    pause
    exit /b 1
)

echo.
echo  ======================================================
echo    [ + ] Gemma AI is running successfully!
echo    URL: http://localhost:8001
echo    Admin: http://localhost:8001/admin
echo  ======================================================
echo.

:: 5. Open browser
start http://localhost:8001

pause
