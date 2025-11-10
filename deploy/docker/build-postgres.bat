@echo off
REM Build and Push PostgreSQL Image Script for Windows
REM This script builds the custom PostgreSQL image and optionally pushes to ACR

setlocal enabledelayedexpansion

REM Configuration
set IMAGE_NAME=ssc-postgres
set VERSION=16.0
if "%ACR_NAME%"=="" set ACR_NAME=sscappregistry

REM Get script directory
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..\..

echo.
echo ========================================
echo PostgreSQL Image Builder for SSC App
echo ========================================
echo Current settings:
echo   - Image name: %IMAGE_NAME%
echo   - Version: %VERSION%
echo   - ACR name: %ACR_NAME%
echo.

:menu
echo.
echo Select an option:
echo 1. Build locally only
echo 2. Build and test locally
echo 3. Build, test, and push to ACR
echo 4. Push existing image to ACR
echo 5. Exit
echo.
set /p option="Enter option (1-5): "

if "%option%"=="1" goto build
if "%option%"=="2" goto build_test
if "%option%"=="3" goto build_test_push
if "%option%"=="4" goto push
if "%option%"=="5" goto exit
echo Invalid option. Please try again.
goto menu

:build
echo [INFO] Building PostgreSQL image locally...
cd /d %PROJECT_ROOT%
docker build -f deploy\docker\Dockerfile.postgres -t %IMAGE_NAME%:%VERSION% -t %IMAGE_NAME%:latest .
if errorlevel 1 (
    echo [ERROR] Build failed!
    goto error
)
echo [INFO] Image built successfully!
echo [INFO] Tagged as: %IMAGE_NAME%:%VERSION% and %IMAGE_NAME%:latest
goto end

:build_test
call :build
echo.
echo [INFO] Testing PostgreSQL image locally...

REM Remove existing test container if exists
docker rm -f %IMAGE_NAME%-test >nul 2>&1

REM Run test container
echo [INFO] Starting test container...
docker run -d --name %IMAGE_NAME%-test -e POSTGRES_PASSWORD=testpass -e POSTGRES_DB=testdb -p 5433:5432 %IMAGE_NAME%:latest
if errorlevel 1 (
    echo [ERROR] Failed to start test container!
    goto error
)

REM Wait for PostgreSQL to be ready
echo [INFO] Waiting for PostgreSQL to be ready...
timeout /t 10 /nobreak >nul

REM Test connection
docker exec %IMAGE_NAME%-test pg_isready -U postgres
if errorlevel 1 (
    echo [ERROR] PostgreSQL health check failed!
    docker logs %IMAGE_NAME%-test
    goto error
)

echo [INFO] PostgreSQL is ready and accepting connections!

REM Show database info
echo [INFO] Database information:
docker exec %IMAGE_NAME%-test psql -U postgres -d testdb -c "SELECT version();"
docker exec %IMAGE_NAME%-test psql -U postgres -d testdb -c "SELECT * FROM pg_extension;"

echo [INFO] Test successful!

REM Cleanup
echo [INFO] Cleaning up test container...
docker rm -f %IMAGE_NAME%-test
goto end

:build_test_push
call :build_test
echo.
goto push

:push
echo [INFO] Pushing image to Azure Container Registry...

REM Login to ACR
echo [INFO] Logging into ACR: %ACR_NAME%
call az acr login --name %ACR_NAME%
if errorlevel 1 (
    echo [ERROR] Failed to login to ACR!
    goto error
)

REM Tag for ACR
set ACR_IMAGE=%ACR_NAME%.azurecr.io/%IMAGE_NAME%

docker tag %IMAGE_NAME%:%VERSION% %ACR_IMAGE%:%VERSION%
docker tag %IMAGE_NAME%:latest %ACR_IMAGE%:latest

REM Push to ACR
echo [INFO] Pushing %ACR_IMAGE%:%VERSION%
docker push %ACR_IMAGE%:%VERSION%
if errorlevel 1 (
    echo [ERROR] Failed to push image!
    goto error
)

echo [INFO] Pushing %ACR_IMAGE%:latest
docker push %ACR_IMAGE%:latest
if errorlevel 1 (
    echo [ERROR] Failed to push image!
    goto error
)

echo [INFO] Successfully pushed to ACR!
echo [INFO] Image: %ACR_IMAGE%:%VERSION%
echo [INFO] Image: %ACR_IMAGE%:latest
goto end

:error
echo.
echo [ERROR] Operation failed!
pause
exit /b 1

:end
echo.
echo [INFO] Done!
pause
exit /b 0
