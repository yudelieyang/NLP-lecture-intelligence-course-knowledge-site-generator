@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Please install Python 3.10+ and try again.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  python -m venv .venv
  if errorlevel 1 goto :error
)

echo Checking pip...
".venv\Scripts\python.exe" -m pip --version >nul 2>nul
if errorlevel 1 (
  echo Repairing pip in the virtual environment...
  ".venv\Scripts\python.exe" -m ensurepip --upgrade
  if errorlevel 1 goto :pip_error
  ".venv\Scripts\python.exe" -m pip --version >nul 2>nul
  if errorlevel 1 goto :pip_error
)

echo Installing dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo Starting local web console...
echo Local Web App is running at http://127.0.0.1:7860
echo Keep this window open while using the app.
echo Press Ctrl+C to stop.
start http://127.0.0.1:7860
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 7860
if errorlevel 1 goto :error

exit /b 0

:error
echo.
echo Console failed. Check the error message above.
pause
exit /b 1

:pip_error
echo.
echo pip is broken inside .venv and automatic repair failed.
echo Please close this window, delete the .venv folder, and run run_console.bat again.
pause
exit /b 1
