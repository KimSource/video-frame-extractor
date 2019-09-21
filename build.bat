@echo off
pyinstaller --onefile --windowed --icon assets/icon.ico --add-data assets/icon.ico;assets main.py
