@echo off
chcp 65001 > nul
title BarberShop Manager - Sistema de Barbearia

echo ============================================================
echo         💈 INICIALIZANDO BARBERSHOP MANAGER 💈
echo ============================================================
echo.

:: Tenta localizar o executável do Python
set PYTHON_CMD=

where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=python
    goto RUN
)

where py >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=py
    goto RUN
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto RUN
)

if exist "%ProgramFiles%\Python312\python.exe" (
    set PYTHON_CMD="%ProgramFiles%\Python312\python.exe"
    goto RUN
)

echo [ERRO] Python não foi encontrado no sistema!
echo Por favor, certifique-se de que o Python 3.10+ está instalado.
echo.
pause
exit /b 1

:RUN
echo [OK] Python localizado: %PYTHON_CMD%
echo [INFO] Iniciando o servidor web em http://127.0.0.1:5000 ...
echo [INFO] Pressione CTRL + C para encerrar o servidor.
echo.
%PYTHON_CMD% app.py
pause

