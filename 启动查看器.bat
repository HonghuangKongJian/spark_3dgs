@echo off
chcp 65001 >nul
setlocal

set "PROJECT_DIR=F:\test\spark_3dgs"
set "PYTHON=C:\Users\amw\.workbuddy\binaries\python\versions\3.13.12\python.exe"
set "PORT=8137"
set "URL=http://localhost:%PORT%/spark_3dgs.html"

cd /d "%PROJECT_DIR%"

REM Check if port is already in use
netstat -ano | findstr /r ":%PORT% " >nul
if %errorlevel%==0 (
    echo [INFO] Server already running on port %PORT%. Opening page...
    goto :open
)

REM Start local server (server.py supports uploads for LCC datasets)
echo [INFO] Starting local server on port %PORT% ...
start "" "%PYTHON%" "%PROJECT_DIR%\server.py" %PORT%
if errorlevel 1 (
    echo [ERROR] Failed to start server. Check Python path.
    pause
    exit /b 1
)

REM Wait for server readiness
echo [INFO] Waiting for server to be ready...
set /a RETRIES=0
:wait
timeout /t 1 >nul
curl -s -o nul -w "%%{http_code}" "http://127.0.0.1:%PORT%/spark_3dgs.html" 2>nul | findstr /r "^200$" >nul
if %errorlevel%==0 goto :open
set /a RETRIES+=1
if %RETRIES% LSS 10 goto :wait

:open
REM Open the viewer in default browser
echo [INFO] Opening %URL%
start "" "%URL%"

endlocal
