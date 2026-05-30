@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (
    python sahur_downloader_gui.py
    goto :end
)

where py >nul 2>nul
if %errorlevel%==0 (
    py sahur_downloader_gui.py
    goto :end
)

echo Python nao foi encontrado. Instale o Python em https://www.python.org/downloads/

:end
pause
