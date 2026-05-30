@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (
    python -m pip install -U -r requirements.txt
    goto :end
)

where py >nul 2>nul
if %errorlevel%==0 (
    py -m pip install -U -r requirements.txt
    goto :end
)

echo Python nao foi encontrado. Instale o Python em https://www.python.org/downloads/

:end
pause
