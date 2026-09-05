@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found on PATH.
    exit /b 1
)

if exist ".venv\Scripts\python.exe" (
    echo Virtual environment already exists at .venv
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create the virtual environment.
        exit /b 1
    )
    echo Virtual environment created at .venv
)

.venv\Scripts\python.exe -m pip install --group build
if errorlevel 1 (
    echo Failed to install the build dependencies.
    exit /b 1
)

echo Build dependencies installed.
echo PowerShell: .\.venv\Scripts\Activate.ps1
echo Command Prompt: call .venv\Scripts\activate.bat
