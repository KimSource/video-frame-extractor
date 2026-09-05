@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Run setup-venv.bat first.
    exit /b 1
)

.venv\Scripts\python.exe -m PyInstaller --onefile --windowed --icon assets/icon.ico --add-data assets/icon.ico;assets main.py
if errorlevel 1 (
    echo Build failed.
    exit /b 1
)

echo Build completed: dist\main.exe
